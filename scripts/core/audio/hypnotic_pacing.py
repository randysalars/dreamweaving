#!/usr/bin/env python3
"""
DEPRECATED: Hypnotic Pacing Audio Post-Processor

⚠️  THIS MODULE IS DEPRECATED AND NO LONGER PART OF THE PRODUCTION WORKFLOW ⚠️

Edge TTS has been removed from the production workflow because:
- Ignores ALL SSML <break> tags
- Too fast for hypnotic/meditative work
- Audio quality issues (skipping/glitching)

This module was a workaround for Edge TTS limitations. With Google Cloud TTS Neural2,
SSML breaks work properly, making this post-processing unnecessary.

See docs/EDGE_TTS_REMOVAL.md for migration guide.

Status: ARCHIVED (kept for reference only)
Last Updated: 2025-11-30

---

Original Purpose:
Adds strategic pauses to voice recordings for hypnotic/meditative delivery

This solved Edge TTS limitation where SSML <break> tags were ignored.
Analyzed voice audio and inserted pauses based on:
- Number counting sequences (countdown/induction)
- Sentence endings and natural breaks
- Visualization cues and suggestions
- Scene transitions and section breaks
"""

import warnings
warnings.warn(
    "hypnotic_pacing.py is DEPRECATED. Edge TTS is no longer supported. "
    "Use Google Cloud TTS Neural2 instead, which respects SSML breaks natively. "
    "See docs/EDGE_TTS_REMOVAL.md for details.",
    DeprecationWarning,
    stacklevel=2
)

import re
from pathlib import Path
from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def detect_number_sequences(text):
    """
    Detect countdown/number sequences in text
    Only matches ACTUAL countdown contexts (not incidental numbers)
    Returns list of {pattern, start_pos, end_pos, numbers}
    """
    sequences = []

    # Look for countdown contexts with explicit framing
    # Pattern: "counting/count down from X to Y" followed by actual numbers
    countdown_context_pattern = r'count(?:ing)?\s+(?:down|up)?\s+from\s+(?:ten|10)\s+to\s+(?:one|1|zero|0)[^.]*?(?:\.{3}|\…)'

    for match in re.finditer(countdown_context_pattern, text, re.IGNORECASE):
        # Find the actual number sequence after this intro
        search_start = match.end()
        search_end = min(search_start + 300, len(text))  # Look ahead 300 chars
        search_region = text[search_start:search_end]

        # Find individual numbers in sequence (10... 9... 8... etc)
        number_pattern = r'(?:\d+|ten|nine|eight|seven|six|five|four|three|two|one|zero)\s*(?:\.{3}|\…)'

        for num_match in re.finditer(number_pattern, search_region, re.IGNORECASE):
            abs_pos = search_start + num_match.start()
            sequences.append({
                'type': 'countdown',
                'start': abs_pos,
                'end': abs_pos + len(num_match.group(0)),
                'text': num_match.group(0)
            })

    return sequences


def detect_visualization_cues(text):
    """
    Detect visualization and suggestion phrases that need extended pauses
    Only matches phrases that BEGIN visualization sequences (not casual usage)
    """
    cues = []

    # Patterns that indicate START of visualization sequences
    # These are command-style phrases that introduce mental imagery
    viz_patterns = [
        r'(?:^|\.|\n)\s*imagine\s+(?:yourself|a|the|how)',  # "Imagine yourself..." at sentence start
        r'(?:^|\.|\n)\s*visualize\s+',                      # "Visualize..." at sentence start
        r'(?:^|\.|\n)\s*see\s+yourself\s+',                 # "See yourself..." at sentence start
        r'(?:^|\.|\n)\s*picture\s+(?:a|the|yourself)',      # "Picture a..." at sentence start
        r'(?:^|\.|\n)\s*allow\s+yourself\s+to',             # "Allow yourself to..." at sentence start
        r'(?:^|\.|\n)\s*notice\s+(?:how|the|a)',            # "Notice how..." at sentence start
    ]

    for pattern in viz_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            cues.append({
                'type': 'visualization',
                'start': match.start(),
                'end': match.end(),
                'text': match.group(0).strip()
            })

    return cues


