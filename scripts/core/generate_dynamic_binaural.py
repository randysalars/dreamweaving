#!/usr/bin/env python3
"""
Dynamic Binaural Generator

Generates binaural beats with dynamic frequency progressions based on:
1. Frequency map JSON files (most detailed)
2. Manifest progression definitions
3. Preset progressions (standard_hypnotic, neuroplasticity, sleep, etc.)

This addresses the key learning that static frequencies miss the hypnotic arc.

Usage:
    # From frequency map JSON
    python3 generate_dynamic_binaural.py --frequency-map session/binaural_frequency_map.json --output output/binaural.wav

    # From manifest
    python3 generate_dynamic_binaural.py --manifest session/manifest.yaml --output output/binaural.wav

    # From preset
    python3 generate_dynamic_binaural.py --preset neuroplasticity --duration 1800 --output output/binaural.wav

    # Generate frequency map template
    python3 generate_dynamic_binaural.py --generate-template --duration 1800 --preset neuroplasticity --output template.json
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

import yaml

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.audio.binaural import generate, save_stem, SectionDict, GammaBurstDict


# ============================================================================
# PRESET PROGRESSIONS
# ============================================================================

PRESETS = {
    "standard_hypnotic": {
        "description": "Standard hypnotic session arc",
        "carrier_freq": 200,
        "stages": [
            {"name": "pretalk", "pct": 10, "freq_start": 12, "freq_end": 12},
            {"name": "induction", "pct": 15, "freq_start": 12, "freq_end": 8, "transition": "logarithmic"},
            {"name": "deepening", "pct": 10, "freq_start": 8, "freq_end": 6, "transition": "logarithmic"},
            {"name": "journey", "pct": 40, "freq_start": 6, "freq_end": 6, "modulation": {"range": 0.3, "rate": 0.05}},
            {"name": "integration", "pct": 15, "freq_start": 6, "freq_end": 10, "transition": "logarithmic"},
            {"name": "awakening", "pct": 10, "freq_start": 10, "freq_end": 12},
        ]
    },

    "neuroplasticity": {
        "description": "Neuroplasticity session with gamma burst (Neural Network Navigator style)",
        "carrier_freq": 200,
        "stages": [
            {"name": "pretalk", "pct": 9, "freq_start": 12, "freq_end": 12},
            {"name": "induction_alpha", "pct": 7, "freq_start": 12, "freq_end": 8, "transition": "logarithmic"},
            {"name": "induction_theta", "pct": 9, "freq_start": 8, "freq_end": 7, "transition": "logarithmic"},
            {"name": "neural_garden", "pct": 16, "freq_start": 7, "freq_end": 7, "modulation": {"range": 0.3, "rate": 0.05}},
            {"name": "pathfinder", "pct": 16, "freq_start": 7, "freq_end": 6, "transition": "linear"},
            {"name": "weaver", "pct": 16, "freq_start": 6, "freq_end": 6, "gamma_burst": {"pct": 67, "duration": 3, "freq": 40}},
            {"name": "consolidation", "pct": 13, "freq_start": 7, "freq_end": 10, "transition": "logarithmic"},
            {"name": "awakening", "pct": 14, "freq_start": 10, "freq_end": 10},
        ]
    },

    "deep_sleep": {
        "description": "Deep sleep induction with delta waves",
        "carrier_freq": 150,
        "stages": [
            {"name": "relaxation", "pct": 15, "freq_start": 10, "freq_end": 10},
            {"name": "deepening", "pct": 25, "freq_start": 10, "freq_end": 6, "transition": "logarithmic"},
            {"name": "sleep_transition", "pct": 30, "freq_start": 6, "freq_end": 3, "transition": "logarithmic"},
            {"name": "deep_sleep", "pct": 30, "freq_start": 3, "freq_end": 1.5, "transition": "logarithmic"},
        ]
    },

    "confidence": {
        "description": "Confidence/activation session with energized return",
        "carrier_freq": 220,
        "stages": [
            {"name": "energized_intro", "pct": 10, "freq_start": 14, "freq_end": 14},
            {"name": "relaxation", "pct": 15, "freq_start": 14, "freq_end": 10},
            {"name": "visualization", "pct": 50, "freq_start": 10, "freq_end": 7, "transition": "logarithmic"},
            {"name": "integration", "pct": 15, "freq_start": 7, "freq_end": 10},
            {"name": "activation", "pct": 10, "freq_start": 10, "freq_end": 14},
        ]
    },

    "healing": {
        "description": "Healing journey with extended theta",
        "carrier_freq": 180,
        "stages": [
            {"name": "opening", "pct": 10, "freq_start": 10, "freq_end": 10},
            {"name": "descent", "pct": 15, "freq_start": 10, "freq_end": 6, "transition": "logarithmic"},
            {"name": "healing_space", "pct": 50, "freq_start": 6, "freq_end": 6, "modulation": {"range": 0.5, "rate": 0.03}},
            {"name": "integration", "pct": 15, "freq_start": 6, "freq_end": 10, "transition": "logarithmic"},
            {"name": "return", "pct": 10, "freq_start": 10, "freq_end": 10},
        ]
    },

    "static_theta": {
        "description": "Simple static theta (use for quick tests)",
        "carrier_freq": 200,
        "stages": [
            {"name": "theta", "pct": 100, "freq_start": 6, "freq_end": 6},
        ]
    },
}


# ============================================================================
# FREQUENCY MAP PARSING
# ============================================================================

def load_frequency_map(path: Path) -> Dict[str, Any]:
    """Load a frequency map JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def frequency_map_to_sections(
    freq_map: Dict[str, Any],
    duration_sec: float
) -> tuple[List[SectionDict], List[GammaBurstDict], float]:
    """
    Convert a frequency map to sections and gamma bursts.

    Returns:
        Tuple of (sections, gamma_bursts, carrier_freq)
    """
    sections: List[SectionDict] = []
    gamma_bursts: List[GammaBurstDict] = []

    carrier_freq = freq_map.get('base_carrier_frequency', 200)

    for event in freq_map.get('frequency_events', []):
        section: SectionDict = {
            'start': event['timestamp'],
            'end': event['timestamp'] + event['duration'],
            'freq_start': event['frequency_start'],
            'freq_end': event.get('frequency_end', event['frequency_start']),
            'transition': event.get('transition_type', 'linear'),
        }
        sections.append(section)

        # Check for gamma burst in this event
        if 'gamma_burst' in event:
            gb = event['gamma_burst']
            if gb.get('enabled', True):
                gamma_bursts.append({
                    'time': gb['timestamp'],
                    'duration': gb['duration'],
                    'frequency': gb['frequency'],
                })

    return sections, gamma_bursts, carrier_freq


