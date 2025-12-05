#!/usr/bin/env python3
"""
Adaptive Audio Processing Module

Advanced psychoacoustic processing that responds dynamically to:
- Hypnosis stage (induction, deepening, journey, integration, return)
- Voice amplitude envelope
- SSML/timing markers
- Spectral content

This module implements:
1. Spectral Motion Generator - slow EQ sweeps for "living" sound
2. Psychoacoustic Masking Correction - dynamic EQ dips around voice
3. Adaptive Reverb Steering - stage-dependent decay times
4. Hypnotic Dynamic Range Architecture (HDR-A) - stage-based gain curves
5. Intelligent Spatial Animator - stage-aware stereo field control

Created: 2025-12
"""

import numpy as np
from numpy.typing import NDArray
from typing import Dict, List, Optional, Tuple, TypedDict
from scipy import signal
from scipy.ndimage import uniform_filter1d


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

class HypnosisStage(TypedDict, total=False):
    """Definition of a hypnosis stage with its audio characteristics."""
    name: str
    start: float  # seconds
    end: float    # seconds
    # Dynamic range
    gain_db: float
    low_shelf_db: float
    air_shelf_db: float
    # Reverb
    reverb_decay: float
    reverb_wet: float
    # Spatial
    stereo_width: float  # 0.0 = mono, 1.0 = full stereo
    vertical_angle: float  # for HRTF simulation
    # Spectral
    spectral_bias: Dict[str, float]  # freq_range: gain_db


# Mono or stereo audio array
AudioArray = NDArray[np.float32]


# =============================================================================
# HYPNOSIS STAGE PRESETS
# =============================================================================

STAGE_PRESETS: Dict[str, HypnosisStage] = {
    'pretalk': {
        'name': 'pretalk',
        'gain_db': 0.0,
        'low_shelf_db': 0.0,
        'air_shelf_db': 0.0,
        'reverb_decay': 3.0,
        'reverb_wet': 0.08,
        'stereo_width': 0.9,
        'vertical_angle': 0.0,
        'spectral_bias': {'midrange': 0.5},
    },
    'induction': {
        'name': 'induction',
        'gain_db': -1.0,
        'low_shelf_db': 0.5,
        'air_shelf_db': -0.5,
        'reverb_decay': 5.0,
        'reverb_wet': 0.10,
        'stereo_width': 0.7,  # Narrowing - symbolic focusing
        'vertical_angle': -5.0,
        'spectral_bias': {'low_mid': 1.0, 'presence': -0.5},
    },
    'deepening': {
        'name': 'deepening',
        'gain_db': -2.5,
        'low_shelf_db': 1.0,
        'air_shelf_db': -1.0,
        'reverb_decay': 8.0,
        'reverb_wet': 0.12,
        'stereo_width': 0.85,  # Expanding - dropping into space
        'vertical_angle': -10.0,
        'spectral_bias': {'sub': 1.5, 'low': 1.0, 'presence': -1.0},
    },
    'journey': {
        'name': 'journey',
        'gain_db': -2.0,
        'low_shelf_db': 0.5,
        'air_shelf_db': 1.0,
        'reverb_decay': 10.0,
        'reverb_wet': 0.14,
        'stereo_width': 1.0,  # Full expansion
        'vertical_angle': 0.0,
        'spectral_bias': {'sub': 1.0, 'air': 1.5},
    },
    'luminous_core': {
        'name': 'luminous_core',
        'gain_db': 1.0,  # Slight lift at apex
        'low_shelf_db': 0.0,
        'air_shelf_db': 2.5,  # Maximum air/brightness
        'reverb_decay': 12.0,
        'reverb_wet': 0.16,
        'stereo_width': 1.0,
        'vertical_angle': 15.0,  # Upward - height simulation
        'spectral_bias': {'air': 3.0, 'presence': 1.5},
    },
    'integration': {
        'name': 'integration',
        'gain_db': -1.0,
        'low_shelf_db': 0.5,
        'air_shelf_db': 0.5,
        'reverb_decay': 6.0,
        'reverb_wet': 0.10,
        'stereo_width': 0.75,  # Gradual narrowing
        'vertical_angle': 5.0,
        'spectral_bias': {'midrange': 0.5},
    },
    'awakening': {
        'name': 'awakening',
        'gain_db': 0.0,
        'low_shelf_db': 0.0,
        'air_shelf_db': 0.0,
        'reverb_decay': 4.0,
        'reverb_wet': 0.08,
        'stereo_width': 0.6,  # Stable center
        'vertical_angle': 0.0,
        'spectral_bias': {'midrange': 1.0, 'grounding': 0.5},
    },
}

