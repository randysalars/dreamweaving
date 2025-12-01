#!/usr/bin/env python3
"""
Generate V2 enhanced voice using Ava Neural (Edge TTS) instead of Google Neural2-A
This keeps all the V2 script enhancements but uses the original V1 voice
"""

import re
import subprocess
import os
import sys

def extract_text_from_ssml(ssml_file):
    """Extract plain text from SSML, preserving pauses"""
    with open(ssml_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove XML declaration and speak tags
    content = re.sub(r'<\?xml[^>]*\?>', '', content)
    content = re.sub(r'<speak[^>]*>', '', content)
    content = re.sub(r'</speak>', '', content)

    # Remove comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    # Convert ALL break tags to natural pauses
    # Must handle both integer and decimal seconds (1s, 1.5s, etc.)
    # Strategy: Convert based on duration to natural punctuation
    def replace_break(match):
        time_str = match.group(1)
        try:
            duration = float(time_str)
            if duration <= 1.5:
                return ''  # Very short, just remove
            elif duration <= 2.5:
                return ', '  # Short pause -> comma
            elif duration <= 3.5:
                return '. '  # Medium pause -> period
            else:
                return '... '  # Long pause -> ellipsis
        except ValueError:
            return '. '  # Fallback

    content = re.sub(r'<break time="([\d.]+)s"\s*/>', replace_break, content)

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

    # Edge TTS format: "+10%" or "-10%" (must be quoted string with sign)
    if rate_pct_num >= 0:
        rate_pct = f"+{rate_pct_num}%"
    else:
        rate_pct = f"{rate_pct_num}%"

    # Convert pitch: remove 'st' and convert to Hz
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

    # Replace pause markers with actual pauses (silence)
    # Edge TTS doesn't support inline pauses, so we'll add periods for natural pauses
    text_with_pauses = re.sub(r'\[PAUSE (\d+)s\]', lambda m: '.' * int(int(m.group(1)) / 2), text)

    print(f"Generating section:")
    print(f"  Rate: {rate_pct}, Pitch: {pitch_str}")
    print(f"  Text length: {len(text_with_pauses)} chars")
    print(f"  Preview: {text_with_pauses[:100]}...")

    cmd = [
        'edge-tts',
        '--voice', voice,
        f'--rate={rate_pct}',
        f'--pitch={pitch_str}',
        '--text', text_with_pauses,
        '--write-media', output_file
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  ✓ Generated: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: {e}")
        print(f"  stderr: {e.stderr}")
        return False

def concatenate_audio_files(file_list, output_file):
    """Concatenate multiple audio files using ffmpeg"""

    # Create a temporary file list for ffmpeg concat
    list_file = "working_files/concat_list.txt"
    with open(list_file, 'w') as f:
        for audio_file in file_list:
            # Use absolute path to avoid issues
            abs_path = os.path.abspath(audio_file)
            f.write(f"file '{abs_path}'\n")

    print(f"\nConcatenating {len(file_list)} sections...")

    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', os.path.abspath(list_file),
        '-c', 'copy',
        '-y',
        os.path.abspath(output_file)
    ]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ Concatenated audio: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Concatenation failed: {e}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    print("=" * 70)
    print("NEURAL NETWORK NAVIGATOR V2 - AVA VOICE GENERATION")
    print("Using V2 Enhanced Script with V1 Ava Voice")
    print("=" * 70)
    print()

    ssml_file = "working_files/voice_script_enhanced_v2.ssml"
    output_dir = "working_files"
    final_output = "working_files/neural_navigator_v2_ava.mp3"

    # Extract sections from SSML
    print(f"Parsing SSML: {ssml_file}")
    sections = extract_text_from_ssml(ssml_file)
    print(f"Found {len(sections)} prosody sections\n")

    # Generate each section
    temp_files = []
    for i, section in enumerate(sections, 1):
        temp_file = f"{output_dir}/section_{i:02d}.mp3"
        temp_files.append(temp_file)

        print(f"\n--- Section {i}/{len(sections)} ---")
        success = generate_audio_section(
            section['text'],
            section['rate'],
            section['pitch'],
            temp_file,
            voice="en-US-AvaNeural"
        )

        if not success:
            print(f"\n✗ Failed to generate section {i}")
            return 1

    # Concatenate all sections
    print("\n" + "=" * 70)
    success = concatenate_audio_files(temp_files, final_output)

    if success:
        # Convert to high-quality WAV
        wav_output = final_output.replace('.mp3', '.wav')
        print(f"\nConverting to WAV: {wav_output}")

        cmd = [
            'ffmpeg',
            '-i', final_output,
            '-ar', '48000',
            '-ac', '2',
            '-y',
            wav_output
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        file_size_mp3 = os.path.getsize(final_output) / (1024 * 1024)
        file_size_wav = os.path.getsize(wav_output) / (1024 * 1024)

        print("\n" + "=" * 70)
        print("✨ VOICE GENERATION COMPLETE!")
        print("=" * 70)
        print(f"\nOutputs:")
        print(f"  MP3: {final_output} ({file_size_mp3:.1f} MB)")
        print(f"  WAV: {wav_output} ({file_size_wav:.1f} MB)")
        print(f"\nVoice: en-US-AvaNeural (Edge TTS)")
        print(f"Script: V2 Enhanced with pretalk and closing")
        print()

        # Clean up temp files
        print("Cleaning up temporary files...")
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if os.path.exists("working_files/concat_list.txt"):
            os.remove("working_files/concat_list.txt")

        return 0
    else:
        print("\n✗ Voice generation failed")
        return 1

if __name__ == '__main__':
    # Already in the correct directory when running from sessions/neural-network-navigator
    sys.exit(main())
