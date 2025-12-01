#!/usr/bin/env python3
"""
Nature Sounds Generator
Universal module for Dreamweaving project
Generates procedural nature sounds: rain, stream, forest ambience
Provides grounding and natural soundscape for meditation
"""

import numpy as np
from scipy.io import wavfile
import os

def generate(
    sound_type,
    duration_sec,
    sample_rate=48000,
    amplitude=0.15,
    variation=0.5,
    fade_in_sec=10.0,
    fade_out_sec=10.0
):
    """
    Generate nature sounds audio

    Args:
        sound_type: 'rain', 'stream', 'forest', or 'ocean'
        duration_sec: Total duration in seconds
        sample_rate: Sample rate in Hz
        amplitude: Output amplitude (0.0-1.0)
        variation: Amount of variation/randomness (0.0-1.0)
        fade_in_sec: Fade in duration (seconds)
        fade_out_sec: Fade out duration (seconds)

    Returns:
        numpy array of stereo audio samples (float32)
    """

    print(f"Generating nature sounds: {sound_type}, {duration_sec/60:.1f} min")

    total_samples = int(sample_rate * duration_sec)

    # Generate based on sound type
    if sound_type == 'rain':
        stereo_audio = _generate_rain(total_samples, sample_rate, variation)
    elif sound_type == 'stream':
        stereo_audio = _generate_stream(total_samples, sample_rate, variation)
    elif sound_type == 'forest':
        stereo_audio = _generate_forest(total_samples, sample_rate, variation)
    elif sound_type == 'ocean':
        stereo_audio = _generate_ocean(total_samples, sample_rate, variation)
    else:
        raise ValueError(f"Unknown sound type: {sound_type}")

    # Apply amplitude
    stereo_audio = stereo_audio * amplitude

    # Apply fade in/out (longer fades for nature sounds)
    if fade_in_sec > 0:
        fade_in_samples = int(fade_in_sec * sample_rate)
        fade_in_curve = np.linspace(0, 1, fade_in_samples)
        stereo_audio[:fade_in_samples, 0] *= fade_in_curve
        stereo_audio[:fade_in_samples, 1] *= fade_in_curve

    if fade_out_sec > 0:
        fade_out_samples = int(fade_out_sec * sample_rate)
        fade_out_curve = np.linspace(1, 0, fade_out_samples)
        stereo_audio[-fade_out_samples:, 0] *= fade_out_curve
        stereo_audio[-fade_out_samples:, 1] *= fade_out_curve

    print(f"✓ Nature sounds generated: {len(stereo_audio)/sample_rate/60:.1f} min")

    return stereo_audio


def _generate_rain(total_samples, sample_rate, variation):
    """
    Generate rain sound using filtered noise with random droplets

    Rain = continuous pink noise + individual raindrop impacts
    """
    # Base: filtered pink noise for continuous rain
    left_base = _generate_filtered_noise(total_samples, sample_rate, 'pink', 200, 8000)
    right_base = _generate_filtered_noise(total_samples, sample_rate, 'pink', 200, 8000)

    stereo = np.stack([left_base, right_base], axis=1).astype(np.float32)

    # Add random raindrops
    if variation > 0.3:
        num_drops = int(total_samples / sample_rate * 5 * variation)  # ~5 drops/sec with variation
        for _ in range(num_drops):
            position = np.random.randint(0, total_samples - 2000)
            drop = _generate_raindrop(sample_rate)
            pan = np.random.rand()  # Random stereo position

            # Add drop to track
            end_pos = min(position + len(drop), total_samples)
            drop_length = end_pos - position
            stereo[position:end_pos, 0] += drop[:drop_length] * (1 - pan) * variation
            stereo[position:end_pos, 1] += drop[:drop_length] * pan * variation

    return stereo


