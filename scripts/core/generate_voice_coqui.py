#!/usr/bin/env python3.11
"""
Coqui TTS Voice Generator with SSML Support

This module provides a drop-in replacement for Google Cloud TTS that:
1. Parses SSML tags and converts them to text + timing metadata
2. Generates audio using Coqui TTS (XTTS-v2)
3. Applies post-processing to simulate SSML features (pauses, emphasis, pitch)
4. Outputs the same audio format as the original pipeline

NOTE: This script requires Python 3.11 and uses venv_coqui environment.

Usage:
    /path/to/venv_coqui/bin/python generate_voice_coqui.py <ssml_file> <output_dir>
"""

import re
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import xml.etree.ElementTree as ET

# Check for required dependencies
try:
    from TTS.api import TTS
    import numpy as np
    from pydub import AudioSegment
    from pydub.effects import normalize, speedup
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("\nInstall required packages:")
    print("  pip install TTS pydub")
    sys.exit(1)


class SSMLParser:
    """Parse SSML and extract text segments with timing/prosody metadata."""
    
    def __init__(self):
        self.segments: List[Dict] = []
        
    def parse_ssml(self, ssml_text: str) -> List[Dict]:
        """Parse SSML and return list of segments with metadata.
        
        Returns:
            List of dicts with keys: text, pause_after, rate, pitch, emphasis
        """
        # Remove XML declaration and SSML wrapper
        ssml_text = re.sub(r'<\?xml[^>]*\?>', '', ssml_text)
        ssml_text = re.sub(r'<speak[^>]*>', '', ssml_text)
        ssml_text = re.sub(r'</speak>', '', ssml_text)
        
        # Remove comments
        ssml_text = re.sub(r'<!--.*?-->', '', ssml_text, flags=re.DOTALL)
        
        # Extract prosody context (rate, pitch)
        current_rate = 1.0
        current_pitch = 0
        
        # Simple regex-based parsing (more robust than full XML for our case)
        segments = []
        
        # Split by prosody tags to track context
        prosody_pattern = r'<prosody\s+rate=[\'"]([^\'"]*)[\'"]\s+pitch=[\'"]([^\'"]*)[\'"]\s*>(.*?)</prosody>'
        
        for match in re.finditer(prosody_pattern, ssml_text, re.DOTALL):
            rate_str = match.group(1)
            pitch_str = match.group(2)
            content = match.group(3)
            
            # Parse rate
            rate = float(rate_str) if rate_str else 1.0
            
            # Parse pitch (e.g., "-2st" -> -2 semitones)
            pitch = 0
            if pitch_str:
                pitch_match = re.match(r'([+-]?\d+)st', pitch_str)
                if pitch_match:
                    pitch = int(pitch_match.group(1))
            
            # Parse content within this prosody block
            segments.extend(self._parse_content(content, rate, pitch))
        
        return segments
    
    def _parse_content(self, content: str, rate: float, pitch: int) -> List[Dict]:
        """Parse content within a prosody block."""
        segments = []
        
        # Split by breaks and text
        # Pattern: text, then optional break
        parts = re.split(r'(<break[^>]*/>)', content)
        
        current_text = ""
        
        for part in parts:
            if part.strip().startswith('<break'):
                # Extract break duration
                time_match = re.search(r'time=[\'"]([^\'"]*)[\'"]', part)
                pause_ms = 0
                if time_match:
                    pause_ms = self._parse_time(time_match.group(1))
                
                # Save current text segment if any
                if current_text.strip():
                    segments.append({
                        'text': self._clean_text(current_text),
                        'pause_after': pause_ms,
                        'rate': rate,
                        'pitch': pitch,
                        'emphasis': False
                    })
                    current_text = ""
                else:
                    # Just a pause with no text
                    segments.append({
                        'text': '',
                        'pause_after': pause_ms,
                        'rate': rate,
                        'pitch': pitch,
                        'emphasis': False
                    })
            else:
                # Accumulate text
                # Check for emphasis
                has_emphasis = '<emphasis' in part
                clean = self._clean_text(part)
                if clean:
                    current_text += clean + " "
        
        # Don't forget remaining text
        if current_text.strip():
            segments.append({
                'text': self._clean_text(current_text),
                'pause_after': 0,
                'rate': rate,
                'pitch': pitch,
                'emphasis': False
            })
        
        return segments
    
    def _parse_time(self, time_str: str) -> int:
        """Parse time string to milliseconds (e.g., '2s' -> 2000, '500ms' -> 500)."""
        if time_str.endswith('ms'):
            return int(time_str[:-2])
        elif time_str.endswith('s'):
            return int(float(time_str[:-1]) * 1000)
        return 0
    
    def _clean_text(self, text: str) -> str:
        """Remove all XML tags and clean text."""
        # Remove all tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove DVE markers
        text = re.sub(r'\[DVE:[^\]]+\]', '', text)
        # Remove style markers like [softly]
        text = re.sub(r'\[[^\]]+\]', '', text)
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class CoquiVoiceGenerator:
    """Generate voice using Coqui TTS with SSML-like control."""
    
    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"):
        """Initialize Coqui TTS.
        
        Args:
            model_name: Coqui model to use. Options:
                - "tts_models/en/ljspeech/tacotron2-DDC" (fast, good quality)
                - "tts_models/multilingual/multi-dataset/xtts_v2" (best quality, slower)
        """
        print(f"Loading Coqui TTS model: {model_name}")
        try:
            self.tts = TTS(model_name=model_name, progress_bar=False)
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            print("\nAvailable models:")
            print("  - tts_models/en/ljspeech/tacotron2-DDC (recommended)")
            print("  - tts_models/en/ljspeech/vits")
            sys.exit(1)
    
    def generate_from_ssml(self, ssml_file: Path, output_dir: Path) -> Path:
        """Generate audio from SSML file.
        
        Args:
            ssml_file: Path to SSML file
            output_dir: Directory to save audio files
            
        Returns:
            Path to final merged audio file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Parse SSML
        print(f"📖 Parsing SSML: {ssml_file}")
        with open(ssml_file, 'r', encoding='utf-8') as f:
            ssml_text = f.read()
        
        parser = SSMLParser()
        segments = parser.parse_ssml(ssml_text)
        
        print(f"   Found {len(segments)} segments")
        
        # Generate audio for each segment
        audio_parts = []
        
        for i, segment in enumerate(segments):
            if not segment['text']:
                # Just add silence
                if segment['pause_after'] > 0:
                    silence = AudioSegment.silent(duration=segment['pause_after'])
                    audio_parts.append(silence)
                continue
            
            print(f"   🎙️  Generating segment {i+1}/{len(segments)}: {segment['text'][:50]}...")
            
            # Generate audio
            temp_file = output_dir / f"temp_segment_{i:03d}.wav"
            
            try:
                self.tts.tts_to_file(
                    text=segment['text'],
                    file_path=str(temp_file)
                )
                
                # Load and process
                audio = AudioSegment.from_wav(str(temp_file))
                
                # Apply rate adjustment (speed up/down)
                if segment['rate'] != 1.0:
                    # pydub speedup is multiplicative
                    audio = audio._spawn(audio.raw_data, overrides={
                        "frame_rate": int(audio.frame_rate * segment['rate'])
                    })
                    audio = audio.set_frame_rate(44100)
                
                # Apply pitch shift (simple octave shift)
                if segment['pitch'] != 0:
                    # Simple pitch shift using sample rate manipulation
                    # Note: This is approximate, real pitch shifting needs librosa
                    new_sample_rate = int(audio.frame_rate * (2 ** (segment['pitch'] / 12.0)))
                    audio = audio._spawn(audio.raw_data, overrides={
                        "frame_rate": new_sample_rate
                    })
                    audio = audio.set_frame_rate(44100)
                
                # Add pause after
                if segment['pause_after'] > 0:
                    silence = AudioSegment.silent(duration=segment['pause_after'])
                    audio = audio + silence
                
                audio_parts.append(audio)
                
                # Clean up temp file
                temp_file.unlink()
                
            except Exception as e:
                print(f"      ⚠️  Failed to generate segment: {e}")
                continue
        
        # Merge all audio
        print("🔗 Merging audio segments...")
        final_audio = sum(audio_parts)
        
        # Normalize
        print("🎚️  Normalizing audio...")
        final_audio = normalize(final_audio)
        
        # Export
        output_file = output_dir / "voice_synth.mp3"
        print(f"💾 Exporting: {output_file}")
        final_audio.export(str(output_file), format="mp3", bitrate="128k")
        
        print(f"✅ Complete! Duration: {len(final_audio) / 1000:.1f} seconds")
        return output_file


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_voice_coqui.py <ssml_file> <output_dir>")
        sys.exit(1)
    
    ssml_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    if not ssml_file.exists():
        print(f"❌ SSML file not found: {ssml_file}")
        sys.exit(1)
    
    print("=" * 70)
    print("   COQUI TTS VOICE GENERATOR (SSML-Compatible)")
    print("=" * 70)
    print()
    
    generator = CoquiVoiceGenerator()
    output_file = generator.generate_from_ssml(ssml_file, output_dir)
    
    print()
    print(f"✅ Voice generation complete: {output_file}")


if __name__ == "__main__":
    main()
