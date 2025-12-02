#!/usr/bin/env python3
"""
Generate Binaural Beats for Temple of a Thousand Steps

Creates a multi-section binaural beat track matching the manifest.yaml frequencies:
  - 0-180s:    11.0 Hz (Alpha for pretalk)
  - 180-420s:  10.0 Hz (Alpha settling)
  - 420-720s:  10.5 Hz (Alpha climbing)
  - 720-1260s:  7.0 Hz (Theta for deep work)
  - 1260-1500s: 7.5 Hz (Theta temple)
  - 1500-1680s: 9.0 Hz (Theta-alpha integration)
  - 1680-1800s: 10.0 Hz (Alpha return)

Requirements:
    pip install numpy scipy

Usage:
    python generate_binaural_beats.py [duration_seconds]

Output:
    binaural_track.wav - The complete binaural beat track (stereo)
"""

import numpy as np
from scipy.io import wavfile
import os
import sys

# Audio settings
SAMPLE_RATE = 48000
BASE_FREQ = 144  # Carrier frequency from manifest

# Binaural sections from manifest
SECTIONS = [
    {"start": 0,    "end": 180,  "offset_hz": 11.0},  # Alpha for pretalk
    {"start": 180,  "end": 420,  "offset_hz": 10.0},  # Alpha settling
    {"start": 420,  "end": 720,  "offset_hz": 10.5},  # Alpha climbing
    {"start": 720,  "end": 1260, "offset_hz": 7.0},   # Theta for deep work
    {"start": 1260, "end": 1500, "offset_hz": 7.5},   # Theta temple
    {"start": 1500, "end": 1680, "offset_hz": 9.0},   # Theta-alpha integration
    {"start": 1680, "end": 1800, "offset_hz": 10.0},  # Alpha return
]


def generate_binaural_beat(base_freq, beat_freq, duration, sample_rate=SAMPLE_RATE):
    """Generate a binaural beat with given frequencies."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    left_freq = base_freq
    right_freq = base_freq + beat_freq

    left_channel = np.sin(2 * np.pi * left_freq * t)
    right_channel = np.sin(2 * np.pi * right_freq * t)

    stereo = np.stack([left_channel, right_channel], axis=1)
    return stereo


def generate_binaural_ramp(base_freq, start_beat, end_beat, duration, sample_rate=SAMPLE_RATE):
    """Generate binaural beat with frequency ramping for smooth transitions."""
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, False)

    # Left channel stays constant
    left_channel = np.sin(2 * np.pi * base_freq * t)

    # Right channel ramps from base + start_beat to base + end_beat
    freq_ramp = np.linspace(start_beat, end_beat, num_samples)
    phase = np.cumsum(2 * np.pi * (base_freq + freq_ramp) / sample_rate)
    right_channel = np.sin(phase)

    stereo = np.stack([left_channel, right_channel], axis=1)
    return stereo


def apply_fade(audio, fade_duration=2.0, sample_rate=SAMPLE_RATE):
    """Apply fade in/out to avoid clicks."""
    fade_samples = int(fade_duration * sample_rate)
    fade_samples = min(fade_samples, len(audio) // 4)  # Max 25% of audio

    if fade_samples > 0:
        fade_in = np.linspace(0, 1, fade_samples)
        audio[:fade_samples] *= fade_in[:, np.newaxis]

        fade_out = np.linspace(1, 0, fade_samples)
        audio[-fade_samples:] *= fade_out[:, np.newaxis]

    return audio


def normalize_audio(audio, target_amplitude=0.3):
    """Normalize audio to target amplitude (30% for mixing with voice)."""
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio * (target_amplitude / max_val)
    return audio


def create_temple_binaural_track(target_duration=None):
    """
    Create the complete binaural beat track for Temple of a Thousand Steps.
    Matches the frequency schedule in manifest.yaml.
    """

    print("=" * 70)
    print("   Temple of a Thousand Steps - Binaural Beat Generator")
    print("   Alpha-Theta progression for consistency work")
    print("=" * 70)
    print()

    sections_audio = []

    for i, section in enumerate(SECTIONS):
        start = section["start"]
        end = section["end"]
        freq = section["offset_hz"]
        duration = end - start

        # Get next section's frequency for transition
        if i < len(SECTIONS) - 1:
            next_freq = SECTIONS[i + 1]["offset_hz"]

            # Main section (90% of duration)
            main_duration = duration * 0.9
            # Transition (10% of duration)
            trans_duration = duration * 0.1

            print(f"🎵 Section {i+1}: {start}s - {end}s | {freq} Hz → {next_freq} Hz")

            main_audio = generate_binaural_beat(BASE_FREQ, freq, main_duration)
            trans_audio = generate_binaural_ramp(BASE_FREQ, freq, next_freq, trans_duration)

            section_audio = np.concatenate([main_audio, trans_audio], axis=0)
        else:
            # Last section - no transition needed
            print(f"🎵 Section {i+1}: {start}s - {end}s | {freq} Hz (final)")
            section_audio = generate_binaural_beat(BASE_FREQ, freq, duration)

        sections_audio.append(section_audio)

    # Concatenate all sections
    print("\n🔗 Concatenating sections...")
    full_track = np.concatenate(sections_audio, axis=0)

    # Extend if target duration is longer
    if target_duration and target_duration > len(full_track) / SAMPLE_RATE:
        extra_needed = int((target_duration - len(full_track) / SAMPLE_RATE) * SAMPLE_RATE)
        print(f"📏 Extending track by {extra_needed / SAMPLE_RATE:.1f}s to match voice duration...")
        # Continue with the last frequency
        last_freq = SECTIONS[-1]["offset_hz"]
        extra_audio = generate_binaural_beat(BASE_FREQ, last_freq, extra_needed / SAMPLE_RATE)
        full_track = np.concatenate([full_track, extra_audio], axis=0)

    # Apply fade in/out
    print("🎚️  Applying fade in/out...")
    full_track = apply_fade(full_track, fade_duration=3.0)

    # Normalize
    print("📊 Normalizing to 30% amplitude...")
    full_track = normalize_audio(full_track, target_amplitude=0.3)

    # Calculate duration
    duration_minutes = len(full_track) / SAMPLE_RATE / 60

    # Convert to 16-bit PCM
    audio_int16 = np.int16(full_track * 32767)

    # Save
    output_file = "binaural_track.wav"
    print(f"\n💾 Saving to {output_file}...")
    wavfile.write(output_file, SAMPLE_RATE, audio_int16)

    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

    print()
    print("=" * 70)
    print("✅ SUCCESS! Binaural track generated successfully!")
    print("=" * 70)
    print(f"📁 Output file: {output_file}")
    print(f"📊 File size: {file_size_mb:.2f} MB")
    print(f"⏱️  Duration: {duration_minutes:.1f} minutes")
    print(f"🎚️  Carrier: {BASE_FREQ} Hz")
    print(f"🔊 Amplitude: 30% (ready for mixing with voice)")
    print()

    return output_file


if __name__ == "__main__":
    target_duration = None
    if len(sys.argv) > 1:
        try:
            target_duration = float(sys.argv[1])
            print(f"Target duration: {target_duration:.1f}s")
        except ValueError:
            pass

    create_temple_binaural_track(target_duration)
