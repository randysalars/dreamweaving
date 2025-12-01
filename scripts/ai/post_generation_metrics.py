#!/usr/bin/env python3
"""
Post-Generation Metrics Collection

Runs after session generation to:
1. Collect actual duration and quality metrics
2. Compare with targets and pre-generation estimates
3. Record lessons learned automatically
4. Update the knowledge base for future sessions

Usage:
    python3 post_generation_metrics.py sessions/my-session
    python3 post_generation_metrics.py sessions/my-session --record-lesson  # Auto-record lessons
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_manifest(session_path: Path) -> Optional[Dict]:
    """Load session manifest."""
    manifest_path = session_path / 'manifest.yaml'
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            return yaml.safe_load(f)
    return None


def get_audio_metrics(audio_path: Path) -> Optional[Dict]:
    """Get audio file metrics using ffprobe."""
    if not audio_path.exists():
        return None

    try:
        # Get duration and format info
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', str(audio_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None

        data = json.loads(result.stdout)
        format_info = data.get('format', {})
        streams = data.get('streams', [])

        # Find audio stream
        audio_stream = None
        for stream in streams:
            if stream.get('codec_type') == 'audio':
                audio_stream = stream
                break

        duration = float(format_info.get('duration', 0))

        metrics = {
            'duration_seconds': duration,
            'duration_minutes': duration / 60,
            'duration_formatted': format_duration(duration),
            'file_size_mb': int(format_info.get('size', 0)) / (1024 * 1024),
            'bit_rate_kbps': int(format_info.get('bit_rate', 0)) / 1000,
            'format': format_info.get('format_name', 'unknown'),
        }

        if audio_stream:
            metrics['sample_rate'] = int(audio_stream.get('sample_rate', 0))
            metrics['channels'] = audio_stream.get('channels', 0)
            metrics['codec'] = audio_stream.get('codec_name', 'unknown')

        return metrics
    except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError):
        return None


def get_video_metrics(video_path: Path) -> Optional[Dict]:
    """Get video file metrics using ffprobe."""
    if not video_path.exists():
        return None

    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None

        data = json.loads(result.stdout)
        format_info = data.get('format', {})
        streams = data.get('streams', [])

        video_stream = None
        audio_stream = None
        for stream in streams:
            if stream.get('codec_type') == 'video' and not video_stream:
                video_stream = stream
            elif stream.get('codec_type') == 'audio' and not audio_stream:
                audio_stream = stream

        duration = float(format_info.get('duration', 0))

        metrics = {
            'duration_seconds': duration,
            'duration_minutes': duration / 60,
            'duration_formatted': format_duration(duration),
            'file_size_mb': int(format_info.get('size', 0)) / (1024 * 1024),
            'bit_rate_kbps': int(format_info.get('bit_rate', 0)) / 1000,
        }

        if video_stream:
            metrics['video'] = {
                'codec': video_stream.get('codec_name', 'unknown'),
                'width': video_stream.get('width', 0),
                'height': video_stream.get('height', 0),
                'fps': eval_fps(video_stream.get('r_frame_rate', '0/1')),
            }

        if audio_stream:
            metrics['audio'] = {
                'codec': audio_stream.get('codec_name', 'unknown'),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': audio_stream.get('channels', 0),
            }

        return metrics
    except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError):
        return None


def eval_fps(fps_str: str) -> float:
    """Evaluate FPS string like '30/1' to float."""
    try:
        if '/' in fps_str:
            num, den = fps_str.split('/')
            return float(num) / float(den) if float(den) != 0 else 0
        return float(fps_str)
    except (ValueError, ZeroDivisionError):
        return 0


def format_duration(seconds: float) -> str:
    """Format seconds as MM:SS or HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def count_vtt_captions(vtt_path: Path) -> int:
    """Count number of captions in VTT file."""
    if not vtt_path.exists():
        return 0

    try:
        with open(vtt_path, 'r') as f:
            content = f.read()
        # Count caption blocks (lines with -->)
        return content.count('-->')
    except IOError:
        return 0