def detect_sentence_breaks(text):
    """
    Detect natural sentence breaks (complete thoughts only)
    Filters out mid-thought periods and compound sentence fragments
    """
    breaks = []

    # Find sentence-ending punctuation
    for match in re.finditer(r'[.!?…]+', text):
        period_pos = match.start()

        # Skip if this is likely a compound sentence or list item
        # Look at context before and after the period

        # Get 50 chars before and after for context
        context_start = max(0, period_pos - 50)
        context_end = min(len(text), period_pos + 50)
        context = text[context_start:context_end]

        # Skip if followed by lowercase (compound sentence)
        after_period = text[match.end():match.end() + 30] if match.end() < len(text) else ""
        if after_period and after_period.lstrip().startswith(tuple('abcdefghijklmnopqrstuvwxyz')):
            continue

        # Skip if in a list/sequence pattern (semicolons, commas nearby)
        if ';' in context or context.count(',') > 3:
            continue

        # Skip if this is an ellipsis in a continuous thought
        if '…' in match.group(0) or '...' in match.group(0):
            # Only pause on ellipsis if followed by newline or paragraph break
            if not (after_period.startswith('\n') or after_period.startswith('<break')):
                continue

        # This is likely a complete thought - add break
        breaks.append({
            'type': 'sentence_end',
            'start': match.start(),
            'end': match.end(),
            'text': match.group(0)
        })

    return breaks


def detect_section_boundaries(text):
    """
    Detect major section boundaries in hypnotic scripts
    These get longer pauses for narrative transitions
    """
    boundaries = []

    # Look for section markers in comments or headers
    section_patterns = [
        r'(?:SECTION\s+\d+:|<!--[^>]*SECTION[^>]*-->)',  # SECTION markers
        r'(?:Pretalk|Induction|Journey|Integration|Awakening|Return):',  # Named sections
        r'(?:^\s*\n\s*\n)',  # Double line breaks (paragraph boundaries)
    ]

    for pattern in section_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
            boundaries.append({
                'type': 'section_boundary',
                'start': match.start(),
                'end': match.end(),
                'text': match.group(0)
            })

    return boundaries


def detect_drift_zones(text):
    """
    Detect extended drift/rest sections with many existing breaks
    These should NOT get additional pauses (already have plenty)
    """
    drift_zones = []

    # Look for areas with multiple consecutive <break> tags (drift sections)
    # Pattern: 3+ breaks in close proximity = drift zone
    break_pattern = r'(<break[^>]*>[^<]*){3,}'

    for match in re.finditer(break_pattern, text):
        drift_zones.append({
            'start': match.start(),
            'end': match.end()
        })

    return drift_zones


