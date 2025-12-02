#!/usr/bin/env python3
"""
Session Consistency Report Generator

Analyzes ALL sessions in the project and generates a comprehensive
consistency report comparing them against production standards and
each other.

This tool ensures uniform quality across the entire session library.

Usage:
    python3 session_consistency_report.py
    python3 session_consistency_report.py --output report.md
    python3 session_consistency_report.py --format html
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml


# =============================================================================
# STANDARDS REFERENCE
# =============================================================================

STANDARDS = {
    "word_count": {"min": 3200, "max": 4200, "target": 3750},
    "duration_min": {"min": 20, "max": 35, "target": 28},
    "anchor_count": {"min": 3, "max": 7, "target": 5},
    "sense_coverage": {"min": 4, "max": 5, "target": 5},
    "section_count": {"min": 5, "max": 5, "target": 5},
    "lufs_target": -14,
    "true_peak_target": -1.5,
}

MANDATORY_ENHANCEMENTS = [
    "warmth_drive",
    "deessing",
    "whisper_overlay",
    "subharmonic",
    "double_voice",
    "room_tone",
    "cuddle_waves",
    "echo",
]

SECTION_ORDER = ["pretalk", "induction", "journey", "integration", "closing"]


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class SessionMetrics:
    """Metrics extracted from a single session."""
    name: str
    path: Path

    # Basic info
    created_date: Optional[str] = None
    duration_seconds: int = 0

    # Script metrics
    word_count: int = 0
    anchor_count: int = 0
    sense_coverage: int = 0
    break_count: int = 0
    section_count: int = 0

    # Audio settings
    voice_name: str = ""
    voice_rate: float = 1.0
    binaural_enabled: bool = False
    binaural_base_hz: int = 0

    # Enhancement flags
    enhancements_enabled: bool = False
    enhancements_present: List[str] = None
    enhancements_missing: List[str] = None

    # Mastering
    target_lufs: float = -14
    true_peak: float = -1.5

    # Output files
    has_voice_enhanced: bool = False
    has_binaural: bool = False
    has_final_master: bool = False

    # Compliance
    is_compliant: bool = True
    compliance_issues: List[str] = None

    def __post_init__(self):
        if self.enhancements_present is None:
            self.enhancements_present = []
        if self.enhancements_missing is None:
            self.enhancements_missing = []
        if self.compliance_issues is None:
            self.compliance_issues = []


# =============================================================================
# EXTRACTION
# =============================================================================

def extract_session_metrics(session_path: Path) -> SessionMetrics:
    """Extract all metrics from a single session."""
    metrics = SessionMetrics(name=session_path.name, path=session_path)

    # Load manifest
    manifest_path = session_path / "manifest.yaml"
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r') as f:
                manifest = yaml.safe_load(f) or {}
            _extract_manifest_metrics(manifest, metrics)
        except Exception as e:
            metrics.compliance_issues.append(f"Failed to parse manifest: {e}")
    else:
        metrics.compliance_issues.append("Missing manifest.yaml")

    # Load script
    script_path = _find_script(session_path)
    if script_path:
        try:
            with open(script_path, 'r') as f:
                script_content = f.read()
            _extract_script_metrics(script_content, metrics)
        except Exception as e:
            metrics.compliance_issues.append(f"Failed to read script: {e}")
    else:
        metrics.compliance_issues.append("No SSML script found")

    # Check output files
    _check_output_files(session_path, metrics)

    # Determine compliance
    _evaluate_compliance(metrics)

    return metrics


def _find_script(session_path: Path) -> Optional[Path]:
    """Find the best script file to analyze."""
    candidates = [
        session_path / "working_files" / "script_production.ssml",
        session_path / "working_files" / "script_voice_clean.ssml",
        session_path / "script.ssml",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _extract_manifest_metrics(manifest: Dict, metrics: SessionMetrics):
    """Extract metrics from manifest."""
    # Session info
    if "session" in manifest:
        session = manifest["session"]
        metrics.created_date = session.get("created")
        metrics.duration_seconds = session.get("duration", 0)

    # Voice settings
    if "voice" in manifest:
        voice = manifest["voice"]
        metrics.voice_name = voice.get("voice_name", "")
        metrics.voice_rate = voice.get("rate", 1.0)

    # Binaural
    if "sound_bed" in manifest and "binaural" in manifest["sound_bed"]:
        binaural = manifest["sound_bed"]["binaural"]
        metrics.binaural_enabled = binaural.get("enabled", False)
        metrics.binaural_base_hz = binaural.get("base_hz", 0)

    # Sections
    if "sections" in manifest:
        metrics.section_count = len(manifest["sections"])

    # Voice enhancement
    if "voice_enhancement" in manifest:
        ve = manifest["voice_enhancement"]
        metrics.enhancements_enabled = ve.get("enabled", False)

        for enhancement in MANDATORY_ENHANCEMENTS:
            if enhancement in ve and ve[enhancement]:
                metrics.enhancements_present.append(enhancement)
            else:
                metrics.enhancements_missing.append(enhancement)
    else:
        metrics.enhancements_missing = MANDATORY_ENHANCEMENTS.copy()

    # Mastering
    if "mastering" in manifest:
        mastering = manifest["mastering"]
        metrics.target_lufs = mastering.get("target_lufs", -14)
        metrics.true_peak = mastering.get("true_peak_dbtp", -1.5)


def _extract_script_metrics(content: str, metrics: SessionMetrics):
    """Extract metrics from script content."""
    content_lower = content.lower()

    # Word count (strip tags)
    text_only = re.sub(r'<[^>]+>', '', content)
    text_only = re.sub(r'\[sfx:[^\]]+\]', '', text_only, flags=re.IGNORECASE)
    metrics.word_count = len(text_only.split())

    # Section markers
    section_pattern = r'<!-- section \d+'
    sections = re.findall(section_pattern, content_lower)
    metrics.section_count = max(metrics.section_count, len(sections))

    # Anchor count
    anchor_patterns = [
        r'whenever you', r'each time you', r'every time you',
        r'when you notice', r'when you feel', r'moment you',
    ]
    for pattern in anchor_patterns:
        metrics.anchor_count += len(re.findall(pattern, content_lower))

    # Sense coverage
    sense_patterns = {
        "sight": r'(see|vision|light|color|glow|notice|observe|watch|look)',
        "sound": r'(hear|sound|listen|voice|whisper|echo|hum)',
        "touch": r'(feel|touch|warm|cool|soft|smooth|pressure|sensation)',
        "smell": r'(smell|scent|fragrance|aroma)',
        "taste": r'(taste|flavor|sweet|bitter|nectar)',
    }
    for sense, pattern in sense_patterns.items():
        if re.search(pattern, content_lower):
            metrics.sense_coverage += 1

    # Break count
    metrics.break_count = len(re.findall(r'<break[^>]*>', content))


def _check_output_files(session_path: Path, metrics: SessionMetrics):
    """Check for expected output files."""
    output_dir = session_path / "output"
    if output_dir.exists():
        metrics.has_voice_enhanced = (output_dir / "voice_enhanced.mp3").exists()
        metrics.has_binaural = any(
            f.name.startswith("binaural")
            for f in output_dir.glob("*.wav")
        )
        metrics.has_final_master = (
            (output_dir / "final_master.mp3").exists() or
            any(f.name.endswith("_final.mp3") for f in output_dir.glob("*.mp3"))
        )


def _evaluate_compliance(metrics: SessionMetrics):
    """Evaluate overall compliance with standards."""
    issues = []

    # Word count
    if metrics.word_count > 0:
        if metrics.word_count < STANDARDS["word_count"]["min"]:
            issues.append(f"Word count too low: {metrics.word_count}")
        elif metrics.word_count > STANDARDS["word_count"]["max"]:
            issues.append(f"Word count too high: {metrics.word_count}")

    # Sections
    if metrics.section_count < 5:
        issues.append(f"Only {metrics.section_count} sections (need 5)")

    # Anchors
    if metrics.anchor_count < STANDARDS["anchor_count"]["min"]:
        issues.append(f"Too few anchors: {metrics.anchor_count}")

    # Senses
    if metrics.sense_coverage < STANDARDS["sense_coverage"]["min"]:
        issues.append(f"Only {metrics.sense_coverage}/5 senses covered")

    # Voice settings
    if metrics.voice_name and metrics.voice_name != "en-US-Neural2-H":
        issues.append(f"Non-standard voice: {metrics.voice_name}")

    # Enhancements
    if metrics.enhancements_missing:
        issues.append(f"Missing enhancements: {', '.join(metrics.enhancements_missing)}")

    # Binaural
    if not metrics.binaural_enabled:
        issues.append("Binaural not enabled")

    # Output files
    if not metrics.has_voice_enhanced:
        issues.append("Missing voice_enhanced.mp3")

    metrics.compliance_issues.extend(issues)
    metrics.is_compliant = len(metrics.compliance_issues) == 0


# =============================================================================
# ANALYSIS
# =============================================================================

def analyze_consistency(all_metrics: List[SessionMetrics]) -> Dict[str, Any]:
    """Analyze consistency across all sessions."""
    if not all_metrics:
        return {}

    analysis = {
        "total_sessions": len(all_metrics),
        "compliant_sessions": sum(1 for m in all_metrics if m.is_compliant),
        "metrics_summary": {},
        "common_issues": [],
        "outliers": {},
        "enhancement_coverage": {},
        "voice_consistency": {},
        "recommendations": [],
    }

    # Metrics summary
    word_counts = [m.word_count for m in all_metrics if m.word_count > 0]
    anchor_counts = [m.anchor_count for m in all_metrics]
    sense_coverages = [m.sense_coverage for m in all_metrics]
    break_counts = [m.break_count for m in all_metrics if m.break_count > 0]

    if word_counts:
        analysis["metrics_summary"]["word_count"] = {
            "mean": sum(word_counts) / len(word_counts),
            "min": min(word_counts),
            "max": max(word_counts),
            "std_dev": _std_dev(word_counts),
            "target": STANDARDS["word_count"]["target"],
        }

    if anchor_counts:
        analysis["metrics_summary"]["anchor_count"] = {
            "mean": sum(anchor_counts) / len(anchor_counts),
            "min": min(anchor_counts),
            "max": max(anchor_counts),
            "target_min": STANDARDS["anchor_count"]["min"],
            "target_max": STANDARDS["anchor_count"]["max"],
        }

    if sense_coverages:
        analysis["metrics_summary"]["sense_coverage"] = {
            "mean": sum(sense_coverages) / len(sense_coverages),
            "min": min(sense_coverages),
            "max": max(sense_coverages),
            "target": 5,
        }

    # Common issues
    issue_counts = defaultdict(int)
    for m in all_metrics:
        for issue in m.compliance_issues:
            # Normalize issue
            normalized = re.sub(r'\d+', 'N', issue)
            issue_counts[normalized] += 1

    analysis["common_issues"] = sorted(
        [(issue, count) for issue, count in issue_counts.items()],
        key=lambda x: -x[1]
    )[:10]

    # Outliers
    if word_counts:
        avg = sum(word_counts) / len(word_counts)
        analysis["outliers"]["low_word_count"] = [
            m.name for m in all_metrics
            if m.word_count < avg * 0.7 and m.word_count > 0
        ]
        analysis["outliers"]["high_word_count"] = [
            m.name for m in all_metrics
            if m.word_count > avg * 1.3
        ]

    analysis["outliers"]["low_anchors"] = [
        m.name for m in all_metrics if m.anchor_count < 3
    ]
    analysis["outliers"]["missing_senses"] = [
        m.name for m in all_metrics if m.sense_coverage < 4
    ]

    # Enhancement coverage
    for enhancement in MANDATORY_ENHANCEMENTS:
        has_count = sum(1 for m in all_metrics if enhancement in m.enhancements_present)
        analysis["enhancement_coverage"][enhancement] = {
            "sessions_with": has_count,
            "sessions_without": len(all_metrics) - has_count,
            "coverage_pct": has_count / len(all_metrics) * 100 if all_metrics else 0,
        }

    # Voice consistency
    voice_names = [m.voice_name for m in all_metrics if m.voice_name]
    voice_counts = defaultdict(int)
    for v in voice_names:
        voice_counts[v] += 1
    analysis["voice_consistency"] = dict(voice_counts)

    # Recommendations
    if analysis["compliant_sessions"] < len(all_metrics):
        analysis["recommendations"].append(
            f"Update {len(all_metrics) - analysis['compliant_sessions']} "
            f"non-compliant sessions"
        )

    missing_enhancements = {
        e: data for e, data in analysis["enhancement_coverage"].items()
        if data["coverage_pct"] < 100
    }
    if missing_enhancements:
        for e, data in missing_enhancements.items():
            if data["sessions_without"] > 0:
                analysis["recommendations"].append(
                    f"Add {e} to {data['sessions_without']} sessions"
                )

    return analysis


def _std_dev(values: List[float]) -> float:
    """Calculate standard deviation."""
    if len(values) < 2:
        return 0
    avg = sum(values) / len(values)
    variance = sum((x - avg) ** 2 for x in values) / len(values)
    return variance ** 0.5


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_markdown_report(
    all_metrics: List[SessionMetrics],
    analysis: Dict[str, Any]
) -> str:
    """Generate Markdown consistency report."""
    lines = [
        "# Session Consistency Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"- **Total Sessions:** {analysis.get('total_sessions', 0)}",
        f"- **Compliant Sessions:** {analysis.get('compliant_sessions', 0)}",
        f"- **Compliance Rate:** {analysis.get('compliant_sessions', 0) / max(analysis.get('total_sessions', 1), 1) * 100:.1f}%",
        "",
    ]

    # Metrics Summary
    lines.extend([
        "---",
        "",
        "## Metrics Summary",
        "",
        "| Metric | Mean | Min | Max | Target |",
        "|--------|------|-----|-----|--------|",
    ])

    for metric, data in analysis.get("metrics_summary", {}).items():
        target = data.get("target", data.get("target_min", "N/A"))
        lines.append(
            f"| {metric} | {data.get('mean', 0):.1f} | {data.get('min', 0)} | "
            f"{data.get('max', 0)} | {target} |"
        )

    # Common Issues
    if analysis.get("common_issues"):
        lines.extend([
            "",
            "---",
            "",
            "## Common Issues",
            "",
            "| Issue | Occurrences |",
            "|-------|-------------|",
        ])
        for issue, count in analysis["common_issues"]:
            lines.append(f"| {issue} | {count} |")

    # Enhancement Coverage
    lines.extend([
        "",
        "---",
        "",
        "## Enhancement Coverage",
        "",
        "| Enhancement | Sessions With | Coverage |",
        "|-------------|---------------|----------|",
    ])
    for enhancement, data in analysis.get("enhancement_coverage", {}).items():
        lines.append(
            f"| {enhancement} | {data['sessions_with']}/{analysis['total_sessions']} | "
            f"{data['coverage_pct']:.0f}% |"
        )

    # Outliers
    if any(analysis.get("outliers", {}).values()):
        lines.extend([
            "",
            "---",
            "",
            "## Outlier Sessions",
            "",
        ])
        for category, sessions in analysis.get("outliers", {}).items():
            if sessions:
                lines.append(f"### {category.replace('_', ' ').title()}")
                for s in sessions:
                    lines.append(f"- {s}")
                lines.append("")

    # Session Details
    lines.extend([
        "",
        "---",
        "",
        "## Individual Session Status",
        "",
        "| Session | Compliant | Words | Anchors | Senses | Issues |",
        "|---------|-----------|-------|---------|--------|--------|",
    ])

    for m in sorted(all_metrics, key=lambda x: x.name):
        status = "✓" if m.is_compliant else "✗"
        issue_count = len(m.compliance_issues)
        lines.append(
            f"| {m.name} | {status} | {m.word_count} | {m.anchor_count} | "
            f"{m.sense_coverage}/5 | {issue_count} |"
        )

    # Recommendations
    if analysis.get("recommendations"):
        lines.extend([
            "",
            "---",
            "",
            "## Recommendations",
            "",
        ])
        for i, rec in enumerate(analysis["recommendations"], 1):
            lines.append(f"{i}. {rec}")

    # Non-compliant details
    non_compliant = [m for m in all_metrics if not m.is_compliant]
    if non_compliant:
        lines.extend([
            "",
            "---",
            "",
            "## Non-Compliant Session Details",
            "",
        ])
        for m in non_compliant:
            lines.append(f"### {m.name}")
            lines.append("")
            for issue in m.compliance_issues:
                lines.append(f"- {issue}")
            lines.append("")

    return "\n".join(lines)


def generate_html_report(
    all_metrics: List[SessionMetrics],
    analysis: Dict[str, Any]
) -> str:
    """Generate HTML consistency report."""
    compliance_pct = (
        analysis.get('compliant_sessions', 0) /
        max(analysis.get('total_sessions', 1), 1) * 100
    )

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Session Consistency Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
               max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; }}
        .card h3 {{ margin-top: 0; color: #7f8c8d; font-size: 14px; text-transform: uppercase; }}
        .card .value {{ font-size: 36px; font-weight: bold; color: #2c3e50; }}
        .card.green .value {{ color: #27ae60; }}
        .card.red .value {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 20px 0; }}
        th {{ background: #3498db; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 12px; border-bottom: 1px solid #ecf0f1; }}
        tr:hover {{ background: #f8f9fa; }}
        .compliant {{ color: #27ae60; font-weight: bold; }}
        .non-compliant {{ color: #e74c3c; font-weight: bold; }}
        .progress {{ background: #ecf0f1; border-radius: 10px; height: 20px; overflow: hidden; }}
        .progress-bar {{ background: #3498db; height: 100%; transition: width 0.3s; }}
        .issue-list {{ background: white; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .timestamp {{ color: #95a5a6; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>Session Consistency Report</h1>
    <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <div class="summary">
        <div class="card">
            <h3>Total Sessions</h3>
            <div class="value">{analysis.get('total_sessions', 0)}</div>
        </div>
        <div class="card {'green' if compliance_pct >= 80 else 'red'}">
            <h3>Compliant</h3>
            <div class="value">{analysis.get('compliant_sessions', 0)}</div>
        </div>
        <div class="card">
            <h3>Compliance Rate</h3>
            <div class="value">{compliance_pct:.0f}%</div>
            <div class="progress">
                <div class="progress-bar" style="width: {compliance_pct}%"></div>
            </div>
        </div>
    </div>

    <h2>Enhancement Coverage</h2>
    <table>
        <thead>
            <tr>
                <th>Enhancement</th>
                <th>Coverage</th>
                <th>Sessions</th>
            </tr>
        </thead>
        <tbody>
"""

    for enhancement, data in analysis.get("enhancement_coverage", {}).items():
        coverage = data['coverage_pct']
        color = '#27ae60' if coverage == 100 else '#e74c3c' if coverage < 50 else '#f39c12'
        html += f"""
            <tr>
                <td>{enhancement}</td>
                <td>
                    <div class="progress" style="width: 200px; display: inline-block;">
                        <div class="progress-bar" style="width: {coverage}%; background: {color}"></div>
                    </div>
                    {coverage:.0f}%
                </td>
                <td>{data['sessions_with']}/{analysis['total_sessions']}</td>
            </tr>
"""

    html += """
        </tbody>
    </table>

    <h2>Session Status</h2>
    <table>
        <thead>
            <tr>
                <th>Session</th>
                <th>Status</th>
                <th>Words</th>
                <th>Anchors</th>
                <th>Senses</th>
                <th>Issues</th>
            </tr>
        </thead>
        <tbody>
"""

    for m in sorted(all_metrics, key=lambda x: x.name):
        status_class = "compliant" if m.is_compliant else "non-compliant"
        status_text = "✓ Compliant" if m.is_compliant else "✗ Non-Compliant"
        html += f"""
            <tr>
                <td><strong>{m.name}</strong></td>
                <td class="{status_class}">{status_text}</td>
                <td>{m.word_count}</td>
                <td>{m.anchor_count}</td>
                <td>{m.sense_coverage}/5</td>
                <td>{len(m.compliance_issues)}</td>
            </tr>
"""

    html += """
        </tbody>
    </table>

    <h2>Common Issues</h2>
    <div class="issue-list">
"""

    for issue, count in analysis.get("common_issues", []):
        html += f"<p><strong>({count}x)</strong> {issue}</p>"

    html += """
    </div>
</body>
</html>
"""

    return html


