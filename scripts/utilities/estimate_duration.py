#!/usr/bin/env python3
"""
Duration Estimator for SSML Scripts

Estimates the audio duration of an SSML script by:
1. Counting words (approx 150 words/minute at normal speed)
2. Summing explicit break/pause durations
3. Adjusting for speaking rate from manifest

This addresses the learning that duration estimation should happen BEFORE
voice generation to avoid duration mismatches.

Usage:
    python3 estimate_duration.py sessions/my-session/working_files/script.ssml
    python3 estimate_duration.py script.ssml --manifest sessions/my-session/manifest.yaml
    python3 estimate_duration.py script.ssml --speaking-rate 0.88
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import yaml


# Constants for estimation
WORDS_PER_MINUTE_BASE = 150  # Average speaking rate
WORDS_PER_MINUTE_HYPNOTIC = 130  # Slower for hypnotic delivery


def parse_ssml(ssml_content: str) -> Dict:
    """
    Parse SSML content and extract word count and pauses.

    Returns:
        Dict with 'words', 'pauses_seconds', 'prosody_sections'
    """
    # Remove XML declaration and SSML tags
    text = ssml_content

    # Extract and sum all break times
    break_pattern = r'<break\s+time=["\'](\d+(?:\.\d+)?)(m?s)["\']'
    breaks = re.findall(break_pattern, text, re.IGNORECASE)

    total_pause_seconds = 0
    for value, unit in breaks:
        seconds = float(value)
        if unit.lower() == 'ms':
            seconds /= 1000
        elif unit.lower() == 's':
            pass  # already in seconds
        total_pause_seconds += seconds

    # Extract prosody rate modifications
    prosody_pattern = r'<prosody[^>]*rate=["\'](\d*\.?\d+)["\'][^>]*>(.*?)</prosody>'
    prosody_sections = []

    for match in re.finditer(prosody_pattern, text, re.DOTALL):
        rate = float(match.group(1))
        content = match.group(2)
        # Count words in this section
        clean_content = re.sub(r'<[^>]+>', ' ', content)
        words_in_section = len(clean_content.split())
        prosody_sections.append({
            'rate': rate,
            'words': words_in_section
        })

    # Remove all XML tags to get plain text
    plain_text = re.sub(r'<[^>]+>', ' ', text)

    # Count total words
    words = plain_text.split()
    word_count = len([w for w in words if w.strip()])

    return {
        'words': word_count,
        'pauses_seconds': total_pause_seconds,
        'prosody_sections': prosody_sections,
        'break_count': len(breaks),
    }


def estimate_duration(
    ssml_content: str,
    speaking_rate: float = 1.0,
    base_wpm: int = WORDS_PER_MINUTE_HYPNOTIC
) -> Dict:
    """
    Estimate the total duration of an SSML script.

    Args:
        ssml_content: The SSML script content
        speaking_rate: Speaking rate multiplier (1.0 = normal, 0.88 = slow)
        base_wpm: Base words per minute (default: 130 for hypnotic)

    Returns:
        Dict with duration breakdown
    """
    parsed = parse_ssml(ssml_content)

    # Calculate effective WPM based on speaking rate
    # Lower speaking rate = fewer WPM = longer duration
    effective_wpm = base_wpm * speaking_rate

    # Calculate base speaking time
    word_count = parsed['words']
    speaking_minutes = word_count / effective_wpm
    speaking_seconds = speaking_minutes * 60

    # Add pauses
    pause_seconds = parsed['pauses_seconds']

    # Total duration
    total_seconds = speaking_seconds + pause_seconds
    total_minutes = total_seconds / 60

    return {
        'word_count': word_count,
        'speaking_rate': speaking_rate,
        'effective_wpm': effective_wpm,
        'speaking_time_seconds': speaking_seconds,
        'pause_time_seconds': pause_seconds,
        'break_count': parsed['break_count'],
        'total_seconds': total_seconds,
        'total_minutes': total_minutes,
        'formatted': format_duration(total_seconds),
        'prosody_sections': len(parsed['prosody_sections']),
    }


def format_duration(seconds: float) -> str:
    """Format seconds as MM:SS or HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def load_manifest(path: Path) -> Optional[Dict]:
    """Load and parse a manifest.yaml file."""
    if not path.exists():
        return None

    with open(path, 'r') as f:
        return yaml.safe_load(f)


def get_speaking_rate_from_manifest(manifest: Dict) -> float:
    """Extract speaking rate from manifest."""
    voice_config = manifest.get('voice', {})
    return voice_config.get('speaking_rate', 1.0)