def _generate_stream(total_samples, sample_rate, variation):
    """
    Generate stream/water sound using filtered noise with gentle modulation
    """
    # Base: filtered noise in water frequency range
    left_base = _generate_filtered_noise(total_samples, sample_rate, 'pink', 100, 6000)
    right_base = _generate_filtered_noise(total_samples, sample_rate, 'pink', 100, 6000)

    # Add gentle modulation (water flow variation)
    t = np.linspace(0, total_samples / sample_rate, total_samples, False)
    modulation = 1.0 + 0.2 * variation * np.sin(2 * np.pi * 0.1 * t)  # Slow 0.1 Hz modulation

    left_base = left_base * modulation
    right_base = right_base * modulation

    # Add occasional burbles (higher frequency events)
    if variation > 0.4:
        num_burbles = int(total_samples / sample_rate * 2 * variation)
        for _ in range(num_burbles):
            position = np.random.randint(0, total_samples - 5000)
            burble = _generate_filtered_noise(5000, sample_rate, 'white', 2000, 8000)
            envelope = np.exp(-np.linspace(0, 5, 5000))
            burble = burble * envelope * 0.3

            pan = np.random.rand()
            end_pos = min(position + len(burble), total_samples)
            burble_length = end_pos - position
            left_base[position:end_pos] += burble[:burble_length] * (1 - pan)
            right_base[position:end_pos] += burble[:burble_length] * pan

    stereo = np.stack([left_base, right_base], axis=1).astype(np.float32)
    return stereo


def _generate_forest(total_samples, sample_rate, variation):
    """
    Generate forest ambience using very low-level filtered noise + occasional bird-like sounds
    """
    # Very gentle background (wind through trees)
    left_base = _generate_filtered_noise(total_samples, sample_rate, 'pink', 50, 2000) * 0.3
    right_base = _generate_filtered_noise(total_samples, sample_rate, 'pink', 50, 2000) * 0.3

    # Add occasional bird-like chirps
    if variation > 0.3:
        num_birds = int(total_samples / sample_rate * 0.5 * variation)  # Sparse
        for _ in range(num_birds):
            position = np.random.randint(0, total_samples - 10000)
            bird = _generate_bird_chirp(sample_rate)
            pan = np.random.rand()

            end_pos = min(position + len(bird), total_samples)
            bird_length = end_pos - position
            left_base[position:end_pos] += bird[:bird_length] * (1 - pan) * variation * 0.5
            right_base[position:end_pos] += bird[:bird_length] * pan * variation * 0.5

    stereo = np.stack([left_base, right_base], axis=1).astype(np.float32)
    return stereo


def _generate_ocean(total_samples, sample_rate, variation):
    """
    Generate ocean waves using low-frequency noise with rhythmic swells
    """
    # Base: very low frequency noise (wave rumble)
    left_base = _generate_filtered_noise(total_samples, sample_rate, 'pink', 20, 1000)
    right_base = _generate_filtered_noise(total_samples, sample_rate, 'pink', 20, 1000)

    # Add wave rhythm (0.1 Hz = ~10 second waves)
    t = np.linspace(0, total_samples / sample_rate, total_samples, False)
    wave_rhythm = 0.3 + 0.7 * (1 + np.sin(2 * np.pi * 0.1 * t)) / 2

    left_base = left_base * wave_rhythm
    right_base = right_base * wave_rhythm

    # Add foam/splash on wave peaks
    if variation > 0.3:
        wave_period_samples = int(sample_rate * 10)  # 10 second waves
        num_waves = total_samples // wave_period_samples

        for i in range(num_waves):
            position = int(i * wave_period_samples + wave_period_samples * 0.7)  # Near peak
            if position < total_samples - 10000:
                splash = _generate_filtered_noise(10000, sample_rate, 'white', 1000, 12000)
                envelope = np.exp(-np.linspace(0, 8, 10000))
                splash = splash * envelope * variation * 0.4

                end_pos = min(position + len(splash), total_samples)
                splash_length = end_pos - position
                left_base[position:end_pos] += splash[:splash_length]
                right_base[position:end_pos] += splash[:splash_length]

    stereo = np.stack([left_base, right_base], axis=1).astype(np.float32)
    return stereo


