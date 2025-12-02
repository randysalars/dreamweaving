#!/usr/bin/env python3
"""
Generate voice audio from affirmations with proper chunking.

This script converts visualizations.txt to voice audio by:
1. Reading the affirmations text
2. Converting to SSML in small chunks
3. Synthesizing each chunk with Google Cloud TTS
4. Concatenating all chunks into a final audio file
"""

import os
import re
import sys
import tempfile
from pathlib import Path

from google.cloud import texttospeech
from pydub import AudioSegment


def parse_affirmations(content: str) -> list[dict]:
    """Parse affirmations text into sections with their content."""
    sections = []
    current_section = None
    current_content = []

    lines = content.split('\n')

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Check if this is a section header
        if re.match(r'^[A-Z][a-zA-Z\s]{0,20}$', line) and not line.endswith('.'):
            # Save previous section
            if current_section and current_content:
                sections.append({
                    'name': current_section,
                    'paragraphs': current_content
                })

            current_section = line
            current_content = []
            continue

        # Clean up the line
        if line.startswith('- "'):
            line = line[3:]
            if line.endswith('"'):
                line = line[:-1]
        elif line.startswith('-'):
            line = line[1:].strip()

        line = line.strip('"')

        if len(line) < 10:
            continue

        current_content.append(line)

    # Save last section
    if current_section and current_content:
        sections.append({
            'name': current_section,
            'paragraphs': current_content
        })

    return sections


def create_ssml_chunk(paragraphs: list[str], section_name: str = None, max_bytes: int = 4500) -> list[str]:
    """Create SSML chunks from paragraphs, ensuring each is under max_bytes."""
    chunks = []

    # SSML wrapper overhead
    wrapper_start = '<speak><prosody rate="0.95" pitch="-1st">'
    wrapper_end = '</prosody></speak>'
    wrapper_bytes = len(wrapper_start.encode('utf-8')) + len(wrapper_end.encode('utf-8'))

    current_content = []
    current_bytes = wrapper_bytes

    # Add section header if provided
    if section_name:
        header = f'<emphasis level="moderate">{section_name}</emphasis><break time="2s"/>'
        header_bytes = len(header.encode('utf-8'))
        if current_bytes + header_bytes < max_bytes:
            current_content.append(header)
            current_bytes += header_bytes

    for para in paragraphs:
        # Escape XML special characters
        para = para.replace('&', '&amp;')
        para = para.replace('<', '&lt;')
        para = para.replace('>', '&gt;')

        para_ssml = f'{para}<break time="1200ms"/>'
        para_bytes = len(para_ssml.encode('utf-8'))

        # Check if adding this paragraph would exceed limit
        if current_bytes + para_bytes > max_bytes:
            # Save current chunk
            if current_content:
                chunk_ssml = wrapper_start + '\n'.join(current_content) + wrapper_end
                chunks.append(chunk_ssml)

            # Start new chunk
            current_content = [para_ssml]
            current_bytes = wrapper_bytes + para_bytes
        else:
            current_content.append(para_ssml)
            current_bytes += para_bytes

    # Save last chunk
    if current_content:
        chunk_ssml = wrapper_start + '\n'.join(current_content) + wrapper_end
        chunks.append(chunk_ssml)

    return chunks


def synthesize_chunk(client, ssml_text: str, voice_name: str) -> bytes:
    """Synthesize a single SSML chunk to audio."""
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

    # Determine gender based on voice name
    # Female Neural2: C, E, F, G, H
    # Male Neural2: A, D, I, J
    female_voices = ['C', 'E', 'F', 'G', 'H']
    voice_letter = voice_name.split('-')[-1]
    is_female = voice_letter in female_voices

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE if is_female else texttospeech.SsmlVoiceGender.MALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.9,  # Slightly slower for affirmations
        pitch=-1.0,  # Slightly lower for warmth
        effects_profile_id=["headphone-class-device"],
        sample_rate_hertz=24000
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    return response.audio_content


def main():
    script_dir = Path(__file__).parent
    input_file = script_dir / 'visualizations.txt'
    output_file = script_dir / 'output' / 'affirmations_voice.mp3'

    # Create output directory
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Voice selection - Neural2-F is clear and articulate, good for affirmations
    voice_name = "en-US-Neural2-F"

    print("=" * 70)
    print("   Affirmations Voice Generator")
    print("   Text → SSML → Voice Audio")
    print("=" * 70)
    print()

    # Read input file
    print(f"📖 Reading affirmations from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse into sections
    sections = parse_affirmations(content)
    print(f"   Found {len(sections)} sections")

    # Create SSML chunks
    all_chunks = []
    for section in sections:
        chunks = create_ssml_chunk(section['paragraphs'], section['name'])
        all_chunks.extend(chunks)
        print(f"   {section['name']}: {len(chunks)} chunk(s)")

    print(f"\n📦 Total chunks to synthesize: {len(all_chunks)}")

    # Validate chunk sizes
    for i, chunk in enumerate(all_chunks, 1):
        chunk_bytes = len(chunk.encode('utf-8'))
        if chunk_bytes > 5000:
            print(f"   ⚠️  Chunk {i}: {chunk_bytes} bytes (TOO LARGE)")
        else:
            pass  # All good

    # Initialize TTS client
    print(f"\n🎙️  Initializing Google Cloud TTS with voice: {voice_name}")
    try:
        client = texttospeech.TextToSpeechClient()
    except Exception as e:
        print(f"❌ Error: Could not initialize Google Cloud TTS client.")
        print(f"   Make sure you've run: gcloud auth application-default login")
        print(f"   Error: {e}")
        sys.exit(1)

    # Synthesize all chunks
    print(f"\n⏳ Synthesizing {len(all_chunks)} chunks...")

    with tempfile.TemporaryDirectory() as temp_dir:
        chunk_files = []

        for i, chunk in enumerate(all_chunks, 1):
            chunk_bytes = len(chunk.encode('utf-8'))
            print(f"   🎙️  Chunk {i}/{len(all_chunks)}: {chunk_bytes} bytes")

            try:
                audio_content = synthesize_chunk(client, chunk, voice_name)

                # Save chunk to temp file
                chunk_file = Path(temp_dir) / f"chunk_{i:04d}.mp3"
                with open(chunk_file, 'wb') as f:
                    f.write(audio_content)

                chunk_files.append(chunk_file)

            except Exception as e:
                print(f"   ❌ Error on chunk {i}: {e}")
                # Continue with next chunk
                continue

        # Concatenate all chunks
        print(f"\n🔗 Concatenating {len(chunk_files)} audio chunks...")
        combined = AudioSegment.empty()

        for chunk_file in chunk_files:
            audio = AudioSegment.from_mp3(chunk_file)
            combined += audio

        # Export final file
        print(f"💾 Exporting to: {output_file}")
        combined.export(output_file, format="mp3", bitrate="192k")

        # Get duration
        duration_seconds = len(combined) / 1000
        duration_minutes = duration_seconds / 60

        print(f"\n✅ Success!")
        print(f"   Duration: {duration_minutes:.1f} minutes ({duration_seconds:.0f} seconds)")
        print(f"   Output: {output_file}")


if __name__ == '__main__':
    main()