# =============================================================================
# MAIN
# =============================================================================

def find_all_sessions(project_root: Path) -> List[Path]:
    """Find all session directories."""
    sessions_dir = project_root / "sessions"
    if not sessions_dir.exists():
        return []
    return [
        d for d in sessions_dir.iterdir()
        if d.is_dir() and d.name != "_template" and not d.name.startswith(".")
    ]


def get_project_root() -> Path:
    """Find project root."""
    script_path = Path(__file__).resolve()
    return script_path.parent.parent.parent


def main():
    parser = argparse.ArgumentParser(
        description="Generate session consistency report"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["md", "html", "json"],
        default="md",
        help="Output format"
    )

    args = parser.parse_args()

    project_root = get_project_root()
    sessions = find_all_sessions(project_root)

    if not sessions:
        print("No sessions found")
        sys.exit(0)

    print(f"Analyzing {len(sessions)} sessions...")

    # Extract metrics from all sessions
    all_metrics = []
    for session_path in sessions:
        print(f"  Processing: {session_path.name}")
        metrics = extract_session_metrics(session_path)
        all_metrics.append(metrics)

    # Analyze consistency
    analysis = analyze_consistency(all_metrics)

    # Generate report
    if args.format == "html":
        report = generate_html_report(all_metrics, analysis)
    elif args.format == "json":
        report = json.dumps({
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "sessions": [
                {
                    "name": m.name,
                    "compliant": m.is_compliant,
                    "word_count": m.word_count,
                    "anchor_count": m.anchor_count,
                    "sense_coverage": m.sense_coverage,
                    "issues": m.compliance_issues,
                }
                for m in all_metrics
            ]
        }, indent=2)
    else:
        report = generate_markdown_report(all_metrics, analysis)

    # Output
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {output_path}")
    else:
        print(report)

    # Summary
    print(f"\n{'='*60}")
    print("CONSISTENCY SUMMARY")
    print(f"{'='*60}")
    print(f"Total Sessions: {analysis['total_sessions']}")
    print(f"Compliant: {analysis['compliant_sessions']}")
    print(f"Compliance Rate: {analysis['compliant_sessions']/max(analysis['total_sessions'], 1)*100:.1f}%")

    sys.exit(0 if analysis['compliant_sessions'] == analysis['total_sessions'] else 1)


if __name__ == "__main__":
    main()
