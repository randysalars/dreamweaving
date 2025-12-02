#!/usr/bin/env python3
"""
Universal Dreamweaving: Chunked Audio Generator

Turns large SSML files into audio by chunking under the provider byte limits.
Keep imports light so it can be reused as a module by other workflows.

Requirements:
    pip install google-cloud-texttospeech pydub

Usage:
    python3 generate_audio_chunked.py input.ssml output.mp3 --voice en-US-Neural2-A
"""

import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

def print_header():
    """Print a simple header"""
    print("=" * 70)
    print("   Dreamweaving: Chunked Audio Generator")
    print("   SSML → Audio (Large File Support)")
    print("=" * 70)
    print()

def split_ssml_into_chunks(ssml_content, max_bytes=4500):
    """
    Split SSML content into chunks that are under max_bytes.
    Splits at prosody boundaries first, then at break tags within prosody sections.
    Each chunk is a complete, valid SSML document.
    """
    # Extract the content between <speak> tags
    speak_match = re.search(r'<speak[^>]*>(.*)</speak>', ssml_content, re.DOTALL)
    if not speak_match:
        raise ValueError("Invalid SSML: No <speak> tags found")

    content = speak_match.group(1)
    speak_opening = ssml_content[:speak_match.start(1)]
    speak_closing = '</speak>'

    # First, split by prosody sections (each prosody block becomes a separate unit)
    # Pattern captures: optional leading content, prosody open tag, content, prosody close tag
    prosody_pattern = r'(<prosody[^>]*>)(.*?)(</prosody>)'
    prosody_sections = []

    last_end = 0
    for match in re.finditer(prosody_pattern, content, re.DOTALL):
        # Capture any content before this prosody (like comments)
        before = content[last_end:match.start()].strip()
        if before:
            prosody_sections.append(('comment', before, None, None))

        prosody_sections.append(('prosody', match.group(2), match.group(1), match.group(3)))
        last_end = match.end()

    # Capture any trailing content
    after = content[last_end:].strip()
    if after:
        prosody_sections.append(('comment', after, None, None))

    # Now process each section
    final_chunks = []

    for section_type, inner_content, prosody_open, prosody_close in prosody_sections:
        if section_type == 'comment':
            # Comments alone - skip or attach to next chunk
            continue

        # Build a test chunk with this prosody section
        test_chunk = speak_opening + prosody_open + inner_content + prosody_close + speak_closing

        if len(test_chunk.encode('utf-8')) <= max_bytes:
            # Fits in one chunk
            final_chunks.append(test_chunk)
        else:
            # Need to split this prosody section at break points
            sub_chunks = split_prosody_section(
                inner_content, prosody_open, prosody_close,
                speak_opening, speak_closing, max_bytes
            )
            final_chunks.extend(sub_chunks)

    return final_chunks


def split_prosody_section(inner_content, prosody_open, prosody_close, speak_opening, speak_closing, max_bytes):
    """Split a prosody section that's too large by break tag boundaries"""

    # Split on break tags with pauses of 2s or more (including decimals like 2.5s, 3.0s, 4.0s)
    # Keep the break tags with the content before them
    parts = re.split(r'(<break time="[2-9](?:\.\d)?s"/>)', inner_content)

    sub_chunks = []
    current = ""

    for i, part in enumerate(parts):
        # Test if adding this part would exceed the limit
        test = speak_opening + prosody_open + current + part + prosody_close + speak_closing

        if len(test.encode('utf-8')) > max_bytes and current.strip():
            # Save current chunk and start a new one
            chunk = speak_opening + prosody_open + current + prosody_close + speak_closing
            sub_chunks.append(chunk)
            current = part
        else:
            current += part

    # Add the final chunk
    if current.strip():
        chunk = speak_opening + prosody_open + current + prosody_close + speak_closing
        sub_chunks.append(chunk)

    return sub_chunks

