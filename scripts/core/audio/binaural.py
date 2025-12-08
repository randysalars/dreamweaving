#!/usr/bin/env python3
"""
Binaural Beats Generator - Enhanced Version

Universal module for generating binaural beats audio with support for:
- Frequency transitions between sections
- Gamma bursts for peak insight moments
- ADSR envelopes for smooth audio
- Dynamic carrier frequency modulation (NEW)
- Harmonic stacking for richer carrier sound (NEW)
- Micro-modulation for organic feel (NEW)
- Slow spatial panning to prevent ear fatigue (NEW)

Binaural beats work by playing slightly different frequencies in each ear,
causing the brain to perceive a "beat" at the frequency difference.
For example: 200 Hz in left ear + 210 Hz in right ear = 10 Hz binaural beat.

Enhanced Features (2025-12):
- Carrier frequency can now follow emotional arc (e.g., 432→360→320→400 Hz)
- Harmonic stacking adds 2nd, 3rd harmonics + sub-harmonic + air shimmer
- Micro-modulation prevents static carrier fatigue
- Slow stereo panning creates subtle movement
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, TypedDict

import numpy as np
from numpy.typing import NDArray
from scipy.io import wavfile


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

class HarmonicConfig(TypedDict, total=False):
    """Configuration for harmonic stacking."""
    enabled: bool
    fundamental: float      # 1.0 amplitude (always present)
    second_harmonic: float  # 2x frequency, default 0.3
    third_harmonic: float   # 3x frequency, default 0.15
    sub_harmonic: float     # 0.5x frequency, default 0.2
    air_shimmer: float      # 8x frequency, default 0.05
    per_sample_tracking: bool  # Phase 6: True for accurate tracking during transitions


class MicroModConfig(TypedDict, total=False):
    """Configuration for micro-modulation."""
    enabled: bool
    pitch_drift_cents: float     # Default ±20 cents
    pitch_drift_rate_hz: float   # Default 0.02 Hz (50 sec cycle)
    amplitude_mod_hz: float      # Default 0.08 Hz
    amplitude_mod_depth: float   # Default 0.1 (±10%)


class SpatialConfig(TypedDict, total=False):
    """Configuration for spatial panning."""
    enabled: bool
    sweep_rate_hz: float  # Default 0.02 Hz (50 sec cycle)
    depth: float          # Default 0.15 (15% stereo movement)


class SectionDict(TypedDict, total=False):
    """Type definition for a binaural section."""
    start: int
    end: int
    freq_start: float
    freq_end: float
    beat_hz: float
    offset_hz: float
    transition: str
    # NEW: Dynamic carrier modulation
    carrier_start: float
    carrier_end: float


class GammaBurstDict(TypedDict, total=False):
    """Type definition for a gamma burst.

    Supports three positioning methods:
    - time: Exact timestamp in seconds (original method)
    - position_pct: Percentage through session (0-100)
    - marker: Script marker name to sync with (e.g., "INSIGHT_MOMENT")

    Only one positioning method should be used. Priority: time > position_pct > marker
    """
    time: int                    # Exact timestamp in seconds
    position_pct: float          # Percentage through session (0-100)
    marker: str                  # Script marker name (requires marker_timestamps)
    duration: float              # Burst duration in seconds (required)
    frequency: float             # Gamma frequency in Hz (required, typically 40)


# Type alias for stereo audio array
StereoAudio = NDArray[np.float32]


# =============================================================================
# VALIDATION CONSTANTS (Research-based optimal ranges)
# =============================================================================

# Carrier frequency: 200-500 Hz optimal for FFR perception (PMC research)
CARRIER_FREQ_MIN = 50.0    # Absolute minimum (sub-optimal)
CARRIER_FREQ_MAX = 500.0   # Maximum for clear perception
CARRIER_FREQ_OPTIMAL_MIN = 200.0  # Optimal range start
CARRIER_FREQ_OPTIMAL_MAX = 500.0  # Optimal range end

# Beat frequency: Maps to brainwave bands
BEAT_FREQ_MIN = 0.5   # Delta floor
BEAT_FREQ_MAX = 100.0  # Absolute maximum (gamma+ range)
BEAT_FREQ_THERAPEUTIC_MAX = 40.0  # Standard brainwave bands (delta-gamma)

# Brainwave band definitions (Hz)
BRAINWAVE_BANDS = {
    'delta': (0.5, 4.0),    # Deep sleep, unconscious
    'theta': (4.0, 8.0),    # Meditation, creativity, trance
    'alpha': (8.0, 13.0),   # Relaxed awareness, calm focus
    'beta': (13.0, 30.0),   # Active thinking, focus
    'gamma': (30.0, 100.0), # Higher cognition, insight binding
}

# Minimum exposure for entrainment effects (meta-analytic research)
MIN_ENTRAINMENT_DURATION_SEC = 900  # 15 minutes


class BreathSyncConfig(TypedDict, total=False):
    """Configuration for breath-synchronized amplitude modulation.

    Research shows breathing at 5-6 breaths/min (0.08-0.1 Hz) enhances
    parasympathetic activation and deepens relaxation response.
    """
    enabled: bool
    breath_rate_hz: float      # Default 0.1 Hz (6 breaths/min)
    inhale_boost_db: float     # Volume increase on inhale phase (default +1 dB)
    exhale_drop_db: float      # Volume decrease on exhale phase (default -1 dB)


DEFAULT_BREATH_SYNC: BreathSyncConfig = {
    'enabled': False,  # Off by default, opt-in feature
    'breath_rate_hz': 0.1,      # 6 breaths per minute
    'inhale_boost_db': 1.0,     # Subtle +1 dB on inhale
    'exhale_drop_db': -1.0,     # Subtle -1 dB on exhale
}


# =============================================================================
# DEFAULT ENHANCEMENT CONFIGURATIONS
# =============================================================================

DEFAULT_HARMONICS: HarmonicConfig = {
    'enabled': True,
    'fundamental': 1.0,
    'second_harmonic': 0.3,
    'third_harmonic': 0.15,
    'sub_harmonic': 0.2,
    'air_shimmer': 0.05,
    'per_sample_tracking': False,  # Phase 6: Enable for accurate frequency tracking
}

DEFAULT_MICRO_MOD: MicroModConfig = {
    'enabled': True,
    'pitch_drift_cents': 20,
    'pitch_drift_rate_hz': 0.02,
    'amplitude_mod_hz': 0.08,
    'amplitude_mod_depth': 0.1,
}

DEFAULT_SPATIAL: SpatialConfig = {
    'enabled': True,
    'sweep_rate_hz': 0.02,
    'depth': 0.15,
}


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def _get_brainwave_band(freq_hz: float) -> str:
    """Get the brainwave band name for a given frequency."""
    for band_name, (low, high) in BRAINWAVE_BANDS.items():
        if low <= freq_hz < high:
            return band_name
    if freq_hz >= 100:
        return "high_gamma"
    return "unknown"


def _validate_carrier_freq(carrier_freq: float) -> List[str]:
    """Validate carrier frequency against optimal ranges."""
    if carrier_freq < CARRIER_FREQ_MIN:
        return [f"⚠️  Carrier {carrier_freq} Hz below minimum ({CARRIER_FREQ_MIN} Hz)."]
    if carrier_freq < CARRIER_FREQ_OPTIMAL_MIN:
        return [f"⚠️  Carrier {carrier_freq} Hz below optimal (200-500 Hz). Consider 200+ Hz."]
    if carrier_freq > CARRIER_FREQ_MAX:
        return [f"⚠️  Carrier {carrier_freq} Hz exceeds max ({CARRIER_FREQ_MAX} Hz)."]
    return []


def _validate_beat_freq(freq: float, section_idx: int, label: str) -> List[str]:
    """Validate a single beat frequency value."""
    if freq < BEAT_FREQ_MIN:
        return [f"⚠️  Section {section_idx} beat ({label}) {freq} Hz below min ({BEAT_FREQ_MIN} Hz)."]
    if freq > BEAT_FREQ_THERAPEUTIC_MAX:
        band = _get_brainwave_band(freq)
        return [f"⚠️  Section {section_idx} beat ({label}) {freq} Hz ({band}) above 40 Hz therapeutic range."]
    return []


def _validate_section(section: SectionDict, idx: int) -> List[str]:
    """Validate a single section's parameters."""
    warnings: List[str] = []
    freq_start = section.get('freq_start', section.get('beat_hz', 10))
    freq_end = section.get('freq_end', freq_start)

    warnings.extend(_validate_beat_freq(freq_start, idx + 1, 'start'))
    warnings.extend(_validate_beat_freq(freq_end, idx + 1, 'end'))

    # Validate section carrier frequencies if specified
    for key in ['carrier_start', 'carrier_end']:
        carrier = section.get(key)
        if carrier is not None and (carrier < CARRIER_FREQ_MIN or carrier > CARRIER_FREQ_MAX):
            warnings.append(f"⚠️  Section {idx+1} {key} {carrier} Hz outside range ({CARRIER_FREQ_MIN}-{CARRIER_FREQ_MAX}).")

    return warnings


