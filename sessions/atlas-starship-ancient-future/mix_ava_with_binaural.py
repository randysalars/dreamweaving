#!/usr/bin/env python3
"""
Mix Ava voice with binaural beats
Voice is shorter than binaural, so we pad binaural to silence after voice ends
"""

from pydub import AudioSegment
from pathlib import Path

def mix_audio():
    print("=" * 70)
    print("ATLAS: Mixing Ava Voice with Binaural Beats")
    print("=" * 70)
    print()

    # Load files
    voice_file = Path("working_files/voice_atlas_ava.mp3")
    binaural_file = Path("working_files/binaural_atlas_complete.wav")
    output_file = Path("working_files/atlas_ava_mixed.wav")

    print(f"Loading voice: {voice_file}")
    voice = AudioSegment.from_file(voice_file)
    voice_duration = len(voice) / 1000.0

    print(f"Loading binaural: {binaural_file}")
    binaural = AudioSegment.from_file(binaural_file)
    binaural_duration = len(binaural) / 1000.0

    print(f"\nDurations:")
    print(f"  Voice:    {voice_duration:.1f} sec ({voice_duration/60:.2f} min)")
    print(f"  Binaural: {binaural_duration:.1f} sec ({binaural_duration/60:.2f} min)")

    # Trim binaural to match voice duration (binaural is longer)
    print(f"\nTrimming binaural to match voice duration...")
    binaural_trimmed = binaural[:len(voice)]

    # Apply volume adjustments per manifest
    # voice_lufs: -16 (already at source from edge-tts)
    # binaural_lufs: -28 (reduce by ~12 dB)
    print(f"\nAdjusting levels:")
    print(f"  Voice:    0 dB (no change)")
    print(f"  Binaural: -12 dB")
    binaural_adjusted = binaural_trimmed - 12

    # Mix
    print(f"\nMixing...")
    mixed = voice.overlay(binaural_adjusted)

    # Export
    print(f"Exporting to {output_file}...")
    mixed.export(
        output_file,
        format="wav",
        parameters=[
            "-ar", "48000",
            "-ac", "2"
        ]
    )

    final_duration = len(mixed) / 1000.0
    print(f"\n✅ Mixed audio created: {output_file}")
    print(f"   Duration: {final_duration:.1f} sec ({final_duration/60:.2f} min)")
    print("=" * 70)

if __name__ == "__main__":
    mix_audio()