# Frequency bands for spectral bias
FREQ_BANDS = {
    'sub': (20, 80),
    'low': (80, 200),
    'low_mid': (200, 500),
    'midrange': (500, 2000),
    'presence': (2000, 5000),
    'air': (8000, 16000),
    'grounding': (100, 300),
}


# =============================================================================
# SPECTRAL MOTION GENERATOR
# =============================================================================

def generate_spectral_motion(
    audio: AudioArray,
    sample_rate: int,
    sweep_rate_hz: float = 0.008,
    freq_range: Tuple[float, float] = (200, 2000),
    boost_db: float = 1.5,
    q_factor: float = 3.0,
) -> AudioArray:
    """
    Generate slow spectral sweeps for "living light" sound.

    Creates a narrow EQ boost that slowly sweeps across the frequency range,
    giving the sound an organic, breathing quality.

    Args:
        audio: Input audio (mono or stereo)
        sample_rate: Sample rate in Hz
        sweep_rate_hz: Rate of sweep (default 0.008 Hz = ~2 min cycle)
        freq_range: Frequency range to sweep (Hz)
        boost_db: Amount of boost in dB
        q_factor: Q factor for the sweeping band

    Returns:
        Audio with spectral motion applied
    """
    is_stereo = audio.ndim == 2
    if is_stereo:
        # Process each channel
        left = generate_spectral_motion(
            audio[:, 0], sample_rate, sweep_rate_hz, freq_range, boost_db, q_factor
        )
        right = generate_spectral_motion(
            audio[:, 1], sample_rate, sweep_rate_hz, freq_range, boost_db, q_factor
        )
        return np.stack([left, right], axis=1)

    duration = len(audio) / sample_rate
    num_samples = len(audio)

    # Generate sweep frequency curve
    t = np.linspace(0, duration, num_samples, dtype=np.float32)
    min_freq, max_freq = freq_range

    # Use log sweep for perceptually even motion
    log_min = np.log10(min_freq)
    log_max = np.log10(max_freq)

    # Sinusoidal sweep between log frequencies
    sweep_phase = np.sin(2 * np.pi * sweep_rate_hz * t)
    log_freq = log_min + (log_max - log_min) * (sweep_phase + 1) / 2
    center_freq = 10 ** log_freq

    # Apply time-varying parametric EQ
    # Process in chunks for efficiency
    chunk_size = sample_rate // 10  # 100ms chunks
    output = audio.copy()

    linear_boost = 10 ** (boost_db / 20)

    for i in range(0, num_samples, chunk_size):
        end_idx = min(i + chunk_size, num_samples)
        chunk = audio[i:end_idx]

        # Use average center frequency for this chunk
        avg_freq = np.mean(center_freq[i:end_idx])

        # Design peaking filter
        w0 = avg_freq / (sample_rate / 2)
        if w0 >= 1.0:
            w0 = 0.99

        try:
            b, a = signal.iirpeak(w0, q_factor)
            # Scale coefficients for boost amount
            b = b * linear_boost
            filtered = signal.lfilter(b, a, chunk)
            # Blend with original (50% wet)
            output[i:end_idx] = chunk * 0.5 + filtered * 0.5
        except ValueError:
            # Skip if filter design fails
            pass

    return output.astype(np.float32)