def synthesize_chunk(client, ssml_text, voice_name, chunk_num, total_chunks, speaking_rate, pitch, sample_rate_hz, effects_profile_id):
    """Synthesize a single chunk of SSML"""
    print(f"   🎙️  Chunk {chunk_num}/{total_chunks}: {len(ssml_text.encode('utf-8'))} bytes")
    
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
    
    # Correct gender mapping for Neural2 voices:
    # Female: C, E, F, G, H
    # Male: A, D, I, J
    voice_letter = voice_name.split('-')[-1] if '-' in voice_name else voice_name[-1]
    female_voices = {'C', 'E', 'F', 'G', 'H'}
    is_female = voice_letter in female_voices

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE if is_female else texttospeech.SsmlVoiceGender.MALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speaking_rate,
        pitch=pitch,
        effects_profile_id=effects_profile_id or ["headphone-class-device"],
        sample_rate_hertz=sample_rate_hz
    )
    
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    
    return response.audio_content

def concatenate_audio_chunks(chunk_files, output_file):
    """Concatenate multiple MP3 files into one.

    Note: Temp file cleanup is handled by tempfile.TemporaryDirectory context manager.
    """
    print(f"\n🔗 Concatenating {len(chunk_files)} audio chunks...")

    combined = AudioSegment.empty()

    for i, chunk_file in enumerate(chunk_files, 1):
        print(f"   Adding chunk {i}/{len(chunk_files)}...")
        audio = AudioSegment.from_mp3(chunk_file)
        combined += audio

    # Export final file
    print(f"💾 Exporting final audio to: {output_file}")
    combined.export(output_file, format="mp3", bitrate="128k")

    return combined

def synthesize_ssml_file_chunked(
    ssml_filepath,
    output_filepath,
    voice_name="en-US-Neural2-A",
    speaking_rate=0.85,
    pitch=-2.0,
    max_bytes=5000,
    sample_rate_hz=24000,
    effects_profile_id=None
):
    """
    Synthesizes speech from large SSML file by chunking it.
    """
    
    # Validate input file exists
    if not os.path.exists(ssml_filepath):
        print(f"❌ Error: Input file not found: {ssml_filepath}")
        sys.exit(1)
    
    # Initialize the Text-to-Speech client
    try:
        client = texttospeech.TextToSpeechClient()
    except Exception as e:
        print(f"❌ Error: Could not initialize Google Cloud TTS client.")
        print(f"   Make sure you've run: gcloud auth application-default login")
        print(f"   Error details: {e}")
        sys.exit(1)

    # Read SSML content from file
    print(f"📖 Reading SSML from: {ssml_filepath}")
    with open(ssml_filepath, 'r', encoding='utf-8') as f:
        ssml_content = f.read()
    
    # Calculate character count
    char_count = len(ssml_content)
    byte_count = len(ssml_content.encode('utf-8'))
    print(f"   Character count: {char_count:,}")
    print(f"   Byte count: {byte_count:,}")
    
    # Check if chunking is needed
    if byte_count <= max_bytes:
        print(f"   ✓ File is under 5000 bytes, no chunking needed")
        chunks = [ssml_content]
    else:
        print(f"   ⚠️  File exceeds 5000 byte limit, chunking required")
        print(f"📦 Splitting into manageable chunks...")
        chunks = split_ssml_into_chunks(ssml_content, max_bytes=max_bytes)
        print(f"   ✓ Created {len(chunks)} chunks")
        
        # Validate chunk sizes
        for i, chunk in enumerate(chunks, 1):
            chunk_bytes = len(chunk.encode('utf-8'))
            if chunk_bytes > 5000:
                print(f"   ⚠️  Warning: Chunk {i} is {chunk_bytes} bytes (may fail)")
    
    # Synthesize each chunk
    print(f"\n🎙️  Generating audio with voice: {voice_name}")
    print(f"   Speaking rate: {speaking_rate:.2f}x")
    print(f"   Pitch: {pitch:.1f} semitones")
    print(f"\n⏳ Synthesizing {len(chunks)} chunk(s)... (this may take 1-2 minutes)")
    print()

    # Use temporary directory for chunk files (auto-cleaned on exit)
    with tempfile.TemporaryDirectory(prefix="dreamweaving_chunks_") as tmpdir:
        tmpdir_path = Path(tmpdir)
        chunk_files = []

        try:
            for i, chunk in enumerate(chunks, 1):
                audio_content = synthesize_chunk(
                    client,
                    chunk,
                    voice_name,
                    i,
                    len(chunks),
                    speaking_rate,
                    pitch,
                    sample_rate_hz,
                    effects_profile_id,
                )

                # Save chunk to temporary file in temp directory
                chunk_file = tmpdir_path / f"chunk_{i:03d}.mp3"
                with open(chunk_file, 'wb') as out:
                    out.write(audio_content)
                chunk_files.append(str(chunk_file))

        except Exception as e:
            print(f"\n❌ Error during synthesis: {e}")
            # Temp directory is auto-cleaned by context manager
            sys.exit(1)

        # Concatenate all chunks if more than one
        if len(chunk_files) == 1:
            # Copy single file (can't rename across filesystems)
            shutil.copy2(chunk_files[0], output_filepath)
        else:
            # Concatenate multiple files
            concatenate_audio_chunks(chunk_files, output_filepath)
    
    # Calculate file size and duration
    file_size_mb = os.path.getsize(output_filepath) / (1024 * 1024)
    
    # Try to get duration if pydub worked
    try:
        audio = AudioSegment.from_mp3(output_filepath)
        duration_minutes = len(audio) / 1000 / 60
        duration_str = f"{duration_minutes:.1f} minutes"
    except (OSError, IOError, CouldntDecodeError):
        duration_str = "~25-30 minutes (estimated)"
    
    print()
    print("=" * 70)
    print("✅ SUCCESS! Audio generated successfully!")
    print("=" * 70)
    print(f"📁 Output file: {output_filepath}")
    print(f"📊 File size: {file_size_mb:.2f} MB")
    print(f"⏱️  Duration: {duration_str}")
    print(f"🎧 Optimized for: Headphone listening")
    print(f"🎙️  Chunks processed: {len(chunks)}")
    print()
    print("💡 Tips:")
    print("   • Listen with headphones in a quiet space")
    print("   • Test pronunciation of 'path-working' (should be two words)")
    print("   • If too slow, regenerate with speakingRate=0.90")
    print("   • If too fast, regenerate with speakingRate=0.80")
    print()

