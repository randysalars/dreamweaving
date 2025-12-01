#!/usr/bin/env python3
"""
Panning Beats Generator
Universal module for Dreamweaving project
Creates intensity-modulated tones that pan between left and right
Simulates movement and enhances spatial awareness during meditation
"""

import numpy as np
from scipy.io import wavfile
import os

def generate(
    sections,
    duration_sec,
    sample_rate=48000,
    carrier_freq=300,
    amplitude=0.2,
    fade_in_sec=5.0,
    fade_out_sec=8.0
):
    """
    Generate panning beats audio

    Args:
        sections: List of dicts with {start, end, freq_start, freq_end, pan_speed}
        duration_sec: Total duration in seconds
        sample_rate: Sample rate in Hz
        carrier_freq: Base tone frequency (Hz)
        amplitude: Output amplitude (0.0-1.0)
        fade_in_sec: Fade in duration (seconds)
        fade_out_sec: Fade out duration (seconds)

    Returns:
        numpy array of stereo audio samples (float32)
    """

    print(f"Generating panning beats: {duration_sec/60:.1f} min, carrier={carrier_freq}Hz")

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
        pan_speed = section.get('pan_speed', 0.1)  # Hz of panning (0.1 = 1 cycle per 10 sec)
        transition = section.get('transition', 'linear')

        print(f"  Section {idx+1}/{len(sections)}: {start}s-{end}s, {freq_start}Hz→{freq_end}Hz, pan={pan_speed}Hz")

        # Generate segment
        segment = _generate_segment(
            duration, freq_start, freq_end, pan_speed, carrier_freq,
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

    print(f"✓ Panning beats generated: {len(full_track)/sample_rate/60:.1f} min")

    return full_track


def _generate_segment(duration, freq_start, freq_end, pan_speed, carrier_freq, amplitude, sample_rate, transition='linear'):
    """
    Generate segment with panning beats

    Creates a carrier tone with amplitude modulation at the beat frequency,
    and pans the modulated signal between left and right channels
    """
    segment_samples = int(sample_rate * duration)
    stereo_segment = np.zeros((segment_samples, 2), dtype=np.float32)

    for i in range(segment_samples):
        t = i / sample_rate
        progress = i / segment_samples

        # Interpolate beat frequency
        if transition == 'logarithmic' and freq_start > 0 and freq_end > 0:
            beat_freq = freq_start * ((freq_end / freq_start) ** progress)
        else:  # linear
            beat_freq = freq_start + (freq_end - freq_start) * progress

        # Generate carrier tone
        carrier = np.sin(2 * np.pi * carrier_freq * t)

        # Apply amplitude modulation at beat frequency
        # Modulation depth creates the "beat" effect
        modulation = 0.5 + 0.5 * np.sin(2 * np.pi * beat_freq * t)
        modulated_tone = carrier * modulation

        # Calculate pan position (oscillates -1 to +1)
        pan_position = np.sin(2 * np.pi * pan_speed * t)

        # Convert pan position to left/right gains
        # -1 = full left, 0 = center, +1 = full right
        # Using constant power panning for smooth transitions
        pan_angle = (pan_position + 1) * (np.pi / 4)  # Map to 0 to π/2
        left_gain = np.cos(pan_angle)
        right_gain = np.sin(pan_angle)

        # Apply panning and amplitude
        stereo_segment[i, 0] = modulated_tone * left_gain * amplitude
        stereo_segment[i, 1] = modulated_tone * right_gain * amplitude

    return stereo_segment


def save_stem(audio, path, sample_rate=48000):
    """
    Save panning beats as WAV file

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
    print(f"✓ Saved panning beats stem: {path} ({file_size:.1f} MB)")


def generate_from_manifest(manifest, session_dir):
    """
    Generate panning beats from session manifest

    Args:
        manifest: Session manifest dict
        session_dir: Session directory path

    Returns:
        Path to generated stem file
    """
    if not manifest['sound_bed']['panning_beats'].get('enabled', False):
        print("Panning beats disabled in manifest")
        return None

    panning_config = manifest['sound_bed']['panning_beats']

    # Build sections from manifest
    sections = []
    for section in panning_config.get('sections', []):
        sections.append({
            'start': section['start'],
            'end': section['end'],
            'freq_start': section.get('beat_hz', 6),
            'freq_end': section.get('beat_hz', 6),
            'pan_speed': section.get('pan_speed', 0.1),
            'transition': 'linear'
        })

    # Generate
    duration = manifest['session']['duration']
    carrier = panning_config.get('carrier_hz', 300)

    audio = generate(
        sections=sections,
        duration_sec=duration,
        carrier_freq=carrier
    )

    # Save
    stem_path = os.path.join(session_dir, "working_files/stems/panning_beats.wav")
    save_stem(audio, stem_path)

    return stem_path


# Example usage for testing
if __name__ == '__main__':
    print("Testing panning beats generation...")

    # Test with different panning speeds
    sections = [
        {
            'start': 0,
            'end': 20,
            'freq_start': 6,
            'freq_end': 6,
            'pan_speed': 0.1  # Slow pan (10 sec per cycle)
        },
        {
            'start': 20,
            'end': 40,
            'freq_start': 6,
            'freq_end': 8,
            'pan_speed': 0.25  # Faster pan (4 sec per cycle)
        }
    ]

    audio = generate(sections, duration_sec=40, carrier_freq=300)
    save_stem(audio, "test_panning_beats.wav")

    print("✓ Test complete: test_panning_beats.wav")
    print("\nListening notes:")
    print("  - Wear headphones to experience panning effect")
    print("  - First 20s: slow panning (10s cycle)")
    print("  - Last 20s: faster panning (4s cycle) with frequency transition")
