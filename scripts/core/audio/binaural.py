#!/usr/bin/env python3
"""
Binaural Beats Generator
Universal module ported from Neural Network Navigator
Supports frequency transitions, gamma bursts, and ADSR envelopes
"""

import numpy as np
from scipy.io import wavfile
import os

def generate(
    sections,
    duration_sec,
    sample_rate=48000,
    carrier_freq=200,
    amplitude=0.3,
    fade_in_sec=5.0,
    fade_out_sec=8.0,
    gamma_bursts=None
):
    """
    Generate binaural beats audio

    Args:
        sections: List of dicts with {start, end, freq_start, freq_end, transition}
        duration_sec: Total duration in seconds
        sample_rate: Sample rate in Hz
        carrier_freq: Base carrier frequency (Hz)
        amplitude: Output amplitude (0.0-1.0)
        fade_in_sec: Fade in duration (seconds)
        fade_out_sec: Fade out duration (seconds)
        gamma_bursts: Optional list of {time, duration, frequency}

    Returns:
        numpy array of stereo audio samples (float32)
    """

    print(f"Generating binaural beats: {duration_sec/60:.1f} min, carrier={carrier_freq}Hz")

    # Initialize empty track
    total_samples = int(sample_rate * duration_sec)
    full_track = np.zeros((total_samples, 2), dtype=np.float32)

    current_sample = 0

    # Process each section
    for idx, section in enumerate(sections):
        start = section['start']
        end = section['end']
        duration = end - start
        freq_start = section.get('freq_start', section.get('beat_hz', 10))
        freq_end = section.get('freq_end', freq_start)
        transition = section.get('transition', 'linear')

        print(f"  Section {idx+1}/{len(sections)}: {start}s-{end}s, {freq_start}Hz→{freq_end}Hz ({transition})")

        # Check for gamma burst in this section
        gamma_in_section = None
        if gamma_bursts:
            for gamma in gamma_bursts:
                if start <= gamma['time'] < end:
                    gamma_in_section = gamma
                    break

        if gamma_in_section:
            # Split around gamma burst
            gamma_time = gamma_in_section['time']
            gamma_duration = gamma_in_section['duration']
            gamma_freq = gamma_in_section['frequency']

            # Pre-gamma segment
            pre_duration = gamma_time - start
            if pre_duration > 0:
                segment = _generate_segment(
                    pre_duration, freq_start, freq_end, carrier_freq,
                    amplitude, sample_rate, transition
                )
                end_sample = current_sample + len(segment)
                full_track[current_sample:end_sample] = segment
                current_sample = end_sample

            # Gamma burst
            print(f"    ⚡ GAMMA BURST at {gamma_time}s: {gamma_freq}Hz for {gamma_duration}s")
            gamma_segment = _generate_gamma_burst(
                carrier_freq, gamma_freq, gamma_duration,
                amplitude, sample_rate
            )
            end_sample = current_sample + len(gamma_segment)
            full_track[current_sample:end_sample] = gamma_segment
            current_sample = end_sample

            # Post-gamma segment
            post_duration = end - (gamma_time + gamma_duration)
            if post_duration > 0:
                segment = _generate_segment(
                    post_duration, freq_start, freq_end, carrier_freq,
                    amplitude, sample_rate, transition
                )
                end_sample = current_sample + len(segment)
                full_track[current_sample:end_sample] = segment
                current_sample = end_sample
        else:
            # Standard segment
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

    print(f"✓ Binaural beats generated: {len(full_track)/sample_rate/60:.1f} min")

    return full_track


