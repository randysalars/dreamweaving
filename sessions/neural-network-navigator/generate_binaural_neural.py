#!/usr/bin/env python3
"""
Generate Binaural Beats for Neural Network Navigator
Based on binaural_frequency_map.json with gamma burst at 18:45
"""

import numpy as np
from scipy.io import wavfile
import json

SAMPLE_RATE = 48000
AMPLITUDE = 0.3  # 30% for mixing with voice
BASE_CARRIER = 200  # Hz

def load_frequency_map(json_file):
    """Load the frequency map from JSON"""
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

def generate_gamma_burst(carrier_freq, gamma_freq, duration=3, sample_rate=SAMPLE_RATE):
    """Generate intense 40 Hz gamma burst for insight moment"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Gamma binaural beat
    left_freq = carrier_freq - (gamma_freq / 2)
    right_freq = carrier_freq + (gamma_freq / 2)

    left_tone = np.sin(2 * np.pi * left_freq * t)
    right_tone = np.sin(2 * np.pi * right_freq * t)

    # Envelope: quick fade in, sustain, quick fade out
    fade_in_samples = int(0.2 * sample_rate)
    fade_out_samples = int(0.5 * sample_rate)

    envelope = np.ones(len(t))
    envelope[:fade_in_samples] = np.linspace(0, 1, fade_in_samples)
    envelope[-fade_out_samples:] = np.linspace(1, 0, fade_out_samples)

    # Apply envelope and slight volume boost for impact
    left_tone = left_tone * envelope * AMPLITUDE * 1.2
    right_tone = right_tone * envelope * AMPLITUDE * 1.2

    stereo = np.stack([left_tone, right_tone], axis=1)
    return stereo

def interpolate_frequency(start_freq, end_freq, progress, transition_type='linear'):
    """Interpolate between two frequencies"""
    if transition_type == 'linear_descent' or transition_type == 'smooth_descent':
        return start_freq + (end_freq - start_freq) * progress
    elif transition_type == 'logarithmic_descent' or transition_type == 'logarithmic':
        # Logarithmic feels more natural for descent
        if start_freq > 0 and end_freq > 0:
            return start_freq * ((end_freq / start_freq) ** progress)
        else:
            return start_freq + (end_freq - start_freq) * progress
    else:  # hold or default
        return start_freq

def generate_full_binaural_track(freq_map):
    """Generate complete 28-minute binaural track"""
    print("Generating complete binaural beat track...")

    duration_seconds = freq_map['duration_seconds']
    carrier_freq = freq_map['base_carrier_frequency']

    # Initialize empty array
    total_samples = int(SAMPLE_RATE * duration_seconds)
    full_track = np.zeros((total_samples, 2))

    current_sample = 0

    # Process each frequency event
    for event_idx, event in enumerate(freq_map['frequency_events']):
        start_time = event['timestamp']
        duration = event['duration']
        freq_start = event['frequency_start']
        freq_end = event['frequency_end']
        transition_type = event.get('transition_type', 'linear')

        print(f"  Section {event_idx + 1}/{len(freq_map['frequency_events'])}: "
              f"{start_time}s-{start_time+duration}s, {freq_start}Hz→{freq_end}Hz")

        # Check for gamma burst
        gamma_burst = event.get('gamma_burst')

        if gamma_burst and gamma_burst.get('enabled'):
            # Split this section around the gamma burst
            gamma_time = gamma_burst['timestamp']
            gamma_duration = gamma_burst['duration']
            gamma_freq = gamma_burst['frequency']

            # Part 1: Before gamma burst
            pre_gamma_duration = gamma_time - start_time
            if pre_gamma_duration > 0:
                segment_samples = int(SAMPLE_RATE * pre_gamma_duration)
                segment = np.zeros((segment_samples, 2))

                # Generate with frequency progression
                for i in range(segment_samples):
                    t = i / SAMPLE_RATE
                    progress = i / segment_samples
                    beat_freq = interpolate_frequency(freq_start, freq_end, progress, transition_type)

                    left_freq = carrier_freq - (beat_freq / 2)
                    right_freq = carrier_freq + (beat_freq / 2)

                    segment[i, 0] = np.sin(2 * np.pi * left_freq * t) * AMPLITUDE
                    segment[i, 1] = np.sin(2 * np.pi * right_freq * t) * AMPLITUDE

                end_sample = current_sample + segment_samples
                full_track[current_sample:end_sample] = segment
                current_sample = end_sample

            # Part 2: Gamma burst (CRITICAL)
            print(f"    ⚡ GAMMA BURST at {gamma_time}s: {gamma_freq}Hz for {gamma_duration}s")
            gamma_segment = generate_gamma_burst(carrier_freq, gamma_freq, gamma_duration)
            gamma_samples = len(gamma_segment)
            end_sample = current_sample + gamma_samples
            full_track[current_sample:end_sample] = gamma_segment
            current_sample = end_sample

            # Part 3: After gamma burst
            post_gamma_duration = (start_time + duration) - (gamma_time + gamma_duration)
            if post_gamma_duration > 0:
                segment_samples = int(SAMPLE_RATE * post_gamma_duration)
                segment = np.zeros((segment_samples, 2))

                for i in range(segment_samples):
                    t = i / SAMPLE_RATE
                    progress = i / segment_samples
                    beat_freq = interpolate_frequency(freq_start, freq_end, progress, transition_type)

                    left_freq = carrier_freq - (beat_freq / 2)
                    right_freq = carrier_freq + (beat_freq / 2)

                    segment[i, 0] = np.sin(2 * np.pi * left_freq * t) * AMPLITUDE
                    segment[i, 1] = np.sin(2 * np.pi * right_freq * t) * AMPLITUDE

                end_sample = current_sample + segment_samples
                full_track[current_sample:end_sample] = segment
                current_sample = end_sample

        else:
            # Standard section without gamma burst
            segment_samples = int(SAMPLE_RATE * duration)
            segment = np.zeros((segment_samples, 2))

            for i in range(segment_samples):
                t = i / SAMPLE_RATE
                progress = i / segment_samples
                beat_freq = interpolate_frequency(freq_start, freq_end, progress, transition_type)

                left_freq = carrier_freq - (beat_freq / 2)
                right_freq = carrier_freq + (beat_freq / 2)

                segment[i, 0] = np.sin(2 * np.pi * left_freq * t) * AMPLITUDE
                segment[i, 1] = np.sin(2 * np.pi * right_freq * t) * AMPLITUDE

            end_sample = current_sample + segment_samples
            full_track[current_sample:end_sample] = segment
            current_sample = end_sample

    # Fade in/out
    fade_in_samples = int(5 * SAMPLE_RATE)
    fade_out_samples = int(8 * SAMPLE_RATE)

    fade_in_curve = np.linspace(0, 1, fade_in_samples)
    full_track[:fade_in_samples, 0] *= fade_in_curve
    full_track[:fade_in_samples, 1] *= fade_in_curve

    fade_out_curve = np.linspace(1, 0, fade_out_samples)
    full_track[-fade_out_samples:, 0] *= fade_out_curve
    full_track[-fade_out_samples:, 1] *= fade_out_curve

    return full_track

def main():
    print("=" * 60)
    print("NEURAL NETWORK NAVIGATOR - Binaural Beat Generation")
    print("=" * 60)

    # Load frequency map
    freq_map_file = "binaural_frequency_map.json"
    print(f"\nLoading frequency map from {freq_map_file}...")
    freq_map = load_frequency_map(freq_map_file)

    duration_min = freq_map['duration_seconds'] / 60
    print(f"Duration: {duration_min:.1f} minutes ({freq_map['duration_seconds']} seconds)")
    print(f"Base carrier: {freq_map['base_carrier_frequency']} Hz")
    print(f"Frequency events: {len(freq_map['frequency_events'])}")

    # Generate track
    print(f"\nGenerating binaural beat track...")
    full_track = generate_full_binaural_track(freq_map)

    # Convert to 16-bit PCM
    print(f"\nConverting to 16-bit PCM...")
    full_track_int = (full_track * 32767).astype(np.int16)

    # Save
    output_file = "working_files/binaural_beats_neural_navigator.wav"
    print(f"Saving to {output_file}...")
    wavfile.write(output_file, SAMPLE_RATE, full_track_int)

    file_size = len(full_track_int) * 2 * 2 / (1024 * 1024)  # 2 channels, 2 bytes per sample
    print(f"\n✓ Binaural beats generated successfully!")
    print(f"  Output: {output_file}")
    print(f"  Size: {file_size:.1f} MB")
    print(f"  Duration: {duration_min:.1f} minutes")
    print(f"\n⚡ CRITICAL: Gamma burst at 18:45 (1125s) - 40 Hz for 3 seconds")
    print(f"\nNext: Generate images")

    return 0

if __name__ == '__main__':
    exit(main())
