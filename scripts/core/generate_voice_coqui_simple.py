#!/home/rsalars/Projects/dreamweaving/venv_coqui/bin/python
"""
Coqui TTS Voice Generator - XTTS v2 (Natural Human Voice)

Uses XTTS v2, the most natural-sounding open-source TTS model.
Supports voice cloning from a reference audio file.

IMPORTANT: This script properly handles SSML <break> tags by inserting
actual silence of the specified duration. This is critical for hypnotic
scripts that require proper pacing.

Usage:
    venv_coqui/bin/python generate_voice_coqui_simple.py <ssml_file> <output_dir>
    venv_coqui/bin/python generate_voice_coqui_simple.py <ssml_file> <output_dir> --voice <reference.wav>

Models (in order of quality):
    - xtts_v2: Best quality, natural human voice, supports cloning (DEFAULT)
    - vits: Good quality, faster, no cloning
    - jenny: Female voice, good quality
"""

import argparse
import re
import sys
import os
import gc
from pathlib import Path
from typing import List, Tuple

# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE OPTIMIZATION FOR CPU-ONLY SYSTEMS
# System has 16 cores / 29GB RAM - limit to prevent resource starvation
# These MUST be set BEFORE importing torch/numpy/any ML libraries
# ═══════════════════════════════════════════════════════════════════════════════
MAX_TTS_THREADS = 8  # Use 8 of 16 cores (50%), leaving room for system processes

# Set thread limits for all numeric libraries
os.environ["OMP_NUM_THREADS"] = str(MAX_TTS_THREADS)
os.environ["MKL_NUM_THREADS"] = str(MAX_TTS_THREADS)
os.environ["OPENBLAS_NUM_THREADS"] = str(MAX_TTS_THREADS)
os.environ["VECLIB_MAXIMUM_THREADS"] = str(MAX_TTS_THREADS)
os.environ["NUMEXPR_NUM_THREADS"] = str(MAX_TTS_THREADS)

# Reduce HuggingFace tokenizer parallelism overhead
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    import torch

    # Apply torch thread limits (must be done after import)
    torch.set_num_threads(MAX_TTS_THREADS)
    torch.set_num_interop_threads(2)  # Limit inter-op parallelism

    # Fix for PyTorch 2.6+ security changes with torch.load
    # XTTS v2 model checkpoint contains many custom classes that need to be
    # deserialized. Since TTS library is a trusted source, we allow all globals.
    # This must be done BEFORE importing TTS.
    if hasattr(torch.serialization, 'add_safe_globals'):
        # Monkey-patch torch.load to use weights_only=False for TTS models
        # This is safe because we're loading official Coqui TTS models
        _original_torch_load = torch.load

        def _patched_torch_load(*args, **kwargs):
            # Default to weights_only=False for model loading
            if 'weights_only' not in kwargs:
                kwargs['weights_only'] = False
            return _original_torch_load(*args, **kwargs)

        torch.load = _patched_torch_load

    from TTS.api import TTS
    from pydub import AudioSegment
    from pydub.effects import normalize

except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)


# Default reference voice for XTTS (warm female voice sample)
DEFAULT_VOICE_SAMPLE = Path(__file__).parent.parent.parent / "assets" / "voice_samples" / "warm_female.wav"


