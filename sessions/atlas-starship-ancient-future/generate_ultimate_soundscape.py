#!/usr/bin/env python3
"""
ATLAS STARSHIP ANCIENT FUTURE - Ultimate Consciousness-Altering Soundscape Generator

Generates all 7 consciousness-altering sound layers as separate stems:
1. Theta Gateway (6.0 Hz binaural) - Star reactor hum
2. Delta Drift (2.5-3 Hz) - Distant warp engine pulsations
3. Xenolinguistic Tones - Ancient alien language shifting tones
4. Harmonic Light-Chord Drone (111 Hz) - Angelic metallic ring
5. Sub-Bass Oscillation (0.9-1.2 Hz) - Starship hull vibration
6. Hyperspace Wind Textures - Interstellar membrane swirls
7. Ship-Memory Echoes - Living vessel recalling ancient knowledge

Each layer is saved as a separate WAV file for later mixing.
"""

import numpy as np
from scipy.io import wavfile
from scipy import signal
import os
import random

# Constants
SAMPLE_RATE = 48000
DURATION = 1597  # Match voice track duration (1596.912 rounded up)
OUTPUT_DIR = "working_files/stems"

def ensure_output_dir():
    """Create output directory if it doesn't exist"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def apply_envelope(audio, fade_in_sec=5.0, fade_out_sec=8.0):
    """Apply fade in/out envelope to audio"""
    fade_in_samples = int(fade_in_sec * SAMPLE_RATE)
    fade_out_samples = int(fade_out_sec * SAMPLE_RATE)

    if len(audio.shape) == 1:
        # Mono
        if fade_in_samples > 0:
            audio[:fade_in_samples] *= np.linspace(0, 1, fade_in_samples)
        if fade_out_samples > 0:
            audio[-fade_out_samples:] *= np.linspace(1, 0, fade_out_samples)
    else:
        # Stereo
        if fade_in_samples > 0:
            fade_in = np.linspace(0, 1, fade_in_samples)
            audio[:fade_in_samples, 0] *= fade_in
            audio[:fade_in_samples, 1] *= fade_in
        if fade_out_samples > 0:
            fade_out = np.linspace(1, 0, fade_out_samples)
            audio[-fade_out_samples:, 0] *= fade_out
            audio[-fade_out_samples:, 1] *= fade_out

    return audio

def save_stem(audio, filename, description):
    """Save audio stem as WAV file"""
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Ensure stereo
    if len(audio.shape) == 1:
        audio = np.stack([audio, audio], axis=1)

    # Convert to 16-bit PCM
    audio_int = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    wavfile.write(filepath, SAMPLE_RATE, audio_int)

    file_size = os.path.getsize(filepath) / (1024 * 1024)
    duration_min = len(audio) / SAMPLE_RATE / 60
    print(f"  ✓ Saved: {filename} ({file_size:.1f} MB, {duration_min:.1f} min)")
    print(f"    {description}")

# =============================================================================
# LAYER 1: THETA GATEWAY (6.0 Hz Binaural)
# =============================================================================
def generate_theta_gateway():
    """
    Base Layer - Theta Gateway (6.0 Hz)
    Purpose: Induction into visionary state, access to alien symbolic cognition
    Sound: Deep, warm hum like a star reactor idling
    Carrier: 432 Hz (sacred frequency)

    Section timings from manifest:
    - 0-150s: Alpha (10 Hz) for pretalk
    - 150-540s: Theta (6.0 Hz) gateway
    - 540-900s: Steady theta (6.0 Hz) for boarding
    - 900-1200s: Delta drift (2.5 Hz)
    - 1200-1500s: Delta blend (3.0 Hz) with gamma flash at 1200
    - 1500-1680s: Return to theta (6.0 Hz)
    - 1680-1800s: Alpha awakening (10.0 Hz)
    """
    print("\n🌌 Layer 1: Theta Gateway (Binaural)")

    carrier = 432  # Sacred frequency
    amplitude = 0.25

    # Section definitions
    sections = [
        {"start": 0, "end": 150, "beat_hz": 10.0, "name": "Pretalk (alpha)"},
        {"start": 150, "end": 540, "beat_hz": 6.0, "name": "Induction (theta gateway)"},
        {"start": 540, "end": 900, "beat_hz": 6.0, "name": "Boarding (steady theta)"},
        {"start": 900, "end": 1200, "beat_hz": 2.5, "name": "Helm (delta drift)"},
        {"start": 1200, "end": 1500, "beat_hz": 3.0, "name": "Download (delta blend)"},
        {"start": 1500, "end": 1680, "beat_hz": 6.0, "name": "Integration (theta)"},
        {"start": 1680, "end": DURATION, "beat_hz": 10.0, "name": "Awakening (alpha)"},
    ]

    gamma_flash_time = 1200
    gamma_flash_duration = 3
    gamma_freq = 40

    all_audio = []

    for section in sections:
        start = section['start']
        end = min(section['end'], DURATION)
        beat_hz = section['beat_hz']
        name = section['name']

        if start >= DURATION:
            continue

        segment_duration = end - start
        print(f"    {start:4d}-{end:4d}s: {beat_hz:4.1f} Hz - {name}")

        # Check for gamma flash
        if start <= gamma_flash_time < end:
            # Before flash
            before_duration = gamma_flash_time - start
            if before_duration > 0:
                audio = _generate_binaural_segment(carrier, beat_hz, before_duration, amplitude)
                all_audio.append(audio)

            # Gamma flash
            print(f"      ⚡ GAMMA FLASH at {gamma_flash_time}s (40 Hz for {gamma_flash_duration}s)")
            gamma = _generate_gamma_flash(carrier, gamma_freq, gamma_flash_duration, amplitude * 1.3)
            all_audio.append(gamma)

            # After flash
            after_duration = end - (gamma_flash_time + gamma_flash_duration)
            if after_duration > 0:
                audio = _generate_binaural_segment(carrier, beat_hz, after_duration, amplitude)
                all_audio.append(audio)
        else:
            audio = _generate_binaural_segment(carrier, beat_hz, segment_duration, amplitude)
            all_audio.append(audio)

    full_track = np.vstack(all_audio)
    full_track = apply_envelope(full_track, fade_in_sec=3.0, fade_out_sec=5.0)

    return full_track

def _generate_binaural_segment(carrier, beat_hz, duration, amplitude):
    """Generate binaural beat segment"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    left_freq = carrier - (beat_hz / 2)
    right_freq = carrier + (beat_hz / 2)

    # Add subtle harmonics for warmth (star reactor character)
    left = np.sin(2 * np.pi * left_freq * t) * amplitude
    left += np.sin(2 * np.pi * left_freq * 2 * t) * amplitude * 0.1  # 2nd harmonic

    right = np.sin(2 * np.pi * right_freq * t) * amplitude
    right += np.sin(2 * np.pi * right_freq * 2 * t) * amplitude * 0.1

    return np.stack([left, right], axis=1).astype(np.float32)

