#!/usr/bin/env python3
"""
Simple command-line wrapper for binaural beat generation
Used by bash scripts for creating individual binaural sections
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path so we can import audio modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.audio.binaural import generate, save_stem

# Import validation utilities
try:
    from utilities.validation import (
        validate_binaural_offset,
        validate_duration,
        validate_frequency,
        validate_output_path,
        validate_percentage,
    )
except ImportError:
    # Fallback to basic validation
    validate_binaural_offset = float
    validate_duration = lambda x: int(float(x))
    validate_frequency = float
    validate_output_path = str
    validate_percentage = float


def main():
    parser = argparse.ArgumentParser(description='Generate binaural beat audio')
    parser.add_argument('--frequency', type=validate_binaural_offset, required=True,
                       help='Binaural beat frequency in Hz (0.5-100, e.g., 10 for alpha, 5 for theta, 40 for gamma)')
    parser.add_argument('--duration', type=validate_duration, required=True,
                       help='Duration in seconds (30-10800)')
    parser.add_argument('--output', type=validate_output_path, required=True,
                       help='Output WAV file path')
    parser.add_argument('--carrier', type=validate_frequency, default=200,
                       help='Carrier frequency in Hz (default: 200)')
    parser.add_argument('--amplitude', type=validate_percentage, default=0.25,
                       help='Amplitude 0.0-1.0 (default: 0.25)')

    args = parser.parse_args()

    # Create single section with constant frequency
    sections = [{
        'start': 0,
        'end': args.duration,
        'freq_start': args.frequency,
        'freq_end': args.frequency,
        'transition': 'linear'
    }]

    # Generate binaural beats
    audio = generate(
        sections=sections,
        duration_sec=args.duration,
        carrier_freq=args.carrier,
        amplitude=args.amplitude,
        fade_in_sec=0.5,   # Short fade in
        fade_out_sec=0.5   # Short fade out
    )

    # Save to file
    save_stem(audio, args.output)

    return 0


if __name__ == '__main__':
    sys.exit(main())
