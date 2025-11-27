#!/usr/bin/env python3
"""
Generate 5 essential sound effects for Neural Network Navigator
Using numpy/scipy for programmatic generation - no external samples needed
"""

import numpy as np
from scipy.io import wavfile
import os

SAMPLE_RATE = 44100
AMPLITUDE = 0.3  # Gentle volume for meditation

def generate_gamma_burst_noise(duration=3, fade_in=0.2, fade_out=0.5):
    """
    Generate white noise burst for gamma moment at 18:45
    Quick fade in, sustain, gradual fade out
    """
    samples = int(SAMPLE_RATE * duration)

    # White noise
    noise = np.random.normal(0, 1, samples)

    # Envelope
    envelope = np.ones(samples)

    # Quick fade in (0.2 seconds)
    fade_in_samples = int(SAMPLE_RATE * fade_in)
    envelope[:fade_in_samples] = np.linspace(0, 1, fade_in_samples)

    # Gradual fade out (0.5 seconds)
    fade_out_samples = int(SAMPLE_RATE * fade_out)
    envelope[-fade_out_samples:] = np.linspace(1, 0, fade_out_samples)

    # Apply envelope and amplitude
    noise = noise * envelope * AMPLITUDE * 0.8  # Slightly quieter

    # Normalize
    noise = noise / np.max(np.abs(noise)) * AMPLITUDE * 0.8

    # Convert to stereo
    stereo = np.stack([noise, noise], axis=1)

    return stereo

def generate_crystal_bell(duration=2.0, fundamental=528):
    """
    Generate crystal bell ping sound
    Uses 528 Hz (Solfeggio frequency) as fundamental
    Multiple harmonics with exponential decay
    """
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples, False)

    # Harmonics: fundamental and partials
    harmonics = [
        (1.0, 1.0),    # Fundamental
        (2.0, 0.6),    # Octave
        (3.0, 0.4),    # Perfect fifth
        (4.5, 0.3),    # Slightly inharmonic for bell character
        (6.2, 0.2),    # Higher partial
    ]

    signal = np.zeros(samples)

    for ratio, amplitude in harmonics:
        freq = fundamental * ratio
        partial = np.sin(2 * np.pi * freq * t) * amplitude
        signal += partial

    # Exponential decay envelope (bell characteristic)
    decay_rate = 3.5  # Faster decay = shorter ring
    envelope = np.exp(-decay_rate * t)

    signal = signal * envelope * AMPLITUDE * 0.7

    # Normalize
    signal = signal / np.max(np.abs(signal)) * AMPLITUDE * 0.7

    # Convert to stereo
    stereo = np.stack([signal, signal], axis=1)

    return stereo

def generate_ambient_pad(duration=28*60, base_freq=110):
    """
    Generate soft ambient pad/drone for background
    Low frequency (A2 = 110 Hz) with gentle harmonics
    Slow LFO for organic feel
    """
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples, False)

    # Multiple layers with slight detuning
    layers = [
        (1.0, 0.4, 0.0),      # Fundamental
        (1.5, 0.25, 0.3),     # Perfect fifth, slightly detuned
        (2.0, 0.2, -0.2),     # Octave, detuned
        (3.0, 0.15, 0.15),    # Octave + fifth
    ]

    signal = np.zeros(samples)

    for ratio, amplitude, detune in layers:
        freq = base_freq * ratio + detune
        layer = np.sin(2 * np.pi * freq * t) * amplitude
        signal += layer

    # Slow LFO (0.05 Hz = 20 second cycle) for gentle modulation
    lfo = 0.15 * np.sin(2 * np.pi * 0.05 * t) + 0.85  # Range: 0.7 to 1.0
    signal = signal * lfo

    # Overall amplitude
    signal = signal * AMPLITUDE * 0.5  # Quiet background

    # Normalize
    signal = signal / np.max(np.abs(signal)) * AMPLITUDE * 0.5

    # Convert to stereo
    stereo = np.stack([signal, signal], axis=1)

    return stereo

