#!/usr/bin/env python3
"""
Percussion / Shamanic Drumming Generator
Universal module for Dreamweaving project
Generates rhythmic percussion patterns for entrainment (typically 4-7 Hz)
Shamanic drumming is especially effective for theta brainwave states
"""

import numpy as np
from scipy.io import wavfile
import os

def generate(
    sections,
    duration_sec,
    sample_rate=48000,
    amplitude=0.2,
    drum_type='frame',  # 'frame', 'bass', 'hand'
    stereo_width=0.3,
    fade_in_sec=5.0,
    fade_out_sec=8.0
):
    """
    Generate percussion/drumming audio

    Args:
        sections: List of dicts with {start, end, tempo_bpm, pattern}
        duration_sec: Total duration in seconds
        sample_rate: Sample rate in Hz
        amplitude: Output amplitude (0.0-1.0)
        drum_type: 'frame' (shamanic), 'bass' (deep), 'hand' (tabla-like)
        stereo_width: Amount of stereo spread (0.0-1.0)
        fade_in_sec: Fade in duration (seconds)
        fade_out_sec: Fade out duration (seconds)

    Returns:
        numpy array of stereo audio samples (float32)
    """

    print(f"Generating percussion: {duration_sec/60:.1f} min, type={drum_type}")

    # Initialize empty track
    total_samples = int(sample_rate * duration_sec)
    stereo_track = np.zeros((total_samples, 2), dtype=np.float32)

    current_sample = 0

    # Process each section
    for idx, section in enumerate(sections):
        start = section['start']
        end = section['end']
        duration = end - start
        tempo_bpm = section.get('tempo_bpm', 240)  # 4 Hz = 240 BPM
        pattern = section.get('pattern', 'steady')  # steady, shamanic, heartbeat

        print(f"  Section {idx+1}/{len(sections)}: {start}s-{end}s, {tempo_bpm} BPM ({pattern} pattern)")

        # Generate segment
        segment = _generate_segment(
            duration, tempo_bpm, pattern, drum_type,
            amplitude, stereo_width, sample_rate
        )
        end_sample = current_sample + len(segment)
        stereo_track[current_sample:end_sample] = segment
        current_sample = end_sample

    # Apply global fade in/out
    if fade_in_sec > 0:
        fade_in_samples = int(fade_in_sec * sample_rate)
        fade_in_curve = np.linspace(0, 1, fade_in_samples)
        stereo_track[:fade_in_samples, 0] *= fade_in_curve
        stereo_track[:fade_in_samples, 1] *= fade_in_curve

    if fade_out_sec > 0:
        fade_out_samples = int(fade_out_sec * sample_rate)
        fade_out_curve = np.linspace(1, 0, fade_out_samples)
        stereo_track[-fade_out_samples:, 0] *= fade_out_curve
        stereo_track[-fade_out_samples:, 1] *= fade_out_curve

    print(f"✓ Percussion generated: {len(stereo_track)/sample_rate/60:.1f} min")

    return stereo_track


def _generate_segment(duration, tempo_bpm, pattern, drum_type, amplitude, stereo_width, sample_rate):
    """Generate percussion segment with specified pattern"""
    segment_samples = int(sample_rate * duration)
    stereo_segment = np.zeros((segment_samples, 2), dtype=np.float32)

    # Convert BPM to interval in samples
    beat_interval_sec = 60.0 / tempo_bpm
    beat_interval_samples = int(beat_interval_sec * sample_rate)

    # Generate beat positions based on pattern
    if pattern == 'shamanic':
        # Shamanic: Strong-weak-medium pattern (3-beat cycle)
        beat_pattern = [1.0, 0.6, 0.8]
    elif pattern == 'heartbeat':
        # Heartbeat: Boom-boom-pause pattern
        beat_pattern = [1.0, 0.7]
    else:  # steady
        # Steady: Even beats
        beat_pattern = [1.0]

    pattern_length = len(beat_pattern)
    beat_count = int(duration / beat_interval_sec)

    for i in range(beat_count):
        beat_time_samples = int(i * beat_interval_samples)
        if beat_time_samples >= segment_samples:
            break

        # Get amplitude for this beat from pattern
        pattern_index = i % pattern_length
        beat_amplitude = amplitude * beat_pattern[pattern_index]

        # Generate drum hit
        drum_hit = _synthesize_drum(drum_type, sample_rate)

        # Apply amplitude
        drum_hit = drum_hit * beat_amplitude

        # Add stereo spread
        if stereo_width > 0:
            # Pan slightly left or right randomly
            pan = (np.random.rand() - 0.5) * stereo_width
            left_gain = 1.0 - (pan if pan > 0 else 0)
            right_gain = 1.0 + (pan if pan < 0 else 0)
        else:
            left_gain = right_gain = 1.0

        # Add to track
        end_sample = min(beat_time_samples + len(drum_hit), segment_samples)
        hit_length = end_sample - beat_time_samples

        stereo_segment[beat_time_samples:end_sample, 0] += drum_hit[:hit_length] * left_gain
        stereo_segment[beat_time_samples:end_sample, 1] += drum_hit[:hit_length] * right_gain

    return stereo_segment


