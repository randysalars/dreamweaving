#!/usr/bin/env python3
"""
Binaural Preset Loader

Loads binaural presets from knowledge/audio/binaural_presets.yaml and converts them
to the format expected by generate_dynamic_binaural.py.

This bridges the ~95 documented presets in the knowledge base to the binaural generator.

Usage:
    from scripts.core.audio.binaural_preset_loader import (
        load_preset, list_presets, get_presets_by_outcome, get_preset_info
    )

    # Load a preset for a 25-minute session
    preset = load_preset("healing_deep")

    # List all available presets
    presets = list_presets()

    # Find presets for a specific outcome
    healing_presets = get_presets_by_outcome("healing")
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Type aliases for clarity
PresetDict = Dict[str, Any]
StageDict = Dict[str, Any]
GammaBurstDict = Dict[str, Any]
OverlayDict = Dict[str, Any]


# =============================================================================
# PATHS
# =============================================================================

def _get_presets_path() -> Path:
    """Get the path to the binaural presets YAML file."""
    # Try relative to this file first
    this_dir = Path(__file__).parent.resolve()
    project_root = this_dir.parent.parent.parent  # scripts/core/audio -> project root

    presets_path = project_root / "knowledge" / "audio" / "binaural_presets.yaml"
    if presets_path.exists():
        return presets_path

    # Fallback: try from current working directory
    cwd_path = Path.cwd() / "knowledge" / "audio" / "binaural_presets.yaml"
    if cwd_path.exists():
        return cwd_path

    raise FileNotFoundError(
        f"Could not find binaural_presets.yaml. Searched:\n"
        f"  - {presets_path}\n"
        f"  - {cwd_path}"
    )


# =============================================================================
# YAML LOADING
# =============================================================================

_cached_data: Optional[Dict[str, Any]] = None


def _load_yaml_data() -> Dict[str, Any]:
    """Load and cache the YAML data."""
    global _cached_data
    if _cached_data is None:
        presets_path = _get_presets_path()
        with open(presets_path, 'r', encoding='utf-8') as f:
            _cached_data = yaml.safe_load(f)
    return _cached_data


def _clear_cache() -> None:
    """Clear the cached data (useful for testing)."""
    global _cached_data
    _cached_data = None


# =============================================================================
# TIME PARSING
# =============================================================================

def _parse_time(time_str: str) -> float:
    """
    Parse a time string (MM:SS or HH:MM:SS) to seconds.

    Examples:
        "00:00" -> 0.0
        "03:30" -> 210.0
        "1:30:00" -> 5400.0
    """
    parts = time_str.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return float(minutes) * 60 + float(seconds)
    elif len(parts) == 3:
        hours, minutes, seconds = parts
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    else:
        raise ValueError(f"Invalid time format: {time_str}")


def _seconds_to_time(seconds: float) -> str:
    """Convert seconds to MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


# =============================================================================
# PRESET CONVERSION
# =============================================================================

def _get_progression(preset: PresetDict) -> List[Dict[str, Any]]:
    """Get the frequency progression from a preset, handling different key names."""
    # Try different key names used in the YAML
    for key in ['progression', 'frequency_progression']:
        if key in preset:
            return preset[key]
    return []


def _convert_progression_to_stages(
    progression: List[Dict[str, Any]],
    total_duration_sec: float
) -> List[StageDict]:
    """
    Convert YAML progression (time-based) to generator stages (percentage-based).

    YAML format:
        - time: "03:00"
          beat_hz: 8.0
          state: "alpha"

    Generator format:
        {"name": "stage1", "pct": 12, "freq_start": 10, "freq_end": 8, "transition": "logarithmic"}
    """
    if not progression:
        return []

    stages: List[StageDict] = []

    for i, point in enumerate(progression):
        start_time = _parse_time(point['time'])
        freq_start = point['beat_hz']

        # Determine end time and frequency
        if i + 1 < len(progression):
            end_time = _parse_time(progression[i + 1]['time'])
            freq_end = progression[i + 1]['beat_hz']
        else:
            end_time = total_duration_sec
            freq_end = freq_start  # Hold at final frequency

        # Calculate percentage of total duration
        duration_sec = end_time - start_time
        pct = (duration_sec / total_duration_sec) * 100

        # Skip zero-duration stages
        if pct <= 0:
            continue

        # Determine transition type
        transition = _determine_transition(freq_start, freq_end, point.get('state', ''))

        # Generate stage name
        state = point.get('state', f"stage_{i+1}")
        name = state.replace(' ', '_').lower()

        stage: StageDict = {
            'name': name,
            'pct': round(pct, 1),
            'freq_start': freq_start,
            'freq_end': freq_end,
            'transition': transition,
        }

        # Add modulation for sustained states
        if freq_start == freq_end and duration_sec > 60:
            stage['modulation'] = {
                'range': 0.3 if freq_start > 8 else 0.5,
                'rate': 0.05 if freq_start > 8 else 0.03,
            }

        stages.append(stage)

    return stages


