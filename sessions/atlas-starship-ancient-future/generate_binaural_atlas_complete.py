#!/usr/bin/env python3
"""
Generate Complete Binaural Beats for ATLAS Starship Ancient Future
Duration: 1887 seconds (~31.45 minutes)
Based on MANIFEST with gamma flash at 20:40
"""

import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 48000
AMPLITUDE = 0.25  # 25% for mixing with voice
BASE_CARRIER = 432  # Hz - sacred frequency

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

def generate_gamma_flash(carrier_freq, gamma_freq=40, duration=3, sample_rate=SAMPLE_RATE):
    """Generate intense 40 Hz gamma burst for insight moment at 20:40"""
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
    left_tone = left_tone * envelope * AMPLITUDE * 1.3
    right_tone = right_tone * envelope * AMPLITUDE * 1.3

    stereo = np.stack([left_tone, right_tone], axis=1)
    return stereo

def generate_full_binaural_track(total_duration=1887):
    """
    Generate complete binaural track matching MANIFEST.YAML:

    Sections from manifest:
    - 0-150s: offset_hz 0 (silence/near-zero for pretalk)
    - 150-540s: offset_hz 6.0 (theta gateway)
    - 540-1200s: offset_hz 6.0 (steady theta)
    - 1200-1460s: offset_hz 2.8 (delta drift blend)
    - 1460-1819s: offset_hz 8.0 (gentle return)

    Plus gamma flash at 1240s (20:40) for 3 seconds
    """
    print(f"Generating {total_duration} second binaural beat track...")
    print("Following MANIFEST.YAML specifications\n")

    # Define sections from manifest (offset_hz is the binaural beat frequency)
    sections = [
        {"start": 0, "end": 150, "beat_hz": 0.5, "name": "Pretalk (near-silence)"},
        {"start": 150, "end": 540, "beat_hz": 6.0, "name": "Induction (theta gateway)"},
        {"start": 540, "end": 1200, "beat_hz": 6.0, "name": "Journey start (steady theta)"},
        {"start": 1200, "end": 1460, "beat_hz": 2.8, "name": "Deep journey (delta blend)"},
        {"start": 1460, "end": 1819, "beat_hz": 8.0, "name": "Integration/Return (alpha)"},
    ]

    # Generate audio for each section
    all_audio = []
    gamma_flash_time = 1240  # 20:40 mark
    gamma_flash_duration = 3

    for section in sections:
        start = section['start']
        end = section['end']
        beat_hz = section['beat_hz']
        name = section['name']

        segment_duration = end - start
        print(f"  {start:4d}-{end:4d}s ({segment_duration:3d}s): {beat_hz:3.1f} Hz - {name}")

        # Check if gamma flash occurs in this section
        if start <= gamma_flash_time < end:
            # Split section into: before flash, flash, after flash
            before_flash = gamma_flash_time - start
            after_flash = end - (gamma_flash_time + gamma_flash_duration)

            # Before flash
            if before_flash > 0:
                audio_before = generate_binaural_segment(BASE_CARRIER, beat_hz, before_flash)
                all_audio.append(audio_before)

            # Gamma flash
            print(f"      >>> GAMMA FLASH at {gamma_flash_time}s (40 Hz for {gamma_flash_duration}s)")
            gamma = generate_gamma_flash(BASE_CARRIER, 40, gamma_flash_duration)
            all_audio.append(gamma)

            # After flash
            if after_flash > 0:
                audio_after = generate_binaural_segment(BASE_CARRIER, beat_hz, after_flash)
                all_audio.append(audio_after)
        else:
            # Normal segment
            audio = generate_binaural_segment(BASE_CARRIER, beat_hz, segment_duration)
            all_audio.append(audio)

    # Handle any remaining time after the schedule ends
    last_end = sections[-1]['end']
    if total_duration > last_end:
        remaining = total_duration - last_end
        last_beat = sections[-1]['beat_hz']
        print(f"  {last_end:4d}-{total_duration:4d}s ({remaining:3d}s): {last_beat:3.1f} Hz - Extension")
        extension = generate_binaural_segment(BASE_CARRIER, last_beat, remaining)
        all_audio.append(extension)

    # Concatenate all segments
    print("\n💫 Concatenating segments...")
    full_track = np.vstack(all_audio)

    return full_track

def main():
    output_file = "working_files/binaural_atlas_complete.wav"

    print("=" * 70)
    print("ATLAS COMPLETE BINAURAL BEAT GENERATOR")
    print("Includes varied frequencies + 40 Hz gamma flash at 20:40")
    print("=" * 70)
    print()

    # Generate the track
    audio = generate_full_binaural_track()

    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)

    # Save
    print(f"\n💾 Saving to {output_file}...")
    wavfile.write(output_file, SAMPLE_RATE, audio_int16)

    duration_min = len(audio) / SAMPLE_RATE / 60
    print(f"✅ Complete! Duration: {duration_min:.2f} minutes")
    print("=" * 70)
    print("\n📊 Summary:")
    print("  • 432 Hz carrier frequency (sacred)")
    print("  • Varied binaural beats: 0.5 Hz → 6 Hz → 2.8 Hz → 8 Hz")
    print("  • 40 Hz gamma flash at 20:40 for cosmic insight")
    print("  • 48kHz stereo, ready for mixing")

if __name__ == "__main__":
    main()