def _validate_gamma_burst(burst: GammaBurstDict, idx: int, duration_sec: float) -> List[str]:
    """Validate a single gamma burst."""
    warnings: List[str] = []
    if burst['time'] < 0 or burst['time'] > duration_sec:
        warnings.append(f"⚠️  Gamma burst {idx+1} at {burst['time']}s outside duration (0-{duration_sec}s).")
    if burst['frequency'] < 30 or burst['frequency'] > 50:
        warnings.append(f"⚠️  Gamma burst {idx+1} freq {burst['frequency']} Hz outside gamma range (30-50 Hz).")
    return warnings


def _validate_parameters(
    carrier_freq: float,
    sections: List[SectionDict],
    duration_sec: float,
    gamma_bursts: Optional[List[GammaBurstDict]] = None,
) -> List[str]:
    """
    Validate binaural generation parameters against research-based optimal ranges.

    Returns a list of warning messages (empty list if all parameters are optimal).
    """
    warnings: List[str] = []

    warnings.extend(_validate_carrier_freq(carrier_freq))

    if duration_sec < MIN_ENTRAINMENT_DURATION_SEC:
        warnings.append(f"⚠️  Duration {duration_sec/60:.1f} min below {MIN_ENTRAINMENT_DURATION_SEC/60:.0f} min minimum.")

    for i, section in enumerate(sections):
        warnings.extend(_validate_section(section, i))

    if gamma_bursts:
        for i, burst in enumerate(gamma_bursts):
            warnings.extend(_validate_gamma_burst(burst, i, duration_sec))

    return warnings


def validate_and_log(
    carrier_freq: float,
    sections: List[SectionDict],
    duration_sec: float,
    gamma_bursts: Optional[List[GammaBurstDict]] = None,
) -> bool:
    """
    Validate parameters and print any warnings.

    Returns True if all parameters are optimal, False if there are warnings.
    """
    warnings = _validate_parameters(carrier_freq, sections, duration_sec, gamma_bursts)
    if warnings:
        print("\n" + "=" * 60)
        print("BINAURAL PARAMETER VALIDATION WARNINGS")
        print("=" * 60)
        for warning in warnings:
            print(warning)
        print("=" * 60 + "\n")
        return False
    return True


def _build_enhancement_list(
    harm_cfg: Dict, mod_cfg: Dict, spatial_cfg: Dict, breath_cfg: Dict
) -> List[str]:
    """Build list of enabled enhancement names for logging."""
    enhancements = []
    if harm_cfg.get('enabled', True):
        enhancements.append("harmonics")
    if mod_cfg.get('enabled', True):
        enhancements.append("micro-mod")
    if spatial_cfg.get('enabled', True):
        enhancements.append("spatial")
    if breath_cfg.get('enabled', False):
        enhancements.append("breath-sync")
    return enhancements


def _resolve_burst_from_pct(
    burst_idx: int, pct: float, duration_sec: float
) -> int:
    """Resolve position_pct to timestamp."""
    if not 0 <= pct <= 100:
        print(f"  ⚠️ Gamma burst {burst_idx}: position_pct {pct} out of range, clamping")
        pct = max(0, min(100, pct))
    resolved_time = int((pct / 100.0) * duration_sec)
    print(f"  ℹ️ Gamma burst {burst_idx}: position_pct {pct}% → {resolved_time}s")
    return resolved_time


def _resolve_burst_from_marker(
    burst_idx: int, marker_name: str, marker_timestamps: Optional[Dict[str, float]]
) -> Optional[int]:
    """Resolve marker to timestamp. Returns None if marker not found."""
    if marker_timestamps and marker_name in marker_timestamps:
        resolved_time = int(marker_timestamps[marker_name])
        print(f"  ℹ️ Gamma burst {burst_idx}: marker '{marker_name}' → {resolved_time}s")
        return resolved_time
    print(f"  ⚠️ Gamma burst {burst_idx}: marker '{marker_name}' not found, skipping")
    return None


def _resolve_single_gamma_burst(
    burst: GammaBurstDict,
    burst_idx: int,
    duration_sec: float,
    marker_timestamps: Optional[Dict[str, float]],
) -> Optional[GammaBurstDict]:
    """Resolve a single gamma burst to have a 'time' field."""
    resolved_burst: GammaBurstDict = {
        'duration': burst.get('duration', 3.0),
        'frequency': burst.get('frequency', 40.0),
    }

    # Priority 1: Use explicit time if provided
    if 'time' in burst and burst['time'] is not None:
        resolved_burst['time'] = burst['time']
        return resolved_burst

    # Priority 2: Resolve position_pct to time
    if 'position_pct' in burst and burst['position_pct'] is not None:
        resolved_burst['time'] = _resolve_burst_from_pct(
            burst_idx, burst['position_pct'], duration_sec
        )
        return resolved_burst

    # Priority 3: Resolve marker to time
    if 'marker' in burst and burst['marker'] is not None:
        resolved_time = _resolve_burst_from_marker(
            burst_idx, burst['marker'], marker_timestamps
        )
        if resolved_time is not None:
            resolved_burst['time'] = resolved_time
            return resolved_burst
        return None

    print(f"  ⚠️ Gamma burst {burst_idx}: no positioning method specified, skipping")
    return None


def _resolve_gamma_burst_times(
    gamma_bursts: Optional[List[GammaBurstDict]],
    duration_sec: float,
    marker_timestamps: Optional[Dict[str, float]] = None,
) -> Optional[List[GammaBurstDict]]:
    """
    Resolve gamma burst positioning to actual timestamps.

    Gamma bursts can be positioned using three methods:
    - time: Exact timestamp in seconds (used directly)
    - position_pct: Percentage through session (0-100), resolved to timestamp
    - marker: Script marker name, resolved via marker_timestamps dict

    Priority: time > position_pct > marker

    Args:
        gamma_bursts: List of gamma burst definitions
        duration_sec: Total session duration in seconds
        marker_timestamps: Optional dict mapping marker names to timestamps
            e.g., {"INSIGHT_MOMENT": 450.0, "TRANSFORMATION_PEAK": 720.0}

    Returns:
        List of gamma bursts with all positions resolved to 'time' field,
        or None if input was None
    """
    if not gamma_bursts:
        return None

    resolved: List[GammaBurstDict] = []
    for i, burst in enumerate(gamma_bursts):
        resolved_burst = _resolve_single_gamma_burst(
            burst, i, duration_sec, marker_timestamps
        )
        if resolved_burst is not None:
            resolved.append(resolved_burst)

    return resolved if resolved else None


def _apply_breath_sync(
    audio: StereoAudio,
    duration_sec: float,
    breath_rate_hz: float = 0.1,
    inhale_boost_db: float = 1.0,
    exhale_drop_db: float = -1.0,
) -> StereoAudio:
    """
    Apply breath-synchronized amplitude modulation.

    Creates a gentle amplitude wave that rises during "inhale" phase
    and falls during "exhale" phase, synchronized to relaxed breathing
    rate (default 6 breaths/min = 0.1 Hz).

    Research shows breathing at 5-6 breaths/min enhances parasympathetic
    activation and deepens the relaxation response.

    Args:
        audio: Input stereo array (samples, 2)
        duration_sec: Total duration in seconds
        breath_rate_hz: Breathing rate (default 0.1 Hz = 6 breaths/min)
        inhale_boost_db: Volume boost during inhale peak (default +1 dB)
        exhale_drop_db: Volume drop during exhale trough (default -1 dB)

    Returns:
        Audio with breath-synchronized modulation applied
    """
    samples = len(audio)
    t = np.linspace(0, duration_sec, samples, dtype=np.float32)

    # Generate breath wave: 0 to 1 range (sine oscillation)
    # Phase offset so we start at neutral (midpoint of breath cycle)
    breath_wave = 0.5 * (1 + np.sin(2 * np.pi * breath_rate_hz * t - np.pi / 2))

    # Convert dB changes to linear multipliers
    # At breath_wave=1 (inhale peak): apply inhale_boost_db
    # At breath_wave=0 (exhale trough): apply exhale_drop_db
    inhale_linear = 10 ** (inhale_boost_db / 20)
    exhale_linear = 10 ** (exhale_drop_db / 20)

    # Interpolate between exhale and inhale levels based on breath wave
    gain = exhale_linear + (inhale_linear - exhale_linear) * breath_wave

    # Apply to both channels
    output = audio.copy()
    output[:, 0] *= gain
    output[:, 1] *= gain

    return output