def analyze_script_timing(ssml_path):
    """
    Analyze SSML script to identify where pauses should be inserted
    Returns list of pause locations with durations
    """
    with open(ssml_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Identify drift zones BEFORE stripping SSML (need <break> tags)
    drift_zones = detect_drift_zones(text)

    # Strip SSML tags to get plain text
    plain_text = re.sub(r'<[^>]+>', '', text)

    pause_points = []

    # Detect different types of pause-worthy moments
    countdowns = detect_number_sequences(plain_text)
    visualizations = detect_visualization_cues(plain_text)
    sentences = detect_sentence_breaks(plain_text)
    sections = detect_section_boundaries(text)

    def is_in_drift_zone(position):
        """Check if position falls within a drift zone"""
        for zone in drift_zones:
            if zone['start'] <= position <= zone['end']:
                return True
        return False

    # Assign pause durations based on context
    for item in countdowns:
        pause_points.append({
            'position': item['end'],
            'duration_ms': 3000,  # 3 seconds after each countdown number
            'reason': 'countdown',
            'text': item['text']
        })

    for item in visualizations:
        # Skip if in drift zone
        if is_in_drift_zone(item['start']):
            continue
        pause_points.append({
            'position': item['end'],
            'duration_ms': 4000,  # 4 seconds for visualization cues
            'reason': 'visualization',
            'text': item['text']
        })

    for item in sentences:
        # Skip if in drift zone (already has breaks)
        if is_in_drift_zone(item['start']):
            continue
        # Shorter pause for normal sentences
        pause_points.append({
            'position': item['end'],
            'duration_ms': 1500,  # 1.5 seconds between sentences
            'reason': 'sentence',
            'text': item['text']
        })

    for item in sections:
        pause_points.append({
            'position': item['end'],
            'duration_ms': 5000,  # 5 seconds for major section transitions
            'reason': 'section_boundary',
            'text': item['text']
        })

    # Sort by position and remove duplicates (same position)
    pause_points.sort(key=lambda x: x['position'])

    # Deduplicate: if multiple pauses at same position, keep the longest
    deduplicated = []
    last_pos = -1
    for point in pause_points:
        if point['position'] == last_pos and deduplicated:
            # Keep whichever has longer duration
            if point['duration_ms'] > deduplicated[-1]['duration_ms']:
                deduplicated[-1] = point
        else:
            deduplicated.append(point)
            last_pos = point['position']

    return deduplicated


def calculate_word_timing(audio, word_count):
    """
    Estimate average time per word based on audio duration and word count
    Returns milliseconds per word
    """
    duration_ms = len(audio)
    if word_count == 0:
        return 0
    return duration_ms / word_count


def insert_pauses_by_content(audio, ssml_path, pause_strategy='intelligent'):
    """
    Insert pauses into audio based on script content analysis

    Args:
        audio: AudioSegment of voice recording
        ssml_path: Path to SSML script file
        pause_strategy: 'intelligent' (content-based) or 'uniform' (every N seconds)

    Returns:
        AudioSegment with pauses inserted
    """
    print("\n🎭 Analyzing script for hypnotic pacing...")

    # Get plain text word count
    with open(ssml_path, 'r', encoding='utf-8') as f:
        text = f.read()
    plain_text = re.sub(r'<[^>]+>', '', text)
    words = plain_text.split()
    word_count = len(words)

    print(f"   Script: {word_count} words, {len(audio)/1000:.1f}s audio")

    if pause_strategy == 'intelligent':
        pause_points = analyze_script_timing(ssml_path)
        print(f"   Identified {len(pause_points)} pause points:")

        # Group by reason
        by_reason = {}
        for p in pause_points:
            by_reason[p['reason']] = by_reason.get(p['reason'], 0) + 1
        for reason, count in by_reason.items():
            print(f"     - {count} {reason} pauses")

        # Calculate word timing to map text positions to audio positions
        ms_per_word = calculate_word_timing(audio, word_count)

        # Build new audio with pauses
        result = AudioSegment.empty()
        last_pos = 0

        for point in pause_points:
            # Estimate audio position based on word position
            word_position = point['position'] / len(plain_text) * word_count
            audio_pos_ms = int(word_position * ms_per_word)

            # Add segment from last position to this pause point
            if audio_pos_ms > last_pos and audio_pos_ms < len(audio):
                result += audio[last_pos:audio_pos_ms]
                # Add pause
                silence = AudioSegment.silent(duration=point['duration_ms'])
                result += silence
                last_pos = audio_pos_ms

        # Add remaining audio
        if last_pos < len(audio):
            result += audio[last_pos:]

    else:
        # Uniform strategy: add pause every N seconds
        segment_duration_ms = 8000  # 8 seconds
        pause_duration_ms = 2000    # 2 second pauses

        result = AudioSegment.empty()
        pos = 0

        while pos < len(audio):
            end = min(pos + segment_duration_ms, len(audio))
            result += audio[pos:end]

            if end < len(audio):
                result += AudioSegment.silent(duration=pause_duration_ms)

            pos = end

    duration_increase = (len(result) - len(audio)) / 1000
    print(f"   Added {duration_increase:.1f}s of pauses")
    print(f"   New duration: {len(result)/1000:.1f}s (was {len(audio)/1000:.1f}s)")

    return result


def apply_hypnotic_pacing(voice_path, ssml_path, output_path=None, strategy='intelligent'):
    """
    Main function to apply hypnotic pacing to voice audio

    Args:
        voice_path: Path to voice audio file
        ssml_path: Path to SSML script
        output_path: Optional output path (defaults to voice_path_paced.ext)
        strategy: 'intelligent' or 'uniform'

    Returns:
        Path to paced audio file
    """
    voice_path = Path(voice_path)
    ssml_path = Path(ssml_path)

    if not output_path:
        output_path = voice_path.parent / f"{voice_path.stem}_paced{voice_path.suffix}"

    print(f"\n{'='*70}")
    print("Hypnotic Pacing Post-Processor")
    print(f"{'='*70}")
    print(f"Input: {voice_path}")
    print(f"Script: {ssml_path}")
    print(f"Strategy: {strategy}")

    # Load audio
    print("\nLoading audio...")
    audio = AudioSegment.from_file(voice_path)
    original_duration = len(audio) / 1000
    print(f"Original duration: {original_duration:.1f}s")

    # Apply pacing
    paced_audio = insert_pauses_by_content(audio, ssml_path, strategy)

    # Export
    print("\nExporting paced audio...")
    fmt = voice_path.suffix.lstrip('.')
    paced_audio.export(
        output_path,
        format=fmt,
        bitrate="320k" if fmt == "mp3" else None,
        parameters=["-q:a", "0"] if fmt == "mp3" else []
    )

    final_duration = len(paced_audio) / 1000
    increase_pct = ((final_duration - original_duration) / original_duration) * 100

    print(f"\n{'='*70}")
    print("✅ Hypnotic Pacing Complete")
    print(f"{'='*70}")
    print(f"Output: {output_path}")
    print(f"Duration: {original_duration:.1f}s → {final_duration:.1f}s (+{increase_pct:.1f}%)")
    print(f"{'='*70}\n")

    return output_path


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Add hypnotic pacing to voice audio')
    parser.add_argument('voice', help='Path to voice audio file')
    parser.add_argument('script', help='Path to SSML script file')
    parser.add_argument('--output', '-o', help='Output path (optional)')
    parser.add_argument('--strategy', choices=['intelligent', 'uniform'],
                        default='intelligent', help='Pause insertion strategy')

    args = parser.parse_args()

    apply_hypnotic_pacing(args.voice, args.script, args.output, args.strategy)
