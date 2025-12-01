#!/usr/bin/env python3
"""
Amplitude Modulated (AM) Tones Generator
Universal module for Dreamweaving project
Generates tones with amplitude modulation in the 40-200 Hz range
AM at these frequencies creates audible rhythm/beating effects
"""

import numpy as np
from scipy.io import wavfile
import os

def generate(
    sections,
    duration_sec,
    sample_rate=48000,
    carrier_freq=500,
    amplitude=0.2,
    modulation_depth=0.8,
    fade_in_sec=5.0,
    fade_out_sec=8.0
):
    """
    Generate amplitude modulated tones audio

    Args:
        sections: List of dicts with {start, end, mod_freq_start, mod_freq_end}
        duration_sec: Total duration in seconds
        sample_rate: Sample rate in Hz
        carrier_freq: Base carrier frequency (Hz) - typically 400-800 Hz
        amplitude: Output amplitude (0.0-1.0)
        modulation_depth: Depth of AM (0.0-1.0, typically 0.6-0.9)
        fade_in_sec: Fade in duration (seconds)
        fade_out_sec: Fade out duration (seconds)

    Returns:
        numpy array of stereo audio samples (float32)
    """

    print(f"Generating AM tones: {duration_sec/60:.1f} min, carrier={carrier_freq}Hz, depth={modulation_depth}")

    # Initialize empty track
    total_samples = int(sample_rate * duration_sec)
    mono_signal = np.zeros(total_samples, dtype=np.float32)

    current_sample = 0

    # Process each section
    for idx, section in enumerate(sections):
        start = section['start']
        end = section['end']
        duration = end - start
        mod_freq_start = section.get('mod_freq_start', section.get('mod_hz', 40))
        mod_freq_end = section.get('mod_freq_end', mod_freq_start)
        transition = section.get('transition', 'linear')

        print(f"  Section {idx+1}/{len(sections)}: {start}s-{end}s, modulation {mod_freq_start}Hz→{mod_freq_end}Hz")

        # Generate segment
        segment = _generate_segment(
            duration, mod_freq_start, mod_freq_end, carrier_freq,
            amplitude, modulation_depth, sample_rate, transition
        )
        end_sample = current_sample + len(segment)
        mono_signal[current_sample:end_sample] = segment
        current_sample = end_sample

    # Duplicate to stereo (AM tones are identical both ears)
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

    print(f"✓ AM tones generated: {len(stereo_signal)/sample_rate/60:.1f} min")

    return stereo_signal


def _generate_segment(duration, mod_freq_start, mod_freq_end, carrier_freq, amplitude, modulation_depth, sample_rate, transition='linear'):
    """
    Generate AM tone segment

    AM formula: output = carrier * (1 + depth * modulator)
    Where modulator is a low-frequency sine wave
    """
    segment_samples = int(sample_rate * duration)
    segment = np.zeros(segment_samples, dtype=np.float32)

    for i in range(segment_samples):
        t = i / sample_rate
        progress = i / segment_samples

        # Interpolate modulation frequency
        if transition == 'logarithmic' and mod_freq_start > 0 and mod_freq_end > 0:
            mod_freq = mod_freq_start * ((mod_freq_end / mod_freq_start) ** progress)
        else:  # linear
            mod_freq = mod_freq_start + (mod_freq_end - mod_freq_start) * progress

        # Generate carrier tone
        carrier = np.sin(2 * np.pi * carrier_freq * t)

        # Generate modulation signal
        # Modulator ranges from -1 to +1
        modulator = np.sin(2 * np.pi * mod_freq * t)

        # Apply amplitude modulation
        # (1 + depth * modulator) ranges from (1-depth) to (1+depth)
        # For depth=0.8, this is 0.2 to 1.8
        am_signal = carrier * (1 + modulation_depth * modulator)

        # Normalize back to -1 to +1 range
        am_signal = am_signal / (1 + modulation_depth)

        segment[i] = am_signal * amplitude

    return segment


def save_stem(audio, path, sample_rate=48000):
    """
    Save AM tones as WAV file

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
    print(f"✓ Saved AM tones stem: {path} ({file_size:.1f} MB)")


def generate_from_manifest(manifest, session_dir):
    """
    Generate AM tones from session manifest

    Args:
        manifest: Session manifest dict
        session_dir: Session directory path

    Returns:
        Path to generated stem file
    """
    if not manifest['sound_bed']['am_tones'].get('enabled', False):
        print("AM tones disabled in manifest")
        return None

    am_config = manifest['sound_bed']['am_tones']

    # Build sections from manifest
    sections = []
    for section in am_config.get('sections', []):
        sections.append({
            'start': section['start'],
            'end': section['end'],
            'mod_freq_start': section.get('mod_hz', 40),
            'mod_freq_end': section.get('mod_hz', 40),
            'transition': 'linear'
        })

    # Generate
    duration = manifest['session']['duration']
    carrier = am_config.get('carrier_hz', 500)
    modulation_depth = am_config.get('modulation_depth', 0.8)

    audio = generate(
        sections=sections,
        duration_sec=duration,
        carrier_freq=carrier,
        modulation_depth=modulation_depth
    )

    # Save
    stem_path = os.path.join(session_dir, "working_files/stems/am_tones.wav")
    save_stem(audio, stem_path)

    return stem_path


# Example usage for testing
if __name__ == '__main__':
    print("Testing AM tones generation...")

    # Test different modulation frequencies
    sections = [
        {
            'start': 0,
            'end': 10,
            'mod_freq_start': 40,
            'mod_freq_end': 40  # Gamma frequency
        },
        {
            'start': 10,
            'end': 20,
            'mod_freq_start': 40,
            'mod_freq_end': 100  # Transition to higher modulation
        },
        {
            'start': 20,
            'end': 30,
            'mod_freq_start': 10,
            'mod_freq_end': 10  # Alpha-like rhythm
        }
    ]

    audio = generate(sections, duration_sec=30, carrier_freq=500, modulation_depth=0.8)
    save_stem(audio, "test_am_tones.wav")

    print("✓ Test complete: test_am_tones.wav")
    print("\nListening notes:")
    print("  - 0-10s: 40 Hz modulation (gamma rhythm)")
    print("  - 10-20s: 40→100 Hz transition")
    print("  - 20-30s: 10 Hz modulation (alpha rhythm)")
    print("  - You should hear rhythmic pulsing of the tone")
