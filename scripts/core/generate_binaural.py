#!/usr/bin/env python3
"""
Simple command-line wrapper for binaural beat generation
Used by bash scripts for creating individual binaural sections
"""

import argparse
import sys
import os

# Add parent directory to path so we can import audio modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.audio.binaural import generate, save_stem


def main():
    parser = argparse.ArgumentParser(description='Generate binaural beat audio')
    parser.add_argument('--frequency', type=float, required=True,
                       help='Binaural beat frequency in Hz (e.g., 10 for alpha, 5 for theta, 40 for gamma)')
    parser.add_argument('--duration', type=float, required=True,
                       help='Duration in seconds')
    parser.add_argument('--output', type=str, required=True,
                       help='Output WAV file path')
    parser.add_argument('--carrier', type=float, default=200,
                       help='Carrier frequency in Hz (default: 200)')
    parser.add_argument('--amplitude', type=float, default=0.3,
                       help='Amplitude 0.0-1.0 (default: 0.3)')

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