def _determine_transition(freq_start: float, freq_end: float, state: str) -> str:
    """Determine the best transition type based on frequency change."""
    if freq_start == freq_end:
        return 'hold'

    # Gamma bursts are sudden transitions
    if 'gamma' in state.lower() and abs(freq_end - freq_start) > 20:
        return 'linear'  # Sharp transition for gamma

    # Large frequency changes use logarithmic for smoothness
    if abs(freq_end - freq_start) > 3:
        return 'logarithmic'

    return 'linear'


def _extract_gamma_bursts(
    progression: List[Dict[str, Any]],
    overlay: Optional[Dict[str, Any]],
    total_duration_sec: float
) -> List[GammaBurstDict]:
    """
    Extract gamma burst events from progression and overlay.

    Gamma bursts are detected by:
    1. State containing "gamma_burst"
    2. Sudden jumps to 40+ Hz
    3. Overlay with type "gamma_burst"
    """
    gamma_bursts: List[GammaBurstDict] = []

    # Check for gamma bursts in progression
    for i, point in enumerate(progression):
        state = point.get('state', '').lower()
        freq = point['beat_hz']
        time_sec = _parse_time(point['time'])

        # Detect gamma burst by state or frequency
        if 'gamma_burst' in state or (freq >= 40 and i > 0):
            prev_freq = progression[i - 1]['beat_hz'] if i > 0 else freq
            if freq >= 40 and prev_freq < 30:  # Sudden jump to gamma
                # Determine duration (until next point or 3 seconds default)
                if i + 1 < len(progression):
                    next_time = _parse_time(progression[i + 1]['time'])
                    duration = min(next_time - time_sec, 5)  # Cap at 5 seconds
                else:
                    duration = 3

                gamma_bursts.append({
                    'time': int(time_sec),
                    'duration': duration,
                    'frequency': freq,
                })

    # Check overlay for gamma bursts
    if overlay and overlay.get('type') == 'gamma_burst':
        # Parse overlay pattern if available
        pattern = overlay.get('pattern', 'single')
        intensities = overlay.get('intensities', [-12])

        # For multi-surge patterns, distribute across the session
        if pattern == 'three_surges' and len(intensities) >= 3:
            for i, intensity in enumerate(intensities):
                # Distribute surges at 30%, 50%, 70% of duration
                pct = 0.3 + (i * 0.2)
                time_sec = total_duration_sec * pct
                gamma_bursts.append({
                    'time': int(time_sec),
                    'duration': 3,
                    'frequency': 40,
                    'volume_db': intensity,
                })

    return gamma_bursts


def _extract_overlay_config(preset: PresetDict) -> Optional[OverlayDict]:
    """Extract overlay configuration from preset."""
    overlay_config: OverlayDict = {}

    # Check for breathing overlay
    breathing = preset.get('breathing_overlay')
    if breathing and breathing.get('enabled', True):
        overlay_config['breathing_entrainment'] = {
            'enabled': True,
            'frequency_hz': breathing.get('frequency', 0.1),
            'depth_db': breathing.get('depth', 2),
        }

    # Check for heart coherence overlay
    heart = preset.get('heart_coherence_overlay')
    if heart and heart.get('enabled', True):
        overlay_config['heart_coherence'] = {
            'enabled': True,
            'frequency_hz': heart.get('frequency', 0.1),
            'activation_time': heart.get('activation_time'),
        }

    # Check generic overlay
    overlay = preset.get('overlay')
    if overlay:
        overlay_type = overlay.get('type')
        if overlay_type == 'heart_coherence':
            overlay_config['heart_coherence'] = {
                'enabled': True,
                'frequency_hz': overlay.get('frequency', 0.1),
                'activation_time': overlay.get('activation_time'),
            }
        elif overlay_type == 'gamma_burst':
            overlay_config['gamma_burst_overlay'] = {
                'enabled': True,
                'pattern': overlay.get('pattern', 'single'),
                'intensities': overlay.get('intensities', [-12]),
            }
        elif overlay_type == 'breathing':
            overlay_config['breathing_entrainment'] = {
                'enabled': True,
                'frequency_hz': overlay.get('frequency', 0.1),
                'depth_db': overlay.get('depth', 2),
            }

    # Check for harmonic layer (e.g., 528 Hz healing)
    harmonic = preset.get('harmonic_layer')
    if harmonic and harmonic.get('enabled', True):
        overlay_config['harmonic_layer'] = {
            'enabled': True,
            'type': harmonic.get('type', 'healing'),
            'volume_db': harmonic.get('volume', -18),
        }

    return overlay_config if overlay_config else None


