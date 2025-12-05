#!/usr/bin/env python3
"""
Luminous SFX Generator - Ethereal Sound Effects for Light-Being Sessions

Generates specialized sound effects for luminous/light-being themed hypnotic sessions:
- Crystal shimmer: Bright, sparkling high frequencies (2-6 kHz)
- Ascending pad: Rising ethereal tones with harmonics
- Halo reverb: Sustained angelic resonance (6s+ decay)
- Choir texture: Very subtle vocal harmonics (-30 dB)

These effects are designed to evoke feelings of transcendence, transformation,
and connection to higher consciousness.

Usage:
    from scripts.core.audio.luminous_sfx import (
        generate_crystal_shimmer,
        generate_ascending_pad,
        generate_halo_reverb,
        generate_choir_texture,
    )

    # Generate a 5-second crystal shimmer
    shimmer = generate_crystal_shimmer(duration=5.0, sample_rate=48000)
"""

import numpy as np
from numpy.typing import NDArray
from scipy import signal
from scipy.io import wavfile
from pathlib import Path
from typing import Optional, List, Dict, Any

# Type alias for stereo audio
StereoAudio = NDArray[np.float32]


# =============================================================================
# CRYSTAL SHIMMER GENERATOR
# =============================================================================

def generate_crystal_shimmer(
    duration: float,
    sample_rate: int = 48000,
    base_freq: float = 3000,
    shimmer_rate: float = 8.0,
    amplitude: float = 0.3,
    stereo_spread: float = 0.3,
) -> StereoAudio:
    """
    Generate bright, sparkling crystal shimmer effect.

    Creates a shimmering high-frequency texture that evokes crystal resonance,
    light refraction, and ethereal sparkle. Ideal for moments of transformation
    or enlightenment in hypnotic sessions.

    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz (default: 48000)
        base_freq: Base frequency in Hz (default: 3000, range 2000-6000)
        shimmer_rate: Rate of shimmer modulation in Hz (default: 8.0)
        amplitude: Output amplitude 0.0-1.0 (default: 0.3)
        stereo_spread: Stereo width 0.0-1.0 (default: 0.3)

    Returns:
        Stereo audio array (samples, 2)
    """
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    # Generate multiple shimmer partials at different frequencies
    rng = np.random.default_rng(42)
    partial_freqs = [base_freq * (1 + 0.1 * i) for i in range(5)]
    partial_amps = [1.0, 0.7, 0.5, 0.3, 0.2]

    shimmer_left = np.zeros(samples, dtype=np.float32)
    shimmer_right = np.zeros(samples, dtype=np.float32)

    for freq, amp in zip(partial_freqs, partial_amps):
        # Add slight random detuning for organic feel
        detune = rng.uniform(-10, 10)
        freq_left = freq + detune
        freq_right = freq - detune

        # Shimmer modulation with different phases for L/R
        mod_left = 0.5 + 0.5 * np.sin(2 * np.pi * shimmer_rate * t)
        mod_right = 0.5 + 0.5 * np.sin(2 * np.pi * shimmer_rate * t + np.pi / 3)

        shimmer_left += amp * mod_left * np.sin(2 * np.pi * freq_left * t)
        shimmer_right += amp * mod_right * np.sin(2 * np.pi * freq_right * t)

    # Normalize and apply amplitude
    max_val = max(np.max(np.abs(shimmer_left)), np.max(np.abs(shimmer_right)))
    if max_val > 0:
        shimmer_left = (shimmer_left / max_val) * amplitude
        shimmer_right = (shimmer_right / max_val) * amplitude

    # Apply stereo spread
    mid = (shimmer_left + shimmer_right) / 2
    side = (shimmer_left - shimmer_right) / 2
    shimmer_left = mid + side * stereo_spread
    shimmer_right = mid - side * stereo_spread

    # Apply gentle envelope (fade in/out)
    fade_samples = int(0.1 * sample_rate)
    fade_in = np.linspace(0, 1, fade_samples, dtype=np.float32)
    fade_out = np.linspace(1, 0, fade_samples, dtype=np.float32)
    shimmer_left[:fade_samples] *= fade_in
    shimmer_left[-fade_samples:] *= fade_out
    shimmer_right[:fade_samples] *= fade_in
    shimmer_right[-fade_samples:] *= fade_out

    return np.stack([shimmer_left, shimmer_right], axis=1).astype(np.float32)