def analyze_binaural(manifest: Dict, session_path: Path) -> Dict:
    """Analyze binaural configuration and what was actually used."""
    binaural_config = manifest.get('audio', {}).get('binaural', {})

    analysis = {
        'enabled': binaural_config.get('enabled', True),
        'type': 'unknown',
        'carrier_freq': binaural_config.get('base_frequency', 200),
    }

    if 'progression' in binaural_config:
        analysis['type'] = 'dynamic'
        analysis['stages'] = len(binaural_config['progression'])
        # Check for gamma burst
        has_gamma = any(
            p.get('frequency', 0) >= 30
            for p in binaural_config['progression']
        )
        analysis['has_gamma_burst'] = has_gamma
    elif 'beat_frequency' in binaural_config:
        analysis['type'] = 'static'
        analysis['beat_frequency'] = binaural_config['beat_frequency']
    else:
        # Check for frequency map file
        freq_map_path = session_path / 'working_files' / 'binaural_frequency_map.json'
        if freq_map_path.exists():
            analysis['type'] = 'frequency_map'
            try:
                with open(freq_map_path, 'r') as f:
                    freq_map = json.load(f)
                analysis['stages'] = len(freq_map.get('frequency_events', []))
            except (json.JSONDecodeError, IOError):
                pass

    return analysis


def compare_with_target(actual: float, target: float) -> Dict:
    """Compare actual duration with target."""
    difference = actual - target
    difference_percent = (difference / target) * 100 if target > 0 else 0

    return {
        'actual': actual,
        'target': target,
        'difference': difference,
        'difference_percent': difference_percent,
        'status': 'ok' if abs(difference_percent) <= 10 else ('short' if difference < 0 else 'long'),
    }


def generate_issues(metrics: Dict, manifest: Dict) -> List[Dict]:
    """Generate issues based on metrics analysis."""
    issues = []

    # Duration check
    if 'duration_comparison' in metrics and metrics['duration_comparison']:
        comp = metrics['duration_comparison']
        if comp['status'] != 'ok':
            severity = 'warning' if abs(comp['difference_percent']) <= 20 else 'error'
            issues.append({
                'id': f"ISSUE-DUR-{datetime.now().strftime('%H%M%S')}",
                'category': 'duration_mismatch',
                'severity': severity,
                'description': f"Duration {comp['actual']:.1f} min vs target {comp['target']} min ({comp['difference_percent']:+.0f}%)",
                'impact': 'Session duration does not match intended experience length',
            })

    # Binaural check
    binaural = metrics.get('binaural_analysis', {})
    if binaural.get('type') == 'static':
        issues.append({
            'id': f"ISSUE-BIN-{datetime.now().strftime('%H%M%S')}",
            'category': 'binaural_implementation',
            'severity': 'medium',
            'description': 'Static binaural frequency used instead of dynamic progression',
            'impact': 'Reduced effectiveness - missing state transitions',
            'recommendation': 'Use generate_dynamic_binaural.py with a preset for future sessions',
        })

    return issues


def generate_successes(metrics: Dict) -> List[Dict]:
    """Generate list of things that worked well."""
    successes = []

    # Audio generation
    if metrics.get('audio_metrics'):
        audio = metrics['audio_metrics']
        details = [
            f"Duration: {audio.get('duration_formatted', 'N/A')}",
            f"Sample rate: {audio.get('sample_rate', 'N/A')} Hz",
            f"File size: {audio.get('file_size_mb', 0):.1f} MB",
        ]
        successes.append({
            'category': 'audio_generation',
            'description': 'Audio pipeline completed successfully',
            'details': details,
        })

    # Video generation
    if metrics.get('video_metrics'):
        video = metrics['video_metrics']
        video_info = video.get('video', {})
        details = [
            f"Resolution: {video_info.get('width', 0)}x{video_info.get('height', 0)}",
            f"FPS: {video_info.get('fps', 0):.0f}",
            f"Duration: {video.get('duration_formatted', 'N/A')}",
            f"File size: {video.get('file_size_mb', 0):.1f} MB",
        ]
        successes.append({
            'category': 'video_generation',
            'description': 'Video assembly completed successfully',
            'details': details,
        })

    # VTT captions
    if metrics.get('vtt_caption_count', 0) > 0:
        successes.append({
            'category': 'subtitle_generation',
            'description': f"Generated {metrics['vtt_caption_count']} captions",
            'details': ['Timing synchronized with audio'],
        })

    return successes


def save_session_learning(
    session_path: Path,
    session_name: str,
    metrics: Dict,
    issues: List[Dict],
    successes: List[Dict]
):
    """Save session learning report."""
    knowledge_dir = Path('knowledge/session_learnings')
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"{session_name}_{date_str}.yaml"
    filepath = knowledge_dir / filename

    report = {
        'session': {
            'name': session_name,
            'date': date_str,
            'duration_actual': metrics.get('audio_metrics', {}).get('duration_minutes', 0),
            'duration_target': metrics.get('manifest', {}).get('duration'),
            'status': 'completed',
        },
        'metrics': {
            'audio': metrics.get('audio_metrics'),
            'video': metrics.get('video_metrics'),
            'binaural': metrics.get('binaural_analysis'),
            'captions': metrics.get('vtt_caption_count'),
        },
        'issues': issues,
        'successes': successes,
        'generated_at': datetime.now().isoformat(),
    }

    with open(filepath, 'w') as f:
        yaml.dump(report, f, default_flow_style=False, sort_keys=False)

    return filepath