def generate_wind_chime(duration=3.0):
    """
    Generate wind chime sound for Pathfinder moments
    Multiple pitched tones with random timing and decay
    """
    samples = int(SAMPLE_RATE * duration)
    signal = np.zeros(samples)

    # Pentatonic scale frequencies (ethereal sound)
    notes = [523, 587, 659, 784, 880, 988]  # C5, D5, E5, G5, A5, B5

    # Generate 8-12 random chime hits
    num_chimes = np.random.randint(8, 13)

    for _ in range(num_chimes):
        # Random start time
        start_sample = np.random.randint(0, int(samples * 0.7))

        # Random note
        freq = np.random.choice(notes)

        # Chime duration (0.8-1.5 seconds)
        chime_duration = np.random.uniform(0.8, 1.5)
        chime_samples = int(SAMPLE_RATE * chime_duration)

        # Don't exceed total duration
        if start_sample + chime_samples > samples:
            chime_samples = samples - start_sample

        t = np.linspace(0, chime_duration, chime_samples, False)

        # Single chime with decay
        chime = np.sin(2 * np.pi * freq * t)
        chime += 0.3 * np.sin(2 * np.pi * freq * 2 * t)  # Harmonic

        # Exponential decay
        decay = np.exp(-2.5 * t)
        chime = chime * decay

        # Add to signal
        signal[start_sample:start_sample + chime_samples] += chime * 0.15

    # Overall amplitude
    signal = signal * AMPLITUDE * 0.6

    # Normalize
    signal = signal / np.max(np.abs(signal)) * AMPLITUDE * 0.6

    # Convert to stereo with slight pan variations
    left = signal * 1.0
    right = signal * 0.9  # Slightly quieter in right channel
    stereo = np.stack([left, right], axis=1)

    return stereo

def generate_singing_bowl(duration=8.0, fundamental=256):
    """
    Generate Tibetan singing bowl tone for grounding
    Rich harmonic content with slow amplitude modulation
    """
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples, False)

    # Singing bowl has many harmonics (some slightly inharmonic)
    harmonics = [
        (1.0, 1.0),
        (2.01, 0.8),    # Slightly sharp octave
        (3.02, 0.6),
        (4.05, 0.5),
        (5.12, 0.4),
        (6.23, 0.3),
        (7.51, 0.2),
    ]

    signal = np.zeros(samples)

    for ratio, amplitude in harmonics:
        freq = fundamental * ratio
        partial = np.sin(2 * np.pi * freq * t) * amplitude
        signal += partial

    # Slow amplitude modulation (beating effect)
    modulation = 0.2 * np.sin(2 * np.pi * 0.5 * t) + 0.8
    signal = signal * modulation

    # Gentle exponential decay
    decay = np.exp(-0.3 * t)
    signal = signal * decay

    # Overall amplitude
    signal = signal * AMPLITUDE * 0.7

    # Normalize
    signal = signal / np.max(np.abs(signal)) * AMPLITUDE * 0.7

    # Convert to stereo
    stereo = np.stack([signal, signal], axis=1)

    return stereo

def main():
    print("=" * 60)
    print("NEURAL NETWORK NAVIGATOR - Essential Sound Effects")
    print("=" * 60)
    print("\nGenerating 5 essential sound effects...\n")

    output_dir = "sound_effects"
    os.makedirs(output_dir, exist_ok=True)

    effects = [
        ("gamma_burst_noise.wav", generate_gamma_burst_noise, "Gamma burst white noise (3s)"),
        ("crystal_bell.wav", generate_crystal_bell, "Crystal bell ping (2s)"),
        ("ambient_pad.wav", generate_ambient_pad, "Soft ambient pad (28 min)"),
        ("wind_chime.wav", generate_wind_chime, "Wind chime (3s)"),
        ("singing_bowl.wav", generate_singing_bowl, "Singing bowl (8s)"),
    ]

    for filename, generator, description in effects:
        print(f"Generating {description}...")

        try:
            audio = generator()
            output_path = f"{output_dir}/{filename}"

            # Convert to 16-bit PCM
            audio_int16 = (audio * 32767).astype(np.int16)

            wavfile.write(output_path, SAMPLE_RATE, audio_int16)

            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"  ✓ Saved: {output_path} ({file_size:.1f} MB)\n")

        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            continue

    print("=" * 60)
    print("✓ Essential sound effects generation complete!")
    print("=" * 60)
    print(f"\nGenerated 5 sound effects in {output_dir}/ directory")
    print("\nNext: Mix 3-layer audio (voice + binaural + effects)")

    return 0

if __name__ == '__main__':
    exit(main())
