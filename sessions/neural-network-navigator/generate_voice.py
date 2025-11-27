#!/usr/bin/env python3
"""
Generate voice audio for Neural Network Navigator using Edge TTS

Since Edge TTS doesn't support SSML directly, we'll:
1. Extract text from SSML
2. Apply rate adjustment via Edge TTS flags
3. Generate multiple sections with different prosody
4. Concatenate them together
"""

import re
import subprocess
import os

def extract_text_from_ssml(ssml_file):
    """Extract plain text from SSML, preserving pauses"""
    with open(ssml_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove XML declaration and speak tags
    content = re.sub(r'<\?xml[^>]*\?>', '', content)
    content = re.sub(r'<speak[^>]*>', '', content)
    content = re.sub(r'</speak>', '', content)

    # Convert breaks to pause notation
    content = re.sub(r'<break time="(\d+)s"/>', r' [PAUSE \1s] ', content)

    # Remove emphasis tags but keep the emphasized text
    content = re.sub(r'<emphasis level="strong">([^<]+)</emphasis>', r'\1', content)

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

def generate_audio_section(text, rate, pitch, output_file, voice="en-US-AvaNeural"):
    """Generate audio for one section using Edge TTS"""

    # Convert rate (0.85 = -15%, 0.90 = -10%, etc.)
    rate_float = float(rate)
    rate_pct_num = int((rate_float - 1.0) * 100)

    # Edge TTS format: +10% or -10% (no zero, must have sign)
    if rate_pct_num > 0:
        rate_pct = f"+{rate_pct_num}%"
    elif rate_pct_num < 0:
        rate_pct = f"{rate_pct_num}%"
    else:
        rate_pct = "+0%"  # Edge TTS requires a sign

    # Convert pitch: remove 'st' and ensure proper format (+0Hz, -2Hz, etc.)
    pitch_val = pitch.replace('st', '')
    try:
        pitch_num = int(pitch_val)
        if pitch_num > 0:
            pitch_str = f"+{pitch_num}Hz"
        elif pitch_num < 0:
            pitch_str = f"{pitch_num}Hz"
        else:
            pitch_str = "+0Hz"
    except:
        pitch_str = "+0Hz"

    print(f"  Generating: rate={rate_pct}, pitch={pitch_str}, length={len(text)} chars...")

    # Write text to temp file
    temp_text = "temp_text.txt"
    with open(temp_text, 'w', encoding='utf-8') as f:
        f.write(text)

    # Generate with edge-tts
    cmd = [
        'edge-tts',
        '--voice', voice,
        '--rate', rate_pct,
        '--pitch', pitch_str,
        '--file', temp_text,
        '--write-media', output_file
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            print(f"    Error: {result.stderr}")
            return False
        print(f"    ✓ Generated {output_file}")
        return True
    except subprocess.TimeoutExpired:
        print(f"    Timeout generating {output_file}")
        return False
    finally:
        if os.path.exists(temp_text):
            os.remove(temp_text)

def concatenate_audio(input_files, output_file):
    """Concatenate multiple audio files using FFmpeg"""
    # Create file list for FFmpeg
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
        print(f"✓ Final audio: {output_file}")
        return True
    else:
        print(f"Error concatenating: {result.stderr}")
        return False

def main():
    print("=" * 60)
    print("NEURAL NETWORK NAVIGATOR - Voice Generation")
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
    audio_files = []

    for i, section in enumerate(sections, 1):
        section_file = f"{output_dir}/section_{i:02d}.mp3"
        success = generate_audio_section(
            section['text'],
            section['rate'],
            section['pitch'],
            section_file
        )
        if success:
            audio_files.append(section_file)

    # Concatenate all sections
    print(f"\n3. Combining all sections...")
    success = concatenate_audio(audio_files, final_output)

    # Cleanup temp files
    print(f"\n4. Cleaning up temporary files...")
    for audio_file in audio_files:
        if os.path.exists(audio_file):
            os.remove(audio_file)

    if success:
        file_size = os.path.getsize(final_output) / (1024 * 1024)
        print(f"\n✓ Voice generation complete!")
        print(f"  Output: {final_output}")
        print(f"  Size: {file_size:.1f} MB")
        print(f"\nNext: Generate binaural beats")
    else:
        print(f"\n✗ Voice generation failed")
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
