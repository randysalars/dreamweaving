#!/usr/bin/env python3
"""
Edge TTS Voice Generator with SSML Support

Microsoft Edge TTS is free and supports SSML natively!
This is a drop-in replacement for Google Cloud TTS.

Usage:
    python generate_voice_edge.py <ssml_file> <output_dir>
"""

import asyncio
import re
import sys
from pathlib import Path
from typing import List

try:
    import edge_tts
    from pydub import AudioSegment
    from pydub.effects import normalize
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("\nInstall required packages:")
    print("  pip install edge-tts pydub")
    sys.exit(1)


class EdgeTTSGenerator:
    """Generate voice using Microsoft Edge TTS with SSML support."""
    
    # Good voices for meditation/calm content
    RECOMMENDED_VOICES = {
        'male_calm': 'en-US-GuyNeural',
        'male_deep': 'en-US-DavisNeural',
        'female_calm': 'en-US-JennyNeural',
        'female_warm': 'en-US-AriaNeural',
    }
    
    def __init__(self, voice: str = 'en-US-GuyNeural'):
        """Initialize Edge TTS generator.
        
        Args:
            voice: Voice name. Use one of RECOMMENDED_VOICES or any Edge TTS voice.
        """
        self.voice = voice
        print(f"Using voice: {voice}")
    
    async def generate_from_ssml_async(self, ssml_file: Path, output_dir: Path) -> Path:
        """Generate audio from SSML file (async version).
        
        Args:
            ssml_file: Path to SSML file
            output_dir: Directory to save audio
            
        Returns:
            Path to output audio file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Read SSML
        print(f"📖 Reading SSML: {ssml_file}")
        with open(ssml_file, 'r', encoding='utf-8') as f:
            ssml_text = f.read()
        
        # Clean up SSML for Edge TTS compatibility
        ssml_text = self._prepare_ssml(ssml_text)
        
        # Count characters
        text_only = re.sub(r'<[^>]+>', '', ssml_text)
        char_count = len(text_only)
        print(f"   Character count: {char_count:,}")
        
        # Edge TTS has a limit (~10000 chars), need to chunk if necessary
        if char_count > 8000:
            print(f"   ⚠️  Long script, will generate in chunks")
            return await self._generate_chunked(ssml_text, output_dir)
        else:
            return await self._generate_single(ssml_text, output_dir)
    
    def _prepare_ssml(self, ssml_text: str) -> str:
        """Prepare SSML for Edge TTS.
        
        Edge TTS supports most SSML but we need to:
        1. Remove custom markers like [DVE:...]
        2. Keep break, prosody, emphasis tags  
        3. Ensure proper voice wrapper
        4. Remove comments
        """
        # Remove custom markers
        ssml_text = re.sub(r'\[DVE:[^\]]+\]', '', ssml_text)
        ssml_text = re.sub(r'\[[^\]]+\]', '', ssml_text)
        
        # Remove XML declaration if present
        ssml_text = re.sub(r'<\?xml[^>]*\?>', '', ssml_text)
        
        # Remove comments
        ssml_text = re.sub(r'<!--.*?-->', '', ssml_text, flags=re.DOTALL)
        
        # Remove existing speak wrapper
        ssml_text = re.sub(r'<speak[^>]*>', '', ssml_text)
        ssml_text = re.sub(r'</speak>', '', ssml_text)
        
        # Clean up excessive whitespace
        ssml_text = re.sub(r'\n\s*\n', '\n', ssml_text)
        
        # Wrap with voice tag for Edge TTS
        ssml_text = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{self.voice}">
{ssml_text}
</voice>
</speak>'''
        
        return ssml_text
    
    async def _generate_single(self, ssml_text: str, output_dir: Path) -> Path:
        """Generate audio from SSML in a single request."""
        output_file = output_dir / "voice_synth_temp.mp3"
        
        print("🎙️  Generating audio with Edge TTS...")
        
        communicate = edge_tts.Communicate(ssml_text, voice=self.voice)
        await communicate.save(str(output_file))
        
        # Load and normalize
        print("🎚️  Normalizing audio...")
        audio = AudioSegment.from_mp3(str(output_file))
        audio = normalize(audio)
        
        # Export final
        final_output = output_dir / "voice_synth.mp3"
        audio.export(str(final_output), format="mp3", bitrate="128k")
        
        # Clean up temp
        output_file.unlink()
        
        duration = len(audio) / 1000
        print(f"✅ Complete! Duration: {duration:.1f} seconds")
        
        return final_output
    
    async def _generate_chunked(self, ssml_text: str, output_dir: Path) -> Path:
        """Generate audio in chunks for long scripts."""
        # Split SSML by prosody blocks (natural break points)
        chunks = self._split_ssml_into_chunks(ssml_text)
        
        print(f"   Generating {len(chunks)} chunks...")
        
        audio_parts = []
        
        for i, chunk in enumerate(chunks):
            print(f"   🎙️  Chunk {i+1}/{len(chunks)}")
            
            chunk_file = output_dir / f"chunk_{i:03d}.mp3"
            
            communicate = edge_tts.Communicate(chunk, voice=self.voice)
            await communicate.save(str(chunk_file))
            
            # Load chunk
            audio = AudioSegment.from_mp3(str(chunk_file))
            audio_parts.append(audio)
            
            # Clean up
            chunk_file.unlink()
        
        # Merge all chunks
        print("🔗 Merging audio chunks...")
        final_audio = sum(audio_parts)
        
        # Normalize
        print("🎚️  Normalizing audio...")
        final_audio = normalize(final_audio)
        
        # Export
        output_file = output_dir / "voice_synth.mp3"
        print(f"💾 Exporting: {output_file}")
        final_audio.export(str(output_file), format="mp3", bitrate="128k")
        
        duration = len(final_audio) / 1000
        print(f"✅ Complete! Duration: {duration:.1f} seconds")
        
        return output_file
    
    def _split_ssml_into_chunks(self, ssml_text: str, max_chars: int = 7000) -> List[str]:
        """Split SSML into chunks at prosody boundaries."""
        # Extract content between voice tags
        voice_match = re.search(r'<voice[^>]*>(.*)</voice>', ssml_text, re.DOTALL)
        if not voice_match:
            return [ssml_text]
        
        content = voice_match.group(1)
        
        # Split by prosody blocks
        prosody_pattern = r'(<prosody[^>]*>.*?</prosody>)'
        blocks = re.split(prosody_pattern, content, flags=re.DOTALL)
        
        chunks = []
        current_chunk = ""
        
        for block in blocks:
            if not block.strip():
                continue
            
            # Check if adding this block would exceed limit
            test_chunk = current_chunk + block
            text_only = re.sub(r'<[^>]+>', '', test_chunk)
            
            if len(text_only) > max_chars and current_chunk:
                # Wrap and save current chunk
                wrapped = self._wrap_chunk(current_chunk)
                chunks.append(wrapped)
                current_chunk = block
            else:
                current_chunk += block
        
        # Don't forget last chunk
        if current_chunk.strip():
            wrapped = self._wrap_chunk(current_chunk)
            chunks.append(wrapped)
        
        return chunks
    
    def _wrap_chunk(self, content: str) -> str:
        """Wrap content fragment in proper SSML structure."""
        return f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<voice name="{self.voice}">
{content}
</voice>
</speak>'''
    
    def generate_from_ssml(self, ssml_file: Path, output_dir: Path) -> Path:
        """Synchronous wrapper for async generation."""
        return asyncio.run(self.generate_from_ssml_async(ssml_file, output_dir))


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_voice_edge.py <ssml_file> <output_dir> [voice]")
        print("\nRecommended voices:")
        for name, voice in EdgeTTSGenerator.RECOMMENDED_VOICES.items():
            print(f"  {name}: {voice}")
        sys.exit(1)
    
    ssml_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    voice = sys.argv[3] if len(sys.argv) > 3 else 'en-US-GuyNeural'
    
    if not ssml_file.exists():
        print(f"❌ SSML file not found: {ssml_file}")
        sys.exit(1)
    
    print("=" * 70)
    print("   EDGE TTS VOICE GENERATOR (Free, SSML-Compatible)")
    print("=" * 70)
    print()
    
    generator = EdgeTTSGenerator(voice=voice)
    output_file = generator.generate_from_ssml(ssml_file, output_dir)
    
    print()
    print(f"✅ Voice generation complete: {output_file}")


if __name__ == "__main__":
    main()