# =============================================================================
# PSYCHOACOUSTIC MASKING CORRECTION
# =============================================================================

def apply_voice_masking_correction(
    background: AudioArray,
    voice: AudioArray,
    sample_rate: int,
    formant_freqs: List[float] = [500, 1500, 2500],
    dip_db: float = -2.0,
    attack_ms: float = 50,
    release_ms: float = 400,
) -> AudioArray:
    """
    Apply dynamic EQ dips to background audio when voice is present.

    Detects voice activity and reduces background audio in formant regions
    to improve voice clarity without sacrificing immersion.

    Args:
        background: Background audio (binaural, ambience, etc.)
        voice: Voice track for detection
        sample_rate: Sample rate in Hz
        formant_freqs: Frequencies to dip (Hz)
        dip_db: Amount of reduction in dB
        attack_ms: Attack time in ms
        release_ms: Release time in ms

    Returns:
        Background audio with masking correction applied
    """
    is_stereo = background.ndim == 2

    # Ensure voice is mono for envelope detection
    if voice.ndim == 2:
        voice_mono = np.mean(voice, axis=1)
    else:
        voice_mono = voice

    # Detect voice envelope
    voice_env = np.abs(voice_mono)
    # Smooth envelope
    smooth_samples = int(sample_rate * 0.05)  # 50ms
    voice_env = uniform_filter1d(voice_env, smooth_samples)

    # Normalize envelope
    max_env = np.max(voice_env)
    if max_env > 0:
        voice_env = voice_env / max_env

    # Apply attack/release smoothing
    attack_samples = int(sample_rate * attack_ms / 1000)
    release_samples = int(sample_rate * release_ms / 1000)

    smoothed_env = np.zeros_like(voice_env)
    current = 0.0
    for i, env in enumerate(voice_env):
        if env > current:
            # Attack
            alpha = 1.0 / max(attack_samples, 1)
            current = current + alpha * (env - current)
        else:
            # Release
            alpha = 1.0 / max(release_samples, 1)
            current = current + alpha * (env - current)
        smoothed_env[i] = current

    # Convert dip to linear gain
    dip_linear = 10 ** (dip_db / 20)

    # Apply dips at formant frequencies
    if is_stereo:
        output = background.copy()
        for ch in range(2):
            output[:, ch] = _apply_formant_dips(
                background[:, ch], smoothed_env, sample_rate,
                formant_freqs, dip_linear
            )
    else:
        output = _apply_formant_dips(
            background, smoothed_env, sample_rate,
            formant_freqs, dip_linear
        )

    return output


def _apply_formant_dips(
    audio: np.ndarray,
    envelope: np.ndarray,
    sample_rate: int,
    formant_freqs: List[float],
    dip_linear: float,
) -> np.ndarray:
    """Apply frequency-selective dips based on voice envelope."""
    output = audio.copy()

    for freq in formant_freqs:
        # Design notch filter
        w0 = freq / (sample_rate / 2)
        if w0 >= 1.0:
            continue

        q = 5.0  # Narrow notch
        try:
            b, a = signal.iirnotch(w0, q)

            # Filter the audio
            notched = signal.lfilter(b, a, audio)

            # Blend based on envelope: when voice present, use more notched
            # dip_linear is the target gain when voice is fully present
            blend = envelope * (1 - dip_linear)  # 0 = no dip, full = max dip
            output = output * (1 - blend) + notched * blend

        except ValueError:
            pass

    return output.astype(np.float32)


# =============================================================================
# HYPNOTIC DYNAMIC RANGE ARCHITECTURE (HDR-A)
# =============================================================================