def generate(
    sections: List[SectionDict],
    duration_sec: float,
    sample_rate: int = 48000,
    carrier_freq: float = 200,
    amplitude: float = 0.25,
    fade_in_sec: float = 5.0,
    fade_out_sec: float = 8.0,
    gamma_bursts: Optional[List[GammaBurstDict]] = None,
    marker_timestamps: Optional[Dict[str, float]] = None,
    # Enhancement configurations
    harmonics: Optional[HarmonicConfig] = None,
    micro_mod: Optional[MicroModConfig] = None,
    spatial: Optional[SpatialConfig] = None,
    breath_sync: Optional[BreathSyncConfig] = None,
) -> StereoAudio:
    """
    Generate binaural beats audio with optional psychoacoustic enhancements.

    Creates a stereo audio track with binaural beats based on the provided
    section definitions. Each section can have its own frequency and
    transition type. Enhanced version supports harmonic stacking, micro-modulation,
    spatial panning, and breath-synchronized modulation.

    Args:
        sections: List of section definitions with timing and frequency info.
            Each section should have:
            - start: Start time in seconds
            - end: End time in seconds
            - freq_start or beat_hz: Starting beat frequency in Hz
            - freq_end: Ending beat frequency (for transitions)
            - transition: 'linear', 'logarithmic', or 'hold'
            - carrier_start: Starting carrier freq for this section
            - carrier_end: Ending carrier freq for this section
        duration_sec: Total duration in seconds
        sample_rate: Sample rate in Hz (default: 48000)
        carrier_freq: Base carrier frequency in Hz (default: 200)
            Used when sections don't specify carrier_start/carrier_end
        amplitude: Output amplitude 0.0-1.0 (default: 0.25)
        fade_in_sec: Fade in duration in seconds (default: 5.0)
        fade_out_sec: Fade out duration in seconds (default: 8.0)
        gamma_bursts: Optional list of gamma burst events for peak moments.
            Supports three positioning methods:
            - time: Exact timestamp in seconds
            - position_pct: Percentage through session (0-100)
            - marker: Script marker name (requires marker_timestamps)
        marker_timestamps: Optional dict mapping marker names to timestamps
            e.g., {"INSIGHT_MOMENT": 450.0, "TRANSFORMATION_PEAK": 720.0}
            Required when using marker-based gamma burst positioning.
        harmonics: Harmonic stacking config (pass None to use defaults,
            {'enabled': False} to disable)
        micro_mod: Micro-modulation config (pass None to use defaults,
            {'enabled': False} to disable)
        spatial: Spatial panning config (pass None to use defaults,
            {'enabled': False} to disable)
        breath_sync: Breath-synchronized modulation config for parasympathetic
            activation. Disabled by default; pass {'enabled': True} to activate.

    Returns:
        Stereo audio as numpy array with shape (samples, 2)

    Example:
        >>> sections = [
        ...     {'start': 0, 'end': 60, 'freq_start': 10, 'freq_end': 10,
        ...      'carrier_start': 432, 'carrier_end': 400},
        ...     {'start': 60, 'end': 120, 'freq_start': 10, 'freq_end': 6,
        ...      'carrier_start': 400, 'carrier_end': 360}
        ... ]
        >>> audio = generate(sections, duration_sec=120, breath_sync={'enabled': True})
    """
    # Validate parameters and log any warnings
    validate_and_log(carrier_freq, sections, duration_sec, gamma_bursts)

    # Resolve gamma burst positioning (position_pct, marker → time)
    resolved_gamma_bursts = _resolve_gamma_burst_times(
        gamma_bursts, duration_sec, marker_timestamps
    )

    # Merge enhancement configs with defaults
    harm_cfg = {**DEFAULT_HARMONICS, **(harmonics or {})}
    mod_cfg = {**DEFAULT_MICRO_MOD, **(micro_mod or {})}
    spatial_cfg = {**DEFAULT_SPATIAL, **(spatial or {})}
    breath_cfg = {**DEFAULT_BREATH_SYNC, **(breath_sync or {})}

    # Print generation info
    enhancements = _build_enhancement_list(harm_cfg, mod_cfg, spatial_cfg, breath_cfg)
    enhance_str = f" [{', '.join(enhancements)}]" if enhancements else ""
    print(f"Generating binaural beats: {duration_sec/60:.1f} min, carrier={carrier_freq}Hz{enhance_str}")

    # Initialize empty track
    total_samples = int(sample_rate * duration_sec)
    full_track: StereoAudio = np.zeros((total_samples, 2), dtype=np.float32)

    current_sample = 0

    # Process each section
    for idx, section in enumerate(sections):
        start = section['start']
        end = section['end']
        duration = end - start
        freq_start = section.get('freq_start', section.get('beat_hz', 10))
        freq_end = section.get('freq_end', freq_start)
        transition = section.get('transition', 'linear')

        # NEW: Dynamic carrier modulation - use section-specific carrier if provided
        section_carrier_start = section.get('carrier_start', carrier_freq)
        section_carrier_end = section.get('carrier_end', section_carrier_start)

        carrier_info = ""
        if section_carrier_start != section_carrier_end:
            carrier_info = f", carrier {section_carrier_start}→{section_carrier_end}Hz"
        elif section_carrier_start != carrier_freq:
            carrier_info = f", carrier {section_carrier_start}Hz"

        print(f"  Section {idx+1}/{len(sections)}: {start}s-{end}s, {freq_start}Hz→{freq_end}Hz ({transition}){carrier_info}")

        # Check for gamma burst in this section (use resolved bursts)
        gamma_in_section = _find_gamma_in_section(resolved_gamma_bursts, start, end)

        if gamma_in_section:
            # Process section with gamma burst
            current_sample = _process_gamma_section(
                full_track, current_sample, section, gamma_in_section,
                section_carrier_start, section_carrier_end, amplitude, sample_rate,
                harm_cfg, mod_cfg
            )
        else:
            # Standard segment with enhancements
            segment = _generate_segment_enhanced(
                duration, freq_start, freq_end,
                section_carrier_start, section_carrier_end,
                amplitude, sample_rate, transition,
                harm_cfg, mod_cfg
            )
            end_sample = current_sample + len(segment)
            full_track[current_sample:end_sample] = segment
            current_sample = end_sample

    # Apply global fade in/out
    full_track = _apply_fades(full_track, fade_in_sec, fade_out_sec, sample_rate)

    # Apply spatial panning if enabled
    if spatial_cfg.get('enabled', True):
        full_track = _apply_spatial_panning(
            full_track, duration_sec,
            spatial_cfg.get('sweep_rate_hz', 0.02),
            spatial_cfg.get('depth', 0.15)
        )

    # Apply breath-synchronized modulation if enabled
    if breath_cfg.get('enabled', False):
        full_track = _apply_breath_sync(
            full_track, duration_sec,
            breath_cfg.get('breath_rate_hz', 0.1),
            breath_cfg.get('inhale_boost_db', 1.0),
            breath_cfg.get('exhale_drop_db', -1.0)
        )

    print(f"✓ Binaural beats generated: {len(full_track)/sample_rate/60:.1f} min")

    return full_track


def _apply_fades(
    audio: StereoAudio,
    fade_in_sec: float,
    fade_out_sec: float,
    sample_rate: int
) -> StereoAudio:
    """Apply fade in and fade out to audio."""
    if fade_in_sec > 0:
        fade_in_samples = int(fade_in_sec * sample_rate)
        fade_in_curve = np.linspace(0, 1, fade_in_samples).astype(np.float32)
        audio[:fade_in_samples, 0] *= fade_in_curve
        audio[:fade_in_samples, 1] *= fade_in_curve

    if fade_out_sec > 0:
        fade_out_samples = int(fade_out_sec * sample_rate)
        fade_out_curve = np.linspace(1, 0, fade_out_samples).astype(np.float32)
        audio[-fade_out_samples:, 0] *= fade_out_curve
        audio[-fade_out_samples:, 1] *= fade_out_curve

    return audio


def _find_gamma_in_section(
    gamma_bursts: Optional[List[GammaBurstDict]],
    start: int,
    end: int
) -> Optional[GammaBurstDict]:
    """Find a gamma burst within a section's time range."""
    if not gamma_bursts:
        return None
    for gamma in gamma_bursts:
        if start <= gamma['time'] < end:
            return gamma
    return None


def _process_gamma_section(
    full_track: StereoAudio,
    current_sample: int,
    section: SectionDict,
    gamma: GammaBurstDict,
    carrier_start: float,
    carrier_end: float,
    amplitude: float,
    sample_rate: int,
    harm_cfg: Dict,
    mod_cfg: Dict
) -> int:
    """Process a section that contains a gamma burst."""
    start = section['start']
    end = section['end']
    freq_start = section.get('freq_start', section.get('beat_hz', 10))
    freq_end = section.get('freq_end', freq_start)
    transition = section.get('transition', 'linear')

    gamma_time = gamma['time']
    gamma_duration = gamma['duration']
    gamma_freq = gamma['frequency']

    # Pre-gamma segment
    pre_duration = gamma_time - start
    if pre_duration > 0:
        segment = _generate_segment_enhanced(
            pre_duration, freq_start, freq_end,
            carrier_start, carrier_end,
            amplitude, sample_rate, transition,
            harm_cfg, mod_cfg
        )
        end_sample = current_sample + len(segment)
        full_track[current_sample:end_sample] = segment
        current_sample = end_sample

    # Gamma burst
    print(f"    ⚡ GAMMA BURST at {gamma_time}s: {gamma_freq}Hz for {gamma_duration}s")
    # Use midpoint carrier for gamma burst
    mid_carrier = (carrier_start + carrier_end) / 2
    gamma_segment = _generate_gamma_burst(
        mid_carrier, gamma_freq, gamma_duration,
        amplitude, sample_rate
    )
    end_sample = current_sample + len(gamma_segment)
    full_track[current_sample:end_sample] = gamma_segment
    current_sample = end_sample

    # Post-gamma segment
    post_duration = end - (gamma_time + gamma_duration)
    if post_duration > 0:
        segment = _generate_segment_enhanced(
            post_duration, freq_start, freq_end,
            carrier_start, carrier_end,
            amplitude, sample_rate, transition,
            harm_cfg, mod_cfg
        )
        end_sample = current_sample + len(segment)
        full_track[current_sample:end_sample] = segment
        current_sample = end_sample

    return current_sample


