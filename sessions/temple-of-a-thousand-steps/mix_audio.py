#!/usr/bin/env python3
"""
Mix Voice and Binaural Beats for Temple of a Thousand Steps

Combines the generated voice track with binaural beats.

Requirements:
    pip install pydub

Usage:
    python mix_audio.py voice.mp3 binaural_track.wav output.mp3
"""

from pydub import AudioSegment
import sys
import os


def mix_tracks(voice_file, binaural_file, output_file, voice_volume=0, binaural_volume=-10):
    """
    Mix voice and binaural tracks

    Args:
        voice_file: Path to voice audio (MP3)
        binaural_file: Path to binaural beats (WAV)
        output_file: Path for output file (MP3)
        voice_volume: Volume adjustment for voice in dB (0 = no change)
        binaural_volume: Volume adjustment for binaural in dB (-10 = 30% amplitude)
    """

    print("=" * 70)
    print("   Temple of a Thousand Steps - Audio Mixer")
    print("   Combining voice + binaural beats")
    print("=" * 70)
    print()

    # Load audio files
    print(f"Loading voice track: {voice_file}")
    voice = AudioSegment.from_file(voice_file)

    print(f"Loading binaural track: {binaural_file}")
    binaural = AudioSegment.from_file(binaural_file)

    # Get durations
    voice_duration = len(voice) / 1000
    binaural_duration = len(binaural) / 1000

    print(f"\n  Voice duration: {voice_duration / 60:.1f} minutes")
    print(f"  Binaural duration: {binaural_duration / 60:.1f} minutes")

    # Match durations
    if len(binaural) < len(voice):
        print(f"\n  Binaural track is shorter. Extending with silence...")
        silence_needed = len(voice) - len(binaural)
        binaural = binaural + AudioSegment.silent(duration=silence_needed)
    elif len(binaural) > len(voice):
        print(f"\n  Binaural track is longer. Trimming...")
        binaural = binaural[:len(voice)]

    # Adjust volumes
    print(f"\n  Adjusting volumes...")
    print(f"    Voice: {voice_volume:+.1f} dB")
    print(f"    Binaural: {binaural_volume:+.1f} dB")

    voice = voice + voice_volume
    binaural = binaural + binaural_volume

    # Mix (overlay)
    print(f"\n  Mixing tracks...")
    mixed = voice.overlay(binaural)

    # Export
    print(f"\n  Exporting to: {output_file}")
    mixed.export(
        output_file,
        format="mp3",
        bitrate="320k",
        parameters=["-q:a", "0"]
    )

    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

    print()
    print("=" * 70)
    print("SUCCESS! Mixed audio created!")
    print("=" * 70)
    print(f"  Output file: {output_file}")
    print(f"  File size: {file_size_mb:.2f} MB")
    print(f"  Duration: {len(mixed) / 1000 / 60:.1f} minutes")
    print(f"  Bitrate: 320 kbps")
    print()

    return output_file


def main():
    if len(sys.argv) < 4:
        print("Usage: python mix_audio.py <voice.mp3> <binaural.wav> <output.mp3>")
        print()
        print("Example:")
        print("  python mix_audio.py output/voice.mp3 binaural_track.wav output/final_mix.mp3")
        print()
        sys.exit(1)

    voice_file = sys.argv[1]
    binaural_file = sys.argv[2]
    output_file = sys.argv[3]

    # Validate input files exist
    if not os.path.exists(voice_file):
        print(f"Error: Voice file not found: {voice_file}")
        sys.exit(1)

    if not os.path.exists(binaural_file):
        print(f"Error: Binaural file not found: {binaural_file}")
        sys.exit(1)

    mix_tracks(voice_file, binaural_file, output_file)


if __name__ == "__main__":
    main()