def _generate_filtered_noise(num_samples, sample_rate, noise_type, low_cutoff, high_cutoff):
    """Generate filtered noise (pink or white) in specified frequency range"""
    if noise_type == 'pink':
        # Simple pink noise approximation
        white = np.random.randn(num_samples)
        # Apply simple IIR filter for pink-ish spectrum
        pink = np.zeros(num_samples)
        b0, b1, b2 = 0.99886, 0.0555179, 0.0750759
        pink[0] = white[0]
        pink[1] = b0 * pink[0] + white[1]
        for i in range(2, num_samples):
            pink[i] = b0 * pink[i-1] - b1 * pink[i-2] + white[i]
        noise = pink
    else:  # white
        noise = np.random.randn(num_samples)

    # Apply simple frequency filtering (butterworth-like)
    # This is a simplified version - proper filtering would use scipy.signal
    from scipy import signal
    nyquist = sample_rate / 2
    low = low_cutoff / nyquist
    high = high_cutoff / nyquist
    b, a = signal.butter(4, [low, high], btype='band')
    filtered = signal.filtfilt(b, a, noise)

    # Normalize
    if np.max(np.abs(filtered)) > 0:
        filtered = filtered / np.max(np.abs(filtered))

    return filtered


def _generate_raindrop(sample_rate):
    """Generate single raindrop impact sound"""
    duration = 0.05  # 50ms
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)

    # Short burst of filtered noise
    noise = np.random.randn(samples)

    # Sharp attack, quick decay
    envelope = np.exp(-t * 50)

    drop = noise * envelope
    return drop


def _generate_bird_chirp(sample_rate):
    """Generate simple bird-like chirp"""
    duration = 0.3  # 300ms chirp
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)

    # Frequency sweep (bird-like)
    freq_start = 2000 + np.random.rand() * 2000  # 2-4 kHz
    freq_end = freq_start + 500 + np.random.rand() * 1000  # Upward sweep

    freq = np.linspace(freq_start, freq_end, samples)
    chirp = np.sin(2 * np.pi * np.cumsum(freq) / sample_rate)

    # Envelope
    attack = int(samples * 0.1)
    release = int(samples * 0.3)
    envelope = np.ones(samples)
    envelope[:attack] = np.linspace(0, 1, attack)
    envelope[-release:] = np.linspace(1, 0, release)

    chirp = chirp * envelope * 0.3
    return chirp


def save_stem(audio, path, sample_rate=48000):
    """
    Save nature sounds as WAV file

    Args:
        audio: numpy array (stereo, float32)
        path: Output file path
        sample_rate: Sample rate in Hz
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Convert to 16-bit PCM
    audio_int = (audio * 32767).astype(np.int16)

    # Save
    wavfile.write(path, sample_rate, audio_int)

    file_size = os.path.getsize(path) / (1024 * 1024)
    print(f"✓ Saved nature sounds stem: {path} ({file_size:.1f} MB)")


def generate_from_manifest(manifest, session_dir):
    """
    Generate nature sounds from session manifest

    Args:
        manifest: Session manifest dict
        session_dir: Session directory path

    Returns:
        Path to generated stem file
    """
    if not manifest['sound_bed']['nature'].get('enabled', False):
        print("Nature sounds disabled in manifest")
        return None

    nature_config = manifest['sound_bed']['nature']

    # Generate
    duration = manifest['session']['duration']
    sound_type = nature_config.get('type', 'rain')
    variation = nature_config.get('variation', 0.5)

    audio = generate(
        sound_type=sound_type,
        duration_sec=duration,
        variation=variation
    )

    # Save
    stem_path = os.path.join(session_dir, "working_files/stems/nature.wav")
    save_stem(audio, stem_path)

    return stem_path


# Example usage for testing
if __name__ == '__main__':
    print("Testing nature sounds generation...")

    duration = 30  # 30 seconds each

    print("\n1. Rain:")
    audio_rain = generate('rain', duration_sec=duration, variation=0.7)
    save_stem(audio_rain, "test_nature_rain.wav")

    print("\n2. Stream:")
    audio_stream = generate('stream', duration_sec=duration, variation=0.6)
    save_stem(audio_stream, "test_nature_stream.wav")

    print("\n3. Forest:")
    audio_forest = generate('forest', duration_sec=duration, variation=0.5)
    save_stem(audio_forest, "test_nature_forest.wav")

    print("\n4. Ocean:")
    audio_ocean = generate('ocean', duration_sec=duration, variation=0.6)
    save_stem(audio_ocean, "test_nature_ocean.wav")

    print("\n✓ All tests complete!")
    print("\nGenerated files:")
    print("  - test_nature_rain.wav")
    print("  - test_nature_stream.wav")
    print("  - test_nature_forest.wav")
    print("  - test_nature_ocean.wav")