def _apply_spatial_panning(
    audio: StereoAudio,
    duration_sec: float,
    sweep_rate_hz: float = 0.02,
    depth: float = 0.15
) -> StereoAudio:
    """
    Apply slow stereo panning sweep to prevent ear fatigue.

    Args:
        audio: Input stereo array (samples, 2)
        duration_sec: Total duration
        sweep_rate_hz: Panning rate (default 0.02 Hz = 50 second cycle)
        depth: Panning depth (0.0-1.0, where 0.15 = 15% movement)

    Returns:
        Audio with spatial panning applied
    """
    samples = len(audio)
    t = np.linspace(0, duration_sec, samples, dtype=np.float32)

    # Generate panning curve (-1 to 1 range, scaled by depth)
    pan = np.sin(2 * np.pi * sweep_rate_hz * t) * depth

    # Convert pan to L/R gains using constant-power panning
    left_gain = np.sqrt(0.5 * (1 - pan))
    right_gain = np.sqrt(0.5 * (1 + pan))

    output = audio.copy()
    output[:, 0] *= left_gain
    output[:, 1] *= right_gain

    return output


# =============================================================================
# ENHANCED SEGMENT GENERATION (NEW)
# =============================================================================

def _generate_harmonic_carrier(
    freq: float,
    t: np.ndarray,
    harm_cfg: Dict
) -> np.ndarray:
    """
    Generate carrier with harmonic stacking for richer sound.

    Creates a carrier tone with multiple harmonics:
    - Fundamental (1x): Base frequency
    - 2nd harmonic (2x): One octave up
    - 3rd harmonic (3x): Octave + fifth
    - Sub-harmonic (0.5x): One octave down
    - Air shimmer (8x): High frequency sparkle

    Args:
        freq: Fundamental frequency in Hz
        t: Time array
        harm_cfg: Harmonic configuration dict

    Returns:
        Mono carrier signal with harmonics
    """
    # Get harmonic levels from config
    fund_amp = harm_cfg.get('fundamental', 1.0)
    h2_amp = harm_cfg.get('second_harmonic', 0.3)
    h3_amp = harm_cfg.get('third_harmonic', 0.15)
    sub_amp = harm_cfg.get('sub_harmonic', 0.2)
    air_amp = harm_cfg.get('air_shimmer', 0.05)

    # Generate each harmonic
    carrier = (
        fund_amp * np.sin(2 * np.pi * freq * t) +
        h2_amp * np.sin(2 * np.pi * freq * 2 * t) +
        h3_amp * np.sin(2 * np.pi * freq * 3 * t) +
        sub_amp * np.sin(2 * np.pi * freq * 0.5 * t) +
        air_amp * np.sin(2 * np.pi * freq * 8 * t)
    )

    # Normalize to prevent clipping
    total_amp = fund_amp + h2_amp + h3_amp + sub_amp + air_amp
    return carrier / total_amp


def _generate_harmonic_carrier_dynamic(
    freq_array: np.ndarray,
    sample_rate: int,
    harm_cfg: Dict
) -> np.ndarray:
    """
    Generate carrier with harmonic stacking using per-sample frequency tracking.

    This is the Phase 6 enhancement that provides accurate harmonic generation
    during frequency transitions. Each harmonic uses its own phase accumulator
    to track frequency changes sample-by-sample.

    Args:
        freq_array: Per-sample frequency array (shape: samples,)
        sample_rate: Sample rate in Hz
        harm_cfg: Harmonic configuration dict

    Returns:
        Mono carrier signal with per-sample accurate harmonics
    """
    # Get harmonic levels from config
    fund_amp = harm_cfg.get('fundamental', 1.0)
    h2_amp = harm_cfg.get('second_harmonic', 0.3)
    h3_amp = harm_cfg.get('third_harmonic', 0.15)
    sub_amp = harm_cfg.get('sub_harmonic', 0.2)
    air_amp = harm_cfg.get('air_shimmer', 0.05)

    # Per-sample phase increment for each harmonic
    # phase_increment = 2 * pi * freq / sample_rate
    base_increment = 2 * np.pi * freq_array / sample_rate

    # Generate cumulative phase for each harmonic ratio
    # Using cumsum for phase accumulator (maintains phase continuity)
    fund_phase = np.cumsum(base_increment)
    h2_phase = np.cumsum(base_increment * 2)      # 2x frequency
    h3_phase = np.cumsum(base_increment * 3)      # 3x frequency
    sub_phase = np.cumsum(base_increment * 0.5)   # 0.5x frequency
    air_phase = np.cumsum(base_increment * 8)     # 8x frequency

    # Generate each harmonic from accumulated phase
    carrier = (
        fund_amp * np.sin(fund_phase) +
        h2_amp * np.sin(h2_phase) +
        h3_amp * np.sin(h3_phase) +
        sub_amp * np.sin(sub_phase) +
        air_amp * np.sin(air_phase)
    )

    # Normalize to prevent clipping
    total_amp = fund_amp + h2_amp + h3_amp + sub_amp + air_amp
    return (carrier / total_amp).astype(np.float32)


def _apply_micro_modulation(
    carrier: np.ndarray,
    t: np.ndarray,
    mod_cfg: Dict
) -> np.ndarray:
    """
    Apply micro-modulation to prevent listener fatigue.

    Adds subtle organic movement to the carrier:
    - Slow amplitude modulation (±10% at 0.08 Hz)
    - Creates "breathing" feel in the binaural

    Note: Pitch drift is complex to implement without phase vocoder,
    so we focus on amplitude modulation which is perceptually effective.

    Args:
        carrier: Input carrier signal
        t: Time array
        mod_cfg: Micro-modulation configuration

    Returns:
        Modulated carrier signal
    """
    amp_mod_hz = mod_cfg.get('amplitude_mod_hz', 0.08)
    amp_mod_depth = mod_cfg.get('amplitude_mod_depth', 0.1)

    # Amplitude modulation with random phase offset for natural feel
    # Intentionally unseeded - we want variation between L/R channels and segments
    rng = np.random.default_rng()  # noqa: S6709
    phase_offset = rng.uniform(0, 2 * np.pi)
    amp_mod = 1 + amp_mod_depth * np.sin(2 * np.pi * amp_mod_hz * t + phase_offset)

    return carrier * amp_mod