# =============================================================================
# ASCENDING PAD GENERATOR
# =============================================================================

def generate_ascending_pad(
    duration: float,
    sample_rate: int = 48000,
    start_freq: float = 220,
    end_freq: float = 440,
    amplitude: float = 0.25,
    harmonics: int = 6,
) -> StereoAudio:
    """
    Generate rising ethereal pad with harmonics.

    Creates a slowly ascending pad sound with rich harmonics, evoking a sense
    of spiritual ascent, rising consciousness, or transformation into light.

    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        start_freq: Starting frequency in Hz (default: 220, A3)
        end_freq: Ending frequency in Hz (default: 440, A4)
        amplitude: Output amplitude 0.0-1.0 (default: 0.25)
        harmonics: Number of harmonics to include (default: 6)

    Returns:
        Stereo audio array (samples, 2)
    """
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, dtype=np.float32)
    progress = np.linspace(0, 1, samples, dtype=np.float32)

    # Logarithmic frequency sweep
    freq = start_freq * ((end_freq / start_freq) ** progress)

    # Generate harmonics with decreasing amplitude
    pad = np.zeros(samples, dtype=np.float32)
    harmonic_weights = [1.0 / (i + 1) for i in range(harmonics)]

    for i, weight in enumerate(harmonic_weights):
        harmonic_freq = freq * (i + 1)
        # Slight detuning for richness
        detune = 1.0 + 0.002 * np.sin(2 * np.pi * 0.1 * t)
        pad += weight * np.sin(2 * np.pi * harmonic_freq * detune * t)

    # Normalize
    pad = pad / np.max(np.abs(pad)) * amplitude

    # Add subtle chorus effect via stereo offset
    chorus_samples = int(0.015 * sample_rate)  # 15ms offset
    left = pad
    right = np.roll(pad, chorus_samples)
    right[:chorus_samples] = 0

    # Apply ADSR envelope
    attack = int(0.3 * sample_rate)
    decay = int(0.2 * sample_rate)
    release = int(0.5 * sample_rate)
    sustain_level = 0.7

    envelope = np.ones(samples, dtype=np.float32)
    # Attack
    envelope[:attack] = np.linspace(0, 1, attack)
    # Decay
    envelope[attack:attack + decay] = np.linspace(1, sustain_level, decay)
    # Sustain (already 1.0)
    envelope[attack + decay:-release] = sustain_level
    # Release
    envelope[-release:] = np.linspace(sustain_level, 0, release)

    left *= envelope
    right *= envelope

    return np.stack([left, right], axis=1).astype(np.float32)


# =============================================================================
# HALO REVERB GENERATOR
# =============================================================================