def _generate_segment(duration, freq_start, freq_end, carrier_freq, amplitude, sample_rate, transition='linear'):
    """Generate a single segment with frequency progression"""
    segment_samples = int(sample_rate * duration)
    segment = np.zeros((segment_samples, 2), dtype=np.float32)

    for i in range(segment_samples):
        t = i / sample_rate
        progress = i / segment_samples

        # Interpolate beat frequency
        if transition == 'logarithmic' and freq_start > 0 and freq_end > 0:
            beat_freq = freq_start * ((freq_end / freq_start) ** progress)
        else:  # linear or hold
            beat_freq = freq_start + (freq_end - freq_start) * progress

        # Calculate left/right frequencies
        left_freq = carrier_freq - (beat_freq / 2)
        right_freq = carrier_freq + (beat_freq / 2)

        # Generate tones
        segment[i, 0] = np.sin(2 * np.pi * left_freq * t) * amplitude
        segment[i, 1] = np.sin(2 * np.pi * right_freq * t) * amplitude

    return segment


def _generate_gamma_burst(carrier_freq, gamma_freq, duration, amplitude, sample_rate):
    """Generate intense gamma burst with quick envelope"""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)

    # Calculate frequencies
    left_freq = carrier_freq - (gamma_freq / 2)
    right_freq = carrier_freq + (gamma_freq / 2)

    # Generate tones
    left_tone = np.sin(2 * np.pi * left_freq * t)
    right_tone = np.sin(2 * np.pi * right_freq * t)

    # Envelope: quick fade in, sustain, quick fade out
    fade_in_samples = int(0.2 * sample_rate)
    fade_out_samples = int(0.5 * sample_rate)

    envelope = np.ones(len(t))
    envelope[:fade_in_samples] = np.linspace(0, 1, fade_in_samples)
    envelope[-fade_out_samples:] = np.linspace(1, 0, fade_out_samples)

    # Apply envelope with slight boost for impact
    left_tone = left_tone * envelope * amplitude * 1.2
    right_tone = right_tone * envelope * amplitude * 1.2

    stereo = np.stack([left_tone, right_tone], axis=1).astype(np.float32)
    return stereo


def save_stem(audio, path, sample_rate=48000):
    """
    Save binaural audio as WAV file

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
    print(f"✓ Saved binaural stem: {path} ({file_size:.1f} MB)")


def generate_from_manifest(manifest, session_dir):
    """
    Generate binaural beats from session manifest

    Args:
        manifest: Session manifest dict
        session_dir: Session directory path

    Returns:
        Path to generated stem file
    """
    if not manifest['sound_bed']['binaural'].get('enabled', False):
        print("Binaural beats disabled in manifest")
        return None

    binaural_config = manifest['sound_bed']['binaural']

    # Build sections from manifest
    sections = []
    for section in binaural_config.get('sections', []):
        sections.append({
            'start': section['start'],
            'end': section['end'],
            'freq_start': section.get('offset_hz', section.get('beat_hz', 10)),
            'freq_end': section.get('offset_hz', section.get('beat_hz', 10)),
            'transition': 'linear'
        })

    # Extract gamma bursts if present
    gamma_bursts = []
    for fx in manifest.get('fx_timeline', []):
        if fx.get('type') == 'gamma_flash':
            gamma_bursts.append({
                'time': fx['time'],
                'duration': fx.get('duration_s', 3.0),
                'frequency': fx.get('freq_hz', 40)
            })

    # Generate
    duration = manifest['session']['duration']
    carrier = binaural_config.get('base_hz', 200)

    audio = generate(
        sections=sections,
        duration_sec=duration,
        carrier_freq=carrier,
        gamma_bursts=gamma_bursts if gamma_bursts else None
    )

    # Save
    stem_path = os.path.join(session_dir, "working_files/stems/binaural.wav")
    save_stem(audio, stem_path)

    return stem_path


# Example usage for testing
if __name__ == '__main__':
    print("Testing binaural beat generation...")

    # Simple test: 2-minute track with alpha->theta transition
    sections = [
        {'start': 0, 'end': 60, 'freq_start': 10, 'freq_end': 10},  # 10 Hz alpha
        {'start': 60, 'end': 120, 'freq_start': 10, 'freq_end': 6}  # Transition to 6 Hz theta
    ]

    audio = generate(sections, duration_sec=120, carrier_freq=200)
    save_stem(audio, "test_binaural.wav")

    print("✓ Test complete: test_binaural.wav")