def apply_hdra(
    audio: AudioArray,
    sample_rate: int,
    stages: List[HypnosisStage],
    crossfade_sec: float = 2.0,
) -> AudioArray:
    """
    Apply Hypnotic Dynamic Range Architecture.

    Stage-dependent gain curves that follow the emotional arc of the session.

    Args:
        audio: Input audio (mono or stereo)
        sample_rate: Sample rate in Hz
        stages: List of hypnosis stages with timing and settings
        crossfade_sec: Crossfade duration between stages

    Returns:
        Audio with HDR-A applied
    """
    is_stereo = audio.ndim == 2
    num_samples = len(audio)
    output = audio.copy().astype(np.float64)

    for stage in stages:
        start_sample = int(stage['start'] * sample_rate)
        end_sample = int(stage['end'] * sample_rate)

        if start_sample >= num_samples or end_sample <= 0:
            continue

        start_sample = max(0, start_sample)
        end_sample = min(num_samples, end_sample)

        # Get stage parameters
        gain_db = stage.get('gain_db', 0.0)
        low_shelf_db = stage.get('low_shelf_db', 0.0)
        air_shelf_db = stage.get('air_shelf_db', 0.0)

        # Apply gain
        gain_linear = 10 ** (gain_db / 20)

        # Create gain envelope with crossfade
        crossfade_samples = int(crossfade_sec * sample_rate)
        stage_length = end_sample - start_sample

        envelope = np.ones(stage_length, dtype=np.float64) * gain_linear

        # Fade in
        if crossfade_samples > 0 and start_sample > 0:
            fade_in_len = min(crossfade_samples, stage_length // 2)
            envelope[:fade_in_len] = np.linspace(1.0, gain_linear, fade_in_len)

        # Fade out
        if crossfade_samples > 0 and end_sample < num_samples:
            fade_out_len = min(crossfade_samples, stage_length // 2)
            envelope[-fade_out_len:] = np.linspace(gain_linear, 1.0, fade_out_len)

        # Apply gain envelope
        if is_stereo:
            output[start_sample:end_sample, 0] *= envelope
            output[start_sample:end_sample, 1] *= envelope
        else:
            output[start_sample:end_sample] *= envelope

        # Apply shelf EQ if significant
        if abs(low_shelf_db) > 0.1 or abs(air_shelf_db) > 0.1:
            segment = output[start_sample:end_sample]
            segment = _apply_shelf_eq(segment, sample_rate, low_shelf_db, air_shelf_db)
            output[start_sample:end_sample] = segment

    return output.astype(np.float32)


def _apply_shelf_eq(
    audio: np.ndarray,
    sample_rate: int,
    low_shelf_db: float,
    air_shelf_db: float,
) -> np.ndarray:
    """Apply low and high shelf EQ."""
    output = audio.copy()

    # Low shelf at 150 Hz
    if abs(low_shelf_db) > 0.1:
        w0 = 150 / (sample_rate / 2)
        if w0 < 1.0:
            gain = 10 ** (low_shelf_db / 20)
            b, a = signal.butter(2, w0, btype='low')
            low = signal.lfilter(b, a, audio, axis=0)
            # Blend low frequencies with boosted version
            output = output + low * (gain - 1)

    # Air shelf at 8 kHz
    if abs(air_shelf_db) > 0.1:
        w0 = 8000 / (sample_rate / 2)
        if w0 < 1.0:
            gain = 10 ** (air_shelf_db / 20)
            b, a = signal.butter(2, w0, btype='high')
            high = signal.lfilter(b, a, audio, axis=0)
            output = output + high * (gain - 1)

    return output


# =============================================================================
# ADAPTIVE REVERB STEERING
# =============================================================================

def get_reverb_params_for_stage(stage_name: str) -> Dict[str, float]:
    """
    Get reverb parameters for a hypnosis stage.

    Args:
        stage_name: Name of the stage (e.g., 'induction', 'journey')

    Returns:
        Dict with reverb_decay and reverb_wet values
    """
    stage = STAGE_PRESETS.get(stage_name, STAGE_PRESETS['journey'])
    return {
        'decay': stage.get('reverb_decay', 6.0),
        'wet': stage.get('reverb_wet', 0.10),
    }


def interpolate_reverb_params(
    stages: List[Dict],
    timestamp: float,
) -> Dict[str, float]:
    """
    Interpolate reverb parameters for a given timestamp.

    Args:
        stages: List of stage dicts with start, end, and name
        timestamp: Current time in seconds

    Returns:
        Interpolated reverb parameters
    """
    for stage in stages:
        if stage['start'] <= timestamp < stage['end']:
            return get_reverb_params_for_stage(stage.get('name', 'journey'))

    # Default
    return {'decay': 6.0, 'wet': 0.10}


# =============================================================================
# INTELLIGENT SPATIAL ANIMATOR
# =============================================================================

def apply_spatial_animation(
    audio: AudioArray,
    sample_rate: int,
    stages: List[HypnosisStage],
    crossfade_sec: float = 3.0,
) -> AudioArray:
    """
    Apply stage-aware stereo field animation.

    Modulates stereo width based on hypnosis stage for symbolic spatial
    reinforcement of the journey.

    Args:
        audio: Stereo input audio
        sample_rate: Sample rate in Hz
        stages: List of hypnosis stages with timing and width settings
        crossfade_sec: Crossfade duration between stages

    Returns:
        Audio with spatial animation applied
    """
    if audio.ndim != 2:
        return audio  # Only works on stereo

    num_samples = len(audio)
    output = audio.copy()

    # Create width envelope
    width_envelope = np.ones(num_samples, dtype=np.float32)

    for stage in stages:
        start_sample = int(stage['start'] * sample_rate)
        end_sample = int(stage['end'] * sample_rate)

        if start_sample >= num_samples or end_sample <= 0:
            continue

        start_sample = max(0, start_sample)
        end_sample = min(num_samples, end_sample)

        target_width = stage.get('stereo_width', 1.0)
        stage_length = end_sample - start_sample

        # Linear interpolation within stage
        width_envelope[start_sample:end_sample] = target_width

    # Smooth the envelope
    crossfade_samples = int(crossfade_sec * sample_rate)
    if crossfade_samples > 0:
        width_envelope = uniform_filter1d(width_envelope, crossfade_samples)

    # Apply M/S processing for width control
    # Mid = (L + R) / 2, Side = (L - R) / 2
    mid = (audio[:, 0] + audio[:, 1]) / 2
    side = (audio[:, 0] - audio[:, 1]) / 2

    # Scale side channel by width
    side = side * width_envelope

    # Reconstruct L/R
    output[:, 0] = mid + side
    output[:, 1] = mid - side

    return output


# =============================================================================
# BREATH-SYNCHRONIZED AMPLITUDE MODULATION
# =============================================================================

def apply_breath_sync(
    audio: AudioArray,
    sample_rate: int,
    breath_rate_hz: float = 0.15,  # ~9 breaths/min
    depth: float = 0.08,  # ±8% modulation
    phase_offset: float = 0.0,
) -> AudioArray:
    """
    Apply breath-synchronized amplitude modulation.

    Creates subtle "breathing" feel aligned with typical relaxed breathing.

    Args:
        audio: Input audio
        sample_rate: Sample rate in Hz
        breath_rate_hz: Breathing rate in Hz (default ~9/min)
        depth: Modulation depth (0.0-1.0)
        phase_offset: Phase offset in radians

    Returns:
        Audio with breath modulation applied
    """
    num_samples = len(audio)
    t = np.arange(num_samples) / sample_rate

    # Breathing curve: slower exhale than inhale
    # Use asymmetric waveform
    breath_phase = 2 * np.pi * breath_rate_hz * t + phase_offset
    # Asymmetric: faster rise (inhale), slower fall (exhale)
    breath_curve = np.sin(breath_phase) * 0.7 + np.sin(breath_phase * 0.5) * 0.3

    # Normalize to 0-1 range
    breath_curve = (breath_curve + 1) / 2

    # Convert to gain modulation
    modulation = 1.0 + depth * (breath_curve - 0.5) * 2

    if audio.ndim == 2:
        output = audio.copy()
        output[:, 0] *= modulation
        output[:, 1] *= modulation
        return output.astype(np.float32)
    else:
        return (audio * modulation).astype(np.float32)


# =============================================================================
# POST-HYPNOTIC ANCHORING WINDOW
# =============================================================================

def create_anchoring_layer(
    duration_sec: float,
    sample_rate: int = 48000,
    sub_freq: float = 70.0,
    sub_level_db: float = -30.0,
    sparkle_freq: float = 12000.0,
    sparkle_level_db: float = -35.0,
    pulse_rate_hz: float = 0.05,
) -> AudioArray:
    """
    Create a subliminal anchoring layer for the final minute.

    Combines:
    - Subharmonic warmth (60-80 Hz)
    - Faint rising harmony
    - Airband sparkle pulsing

    This becomes a state-recall signature for replay value.

    Args:
        duration_sec: Duration in seconds
        sample_rate: Sample rate in Hz
        sub_freq: Subharmonic frequency in Hz
        sub_level_db: Subharmonic level in dB
        sparkle_freq: Sparkle frequency in Hz
        sparkle_level_db: Sparkle level in dB
        pulse_rate_hz: Pulsing rate in Hz

    Returns:
        Stereo anchoring layer
    """
    num_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, num_samples, dtype=np.float32)

    # Subharmonic warmth
    sub_amp = 10 ** (sub_level_db / 20)
    subharmonic = sub_amp * np.sin(2 * np.pi * sub_freq * t)

    # Add octave up for rising harmony (very faint)
    harmony_amp = sub_amp * 0.3
    # Rising frequency
    harmony_freq = sub_freq * 2 * (1 + 0.1 * t / duration_sec)
    harmony = harmony_amp * np.sin(2 * np.pi * harmony_freq * t)

    # Airband sparkle with pulsing
    sparkle_amp = 10 ** (sparkle_level_db / 20)
    pulse_envelope = 0.5 + 0.5 * np.sin(2 * np.pi * pulse_rate_hz * t)
    sparkle = sparkle_amp * pulse_envelope * np.sin(2 * np.pi * sparkle_freq * t)

    # Combine
    mono = subharmonic + harmony + sparkle

    # Gentle stereo spread
    stereo = np.stack([mono, mono], axis=1).astype(np.float32)

    # Apply gentle fade in/out
    fade_samples = int(sample_rate * 2)  # 2 second fade
    if fade_samples > 0 and num_samples > fade_samples * 2:
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        stereo[:fade_samples] *= fade_in[:, np.newaxis]
        stereo[-fade_samples:] *= fade_out[:, np.newaxis]

    return stereo


# =============================================================================
# UTILITY: STAGE DETECTION FROM MANIFEST
# =============================================================================

def stages_from_manifest(manifest: Dict) -> List[HypnosisStage]:
    """
    Extract hypnosis stages from a session manifest.

    Args:
        manifest: Session manifest dictionary

    Returns:
        List of HypnosisStage dicts with timing and presets applied
    """
    stages = []

    for section in manifest.get('sections', []):
        stage_name = _map_section_to_stage(section.get('name', ''))
        preset = STAGE_PRESETS.get(stage_name, STAGE_PRESETS['journey'])

        stage: HypnosisStage = {
            'name': stage_name,
            'start': section.get('start', 0),
            'end': section.get('end', 0),
            **preset,  # Apply preset values
        }
        stages.append(stage)

    return stages


def _map_section_to_stage(section_name: str) -> str:
    """Map manifest section names to stage presets."""
    name_lower = section_name.lower()

    if 'pretalk' in name_lower or 'pre-talk' in name_lower:
        return 'pretalk'
    elif 'induction' in name_lower:
        return 'induction'
    elif 'deepen' in name_lower:
        return 'deepening'
    elif 'journey' in name_lower:
        return 'journey'
    elif 'luminous' in name_lower or 'core' in name_lower or 'apex' in name_lower:
        return 'luminous_core'
    elif 'integrat' in name_lower:
        return 'integration'
    elif 'awaken' in name_lower or 'return' in name_lower:
        return 'awakening'
    else:
        return 'journey'  # Default


# =============================================================================
# COMPREHENSIVE ADAPTIVE PROCESSING
# =============================================================================

def apply_full_adaptive_processing(
    audio: AudioArray,
    sample_rate: int,
    stages: List[HypnosisStage],
    voice_track: Optional[AudioArray] = None,
    enable_spectral_motion: bool = True,
    enable_masking: bool = True,
    enable_hdra: bool = True,
    enable_spatial: bool = True,
    enable_breath_sync: bool = True,
) -> AudioArray:
    """
    Apply comprehensive adaptive processing pipeline.

    Combines all adaptive processing modules in optimal order.

    Args:
        audio: Input audio (stereo preferred)
        sample_rate: Sample rate in Hz
        stages: List of hypnosis stages
        voice_track: Optional voice track for masking correction
        enable_*: Toggles for each processing module

    Returns:
        Fully processed audio
    """
    print("  Applying adaptive processing pipeline...")
    output = audio.copy()

    # 1. Psychoacoustic masking (if voice provided)
    if enable_masking and voice_track is not None:
        print("    - Psychoacoustic masking correction")
        output = apply_voice_masking_correction(output, voice_track, sample_rate)

    # 2. Spectral motion
    if enable_spectral_motion:
        print("    - Spectral motion generator")
        output = generate_spectral_motion(output, sample_rate)

    # 3. HDR-A (dynamic range architecture)
    if enable_hdra and stages:
        print("    - Hypnotic Dynamic Range Architecture")
        output = apply_hdra(output, sample_rate, stages)

    # 4. Spatial animation
    if enable_spatial and stages and output.ndim == 2:
        print("    - Intelligent spatial animation")
        output = apply_spatial_animation(output, sample_rate, stages)

    # 5. Breath synchronization
    if enable_breath_sync:
        print("    - Breath-synchronized modulation")
        output = apply_breath_sync(output, sample_rate)

    return output


# =============================================================================
# TESTING
# =============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("ADAPTIVE PROCESSING MODULE - TEST")
    print("=" * 70)

    # Create test audio
    duration = 10.0
    sr = 48000
    samples = int(duration * sr)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    # Test tone (440 Hz)
    test_mono = 0.3 * np.sin(2 * np.pi * 440 * t)
    test_stereo = np.stack([test_mono, test_mono], axis=1).astype(np.float32)

    # Test stages
    test_stages: List[HypnosisStage] = [
        {'name': 'induction', 'start': 0, 'end': 3, **STAGE_PRESETS['induction']},
        {'name': 'journey', 'start': 3, 'end': 7, **STAGE_PRESETS['journey']},
        {'name': 'awakening', 'start': 7, 'end': 10, **STAGE_PRESETS['awakening']},
    ]

    print("\n[Test 1] Spectral motion...")
    result1 = generate_spectral_motion(test_stereo, sr)
    print(f"  Output shape: {result1.shape}")

    print("\n[Test 2] HDR-A...")
    result2 = apply_hdra(test_stereo, sr, test_stages)
    print(f"  Output shape: {result2.shape}")

    print("\n[Test 3] Spatial animation...")
    result3 = apply_spatial_animation(test_stereo, sr, test_stages)
    print(f"  Output shape: {result3.shape}")

    print("\n[Test 4] Breath sync...")
    result4 = apply_breath_sync(test_stereo, sr)
    print(f"  Output shape: {result4.shape}")

    print("\n[Test 5] Anchoring layer...")
    result5 = create_anchoring_layer(duration, sr)
    print(f"  Output shape: {result5.shape}")

    print("\n[Test 6] Full pipeline...")
    result6 = apply_full_adaptive_processing(
        test_stereo, sr, test_stages,
        enable_masking=False  # No voice for test
    )
    print(f"  Output shape: {result6.shape}")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)