def generate_halo_reverb(
    duration: float,
    sample_rate: int = 48000,
    center_freq: float = 528,
    reverb_time: float = 6.0,
    amplitude: float = 0.2,
    brightness: float = 0.5,
) -> StereoAudio:
    """
    Generate sustained angelic resonance with long decay.

    Creates a sustained, ethereal tone with very long reverb tail, evoking
    the sound of angelic presence, divine light, or sacred space.
    The 528 Hz default is associated with transformation and DNA repair.

    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        center_freq: Center frequency in Hz (default: 528, "miracle tone")
        reverb_time: Reverb decay time in seconds (default: 6.0)
        amplitude: Output amplitude 0.0-1.0 (default: 0.2)
        brightness: High frequency content 0.0-1.0 (default: 0.5)

    Returns:
        Stereo audio array (samples, 2)
    """
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    # Generate base tone with gentle harmonics
    tone = np.sin(2 * np.pi * center_freq * t)
    tone += 0.3 * np.sin(2 * np.pi * center_freq * 2 * t) * brightness
    tone += 0.15 * np.sin(2 * np.pi * center_freq * 3 * t) * brightness

    # Create long reverb tail via convolution with IR
    reverb_samples = int(reverb_time * sample_rate)
    t_ir = np.linspace(0, reverb_time, reverb_samples, dtype=np.float32)

    # Exponential decay with modulated diffusion
    rng = np.random.default_rng(123)
    ir = np.exp(-t_ir * (3 / reverb_time)) * rng.standard_normal(reverb_samples)

    # Add shimmer to IR
    shimmer = 1 + 0.1 * np.sin(2 * np.pi * 0.5 * t_ir)
    ir *= shimmer * 0.1

    # Convolve to create reverb
    reverbed = signal.fftconvolve(tone, ir, mode='full')[:samples]

    # Normalize
    reverbed = reverbed / np.max(np.abs(reverbed)) * amplitude

    # Create stereo with subtle phase difference
    left = reverbed
    right = np.roll(reverbed, int(0.002 * sample_rate))  # 2ms offset

    # Apply gentle fade envelope
    fade = int(0.5 * sample_rate)
    fade_in = np.linspace(0, 1, fade, dtype=np.float32)
    fade_out = np.linspace(1, 0, fade, dtype=np.float32)

    left[:fade] *= fade_in
    left[-fade:] *= fade_out
    right[:fade] *= fade_in
    right[-fade:] *= fade_out

    return np.stack([left, right], axis=1).astype(np.float32)


# =============================================================================
# CHOIR TEXTURE GENERATOR
# =============================================================================

def generate_choir_texture(
    duration: float,
    sample_rate: int = 48000,
    base_freq: float = 261.63,
    amplitude: float = 0.15,
    voices: int = 8,
) -> StereoAudio:
    """
    Generate very subtle vocal harmonic texture.

    Creates a choir-like pad using filtered noise and harmonics to simulate
    distant angelic voices. Extremely subtle (-30 dB typical in mix),
    designed to be felt more than heard.

    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        base_freq: Base frequency in Hz (default: 261.63, C4)
        amplitude: Output amplitude 0.0-1.0 (default: 0.15, very quiet)
        voices: Number of simulated voices (default: 8)

    Returns:
        Stereo audio array (samples, 2)
    """
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, dtype=np.float32)
    nyq = sample_rate / 2

    rng = np.random.default_rng(456)
    choir = np.zeros(samples, dtype=np.float32)

    # Generate multiple "voices" at different pitches
    voice_intervals = [0, 3, 5, 7, 12, 15, 19, 24]  # Musical intervals in semitones

    for i in range(min(voices, len(voice_intervals))):
        interval = voice_intervals[i]
        freq = base_freq * (2 ** (interval / 12))

        # Each voice is a bandpass-filtered noise + sine blend
        # Generate narrow bandpass around the frequency
        bandwidth = 50  # Hz
        low = max(freq - bandwidth / 2, 20) / nyq
        high = min(freq + bandwidth / 2, nyq - 100) / nyq

        if low < high < 1:
            b, a = signal.butter(2, [low, high], btype='band')
            noise = rng.standard_normal(samples)
            voice_noise = signal.filtfilt(b, a, noise) * 0.3

            # Add pure tone
            voice_tone = np.sin(2 * np.pi * freq * t)

            # Slow amplitude modulation for breath-like quality
            breath = 0.7 + 0.3 * np.sin(2 * np.pi * (0.1 + 0.02 * i) * t)

            voice = (voice_noise + voice_tone) * breath
            choir += voice / voices

    # Normalize
    if np.max(np.abs(choir)) > 0:
        choir = choir / np.max(np.abs(choir)) * amplitude

    # Add reverb-like diffusion
    diffusion_samples = int(0.5 * sample_rate)
    t_diff = np.linspace(0, 0.5, diffusion_samples, dtype=np.float32)
    diffusion_ir = np.exp(-t_diff * 6) * rng.standard_normal(diffusion_samples) * 0.1
    choir = signal.fftconvolve(choir, diffusion_ir, mode='same')

    # Stereo spread
    left = choir
    right = np.roll(choir, int(0.01 * sample_rate))

    # Apply envelope
    fade = int(0.3 * sample_rate)
    envelope = np.ones(samples, dtype=np.float32)
    envelope[:fade] = np.linspace(0, 1, fade)
    envelope[-fade:] = np.linspace(1, 0, fade)

    left *= envelope
    right *= envelope

    return np.stack([left, right], axis=1).astype(np.float32)


