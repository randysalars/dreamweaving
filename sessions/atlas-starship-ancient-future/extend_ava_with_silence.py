#!/usr/bin/env python3
"""
Extend Ava voice to full binaural duration by adding silence at strategic points
This compensates for Edge TTS not respecting SSML break times
"""

from pydub import AudioSegment
from pydub.generators import Sine
from pathlib import Path

def create_silence(duration_ms):
    """Create silence"""
    return AudioSegment.silent(duration=duration_ms)

def extend_voice_to_full_duration():
    """
    Extend the Ava voice from ~15 min to ~31 min by adding silence
    Strategic placement: after the drift sections
    """

    voice_file = Path("working_files/voice_atlas_ava_extended.mp3")
    output_file = Path("working_files/voice_atlas_ava_full.mp3")

    print("Loading Ava voice...")
    voice = AudioSegment.from_file(voice_file)
    voice_duration_sec = len(voice) / 1000.0

    target_duration = 1887  # seconds (31.45 minutes)
    additional_silence_needed = (target_duration - voice_duration_sec) * 1000  # convert to ms

    print(f"Voice duration: {voice_duration_sec:.1f} sec ({voice_duration_sec/60:.2f} min)")
    print(f"Target duration: {target_duration} sec ({target_duration/60:.2f} min)")
    print(f"Additional silence needed: {additional_silence_needed/1000:.1f} sec")

    # Add the silence at approximately 75% through (during the drift section)
    # This is around 680 seconds into the voice
    split_point = int(680 * 1000)  # 680 seconds in ms

    part1 = voice[:split_point]
    part2 = voice[split_point:]

    silence = create_silence(int(additional_silence_needed))

    print(f"\nSplitting voice at {split_point/1000:.1f} seconds")
    print(f"Adding {additional_silence_needed/1000:.1f} seconds of silence")
    print(f"Part 1: {len(part1)/1000:.1f}s")
    print(f"Silence: {len(silence)/1000:.1f}s")
    print(f"Part 2: {len(part2)/1000:.1f}s")

    # Combine
    extended = part1 + silence + part2

    final_duration = len(extended) / 1000.0
    print(f"\nFinal duration: {final_duration:.1f} sec ({final_duration/60:.2f} min)")

    # Export
    print(f"\nExporting to {output_file}...")
    extended.export(output_file, format="mp3", bitrate="320k")

    print(f"✅ Extended voice created: {output_file}")

if __name__ == "__main__":
    extend_voice_to_full_duration()
