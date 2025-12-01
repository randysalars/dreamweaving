#!/usr/bin/env python3
"""
Isochronic Tones Generator
Universal module for Dreamweaving project
Isochronic tones are evenly spaced pulses of sound that turn on and off
Works without headphones - useful for entrainment when binaural not possible
"""

import numpy as np
from scipy.io import wavfile
import os

def generate(
    sections,
    duration_sec,
    sample_rate=48000,
    carrier_freq=250,
    amplitude=0.25,
    fade_in_sec=5.0,
    fade_out_sec=8.0,
    pulse_shape='sine'
):
    """
    Generate isochronic tones audio

    Args:
        sections: List of dicts with {start, end, freq_start, freq_end, transition}
        duration_sec: Total duration in seconds
        sample_rate: Sample rate in Hz
        carrier_freq: Base tone frequency (Hz) - typically 200-300 Hz
        amplitude: Output amplitude (0.0-1.0)
        fade_in_sec: Fade in duration (seconds)
        fade_out_sec: Fade out duration (seconds)
        pulse_shape: 'sine' or 'square' for pulse envelope shape

    Returns:
        numpy array of stereo audio samples (float32)
    """

    print(f"Generating isochronic tones: {duration_sec/60:.1f} min, carrier={carrier_freq}Hz")

    # Initialize empty track
    total_samples = int(sample_rate * duration_sec)
    mono_signal = np.zeros(total_samples, dtype=np.float32)

    # Generate carrier tone
    t = np.linspace(0, duration_sec, total_samples, False)
    carrier = np.sin(2 * np.pi * carrier_freq * t) * amplitude

    current_sample = 0

    # Process each section
    for idx, section in enumerate(sections):
        start = section['start']
        end = section['end']
        duration = end - start
        freq_start = section.get('freq_start', section.get('pulse_hz', 6))
        freq_end = section.get('freq_end', freq_start)
        transition = section.get('transition', 'linear')

        print(f"  Section {idx+1}/{len(sections)}: {start}s-{end}s, {freq_start}Hz→{freq_end}Hz ({transition})")

        # Generate pulse envelope for this section
        segment_samples = int(sample_rate * duration)
        envelope = _generate_pulse_envelope(
            segment_samples, freq_start, freq_end, sample_rate,
            transition, pulse_shape
        )

        # Apply envelope to carrier
        end_sample = current_sample + segment_samples
        mono_signal[current_sample:end_sample] = carrier[current_sample:end_sample] * envelope
        current_sample = end_sample

    # Duplicate to stereo (isochronic is identical both ears)
    stereo_signal = np.stack([mono_signal, mono_signal], axis=1).astype(np.float32)

    # Apply global fade in/out
    if fade_in_sec > 0:
        fade_in_samples = int(fade_in_sec * sample_rate)
        fade_in_curve = np.linspace(0, 1, fade_in_samples)
        stereo_signal[:fade_in_samples, 0] *= fade_in_curve
        stereo_signal[:fade_in_samples, 1] *= fade_in_curve

    if fade_out_sec > 0:
        fade_out_samples = int(fade_out_sec * sample_rate)
        fade_out_curve = np.linspace(1, 0, fade_out_samples)
        stereo_signal[-fade_out_samples:, 0] *= fade_out_curve
        stereo_signal[-fade_out_samples:, 1] *= fade_out_curve

    print(f"✓ Isochronic tones generated: {len(stereo_signal)/sample_rate/60:.1f} min")

    return stereo_signal


def _generate_pulse_envelope(segment_samples, freq_start, freq_end, sample_rate, transition='linear', pulse_shape='sine'):
    """
    Generate pulse envelope for isochronic tones

    The envelope determines when the tone is on/off
    - 'sine' shape: smooth on/off (gentler)
    - 'square' shape: abrupt on/off (stronger entrainment)
    """
    envelope = np.zeros(segment_samples, dtype=np.float32)

    for i in range(segment_samples):
        progress = i / segment_samples

        # Interpolate pulse frequency
        if transition == 'logarithmic' and freq_start > 0 and freq_end > 0:
            pulse_freq = freq_start * ((freq_end / freq_start) ** progress)
        else:  # linear
            pulse_freq = freq_start + (freq_end - freq_start) * progress

        # Calculate phase of current pulse
        t = i / sample_rate
        phase = (t * pulse_freq) % 1.0  # 0.0 to 1.0

        # Generate envelope value based on pulse shape
        if pulse_shape == 'square':
            # Square wave: on for 50% of cycle, off for 50%
            envelope[i] = 1.0 if phase < 0.5 else 0.0
        else:  # sine (default)
            # Sine wave: smooth on/off transition
            # Using rectified sine: only positive half
            sine_val = np.sin(2 * np.pi * phase)
            envelope[i] = max(0, sine_val)

    return envelope


def save_stem(audio, path, sample_rate=48000):
    """
    Save isochronic audio as WAV file

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
    print(f"✓ Saved isochronic stem: {path} ({file_size:.1f} MB)")


def generate_from_manifest(manifest, session_dir):
    """
    Generate isochronic tones from session manifest

    Args:
        manifest: Session manifest dict
        session_dir: Session directory path

    Returns:
        Path to generated stem file
    """
    if not manifest['sound_bed']['isochronic'].get('enabled', False):
        print("Isochronic tones disabled in manifest")
        return None

    isochronic_config = manifest['sound_bed']['isochronic']

    # Build sections from manifest
    sections = []
    for section in isochronic_config.get('sections', []):
        sections.append({
            'start': section['start'],
            'end': section['end'],
            'freq_start': section.get('pulse_hz', 6),
            'freq_end': section.get('pulse_hz', 6),
            'transition': 'linear'
        })

    # Generate
    duration = manifest['session']['duration']
    carrier = isochronic_config.get('carrier_hz', 250)
    pulse_shape = isochronic_config.get('pulse_shape', 'sine')

    audio = generate(
        sections=sections,
        duration_sec=duration,
        carrier_freq=carrier,
        pulse_shape=pulse_shape
    )

    # Save
    stem_path = os.path.join(session_dir, "working_files/stems/isochronic.wav")
    save_stem(audio, stem_path)

    return stem_path


# Example usage for testing
if __name__ == '__main__':
    print("Testing isochronic tone generation...")

    # Simple test: 1-minute track with theta pulses
    sections = [
        {'start': 0, 'end': 30, 'freq_start': 6, 'freq_end': 6},  # 6 Hz theta
        {'start': 30, 'end': 60, 'freq_start': 6, 'freq_end': 10}  # Transition to alpha
    ]

    # Test both pulse shapes
    print("\n1. Sine-shaped pulses (gentle):")
    audio_sine = generate(sections, duration_sec=60, carrier_freq=250, pulse_shape='sine')
    save_stem(audio_sine, "test_isochronic_sine.wav")

    print("\n2. Square-shaped pulses (strong):")
    audio_square = generate(sections, duration_sec=60, carrier_freq=250, pulse_shape='square')
    save_stem(audio_square, "test_isochronic_square.wav")

    print("\n✓ Test complete: test_isochronic_sine.wav and test_isochronic_square.wav")