def update_lessons_learned(issues: List[Dict], session_name: str):
    """Update global lessons learned with new insights."""
    lessons_path = Path('knowledge/lessons_learned.yaml')

    if lessons_path.exists():
        with open(lessons_path, 'r') as f:
            lessons_data = yaml.safe_load(f) or {}
    else:
        lessons_data = {'lessons': [], 'metadata': {}}

    existing_lessons = lessons_data.get('lessons', [])

    # Only add lessons for significant issues
    for issue in issues:
        if issue.get('severity') in ['error', 'high']:
            # Check if similar lesson exists
            similar_exists = any(
                issue['category'] in l.get('tags', [])
                for l in existing_lessons
            )

            if not similar_exists:
                new_lesson = {
                    'id': f"L{len(existing_lessons) + 1:03d}",
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'session': session_name,
                    'category': issue['category'],
                    'finding': issue['description'],
                    'action': issue.get('recommendation', 'Review and address'),
                    'priority': 'high' if issue['severity'] == 'error' else 'medium',
                    'tags': [issue['category']],
                    'auto_generated': True,
                }
                existing_lessons.append(new_lesson)

    lessons_data['lessons'] = existing_lessons
    lessons_data['metadata'] = {
        'last_updated': datetime.now().isoformat(),
        'total_lessons': len(existing_lessons),
    }

    with open(lessons_path, 'w') as f:
        yaml.dump(lessons_data, f, default_flow_style=False, sort_keys=False)


