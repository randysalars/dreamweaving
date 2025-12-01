#!/usr/bin/env python3
"""
Pre-Generation Check and Recommendations

Runs before voice generation to:
1. Estimate duration and compare with target
2. Query lessons learned for recommendations
3. Validate configuration
4. Suggest improvements based on accumulated knowledge

Usage:
    python3 pre_generation_check.py sessions/my-session
    python3 pre_generation_check.py sessions/my-session --fix  # Apply auto-fixes
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utilities.estimate_duration import estimate_duration, compare_with_target, suggest_adjustments


def load_manifest(session_path: Path) -> Optional[Dict]:
    """Load session manifest."""
    manifest_path = session_path / 'manifest.yaml'
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            return yaml.safe_load(f)
    return None


def load_ssml(session_path: Path) -> Optional[str]:
    """Load SSML script."""
    ssml_paths = [
        session_path / 'working_files' / 'script.ssml',
        session_path / 'script.ssml',
    ]
    for path in ssml_paths:
        if path.exists():
            with open(path, 'r') as f:
                return f.read()
    return None


def load_lessons_learned() -> Dict:
    """Load lessons from knowledge base."""
    lessons_path = Path('knowledge/lessons_learned.yaml')
    if lessons_path.exists():
        with open(lessons_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def get_relevant_lessons(manifest: Dict, lessons: Dict) -> List[Dict]:
    """Get lessons relevant to this session's configuration."""
    relevant = []

    all_lessons = lessons.get('lessons', [])

    # Filter by tags that match this session
    theme = manifest.get('theme', '')
    session_tags = [theme.lower()] if theme else []

    for lesson in all_lessons:
        # Include high/critical priority lessons
        if lesson.get('priority') in ['critical', 'high']:
            relevant.append(lesson)
            continue

        # Include lessons matching session tags
        lesson_tags = [t.lower() for t in lesson.get('tags', [])]
        if any(tag in lesson_tags for tag in session_tags):
            relevant.append(lesson)

    return relevant


def check_binaural_config(manifest: Dict) -> List[Dict]:
    """Check binaural configuration for issues."""
    issues = []

    binaural_config = manifest.get('audio', {}).get('binaural', {})

    if not binaural_config.get('enabled', True):
        return issues

    # Check if using static frequency without progression
    if 'beat_frequency' in binaural_config and 'progression' not in binaural_config:
        issues.append({
            'severity': 'warning',
            'category': 'binaural',
            'message': 'Using static binaural frequency. Dynamic progressions are more effective.',
            'recommendation': 'Add progression definition or use generate_dynamic_binaural.py with a preset',
            'lesson_id': 'L001'
        })

    return issues


def check_voice_config(manifest: Dict) -> List[Dict]:
    """Check voice configuration for issues."""
    issues = []

    voice_config = manifest.get('voice', {})
    voice_id = voice_config.get('id', '')

    # Check for known voice gender issues
    male_voices = ['en-US-Neural2-A', 'en-US-Neural2-D', 'en-US-Neural2-I', 'en-US-Neural2-J']
    female_voices = ['en-US-Neural2-C', 'en-US-Neural2-E', 'en-US-Neural2-F']

    if voice_id in male_voices:
        issues.append({
            'severity': 'info',
            'category': 'voice',
            'message': f'{voice_id} is a MALE voice',
            'recommendation': f'For female voice, use: {", ".join(female_voices)}',
            'lesson_id': 'L005'
        })

    return issues


def check_duration(
    ssml_content: str,
    manifest: Dict
) -> Dict:
    """Check duration estimation vs target."""
    speaking_rate = manifest.get('voice', {}).get('speaking_rate', 1.0)
    target_minutes = manifest.get('duration')

    estimate = estimate_duration(ssml_content, speaking_rate)

    result = {
        'estimated_minutes': estimate['total_minutes'],
        'word_count': estimate['word_count'],
        'pause_seconds': estimate['pause_time_seconds'],
        'issues': []
    }

    if target_minutes:
        comparison = compare_with_target(estimate['total_minutes'], target_minutes)
        result['target_minutes'] = target_minutes
        result['difference_percent'] = comparison['difference_percent']

        if comparison['status'] != 'ok':
            suggestions = suggest_adjustments(comparison)
            result['issues'].append({
                'severity': 'warning' if abs(comparison['difference_percent']) <= 20 else 'error',
                'category': 'duration',
                'message': f"Duration mismatch: estimated {estimate['total_minutes']:.1f} min vs target {target_minutes} min ({comparison['difference_percent']:+.0f}%)",
                'recommendation': suggestions[0] if suggestions else 'Adjust script length',
                'lesson_id': 'L004'
            })

    return result


