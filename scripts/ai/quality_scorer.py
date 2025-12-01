#!/usr/bin/env python3
"""
Quality Scorer for Dreamweaving

Validates and scores session components:
- SSML script quality
- Manifest completeness
- Audio quality metrics
- Overall session readiness

Usage:
    python3 scripts/ai/quality_scorer.py sessions/{session}
    python3 scripts/ai/quality_scorer.py sessions/{session} --component script
"""

import os
import sys
import yaml
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import subprocess
import json


class QualityReport:
    """Structured quality report."""

    def __init__(self, component: str):
        self.component = component
        self.score = 100
        self.issues: List[Dict] = []
        self.warnings: List[Dict] = []
        self.passed: List[str] = []

    def add_issue(self, description: str, severity: str = "error", deduction: int = 10):
        """Add an issue (reduces score)."""
        self.issues.append({
            "description": description,
            "severity": severity,
            "deduction": deduction,
        })
        self.score = max(0, self.score - deduction)

    def add_warning(self, description: str):
        """Add a warning (doesn't affect score)."""
        self.warnings.append({"description": description})

    def add_pass(self, description: str):
        """Mark something as passed."""
        self.passed.append(description)

    def to_dict(self) -> Dict:
        return {
            "component": self.component,
            "score": self.score,
            "grade": self._get_grade(),
            "issues": self.issues,
            "warnings": self.warnings,
            "passed": self.passed,
        }

    def _get_grade(self) -> str:
        if self.score >= 90:
            return "A"
        elif self.score >= 80:
            return "B"
        elif self.score >= 70:
            return "C"
        elif self.score >= 60:
            return "D"
        else:
            return "F"


def score_ssml(session_path: Path) -> QualityReport:
    """Score SSML script quality."""
    report = QualityReport("ssml_script")

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
        report.add_issue("No SSML script found", deduction=100)
        return report

    with open(ssml_path, 'r') as f:
        content = f.read()

    # Basic structure checks
    if not content.strip().startswith('<?xml'):
        report.add_issue("Missing XML declaration", deduction=5)
    else:
        report.add_pass("XML declaration present")

    if '<speak' not in content:
        report.add_issue("Missing <speak> root element", deduction=20)
    else:
        report.add_pass("<speak> root element present")

    # Check for balanced tags
    open_tags = len(re.findall(r'<prosody[^>]*>', content))
    close_tags = len(re.findall(r'</prosody>', content))
    if open_tags != close_tags:
        report.add_issue(f"Unbalanced prosody tags: {open_tags} open, {close_tags} close", deduction=15)
    else:
        report.add_pass("Prosody tags balanced")

    # Check for break tags (essential for hypnotic pacing)
    break_count = len(re.findall(r'<break[^>]*/>', content))
    if break_count < 10:
        report.add_issue(f"Too few break tags ({break_count}). Hypnotic scripts need pauses.", deduction=10)
    elif break_count < 30:
        report.add_warning(f"Only {break_count} break tags. Consider adding more pauses.")
    else:
        report.add_pass(f"Good use of pauses ({break_count} break tags)")

    # Check for hypnotic elements
    emphasis_count = len(re.findall(r'<emphasis[^>]*>', content))
    if emphasis_count < 5:
        report.add_warning("Few emphasis tags. Consider emphasizing key suggestions.")
    else:
        report.add_pass(f"Good use of emphasis ({emphasis_count} tags)")

    # Check word count (typical session: 2000-5000 words)
    text_only = re.sub(r'<[^>]+>', '', content)
    word_count = len(text_only.split())
    if word_count < 500:
        report.add_issue(f"Script too short ({word_count} words)", deduction=15)
    elif word_count < 1500:
        report.add_warning(f"Script may be short ({word_count} words)")
    elif word_count > 8000:
        report.add_warning(f"Script is very long ({word_count} words)")
    else:
        report.add_pass(f"Good script length ({word_count} words)")

    # Check for section markers
    sections = re.findall(r'<!-- SECTION:?\s*(\w+)', content, re.IGNORECASE)
    if len(sections) < 3:
        report.add_warning("Few section markers. Consider organizing with <!-- SECTION --> comments.")
    else:
        report.add_pass(f"Well organized ({len(sections)} sections)")

    return report


