#!/usr/bin/env python3
"""
Garden of Eden Path-Working: Chunked Audio Generator
Handles large SSML files by splitting into chunks under 5000 bytes

Requirements:
    pip install google-cloud-texttospeech pydub

Usage:
    python3 generate_audio_chunked.py garden_of_eden_hypnosis.ssml output.mp3

Author: The Sacred Digital Dreamweaver - Randy Sailer's Autonomous AI Clone
"""

from google.cloud import texttospeech
import sys
import os
import re
from pydub import AudioSegment

def print_header():
    """Print a nice header"""
    print("=" * 70)
    print("   Garden of Eden Path-Working: Chunked Audio Generator")
    print("   Hypnotic SSML → Professional Audio (Large File Support)")
    print("=" * 70)
    print()

def split_ssml_into_chunks(ssml_content, max_bytes=4500):
    """
    Split SSML content into chunks that are under max_bytes.
    Splits at sentence boundaries to maintain natural flow.
    """
    # Extract the content between <speak> tags
    speak_match = re.search(r'<speak[^>]*>(.*)</speak>', ssml_content, re.DOTALL)
    if not speak_match:
        raise ValueError("Invalid SSML: No <speak> tags found")
    
    content = speak_match.group(1)
    speak_opening = ssml_content[:speak_match.start(1)]
    speak_closing = '</speak>'
    
    # Split on major section boundaries (comments with SECTION)
    section_pattern = r'(<!-- SECTION \d:.*?-->)'
    sections = re.split(section_pattern, content)
    
    chunks = []
    current_chunk = ""
    
    for section in sections:
        if not section.strip():
            continue
            
        # Calculate size with SSML wrapper
        test_chunk = speak_opening + current_chunk + section + speak_closing
        
        if len(test_chunk.encode('utf-8')) > max_bytes:
            # Current chunk is full, save it
            if current_chunk:
                chunks.append(speak_opening + current_chunk + speak_closing)
            current_chunk = section
        else:
            current_chunk += section
    
    # Add the last chunk
    if current_chunk:
        chunks.append(speak_opening + current_chunk + speak_closing)
    
    # If we still have chunks that are too large, split by prosody tags
    final_chunks = []
    for chunk in chunks:
        if len(chunk.encode('utf-8')) <= max_bytes:
            final_chunks.append(chunk)
        else:
            # Split this chunk further by prosody sections
            final_chunks.extend(split_large_chunk(chunk, speak_opening, speak_closing, max_bytes))
    
    return final_chunks

def split_large_chunk(chunk, speak_opening, speak_closing, max_bytes):
    """Split a chunk that's still too large by prosody boundaries"""
    # Extract content
    content = chunk.replace(speak_opening, '').replace(speak_closing, '')
    
    # Split on break tags with long pauses
    parts = re.split(r'(<break time="[23]s"/>)', content)
    
    sub_chunks = []
    current = ""
    
    for part in parts:
        test = speak_opening + current + part + speak_closing
        if len(test.encode('utf-8')) > max_bytes and current:
            sub_chunks.append(speak_opening + current + speak_closing)
            current = part
        else:
            current += part
    
    if current:
        sub_chunks.append(speak_opening + current + speak_closing)
    
    return sub_chunks

def synthesize_chunk(client, ssml_text, voice_name, chunk_num, total_chunks):
    """Synthesize a single chunk of SSML"""
    print(f"   🎙️  Chunk {chunk_num}/{total_chunks}: {len(ssml_text.encode('utf-8'))} bytes")
    
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE if "A" in voice_name or "C" in voice_name or "E" in voice_name or "F" in voice_name else texttospeech.SsmlVoiceGender.MALE
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.85,
        pitch=-2.0,
        effects_profile_id=["headphone-class-device"],
        sample_rate_hertz=24000
    )
    
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    
    return response.audio_content

