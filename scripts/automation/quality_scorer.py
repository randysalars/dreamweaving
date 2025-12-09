#!/usr/bin/env python3
"""
Quality Scorer

Computes quality scores for generated sessions based on:
- Audio quality (LUFS, no clipping)
- Video presence and validity
- Script validation (SSML, NLP patterns)
- Duration accuracy
- Metadata completeness

Quality scores (0-100) are used to prioritize uploads.

Usage:
    from scripts.automation.quality_scorer import compute_quality_score

    score = compute_quality_score('/path/to/session')
    print(f"Quality score: {score:.1f}")

    # Get detailed breakdown
    details = compute_quality_score('/path/to/session', detailed=True)
    print(details)

CLI:
    python -m scripts.automation.quality_scorer --session sessions/my-session/
"""

import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

logger = logging.getLogger(__name__)

# Target audio loudness
TARGET_LUFS = -14.0


def compute_quality_score(
    session_path: str,
    detailed: bool = False
) -> float | Dict[str, Any]:
    """Compute overall quality score for a session.

    Args:
        session_path: Path to session directory
        detailed: If True, return dict with score breakdown

    Returns:
        Quality score (0-100) or dict with detailed breakdown
    """
    session_path = Path(session_path)
    session_name = session_path.name

    scores = {}
    details = {}

    # Audio quality (25%)
    audio_score, audio_details = score_audio(session_path)
    scores['audio'] = audio_score * 0.25
    details['audio'] = audio_details

    # Video presence (15%)
    video_score, video_details = score_video(session_path)
    scores['video'] = video_score * 0.15
    details['video'] = video_details

    # Script validation (25%)
    script_score, script_details = score_script(session_path)
    scores['script'] = script_score * 0.25
    details['script'] = script_details

    # Duration accuracy (15%)
    duration_score, duration_details = score_duration(session_path)
    scores['duration'] = duration_score * 0.15
    details['duration'] = duration_details

    # Metadata completeness (20%)
    metadata_score, metadata_details = score_metadata(session_path)
    scores['metadata'] = metadata_score * 0.20
    details['metadata'] = metadata_details

    total_score = sum(scores.values())

    if detailed:
        return {
            'total_score': round(total_score, 1),
            'component_scores': {k: round(v, 2) for k, v in scores.items()},
            'weights': {
                'audio': 0.25,
                'video': 0.15,
                'script': 0.25,
                'duration': 0.15,
                'metadata': 0.20,
            },
            'details': details,
            'session_name': session_name,
        }

    return round(total_score, 1)


def score_audio(session_path: Path) -> Tuple[float, Dict]:
    """Score audio quality.

    Checks:
    - Master audio file exists
    - LUFS within acceptable range (-16 to -12)
    - No clipping (true peak < -1 dBTP)

    Args:
        session_path: Session directory path

    Returns:
        (score 0-100, details dict)
    """
    session_name = session_path.name
    details = {'checks': {}, 'issues': []}

    # Find master audio file
    audio_path = session_path / 'output' / f'{session_name}_MASTER.mp3'
    if not audio_path.exists():
        # Try alternative names
        for alt in ['final_master.mp3', 'session_mixed.wav', 'voice_enhanced.mp3']:
            alt_path = session_path / 'output' / alt
            if alt_path.exists():
                audio_path = alt_path
                break

    if not audio_path.exists():
        details['issues'].append('No master audio file found')
        details['checks']['file_exists'] = False
        return 0.0, details

    details['checks']['file_exists'] = True
    details['audio_path'] = str(audio_path)

    # Get audio properties using ffprobe
    lufs, true_peak = get_audio_loudness(audio_path)

    if lufs is None:
        details['issues'].append('Could not analyze audio loudness')
        return 50.0, details

    details['lufs'] = lufs
    details['true_peak'] = true_peak

    # Score based on LUFS deviation from target (-14)
    lufs_deviation = abs(lufs - TARGET_LUFS)
    if lufs_deviation <= 1:
        lufs_score = 100
    elif lufs_deviation <= 2:
        lufs_score = 90
    elif lufs_deviation <= 3:
        lufs_score = 80
    elif lufs_deviation <= 5:
        lufs_score = 60
    else:
        lufs_score = max(0, 100 - lufs_deviation * 5)
        details['issues'].append(f'LUFS deviation too high: {lufs_deviation:.1f} dB')

    details['checks']['lufs_acceptable'] = lufs_score >= 60

    # Check for clipping
    if true_peak is not None:
        if true_peak > -1.0:
            details['issues'].append(f'Possible clipping: true peak {true_peak:.1f} dBTP')
            lufs_score -= 20
        details['checks']['no_clipping'] = true_peak <= -1.0

    return max(0, min(100, lufs_score)), details