def compare_with_target(estimated_minutes: float, target_minutes: float) -> Dict:
    """Compare estimated duration with target."""
    difference_minutes = estimated_minutes - target_minutes
    difference_percent = (difference_minutes / target_minutes) * 100

    return {
        'target_minutes': target_minutes,
        'estimated_minutes': estimated_minutes,
        'difference_minutes': difference_minutes,
        'difference_percent': difference_percent,
        'status': 'ok' if abs(difference_percent) <= 10 else ('short' if difference_percent < 0 else 'long'),
    }


def suggest_adjustments(comparison: Dict) -> list:
    """Suggest adjustments based on duration comparison."""
    suggestions = []

    if comparison['status'] == 'short':
        deficit_minutes = abs(comparison['difference_minutes'])
        suggestions.append(f"Session is ~{deficit_minutes:.1f} minutes short of target")
        suggestions.append(f"Add approximately {int(deficit_minutes * 130)} more words")
        suggestions.append(f"Or add ~{int(deficit_minutes * 60 / 3)} more 3-second pauses")

    elif comparison['status'] == 'long':
        excess_minutes = comparison['difference_minutes']
        suggestions.append(f"Session is ~{excess_minutes:.1f} minutes over target")
        suggestions.append(f"Remove approximately {int(excess_minutes * 130)} words")
        suggestions.append(f"Or reduce pause durations")

    return suggestions


def main():
    parser = argparse.ArgumentParser(
        description='Estimate duration of an SSML script before voice generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s script.ssml
  %(prog)s script.ssml --manifest manifest.yaml
  %(prog)s script.ssml --speaking-rate 0.88 --target 30

This tool helps you verify duration BEFORE expensive voice generation.
"""
    )

    parser.add_argument('ssml_file', type=Path,
                       help='Path to SSML script file')
    parser.add_argument('--manifest', type=Path,
                       help='Path to manifest.yaml to get speaking rate')
    parser.add_argument('--speaking-rate', type=float,
                       help='Override speaking rate (e.g., 0.88)')
    parser.add_argument('--target', type=float,
                       help='Target duration in minutes for comparison')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')

    args = parser.parse_args()

    # Read SSML file
    if not args.ssml_file.exists():
        print(f"Error: File not found: {args.ssml_file}", file=sys.stderr)
        return 1

    with open(args.ssml_file, 'r') as f:
        ssml_content = f.read()

    # Determine speaking rate
    speaking_rate = 1.0

    if args.manifest:
        manifest = load_manifest(args.manifest)
        if manifest:
            speaking_rate = get_speaking_rate_from_manifest(manifest)

    if args.speaking_rate:
        speaking_rate = args.speaking_rate

    # Estimate duration
    estimate = estimate_duration(ssml_content, speaking_rate)

    # Compare with target if provided
    comparison = None
    suggestions = []
    target = args.target

    if not target and args.manifest:
        manifest = load_manifest(args.manifest)
        if manifest:
            target = manifest.get('duration')

    if target:
        comparison = compare_with_target(estimate['total_minutes'], target)
        suggestions = suggest_adjustments(comparison)

    # Output
    if args.json:
        import json
        output = {
            'estimate': estimate,
            'comparison': comparison,
            'suggestions': suggestions,
        }
        print(json.dumps(output, indent=2))
    else:
        print("=" * 60)
        print("SSML DURATION ESTIMATE")
        print("=" * 60)
        print(f"\nFile: {args.ssml_file}")
        print(f"\n--- Analysis ---")
        print(f"Word count: {estimate['word_count']:,}")
        print(f"Break tags: {estimate['break_count']}")
        print(f"Prosody sections: {estimate['prosody_sections']}")
        print(f"\n--- Timing ---")
        print(f"Speaking rate: {estimate['speaking_rate']}x")
        print(f"Effective WPM: {estimate['effective_wpm']:.0f}")
        print(f"Speaking time: {estimate['speaking_time_seconds']/60:.1f} min")
        print(f"Pause time: {estimate['pause_time_seconds']/60:.1f} min ({estimate['pause_time_seconds']:.0f} sec)")
        print(f"\n--- Estimated Duration ---")
        print(f"Total: {estimate['formatted']} ({estimate['total_minutes']:.1f} minutes)")

        if comparison:
            print(f"\n--- Target Comparison ---")
            print(f"Target: {comparison['target_minutes']:.0f} minutes")
            print(f"Estimated: {comparison['estimated_minutes']:.1f} minutes")
            diff_sign = '+' if comparison['difference_minutes'] > 0 else ''
            print(f"Difference: {diff_sign}{comparison['difference_minutes']:.1f} min ({diff_sign}{comparison['difference_percent']:.0f}%)")

            if comparison['status'] != 'ok':
                status_icon = '⚠️' if abs(comparison['difference_percent']) > 20 else '📝'
                print(f"\nStatus: {status_icon} {comparison['status'].upper()}")
                print("\nSuggestions:")
                for suggestion in suggestions:
                    print(f"  • {suggestion}")
            else:
                print(f"\n✅ Duration is within acceptable range")

        print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