def score_manifest(session_path: Path) -> QualityReport:
    """Score manifest completeness."""
    report = QualityReport("manifest")

    manifest_path = session_path / 'manifest.yaml'
    if not manifest_path.exists():
        report.add_issue("No manifest.yaml found", deduction=100)
        return report

    with open(manifest_path, 'r') as f:
        manifest = yaml.safe_load(f)

    if not manifest:
        report.add_issue("Empty manifest", deduction=100)
        return report

    # Required fields
    required_fields = ['title', 'description', 'duration']
    for field in required_fields:
        if field not in manifest:
            report.add_issue(f"Missing required field: {field}", deduction=15)
        else:
            report.add_pass(f"Has {field}")

    # Voice configuration
    if 'voice' not in manifest:
        report.add_issue("Missing voice configuration", deduction=10)
    else:
        voice = manifest['voice']
        if 'id' not in voice:
            report.add_issue("Missing voice.id", deduction=10)
        else:
            report.add_pass("Voice ID configured")

    # Audio configuration
    if 'audio' not in manifest:
        report.add_warning("No audio configuration section")
    else:
        audio = manifest['audio']
        if 'binaural' not in audio:
            report.add_warning("No binaural configuration")
        else:
            report.add_pass("Binaural configured")

        if 'background' not in audio:
            report.add_warning("No background audio configuration")
        else:
            report.add_pass("Background audio configured")

    # Video configuration (optional but good)
    if 'video' in manifest:
        report.add_pass("Video configuration present")
    else:
        report.add_warning("No video configuration")

    return report


def score_audio(session_path: Path) -> QualityReport:
    """Score audio file quality."""
    report = QualityReport("audio")

    output_dir = session_path / 'output'
    if not output_dir.exists():
        report.add_issue("No output directory", deduction=50)
        return report

    # Check for voice audio
    voice_path = output_dir / 'voice.mp3'
    if not voice_path.exists():
        report.add_warning("No voice.mp3 generated yet")
    else:
        report.add_pass("Voice audio exists")
        # Check duration
        duration = get_audio_duration(str(voice_path))
        if duration:
            if duration < 60:
                report.add_warning(f"Voice very short ({duration:.0f}s)")
            else:
                report.add_pass(f"Voice duration: {duration:.0f}s")

    # Check for final audio
    final_path = output_dir / 'final.mp3'
    if not final_path.exists():
        report.add_warning("No final.mp3 generated yet")
    else:
        report.add_pass("Final audio exists")
        duration = get_audio_duration(str(final_path))
        if duration:
            report.add_pass(f"Final duration: {duration:.0f}s")

    # Check audio levels (basic)
    if final_path.exists():
        levels = check_audio_levels(str(final_path))
        if levels:
            if levels['peak'] > -1:
                report.add_issue("Audio may be clipping (peak > -1dB)", deduction=10)
            elif levels['peak'] < -12:
                report.add_warning(f"Audio may be too quiet (peak: {levels['peak']:.1f}dB)")
            else:
                report.add_pass(f"Good audio levels (peak: {levels['peak']:.1f}dB)")

    return report


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
    except Exception:
        return None


def check_audio_levels(audio_path: str) -> Optional[Dict]:
    """Check audio levels using ffmpeg."""
    try:
        result = subprocess.run(
            ['ffmpeg', '-i', audio_path, '-af', 'volumedetect', '-f', 'null', '-'],
            capture_output=True, text=True
        )
        stderr = result.stderr

        peak = None
        mean = None

        peak_match = re.search(r'max_volume:\s*([-\d.]+)\s*dB', stderr)
        if peak_match:
            peak = float(peak_match.group(1))

        mean_match = re.search(r'mean_volume:\s*([-\d.]+)\s*dB', stderr)
        if mean_match:
            mean = float(mean_match.group(1))

        if peak is not None:
            return {"peak": peak, "mean": mean}
    except Exception:
        pass
    return None


