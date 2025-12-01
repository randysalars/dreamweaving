#!/usr/bin/env python3
"""
Simple command-line wrapper for pink noise generation
Used by bash scripts for creating ambient pads

Now supports caching - checks for pre-generated pink noise in assets/
and trims to needed duration instead of regenerating
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

# Add parent directory to path so we can import audio modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.audio.pink_noise import generate, save_stem

# Import validation utilities
try:
    from utilities.validation import (
        validate_duration,
        validate_output_path,
        validate_percentage,
    )
except ImportError:
    # Fallback to basic validation
    validate_duration = lambda x: int(float(x))
    validate_output_path = str
    validate_percentage = float


def get_project_root():
    """Find project root (directory containing assets/)"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up from scripts/core/ to project root
    return os.path.dirname(os.path.dirname(script_dir))


def find_cached_pink_noise(duration_sec):
    """
    Look for cached pink noise files that are long enough
    Returns path if found, None otherwise
    """
    project_root = get_project_root()
    assets_dir = os.path.join(project_root, 'assets', 'audio', 'ambient')

    if not os.path.exists(assets_dir):
        return None

    # Look for pink noise files
    for filename in os.listdir(assets_dir):
        if filename.startswith('pink_noise_') and filename.endswith('.wav'):
            filepath = os.path.join(assets_dir, filename)

            # Get duration using ffprobe
            try:
                result = subprocess.run(
                    ['ffprobe', '-v', 'error', '-show_entries',
                     'format=duration', '-of',
                     'default=noprint_wrappers=1:nokey=1', filepath],
                    capture_output=True,
                    text=True,
                    check=True
                )
                file_duration = float(result.stdout.strip())

                # If this file is long enough, use it
                if file_duration >= duration_sec:
                    return filepath, file_duration

            except (subprocess.CalledProcessError, ValueError):
                continue

    return None


def trim_audio(input_path, output_path, duration_sec):
    """Trim audio file to specified duration using ffmpeg"""
    cmd = [
        'ffmpeg', '-i', input_path,
        '-t', str(duration_sec),
        '-c', 'copy',
        '-y', output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def main():
    parser = argparse.ArgumentParser(description='Generate pink noise ambient pad')
    parser.add_argument('--duration', type=validate_duration, required=True,
                       help='Duration in seconds (30-10800)')
    parser.add_argument('--output', type=validate_output_path, required=True,
                       help='Output WAV file path')
    parser.add_argument('--amplitude', type=validate_percentage, default=0.15,
                       help='Amplitude 0.0-1.0 (default: 0.15)')
    parser.add_argument('--stereo-variation', action='store_true', default=True,
                       help='Enable stereo variation (default: True)')
    parser.add_argument('--force-generate', action='store_true',
                       help='Force generation instead of using cached asset')

    args = parser.parse_args()

    # Try to use cached pink noise unless forced to generate
    if not args.force_generate:
        cached = find_cached_pink_noise(args.duration)
        if cached:
            cached_path, cached_duration = cached
            print(f"✓ Using cached pink noise: {os.path.basename(cached_path)}")
            print(f"  Cached duration: {cached_duration/60:.1f} min")
            print(f"  Trimming to: {args.duration/60:.1f} min")

            try:
                trim_audio(cached_path, args.output, args.duration)
                print(f"✓ Trimmed pink noise saved: {args.output}")
                return 0
            except subprocess.CalledProcessError:
                print("⚠ Failed to trim cached audio, generating fresh...")

    # Generate pink noise (fallback or forced)
    print(f"Generating pink noise: {args.duration/60:.1f} min")
    audio = generate(
        duration_sec=args.duration,
        amplitude=args.amplitude,
        fade_in_sec=5.0,
        fade_out_sec=8.0,
        stereo_variation=args.stereo_variation
    )

    # Save to file
    save_stem(audio, args.output)

    return 0


if __name__ == '__main__':
    sys.exit(main())