def parse_ssml_with_breaks(ssml_text: str) -> List[Tuple[str, int]]:
    """
    Parse SSML and extract text segments with their following break durations.

    Returns a list of tuples: (text_segment, break_duration_ms)
    """
    # Remove XML declaration
    text = re.sub(r'<\?xml[^>]*\?>', '', ssml_text)
    # Remove comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # Remove DVE markers
    text = re.sub(r'\[DVE:[^\]]+\]', '', text)
    # Remove SFX markers
    text = re.sub(r'\[SFX:[^\]]+\]', '', text)
    # Remove other markers
    text = re.sub(r'\[[^\]]+\]', '', text)

    # Replace prosody and other non-break tags with nothing
    text = re.sub(r'<prosody[^>]*>', '', text)
    text = re.sub(r'</prosody>', '', text)
    text = re.sub(r'<speak[^>]*>', '', text)
    text = re.sub(r'</speak>', '', text)
    text = re.sub(r'<emphasis[^>]*>', '', text)
    text = re.sub(r'</emphasis>', '', text)

    # Now parse text segments and breaks
    # Pattern to find breaks with their durations
    break_pattern = r'<break\s+time=["\'](\d+\.?\d*)(m?s)["\']\s*/>'

    segments = []
    last_end = 0

    for match in re.finditer(break_pattern, text):
        # Get text before this break
        text_before = text[last_end:match.start()]

        # Parse break duration
        value = float(match.group(1))
        unit = match.group(2)
        if unit == 's':
            duration_ms = int(value * 1000)
        else:  # ms
            duration_ms = int(value)

        # Clean up the text
        text_before = re.sub(r'\s+', ' ', text_before).strip()

        if text_before:
            segments.append((text_before, duration_ms))
        elif segments:
            # No text but we have a break - add to previous segment's break
            prev_text, prev_break = segments[-1]
            segments[-1] = (prev_text, prev_break + duration_ms)

        last_end = match.end()

    # Get any remaining text after the last break
    remaining = text[last_end:]
    remaining = re.sub(r'\s+', ' ', remaining).strip()
    if remaining:
        segments.append((remaining, 500))  # Default ending pause

    return segments


def generate_audio_with_breaks(tts, segments: List[Tuple[str, int]], voice_sample: Path = None) -> AudioSegment:
    """
    Generate audio for each text segment and insert proper silence breaks.

    Args:
        tts: The TTS model instance
        segments: List of (text, break_duration_ms) tuples
        voice_sample: Optional voice sample for XTTS cloning

    Returns:
        Combined AudioSegment with proper pacing
    """
    import tempfile

    combined = AudioSegment.empty()
    total_segments = len(segments)

    # Minimum break duration to avoid tiny pauses
    MIN_BREAK_MS = 200
    # Maximum break duration (cap extremely long breaks)
    MAX_BREAK_MS = 8000

    print(f"   Processing {total_segments} segments with breaks...")

    for i, (text, break_ms) in enumerate(segments, 1):
        if not text.strip():
            continue

        # Cap break duration
        break_ms = max(MIN_BREAK_MS, min(break_ms, MAX_BREAK_MS))

        # Show progress every 20 segments
        if i % 20 == 0 or i == total_segments:
            print(f"   [{i}/{total_segments}] {text[:40]}... (pause: {break_ms}ms)")

        # Periodic garbage collection to prevent memory bloat (every 50 segments)
        if i % 50 == 0:
            gc.collect()

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Generate audio for this segment
            if voice_sample and voice_sample.exists():
                tts.tts_to_file(
                    text=text,
                    file_path=tmp_path,
                    speaker_wav=str(voice_sample),
                    language="en"
                )
            else:
                tts.tts_to_file(text=text, file_path=tmp_path)

            # Load the generated audio
            segment_audio = AudioSegment.from_wav(tmp_path)

            # Add to combined audio
            combined += segment_audio

            # Add silence for the break
            combined += AudioSegment.silent(duration=break_ms)

        except Exception as e:
            print(f"   Warning: Failed to generate segment {i}: {e}")
            # Add a pause anyway to maintain timing
            combined += AudioSegment.silent(duration=break_ms)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    return combined


