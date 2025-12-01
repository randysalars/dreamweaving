#!/usr/bin/env python3
"""
Generate Binaural Beats for ATLAS Starship Ancient Future
Duration: 1887 seconds (~31.45 minutes)
Based on manifest beat schedule with 432 Hz carrier
"""

import numpy as np
from scipy.io import wavfile
import json

SAMPLE_RATE = 48000
AMPLITUDE = 0.25  # 25% for mixing with voice
BASE_CARRIER = 432  # Hz - sacred frequency

def load_beat_schedule(json_file):
    """Load the beat schedule from JSON"""
    with open(json_file, 'r') as f:
        return json.load(f)

def generate_binaural_segment(carrier_freq, beat_freq, duration, sample_rate=SAMPLE_RATE):
    """Generate standard binaural beat for a duration"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Left and right frequencies
    left_freq = carrier_freq - (beat_freq / 2)
    right_freq = carrier_freq + (beat_freq / 2)

    # Generate tones
    left_tone = np.sin(2 * np.pi * left_freq * t) * AMPLITUDE
    right_tone = np.sin(2 * np.pi * right_freq * t) * AMPLITUDE

    # Create stereo
    stereo = np.stack([left_tone, right_tone], axis=1)
    return stereo

def interpolate_frequency(start_freq, end_freq, progress):
    """Linear interpolation between two frequencies"""
    return start_freq + (end_freq - start_freq) * progress

def generate_full_binaural_track(schedule_file, total_duration=1887):
    """Generate complete binaural track matching voice duration"""
    print(f"Generating {total_duration} second binaural beat track...")

    schedule = load_beat_schedule(schedule_file)

    # Generate audio for each scheduled segment
    all_audio = []

    for segment in schedule:
        start = segment['start']
        end = segment['end']
        freq_start = segment['freq_start']
        freq_end = segment['freq_end']

        segment_duration = end - start
        print(f"  Segment {start}-{end}s: {freq_start} Hz → {freq_end} Hz")

        # Generate with frequency sweep
        t = np.linspace(0, segment_duration, int(SAMPLE_RATE * segment_duration), False)

        # For each sample, calculate the interpolated frequency
        left_channel = np.zeros(len(t))
        right_channel = np.zeros(len(t))

        for i, time in enumerate(t):
            progress = time / segment_duration
            beat_freq = interpolate_frequency(freq_start, freq_end, progress)

            left_freq = BASE_CARRIER - (beat_freq / 2)
            right_freq = BASE_CARRIER + (beat_freq / 2)

            left_channel[i] = np.sin(2 * np.pi * left_freq * time) * AMPLITUDE
            right_channel[i] = np.sin(2 * np.pi * right_freq * time) * AMPLITUDE

        stereo = np.stack([left_channel, right_channel], axis=1)
        all_audio.append(stereo)

    # Handle any remaining time after the schedule ends
    last_end = schedule[-1]['end']
    if total_duration > last_end:
        remaining = total_duration - last_end
        last_freq = schedule[-1]['freq_end']
        print(f"  Extending {remaining}s at {last_freq} Hz")
        extension = generate_binaural_segment(BASE_CARRIER, last_freq, remaining)
        all_audio.append(extension)

    # Concatenate all segments
    print("Concatenating segments...")
    full_track = np.vstack(all_audio)

    return full_track

def main():
    schedule_file = "beat_schedule.json"
    output_file = "working_files/binaural_atlas.wav"

    print("=" * 60)
    print("ATLAS Binaural Beat Generator")
    print("=" * 60)

    # Generate the track
    audio = generate_full_binaural_track(schedule_file)

    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)

    # Save
    print(f"\n💾 Saving to {output_file}...")
    wavfile.write(output_file, SAMPLE_RATE, audio_int16)

    duration_min = len(audio) / SAMPLE_RATE / 60
    print(f"✅ Complete! Duration: {duration_min:.2f} minutes")
    print("=" * 60)

if __name__ == "__main__":
    main()