def _generate_segment_enhanced(
    duration: float,
    freq_start: float,
    freq_end: float,
    carrier_start: float,
    carrier_end: float,
    amplitude: float,
    sample_rate: int,
    transition: str,
    harm_cfg: Dict,
    mod_cfg: Dict
) -> StereoAudio:
    """
    Generate a segment with enhanced psychoacoustic features.

    This is the enhanced version of _generate_segment that supports:
    - Dynamic carrier frequency modulation
    - Harmonic stacking for richer sound
    - Micro-modulation for organic feel

    Args:
        duration: Segment duration in seconds
        freq_start: Starting beat frequency in Hz
        freq_end: Ending beat frequency in Hz
        carrier_start: Starting carrier frequency in Hz
        carrier_end: Ending carrier frequency in Hz
        amplitude: Output amplitude (0.0-1.0)
        sample_rate: Sample rate in Hz
        transition: Transition type ('linear', 'logarithmic', or 'hold')
        harm_cfg: Harmonic stacking configuration
        mod_cfg: Micro-modulation configuration

    Returns:
        Stereo audio segment as numpy array
    """
    segment_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, segment_samples, dtype=np.float32)
    progress = np.linspace(0, 1, segment_samples, dtype=np.float32)

    # Interpolate beat frequency
    if transition == 'logarithmic' and freq_start > 0 and freq_end > 0:
        beat_freq = freq_start * ((freq_end / freq_start) ** progress)
    else:  # linear or hold
        beat_freq = freq_start + (freq_end - freq_start) * progress

    # Interpolate carrier frequency (always linear for smoothness)
    carrier_freq = carrier_start + (carrier_end - carrier_start) * progress

    # Calculate left/right frequencies
    left_freq = carrier_freq - (beat_freq / 2)
    right_freq = carrier_freq + (beat_freq / 2)

    # Check if harmonics are enabled
    use_harmonics = harm_cfg.get('enabled', True)
    use_micro_mod = mod_cfg.get('enabled', True)

    if use_harmonics:
        # Generate with harmonic stacking
        use_per_sample = harm_cfg.get('per_sample_tracking', False)

        if use_per_sample:
            # Phase 6: Per-sample frequency tracking for accurate harmonics
            # during large frequency transitions. Uses phase accumulators
            # for each harmonic, trading CPU for accuracy.
            left_tone = _generate_harmonic_carrier_dynamic(left_freq, sample_rate, harm_cfg)
            right_tone = _generate_harmonic_carrier_dynamic(right_freq, sample_rate, harm_cfg)
        else:
            # Original approach: Generate harmonics at average frequencies
            # then apply frequency modulation envelope. Fast but approximate.
            avg_left = (left_freq[0] + left_freq[-1]) / 2
            avg_right = (right_freq[0] + right_freq[-1]) / 2

            left_carrier = _generate_harmonic_carrier(avg_left, t, harm_cfg)
            right_carrier = _generate_harmonic_carrier(avg_right, t, harm_cfg)

            # Apply frequency modulation via phase adjustment
            freq_mod_left = left_freq / avg_left
            freq_mod_right = right_freq / avg_right

            left_tone = left_carrier * freq_mod_left
            right_tone = right_carrier * freq_mod_right

    else:
        # Simple sine wave generation (original behavior)
        # Use phase accumulator for accurate frequency tracking
        left_phase = np.cumsum(2 * np.pi * left_freq / sample_rate)
        right_phase = np.cumsum(2 * np.pi * right_freq / sample_rate)

        left_tone = np.sin(left_phase)
        right_tone = np.sin(right_phase)

    # Apply micro-modulation if enabled
    if use_micro_mod:
        left_tone = _apply_micro_modulation(left_tone, t, mod_cfg)
        right_tone = _apply_micro_modulation(right_tone, t, mod_cfg)

    # Apply amplitude
    left_tone *= amplitude
    right_tone *= amplitude

    # Stack to stereo
    segment: StereoAudio = np.stack([left_tone, right_tone], axis=1).astype(np.float32)

    return segment


def _generate_segment(
    duration: float,
    freq_start: float,
    freq_end: float,
    carrier_freq: float,
    amplitude: float,
    sample_rate: int,
    transition: str = 'linear'
) -> StereoAudio:
    """
    Generate a single segment with frequency progression.

    Args:
        duration: Segment duration in seconds
        freq_start: Starting beat frequency in Hz
        freq_end: Ending beat frequency in Hz
        carrier_freq: Carrier frequency in Hz
        amplitude: Output amplitude (0.0-1.0)
        sample_rate: Sample rate in Hz
        transition: Transition type ('linear', 'logarithmic', or 'hold')

    Returns:
        Stereo audio segment as numpy array
    """
    segment_samples = int(sample_rate * duration)
    segment: StereoAudio = np.zeros((segment_samples, 2), dtype=np.float32)

    for i in range(segment_samples):
        t = i / sample_rate
        progress = i / segment_samples

        # Interpolate beat frequency
        if transition == 'logarithmic' and freq_start > 0 and freq_end > 0:
            beat_freq = freq_start * ((freq_end / freq_start) ** progress)
        else:  # linear or hold
            beat_freq = freq_start + (freq_end - freq_start) * progress

        # Calculate left/right frequencies
        left_freq = carrier_freq - (beat_freq / 2)
        right_freq = carrier_freq + (beat_freq / 2)

        # Generate tones
        segment[i, 0] = np.sin(2 * np.pi * left_freq * t) * amplitude
        segment[i, 1] = np.sin(2 * np.pi * right_freq * t) * amplitude

    return segment


def _generate_gamma_burst(
    carrier_freq: float,
    gamma_freq: float,
    duration: float,
    amplitude: float,
    sample_rate: int
) -> StereoAudio:
    """
    Generate intense gamma burst with quick envelope.

    Gamma bursts are used for peak insight moments, typically at 40 Hz.
    The envelope provides a quick fade in and longer fade out for
    smooth integration with surrounding audio.

    Args:
        carrier_freq: Carrier frequency in Hz
        gamma_freq: Gamma beat frequency in Hz (typically 40)
        duration: Burst duration in seconds
        amplitude: Base amplitude (0.0-1.0)
        sample_rate: Sample rate in Hz

    Returns:
        Stereo audio segment as numpy array
    """
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, endpoint=False)

    # Calculate frequencies
    left_freq = carrier_freq - (gamma_freq / 2)
    right_freq = carrier_freq + (gamma_freq / 2)

    # Generate tones
    left_tone = np.sin(2 * np.pi * left_freq * t)
    right_tone = np.sin(2 * np.pi * right_freq * t)

    # Envelope: quick fade in, sustain, quick fade out
    fade_in_samples = int(0.2 * sample_rate)
    fade_out_samples = int(0.5 * sample_rate)

    envelope = np.ones(len(t))
    envelope[:fade_in_samples] = np.linspace(0, 1, fade_in_samples)
    envelope[-fade_out_samples:] = np.linspace(1, 0, fade_out_samples)

    # Apply envelope with slight boost for impact
    left_tone = left_tone * envelope * amplitude * 1.2
    right_tone = right_tone * envelope * amplitude * 1.2

    stereo: StereoAudio = np.stack([left_tone, right_tone], axis=1).astype(np.float32)
    return stereo


def save_stem(
    audio: StereoAudio,
    path: Union[str, Path],
    sample_rate: int = 48000
) -> None:
    """
    Save binaural audio as WAV file.

    Args:
        audio: Stereo audio array (float32, shape (samples, 2))
        path: Output file path
        sample_rate: Sample rate in Hz

    Raises:
        OSError: If the file cannot be written
    """
    path = Path(path)

    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to 16-bit PCM
    audio_int = (audio * 32767).astype(np.int16)

    # Save
    wavfile.write(str(path), sample_rate, audio_int)

    file_size = path.stat().st_size / (1024 * 1024)
    print(f"✓ Saved binaural stem: {path} ({file_size:.1f} MB)")


def _build_sections_from_manifest(
    binaural_config: Dict[str, Any]
) -> List[SectionDict]:
    """Build section list from manifest binaural config."""
    sections: List[SectionDict] = []
    carrier_progression = binaural_config.get('carrier_progression', [])
    base_hz = binaural_config.get('base_hz', 200)

    for section in binaural_config.get('sections', []):
        section_dict: SectionDict = {
            'start': section['start'],
            'end': section['end'],
            'freq_start': section.get('offset_hz', section.get('beat_hz', 10)),
            'freq_end': section.get('offset_hz', section.get('beat_hz', 10)),
            'transition': section.get('transition', 'linear')
        }

        # Apply carrier modulation if defined
        _apply_carrier_progression(section_dict, carrier_progression, base_hz)
        sections.append(section_dict)

    return sections


def _apply_carrier_progression(
    section_dict: SectionDict,
    carrier_progression: List[Dict],
    base_hz: float
) -> None:
    """Apply carrier progression to a section dict (mutates in place)."""
    for cp in carrier_progression:
        cp_time = cp.get('timestamp', 0)
        if section_dict['start'] <= cp_time < section_dict['end']:
            section_dict['carrier_start'] = cp.get('carrier_hz', base_hz)
            # Find next carrier point for end value
            next_cp = next(
                (c for c in carrier_progression if c.get('timestamp', 0) > cp_time),
                None
            )
            if next_cp:
                section_dict['carrier_end'] = next_cp.get('carrier_hz', section_dict['carrier_start'])
            break


def _extract_gamma_bursts(manifest: Dict[str, Any]) -> List[GammaBurstDict]:
    """Extract gamma burst events from manifest fx_timeline."""
    gamma_bursts: List[GammaBurstDict] = []
    for fx in manifest.get('fx_timeline', []):
        if fx.get('type') == 'gamma_flash':
            gamma_bursts.append({
                'time': fx['time'],
                'duration': fx.get('duration_s', 3.0),
                'frequency': fx.get('freq_hz', 40)
            })
    return gamma_bursts


def _get_enhancement_config(
    binaural_config: Dict[str, Any],
    override: Optional[Dict],
    key: str
) -> Optional[Dict]:
    """Get enhancement config from override or manifest."""
    if override is not None:
        return override
    manifest_config = binaural_config.get(key, {})
    return manifest_config if manifest_config else None


