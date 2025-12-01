#!/usr/bin/env python3
"""
VTT Subtitle Generator for Dreamweaving

Generates properly-timed WebVTT subtitles from SSML scripts.
Scales timing to match actual audio duration.

Usage:
    python3 scripts/ai/vtt_generator.py sessions/{session}
    python3 scripts/ai/vtt_generator.py sessions/{session} --audio output/final.mp3
"""

import re
import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import subprocess
import json


def parse_time_string(time_str: str) -> float:
    """Parse SSML time string like '1.5s' or '1200ms' to seconds."""
    if time_str.endswith('ms'):
        return float(time_str[:-2]) / 1000
    elif time_str.endswith('s'):
        return float(time_str[:-1])
    return 0


def format_vtt_time(seconds: float) -> str:
    """Format seconds as VTT timestamp (HH:MM:SS.mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def clean_text(text: str) -> str:
    """Remove SSML tags and clean up text."""
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
    # Remove phoneme tags but keep content
    text = re.sub(r'<phoneme[^>]*>', '', text)
    text = re.sub(r'</phoneme>', '', text)
    # Remove other tags
    text = re.sub(r'<[^>]+>', '', text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_audio_duration(audio_path: str) -> Optional[float]:
    """Get audio duration using ffprobe."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
             '-of', 'json', audio_path],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except Exception as e:
        print(f"Warning: Could not get audio duration: {e}")
        return None


def estimate_speech_duration(text: str, wpm: int = 120, rate_multiplier: float = 0.85) -> float:
    """Estimate how long it takes to speak the text."""
    words = len(text.split())
    return (words / wpm) * 60 * rate_multiplier


def parse_ssml_to_segments(ssml_content: str) -> List[Dict]:
    """Parse SSML and extract text segments with timing."""
    segments = []
    current_time = 0.0

    # Split into lines for easier processing
    lines = ssml_content.split('\n')

    for line in lines:
        # Skip XML declaration and speak tags
        if line.strip().startswith('<?xml') or line.strip().startswith('<speak') or line.strip().startswith('</speak'):
            continue

        # Skip section comments
        if '<!-- SECTION' in line or '<!--=====' in line or line.strip().startswith('<!--'):
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


def merge_short_segments(segments: List[Dict], min_duration: float = 2.0, max_chars: int = 80) -> List[Dict]:
    """Merge very short segments and split long ones for readability."""
    if not segments:
        return []

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


def generate_vtt(segments: List[Dict]) -> str:
    """Generate VTT content from segments."""
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
    parser = argparse.ArgumentParser(description='Generate VTT subtitles from SSML')
    parser.add_argument('session_path', help='Path to session directory')
    parser.add_argument('--audio', help='Path to audio file for duration scaling')
    parser.add_argument('--output', help='Output VTT path (default: output/subtitles.vtt)')
    args = parser.parse_args()

    session_path = Path(args.session_path)

    # Find SSML file
    ssml_paths = [
        session_path / 'working_files' / 'script.ssml',
        session_path / 'script.ssml',
    ]

    ssml_path = None
    for path in ssml_paths:
        if path.exists():
            ssml_path = path
            break

    if not ssml_path:
        print(f"Error: No SSML file found in {session_path}")
        sys.exit(1)

    print(f"Generating VTT subtitles from {ssml_path}...")

    # Read SSML
    with open(ssml_path, 'r') as f:
        ssml_content = f.read()

    # Parse to segments
    segments = parse_ssml_to_segments(ssml_content)
    print(f"  Parsed {len(segments)} raw segments")

    # Merge/split for better readability
    segments = merge_short_segments(segments)
    print(f"  Merged to {len(segments)} display segments")

    # Get actual audio duration if available
    audio_path = args.audio
    if not audio_path:
        # Try to find audio file
        audio_candidates = [
            session_path / 'output' / 'final.mp3',
            session_path / 'output' / 'voice.mp3',
        ]
        for candidate in audio_candidates:
            if candidate.exists():
                audio_path = str(candidate)
                break

    # Scale timing to match actual audio duration
    if segments and audio_path:
        actual_duration = get_audio_duration(audio_path)
        if actual_duration:
            estimated_duration = segments[-1]['end']
            scale = actual_duration / estimated_duration

            print(f"  Estimated duration: {estimated_duration:.1f}s")
            print(f"  Actual duration: {actual_duration:.1f}s")
            print(f"  Scaling factor: {scale:.2f}")

            for seg in segments:
                seg['start'] *= scale
                seg['end'] *= scale

    # Generate VTT
    vtt_content = generate_vtt(segments)

    # Determine output path
    if args.output:
        vtt_path = Path(args.output)
    else:
        vtt_path = session_path / 'output' / 'subtitles.vtt'

    # Ensure output directory exists
    vtt_path.parent.mkdir(parents=True, exist_ok=True)

    # Save VTT
    with open(vtt_path, 'w') as f:
        f.write(vtt_content)

    print(f"\n✓ Saved: {vtt_path}")
    print(f"  Total captions: {len(segments)}")

    # Also save to youtube_package if it exists
    youtube_path = session_path / 'output' / 'youtube_package' / 'subtitles.vtt'
    if youtube_path.parent.exists():
        with open(youtube_path, 'w') as f:
            f.write(vtt_content)
        print(f"  Also saved: {youtube_path}")


if __name__ == "__main__":
    main()