# =============================================================================
# GOLDEN BELL CHIME (NEW - Ceremonial Transition Marker)
# =============================================================================

def generate_golden_bell(
    duration: float = 4.0,
    sample_rate: int = 48000,
    base_freq: float = 432.0,
    amplitude: float = 0.35,
    decay_time: float = 3.5,
) -> StereoAudio:
    """
    Generate a resonant golden bell chime for ceremonial moments.

    Creates a rich bell strike with complex harmonics and long sustain,
    ideal for marking transitions, initiations, or awakening moments.
    Uses 432 Hz by default for "natural" harmonic resonance.

    Args:
        duration: Duration in seconds (default: 4.0)
        sample_rate: Sample rate in Hz
        base_freq: Fundamental frequency in Hz (default: 432)
        amplitude: Output amplitude 0.0-1.0 (default: 0.35)
        decay_time: Exponential decay time in seconds (default: 3.5)

    Returns:
        Stereo audio array (samples, 2)
    """
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    # Bell partials (based on real bell acoustics)
    # Partials are non-harmonic for authentic bell sound
    partial_ratios = [1.0, 2.0, 2.4, 3.0, 4.2, 5.4, 6.8, 8.0]
    partial_amps = [1.0, 0.6, 0.4, 0.3, 0.2, 0.15, 0.1, 0.05]
    partial_decays = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3]

    bell = np.zeros(samples, dtype=np.float32)

    for ratio, amp, decay_mult in zip(partial_ratios, partial_amps, partial_decays):
        freq = base_freq * ratio
        # Each partial has slightly different decay
        partial_decay = decay_time * decay_mult
        envelope = np.exp(-t / partial_decay)
        # Add slight inharmonicity for realism
        inharmonicity = 1.0 + 0.001 * ratio * ratio
        bell += amp * envelope * np.sin(2 * np.pi * freq * inharmonicity * t)

    # Normalize
    bell = bell / np.max(np.abs(bell)) * amplitude

    # Attack transient (strike impulse)
    attack_samples = int(0.002 * sample_rate)  # 2ms
    attack = np.exp(-np.linspace(0, 5, attack_samples))
    bell[:attack_samples] *= attack

    # Create stereo with decorrelated reverb tails
    rng = np.random.default_rng(789)
    reverb_ir = np.exp(-np.linspace(0, 4, int(0.3 * sample_rate))) * rng.standard_normal(int(0.3 * sample_rate)) * 0.05
    left = signal.fftconvolve(bell, reverb_ir, mode='same')
    right = signal.fftconvolve(bell, np.roll(reverb_ir, 100), mode='same')

    return np.stack([left, right], axis=1).astype(np.float32)


# =============================================================================
# SACRED DRONE (NEW - Deep Foundation Layer)
# =============================================================================