def generate_from_manifest(
    manifest: Dict[str, Any],
    session_dir: Union[str, Path],
    harmonics: Optional[HarmonicConfig] = None,
    micro_mod: Optional[MicroModConfig] = None,
    spatial: Optional[SpatialConfig] = None,
) -> Optional[Path]:
    """
    Generate binaural beats from session manifest.

    Reads the binaural configuration from the manifest and generates
    the appropriate audio file. Supports enhanced features via manifest
    or explicit parameters.

    Args:
        manifest: Session manifest dictionary
        session_dir: Path to session directory
        harmonics: Override harmonic config (reads from manifest if None)
        micro_mod: Override micro-modulation config (reads from manifest if None)
        spatial: Override spatial config (reads from manifest if None)

    Returns:
        Path to generated stem file, or None if binaural is disabled
    """
    session_dir = Path(session_dir)

    if not manifest['sound_bed']['binaural'].get('enabled', False):
        print("Binaural beats disabled in manifest")
        return None

    binaural_config = manifest['sound_bed']['binaural']

    # Build sections and extract events
    sections = _build_sections_from_manifest(binaural_config)
    gamma_bursts = _extract_gamma_bursts(manifest)

    # Get enhancement configs (override or from manifest)
    harm_cfg = _get_enhancement_config(binaural_config, harmonics, 'harmonics')
    mod_cfg = _get_enhancement_config(binaural_config, micro_mod, 'micro_modulation')
    spatial_cfg = _get_enhancement_config(binaural_config, spatial, 'spatial')

    # Generate audio
    audio = generate(
        sections=sections,
        duration_sec=manifest['session']['duration'],
        carrier_freq=binaural_config.get('base_hz', 200),
        gamma_bursts=gamma_bursts if gamma_bursts else None,
        harmonics=harm_cfg,
        micro_mod=mod_cfg,
        spatial=spatial_cfg,
    )

    # Save
    stem_path = session_dir / "working_files" / "stems" / "binaural.wav"
    save_stem(audio, stem_path)

    return stem_path


# =============================================================================
# DUAL-LAYER BINAURAL GENERATION (PHASE 3 ENHANCEMENT)
# =============================================================================
# Creates simultaneous primary + delta sublayer for "deep floating" sensation
# This mimics advanced clinical entrainment systems

class DualLayerConfig(TypedDict, total=False):
    """Configuration for dual-layer binaural generation."""
    enabled: bool
    sublayer_freq: float       # Delta frequency for sublayer (default 1.5 Hz)
    sublayer_level_db: float   # Level relative to primary (default -6 dB)
    sublayer_carrier_offset: float  # Carrier offset for sublayer (default +50 Hz)
    crossfade_sec: float       # Crossfade between layers (default 2.0)


DEFAULT_DUAL_LAYER: DualLayerConfig = {
    'enabled': True,
    'sublayer_freq': 1.5,          # Delta frequency
    'sublayer_level_db': -6,       # 6 dB quieter than primary
    'sublayer_carrier_offset': 50,  # Slightly higher carrier for separation
    'crossfade_sec': 2.0,
}


def generate_dual_layer(
    sections: List[SectionDict],
    duration_sec: float,
    sample_rate: int = 48000,
    carrier_freq: float = 200,
    amplitude: float = 0.25,
    fade_in_sec: float = 5.0,
    fade_out_sec: float = 8.0,
    gamma_bursts: Optional[List[GammaBurstDict]] = None,
    marker_timestamps: Optional[Dict[str, float]] = None,
    harmonics: Optional[HarmonicConfig] = None,
    micro_mod: Optional[MicroModConfig] = None,
    spatial: Optional[SpatialConfig] = None,
    dual_layer: Optional[DualLayerConfig] = None,
) -> StereoAudio:
    """
    Generate dual-layer binaural beats with primary + delta sublayer.

    This creates the "deep floating" sensation used in advanced clinical
    entrainment systems. The primary layer follows the specified sections
    while a constant delta sublayer (1.5 Hz default) runs underneath,
    creating simultaneous alpha/theta entrainment with grounding delta.

    The dual-layer approach provides:
    - Primary layer: Dynamic beat frequency following hypnosis arc
    - Delta sublayer: Constant deep-trance foundation at ~1.5 Hz
    - Physical heaviness sensation from delta
    - Enhanced trance depth without disorientation

    Args:
        sections: List of section definitions for PRIMARY layer
        duration_sec: Total duration in seconds
        sample_rate: Sample rate in Hz (default: 48000)
        carrier_freq: Base carrier frequency for primary (default: 200)
        amplitude: Total output amplitude 0.0-1.0 (default: 0.25)
        fade_in_sec: Fade in duration in seconds (default: 5.0)
        fade_out_sec: Fade out duration in seconds (default: 8.0)
        gamma_bursts: Optional gamma burst events (applied to primary only)
        marker_timestamps: Optional dict mapping marker names to timestamps
            for marker-based gamma burst positioning
        harmonics: Harmonic stacking config
        micro_mod: Micro-modulation config
        spatial: Spatial panning config
        dual_layer: Dual-layer configuration (pass None for defaults)

    Returns:
        Stereo audio as numpy array with shape (samples, 2)

    Example:
        >>> sections = [
        ...     {'start': 0, 'end': 300, 'freq_start': 10, 'freq_end': 4,
        ...      'transition': 'logarithmic'},  # Alpha to theta
        ...     {'start': 300, 'end': 600, 'freq_start': 4, 'freq_end': 7,
        ...      'transition': 'logarithmic'},  # Return to light theta
        ... ]
        >>> audio = generate_dual_layer(
        ...     sections, duration_sec=600,
        ...     dual_layer={'sublayer_freq': 1.5, 'sublayer_level_db': -6}
        ... )
    """
    # Merge dual-layer config with defaults
    dl_cfg = {**DEFAULT_DUAL_LAYER, **(dual_layer or {})}

    if not dl_cfg.get('enabled', True):
        # Fall back to standard generation
        return generate(
            sections, duration_sec, sample_rate, carrier_freq,
            amplitude, fade_in_sec, fade_out_sec, gamma_bursts,
            marker_timestamps, harmonics, micro_mod, spatial
        )

    sublayer_freq = dl_cfg.get('sublayer_freq', 1.5)
    sublayer_db = dl_cfg.get('sublayer_level_db', -6)
    carrier_offset = dl_cfg.get('sublayer_carrier_offset', 50)

    print(f"Generating DUAL-LAYER binaural beats: {duration_sec/60:.1f} min")
    print("  Primary: sections with dynamic beat frequency")
    print(f"  Sublayer: constant {sublayer_freq} Hz delta at {sublayer_db} dB")

    # Generate primary layer (uses full amplitude, we'll adjust later)
    primary = generate(
        sections, duration_sec, sample_rate, carrier_freq,
        amplitude=1.0,  # Generate at full scale, mix later
        fade_in_sec=0,  # We'll apply fades to combined signal
        fade_out_sec=0,
        gamma_bursts=gamma_bursts,
        marker_timestamps=marker_timestamps,
        harmonics=harmonics,
        micro_mod=micro_mod,
        spatial=spatial,
    )

    # Generate delta sublayer - constant frequency throughout
    sublayer_carrier = carrier_freq + carrier_offset
    sublayer_sections: List[SectionDict] = [{
        'start': 0,
        'end': int(duration_sec),
        'freq_start': sublayer_freq,
        'freq_end': sublayer_freq,
        'transition': 'hold',
        'carrier_start': sublayer_carrier,
        'carrier_end': sublayer_carrier,
    }]

    # Use minimal enhancements for sublayer (cleaner, less distracting)
    sublayer = generate(
        sublayer_sections, duration_sec, sample_rate, sublayer_carrier,
        amplitude=1.0,
        fade_in_sec=0,
        fade_out_sec=0,
        gamma_bursts=None,  # No gamma in sublayer
        harmonics={'enabled': True, 'second_harmonic': 0.2, 'third_harmonic': 0.1,
                   'sub_harmonic': 0.3, 'air_shimmer': 0.0},  # More sub, no air
        micro_mod={'enabled': True, 'amplitude_mod_depth': 0.05},  # Subtle mod
        spatial={'enabled': False},  # No panning (centered for stability)
    )

    # Calculate mix levels
    # Primary at 0 dB reference, sublayer at specified dB below
    sublayer_linear = 10 ** (sublayer_db / 20)
    primary_level = 1.0
    sublayer_level = sublayer_linear

    # Normalize so combined peak is at target amplitude
    total_level = primary_level + sublayer_level
    mix_scale = amplitude / total_level

    # Mix layers
    combined = (primary * primary_level + sublayer * sublayer_level) * mix_scale

    # Apply crossfade at start (sublayer fades in slightly before primary stabilizes)
    crossfade_samples = int(dl_cfg.get('crossfade_sec', 2.0) * sample_rate)
    if crossfade_samples > 0 and crossfade_samples < len(combined) // 4:
        # Primary starts strong, sublayer fades in
        sublayer_fade = np.linspace(0, 1, crossfade_samples).astype(np.float32)
        for ch in range(2):
            combined[:crossfade_samples, ch] = (
                primary[:crossfade_samples, ch] * primary_level +
                sublayer[:crossfade_samples, ch] * sublayer_level * sublayer_fade
            ) * mix_scale

    # Apply global fades
    combined = _apply_fades(combined, fade_in_sec, fade_out_sec, sample_rate)

    print(f"✓ Dual-layer binaural generated: {len(combined)/sample_rate/60:.1f} min")
    print(f"  Mix: primary={primary_level:.2f}, sublayer={sublayer_level:.2f} "
          f"(total scaled by {mix_scale:.2f})")

    return combined


