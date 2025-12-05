#!/usr/bin/env python3
"""
Binaural Beats Validation Utility

Validates binaural beat parameters in:
- Frequency map JSON files
- Session manifest.yaml files
- CLI-specified parameters

Checks against research-based optimal ranges for therapeutic effectiveness.

Usage:
    # Validate a frequency map JSON
    python3 validate_binaural.py --frequency-map session/binaural_map.json

    # Validate a session manifest
    python3 validate_binaural.py --manifest sessions/my-session/manifest.yaml

    # Validate specific parameters
    python3 validate_binaural.py --carrier 200 --beat-range 4-10 --duration 1800

    # List available presets and their parameters
    python3 validate_binaural.py --list-presets
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from core.audio.binaural import (
    BRAINWAVE_BANDS,
    CARRIER_FREQ_MIN,
    CARRIER_FREQ_MAX,
    CARRIER_FREQ_OPTIMAL_MIN,
    CARRIER_FREQ_OPTIMAL_MAX,
    BEAT_FREQ_MIN,
    BEAT_FREQ_MAX,
    BEAT_FREQ_THERAPEUTIC_MAX,
    MIN_ENTRAINMENT_DURATION_SEC,
    _validate_parameters,
    _get_brainwave_band,
    SectionDict,
    GammaBurstDict,
)


def print_brainwave_reference() -> None:
    """Print brainwave band reference table."""
    print("\n" + "=" * 60)
    print("BRAINWAVE FREQUENCY REFERENCE")
    print("=" * 60)
    print(f"{'Band':<12} {'Range (Hz)':<15} {'State'}")
    print("-" * 60)
    states = {
        'delta': 'Deep sleep, unconscious, body restoration',
        'theta': 'Meditation, creativity, trance, hypnosis',
        'alpha': 'Relaxed awareness, calm focus, light meditation',
        'beta': 'Active thinking, problem-solving, focus',
        'gamma': 'Higher cognition, insight binding, peak awareness',
    }
    for band, (low, high) in BRAINWAVE_BANDS.items():
        print(f"{band.capitalize():<12} {low:.1f}-{high:.1f} Hz{'':<6} {states.get(band, '')}")
    print("=" * 60 + "\n")


def print_validation_summary(
    carrier_freq: float,
    beat_freqs: List[float],
    duration_sec: float,
) -> None:
    """Print a summary of the parameters and their validity."""
    print("\n" + "=" * 60)
    print("BINAURAL PARAMETER SUMMARY")
    print("=" * 60)

    # Carrier frequency
    carrier_status = "✅ OPTIMAL" if CARRIER_FREQ_OPTIMAL_MIN <= carrier_freq <= CARRIER_FREQ_OPTIMAL_MAX else "⚠️  SUB-OPTIMAL"
    print(f"Carrier Frequency: {carrier_freq} Hz {carrier_status}")
    print(f"  Optimal range: {CARRIER_FREQ_OPTIMAL_MIN}-{CARRIER_FREQ_OPTIMAL_MAX} Hz")

    # Beat frequencies
    print(f"\nBeat Frequencies:")
    for freq in beat_freqs:
        band = _get_brainwave_band(freq)
        status = "✅" if BEAT_FREQ_MIN <= freq <= BEAT_FREQ_THERAPEUTIC_MAX else "⚠️ "
        print(f"  {status} {freq:.1f} Hz ({band})")

    # Duration
    duration_min = duration_sec / 60
    duration_status = "✅ SUFFICIENT" if duration_sec >= MIN_ENTRAINMENT_DURATION_SEC else "⚠️  SHORT"
    print(f"\nDuration: {duration_min:.1f} min {duration_status}")
    print(f"  Minimum for entrainment: {MIN_ENTRAINMENT_DURATION_SEC/60:.0f} min")

    print("=" * 60 + "\n")


def validate_frequency_map(path: Path) -> bool:
    """Validate a frequency map JSON file."""
    print(f"\nValidating frequency map: {path}")

    try:
        with open(path) as f:
            freq_map = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"❌ Error loading file: {e}")
        return False

    # Extract parameters
    carrier_freq = freq_map.get('base_carrier_frequency', 200)
    duration_sec = freq_map.get('total_duration', 0)

    sections: List[SectionDict] = []
    gamma_bursts: List[GammaBurstDict] = []

    for event in freq_map.get('frequency_events', []):
        sections.append({
            'start': event.get('timestamp', 0),
            'end': event.get('timestamp', 0) + event.get('duration', 0),
            'freq_start': event.get('frequency_start', 10),
            'freq_end': event.get('frequency_end', event.get('frequency_start', 10)),
        })

        if 'gamma_burst' in event:
            gb = event['gamma_burst']
            if gb.get('enabled', True):
                gamma_bursts.append({
                    'time': gb.get('timestamp', 0),
                    'duration': gb.get('duration', 3),
                    'frequency': gb.get('frequency', 40),
                })

    # Validate
    warnings = _validate_parameters(carrier_freq, sections, duration_sec, gamma_bursts)

    # Collect beat frequencies for summary
    beat_freqs = []
    for section in sections:
        beat_freqs.append(section.get('freq_start', 10))
        beat_freqs.append(section.get('freq_end', 10))
    beat_freqs = list(set(beat_freqs))

    print_validation_summary(carrier_freq, beat_freqs, duration_sec)

    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
        return False

    print("✅ All parameters are within optimal ranges.")
    return True


def validate_manifest(path: Path) -> bool:
    """Validate binaural settings in a session manifest."""
    print(f"\nValidating manifest: {path}")

    try:
        with open(path) as f:
            manifest = yaml.safe_load(f)
    except (yaml.YAMLError, FileNotFoundError) as e:
        print(f"❌ Error loading file: {e}")
        return False

    # Check if binaural is enabled
    binaural_config = manifest.get('sound_bed', {}).get('binaural', {})
    if not binaural_config.get('enabled', False):
        print("⚠️  Binaural beats are disabled in this manifest.")
        return True

    # Extract parameters
    carrier_freq = binaural_config.get('base_hz', 200)
    duration_sec = manifest.get('session', {}).get('duration', 0)

    sections: List[SectionDict] = []
    for sec in binaural_config.get('sections', []):
        sections.append({
            'start': sec.get('start', 0),
            'end': sec.get('end', 0),
            'freq_start': sec.get('offset_hz', 10),
            'freq_end': sec.get('offset_hz', 10),
        })

    # Extract gamma bursts from fx_timeline
    gamma_bursts: List[GammaBurstDict] = []
    for fx in manifest.get('fx_timeline', []):
        if fx.get('type') == 'gamma_flash':
            gamma_bursts.append({
                'time': fx.get('time', 0),
                'duration': fx.get('duration_s', 3),
                'frequency': fx.get('freq_hz', 40),
            })

    # Validate
    warnings = _validate_parameters(carrier_freq, sections, duration_sec, gamma_bursts)

    # Collect beat frequencies for summary
    beat_freqs = list(set(
        sec.get('offset_hz', 10) for sec in binaural_config.get('sections', [])
    ))

    print_validation_summary(carrier_freq, beat_freqs, duration_sec)

    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
        return False

    print("✅ All parameters are within optimal ranges.")
    return True


def list_presets() -> None:
    """List available binaural presets."""
    from generate_dynamic_binaural import PRESETS

    print("\n" + "=" * 70)
    print("AVAILABLE BINAURAL PRESETS")
    print("=" * 70)

    for name, preset in PRESETS.items():
        desc = preset.get('description', 'No description')
        carrier = preset.get('carrier_freq', 200)
        stages = preset.get('stages', [])

        # Calculate frequency range
        all_freqs = []
        for stage in stages:
            all_freqs.append(stage.get('freq_start', 10))
            all_freqs.append(stage.get('freq_end', 10))

        freq_min = min(all_freqs) if all_freqs else 0
        freq_max = max(all_freqs) if all_freqs else 0

        has_gamma = any('gamma_burst' in s for s in stages)
        has_dual = 'dual_layer' in preset
        has_breath = 'enhancements' in preset and preset['enhancements'].get('breath_sync', {}).get('enabled')

        features = []
        if has_gamma:
            features.append("gamma-burst")
        if has_dual:
            features.append("dual-layer")
        if has_breath:
            features.append("breath-sync")

        feature_str = f" [{', '.join(features)}]" if features else ""

        print(f"\n{name}{feature_str}")
        print(f"  {desc}")
        print(f"  Carrier: {carrier} Hz | Beat range: {freq_min:.1f}-{freq_max:.1f} Hz | Stages: {len(stages)}")

    print("\n" + "=" * 70)
    print("Usage: python3 generate_dynamic_binaural.py --preset <name> --duration <sec>")
    print("=" * 70 + "\n")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate binaural beat parameters against research-based optimal ranges.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --frequency-map session/binaural_map.json
  %(prog)s --manifest sessions/my-session/manifest.yaml
  %(prog)s --carrier 200 --beat-range 4-10 --duration 1800
  %(prog)s --list-presets
  %(prog)s --reference
        """
    )

    parser.add_argument('--frequency-map', type=Path, help='Path to frequency map JSON file')
    parser.add_argument('--manifest', type=Path, help='Path to session manifest.yaml')
    parser.add_argument('--carrier', type=float, help='Carrier frequency in Hz')
    parser.add_argument('--beat-range', type=str, help='Beat frequency range (e.g., "4-10")')
    parser.add_argument('--duration', type=float, help='Session duration in seconds')
    parser.add_argument('--list-presets', action='store_true', help='List available presets')
    parser.add_argument('--reference', action='store_true', help='Show brainwave frequency reference')

    args = parser.parse_args()

    if args.reference:
        print_brainwave_reference()
        return 0

    if args.list_presets:
        list_presets()
        return 0

    if args.frequency_map:
        success = validate_frequency_map(args.frequency_map)
        return 0 if success else 1

    if args.manifest:
        success = validate_manifest(args.manifest)
        return 0 if success else 1

    if args.carrier or args.beat_range or args.duration:
        carrier = args.carrier or 200
        duration = args.duration or 1800

        beat_freqs = [6.0]  # Default
        if args.beat_range:
            try:
                parts = args.beat_range.split('-')
                beat_freqs = [float(parts[0]), float(parts[1])]
            except (ValueError, IndexError):
                print(f"❌ Invalid beat-range format: {args.beat_range}")
                print("   Use format: '4-10' for 4 Hz to 10 Hz")
                return 1

        sections: List[SectionDict] = [{
            'start': 0,
            'end': int(duration),
            'freq_start': beat_freqs[0],
            'freq_end': beat_freqs[-1],
        }]

        warnings = _validate_parameters(carrier, sections, duration, None)
        print_validation_summary(carrier, beat_freqs, duration)

        if warnings:
            print("WARNINGS:")
            for warning in warnings:
                print(f"  {warning}")
            return 1

        print("✅ All parameters are within optimal ranges.")
        return 0

    # No arguments - show reference
    print_brainwave_reference()
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