def concatenate_audio_chunks(chunk_files, output_file):
    """Concatenate multiple MP3 files into one"""
    print(f"\n🔗 Concatenating {len(chunk_files)} audio chunks...")
    
    combined = AudioSegment.empty()
    
    for i, chunk_file in enumerate(chunk_files, 1):
        print(f"   Adding chunk {i}/{len(chunk_files)}...")
        audio = AudioSegment.from_mp3(chunk_file)
        combined += audio
        # Clean up temporary file
        os.remove(chunk_file)
    
    # Export final file
    print(f"💾 Exporting final audio to: {output_file}")
    combined.export(output_file, format="mp3", bitrate="128k")
    
    return combined

def synthesize_ssml_file_chunked(ssml_filepath, output_filepath, voice_name="en-US-Neural2-A"):
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
    if byte_count <= 5000:
        print(f"   ✓ File is under 5000 bytes, no chunking needed")
        chunks = [ssml_content]
    else:
        print(f"   ⚠️  File exceeds 5000 byte limit, chunking required")
        print(f"📦 Splitting into manageable chunks...")
        chunks = split_ssml_into_chunks(ssml_content)
        print(f"   ✓ Created {len(chunks)} chunks")
        
        # Validate chunk sizes
        for i, chunk in enumerate(chunks, 1):
            chunk_bytes = len(chunk.encode('utf-8'))
            if chunk_bytes > 5000:
                print(f"   ⚠️  Warning: Chunk {i} is {chunk_bytes} bytes (may fail)")
    
    # Synthesize each chunk
    print(f"\n🎙️  Generating audio with voice: {voice_name}")
    print(f"   Speaking rate: 0.85x (hypnotic pace)")
    print(f"   Pitch: -2.0 semitones (calming)")
    print(f"\n⏳ Synthesizing {len(chunks)} chunk(s)... (this may take 1-2 minutes)")
    print()
    
    chunk_files = []
    
    try:
        for i, chunk in enumerate(chunks, 1):
            audio_content = synthesize_chunk(client, chunk, voice_name, i, len(chunks))
            
            # Save chunk to temporary file
            chunk_file = f"temp_chunk_{i:03d}.mp3"
            with open(chunk_file, 'wb') as out:
                out.write(audio_content)
            chunk_files.append(chunk_file)
            
    except Exception as e:
        print(f"\n❌ Error during synthesis: {e}")
        # Clean up any temporary files
        for chunk_file in chunk_files:
            if os.path.exists(chunk_file):
                os.remove(chunk_file)
        sys.exit(1)
    
    # Concatenate all chunks if more than one
    if len(chunk_files) == 1:
        # Just rename the single file
        os.rename(chunk_files[0], output_filepath)
    else:
        # Concatenate multiple files
        combined = concatenate_audio_chunks(chunk_files, output_filepath)
    
    # Calculate file size and duration
    file_size_mb = os.path.getsize(output_filepath) / (1024 * 1024)
    
    # Try to get duration if pydub worked
    try:
        audio = AudioSegment.from_mp3(output_filepath)
        duration_minutes = len(audio) / 1000 / 60
        duration_str = f"{duration_minutes:.1f} minutes"
    except:
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
    print_header()
    
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("❌ Error: Missing required arguments")
        print()
        print("Usage:")
        print("   python3 generate_audio_chunked.py <input.ssml> <output.mp3> [voice_name]")
        print()
        print("Example:")
        print("   python3 generate_audio_chunked.py garden_of_eden_hypnosis.ssml output.mp3")
        print()
        print("Optional voice_name (default: en-US-Neural2-A):")
        print("   Female voices: en-US-Neural2-A, en-US-Neural2-C, en-US-Neural2-E, en-US-Neural2-F")
        print("   Male voices: en-US-Neural2-D, en-US-Neural2-I, en-US-Neural2-J")
        print()
        sys.exit(1)
    
    ssml_file = sys.argv[1]
    output_file = sys.argv[2]
    voice_name = sys.argv[3] if len(sys.argv) > 3 else "en-US-Neural2-A"
    
    # Check for pydub
    try:
        import pydub
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
    
    # Generate the audio
    synthesize_ssml_file_chunked(ssml_file, output_file, voice_name)

if __name__ == "__main__":
    main()