def get_audio_loudness(audio_path: Path) -> Tuple[Optional[float], Optional[float]]:
    """Get LUFS and true peak using ffmpeg loudnorm filter.

    Args:
        audio_path: Path to audio file

    Returns:
        (lufs, true_peak) or (None, None) on error
    """
    try:
        result = subprocess.run(
            [
                'ffmpeg', '-i', str(audio_path),
                '-af', 'loudnorm=print_format=json',
                '-f', 'null', '-'
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Parse JSON from stderr
        output = result.stderr
        json_match = re.search(r'\{[^}]+\}', output, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            lufs = float(data.get('input_i', 0))
            true_peak = float(data.get('input_tp', 0))
            return lufs, true_peak

    except Exception as e:
        logger.warning(f"Failed to analyze audio: {e}")

    return None, None


def score_video(session_path: Path) -> Tuple[float, Dict]:
    """Score video file presence and validity.

    Checks:
    - Final video file exists
    - Video is valid (can be probed)
    - Resolution is correct (1920x1080)

    Args:
        session_path: Session directory path

    Returns:
        (score 0-100, details dict)
    """
    details = {'checks': {}, 'issues': []}

    # Check for video file
    video_path = session_path / 'output' / 'youtube_package' / 'final_video.mp4'
    if not video_path.exists():
        # Try alternative location
        video_path = session_path / 'output' / 'video' / 'session_final.mp4'

    if not video_path.exists():
        details['issues'].append('No video file found')
        details['checks']['file_exists'] = False
        return 0.0, details

    details['checks']['file_exists'] = True
    details['video_path'] = str(video_path)

    # Probe video
    try:
        result = subprocess.run(
            [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(video_path)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        probe_data = json.loads(result.stdout)

        # Find video stream
        video_stream = None
        for stream in probe_data.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break

        if video_stream:
            width = video_stream.get('width', 0)
            height = video_stream.get('height', 0)
            duration = float(probe_data.get('format', {}).get('duration', 0))

            details['width'] = width
            details['height'] = height
            details['duration_seconds'] = duration
            details['checks']['valid_video'] = True

            # Check resolution
            if width == 1920 and height == 1080:
                details['checks']['correct_resolution'] = True
                return 100.0, details
            else:
                details['issues'].append(f'Non-standard resolution: {width}x{height}')
                details['checks']['correct_resolution'] = False
                return 80.0, details

    except Exception as e:
        logger.warning(f"Failed to probe video: {e}")
        details['issues'].append(f'Failed to probe video: {e}')
        details['checks']['valid_video'] = False
        return 50.0, details

    return 50.0, details


def score_script(session_path: Path) -> Tuple[float, Dict]:
    """Score script quality.

    Checks:
    - SSML script exists
    - SSML is valid (basic XML check)
    - Contains expected sections
    - Word count is appropriate

    Args:
        session_path: Session directory path

    Returns:
        (score 0-100, details dict)
    """
    details = {'checks': {}, 'issues': []}

    # Find script file
    script_path = session_path / 'working_files' / 'script_production.ssml'
    if not script_path.exists():
        script_path = session_path / 'working_files' / 'script_voice_clean.ssml'

    if not script_path.exists():
        details['issues'].append('No SSML script found')
        details['checks']['file_exists'] = False
        return 0.0, details

    details['checks']['file_exists'] = True
    details['script_path'] = str(script_path)

    try:
        content = script_path.read_text(encoding='utf-8')

        # Basic XML validity check
        if not content.strip().startswith('<?xml') and not content.strip().startswith('<speak'):
            if '<speak' in content:
                details['checks']['valid_ssml'] = True
            else:
                details['issues'].append('Script missing <speak> tag')
                details['checks']['valid_ssml'] = False
                return 30.0, details
        else:
            details['checks']['valid_ssml'] = True

        # Count words (strip SSML tags)
        text_only = re.sub(r'<[^>]+>', ' ', content)
        words = len(text_only.split())
        details['word_count'] = words

        # Expected word count: ~3500-4500 for 25-30 min session
        if words < 2000:
            details['issues'].append(f'Script too short: {words} words')
            word_score = 60
        elif words < 3000:
            word_score = 80
        elif words <= 5000:
            word_score = 100
        else:
            details['issues'].append(f'Script may be too long: {words} words')
            word_score = 85

        details['checks']['appropriate_length'] = word_score >= 80

        # Check for expected patterns
        patterns = {
            'breath_cues': r'breath|breathe|breathing',
            'sensory_language': r'feel|see|hear|notice|imagine',
            'deepening': r'deeper|relax|calm|peace',
            'breaks': r'<break\s+time=',
        }

        pattern_scores = 0
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                pattern_scores += 1
                details['checks'][pattern_name] = True
            else:
                details['checks'][pattern_name] = False

        pattern_score = (pattern_scores / len(patterns)) * 100

        # Combined score
        final_score = (word_score * 0.4) + (pattern_score * 0.6)
        return final_score, details

    except Exception as e:
        logger.warning(f"Failed to analyze script: {e}")
        details['issues'].append(f'Script analysis error: {e}')
        return 30.0, details


def score_duration(session_path: Path) -> Tuple[float, Dict]:
    """Score duration accuracy.

    Compares actual video/audio duration to manifest target.

    Args:
        session_path: Session directory path

    Returns:
        (score 0-100, details dict)
    """
    details = {'checks': {}, 'issues': []}

    # Load manifest
    manifest_path = session_path / 'manifest.yaml'
    if not manifest_path.exists():
        details['issues'].append('No manifest.yaml found')
        return 50.0, details

    try:
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)

        target_minutes = manifest.get('session', {}).get('duration_minutes', 25)
        target_seconds = target_minutes * 60
        details['target_duration_minutes'] = target_minutes

        # Get actual duration from video or audio
        actual_seconds = None

        video_path = session_path / 'output' / 'youtube_package' / 'final_video.mp4'
        if video_path.exists():
            actual_seconds = get_media_duration(video_path)

        if actual_seconds is None:
            audio_path = session_path / 'output' / f'{session_path.name}_MASTER.mp3'
            if audio_path.exists():
                actual_seconds = get_media_duration(audio_path)

        if actual_seconds is None:
            details['issues'].append('Could not determine actual duration')
            return 50.0, details

        details['actual_duration_seconds'] = actual_seconds
        details['actual_duration_minutes'] = round(actual_seconds / 60, 1)

        # Calculate accuracy
        deviation_percent = abs(actual_seconds - target_seconds) / target_seconds * 100
        details['deviation_percent'] = round(deviation_percent, 1)

        if deviation_percent <= 5:
            score = 100
        elif deviation_percent <= 10:
            score = 90
        elif deviation_percent <= 20:
            score = 75
        elif deviation_percent <= 30:
            score = 60
        else:
            score = max(0, 100 - deviation_percent)
            details['issues'].append(f'Duration deviation too high: {deviation_percent:.0f}%')

        details['checks']['duration_acceptable'] = score >= 60
        return score, details

    except Exception as e:
        logger.warning(f"Failed to check duration: {e}")
        details['issues'].append(f'Duration check error: {e}')
        return 50.0, details


def get_media_duration(path: Path) -> Optional[float]:
    """Get duration of media file in seconds.

    Args:
        path: Path to media file

    Returns:
        Duration in seconds or None
    """
    try:
        result = subprocess.run(
            [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', str(path)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        data = json.loads(result.stdout)
        return float(data.get('format', {}).get('duration', 0))
    except Exception:
        return None


def score_metadata(session_path: Path) -> Tuple[float, Dict]:
    """Score metadata completeness.

    Checks:
    - metadata.yaml exists in youtube_package
    - Has title, description, tags
    - VTT subtitles exist
    - Thumbnail exists

    Args:
        session_path: Session directory path

    Returns:
        (score 0-100, details dict)
    """
    details = {'checks': {}, 'issues': []}

    youtube_pkg = session_path / 'output' / 'youtube_package'

    # Check metadata.yaml
    metadata_path = youtube_pkg / 'metadata.yaml'
    if metadata_path.exists():
        details['checks']['metadata_file'] = True
        try:
            with open(metadata_path) as f:
                metadata = yaml.safe_load(f)

            details['checks']['has_title'] = bool(metadata.get('title'))
            details['checks']['has_description'] = bool(metadata.get('description'))
            details['checks']['has_tags'] = bool(metadata.get('tags'))

            if not metadata.get('title'):
                details['issues'].append('Missing title')
            if not metadata.get('description'):
                details['issues'].append('Missing description')
            if not metadata.get('tags'):
                details['issues'].append('Missing tags')

        except Exception as e:
            details['issues'].append(f'Failed to parse metadata: {e}')
            details['checks']['has_title'] = False
            details['checks']['has_description'] = False
            details['checks']['has_tags'] = False
    else:
        details['issues'].append('No metadata.yaml found')
        details['checks']['metadata_file'] = False
        details['checks']['has_title'] = False
        details['checks']['has_description'] = False
        details['checks']['has_tags'] = False

    # Check VTT subtitles
    vtt_path = youtube_pkg / 'subtitles.vtt'
    details['checks']['has_vtt'] = vtt_path.exists()
    if not vtt_path.exists():
        details['issues'].append('Missing subtitles.vtt')

    # Check thumbnail
    thumbnail_path = youtube_pkg / 'thumbnail.png'
    if not thumbnail_path.exists():
        thumbnail_path = session_path / 'output' / 'youtube_thumbnail.png'
    details['checks']['has_thumbnail'] = thumbnail_path.exists()
    if not thumbnail_path.exists():
        details['issues'].append('Missing thumbnail')

    # Calculate score
    checks = [
        details['checks'].get('metadata_file', False),
        details['checks'].get('has_title', False),
        details['checks'].get('has_description', False),
        details['checks'].get('has_tags', False),
        details['checks'].get('has_vtt', False),
        details['checks'].get('has_thumbnail', False),
    ]

    score = (sum(checks) / len(checks)) * 100
    return score, details


# ==================== CLI ====================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Quality Scorer')
    parser.add_argument('--session', type=str, required=True, help='Session directory path')
    parser.add_argument('--detailed', action='store_true', help='Show detailed breakdown')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    session_path = Path(args.session)
    if not session_path.exists():
        print(f"Session not found: {session_path}")
        exit(1)

    result = compute_quality_score(session_path, detailed=args.detailed or args.json)

    if args.json:
        print(json.dumps(result, indent=2))
    elif args.detailed:
        print(f"\n=== Quality Score: {result['total_score']}/100 ===")
        print(f"\nSession: {result['session_name']}")
        print("\nComponent Scores:")
        for component, score in result['component_scores'].items():
            weight = result['weights'][component]
            raw = score / weight if weight else 0
            print(f"  {component}: {raw:.0f} x {weight:.0%} = {score:.1f}")
        print("\nDetails:")
        for component, detail in result['details'].items():
            issues = detail.get('issues', [])
            if issues:
                print(f"  {component} issues: {', '.join(issues)}")
    else:
        print(f"Quality score: {result}")
