#!/usr/bin/env python3
"""
Alternate Beeps Generator
Universal module for Dreamweaving project
Short tones that alternate between left and right ears
Creates rhythmic entrainment and spatial awareness
"""

import numpy as np
from scipy.io import wavfile
import os

def generate(
    sections,
    duration_sec,
    sample_rate=48000,
    tone_freq=400,
    amplitude=0.18,
    fade_in_sec=5.0,
    fade_out_sec=8.0
):
    """
    Generate alternating beeps audio

    Args:
        sections: List of dicts with {start, end, freq_start, freq_end, beep_duration}
        duration_sec: Total duration in seconds
        sample_rate: Sample rate in Hz
        tone_freq: Frequency of the beep tone (Hz)
        amplitude: Output amplitude (0.0-1.0)
        fade_in_sec: Fade in duration (seconds)
        fade_out_sec: Fade out duration (seconds)

    Returns:
        numpy array of stereo audio samples (float32)
    """

    print(f"Generating alternate beeps: {duration_sec/60:.1f} min, tone={tone_freq}Hz")

    # Initialize empty track
    total_samples = int(sample_rate * duration_sec)
    full_track = np.zeros((total_samples, 2), dtype=np.float32)

    current_sample = 0

    # Process each section
    for idx, section in enumerate(sections):
        start = section['start']
        end = section['end']
        duration = end - start
        freq_start = section.get('freq_start', section.get('beep_hz', 4))
        freq_end = section.get('freq_end', freq_start)
        beep_duration_ms = section.get('beep_duration_ms', 50)  # Duration of each beep in ms
        transition = section.get('transition', 'linear')

        print(f"  Section {idx+1}/{len(sections)}: {start}s-{end}s, {freq_start}Hz→{freq_end}Hz, beep={beep_duration_ms}ms")

        # Generate segment
        segment = _generate_segment(
            duration, freq_start, freq_end, beep_duration_ms, tone_freq,
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

    print(f"✓ Alternate beeps generated: {len(full_track)/sample_rate/60:.1f} min")

    return full_track


def _generate_segment(duration, freq_start, freq_end, beep_duration_ms, tone_freq, amplitude, sample_rate, transition='linear'):
    """Generate segment with alternating beeps"""
    segment_samples = int(sample_rate * duration)
    stereo_segment = np.zeros((segment_samples, 2), dtype=np.float32)

    # Calculate beep parameters
    beep_samples = int((beep_duration_ms / 1000.0) * sample_rate)

    current_sample = 0
    beep_count = 0

    while current_sample < segment_samples:
        # Calculate current beep rate
        progress = current_sample / segment_samples
        if transition == 'logarithmic' and freq_start > 0 and freq_end > 0:
            beep_rate = freq_start * ((freq_end / freq_start) ** progress)
        else:  # linear
            beep_rate = freq_start + (freq_end - freq_start) * progress

        # Calculate interval between beeps (in samples)
        interval_samples = int(sample_rate / beep_rate)

        # Generate beep
        beep = _generate_beep(beep_samples, tone_freq, sample_rate)

        # Determine which channel (alternate L/R)
        channel = beep_count % 2  # 0 = left, 1 = right

        # Add beep to appropriate channel
        end_sample = min(current_sample + beep_samples, segment_samples)
        beep_length = end_sample - current_sample

        stereo_segment[current_sample:end_sample, channel] += beep[:beep_length] * amplitude

        # Move to next beep position
        current_sample += interval_samples
        beep_count += 1

    return stereo_segment


def _generate_beep(beep_samples, tone_freq, sample_rate):
    """
    Generate a single beep with smooth envelope

    Uses a sine tone with attack/release to avoid clicks
    """
    t = np.linspace(0, beep_samples / sample_rate, beep_samples, False)

    # Generate sine tone
    beep = np.sin(2 * np.pi * tone_freq * t)

    # Apply envelope to prevent clicks
    # Quick attack (5%), sustain (90%), quick release (5%)
    attack_samples = max(int(beep_samples * 0.05), 1)
    release_samples = max(int(beep_samples * 0.05), 1)

    envelope = np.ones(beep_samples)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    envelope[-release_samples:] = np.linspace(1, 0, release_samples)

    beep = beep * envelope

    return beep


def save_stem(audio, path, sample_rate=48000):
    """
    Save alternate beeps as WAV file

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
    print(f"✓ Saved alternate beeps stem: {path} ({file_size:.1f} MB)")


def generate_from_manifest(manifest, session_dir):
    """
    Generate alternate beeps from session manifest

    Args:
        manifest: Session manifest dict
        session_dir: Session directory path

    Returns:
        Path to generated stem file
    """
    if not manifest['sound_bed']['alternate_beeps'].get('enabled', False):
        print("Alternate beeps disabled in manifest")
        return None

    beeps_config = manifest['sound_bed']['alternate_beeps']

    # Build sections from manifest
    sections = []
    for section in beeps_config.get('sections', []):
        sections.append({
            'start': section['start'],
            'end': section['end'],
            'freq_start': section.get('beep_hz', 4),
            'freq_end': section.get('beep_hz', 4),
            'beep_duration_ms': section.get('beep_duration_ms', 50),
            'transition': 'linear'
        })

    # Generate
    duration = manifest['session']['duration']
    tone_freq = beeps_config.get('tone_hz', 400)

    audio = generate(
        sections=sections,
        duration_sec=duration,
        tone_freq=tone_freq
    )

    # Save
    stem_path = os.path.join(session_dir, "working_files/stems/alternate_beeps.wav")
    save_stem(audio, stem_path)

    return stem_path


# Example usage for testing
if __name__ == '__main__':
    print("Testing alternate beeps generation...")

    sections = [
        {
            'start': 0,
            'end': 15,
            'freq_start': 4,
            'freq_end': 4,
            'beep_duration_ms': 50  # Short beeps
        },
        {
            'start': 15,
            'end': 30,
            'freq_start': 4,
            'freq_end': 6,
            'beep_duration_ms': 100  # Longer beeps
        }
    ]

    audio = generate(sections, duration_sec=30, tone_freq=400)
    save_stem(audio, "test_alternate_beeps.wav")

    print("✓ Test complete: test_alternate_beeps.wav")
    print("\nListening notes:")
    print("  - Wear headphones to experience alternation")
    print("  - First 15s: 4 Hz rate with short beeps")
    print("  - Last 15s: 4→6 Hz transition with longer beeps")
