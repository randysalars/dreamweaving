#!/usr/bin/env python3
"""
Generate Binaural Beats for Garden of Eden Path-Working

Creates a multi-section binaural beat track with Theta waves and Solfeggio frequencies
optimized for hypnotic trance and spiritual journey work.

Requirements:
    pip install numpy scipy

Usage:
    python generate_binaural_beats.py

Output:
    binaural_track.wav - The complete binaural beat track (stereo)

Author: The Sacred Digital Dreamweaver - Randy Sailer's Autonomous AI Clone
"""

import numpy as np
from scipy.io import wavfile
import os

# Audio settings
SAMPLE_RATE = 48000  # 48kHz for high quality
DURATION_TOTAL = 27 * 60  # 27 minutes in seconds (adjust based on final voice track)

def generate_tone(frequency, duration, sample_rate=SAMPLE_RATE):
    """Generate a pure sine wave tone"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(2 * np.pi * frequency * t)
    return tone

def generate_binaural_beat(base_freq, beat_freq, duration, sample_rate=SAMPLE_RATE):
    """
    Generate a binaural beat

    Args:
        base_freq: Carrier frequency (e.g., 174 Hz)
        beat_freq: Binaural beat frequency (e.g., 6 Hz for Theta)
        duration: Duration in seconds
        sample_rate: Sample rate in Hz

    Returns:
        Stereo audio as numpy array
    """
    left_freq = base_freq
    right_freq = base_freq + beat_freq

    left_channel = generate_tone(left_freq, duration, sample_rate)
    right_channel = generate_tone(right_freq, duration, sample_rate)

    # Stack into stereo
    stereo = np.stack([left_channel, right_channel], axis=1)
    return stereo

def ramp_frequency(start_freq, end_freq, duration, sample_rate=SAMPLE_RATE):
    """Create a frequency that gradually transitions from start to end"""
    num_samples = int(sample_rate * duration)
    freq_ramp = np.linspace(start_freq, end_freq, num_samples)

    phase = np.cumsum(2 * np.pi * freq_ramp / sample_rate)
    tone = np.sin(phase)
    return tone

def generate_binaural_ramp(base_freq, start_beat, end_beat, duration, sample_rate=SAMPLE_RATE):
    """Generate binaural beat with frequency ramping"""
    left_freq = base_freq

    left_channel = generate_tone(left_freq, duration, sample_rate)

    # Right channel ramps from base + start_beat to base + end_beat
    right_channel = ramp_frequency(left_freq + start_beat, left_freq + end_beat, duration, sample_rate)

    stereo = np.stack([left_channel, right_channel], axis=1)
    return stereo

def apply_fade(audio, fade_duration=2.0, sample_rate=SAMPLE_RATE):
    """Apply fade in/out to avoid clicks"""
    fade_samples = int(fade_duration * sample_rate)

    # Fade in
    fade_in = np.linspace(0, 1, fade_samples)
    audio[:fade_samples] *= fade_in[:, np.newaxis] if len(audio.shape) > 1 else fade_in

    # Fade out
    fade_out = np.linspace(1, 0, fade_samples)
    audio[-fade_samples:] *= fade_out[:, np.newaxis] if len(audio.shape) > 1 else fade_out

    return audio

def normalize_audio(audio, target_amplitude=0.3):
    """Normalize audio to target amplitude (30% of max for mixing with voice)"""
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio * (target_amplitude / max_val)
    return audio

def create_garden_of_eden_binaural_track():
    """
    Create the complete binaural beat track for Garden of Eden

    Section breakdown (approximate times - adjust to match your voice track):
    0:00-2:30   Pre-Talk (no binaural)
    2:30-7:00   Induction (12→6 Hz with 174 Hz carrier)
    7:00-12:00  Meadow (6 Hz with 396 Hz carrier)
    12:00-15:30 Serpent (7.5 Hz with 528 Hz carrier)
    15:30-19:00 Tree of Life (7.83 Hz with chakra tones cycling)
    19:00-21:30 Divine (8 Hz with 963 Hz carrier)
    21:30-23:00 Return (8→12 Hz with 432 Hz carrier)
    23:00-27:00 Anchors (10 Hz with 432 Hz carrier)
    """

    print("=" * 70)
    print("   Garden of Eden - Binaural Beat Generator")
    print("   Creating Theta-wave hypnotic soundscape")
    print("=" * 70)
    print()

    sections = []

    # Section 1: Pre-Talk (2:30 - no binaural, silence)
    print("🔇 Section 1: Pre-Talk (2:30) - Silence")
    silence = np.zeros((int(2.5 * 60 * SAMPLE_RATE), 2))
    sections.append(silence)

    # Section 2: Induction (4:30 - 12 Hz → 6 Hz transition, 174 Hz carrier)
    print("🌀 Section 2: Induction (4:30) - 12→6 Hz ramp, 174 Hz carrier")
    induction = generate_binaural_ramp(174, 12, 6, 4.5 * 60)
    induction = apply_fade(induction, fade_duration=3.0)
    sections.append(induction)

    # Section 3a: Meadow of Innocence (5:00 - 6 Hz, 396 Hz carrier)
    print("🦌 Section 3a: Meadow (5:00) - 6 Hz, 396 Hz carrier")
    meadow = generate_binaural_beat(396, 6, 5.0 * 60)
    sections.append(meadow)

    # Section 3b: Serpent Wisdom (3:30 - 7.5 Hz, 528 Hz carrier)
    print("🐍 Section 3b: Serpent (3:30) - 7.5 Hz, 528 Hz carrier")
    serpent = generate_binaural_beat(528, 7.5, 3.5 * 60)
    sections.append(serpent)

    # Section 3c: Tree of Life (3:30 - 7.83 Hz, 639 Hz carrier - heart chakra)
    print("🌳 Section 3c: Tree of Life (3:30) - 7.83 Hz, 639 Hz carrier")
    tree = generate_binaural_beat(639, 7.83, 3.5 * 60)
    sections.append(tree)

    # Section 3d: Divine Presence (2:30 - 8 Hz, 963 Hz carrier)
    print("✨ Section 3d: Divine (2:30) - 8 Hz, 963 Hz carrier")
    divine = generate_binaural_beat(963, 8, 2.5 * 60)
    sections.append(divine)

    # Section 4: Return (1:30 - 8 Hz → 12 Hz transition, 432 Hz carrier)
    print("🌅 Section 4: Return (1:30) - 8→12 Hz ramp, 432 Hz carrier")
    return_section = generate_binaural_ramp(432, 8, 12, 1.5 * 60)
    sections.append(return_section)

    # Section 5: Anchors (4:00 - 10 Hz, 432 Hz carrier)
    print("⚓ Section 5: Anchors (4:00) - 10 Hz, 432 Hz carrier")
    anchors = generate_binaural_beat(432, 10, 4.0 * 60)
    anchors = apply_fade(anchors, fade_duration=4.0)  # Longer fade out at end
    sections.append(anchors)

    # Concatenate all sections
    print("\n🔗 Concatenating sections...")
    full_track = np.concatenate(sections, axis=0)

    # Normalize to 30% amplitude (for mixing with voice)
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
    print(f"🎚️  Sample rate: {SAMPLE_RATE} Hz")
    print(f"🔊 Amplitude: 30% (ready for mixing with voice)")
    print()
    print("📝 Next steps:")
    print("   1. Generate your voice track using generate_audio_chunked.py")
    print("   2. Use mix_audio.py to combine voice + binaural beats")
    print("   3. Optionally add subtle nature sounds")
    print()

    return output_file

def create_simple_theta_track(duration_minutes=27):
    """
    Simplified version: Single 7.83 Hz Theta beat with 432 Hz carrier
    Great for beginners or quick production
    """
    print("=" * 70)
    print("   Garden of Eden - Simple Theta Track Generator")
    print("   7.83 Hz (Schumann) + 432 Hz carrier")
    print("=" * 70)
    print()

    duration = duration_minutes * 60

    print(f"🌊 Generating {duration_minutes} minute Theta track...")
    audio = generate_binaural_beat(432, 7.83, duration)

    print("🎚️  Applying fade in/out...")
    audio = apply_fade(audio, fade_duration=5.0)

    print("📊 Normalizing to 30% amplitude...")
    audio = normalize_audio(audio, target_amplitude=0.3)

    # Convert to 16-bit PCM
    audio_int16 = np.int16(audio * 32767)

    output_file = "simple_theta_track.wav"
    print(f"💾 Saving to {output_file}...")
    wavfile.write(output_file, SAMPLE_RATE, audio_int16)

    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

    print()
    print("✅ Simple Theta track created!")
    print(f"📁 File: {output_file}")
    print(f"📊 Size: {file_size_mb:.2f} MB")
    print(f"⏱️  Duration: {duration_minutes} minutes")
    print()

    return output_file

if __name__ == "__main__":
    import sys

    print()
    print("Choose generation mode:")
    print("  1. Full multi-section binaural track (recommended)")
    print("  2. Simple single-frequency Theta track (easier)")
    print()

    if len(sys.argv) > 1 and sys.argv[1] == "simple":
        mode = "2"
    else:
        mode = input("Enter choice (1 or 2, default=1): ").strip() or "1"

    print()

    if mode == "2":
        create_simple_theta_track()
    else:
        create_garden_of_eden_binaural_track()

    print("🎧 Ready to mix with your voice track!")
    print()