def generate_recommendations(
    manifest: Dict,
    lessons: List[Dict],
    issues: List[Dict]
) -> Dict:
    """Generate recommendations based on lessons and issues."""
    recommendations = {
        'critical': [],
        'high': [],
        'medium': [],
        'info': []
    }

    # Add lesson-based recommendations
    for lesson in lessons:
        priority = lesson.get('priority', 'medium')
        rec = {
            'source': 'lesson',
            'lesson_id': lesson.get('id'),
            'message': lesson.get('finding'),
            'action': lesson.get('action'),
        }

        if priority == 'critical':
            recommendations['critical'].append(rec)
        elif priority == 'high':
            recommendations['high'].append(rec)
        else:
            recommendations['medium'].append(rec)

    # Add issue-based recommendations
    for issue in issues:
        severity = issue.get('severity', 'info')
        rec = {
            'source': 'check',
            'message': issue['message'],
            'action': issue.get('recommendation', ''),
        }

        if severity == 'error':
            recommendations['critical'].append(rec)
        elif severity == 'warning':
            recommendations['high'].append(rec)
        else:
            recommendations['info'].append(rec)

    return recommendations


def print_report(
    session_name: str,
    duration_result: Dict,
    issues: List[Dict],
    recommendations: Dict
):
    """Print the pre-generation check report."""
    print("=" * 70)
    print("PRE-GENERATION CHECK")
    print("=" * 70)
    print(f"\nSession: {session_name}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Duration
    print(f"\n--- Duration Analysis ---")
    print(f"Word count: {duration_result['word_count']:,}")
    print(f"Pause time: {duration_result['pause_seconds']:.0f} seconds")
    print(f"Estimated: {duration_result['estimated_minutes']:.1f} minutes")
    if 'target_minutes' in duration_result:
        print(f"Target: {duration_result['target_minutes']} minutes")
        diff = duration_result.get('difference_percent', 0)
        status = '✅' if abs(diff) <= 10 else ('⚠️' if abs(diff) <= 20 else '❌')
        print(f"Status: {status} ({diff:+.0f}%)")

    # Issues
    if issues:
        print(f"\n--- Issues Found ({len(issues)}) ---")
        for issue in issues:
            icon = '❌' if issue['severity'] == 'error' else ('⚠️' if issue['severity'] == 'warning' else 'ℹ️')
            print(f"{icon} [{issue['category']}] {issue['message']}")

    # Recommendations
    print(f"\n--- Recommendations ---")

    if recommendations['critical']:
        print("\n🔴 CRITICAL:")
        for rec in recommendations['critical']:
            print(f"  • {rec['message']}")
            if rec.get('action'):
                print(f"    Action: {rec['action']}")

    if recommendations['high']:
        print("\n🟠 HIGH PRIORITY:")
        for rec in recommendations['high']:
            print(f"  • {rec['message']}")
            if rec.get('action'):
                print(f"    Action: {rec['action']}")

    if recommendations['medium']:
        print("\n🟡 SUGGESTIONS:")
        for rec in recommendations['medium'][:3]:  # Limit to top 3
            print(f"  • {rec['message']}")

    if not any(recommendations.values()):
        print("  ✅ No issues found")

    # Summary
    print(f"\n--- Summary ---")
    total_issues = len(issues)
    critical_count = len(recommendations['critical'])
    high_count = len(recommendations['high'])

    if critical_count > 0:
        print(f"❌ {critical_count} critical issues - address before generation")
    elif high_count > 0:
        print(f"⚠️ {high_count} high-priority items - consider addressing")
    else:
        print("✅ Ready for generation")

    print()


def main():
    parser = argparse.ArgumentParser(
        description='Pre-generation check and recommendations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sessions/my-session
  %(prog)s sessions/my-session --json
"""
    )

    parser.add_argument('session_path', type=Path,
                       help='Path to session directory')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')
    parser.add_argument('--strict', action='store_true',
                       help='Exit with error code if critical issues found')

    args = parser.parse_args()

    session_path = args.session_path

    if not session_path.exists():
        print(f"Error: Session path not found: {session_path}", file=sys.stderr)
        return 1

    # Load configuration
    manifest = load_manifest(session_path)
    if not manifest:
        print(f"Error: No manifest.yaml found in {session_path}", file=sys.stderr)
        return 1

    ssml_content = load_ssml(session_path)
    if not ssml_content:
        print(f"Error: No SSML script found in {session_path}", file=sys.stderr)
        return 1

    # Load lessons
    lessons_data = load_lessons_learned()

    # Run checks
    all_issues = []

    # Duration check
    duration_result = check_duration(ssml_content, manifest)
    all_issues.extend(duration_result.get('issues', []))

    # Binaural check
    all_issues.extend(check_binaural_config(manifest))

    # Voice check
    all_issues.extend(check_voice_config(manifest))

    # Get relevant lessons
    relevant_lessons = get_relevant_lessons(manifest, lessons_data)

    # Generate recommendations
    recommendations = generate_recommendations(manifest, relevant_lessons, all_issues)

    # Output
    if args.json:
        import json
        output = {
            'session': str(session_path),
            'duration': duration_result,
            'issues': all_issues,
            'recommendations': recommendations,
            'lessons_applied': len(relevant_lessons),
        }
        print(json.dumps(output, indent=2))
    else:
        print_report(
            session_path.name,
            duration_result,
            all_issues,
            recommendations
        )

    # Exit code
    if args.strict and recommendations['critical']:
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