# =============================================================================
# MULTI-LAYER BINAURAL GENERATION (PHASE 4 ENHANCEMENT)
# =============================================================================
# Extends dual-layer to support flexible multi-layer configurations
# Triple-layer example: Primary (dynamic) + Alpha cushion + Delta foundation


class LayerDef(TypedDict, total=False):
    """Definition for a single layer in multi-layer binaural generation."""
    name: str                  # Layer name for logging
    freq_hz: float             # Beat frequency (ignored if 'dynamic' mode)
    mode: str                  # 'static' (constant freq) or 'dynamic' (follows sections)
    carrier_offset: float      # Offset from base carrier (Hz)
    level_db: float            # Level relative to primary (0 = same, -6 = half)
    harmonics: HarmonicConfig  # Layer-specific harmonic config
    micro_mod: MicroModConfig  # Layer-specific micro-mod config
    spatial: SpatialConfig     # Layer-specific spatial config


class MultiLayerConfig(TypedDict, total=False):
    """Configuration for multi-layer binaural generation."""
    enabled: bool
    layers: List[LayerDef]     # List of layer definitions
    crossfade_sec: float       # Crossfade between layers at start


# Preset multi-layer configurations
MULTI_LAYER_PRESETS: Dict[str, MultiLayerConfig] = {
    'triple_deep': {
        'enabled': True,
        'crossfade_sec': 3.0,
        'layers': [
            {
                'name': 'primary',
                'mode': 'dynamic',
                'carrier_offset': 0,
                'level_db': 0,
            },
            {
                'name': 'alpha_cushion',
                'mode': 'static',
                'freq_hz': 10.0,
                'carrier_offset': 30,
                'level_db': -8,
                'harmonics': {'enabled': True, 'second_harmonic': 0.15,
                              'third_harmonic': 0.05, 'sub_harmonic': 0.1,
                              'air_shimmer': 0.05},
                'spatial': {'enabled': True, 'pan_rate': 0.015},
            },
            {
                'name': 'delta_foundation',
                'mode': 'static',
                'freq_hz': 1.5,
                'carrier_offset': 60,
                'level_db': -6,
                'harmonics': {'enabled': True, 'second_harmonic': 0.1,
                              'third_harmonic': 0.0, 'sub_harmonic': 0.4,
                              'air_shimmer': 0.0},
                'spatial': {'enabled': False},
            },
        ],
    },
    'dual_grounded': {
        'enabled': True,
        'crossfade_sec': 2.0,
        'layers': [
            {
                'name': 'primary',
                'mode': 'dynamic',
                'carrier_offset': 0,
                'level_db': 0,
            },
            {
                'name': 'delta_foundation',
                'mode': 'static',
                'freq_hz': 2.0,
                'carrier_offset': 50,
                'level_db': -6,
            },
        ],
    },
    'theta_alpha_blend': {
        'enabled': True,
        'crossfade_sec': 2.5,
        'layers': [
            {
                'name': 'primary',
                'mode': 'dynamic',
                'carrier_offset': 0,
                'level_db': 0,
            },
            {
                'name': 'alpha_bed',
                'mode': 'static',
                'freq_hz': 10.0,
                'carrier_offset': 25,
                'level_db': -4,
            },
        ],
    },
}


def _generate_layer(
    layer: LayerDef,
    sections: List[SectionDict],
    duration_sec: float,
    sample_rate: int,
    base_carrier: float,
    gamma_bursts: Optional[List[GammaBurstDict]],
    marker_timestamps: Optional[Dict[str, float]],
    default_harmonics: Optional[HarmonicConfig],
    default_micro_mod: Optional[MicroModConfig],
    default_spatial: Optional[SpatialConfig],
) -> StereoAudio:
    """Generate a single layer for multi-layer binaural."""
    mode = layer.get('mode', 'static')
    carrier = base_carrier + layer.get('carrier_offset', 0)

    # Layer-specific configs override defaults
    harm_cfg = layer.get('harmonics', default_harmonics)
    mod_cfg = layer.get('micro_mod', default_micro_mod)
    spatial_cfg = layer.get('spatial', default_spatial)

    if mode == 'dynamic':
        # Dynamic layer follows the sections
        return generate(
            sections, duration_sec, sample_rate, carrier,
            amplitude=1.0,
            fade_in_sec=0,
            fade_out_sec=0,
            gamma_bursts=gamma_bursts,
            marker_timestamps=marker_timestamps,
            harmonics=harm_cfg,
            micro_mod=mod_cfg,
            spatial=spatial_cfg,
        )
    else:
        # Static layer has constant frequency
        freq = layer.get('freq_hz', 6.0)
        static_sections: List[SectionDict] = [{
            'start': 0,
            'end': int(duration_sec),
            'freq_start': freq,
            'freq_end': freq,
            'transition': 'hold',
            'carrier_start': carrier,
            'carrier_end': carrier,
        }]
        return generate(
            static_sections, duration_sec, sample_rate, carrier,
            amplitude=1.0,
            fade_in_sec=0,
            fade_out_sec=0,
            gamma_bursts=None,  # No gamma on static layers
            harmonics=harm_cfg,
            micro_mod=mod_cfg,
            spatial=spatial_cfg,
        )


class MultiLayerParams(TypedDict, total=False):
    """Parameters for multi-layer generation (reduces argument count)."""
    sample_rate: int
    carrier_freq: float
    amplitude: float
    fade_in_sec: float
    fade_out_sec: float
    gamma_bursts: Optional[List[GammaBurstDict]]
    marker_timestamps: Optional[Dict[str, float]]
    harmonics: Optional[HarmonicConfig]
    micro_mod: Optional[MicroModConfig]
    spatial: Optional[SpatialConfig]


def _get_multi_layer_config(
    preset: Optional[str], multi_layer: Optional[MultiLayerConfig]
) -> MultiLayerConfig:
    """Get multi-layer config from preset or parameter."""
    if preset and preset in MULTI_LAYER_PRESETS:
        return {**MULTI_LAYER_PRESETS[preset], **(multi_layer or {})}
    if multi_layer:
        return multi_layer
    return MULTI_LAYER_PRESETS['dual_grounded']


def _mix_layers(
    layer_audios: List[StereoAudio],
    layer_levels: List[float],
    amplitude: float,
) -> Tuple[StereoAudio, float]:
    """Mix multiple layers with specified levels. Returns combined audio and mix scale."""
    total_level = sum(layer_levels)
    mix_scale = amplitude / total_level

    combined = np.zeros_like(layer_audios[0])
    for audio, level in zip(layer_audios, layer_levels):
        combined += audio * level
    combined *= mix_scale

    return combined, mix_scale


def _apply_layer_crossfade(
    combined: StereoAudio,
    layer_audios: List[StereoAudio],
    layer_levels: List[float],
    crossfade_sec: float,
    sample_rate: int,
    mix_scale: float,
) -> StereoAudio:
    """Apply crossfade where secondary layers fade in."""
    crossfade_samples = int(crossfade_sec * sample_rate)
    if crossfade_samples <= 0 or crossfade_samples >= len(combined) // 4:
        return combined

    fade_curve = np.linspace(0, 1, crossfade_samples).astype(np.float32)
    combined[:crossfade_samples] = np.zeros((crossfade_samples, 2), dtype=np.float32)

    for i, (audio, level) in enumerate(zip(layer_audios, layer_levels)):
        if i == 0:
            combined[:crossfade_samples] += audio[:crossfade_samples] * level * mix_scale
        else:
            for ch in range(2):
                combined[:crossfade_samples, ch] += (
                    audio[:crossfade_samples, ch] * level * fade_curve * mix_scale
                )
    return combined


