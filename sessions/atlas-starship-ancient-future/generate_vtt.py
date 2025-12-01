#!/usr/bin/env python3
"""
Generate VTT subtitles from SSML script for ATLAS Starship session.
Estimates timing based on speech rate and break tags.
"""

import re
import os

SESSION_DIR = "/home/rsalars/Projects/dreamweaving/sessions/atlas-starship-ancient-future"
SSML_PATH = f"{SESSION_DIR}/script.ssml"
VTT_PATH = f"{SESSION_DIR}/output/youtube_package/subtitles.vtt"

# Average speaking rate (words per minute) - adjusted for slow hypnotic pace
BASE_WPM = 120  # Normal speech
SLOW_RATE_MULTIPLIER = 0.85  # Account for prosody rate="0.9" etc.

def parse_time_string(time_str):
    """Parse SSML time string like '1.5s' or '1200ms' to seconds"""
    if time_str.endswith('ms'):
        return float(time_str[:-2]) / 1000
    elif time_str.endswith('s'):
        return float(time_str[:-1])
    return 0

def format_vtt_time(seconds):
    """Format seconds as VTT timestamp (HH:MM:SS.mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

def clean_text(text):
    """Remove SSML tags and clean up text"""
    # Remove XML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # Remove prosody tags but keep content
    text = re.sub(r'<prosody[^>]*>', '', text)
    text = re.sub(r'</prosody>', '', text)
    # Remove emphasis tags but keep content
    text = re.sub(r'<emphasis[^>]*>', '', text)
    text = re.sub(r'</emphasis>', '', text)
    # Remove break tags (we handle them separately)
    text = re.sub(r'<break[^>]*/>', '', text)
    # Remove other tags
    text = re.sub(r'<[^>]+>', '', text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def estimate_speech_duration(text, wpm=BASE_WPM):
    """Estimate how long it takes to speak the text"""
    words = len(text.split())
    return (words / wpm) * 60 * SLOW_RATE_MULTIPLIER

def parse_ssml_to_segments(ssml_content):
    """Parse SSML and extract text segments with timing"""
    segments = []
    current_time = 0.0

    # Split into lines for easier processing
    lines = ssml_content.split('\n')

    current_text = ""

    for line in lines:
        # Skip XML declaration and speak tags
        if line.strip().startswith('<?xml') or line.strip().startswith('<speak') or line.strip().startswith('</speak'):
            continue

        # Skip section comment headers but extract section info
        if '<!-- SECTION' in line or '<!--=====' in line:
            continue

        # Skip other comments
        if line.strip().startswith('<!--'):
            continue

        # Find all break tags and their durations
        breaks = re.findall(r'<break time="([^"]+)"/?>', line)

        # Get text content (cleaned)
        text = clean_text(line)

        if text:
            # Estimate duration for this text
            speech_duration = estimate_speech_duration(text)

            # Create segment
            start_time = current_time
            end_time = current_time + speech_duration

            segments.append({
                'start': start_time,
                'end': end_time,
                'text': text
            })

            current_time = end_time

        # Add break durations
        for break_time in breaks:
            pause = parse_time_string(break_time)
            current_time += pause

    return segments

def merge_short_segments(segments, min_duration=2.0, max_chars=80):
    """Merge very short segments and split long ones"""
    merged = []
    buffer_text = ""
    buffer_start = 0

    for seg in segments:
        if not buffer_text:
            buffer_start = seg['start']

        # Add to buffer
        if buffer_text:
            buffer_text += " " + seg['text']
        else:
            buffer_text = seg['text']

        # Check if we should output
        duration = seg['end'] - buffer_start

        if duration >= min_duration or len(buffer_text) > max_chars:
            # Split long text into multiple lines
            if len(buffer_text) > max_chars:
                words = buffer_text.split()
                mid = len(words) // 2
                line1 = ' '.join(words[:mid])
                line2 = ' '.join(words[mid:])
                buffer_text = line1 + '\n' + line2

            merged.append({
                'start': buffer_start,
                'end': seg['end'],
                'text': buffer_text
            })
            buffer_text = ""

    # Don't forget last buffer
    if buffer_text:
        merged.append({
            'start': buffer_start,
            'end': segments[-1]['end'] if segments else buffer_start + 3,
            'text': buffer_text
        })

    return merged

def generate_vtt(segments):
    """Generate VTT content from segments"""
    vtt_lines = ["WEBVTT", "Kind: captions", "Language: en", ""]

    for i, seg in enumerate(segments, 1):
        start = format_vtt_time(seg['start'])
        end = format_vtt_time(seg['end'])
        vtt_lines.append(f"{i}")
        vtt_lines.append(f"{start} --> {end}")
        vtt_lines.append(seg['text'])
        vtt_lines.append("")

    return '\n'.join(vtt_lines)

def main():
    print("Generating VTT subtitles from SSML...")

    # Read SSML
    with open(SSML_PATH, 'r') as f:
        ssml_content = f.read()

    # Parse to segments
    segments = parse_ssml_to_segments(ssml_content)
    print(f"  Parsed {len(segments)} raw segments")

    # Merge/split for better readability
    segments = merge_short_segments(segments)
    print(f"  Merged to {len(segments)} display segments")

    # Scale timing to match actual audio duration (1597 seconds)
    if segments:
        estimated_duration = segments[-1]['end']
        actual_duration = 1597.0
        scale = actual_duration / estimated_duration

        print(f"  Estimated duration: {estimated_duration:.1f}s")
        print(f"  Actual duration: {actual_duration:.1f}s")
        print(f"  Scaling factor: {scale:.2f}")

        for seg in segments:
            seg['start'] *= scale
            seg['end'] *= scale

    # Generate VTT
    vtt_content = generate_vtt(segments)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(VTT_PATH), exist_ok=True)

    # Save
    with open(VTT_PATH, 'w') as f:
        f.write(vtt_content)

    print(f"\n✓ Saved: {VTT_PATH}")
    print(f"  Total captions: {len(segments)}")

    # Also save to main output folder
    alt_path = f"{SESSION_DIR}/output/subtitles.vtt"
    with open(alt_path, 'w') as f:
        f.write(vtt_content)
    print(f"  Also saved: {alt_path}")

if __name__ == "__main__":
    main()
