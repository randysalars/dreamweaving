#!/usr/bin/env python3
"""
Generate voice audio for Neural Network Navigator using Edge TTS Python API directly
This bypasses the CLI issues with rate parameters
"""

import asyncio
import edge_tts
import re
import os
import subprocess

def extract_text_from_ssml(ssml_file):
    """Extract plain text and prosody from SSML"""
    with open(ssml_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove XML declaration and speak tags
    content = re.sub(r'<\?xml[^>]*\?>', '', content)
    content = re.sub(r'<speak[^>]*>', '', content)
    content = re.sub(r'</speak>', '', content)

    # Remove emphasis tags but keep the emphasized text
    content = re.sub(r'<emphasis level="strong">([^<]+)</emphasis>', r'\1', content)

    # Remove break tags (Edge TTS doesn't support them well)
    content = re.sub(r'<break time="\d+s"/>', '. ', content)

    # Extract prosody sections
    sections = []
    prosody_pattern = r'<prosody rate="([^"]+)" pitch="([^"]+)">(.*?)</prosody>'

    for match in re.finditer(prosody_pattern, content, re.DOTALL):
        rate = match.group(1)
        pitch = match.group(2)
        text = match.group(3).strip()

        # Clean up the text
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('\n', ' ')

        sections.append({
            'rate': rate,
            'pitch': pitch,
            'text': text
        })

    return sections

async def generate_audio_section(text, rate, pitch, output_file, voice="en-US-AvaNeural"):
    """Generate audio for one section using Edge TTS Python API"""

    # Convert rate (0.85 = -15%, 0.90 = -10%, etc.)
    rate_float = float(rate)
    rate_pct_num = int((rate_float - 1.0) * 100)

    # Format for Edge TTS: "+10%" or "-10%"
    if rate_pct_num >= 0:
        rate_str = f"+{rate_pct_num}%"
    else:
        rate_str = f"{rate_pct_num}%"

    # Convert pitch
    pitch_val = pitch.replace('st', '')
    try:
        pitch_num = int(pitch_val)
        if pitch_num >= 0:
            pitch_str = f"+{pitch_num}Hz"
        else:
            pitch_str = f"{pitch_num}Hz"
    except:
        pitch_str = "+0Hz"

    print(f"  Generating: rate={rate_str}, pitch={pitch_str}, length={len(text)} chars...")

    try:
        # Use edge_tts.Communicate directly
        communicate = edge_tts.Communicate(text, voice, rate=rate_str, pitch=pitch_str)
        await communicate.save(output_file)

        file_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"    ✓ Generated {output_file} ({file_size:.1f} MB)")
        return True
    except Exception as e:
        print(f"    Error: {e}")
        return False

async def generate_all_sections(sections, output_dir):
    """Generate all audio sections"""
    audio_files = []

    for i, section in enumerate(sections, 1):
        section_file = f"{output_dir}/section_{i:02d}.mp3"
        success = await generate_audio_section(
            section['text'],
            section['rate'],
            section['pitch'],
            section_file
        )
        if success:
            audio_files.append(section_file)

    return audio_files

def concatenate_audio(input_files, output_file):
    """Concatenate multiple audio files using FFmpeg"""
    list_file = "temp_filelist.txt"
    with open(list_file, 'w') as f:
        for audio_file in input_files:
            f.write(f"file '{audio_file}'\n")

    cmd = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', list_file,
        '-c', 'copy',
        output_file
    ]

    print(f"\nConcatenating {len(input_files)} sections...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    os.remove(list_file)

    if result.returncode == 0:
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✓ Final audio: {output_file} ({file_size:.1f} MB)")
        return True
    else:
        print(f"Error concatenating: {result.stderr}")
        return False

async def main():
    print("=" * 60)
    print("NEURAL NETWORK NAVIGATOR - Voice Generation v2")
    print("=" * 60)

    ssml_file = "working_files/voice_script.ssml"
    output_dir = "working_files"
    final_output = f"{output_dir}/voice_neural_navigator.mp3"

    # Extract sections
    print(f"\n1. Extracting text from {ssml_file}...")
    sections = extract_text_from_ssml(ssml_file)
    print(f"   Found {len(sections)} sections")

    # Generate each section
    print(f"\n2. Generating audio for each section...")
    audio_files = await generate_all_sections(sections, output_dir)

    if len(audio_files) == 0:
        print("\n✗ No audio files generated!")
        return 1

    # Concatenate all sections
    print(f"\n3. Combining all sections...")
    success = concatenate_audio(audio_files, final_output)

    # Cleanup temp files
    print(f"\n4. Cleaning up temporary files...")
    for audio_file in audio_files:
        if os.path.exists(audio_file):
            os.remove(audio_file)

    if success:
        print(f"\n✓ Voice generation complete!")
        print(f"\nNext: Generate binaural beats")
        return 0
    else:
        print(f"\n✗ Voice generation failed")
        return 1

if __name__ == '__main__':
    exit(asyncio.run(main()))
