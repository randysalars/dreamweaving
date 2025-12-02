#!/usr/bin/env python3
"""
Dreamweaving Production Voice Generator

This is the CANONICAL script for generating voice tracks. It automatically:
1. Uses the production standard voice (en-US-Neural2-H - bright female)
2. Applies voice enhancement for natural, warm sound
3. Outputs both WAV and MP3 formats

ALWAYS use this script for voice generation to ensure consistency.

Usage:
    python scripts/core/generate_voice.py <script.ssml> <output_dir>
    python scripts/core/generate_voice.py sessions/my-session/working_files/script.ssml sessions/my-session/output

Options:
    --voice         Override voice (default: en-US-Neural2-H)
    --rate          Speaking rate (default: 0.88)
    --pitch         Pitch in semitones (default: 0)
    --skip-enhance  Skip voice enhancement (not recommended)
    --enhance-only  Only run enhancement on existing voice.mp3

Examples:
    # Standard production voice generation
    python scripts/core/generate_voice.py sessions/iron-soul-forge/working_files/script.ssml sessions/iron-soul-forge/output

    # Custom settings (still applies enhancement)
    python scripts/core/generate_voice.py script.ssml output/ --rate 0.85 --pitch -1
"""

import argparse
import os
import sys
import subprocess
import shutil
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.core.generate_audio_chunked import synthesize_ssml_file_chunked
from scripts.core.audio.voice_enhancement import enhance_voice


# =============================================================================
# PRODUCTION VOICE SETTINGS
# =============================================================================

PRODUCTION_VOICE = {
    'name': 'en-US-Neural2-H',      # Bright, clear female voice
    'speaking_rate': 0.88,           # Slightly slow for clarity
    'pitch': 0.0,                    # Natural pitch (not lowered)
    'sample_rate_hz': 24000,
    'effects_profile': ['headphone-class-device'],
}

ENHANCEMENT_SETTINGS = {
    'apply_warmth': True,
    'apply_deessing': True,
    'add_whisper': True,
    'add_double': True,
    'add_breath': False,
    'add_room': True,
    'add_micropan': True,
    'add_subharmonic': True,
    'add_cuddle_waves': False,       # Disabled due to FFmpeg compatibility
    'warmth_drive': 0.3,
    'whisper_db': -24,
    'double_db': -16,
    'double_delay_ms': 8,
    'room_amount': 0.04,
    'micropan_amount': 0.03,
    'subharmonic_db': -14,
}


def print_header():
    """Print script header."""
    print("=" * 70)
    print("   DREAMWEAVING PRODUCTION VOICE GENERATOR")
    print("   Consistent voice + automatic enhancement")
    print("=" * 70)
    print()


def print_settings(voice_name, speaking_rate, pitch, enhance):
    """Print current settings."""
    print("Production Settings:")
    print(f"  Voice: {voice_name}")
    print(f"  Speaking Rate: {speaking_rate}x")
    print(f"  Pitch: {pitch} semitones")
    print(f"  Enhancement: {'Enabled' if enhance else 'Disabled'}")
    print()