def print_report(session_name: str, metrics: Dict, issues: List[Dict], successes: List[Dict]):
    """Print the post-generation metrics report."""
    print("=" * 70)
    print("POST-GENERATION METRICS REPORT")
    print("=" * 70)
    print(f"\nSession: {session_name}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Audio metrics
    audio = metrics.get('audio_metrics')
    if audio:
        print(f"\n--- Audio Metrics ---")
        print(f"Duration: {audio.get('duration_formatted', 'N/A')} ({audio.get('duration_minutes', 0):.1f} min)")
        print(f"Format: {audio.get('format', 'N/A')} / {audio.get('codec', 'N/A')}")
        print(f"Sample rate: {audio.get('sample_rate', 'N/A')} Hz")
        print(f"Channels: {audio.get('channels', 'N/A')}")
        print(f"Bit rate: {audio.get('bit_rate_kbps', 0):.0f} kbps")
        print(f"File size: {audio.get('file_size_mb', 0):.1f} MB")

    # Duration comparison
    if metrics.get('duration_comparison'):
        comp = metrics['duration_comparison']
        print(f"\n--- Duration Comparison ---")
        print(f"Actual: {comp['actual']:.1f} minutes")
        print(f"Target: {comp['target']} minutes")
        diff = comp['difference']
        pct = comp['difference_percent']
        status_icon = '✅' if comp['status'] == 'ok' else ('⚠️' if abs(pct) <= 20 else '❌')
        print(f"Status: {status_icon} {diff:+.1f} min ({pct:+.0f}%)")

    # Binaural analysis
    binaural = metrics.get('binaural_analysis', {})
    if binaural:
        print(f"\n--- Binaural Analysis ---")
        print(f"Type: {binaural.get('type', 'unknown')}")
        print(f"Carrier frequency: {binaural.get('carrier_freq', 'N/A')} Hz")
        if binaural.get('type') == 'static':
            print(f"Beat frequency: {binaural.get('beat_frequency', 'N/A')} Hz")
        elif binaural.get('type') == 'dynamic':
            print(f"Stages: {binaural.get('stages', 0)}")
            print(f"Has gamma burst: {'Yes' if binaural.get('has_gamma_burst') else 'No'}")

    # Video metrics
    video = metrics.get('video_metrics')
    if video:
        print(f"\n--- Video Metrics ---")
        video_info = video.get('video', {})
        print(f"Duration: {video.get('duration_formatted', 'N/A')}")
        print(f"Resolution: {video_info.get('width', 0)}x{video_info.get('height', 0)}")
        print(f"FPS: {video_info.get('fps', 0):.0f}")
        print(f"File size: {video.get('file_size_mb', 0):.1f} MB")

    # VTT captions
    if metrics.get('vtt_caption_count'):
        print(f"\n--- Subtitles ---")
        print(f"Caption count: {metrics['vtt_caption_count']}")

    # Issues
    if issues:
        print(f"\n--- Issues Identified ({len(issues)}) ---")
        for issue in issues:
            icon = '❌' if issue['severity'] == 'error' else ('⚠️' if issue['severity'] == 'warning' else 'ℹ️')
            print(f"{icon} [{issue['category']}] {issue['description']}")
            if issue.get('recommendation'):
                print(f"   Recommendation: {issue['recommendation']}")

    # Successes
    if successes:
        print(f"\n--- Successes ({len(successes)}) ---")
        for success in successes:
            print(f"✅ {success['description']}")
            for detail in success.get('details', [])[:3]:
                print(f"   • {detail}")

    # Summary
    print(f"\n--- Summary ---")
    if not issues:
        print("✅ Session completed successfully with no issues")
    elif any(i['severity'] == 'error' for i in issues):
        print(f"❌ {len([i for i in issues if i['severity'] == 'error'])} critical issues found")
    else:
        print(f"⚠️ {len(issues)} minor issues to address in future sessions")

    print()


def main():
    parser = argparse.ArgumentParser(
        description='Post-generation metrics collection and analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sessions/my-session
  %(prog)s sessions/my-session --record-lesson
  %(prog)s sessions/my-session --json
"""
    )

    parser.add_argument('session_path', type=Path,
                       help='Path to session directory')
    parser.add_argument('--record-lesson', action='store_true',
                       help='Auto-record lessons learned')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')
    parser.add_argument('--save-report', action='store_true',
                       help='Save learning report to knowledge base')

    args = parser.parse_args()

    session_path = args.session_path
    session_name = session_path.name

    if not session_path.exists():
        print(f"Error: Session path not found: {session_path}", file=sys.stderr)
        return 1

    # Load manifest
    manifest = load_manifest(session_path)
    if not manifest:
        print(f"Warning: No manifest.yaml found in {session_path}", file=sys.stderr)
        manifest = {}

    # Collect metrics
    metrics: Dict[str, Any] = {'manifest': manifest}

    # Audio metrics - check multiple possible locations
    audio_paths = [
        session_path / 'output' / 'final.mp3',
        session_path / 'output' / f'{session_name.replace("-", "_")}.mp3',
        session_path / 'output' / 'voice.mp3',
    ]

    for audio_path in audio_paths:
        audio_metrics = get_audio_metrics(audio_path)
        if audio_metrics:
            metrics['audio_metrics'] = audio_metrics
            metrics['audio_file'] = str(audio_path)
            break

    # Video metrics
    video_paths = [
        session_path / 'output' / f'{session_name.replace("-", "_")}.mp4',
        session_path / 'output' / 'final.mp4',
    ]

    for video_path in video_paths:
        video_metrics = get_video_metrics(video_path)
        if video_metrics:
            metrics['video_metrics'] = video_metrics
            metrics['video_file'] = str(video_path)
            break

    # VTT caption count
    vtt_paths = [
        session_path / 'output' / f'{session_name.replace("-", "_")}.vtt',
        session_path / 'output' / 'subtitles.vtt',
    ]

    for vtt_path in vtt_paths:
        count = count_vtt_captions(vtt_path)
        if count > 0:
            metrics['vtt_caption_count'] = count
            break

    # Duration comparison
    target_duration = manifest.get('duration')
    if target_duration and metrics.get('audio_metrics'):
        actual_duration = metrics['audio_metrics']['duration_minutes']
        metrics['duration_comparison'] = compare_with_target(actual_duration, target_duration)

    # Binaural analysis
    metrics['binaural_analysis'] = analyze_binaural(manifest, session_path)

    # Generate issues and successes
    issues = generate_issues(metrics, manifest)
    successes = generate_successes(metrics)

    # Output
    if args.json:
        output = {
            'session': session_name,
            'metrics': metrics,
            'issues': issues,
            'successes': successes,
            'generated_at': datetime.now().isoformat(),
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print_report(session_name, metrics, issues, successes)

    # Save learning report
    if args.save_report:
        report_path = save_session_learning(session_path, session_name, metrics, issues, successes)
        print(f"📝 Learning report saved: {report_path}")

    # Record lessons
    if args.record_lesson and issues:
        update_lessons_learned(issues, session_name)
        print(f"📚 Lessons learned updated")

    return 0


if __name__ == '__main__':
    sys.exit(main())