def generate_sacred_drone(
    duration: float,
    sample_rate: int = 48000,
    base_freq: float = 60.0,
    amplitude: float = 0.2,
    warmth: float = 0.5,
    movement_rate: float = 0.03,
) -> StereoAudio:
    """
    Generate a deep, grounding sacred drone.

    Creates a rich, warm low-frequency foundation with subtle organic
    movement. Evokes ancient temples, deep earth, and primordial power.
    Perfect for grounding sections or underscoring powerful moments.

    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        base_freq: Base frequency in Hz (default: 60, deep bass)
        amplitude: Output amplitude 0.0-1.0 (default: 0.2)
        warmth: Amount of harmonic richness 0.0-1.0 (default: 0.5)
        movement_rate: Rate of subtle pitch/amplitude modulation Hz

    Returns:
        Stereo audio array (samples, 2)
    """
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, dtype=np.float32)

    # Base drone with subtle movement
    pitch_mod = 1 + 0.002 * np.sin(2 * np.pi * movement_rate * t)
    amp_mod = 1 + 0.1 * np.sin(2 * np.pi * movement_rate * 1.618 * t)  # Golden ratio offset

    # Fundamental
    drone = np.sin(2 * np.pi * base_freq * pitch_mod * t)

    # Add harmonics for warmth
    if warmth > 0:
        drone += warmth * 0.5 * np.sin(2 * np.pi * base_freq * 2 * pitch_mod * t)
        drone += warmth * 0.3 * np.sin(2 * np.pi * base_freq * 3 * pitch_mod * t)
        drone += warmth * 0.15 * np.sin(2 * np.pi * base_freq * 4 * pitch_mod * t)

    # Add sub-octave for depth
    drone += 0.4 * np.sin(2 * np.pi * base_freq * 0.5 * pitch_mod * t)

    # Apply amplitude modulation
    drone *= amp_mod

    # Normalize
    drone = drone / np.max(np.abs(drone)) * amplitude

    # Stereo with subtle width
    left = drone
    right = np.roll(drone, int(0.005 * sample_rate))  # 5ms offset

    # Apply envelope
    fade = int(1.0 * sample_rate)
    envelope = np.ones(samples, dtype=np.float32)
    envelope[:fade] = np.linspace(0, 1, fade) ** 2  # Quadratic fade in
    envelope[-fade:] = np.linspace(1, 0, fade) ** 2

    left *= envelope
    right *= envelope

    return np.stack([left, right], axis=1).astype(np.float32)


# =============================================================================
# STARFIELD SPARKLE (NEW - Cosmic Particle Effects)
# =============================================================================

def generate_starfield_sparkle(
    duration: float,
    sample_rate: int = 48000,
    density: float = 0.5,
    amplitude: float = 0.15,
    freq_range: tuple = (4000, 12000),
) -> StereoAudio:
    """
    Generate random cosmic particle/sparkle effects.

    Creates sporadic high-frequency sparkle events that evoke
    stars twinkling, cosmic particles, or light refracting through
    crystal. Events are randomly distributed in stereo field.

    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        density: Event density 0.0-1.0 (higher = more sparkles)
        amplitude: Output amplitude 0.0-1.0 (default: 0.15)
        freq_range: Frequency range for sparkle events (Hz)

    Returns:
        Stereo audio array (samples, 2)
    """
    samples = int(duration * sample_rate)
    left = np.zeros(samples, dtype=np.float32)
    right = np.zeros(samples, dtype=np.float32)

    rng = np.random.default_rng(321)

    # Calculate number of sparkle events based on density
    num_events = int(duration * density * 5)  # ~5 events/sec at density=1

    for _ in range(num_events):
        # Random position
        pos = rng.integers(0, samples)

        # Random frequency
        freq = rng.uniform(freq_range[0], freq_range[1])

        # Random duration (very short)
        event_duration = rng.uniform(0.02, 0.08)  # 20-80ms
        event_samples = int(event_duration * sample_rate)

        if pos + event_samples > samples:
            continue

        # Generate sparkle
        t_event = np.linspace(0, event_duration, event_samples, dtype=np.float32)
        sparkle = np.sin(2 * np.pi * freq * t_event)

        # Envelope: fast attack, exponential decay
        envelope = np.exp(-t_event / (event_duration * 0.3))

        sparkle *= envelope * amplitude * rng.uniform(0.3, 1.0)

        # Random stereo position
        pan = rng.uniform(0, 1)
        left[pos:pos + event_samples] += sparkle * (1 - pan)
        right[pos:pos + event_samples] += sparkle * pan

    # Prevent clipping
    peak = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if peak > 0.95:
        left *= 0.95 / peak
        right *= 0.95 / peak

    return np.stack([left, right], axis=1).astype(np.float32)


# =============================================================================
# OCEANIC WHISPER (NEW - Deep Water/Breath Effects)
# =============================================================================