def generate_voice(
    ssml_path: str,
    output_dir: str,
    voice_name: str = None,
    speaking_rate: float = None,
    pitch: float = None,
    apply_enhancement: bool = True,
    enhance_only: bool = False
) -> dict:
    """
    Generate production-quality voice track with enhancement.

    Args:
        ssml_path: Path to SSML script
        output_dir: Output directory
        voice_name: Override voice (default: production voice)
        speaking_rate: Override speaking rate
        pitch: Override pitch
        apply_enhancement: Whether to apply voice enhancement
        enhance_only: Only run enhancement on existing voice.mp3

    Returns:
        Dict with output file paths and metadata
    """
    # Use production defaults if not overridden
    voice_name = voice_name or PRODUCTION_VOICE['name']
    speaking_rate = speaking_rate if speaking_rate is not None else PRODUCTION_VOICE['speaking_rate']
    pitch = pitch if pitch is not None else PRODUCTION_VOICE['pitch']

    # Ensure output directory exists
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Output file paths
    voice_raw_mp3 = output_dir / "voice.mp3"
    voice_enhanced_wav = output_dir / "voice_enhanced.wav"
    voice_enhanced_mp3 = output_dir / "voice_enhanced.mp3"

    result = {
        'voice_raw': str(voice_raw_mp3),
        'voice_enhanced_wav': str(voice_enhanced_wav),
        'voice_enhanced_mp3': str(voice_enhanced_mp3),
        'voice_name': voice_name,
        'speaking_rate': speaking_rate,
        'pitch': pitch,
        'enhanced': apply_enhancement,
    }

    # Step 1: Generate raw TTS voice (unless enhance_only)
    if not enhance_only:
        print("STEP 1: Generating TTS voice...")
        print("-" * 40)

        synthesize_ssml_file_chunked(
            ssml_filepath=ssml_path,
            output_filepath=str(voice_raw_mp3),
            voice_name=voice_name,
            speaking_rate=speaking_rate,
            pitch=pitch,
            sample_rate_hz=PRODUCTION_VOICE['sample_rate_hz'],
            effects_profile_id=PRODUCTION_VOICE['effects_profile']
        )

        if not voice_raw_mp3.exists():
            print("ERROR: Voice generation failed!")
            return None

        print()

    # Step 2: Apply voice enhancement
    if apply_enhancement:
        print("STEP 2: Applying voice enhancement...")
        print("-" * 40)

        if not voice_raw_mp3.exists():
            print(f"ERROR: Raw voice file not found: {voice_raw_mp3}")
            return None

        enhance_voice(
            input_path=str(voice_raw_mp3),
            output_path=str(voice_enhanced_wav),
            **ENHANCEMENT_SETTINGS
        )

        if not voice_enhanced_wav.exists():
            print("ERROR: Voice enhancement failed!")
            return None

        # Convert enhanced WAV to MP3
        print("\nConverting enhanced voice to MP3...")
        cmd = [
            'ffmpeg', '-y',
            '-i', str(voice_enhanced_wav),
            '-c:a', 'libmp3lame',
            '-b:a', '192k',
            str(voice_enhanced_mp3)
        ]
        subprocess.run(cmd, capture_output=True)

        if voice_enhanced_mp3.exists():
            print(f"  ✓ MP3 created: {voice_enhanced_mp3}")
        else:
            print("  ✗ MP3 conversion failed")

    # Get duration
    try:
        probe_cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(voice_enhanced_mp3 if apply_enhancement else voice_raw_mp3)
        ]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        duration = float(probe_result.stdout.strip())
        result['duration_seconds'] = duration
        result['duration_minutes'] = duration / 60
    except (ValueError, subprocess.SubprocessError):
        result['duration_seconds'] = 0
        result['duration_minutes'] = 0

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Dreamweaving Production Voice Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard production voice
  python generate_voice.py sessions/my-session/working_files/script.ssml sessions/my-session/output

  # Custom rate and pitch
  python generate_voice.py script.ssml output/ --rate 0.85 --pitch -1

  # Only enhance existing voice.mp3
  python generate_voice.py script.ssml output/ --enhance-only
        """
    )

    parser.add_argument('ssml_path', help="Path to SSML script file")
    parser.add_argument('output_dir', help="Output directory for voice files")
    parser.add_argument('--voice', default=None,
                       help=f"Voice name (default: {PRODUCTION_VOICE['name']})")
    parser.add_argument('--rate', type=float, default=None,
                       help=f"Speaking rate (default: {PRODUCTION_VOICE['speaking_rate']})")
    parser.add_argument('--pitch', type=float, default=None,
                       help=f"Pitch in semitones (default: {PRODUCTION_VOICE['pitch']})")
    parser.add_argument('--skip-enhance', action='store_true',
                       help="Skip voice enhancement (not recommended)")
    parser.add_argument('--enhance-only', action='store_true',
                       help="Only run enhancement on existing voice.mp3")

    args = parser.parse_args()

    # Validate input
    if not args.enhance_only and not Path(args.ssml_path).exists():
        print(f"ERROR: SSML file not found: {args.ssml_path}")
        sys.exit(1)

    print_header()
    print_settings(
        args.voice or PRODUCTION_VOICE['name'],
        args.rate or PRODUCTION_VOICE['speaking_rate'],
        args.pitch or PRODUCTION_VOICE['pitch'],
        not args.skip_enhance
    )

    result = generate_voice(
        ssml_path=args.ssml_path,
        output_dir=args.output_dir,
        voice_name=args.voice,
        speaking_rate=args.rate,
        pitch=args.pitch,
        apply_enhancement=not args.skip_enhance,
        enhance_only=args.enhance_only
    )

    if result:
        print()
        print("=" * 70)
        print("✅ VOICE GENERATION COMPLETE")
        print("=" * 70)
        print()
        print("Output Files:")
        print(f"  Raw voice:      {result['voice_raw']}")
        if result['enhanced']:
            print(f"  Enhanced (WAV): {result['voice_enhanced_wav']}")
            print(f"  Enhanced (MP3): {result['voice_enhanced_mp3']}")
        print()
        print(f"Duration: {result['duration_minutes']:.1f} minutes")
        print(f"Voice: {result['voice_name']}")
        print()
        print("🎧 Use the enhanced MP3 for production!")
    else:
        print()
        print("❌ Voice generation failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