def generate_multi_layer(
    sections: List[SectionDict],
    duration_sec: float,
    params: Optional[MultiLayerParams] = None,
    multi_layer: Optional[MultiLayerConfig] = None,
    preset: Optional[str] = None,
) -> StereoAudio:
    """
    Generate multi-layer binaural beats with flexible layer configuration.

    This extends dual-layer to support any number of simultaneous layers,
    each with its own frequency, carrier offset, and processing settings.
    Useful for complex entrainment patterns like triple-layer.

    Triple-layer example:
    - Primary: Dynamic theta following hypnosis arc
    - Alpha cushion: Constant 10 Hz for cognitive stability
    - Delta foundation: Constant 1.5 Hz for deep grounding

    Args:
        sections: List of section definitions for dynamic layers
        duration_sec: Total duration in seconds
        params: Generation parameters (sample_rate, carrier_freq, amplitude, etc.)
        multi_layer: Multi-layer configuration (layers list)
        preset: Preset name ('triple_deep', 'dual_grounded', 'theta_alpha_blend')

    Returns:
        Stereo audio as numpy array with shape (samples, 2)

    Example:
        >>> # Use preset
        >>> audio = generate_multi_layer(sections, 1800, preset='triple_deep')

        >>> # Custom configuration
        >>> config = {
        ...     'layers': [
        ...         {'name': 'primary', 'mode': 'dynamic', 'level_db': 0},
        ...         {'name': 'alpha', 'mode': 'static', 'freq_hz': 10,
        ...          'carrier_offset': 30, 'level_db': -6},
        ...         {'name': 'delta', 'mode': 'static', 'freq_hz': 1.5,
        ...          'carrier_offset': 60, 'level_db': -8},
        ...     ]
        ... }
        >>> audio = generate_multi_layer(sections, 1800, multi_layer=config)
    """
    # Extract parameters with defaults
    p = params or {}
    sample_rate = p.get('sample_rate', 48000)
    carrier_freq = p.get('carrier_freq', 200)
    amplitude = p.get('amplitude', 0.25)
    fade_in_sec = p.get('fade_in_sec', 5.0)
    fade_out_sec = p.get('fade_out_sec', 8.0)
    gamma_bursts = p.get('gamma_bursts')
    marker_timestamps = p.get('marker_timestamps')
    harmonics = p.get('harmonics')
    micro_mod = p.get('micro_mod')
    spatial = p.get('spatial')

    cfg = _get_multi_layer_config(preset, multi_layer)

    if not cfg.get('enabled', True):
        return generate(
            sections, duration_sec, sample_rate, carrier_freq,
            amplitude, fade_in_sec, fade_out_sec, gamma_bursts,
            marker_timestamps, harmonics, micro_mod, spatial
        )

    layers_config = cfg.get('layers', [])
    if not layers_config:
        return generate(
            sections, duration_sec, sample_rate, carrier_freq,
            amplitude, fade_in_sec, fade_out_sec, gamma_bursts,
            marker_timestamps, harmonics, micro_mod, spatial
        )

    print(f"Generating MULTI-LAYER binaural beats: {duration_sec/60:.1f} min")
    print(f"  Layers: {len(layers_config)}")

    # Generate each layer
    layer_audios: List[StereoAudio] = []
    layer_levels: List[float] = []

    for layer_def in layers_config:
        name = layer_def.get('name', f'layer_{len(layer_audios)}')
        mode = layer_def.get('mode', 'static')
        freq = layer_def.get('freq_hz', 6.0)
        level_db = layer_def.get('level_db', 0)

        mode_str = "dynamic" if mode == 'dynamic' else f"static {freq} Hz"
        print(f"    {name}: {mode_str} at {level_db} dB")

        audio = _generate_layer(
            layer_def, sections, duration_sec, sample_rate, carrier_freq,
            gamma_bursts, marker_timestamps, harmonics, micro_mod, spatial
        )
        layer_audios.append(audio)
        layer_levels.append(10 ** (level_db / 20))

    # Mix and apply crossfade
    combined, mix_scale = _mix_layers(layer_audios, layer_levels, amplitude)
    combined = _apply_layer_crossfade(
        combined, layer_audios, layer_levels,
        cfg.get('crossfade_sec', 2.0), sample_rate, mix_scale
    )
    combined = _apply_fades(combined, fade_in_sec, fade_out_sec, sample_rate)

    print(f"✓ Multi-layer binaural generated: {len(combined)/sample_rate/60:.1f} min")
    level_strs = [f"{l:.2f}" for l in layer_levels]
    print(f"  Mix levels: {', '.join(level_strs)} (scaled by {mix_scale:.2f})")

    return combined


def generate_dual_layer_from_manifest(
    manifest: Dict[str, Any],
    session_dir: Union[str, Path],
    harmonics: Optional[HarmonicConfig] = None,
    micro_mod: Optional[MicroModConfig] = None,
    spatial: Optional[SpatialConfig] = None,
    dual_layer: Optional[DualLayerConfig] = None,
) -> Optional[Path]:
    """
    Generate dual-layer binaural beats from session manifest.

    This is the manifest-driven version of generate_dual_layer.
    If dual_layer configuration is not provided and not in manifest,
    dual-layer is enabled by default with standard delta sublayer.

    Args:
        manifest: Session manifest dictionary
        session_dir: Path to session directory
        harmonics: Override harmonic config
        micro_mod: Override micro-modulation config
        spatial: Override spatial config
        dual_layer: Dual-layer config (uses defaults if None)

    Returns:
        Path to generated stem file, or None if binaural is disabled
    """
    session_dir = Path(session_dir)

    if not manifest['sound_bed']['binaural'].get('enabled', False):
        print("Binaural beats disabled in manifest")
        return None

    binaural_config = manifest['sound_bed']['binaural']

    # Build sections and extract events
    sections = _build_sections_from_manifest(binaural_config)
    gamma_bursts = _extract_gamma_bursts(manifest)

    # Get enhancement configs
    harm_cfg = _get_enhancement_config(binaural_config, harmonics, 'harmonics')
    mod_cfg = _get_enhancement_config(binaural_config, micro_mod, 'micro_modulation')
    spatial_cfg = _get_enhancement_config(binaural_config, spatial, 'spatial')

    # Get dual-layer config from manifest or use override
    if dual_layer is not None:
        dl_cfg = dual_layer
    else:
        manifest_dl = binaural_config.get('dual_layer', {})
        dl_cfg = manifest_dl if manifest_dl else None

    # Generate audio with dual-layer
    audio = generate_dual_layer(
        sections=sections,
        duration_sec=manifest['session']['duration'],
        carrier_freq=binaural_config.get('base_hz', 200),
        gamma_bursts=gamma_bursts if gamma_bursts else None,
        harmonics=harm_cfg,
        micro_mod=mod_cfg,
        spatial=spatial_cfg,
        dual_layer=dl_cfg,
    )

    # Save with distinct filename
    stem_path = session_dir / "working_files" / "stems" / "binaural_dual_layer.wav"
    save_stem(audio, stem_path)

    return stem_path


# =============================================================================
# EXAMPLE USAGE AND TESTING
# =============================================================================

if __name__ == '__main__':
    import sys

    print("=" * 70)
    print("ENHANCED BINAURAL BEAT GENERATOR - TEST")
    print("=" * 70)

    # Test 1: Basic generation (backward compatible)
    print("\n[Test 1] Basic 2-minute track (backward compatible)...")
    test_sections_basic: List[SectionDict] = [
        {'start': 0, 'end': 60, 'freq_start': 10, 'freq_end': 10},
        {'start': 60, 'end': 120, 'freq_start': 10, 'freq_end': 6}
    ]
    audio_basic = generate(
        test_sections_basic, duration_sec=120, carrier_freq=200,
        harmonics={'enabled': False},
        micro_mod={'enabled': False},
        spatial={'enabled': False}
    )
    save_stem(audio_basic, "test_binaural_basic.wav")

    # Test 2: Enhanced with all features
    print("\n[Test 2] Enhanced 2-minute track (all features)...")
    test_sections_enhanced: List[SectionDict] = [
        {'start': 0, 'end': 60, 'freq_start': 10, 'freq_end': 10,
         'carrier_start': 432, 'carrier_end': 400},
        {'start': 60, 'end': 120, 'freq_start': 10, 'freq_end': 6,
         'carrier_start': 400, 'carrier_end': 360}
    ]
    audio_enhanced = generate(
        test_sections_enhanced, duration_sec=120, carrier_freq=432,
        harmonics={'enabled': True, 'second_harmonic': 0.3, 'sub_harmonic': 0.2},
        micro_mod={'enabled': True, 'amplitude_mod_depth': 0.1},
        spatial={'enabled': True, 'depth': 0.15}
    )
    save_stem(audio_enhanced, "test_binaural_enhanced.wav")

    # Test 3: Luminous Being style (healing, 432 Hz carrier arc)
    print("\n[Test 3] Luminous Being style (30-second demo)...")
    luminous_sections: List[SectionDict] = [
        {'start': 0, 'end': 10, 'freq_start': 10, 'freq_end': 7,
         'carrier_start': 432, 'carrier_end': 400, 'transition': 'logarithmic'},
        {'start': 10, 'end': 20, 'freq_start': 7, 'freq_end': 4,
         'carrier_start': 400, 'carrier_end': 360, 'transition': 'logarithmic'},
        {'start': 20, 'end': 30, 'freq_start': 4, 'freq_end': 9,
         'carrier_start': 360, 'carrier_end': 420, 'transition': 'logarithmic'}
    ]
    audio_luminous = generate(
        luminous_sections, duration_sec=30, carrier_freq=432,
        fade_in_sec=2, fade_out_sec=3
    )
    save_stem(audio_luminous, "test_binaural_luminous.wav")

    print("\n" + "=" * 70)
    print("✓ ALL TESTS COMPLETE")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - test_binaural_basic.wav    (no enhancements)")
    print("  - test_binaural_enhanced.wav (harmonics + micro-mod + spatial)")
    print("  - test_binaural_luminous.wav (Luminous Being style)")

    sys.exit(0)
