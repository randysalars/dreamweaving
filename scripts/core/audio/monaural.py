#!/usr/bin/env python3
"""
Monaural Beats Generator
Universal module for Dreamweaving project
Monaural beats are created by summing two tones and playing the result to both ears
Simpler than binaural - reinforces binaural effects, works without headphones
"""

import numpy as np
from scipy.io import wavfile
import os

def generate(
    sections,
    duration_sec,
    sample_rate=48000,
    carrier_freq=150,
    amplitude=0.2,
    fade_in_sec=5.0,
    fade_out_sec=8.0
):
    """
    Generate monaural beats audio

    Args:
        sections: List of dicts with {start, end, freq_start, freq_end, transition}
        duration_sec: Total duration in seconds
        sample_rate: Sample rate in Hz
        carrier_freq: Base carrier frequency (Hz) - typically 100-200 Hz
        amplitude: Output amplitude (0.0-1.0)
        fade_in_sec: Fade in duration (seconds)
        fade_out_sec: Fade out duration (seconds)

    Returns:
        numpy array of stereo audio samples (float32)
    """

    print(f"Generating monaural beats: {duration_sec/60:.1f} min, carrier={carrier_freq}Hz")

    # Initialize empty track
    total_samples = int(sample_rate * duration_sec)
    full_track = np.zeros((total_samples, 2), dtype=np.float32)

    current_sample = 0

    # Process each section
    for idx, section in enumerate(sections):
        start = section['start']
        end = section['end']
        duration = end - start
        freq_start = section.get('freq_start', section.get('beat_hz', 6))
        freq_end = section.get('freq_end', freq_start)
        transition = section.get('transition', 'linear')

        print(f"  Section {idx+1}/{len(sections)}: {start}s-{end}s, {freq_start}Hz→{freq_end}Hz ({transition})")

        # Generate segment
        segment = _generate_segment(
            duration, freq_start, freq_end, carrier_freq,
            amplitude, sample_rate, transition
        )
        end_sample = current_sample + len(segment)
        full_track[current_sample:end_sample] = segment
        current_sample = end_sample

    # Apply global fade in/out
    if fade_in_sec > 0:
        fade_in_samples = int(fade_in_sec * sample_rate)
        fade_in_curve = np.linspace(0, 1, fade_in_samples)
        full_track[:fade_in_samples, 0] *= fade_in_curve
        full_track[:fade_in_samples, 1] *= fade_in_curve

    if fade_out_sec > 0:
        fade_out_samples = int(fade_out_sec * sample_rate)
        fade_out_curve = np.linspace(1, 0, fade_out_samples)
        full_track[-fade_out_samples:, 0] *= fade_out_curve
        full_track[-fade_out_samples:, 1] *= fade_out_curve

    print(f"✓ Monaural beats generated: {len(full_track)/sample_rate/60:.1f} min")

    return full_track


def _generate_segment(duration, freq_start, freq_end, carrier_freq, amplitude, sample_rate, transition='linear'):
    """
    Generate a single segment with frequency progression

    Monaural beats are created by summing two tones:
    - Tone 1: carrier - (beat/2)
    - Tone 2: carrier + (beat/2)
    The interference creates the beat frequency, played to both ears
    """
    segment_samples = int(sample_rate * duration)
    mono_signal = np.zeros(segment_samples, dtype=np.float32)

    for i in range(segment_samples):
        t = i / sample_rate
        progress = i / segment_samples

        # Interpolate beat frequency
        if transition == 'logarithmic' and freq_start > 0 and freq_end > 0:
            beat_freq = freq_start * ((freq_end / freq_start) ** progress)
        else:  # linear or hold
            beat_freq = freq_start + (freq_end - freq_start) * progress

        # Calculate the two component frequencies
        freq1 = carrier_freq - (beat_freq / 2)
        freq2 = carrier_freq + (beat_freq / 2)

        # Sum the two tones to create monaural beat
        tone1 = np.sin(2 * np.pi * freq1 * t)
        tone2 = np.sin(2 * np.pi * freq2 * t)

        # Average and apply amplitude
        mono_signal[i] = ((tone1 + tone2) / 2) * amplitude

    # Duplicate mono signal to stereo (both ears receive same signal)
    stereo_segment = np.stack([mono_signal, mono_signal], axis=1).astype(np.float32)

    return stereo_segment


def save_stem(audio, path, sample_rate=48000):
    """
    Save monaural audio as WAV file

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
    print(f"✓ Saved monaural stem: {path} ({file_size:.1f} MB)")


def generate_from_manifest(manifest, session_dir):
    """
    Generate monaural beats from session manifest

    Args:
        manifest: Session manifest dict
        session_dir: Session directory path

    Returns:
        Path to generated stem file
    """
    if not manifest['sound_bed']['monaural'].get('enabled', False):
        print("Monaural beats disabled in manifest")
        return None

    monaural_config = manifest['sound_bed']['monaural']

    # Build sections from manifest
    sections = []
    for section in monaural_config.get('sections', []):
        sections.append({
            'start': section['start'],
            'end': section['end'],
            'freq_start': section.get('beat_hz', 6),
            'freq_end': section.get('beat_hz', 6),
            'transition': 'linear'
        })

    # Generate
    duration = manifest['session']['duration']
    carrier = monaural_config.get('carrier_hz', 150)

    audio = generate(
        sections=sections,
        duration_sec=duration,
        carrier_freq=carrier
    )

    # Save
    stem_path = os.path.join(session_dir, "working_files/stems/monaural.wav")
    save_stem(audio, stem_path)

    return stem_path


# Example usage for testing
if __name__ == '__main__':
    print("Testing monaural beat generation...")

    # Simple test: 2-minute track with theta frequency
    sections = [
        {'start': 0, 'end': 60, 'freq_start': 6, 'freq_end': 6},  # 6 Hz theta
        {'start': 60, 'end': 120, 'freq_start': 6, 'freq_end': 8}  # Transition to 8 Hz alpha-theta border
    ]

    audio = generate(sections, duration_sec=120, carrier_freq=150)
    save_stem(audio, "test_monaural.wav")

    print("✓ Test complete: test_monaural.wav")