def main():
    """Main execution function"""
    import argparse

    # Import validation utilities
    try:
        from scripts.utilities.validation import (
            validate_file_exists,
            validate_output_path,
            validate_speaking_rate,
            validate_pitch,
        )
    except ImportError:
        # Fallback if not installed as package
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        try:
            from scripts.utilities.validation import (
                validate_file_exists,
                validate_output_path,
                validate_speaking_rate,
                validate_pitch,
            )
        except ImportError:
            # Use basic validation if module not available
            validate_file_exists = str
            validate_output_path = str
            validate_speaking_rate = float
            validate_pitch = float

    print_header()

    parser = argparse.ArgumentParser(description="Chunked SSML → audio generator")
    parser.add_argument("ssml_file", type=validate_file_exists, help="Path to input SSML file")
    parser.add_argument("output_file", type=validate_output_path, help="Path to output MP3 file")
    parser.add_argument("--voice", default="en-US-Neural2-A", help="Voice name (default: en-US-Neural2-A)")
    parser.add_argument("--speaking-rate", type=validate_speaking_rate, default=0.85, help="Speaking rate multiplier (0.25-4.0, default: 0.85)")
    parser.add_argument("--pitch", type=validate_pitch, default=-2.0, help="Pitch shift in semitones (-20 to +20, default: -2.0)")
    parser.add_argument("--max-bytes", type=int, default=5000, help="Max bytes per chunk before splitting (default: 5000)")
    parser.add_argument("--sample-rate", type=int, default=24000, choices=[16000, 22050, 24000, 44100, 48000], help="Sample rate in Hz (default: 24000)")
    parser.add_argument("--effects-profile", default=None, nargs="*", help="Effects profile IDs (default: headphone-class-device)")

    args = parser.parse_args()

    # Check for pydub
    try:
        import pydub  # noqa: F401
    except ImportError:
        print("❌ Error: pydub is required for concatenating audio chunks")
        print()
        print("Install with:")
        print("   pip install pydub")
        print()
        print("Also requires ffmpeg:")
        print("   Ubuntu/Debian: sudo apt install ffmpeg")
        print("   Mac: brew install ffmpeg")
        print()
        sys.exit(1)

    synthesize_ssml_file_chunked(
        str(args.ssml_file),
        str(args.output_file),
        voice_name=args.voice,
        speaking_rate=args.speaking_rate,
        pitch=args.pitch,
        max_bytes=args.max_bytes,
        sample_rate_hz=args.sample_rate,
        effects_profile_id=args.effects_profile,
    )

if __name__ == "__main__":
    main()