# =============================================================================
# PUBLIC API
# =============================================================================

def list_presets() -> List[str]:
    """
    List all available preset names.

    Returns:
        List of preset names (e.g., ['healing_deep', 'healing_gentle', ...])
    """
    data = _load_yaml_data()
    presets = data.get('presets', {})
    return sorted(presets.keys())


def get_preset_info(preset_name: str) -> Optional[Dict[str, Any]]:
    """
    Get metadata about a preset without converting it.

    Returns:
        Dict with name, description, duration, outcome_alignment, etc.
    """
    data = _load_yaml_data()
    presets = data.get('presets', {})

    if preset_name not in presets:
        return None

    preset = presets[preset_name]
    return {
        'name': preset.get('name', preset_name),
        'description': preset.get('description', ''),
        'duration_minutes': preset.get('duration_minutes', 25),
        'outcome_alignment': preset.get('outcome_alignment', []),
        'journey_family': preset.get('journey_family', []),
        'intensity': preset.get('intensity', 'moderate'),
        'category': preset.get('category', 'standard'),
        'caution': preset.get('caution'),
        'carrier_frequency': preset.get('carrier_frequency', preset.get('carrier_hz', 200)),
    }


def load_preset(
    preset_name: str,
    duration_override: Optional[float] = None
) -> Dict[str, Any]:
    """
    Load a preset and convert it to generator format.

    Args:
        preset_name: Name of the preset (e.g., "healing_deep")
        duration_override: Optional duration in seconds to override preset default

    Returns:
        Dict in generator format:
        {
            'description': str,
            'carrier_freq': int,
            'stages': [...],
            'gamma_bursts': [...],
            'overlays': {...},
            'enhancements': {...},
            'metadata': {...}
        }

    Raises:
        ValueError: If preset not found
    """
    data = _load_yaml_data()
    presets = data.get('presets', {})

    if preset_name not in presets:
        available = list(presets.keys())[:10]
        raise ValueError(
            f"Unknown preset: '{preset_name}'. "
            f"Available presets include: {available}... "
            f"(Total: {len(presets)} presets)"
        )

    preset = presets[preset_name]

    # Determine duration
    duration_minutes = preset.get('duration_minutes', 25)
    duration_sec = duration_override if duration_override else duration_minutes * 60

    # Get carrier frequency (handle both key names)
    carrier_freq = preset.get('carrier_frequency', preset.get('carrier_hz', 200))

    # Get and convert progression
    progression = _get_progression(preset)
    stages = _convert_progression_to_stages(progression, duration_sec)

    # Extract gamma bursts
    overlay = preset.get('overlay')
    gamma_bursts = _extract_gamma_bursts(progression, overlay, duration_sec)

    # Extract overlay configuration
    overlays = _extract_overlay_config(preset)

    # Build enhancements from preset
    enhancements: Dict[str, Any] = {}

    # Secondary layer (spatial depth)
    secondary = preset.get('secondary_layer')
    if secondary and secondary.get('enabled', True):
        enhancements['dual_layer'] = {
            'enabled': True,
            'sublayer_freq': secondary.get('offset_hz', 0.5),
            'sublayer_level_db': -6,
        }

    # Transition style affects modulation
    transition_style = preset.get('transition_style', 'smooth')
    if transition_style == 'very_smooth':
        enhancements['smooth_transitions'] = True

    result = {
        'description': preset.get('description', preset.get('name', preset_name)),
        'carrier_freq': carrier_freq,
        'stages': stages,
        'metadata': {
            'preset_name': preset_name,
            'original_duration_minutes': duration_minutes,
            'actual_duration_seconds': duration_sec,
            'outcome_alignment': preset.get('outcome_alignment', []),
            'intensity': preset.get('intensity', 'moderate'),
            'category': preset.get('category', 'standard'),
            'fade_in': preset.get('fade_in_seconds', 30),
            'fade_out': preset.get('fade_out_seconds', 45),
        }
    }

    if gamma_bursts:
        result['gamma_bursts'] = gamma_bursts

    if overlays:
        result['overlays'] = overlays

    if enhancements:
        result['enhancements'] = enhancements

    return result