def manifest_to_sections(
    manifest: Dict[str, Any],
    duration_sec: float
) -> tuple[List[SectionDict], List[GammaBurstDict], float]:
    """
    Convert manifest binaural config to sections.

    Supports both simple beat_frequency and progression definitions.
    """
    sections: List[SectionDict] = []
    gamma_bursts: List[GammaBurstDict] = []

    binaural_config = manifest.get('audio', {}).get('binaural', {})

    if not binaural_config.get('enabled', True):
        return [], [], 200

    carrier_freq = binaural_config.get('base_frequency', 200)

    # Check for progression definition
    if 'progression' in binaural_config:
        progression = binaural_config['progression']
        for i, stage in enumerate(progression):
            # Get end time from next stage or duration
            if i + 1 < len(progression):
                end_time = progression[i + 1].get('timestamp', duration_sec)
            else:
                end_time = duration_sec

            section: SectionDict = {
                'start': stage['timestamp'],
                'end': end_time,
                'freq_start': stage['frequency'],
                'freq_end': stage.get('frequency_end', stage['frequency']),
                'transition': stage.get('transition', 'linear'),
            }
            sections.append(section)

            # Check for gamma burst
            if stage.get('transition') == 'burst':
                gamma_bursts.append({
                    'time': stage['timestamp'],
                    'duration': stage.get('duration', 3),
                    'frequency': stage['frequency'],
                })
    else:
        # Simple static frequency
        beat_freq = binaural_config.get('beat_frequency', 6)
        sections.append({
            'start': 0,
            'end': duration_sec,
            'freq_start': beat_freq,
            'freq_end': beat_freq,
            'transition': 'hold',
        })

    return sections, gamma_bursts, carrier_freq


