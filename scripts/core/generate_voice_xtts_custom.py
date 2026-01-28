#!/home/rsalars/Projects/dreamweaving/venv_coqui/bin/python
"""
XTTS-v2 Voice Generator - Custom Script
Bypasses torchcodec dependency by using soundfile for audio loading.
"""

import argparse
import gc
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

# Limit threads before importing ML libraries
os.environ["OMP_NUM_THREADS"] = "8"
os.environ["MKL_NUM_THREADS"] = "8"
os.environ["OPENBLAS_NUM_THREADS"] = "8"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch
torch.set_num_threads(8)

# Fix weights_only for TTS model loading (PyTorch 2.6+)
if hasattr(torch.serialization, 'add_safe_globals'):
    _original_torch_load = torch.load
    def _patched_torch_load(*args, **kwargs):
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        return _original_torch_load(*args, **kwargs)
    torch.load = _patched_torch_load

import numpy as np
import soundfile as sf
from pydub import AudioSegment
from pydub.effects import normalize

# Patch torchaudio to use soundfile instead of torchcodec
import torchaudio
_original_torchaudio_load = torchaudio.load
def _patched_torchaudio_load(filepath, *args, **kwargs):
    """Use soundfile backend to load audio, bypassing torchcodec."""
    audio, sr = sf.read(str(filepath))
    if audio.ndim == 1:
        audio = audio.reshape(1, -1)
    else:
        audio = audio.T
    return torch.tensor(audio, dtype=torch.float32), sr
torchaudio.load = _patched_torchaudio_load

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts


def clean_text_for_tts(text: str) -> str:
    """Remove ALL XML/SSML tags and cleanup text for TTS."""
    # Remove all XML tags (any tag like <anything> or </anything> or <anything/>)
    text = re.sub(r'<[^>]+>', '', text)
    # Remove markers like [DVE:...], [SFX:...], etc
    text = re.sub(r'\[[^\]]+\]', '', text)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_ssml_with_breaks(ssml_text: str) -> List[Tuple[str, int]]:
    """Parse SSML and extract text segments with their following break durations."""
    # First remove comments (they can contain anything)
    text = re.sub(r'<!--.*?-->', '', ssml_text, flags=re.DOTALL)
    
    # Find all breaks and extract their positions and durations
    break_pattern = r'<break\s+time=["\'](\d+\.?\d*)(m?s)["\']\s*/>'
    segments = []
    last_end = 0
    
    for match in re.finditer(break_pattern, text):
        text_before = text[last_end:match.start()]
        value = float(match.group(1))
        unit = match.group(2)
        duration_ms = int(value * 1000) if unit == 's' else int(value)
        
        # Clean all XML tags from the text segment
        clean_segment = clean_text_for_tts(text_before)
        
        if clean_segment:
            segments.append((clean_segment, duration_ms))
        elif segments:
            # No text but we have a break - add to previous segment's break
            prev_text, prev_break = segments[-1]
            segments[-1] = (prev_text, prev_break + duration_ms)
        
        last_end = match.end()
    
    # Get any remaining text after the last break
    remaining = text[last_end:]
    clean_remaining = clean_text_for_tts(remaining)
    if clean_remaining:
        segments.append((clean_remaining, 500))
    
    return segments


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ssml_file', type=Path)
    parser.add_argument('output_dir', type=Path)
    parser.add_argument('--voice', type=Path, required=True)
    parser.add_argument('--speed', type=float, default=0.88)
    args = parser.parse_args()
    
    print("=" * 70)
    print("   XTTS-v2 VOICE GENERATOR (soundfile backend)")
    print("=" * 70)
    
    # Read SSML
    with open(args.ssml_file, 'r') as f:
        ssml_text = f.read()
    
    segments = parse_ssml_with_breaks(ssml_text)
    print(f"Found {len(segments)} segments")
    print(f"Total break time: {sum(s[1] for s in segments) / 1000:.1f}s")
    
    # Load model
    print("\nLoading XTTS-v2 model...")
    model_dir = Path.home() / ".local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2"
    
    config = XttsConfig()
    config.load_json(str(model_dir / "config.json"))
    model = Xtts.init_from_config(config)
    model.load_checkpoint(config, checkpoint_dir=str(model_dir))
    model.eval()
    print("Model loaded!")
    
    # Get conditioning latents from voice sample
    print(f"\nProcessing voice sample: {args.voice}")
    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
        audio_path=str(args.voice),
        load_sr=22050
    )
    print("Voice cloning ready!")
    
    # Generate audio for each segment
    args.output_dir.mkdir(parents=True, exist_ok=True)
    combined = AudioSegment.empty()
    
    MIN_BREAK_MS = 200
    MAX_BREAK_MS = 8000
    
    print(f"\nGenerating {len(segments)} segments...")
    for i, (text, break_ms) in enumerate(segments, 1):
        if not text.strip():
            continue
        
        break_ms = max(MIN_BREAK_MS, min(break_ms, MAX_BREAK_MS))
        
        if i % 20 == 0 or i == len(segments):
            print(f"   [{i}/{len(segments)}] {text[:40]}... (pause: {break_ms}ms)")
        
        if i % 50 == 0:
            gc.collect()
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name
            
            out = model.inference(
                text,
                "en",
                gpt_cond_latent,
                speaker_embedding,
                enable_text_splitting=True
            )
            
            # Save audio
            audio_array = out["wav"]
            sample_rate = 24000
            sf.write(tmp_path, audio_array, sample_rate)
            
            segment_audio = AudioSegment.from_wav(tmp_path)
            combined += segment_audio
            combined += AudioSegment.silent(duration=break_ms)
            
        except Exception as e:
            print(f"   Warning: Failed segment {i}: {e}")
            combined += AudioSegment.silent(duration=break_ms)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    # Apply speed adjustment
    if args.speed != 1.0:
        print(f"\nAdjusting speed to {args.speed}x...")
        combined = combined._spawn(combined.raw_data, overrides={
            "frame_rate": int(combined.frame_rate * args.speed)
        }).set_frame_rate(combined.frame_rate)
    
    # Normalize
    print("Normalizing audio...")
    combined = normalize(combined)
    
    # Export
    output_file = args.output_dir / "voice_xtts.mp3"
    combined.export(str(output_file), format="mp3", bitrate="192k")
    
    duration = len(combined) / 1000
    print(f"\n✅ Complete! Duration: {duration/60:.1f} minutes")
    print(f"   Output: {output_file}")


if __name__ == "__main__":
    main()