def get_presets_by_outcome(outcome: str) -> List[str]:
    """
    Get preset names that align with a specific outcome.

    Checks both:
    1. Individual preset's outcome_alignment field
    2. selection_guide.by_outcome mapping

    Args:
        outcome: Outcome category (e.g., "healing", "transformation", "kundalini")

    Returns:
        List of preset names
    """
    data = _load_yaml_data()
    presets = data.get('presets', {})
    outcome_lower = outcome.lower()

    matching = set()

    # Method 1: Check selection_guide.by_outcome for curated lists
    selection_guide = data.get('selection_guide', {})
    by_outcome = selection_guide.get('by_outcome', {})
    if outcome_lower in by_outcome:
        for preset_name in by_outcome[outcome_lower]:
            if preset_name in presets:
                matching.add(preset_name)

    # Method 2: Check individual preset's outcome_alignment
    for name, preset in presets.items():
        outcomes = preset.get('outcome_alignment', [])
        if outcome_lower in [o.lower() for o in outcomes]:
            matching.add(name)

    return sorted(matching)


def get_presets_by_intensity(intensity: str) -> List[str]:
    """
    Get preset names matching an intensity level.

    Args:
        intensity: One of "gentle", "moderate", "intense", "extreme"

    Returns:
        List of preset names
    """
    data = _load_yaml_data()
    presets = data.get('presets', {})

    matching = []
    for name, preset in presets.items():
        preset_intensity = preset.get('intensity', 'moderate').lower()
        if preset_intensity == intensity.lower():
            matching.append(name)

    return sorted(matching)


def get_presets_by_duration(
    min_minutes: int = 0,
    max_minutes: int = 999
) -> List[str]:
    """
    Get preset names within a duration range.

    Args:
        min_minutes: Minimum duration in minutes
        max_minutes: Maximum duration in minutes

    Returns:
        List of preset names
    """
    data = _load_yaml_data()
    presets = data.get('presets', {})

    matching = []
    for name, preset in presets.items():
        duration = preset.get('duration_minutes', 25)
        if min_minutes <= duration <= max_minutes:
            matching.append(name)

    return sorted(matching)


def get_selection_guide() -> Dict[str, Any]:
    """
    Get the selection guide from the presets file.

    Returns the by_outcome, by_duration, and by_intensity mappings.
    """
    data = _load_yaml_data()
    return data.get('selection_guide', {})


def get_journey_families() -> Dict[str, Any]:
    """
    Get the journey families (multi-session series).

    Returns dict of family_name -> {name, presets, suggested_order, etc.}
    """
    data = _load_yaml_data()
    return data.get('journey_families', {})


def get_brainwave_reference() -> Dict[str, Any]:
    """
    Get the brainwave reference information.

    Returns dict of brainwave_type -> {range, typical, state, uses, etc.}
    """
    data = _load_yaml_data()
    return data.get('brainwave_reference', {})


# =============================================================================
# CLI FOR TESTING
# =============================================================================

def _cli():
    """Simple CLI for testing the loader."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Binaural Preset Loader')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # list command
    list_parser = subparsers.add_parser('list', help='List all presets')
    list_parser.add_argument('--outcome', help='Filter by outcome')
    list_parser.add_argument('--intensity', help='Filter by intensity')

    # info command
    info_parser = subparsers.add_parser('info', help='Get preset info')
    info_parser.add_argument('preset', help='Preset name')

    # load command
    load_parser = subparsers.add_parser('load', help='Load and convert preset')
    load_parser.add_argument('preset', help='Preset name')
    load_parser.add_argument('--duration', type=float, help='Duration override (seconds)')
    load_parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if args.command == 'list':
        if args.outcome:
            presets = get_presets_by_outcome(args.outcome)
            print(f"Presets for outcome '{args.outcome}':")
        elif args.intensity:
            presets = get_presets_by_intensity(args.intensity)
            print(f"Presets with intensity '{args.intensity}':")
        else:
            presets = list_presets()
            print(f"All presets ({len(presets)}):")

        for name in presets:
            info = get_preset_info(name)
            if info:
                print(f"  - {name}: {info['description'][:60]}...")
            else:
                print(f"  - {name}")

    elif args.command == 'info':
        info = get_preset_info(args.preset)
        if info:
            print(f"Preset: {args.preset}")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print(f"Preset not found: {args.preset}")

    elif args.command == 'load':
        try:
            result = load_preset(args.preset, args.duration)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Loaded preset: {args.preset}")
                print(f"  Carrier: {result['carrier_freq']} Hz")
                print(f"  Stages: {len(result['stages'])}")
                for stage in result['stages']:
                    print(f"    - {stage['name']}: {stage['pct']:.1f}% "
                          f"({stage['freq_start']}→{stage['freq_end']} Hz)")
                if result.get('gamma_bursts'):
                    print(f"  Gamma bursts: {len(result['gamma_bursts'])}")
                if result.get('overlays'):
                    print(f"  Overlays: {list(result['overlays'].keys())}")
        except ValueError as e:
            print(f"Error: {e}")

    else:
        parser.print_help()


if __name__ == '__main__':
    _cli()