def score_session_readiness(session_path: Path) -> QualityReport:
    """Overall session readiness score."""
    report = QualityReport("readiness")

    # Check all required directories
    required_dirs = ['working_files', 'output']
    for dir_name in required_dirs:
        dir_path = session_path / dir_name
        if not dir_path.exists():
            report.add_issue(f"Missing directory: {dir_name}", deduction=10)
        else:
            report.add_pass(f"Directory exists: {dir_name}")

    # Check images for video
    images_dir = session_path / 'images_uploaded'
    if images_dir.exists():
        images = list(images_dir.glob('*.png')) + list(images_dir.glob('*.jpg'))
        if len(images) >= 3:
            report.add_pass(f"Images ready ({len(images)} found)")
        else:
            report.add_warning(f"Only {len(images)} images found")
    else:
        report.add_warning("No images_uploaded directory")

    # Check for YouTube package
    youtube_dir = session_path / 'output' / 'youtube_package'
    if youtube_dir.exists():
        report.add_pass("YouTube package directory exists")
    else:
        report.add_warning("No YouTube package yet")

    return report


def generate_full_report(session_path: Path) -> Dict:
    """Generate comprehensive quality report."""
    reports = {
        "ssml": score_ssml(session_path),
        "manifest": score_manifest(session_path),
        "audio": score_audio(session_path),
        "readiness": score_session_readiness(session_path),
    }

    # Calculate overall score
    total_score = sum(r.score for r in reports.values()) / len(reports)

    return {
        "session": session_path.name,
        "overall_score": round(total_score, 1),
        "overall_grade": get_grade(total_score),
        "components": {name: report.to_dict() for name, report in reports.items()},
    }


def get_grade(score: float) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def print_report(report: Dict):
    """Print formatted quality report."""
    print(f"\n{'='*60}")
    print(f"Quality Report: {report['session']}")
    print(f"{'='*60}")
    print(f"\nOverall Score: {report['overall_score']}/100 ({report['overall_grade']})")

    for name, component in report['components'].items():
        print(f"\n--- {component['component'].upper()} ---")
        print(f"Score: {component['score']}/100 ({component['grade']})")

        if component['passed']:
            print(f"  Passed ({len(component['passed'])}):")
            for item in component['passed'][:5]:  # Show first 5
                print(f"    + {item}")
            if len(component['passed']) > 5:
                print(f"    ... and {len(component['passed'])-5} more")

        if component['warnings']:
            print(f"  Warnings ({len(component['warnings'])}):")
            for w in component['warnings']:
                print(f"    ! {w['description']}")

        if component['issues']:
            print(f"  Issues ({len(component['issues'])}):")
            for issue in component['issues']:
                print(f"    X {issue['description']} (-{issue['deduction']})")


def main():
    parser = argparse.ArgumentParser(description='Score session quality')
    parser.add_argument('session_path', help='Path to session directory')
    parser.add_argument('--component', choices=['ssml', 'manifest', 'audio', 'readiness'],
                       help='Score only specific component')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    session_path = Path(args.session_path)

    if not session_path.exists():
        print(f"Error: Session path does not exist: {session_path}")
        sys.exit(1)

    if args.component:
        score_funcs = {
            'ssml': score_ssml,
            'manifest': score_manifest,
            'audio': score_audio,
            'readiness': score_session_readiness,
        }
        report = score_funcs[args.component](session_path).to_dict()
    else:
        report = generate_full_report(session_path)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if args.component:
            print(f"\n{args.component.upper()} Score: {report['score']}/100 ({report['grade']})")
            for item in report['passed']:
                print(f"  + {item}")
            for w in report['warnings']:
                print(f"  ! {w['description']}")
            for issue in report['issues']:
                print(f"  X {issue['description']}")
        else:
            print_report(report)


if __name__ == "__main__":
    main()