def generate_oceanic_whisper(
    duration: float,
    sample_rate: int = 48000,
    wave_rate: float = 0.08,
    amplitude: float = 0.2,
    depth: float = 0.5,
) -> StereoAudio:
    """
    Generate oceanic breath/wave texture.

    Creates rhythmic filtered noise that simulates ocean waves or
    deep cosmic breathing. Perfect for induction sections or
    oceanic journey themes.

    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        wave_rate: Rate of wave cycles in Hz (default: 0.08 = ~1 every 12s)
        amplitude: Output amplitude 0.0-1.0 (default: 0.2)
        depth: Depth of modulation 0.0-1.0 (default: 0.5)

    Returns:
        Stereo audio array (samples, 2)
    """
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, dtype=np.float32)
    nyq = sample_rate / 2

    rng = np.random.default_rng(654)

    # Generate base noise
    noise = rng.standard_normal(samples).astype(np.float32)

    # Create wave envelope (asymmetric like ocean waves)
    # Slow rise, faster fall
    wave_phase = 2 * np.pi * wave_rate * t
    wave_envelope = 0.5 + 0.5 * np.sin(wave_phase - np.pi / 4)
    wave_envelope = wave_envelope ** 1.5  # Asymmetric shaping

    # Modulate filter cutoff with wave
    base_cutoff = 400  # Hz
    cutoff_range = 600  # Hz

    # Process in chunks with varying filter
    chunk_size = sample_rate // 20  # 50ms chunks
    output = np.zeros(samples, dtype=np.float32)

    for i in range(0, samples, chunk_size):
        end_idx = min(i + chunk_size, samples)
        chunk = noise[i:end_idx]

        # Get average envelope for this chunk
        avg_env = np.mean(wave_envelope[i:end_idx])

        # Calculate cutoff frequency
        cutoff = base_cutoff + cutoff_range * avg_env * depth
        w0 = min(cutoff / nyq, 0.99)

        # Apply lowpass filter
        b, a = signal.butter(2, w0, btype='low')
        filtered = signal.lfilter(b, a, chunk)

        # Apply envelope
        output[i:end_idx] = filtered * wave_envelope[i:end_idx]

    # Normalize
    output = output / np.max(np.abs(output)) * amplitude

    # Stereo with wave-like panning
    pan = 0.5 + 0.3 * np.sin(wave_phase * 0.5)  # Slow stereo movement
    left = output * (1 - pan)
    right = output * pan

    # Apply overall envelope
    fade = int(1.0 * sample_rate)
    envelope = np.ones(samples, dtype=np.float32)
    envelope[:fade] = np.linspace(0, 1, fade)
    envelope[-fade:] = np.linspace(1, 0, fade)

    left *= envelope
    right *= envelope

    return np.stack([left, right], axis=1).astype(np.float32)


# =============================================================================
# COMPOSITE GENERATOR
# =============================================================================