def _generate_gamma_flash(carrier, gamma_freq, duration, amplitude):
    """Generate intense gamma burst"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    left_freq = carrier - (gamma_freq / 2)
    right_freq = carrier + (gamma_freq / 2)

    left = np.sin(2 * np.pi * left_freq * t)
    right = np.sin(2 * np.pi * right_freq * t)

    # Quick envelope
    envelope = np.ones(len(t))
    fade_in = int(0.2 * SAMPLE_RATE)
    fade_out = int(0.5 * SAMPLE_RATE)
    envelope[:fade_in] = np.linspace(0, 1, fade_in)
    envelope[-fade_out:] = np.linspace(1, 0, fade_out)

    left = left * envelope * amplitude
    right = right * envelope * amplitude

    return np.stack([left, right], axis=1).astype(np.float32)

# =============================================================================
# LAYER 2: DELTA DRIFT (2.5-3 Hz)
# =============================================================================
def generate_delta_drift():
    """
    Transition Layer - Delta Drift (2.5-3 Hz)
    Purpose: Let the mind descend into subconscious symbolic territory
    Sound: Slow pulsations resembling distant warp engines

    Active: 900-1500s (helm and download phases)
    """
    print("\n🌊 Layer 2: Delta Drift")

    total_samples = int(SAMPLE_RATE * DURATION)
    track = np.zeros((total_samples, 2), dtype=np.float32)

    # Active region: 900-1500s
    active_start = 900
    active_end = 1500
    amplitude = 0.15

    # Create warp engine pulsation effect
    start_sample = int(active_start * SAMPLE_RATE)
    end_sample = int(active_end * SAMPLE_RATE)
    duration = active_end - active_start

    t = np.linspace(0, duration, end_sample - start_sample, False)

    # Oscillating frequency between 2.5 and 3.0 Hz
    freq_mod = 2.75 + 0.25 * np.sin(2 * np.pi * 0.02 * t)  # Slow modulation

    # Create pulsation using amplitude modulation
    pulse = np.sin(2 * np.pi * np.cumsum(freq_mod) / SAMPLE_RATE)

    # Deep carrier tone (sub-bass character)
    carrier = 55  # Low A
    carrier_tone = np.sin(2 * np.pi * carrier * t) * 0.5
    carrier_tone += np.sin(2 * np.pi * carrier * 1.5 * t) * 0.2  # 5th harmonic

    # Modulate carrier with pulse
    warp_sound = carrier_tone * (0.5 + 0.5 * pulse) * amplitude

    # Slight stereo offset for width
    track[start_sample:end_sample, 0] = warp_sound
    track[start_sample:end_sample, 1] = np.roll(warp_sound, int(0.01 * SAMPLE_RATE))

    # Smooth fade in/out for active region
    fade_samples = int(10 * SAMPLE_RATE)
    track[start_sample:start_sample + fade_samples] *= np.linspace(0, 1, fade_samples)[:, np.newaxis]
    track[end_sample - fade_samples:end_sample] *= np.linspace(1, 0, fade_samples)[:, np.newaxis]

    print(f"    Active: {active_start}-{active_end}s (warp engine pulsations)")

    return track

# =============================================================================
# LAYER 3: XENOLINGUISTIC TONES
# =============================================================================
def generate_xenolinguistic():
    """
    Xenolinguistic Tones (Randomized Microtonal Scales)
    Purpose: Create the sense of ancient alien language being received
    Sound: Soft, consonant yet "not-quite-human" shifting tones

    Active: 540-1500s (boarding through download)
    """
    print("\n👽 Layer 3: Xenolinguistic Tones")

    total_samples = int(SAMPLE_RATE * DURATION)
    track = np.zeros((total_samples, 2), dtype=np.float32)

    active_start = 540
    active_end = 1500
    amplitude = 0.08

    # Microtonal scale based on 11-limit just intonation (alien harmonics)
    base_freq = 174  # F below middle C
    ratios = [
        1.0,        # Root
        11/10,      # Microtonal 2nd
        9/8,        # Major 2nd
        7/6,        # Septimal minor 3rd
        11/9,       # Undecimal neutral 3rd
        4/3,        # Perfect 4th
        11/8,       # Undecimal tritone
        3/2,        # Perfect 5th
        11/7,       # Undecimal minor 6th
        7/4,        # Harmonic 7th
        11/6,       # Undecimal neutral 7th
    ]

    # Generate slowly shifting tones
    num_voices = 4
    voice_phases = np.zeros(num_voices)

    start_sample = int(active_start * SAMPLE_RATE)
    end_sample = int(active_end * SAMPLE_RATE)

    np.random.seed(42)  # Reproducible randomness

    for i in range(start_sample, end_sample, SAMPLE_RATE // 10):  # Update every 0.1s
        chunk_end = min(i + SAMPLE_RATE // 10, end_sample)
        chunk_len = chunk_end - i
        t = np.linspace(0, chunk_len / SAMPLE_RATE, chunk_len, False)

        chunk = np.zeros((chunk_len, 2))

        for v in range(num_voices):
            # Slowly shift to new notes
            if np.random.random() < 0.02:  # 2% chance to change note
                voice_phases[v] = np.random.randint(0, len(ratios))

            freq = base_freq * ratios[int(voice_phases[v])]

            # Add slight detuning for alien quality
            detune = 1 + (np.random.random() - 0.5) * 0.02
            freq *= detune

            # Generate tone with slow amplitude envelope
            tone = np.sin(2 * np.pi * freq * t) * amplitude / num_voices

            # Slight stereo pan based on voice
            pan = (v / num_voices) * 0.6 - 0.3
            chunk[:, 0] += tone * (0.5 - pan)
            chunk[:, 1] += tone * (0.5 + pan)

        track[i:chunk_end] = chunk

    # Smooth the transitions with lowpass filter
    b, a = signal.butter(2, 50 / (SAMPLE_RATE / 2), btype='low')
    track[:, 0] = signal.filtfilt(b, a, track[:, 0])
    track[:, 1] = signal.filtfilt(b, a, track[:, 1])

    # Fade in/out
    fade_samples = int(15 * SAMPLE_RATE)
    track[start_sample:start_sample + fade_samples] *= np.linspace(0, 1, fade_samples)[:, np.newaxis]
    track[end_sample - fade_samples:end_sample] *= np.linspace(1, 0, fade_samples)[:, np.newaxis]

    print(f"    Active: {active_start}-{active_end}s (microtonal alien language)")

    return track

# =============================================================================
# LAYER 4: HARMONIC LIGHT-CHORD DRONE (111 Hz)
# =============================================================================
def generate_harmonic_drone():
    """
    Harmonic Light-Chord Drone (111 Hz)
    Purpose: Stimulate frontal midline theta; associated with mystical states
    Sound: A glowing, angelic metallic ring

    Active: 540-1500s (journey phases)
    """
    print("\n✨ Layer 4: Harmonic Light-Chord Drone (111 Hz)")

    total_samples = int(SAMPLE_RATE * DURATION)
    track = np.zeros((total_samples, 2), dtype=np.float32)

    active_start = 540
    active_end = 1500
    amplitude = 0.12
    base_freq = 111  # Cell regeneration frequency

    start_sample = int(active_start * SAMPLE_RATE)
    end_sample = int(active_end * SAMPLE_RATE)
    duration = active_end - active_start

    t = np.linspace(0, duration, end_sample - start_sample, False)

    # Build harmonic stack for "angelic metallic ring" character
    harmonics = [
        (1.0, 1.0),     # Fundamental
        (2.0, 0.5),     # Octave
        (3.0, 0.3),     # 12th
        (4.0, 0.2),     # 2 octaves
        (5.0, 0.15),    # Major 3rd + 2 oct
        (6.0, 0.1),     # 5th + 2 oct
        (7.0, 0.08),    # Harmonic 7th
    ]

    drone = np.zeros(len(t))
    for ratio, level in harmonics:
        freq = base_freq * ratio
        drone += np.sin(2 * np.pi * freq * t) * level

    # Normalize and apply amplitude
    drone = drone / np.max(np.abs(drone)) * amplitude

    # Add subtle shimmer (metallic character)
    shimmer_freq = 3.5  # Slow shimmer
    shimmer = 1 + 0.1 * np.sin(2 * np.pi * shimmer_freq * t)
    drone *= shimmer

    # Stereo spread with slight detuning
    track[start_sample:end_sample, 0] = drone
    # Right channel slightly detuned for width
    t_r = t + 0.002  # 2ms offset
    drone_r = np.zeros(len(t_r))
    for ratio, level in harmonics:
        freq = base_freq * ratio * 1.002  # Slight sharp
        drone_r += np.sin(2 * np.pi * freq * t_r) * level
    drone_r = drone_r / np.max(np.abs(drone_r)) * amplitude * shimmer
    track[start_sample:end_sample, 1] = drone_r

    # Smooth fade
    fade_samples = int(15 * SAMPLE_RATE)
    track[start_sample:start_sample + fade_samples] *= np.linspace(0, 1, fade_samples)[:, np.newaxis]
    track[end_sample - fade_samples:end_sample] *= np.linspace(1, 0, fade_samples)[:, np.newaxis]

    print(f"    Active: {active_start}-{active_end}s (111 Hz mystical drone)")

    return track

# =============================================================================
# LAYER 5: SUB-BASS OSCILLATION (0.9-1.2 Hz)
# =============================================================================
def generate_sub_bass():
    """
    Sub-Bass Oscillation (0.9-1.2 Hz)
    Purpose: Body resonance, grounding, "grav-field" effect
    Sound: Felt more than heard, like the hum of a starship hull

    Active: 150-1680s (throughout main journey)
    """
    print("\n🔊 Layer 5: Sub-Bass Oscillation")

    total_samples = int(SAMPLE_RATE * DURATION)
    track = np.zeros((total_samples, 2), dtype=np.float32)

    active_start = 150
    active_end = min(1680, DURATION)  # Cap at actual duration
    amplitude = 0.2  # Higher for physical presence

    start_sample = int(active_start * SAMPLE_RATE)
    end_sample = min(int(active_end * SAMPLE_RATE), int(SAMPLE_RATE * DURATION))
    duration = (end_sample - start_sample) / SAMPLE_RATE

    t = np.linspace(0, duration, end_sample - start_sample, False)

    # Very low frequency oscillation (felt, not heard)
    # Modulating between 0.9 and 1.2 Hz
    lfo_freq = 0.05  # Very slow modulation
    pulse_freq = 1.05 + 0.15 * np.sin(2 * np.pi * lfo_freq * t)

    # Integrate frequency to get phase
    phase = np.cumsum(pulse_freq) / SAMPLE_RATE
    pulse = np.sin(2 * np.pi * phase)

    # Sub-bass carrier (around 30-40 Hz for physical rumble)
    carrier_freq = 35
    carrier = np.sin(2 * np.pi * carrier_freq * t)
    carrier += np.sin(2 * np.pi * carrier_freq * 2 * t) * 0.3  # Add harmonic

    # Modulate carrier with ultra-slow pulse
    sub_bass = carrier * (0.6 + 0.4 * pulse) * amplitude

    # Apply lowpass to keep it truly sub
    b, a = signal.butter(2, 80 / (SAMPLE_RATE / 2), btype='low')
    sub_bass = signal.filtfilt(b, a, sub_bass)

    # Stereo (mono sub-bass for coherence)
    track[start_sample:end_sample, 0] = sub_bass
    track[start_sample:end_sample, 1] = sub_bass

    # Long fade in/out
    fade_samples = int(20 * SAMPLE_RATE)
    track[start_sample:start_sample + fade_samples] *= np.linspace(0, 1, fade_samples)[:, np.newaxis]
    track[end_sample - fade_samples:end_sample] *= np.linspace(1, 0, fade_samples)[:, np.newaxis]

    print(f"    Active: {active_start}-{active_end}s (starship hull resonance)")

    return track

# =============================================================================
# LAYER 6: HYPERSPACE WIND TEXTURES
# =============================================================================
def generate_hyperspace_wind():
    """
    Hyperspace Wind Textures
    Purpose: Evoke the sense of passing through interstellar membranes
    Sound: Airy, slow-moving, swirling winds with reverb tails

    Active: 540-1500s (journey phases)
    """
    print("\n🌬️ Layer 6: Hyperspace Wind Textures")

    total_samples = int(SAMPLE_RATE * DURATION)
    track = np.zeros((total_samples, 2), dtype=np.float32)

    active_start = 540
    active_end = 1500
    amplitude = 0.06

    start_sample = int(active_start * SAMPLE_RATE)
    end_sample = int(active_end * SAMPLE_RATE)
    duration = active_end - active_start
    samples = end_sample - start_sample

    # Generate filtered noise base
    np.random.seed(123)
    noise_l = np.random.randn(samples)
    noise_r = np.random.randn(samples)

    # Bandpass filter for "wind" character (200-2000 Hz)
    b_bp, a_bp = signal.butter(3, [200 / (SAMPLE_RATE / 2), 2000 / (SAMPLE_RATE / 2)], btype='band')
    wind_l = signal.filtfilt(b_bp, a_bp, noise_l)
    wind_r = signal.filtfilt(b_bp, a_bp, noise_r)

    # Create slow swirling motion with amplitude modulation
    t = np.linspace(0, duration, samples, False)

    # Multiple LFOs for complex swirling
    swirl1 = 0.5 + 0.3 * np.sin(2 * np.pi * 0.03 * t)  # Very slow
    swirl2 = 0.5 + 0.2 * np.sin(2 * np.pi * 0.07 * t + 1.5)  # Slightly faster
    swirl3 = 0.5 + 0.15 * np.sin(2 * np.pi * 0.11 * t + 3.0)  # Different phase

    swirl_envelope = swirl1 * swirl2 * swirl3

    # Apply swirl to wind
    wind_l = wind_l * swirl_envelope * amplitude
    wind_r = wind_r * swirl_envelope * amplitude

    # Cross-feed for stereo width
    wind_l_final = wind_l * 0.7 + wind_r * 0.3
    wind_r_final = wind_r * 0.7 + wind_l * 0.3

    # Add reverb-like tail using FFT-based convolution (much faster)
    reverb_length = int(2.0 * SAMPLE_RATE)  # 2 second reverb
    decay = np.exp(-np.linspace(0, 5, reverb_length))
    reverb_ir = np.random.randn(reverb_length) * decay * 0.02

    # Use scipy.signal.fftconvolve for efficient convolution
    wind_l_final = signal.fftconvolve(wind_l_final, reverb_ir, mode='same')
    wind_r_final = signal.fftconvolve(wind_r_final, reverb_ir, mode='same')

    track[start_sample:end_sample, 0] = wind_l_final
    track[start_sample:end_sample, 1] = wind_r_final

    # Smooth fade
    fade_samples = int(20 * SAMPLE_RATE)
    track[start_sample:start_sample + fade_samples] *= np.linspace(0, 1, fade_samples)[:, np.newaxis]
    track[end_sample - fade_samples:end_sample] *= np.linspace(1, 0, fade_samples)[:, np.newaxis]

    print(f"    Active: {active_start}-{active_end}s (interstellar membrane winds)")

    return track

# =============================================================================
# LAYER 7: SHIP-MEMORY ECHOES
# =============================================================================
def generate_ship_memory():
    """
    Ship-Memory Echoes
    Purpose: Mimic a living vessel recalling ancient knowledge
    Sound: Faint whispers, reversed tones, soft electro-chimes

    Active: 720-1200s (deeper journey phases)
    """
    print("\n🚀 Layer 7: Ship-Memory Echoes")

    total_samples = int(SAMPLE_RATE * DURATION)
    track = np.zeros((total_samples, 2), dtype=np.float32)

    active_start = 720
    active_end = 1200
    amplitude = 0.05

    start_sample = int(active_start * SAMPLE_RATE)
    end_sample = int(active_end * SAMPLE_RATE)
    duration = active_end - active_start

    np.random.seed(777)

    # Generate sparse chime events
    num_chimes = int(duration / 5)  # Roughly one event every 5 seconds
    chime_times = np.sort(np.random.uniform(0, duration, num_chimes))

    # Chime frequencies (crystalline, harmonic)
    chime_freqs = [523, 659, 784, 880, 1047, 1175]  # C5, E5, G5, A5, C6, D6

    for chime_time in chime_times:
        chime_sample = start_sample + int(chime_time * SAMPLE_RATE)

        # Random chime duration (0.5-2 seconds)
        chime_duration = np.random.uniform(0.5, 2.0)
        chime_samples = int(chime_duration * SAMPLE_RATE)

        if chime_sample + chime_samples > end_sample:
            continue

        t = np.linspace(0, chime_duration, chime_samples, False)

        # Select random frequency
        freq = np.random.choice(chime_freqs)

        # Generate chime with decay
        decay = np.exp(-t * 3)
        chime = np.sin(2 * np.pi * freq * t) * decay

        # Add harmonic overtones for "electro-chime" character
        chime += np.sin(2 * np.pi * freq * 2.0 * t) * decay * 0.3
        chime += np.sin(2 * np.pi * freq * 3.0 * t) * decay * 0.15

        # Random pan
        pan = np.random.uniform(-0.5, 0.5)

        # Apply amplitude
        chime *= amplitude

        # Add to track with pan
        track[chime_sample:chime_sample + chime_samples, 0] += chime * (0.5 - pan)
        track[chime_sample:chime_sample + chime_samples, 1] += chime * (0.5 + pan)

        # 30% chance to add reversed tail (memory echo effect)
        if np.random.random() < 0.3:
            reversed_chime = chime[::-1] * 0.4
            reverse_start = chime_sample + chime_samples
            if reverse_start + chime_samples <= end_sample:
                track[reverse_start:reverse_start + chime_samples, 0] += reversed_chime * (0.5 + pan)
                track[reverse_start:reverse_start + chime_samples, 1] += reversed_chime * (0.5 - pan)

    # Add subtle whisper-like filtered noise bursts
    num_whispers = int(duration / 15)  # One every ~15 seconds
    whisper_times = np.sort(np.random.uniform(0, duration, num_whispers))

    for whisper_time in whisper_times:
        whisper_sample = start_sample + int(whisper_time * SAMPLE_RATE)
        whisper_duration = np.random.uniform(1.0, 3.0)
        whisper_samples = int(whisper_duration * SAMPLE_RATE)

        if whisper_sample + whisper_samples > end_sample:
            continue

        # Generate filtered noise "whisper"
        noise = np.random.randn(whisper_samples)

        # Narrow bandpass for whisper character
        center_freq = np.random.uniform(800, 1500)
        b, a = signal.butter(3, [center_freq * 0.8 / (SAMPLE_RATE / 2),
                                  center_freq * 1.2 / (SAMPLE_RATE / 2)], btype='band')
        whisper = signal.filtfilt(b, a, noise)

        # Envelope
        env_t = np.linspace(0, 1, whisper_samples)
        envelope = np.sin(env_t * np.pi) ** 2  # Smooth rise and fall
        whisper = whisper * envelope * amplitude * 0.3

        # Pan
        pan = np.random.uniform(-0.6, 0.6)
        track[whisper_sample:whisper_sample + whisper_samples, 0] += whisper * (0.5 - pan)
        track[whisper_sample:whisper_sample + whisper_samples, 1] += whisper * (0.5 + pan)

    # Overall fade
    fade_samples = int(15 * SAMPLE_RATE)
    track[start_sample:start_sample + fade_samples] *= np.linspace(0, 1, fade_samples)[:, np.newaxis]
    track[end_sample - fade_samples:end_sample] *= np.linspace(1, 0, fade_samples)[:, np.newaxis]

    print(f"    Active: {active_start}-{active_end}s (ancient vessel memories)")

    return track

# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 70)
    print("ATLAS STARSHIP ANCIENT FUTURE")
    print("Ultimate Consciousness-Altering Soundscape Generator")
    print(f"Duration: {DURATION} seconds ({DURATION/60:.1f} minutes)")
    print("=" * 70)

    ensure_output_dir()

    # Generate all layers
    print("\n📡 Generating 7 consciousness-altering layers...")

    # Layer 1: Theta Gateway
    theta = generate_theta_gateway()
    save_stem(theta, "01_theta_gateway.wav", "Binaural beats: 432 Hz carrier, alpha→theta→delta→alpha")

    # Layer 2: Delta Drift
    delta = generate_delta_drift()
    save_stem(delta, "02_delta_drift.wav", "Warp engine pulsations: 2.5-3 Hz body resonance")

    # Layer 3: Xenolinguistic Tones
    xeno = generate_xenolinguistic()
    save_stem(xeno, "03_xenolinguistic.wav", "Microtonal alien tones: 11-limit just intonation")

    # Layer 4: Harmonic Drone
    drone = generate_harmonic_drone()
    save_stem(drone, "04_harmonic_drone.wav", "111 Hz mystical drone: angelic metallic ring")

    # Layer 5: Sub-Bass
    sub = generate_sub_bass()
    save_stem(sub, "05_sub_bass.wav", "Sub-bass oscillation: 0.9-1.2 Hz grav-field effect")

    # Layer 6: Hyperspace Wind
    wind = generate_hyperspace_wind()
    save_stem(wind, "06_hyperspace_wind.wav", "Filtered wind textures: interstellar membrane swirls")

    # Layer 7: Ship Memory
    memory = generate_ship_memory()
    save_stem(memory, "07_ship_memory.wav", "Electro-chimes and reversed echoes: vessel memories")

    print("\n" + "=" * 70)
    print("✅ ALL 7 LAYERS GENERATED SUCCESSFULLY")
    print(f"   Output directory: {OUTPUT_DIR}/")
    print("=" * 70)
    print("\n📋 Layer Summary:")
    print("   01. Theta Gateway    - Base binaural beats (full track)")
    print("   02. Delta Drift      - Warp engine pulse (900-1500s)")
    print("   03. Xenolinguistic   - Alien microtonal (540-1500s)")
    print("   04. Harmonic Drone   - 111 Hz mystical (540-1500s)")
    print("   05. Sub-Bass         - Hull resonance (150-1680s)")
    print("   06. Hyperspace Wind  - Swirling textures (540-1500s)")
    print("   07. Ship Memory      - Echoes & chimes (720-1200s)")
    print("\n🎛️  Ready for mixing (stems not combined)")

if __name__ == "__main__":
    main()