def strip_ssml_simple(ssml_text: str) -> str:
    """Simple SSML stripping for fallback - removes all tags."""
    # Remove XML declaration
    text = re.sub(r'<\?xml[^>]*\?>', '', ssml_text)
    # Remove comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # Remove all tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove markers
    text = re.sub(r'\[[^\]]+\]', '', text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def main():
    parser = argparse.ArgumentParser(description='Coqui TTS Voice Generator')
    parser.add_argument('ssml_file', type=Path, help='SSML file to synthesize')
    parser.add_argument('output_dir', type=Path, help='Output directory')
    parser.add_argument('--voice', type=Path, help='Reference voice WAV for cloning')
    parser.add_argument('--model', choices=['xtts', 'vits', 'jenny'], default='xtts',
                       help='TTS model to use (default: xtts)')
    parser.add_argument('--speed', type=float, default=0.92,
                       help='Speech speed (0.8-1.2, default: 0.92 for hypnotic pace)')
    parser.add_argument('--no-breaks', action='store_true',
                       help='Disable SSML break parsing (faster but loses pacing)')
    args = parser.parse_args()

    if not args.ssml_file.exists():
        print(f"SSML file not found: {args.ssml_file}")
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("   COQUI TTS VOICE GENERATOR")
    print("   Model: " + args.model.upper())
    print("   SSML Break Handling: " + ("DISABLED" if args.no_breaks else "ENABLED"))
    print("=" * 70)
    print()

    # Read SSML
    print(f"Reading SSML: {args.ssml_file}")
    with open(args.ssml_file, 'r', encoding='utf-8') as f:
        ssml_text = f.read()

    # Parse SSML with breaks or simple strip
    if args.no_breaks:
        plain_text = strip_ssml_simple(ssml_text)
        segments = None
        char_count = len(plain_text)
    else:
        segments = parse_ssml_with_breaks(ssml_text)
        char_count = sum(len(s[0]) for s in segments)
        total_break_time = sum(s[1] for s in segments) / 1000
        print(f"   Found {len(segments)} text segments")
        print(f"   Total break time: {total_break_time:.1f}s ({total_break_time/60:.1f} min)")

    print(f"   Character count: {char_count:,}")

    # Check for voice sample BEFORE loading model
    voice_sample = None
    if args.model == 'xtts':
        voice_sample = args.voice if args.voice else DEFAULT_VOICE_SAMPLE
        if voice_sample and voice_sample.exists():
            print(f"   Voice sample found: {voice_sample.name}")
        else:
            print("   No voice sample found - using Jenny model instead")
            print("   (XTTS v2 requires a reference voice file for cloning)")
            args.model = 'jenny'
            voice_sample = None

    # Memory optimization: clear any cached memory before loading large model
    gc.collect()

    # Select and load model
    if args.model == 'xtts':
        model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        print("\nLoading XTTS v2 (this takes 1-2 minutes on first run)...")
    elif args.model == 'vits':
        model_name = "tts_models/en/ljspeech/vits"
        print("\nLoading VITS model...")
    elif args.model == 'jenny':
        model_name = "tts_models/en/jenny/jenny"
        print("\nLoading Jenny model...")

    # Check for GPU
    use_gpu = torch.cuda.is_available()
    if use_gpu:
        print(f"   Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("   Using CPU (GPU not available)")

    tts = TTS(model_name=model_name, progress_bar=True, gpu=use_gpu)
    print("   Model loaded")

    # Generate audio
    print(f"\nGenerating audio ({char_count:,} characters)...")

    if segments and not args.no_breaks:
        # Generate with proper break handling
        audio = generate_audio_with_breaks(tts, segments, voice_sample)
    else:
        # Fallback: generate without breaks (fast but loses pacing)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        try:
            if voice_sample and voice_sample.exists():
                tts.tts_to_file(
                    text=plain_text,
                    file_path=tmp_path,
                    speaker_wav=str(voice_sample),
                    language="en"
                )
            else:
                tts.tts_to_file(text=plain_text, file_path=tmp_path)
            audio = AudioSegment.from_wav(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    # Apply speed adjustment
    if args.speed != 1.0:
        print(f"\nAdjusting speed to {args.speed}x...")
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * args.speed)
        }).set_frame_rate(audio.frame_rate)

    # Normalize
    print("Normalizing audio...")
    audio = normalize(audio)

    # Export
    output_file = args.output_dir / "voice.mp3"
    audio.export(str(output_file), format="mp3", bitrate="192k")

    duration = len(audio) / 1000
    print(f"\nComplete! Duration: {duration/60:.1f} minutes")
    print(f"   Output: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