def generate_luminous_sfx_track(
    duration: float,
    sample_rate: int = 48000,
    events: Optional[List[Dict[str, Any]]] = None,
) -> StereoAudio:
    """
    Generate a complete luminous SFX track with timed events.

    Combines multiple luminous SFX elements at specified timestamps
    to create a cohesive ethereal soundscape.

    Args:
        duration: Total duration in seconds
        sample_rate: Sample rate in Hz
        events: List of event dicts with:
            - type: 'shimmer', 'ascending', 'halo', or 'choir'
            - time: Start time in seconds
            - duration: Event duration in seconds
            - amplitude: Event amplitude (optional)
            - Additional type-specific parameters

    Returns:
        Stereo audio array (samples, 2)

    Example:
        events = [
            {'type': 'shimmer', 'time': 0, 'duration': 5, 'amplitude': 0.2},
            {'type': 'halo', 'time': 10, 'duration': 8, 'center_freq': 432},
            {'type': 'ascending', 'time': 20, 'duration': 10},
        ]
        track = generate_luminous_sfx_track(60, events=events)
    """
    total_samples = int(duration * sample_rate)
    track: StereoAudio = np.zeros((total_samples, 2), dtype=np.float32)

    if not events:
        return track

    generators = {
        'shimmer': generate_crystal_shimmer,
        'ascending': generate_ascending_pad,
        'halo': generate_halo_reverb,
        'choir': generate_choir_texture,
        'bell': generate_golden_bell,
        'drone': generate_sacred_drone,
        'sparkle': generate_starfield_sparkle,
        'oceanic': generate_oceanic_whisper,
    }

    for event in events:
        event_type = event.get('type', 'shimmer')
        event_time = event.get('time', 0)
        event_duration = event.get('duration', 3.0)

        if event_type not in generators:
            print(f"  Warning: Unknown SFX type '{event_type}', skipping")
            continue

        # Build kwargs for generator
        kwargs = {
            'duration': event_duration,
            'sample_rate': sample_rate,
        }

        # Add optional parameters
        for key in ['amplitude', 'base_freq', 'start_freq', 'end_freq',
                    'center_freq', 'reverb_time', 'brightness', 'voices',
                    'decay_time', 'warmth', 'movement_rate', 'density',
                    'freq_range', 'wave_rate', 'depth']:
            if key in event:
                kwargs[key] = event[key]

        # Generate the effect
        effect = generators[event_type](**kwargs)

        # Place in track at specified time
        start_sample = int(event_time * sample_rate)
        end_sample = min(start_sample + len(effect), total_samples)
        effect_length = end_sample - start_sample

        if effect_length > 0:
            track[start_sample:end_sample] += effect[:effect_length]

    # Prevent clipping
    peak = np.max(np.abs(track))
    if peak > 0.95:
        track = track * (0.95 / peak)

    return track


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def save_sfx(audio: StereoAudio, path: Path, sample_rate: int = 48000) -> None:
    """Save SFX audio to WAV file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to 16-bit
    audio_int = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    wavfile.write(str(path), sample_rate, audio_int)

    file_size = path.stat().st_size / 1024
    print(f"✓ Saved SFX: {path} ({file_size:.1f} KB)")


# =============================================================================
# EXAMPLE USAGE AND TESTING
# =============================================================================

if __name__ == '__main__':
    import sys

    print("=" * 70)
    print("LUMINOUS SFX GENERATOR - TEST")
    print("=" * 70)

    # Test 1: Crystal shimmer
    print("\n[Test 1] Generating crystal shimmer (5 seconds)...")
    shimmer = generate_crystal_shimmer(duration=5.0, amplitude=0.3)
    save_sfx(shimmer, Path("test_sfx_shimmer.wav"))

    # Test 2: Ascending pad
    print("\n[Test 2] Generating ascending pad (8 seconds)...")
    ascending = generate_ascending_pad(duration=8.0, start_freq=220, end_freq=880)
    save_sfx(ascending, Path("test_sfx_ascending.wav"))

    # Test 3: Halo reverb
    print("\n[Test 3] Generating halo reverb (10 seconds)...")
    halo = generate_halo_reverb(duration=10.0, center_freq=528, reverb_time=6.0)
    save_sfx(halo, Path("test_sfx_halo.wav"))

    # Test 4: Choir texture
    print("\n[Test 4] Generating choir texture (6 seconds)...")
    choir = generate_choir_texture(duration=6.0, voices=8)
    save_sfx(choir, Path("test_sfx_choir.wav"))

    # Test 5: Composite track
    print("\n[Test 5] Generating composite track (30 seconds)...")
    events = [
        {'type': 'shimmer', 'time': 0, 'duration': 5, 'amplitude': 0.2},
        {'type': 'ascending', 'time': 5, 'duration': 8, 'amplitude': 0.25},
        {'type': 'halo', 'time': 12, 'duration': 10, 'center_freq': 432, 'amplitude': 0.2},
        {'type': 'choir', 'time': 20, 'duration': 10, 'amplitude': 0.15},
    ]
    composite = generate_luminous_sfx_track(30.0, events=events)
    save_sfx(composite, Path("test_sfx_composite.wav"))

    print("\n" + "=" * 70)
    print("✓ ALL TESTS COMPLETE")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - test_sfx_shimmer.wav    (crystal shimmer)")
    print("  - test_sfx_ascending.wav  (ascending pad)")
    print("  - test_sfx_halo.wav       (halo reverb)")
    print("  - test_sfx_choir.wav      (choir texture)")
    print("  - test_sfx_composite.wav  (composite track)")

    sys.exit(0)
