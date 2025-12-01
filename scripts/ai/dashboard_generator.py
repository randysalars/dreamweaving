#!/usr/bin/env python3
"""
Analytics Dashboard Generator for Dreamweaving

Generates an HTML dashboard showing:
- Session overview and statistics
- Quality scores across sessions
- Learning system insights
- Trend analysis

Usage:
    python3 scripts/ai/dashboard_generator.py
    python3 scripts/ai/dashboard_generator.py --output reports/dashboard.html
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import html


class DashboardGenerator:
    """Generate HTML analytics dashboard."""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.sessions_dir = self.project_root / "sessions"
        self.knowledge_dir = self.project_root / "knowledge"

    def collect_session_data(self) -> List[Dict]:
        """Collect data from all sessions."""
        sessions = []

        if not self.sessions_dir.exists():
            return sessions

        for session_dir in sorted(self.sessions_dir.iterdir()):
            if not session_dir.is_dir():
                continue

            manifest_path = session_dir / "manifest.yaml"
            if not manifest_path.exists():
                continue

            session_data = {
                "name": session_dir.name,
                "path": str(session_dir),
                "has_manifest": True,
                "has_ssml": False,
                "has_voice": False,
                "has_final": False,
                "has_video": False,
                "has_youtube_package": False,
                "quality_score": None,
                "theme": None,
                "duration": None,
            }

            # Load manifest
            try:
                with open(manifest_path, 'r') as f:
                    manifest = yaml.safe_load(f)
                session_data["theme"] = manifest.get("theme", "unknown")
                session_data["duration"] = manifest.get("duration")
            except Exception:
                pass

            # Check files
            session_data["has_ssml"] = (session_dir / "working_files" / "script.ssml").exists()
            session_data["has_voice"] = (session_dir / "output" / "voice.mp3").exists()
            session_data["has_final"] = (session_dir / "output" / "final.mp3").exists()
            session_data["has_video"] = (session_dir / "output" / "youtube_package" / "video.mp4").exists()
            session_data["has_youtube_package"] = (session_dir / "output" / "youtube_package").exists()

            # Load quality score
            quality_path = session_dir / "working_files" / "quality_report.json"
            if quality_path.exists():
                try:
                    with open(quality_path, 'r') as f:
                        quality = json.load(f)
                    session_data["quality_score"] = quality.get("overall_score")
                except Exception:
                    pass

            sessions.append(session_data)

        return sessions

    def collect_learning_data(self) -> Dict:
        """Collect data from learning system."""
        learning_data = {
            "lessons_count": 0,
            "recent_lessons": [],
            "categories": {},
            "code_reviews": [],
        }

        # Load lessons
        lessons_path = self.knowledge_dir / "lessons_learned.yaml"
        if lessons_path.exists():
            try:
                with open(lessons_path, 'r') as f:
                    lessons = yaml.safe_load(f) or {}

                for category, items in lessons.items():
                    if isinstance(items, list):
                        learning_data["lessons_count"] += len(items)
                        learning_data["categories"][category] = len(items)

                        # Get recent lessons
                        cutoff = (datetime.now() - timedelta(days=30)).isoformat()[:10]
                        recent = [l for l in items if l.get("date", "") >= cutoff]
                        learning_data["recent_lessons"].extend(recent[-5:])
            except Exception:
                pass

        # Load code review history
        improvements_path = self.knowledge_dir / "code_improvements" / "improvements.yaml"
        if improvements_path.exists():
            try:
                with open(improvements_path, 'r') as f:
                    improvements = yaml.safe_load(f) or {}
                learning_data["code_reviews"] = improvements.get("reviews", [])[-10:]
            except Exception:
                pass

        return learning_data

    def collect_batch_reports(self) -> List[Dict]:
        """Collect batch processing reports."""
        reports = []
        reports_dir = self.knowledge_dir / "batch_reports"

        if reports_dir.exists():
            for report_file in sorted(reports_dir.glob("*.yaml"))[-10:]:
                try:
                    with open(report_file, 'r') as f:
                        report = yaml.safe_load(f)
                    reports.append(report)
                except Exception:
                    pass

        return reports

    def generate_html(self, sessions: List[Dict], learning: Dict, batch_reports: List[Dict]) -> str:
        """Generate HTML dashboard."""
        # Calculate statistics
        total_sessions = len(sessions)
        complete_sessions = sum(1 for s in sessions if s["has_final"])
        with_video = sum(1 for s in sessions if s["has_video"])

        avg_quality = 0
        quality_scores = [s["quality_score"] for s in sessions if s["quality_score"]]
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)

        themes = defaultdict(int)
        for s in sessions:
            themes[s["theme"] or "unknown"] += 1

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dreamweaving Analytics Dashboard</title>
    <style>
        :root {{
            --bg-dark: #1a1a2e;
            --bg-card: #16213e;
            --accent: #e94560;
            --accent-light: #ff6b6b;
            --text: #eee;
            --text-muted: #aaa;
            --success: #4ade80;
            --warning: #fbbf24;
            --error: #f87171;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-dark);
            color: var(--text);
            min-height: 100vh;
            padding: 20px;
        }}

        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, var(--bg-card), #1f4068);
            border-radius: 12px;
        }}

        header h1 {{
            font-size: 2rem;
            background: linear-gradient(90deg, var(--accent), var(--accent-light));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }}

        header p {{
            color: var(--text-muted);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: var(--bg-card);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}

        .stat-card .value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--accent);
        }}

        .stat-card .label {{
            color: var(--text-muted);
            margin-top: 5px;
        }}

        .section {{
            background: var(--bg-card);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }}

        .section h2 {{
            font-size: 1.2rem;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }}

        .sessions-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .sessions-table th,
        .sessions-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #333;
        }}

        .sessions-table th {{
            color: var(--text-muted);
            font-weight: normal;
        }}

        .sessions-table tr:hover {{
            background: rgba(255,255,255,0.05);
        }}

        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
        }}

        .status-complete {{ background: var(--success); color: #000; }}
        .status-partial {{ background: var(--warning); color: #000; }}
        .status-pending {{ background: #666; }}

        .quality-bar {{
            height: 8px;
            background: #333;
            border-radius: 4px;
            overflow: hidden;
        }}

        .quality-bar-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }}

        .quality-a {{ background: var(--success); }}
        .quality-b {{ background: #a3e635; }}
        .quality-c {{ background: var(--warning); }}
        .quality-d {{ background: #fb923c; }}
        .quality-f {{ background: var(--error); }}

        .themes-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .theme-badge {{
            padding: 8px 16px;
            background: rgba(233, 69, 96, 0.2);
            border: 1px solid var(--accent);
            border-radius: 20px;
            font-size: 0.9rem;
        }}

        .lessons-list {{
            list-style: none;
        }}

        .lessons-list li {{
            padding: 10px;
            margin-bottom: 8px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            border-left: 3px solid var(--accent);
        }}

        .lessons-list .date {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        .two-col {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}

        footer {{
            text-align: center;
            padding: 20px;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}

        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .two-col {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <header>
            <h1>Dreamweaving Analytics</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="value">{total_sessions}</div>
                <div class="label">Total Sessions</div>
            </div>
            <div class="stat-card">
                <div class="value">{complete_sessions}</div>
                <div class="label">Complete</div>
            </div>
            <div class="stat-card">
                <div class="value">{with_video}</div>
                <div class="label">With Video</div>
            </div>
            <div class="stat-card">
                <div class="value">{avg_quality:.0f}</div>
                <div class="label">Avg Quality Score</div>
            </div>
            <div class="stat-card">
                <div class="value">{learning['lessons_count']}</div>
                <div class="label">Lessons Learned</div>
            </div>
        </div>

        <div class="section">
            <h2>Sessions Overview</h2>
            <table class="sessions-table">
                <thead>
                    <tr>
                        <th>Session</th>
                        <th>Theme</th>
                        <th>Status</th>
                        <th>Quality</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_sessions_rows(sessions)}
                </tbody>
            </table>
        </div>

        <div class="two-col">
            <div class="section">
                <h2>Themes Distribution</h2>
                <div class="themes-grid">
                    {self._generate_theme_badges(themes)}
                </div>
            </div>

            <div class="section">
                <h2>Recent Lessons</h2>
                <ul class="lessons-list">
                    {self._generate_lessons_list(learning['recent_lessons'])}
                </ul>
            </div>
        </div>

        <div class="section">
            <h2>Learning Categories</h2>
            <div class="themes-grid">
                {self._generate_category_badges(learning['categories'])}
            </div>
        </div>

        <footer>
            <p>Dreamweaving AI Creative OS | Auto-generated dashboard</p>
        </footer>
    </div>
</body>
</html>"""

        return html_content

    def _generate_sessions_rows(self, sessions: List[Dict]) -> str:
        """Generate table rows for sessions."""
        rows = []
        for s in sessions:
            status = "complete" if s["has_final"] else ("partial" if s["has_ssml"] else "pending")
            status_text = "Complete" if s["has_final"] else ("In Progress" if s["has_ssml"] else "Pending")

            quality_html = ""
            if s["quality_score"]:
                grade_class = self._get_grade_class(s["quality_score"])
                quality_html = f"""
                    <div class="quality-bar">
                        <div class="quality-bar-fill {grade_class}" style="width: {s['quality_score']}%"></div>
                    </div>
                    <small>{s['quality_score']:.0f}/100</small>
                """
            else:
                quality_html = "<small style='color: #666'>N/A</small>"

            rows.append(f"""
                <tr>
                    <td>{html.escape(s['name'])}</td>
                    <td>{html.escape(s['theme'] or 'unknown')}</td>
                    <td><span class="status-badge status-{status}">{status_text}</span></td>
                    <td>{quality_html}</td>
                </tr>
            """)

        return "\n".join(rows) if rows else "<tr><td colspan='4'>No sessions found</td></tr>"

    def _get_grade_class(self, score: float) -> str:
        """Get CSS class for quality grade."""
        if score >= 90:
            return "quality-a"
        elif score >= 80:
            return "quality-b"
        elif score >= 70:
            return "quality-c"
        elif score >= 60:
            return "quality-d"
        return "quality-f"

    def _generate_theme_badges(self, themes: Dict) -> str:
        """Generate theme badges HTML."""
        badges = []
        for theme, count in sorted(themes.items(), key=lambda x: -x[1]):
            badges.append(f'<span class="theme-badge">{html.escape(theme)}: {count}</span>')
        return "\n".join(badges) if badges else "<p>No themes found</p>"

    def _generate_category_badges(self, categories: Dict) -> str:
        """Generate category badges HTML."""
        badges = []
        for category, count in sorted(categories.items(), key=lambda x: -x[1]):
            badges.append(f'<span class="theme-badge">{html.escape(category)}: {count}</span>')
        return "\n".join(badges) if badges else "<p>No categories found</p>"

    def _generate_lessons_list(self, lessons: List[Dict]) -> str:
        """Generate lessons list HTML."""
        items = []
        for lesson in lessons[-5:]:
            date = lesson.get("date", "Unknown")
            text = html.escape(lesson.get("lesson", "")[:200])
            items.append(f'<li><span class="date">{date}</span><br>{text}</li>')
        return "\n".join(items) if items else "<li>No recent lessons</li>"

    def generate(self, output_path: Path = None) -> Path:
        """Generate the complete dashboard."""
        # Collect data
        sessions = self.collect_session_data()
        learning = self.collect_learning_data()
        batch_reports = self.collect_batch_reports()

        # Generate HTML
        html_content = self.generate_html(sessions, learning, batch_reports)

        # Determine output path
        if output_path is None:
            output_path = self.project_root / "reports" / "dashboard.html"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(html_content)

        return output_path


def main():
    parser = argparse.ArgumentParser(description='Generate analytics dashboard')
    parser.add_argument('--output', '-o', help='Output HTML path')
    args = parser.parse_args()

    generator = DashboardGenerator()

    output_path = Path(args.output) if args.output else None
    result_path = generator.generate(output_path)

    print(f"Dashboard generated: {result_path}")
    print(f"Open in browser: file://{result_path.absolute()}")


if __name__ == "__main__":
    main()