def preset_to_sections(
    preset_name: str,
    duration_sec: float
) -> tuple[List[SectionDict], List[GammaBurstDict], float]:
    """
    Convert a preset progression to sections.
    """
    if preset_name not in PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(PRESETS.keys())}")

    preset = PRESETS[preset_name]
    sections: List[SectionDict] = []
    gamma_bursts: List[GammaBurstDict] = []

    carrier_freq = preset.get('carrier_freq', 200)

    current_time = 0
    for stage in preset['stages']:
        stage_duration = duration_sec * (stage['pct'] / 100)

        section: SectionDict = {
            'start': int(current_time),
            'end': int(current_time + stage_duration),
            'freq_start': stage['freq_start'],
            'freq_end': stage['freq_end'],
            'transition': stage.get('transition', 'linear'),
        }
        sections.append(section)

        # Check for gamma burst
        if 'gamma_burst' in stage:
            gb = stage['gamma_burst']
            burst_time = current_time + (stage_duration * gb['pct'] / 100)
            gamma_bursts.append({
                'time': int(burst_time),
                'duration': gb['duration'],
                'frequency': gb['freq'],
            })

        current_time += stage_duration

    return sections, gamma_bursts, carrier_freq


# ============================================================================
# FREQUENCY MAP TEMPLATE GENERATION
# ============================================================================

def generate_frequency_map_template(
    duration_sec: float,
    preset_name: str = "standard_hypnotic",
    session_name: str = "my_session"
) -> Dict[str, Any]:
    """
    Generate a frequency map JSON template for a session.
    """
    sections, gamma_bursts, carrier_freq = preset_to_sections(preset_name, duration_sec)

    preset = PRESETS[preset_name]

    frequency_events = []
    current_time = 0

    for i, (section, stage) in enumerate(zip(sections, preset['stages'])):
        event = {
            "timestamp": section['start'],
            "duration": section['end'] - section['start'],
            "frequency_start": section['freq_start'],
            "frequency_end": section['freq_end'],
            "state": _freq_to_state(section['freq_start']),
            "script_section": stage['name'],
            "description": _generate_description(stage),
            "transition_type": section['transition'],
            "sync_points": [
                {
                    "time": section['start'],
                    "event": f"{stage['name']}_start",
                    "frequency": section['freq_start'],
                    "note": f"Beginning of {stage['name'].replace('_', ' ')}"
                }
            ]
        }

        # Add modulation if present
        if 'modulation' in stage:
            event['modulation'] = {
                "enabled": True,
                "range": stage['modulation']['range'],
                "frequency_hz": stage['modulation']['rate'],
                "description": f"Subtle oscillation for enhanced entrainment"
            }

        # Add gamma burst if present
        for gb in gamma_bursts:
            if section['start'] <= gb['time'] < section['end']:
                event['gamma_burst'] = {
                    "enabled": True,
                    "timestamp": gb['time'],
                    "duration": gb['duration'],
                    "frequency": gb['frequency'],
                    "description": f"{gb['duration']}-second {gb['frequency']} Hz gamma burst for insight moment",
                    "fade_in": 0.2,
                    "fade_out": 0.5,
                    "volume_boost_db": 2,
                    "critical_sync": "Synchronize with script insight moment and visual pulse"
                }

        frequency_events.append(event)

    template = {
        "session": session_name,
        "duration_seconds": int(duration_sec),
        "base_carrier_frequency": carrier_freq,
        "description": preset['description'],
        "frequency_events": frequency_events,
        "technical_specifications": {
            "carrier_frequency": carrier_freq,
            "volume_envelope": {
                "fade_in": 5,
                "fade_out": 8,
                "base_volume_db": -20
            },
            "stereo_field": {
                "carrier_left_pan": -1.0,
                "carrier_right_pan": 1.0,
                "width": 1.0
            },
            "export_format": {
                "sample_rate": 48000,
                "bit_depth": 24,
                "format": "wav"
            }
        },
        "neuroscience_rationale": {
            "delta_1-4hz": "Deep sleep, healing, regeneration",
            "theta_4-8hz": "Deep meditation, vivid imagery, neuroplasticity",
            "alpha_8-14hz": "Relaxed alertness, light meditation, integration",
            "beta_14-30hz": "Active thinking, focus, awakening",
            "gamma_30-100hz": "Peak insight, integration, binding of information"
        }
    }

    return template


def _freq_to_state(freq: float) -> str:
    """Convert frequency to brainwave state name."""
    if freq < 4:
        return "delta"
    elif freq < 8:
        return "theta"
    elif freq < 14:
        return "alpha"
    elif freq < 30:
        return "beta"
    else:
        return "gamma"