def _synthesize_drum(drum_type, sample_rate):
    """
    Synthesize drum hit sound

    Creates realistic drum sounds using:
    - Sharp attack
    - Frequency sweep (pitch bend)
    - Exponential decay
    """
    duration = 0.5  # 500ms drum hit
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)

    if drum_type == 'frame':
        # Frame drum: Mid-low frequency, warm tone
        # Frequency sweeps from 200 Hz down to 80 Hz
        freq = 200 * np.exp(-t * 8) + 80
        drum = np.sin(2 * np.pi * np.cumsum(freq) / sample_rate)

        # Exponential decay envelope
        envelope = np.exp(-t * 6)

    elif drum_type == 'bass':
        # Bass drum: Deep, punchy
        # Frequency sweeps from 100 Hz down to 40 Hz
        freq = 100 * np.exp(-t * 10) + 40
        drum = np.sin(2 * np.pi * np.cumsum(freq) / sample_rate)

        # Faster decay
        envelope = np.exp(-t * 8)

    else:  # 'hand' (tabla-like)
        # Hand drum: Higher pitch, snappier
        # Frequency sweeps from 300 Hz down to 150 Hz
        freq = 300 * np.exp(-t * 7) + 150
        drum = np.sin(2 * np.pi * np.cumsum(freq) / sample_rate)

        # Medium decay
        envelope = np.exp(-t * 7)

    # Apply envelope
    drum = drum * envelope

    # Add slight noise/texture for realism
    noise = np.random.randn(len(drum)) * 0.05 * envelope
    drum = drum + noise

    # Normalize
    if np.max(np.abs(drum)) > 0:
        drum = drum / np.max(np.abs(drum))

    return drum


def save_stem(audio, path, sample_rate=48000):
    """
    Save percussion as WAV file

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
    print(f"✓ Saved percussion stem: {path} ({file_size:.1f} MB)")


def generate_from_manifest(manifest, session_dir):
    """
    Generate percussion from session manifest

    Args:
        manifest: Session manifest dict
        session_dir: Session directory path

    Returns:
        Path to generated stem file
    """
    if not manifest['sound_bed']['percussion'].get('enabled', False):
        print("Percussion disabled in manifest")
        return None

    perc_config = manifest['sound_bed']['percussion']

    # Build sections from manifest
    sections = []
    for section in perc_config.get('sections', []):
        sections.append({
            'start': section['start'],
            'end': section['end'],
            'tempo_bpm': section.get('tempo_bpm', 240),
            'pattern': section.get('pattern', 'steady')
        })

    # Generate
    duration = manifest['session']['duration']
    drum_type = perc_config.get('drum_type', 'frame')
    stereo_width = perc_config.get('stereo_width', 0.3)

    audio = generate(
        sections=sections,
        duration_sec=duration,
        drum_type=drum_type,
        stereo_width=stereo_width
    )

    # Save
    stem_path = os.path.join(session_dir, "working_files/stems/percussion.wav")
    save_stem(audio, stem_path)

    return stem_path


# Example usage for testing
if __name__ == '__main__':
    print("Testing percussion generation...")

    # Test different drum types and patterns
    sections = [
        {'start': 0, 'end': 15, 'tempo_bpm': 240, 'pattern': 'steady'},      # 4 Hz
        {'start': 15, 'end': 30, 'tempo_bpm': 240, 'pattern': 'shamanic'},   # Shamanic pattern
        {'start': 30, 'end': 45, 'tempo_bpm': 300, 'pattern': 'heartbeat'}   # 5 Hz heartbeat
    ]

    print("\n1. Frame drum (shamanic):")
    audio_frame = generate(sections, duration_sec=45, drum_type='frame')
    save_stem(audio_frame, "test_percussion_frame.wav")

    print("\n2. Bass drum (deep):")
    audio_bass = generate(sections, duration_sec=45, drum_type='bass')
    save_stem(audio_bass, "test_percussion_bass.wav")

    print("\n✓ Test complete: test_percussion_frame.wav and test_percussion_bass.wav")