def _generate_description(stage: Dict) -> str:
    """Generate a description for a stage."""
    freq_start = stage['freq_start']
    freq_end = stage['freq_end']
    name = stage['name'].replace('_', ' ')

    if freq_start == freq_end:
        state = _freq_to_state(freq_start)
        return f"{name.title()}: {state} state at {freq_start} Hz"
    else:
        state_start = _freq_to_state(freq_start)
        state_end = _freq_to_state(freq_end)
        return f"{name.title()}: {state_start} to {state_end} transition ({freq_start}→{freq_end} Hz)"


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate dynamic binaural beats with frequency progressions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From frequency map JSON (most detailed control)
  %(prog)s --frequency-map session/binaural_frequency_map.json --output output/binaural.wav

  # From manifest with progression
  %(prog)s --manifest session/manifest.yaml --output output/binaural.wav

  # From preset
  %(prog)s --preset neuroplasticity --duration 1800 --output output/binaural.wav

  # Generate template for manual editing
  %(prog)s --generate-template --preset neuroplasticity --duration 1800 --output template.json

Available presets: """ + ", ".join(PRESETS.keys())
    )

    # Input sources (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--frequency-map', type=Path,
                            help='Path to frequency map JSON file')
    input_group.add_argument('--manifest', type=Path,
                            help='Path to session manifest.yaml')
    input_group.add_argument('--preset', choices=list(PRESETS.keys()),
                            help='Use a preset progression')
    input_group.add_argument('--generate-template', action='store_true',
                            help='Generate a frequency map template')

    # Output
    parser.add_argument('--output', type=Path, required=True,
                       help='Output file path (.wav for audio, .json for template)')

    # Duration (required for preset and template)
    parser.add_argument('--duration', type=float,
                       help='Duration in seconds (required for preset/template)')

    # Options
    parser.add_argument('--carrier', type=float, default=None,
                       help='Override carrier frequency (Hz)')
    parser.add_argument('--amplitude', type=float, default=0.3,
                       help='Amplitude 0.0-1.0 (default: 0.3)')
    parser.add_argument('--session-name', default='my_session',
                       help='Session name for template generation')
    parser.add_argument('--template-preset', choices=list(PRESETS.keys()),
                       default='standard_hypnotic',
                       help='Preset to use for template generation (default: standard_hypnotic)')

    args = parser.parse_args()

    # Generate template
    if args.generate_template:
        if not args.duration:
            parser.error("--duration is required with --generate-template")

        preset = args.template_preset
        template = generate_frequency_map_template(
            args.duration,
            preset,
            args.session_name
        )

        with open(args.output, 'w') as f:
            json.dump(template, f, indent=2)

        print(f"✓ Generated frequency map template: {args.output}")
        print(f"  Preset: {preset}")
        print(f"  Duration: {args.duration/60:.1f} minutes")
        print(f"  Stages: {len(template['frequency_events'])}")
        return 0

    # Get sections from input source
    if args.frequency_map:
        freq_map = load_frequency_map(args.frequency_map)
        duration = freq_map.get('duration_seconds', args.duration)
        if not duration:
            parser.error("Duration not found in frequency map; use --duration")
        sections, gamma_bursts, carrier_freq = frequency_map_to_sections(freq_map, duration)

    elif args.manifest:
        with open(args.manifest, 'r') as f:
            manifest = yaml.safe_load(f)
        duration = manifest.get('duration', args.duration)
        if duration:
            duration = duration * 60  # Convert minutes to seconds
        if not duration:
            parser.error("Duration not found in manifest; use --duration")
        sections, gamma_bursts, carrier_freq = manifest_to_sections(manifest, duration)

    elif args.preset:
        if not args.duration:
            parser.error("--duration is required with --preset")
        duration = args.duration
        sections, gamma_bursts, carrier_freq = preset_to_sections(args.preset, duration)

    # Override carrier if specified
    if args.carrier:
        carrier_freq = args.carrier

    # Generate audio
    print("=" * 70)
    print("DYNAMIC BINAURAL GENERATOR")
    print("=" * 70)
    print(f"\nDuration: {duration/60:.1f} minutes")
    print(f"Carrier: {carrier_freq} Hz")
    print(f"Sections: {len(sections)}")
    if gamma_bursts:
        print(f"Gamma bursts: {len(gamma_bursts)}")
    print()

    audio = generate(
        sections=sections,
        duration_sec=duration,
        carrier_freq=carrier_freq,
        amplitude=args.amplitude,
        gamma_bursts=gamma_bursts if gamma_bursts else None
    )

    # Save
    save_stem(audio, args.output)

    print("\n" + "=" * 70)
    print("✓ DYNAMIC BINAURAL GENERATION COMPLETE")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
