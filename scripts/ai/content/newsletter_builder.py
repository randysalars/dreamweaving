"""
Newsletter Builder Agent.

Creates email campaigns from recent Dreamweaving sessions.
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import re


@dataclass
class Newsletter:
    """Represents a generated newsletter."""
    subject: str
    preview_text: str
    html_content: str
    plain_text: str
    sessions_featured: List[str]
    newsletter_type: str
    created_at: datetime = field(default_factory=datetime.now)

    def to_yaml(self) -> str:
        """Export newsletter metadata as YAML."""
        metadata = {
            'subject': self.subject,
            'preview_text': self.preview_text,
            'sessions_featured': self.sessions_featured,
            'newsletter_type': self.newsletter_type,
            'created_at': self.created_at.isoformat(),
        }
        return yaml.dump(metadata, default_flow_style=False)


class NewsletterBuilder:
    """
    Newsletter Builder Agent.

    Creates email campaigns featuring recent sessions,
    insights from the knowledge base, and engagement content.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parents[3]
        self.sessions_path = self.project_root / 'sessions'
        self.knowledge_path = self.project_root / 'knowledge'
        self.output_path = self.project_root / 'output' / 'newsletters'
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Brand colors
        self.colors = {
            'primary': '#D4AF37',      # Gold
            'secondary': '#1A1A2E',    # Dark blue
            'background': '#0F0F1A',   # Near black
            'text': '#E5E5E5',         # Light gray
            'accent': '#9B6DFF',       # Purple
        }

    def _get_recent_sessions(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get sessions created/modified in the last N days."""
        sessions = []
        cutoff = datetime.now() - timedelta(days=days)

        for session_dir in self.sessions_path.iterdir():
            if not session_dir.is_dir():
                continue
            if session_dir.name.startswith(('_', '.')):
                continue

            manifest_path = session_dir / 'manifest.yaml'
            if not manifest_path.exists():
                continue

            # Check modification time
            mtime = datetime.fromtimestamp(manifest_path.stat().st_mtime)
            if mtime < cutoff:
                continue

            with open(manifest_path, 'r') as f:
                manifest = yaml.safe_load(f) or {}

            session_data = manifest.get('session', {})
            session_data['name'] = session_dir.name
            session_data['modified'] = mtime
            sessions.append(session_data)

        # Sort by modification time, newest first
        sessions.sort(key=lambda x: x.get('modified', datetime.min), reverse=True)
        return sessions

    def _load_featured_sessions(self, session_names: List[str]) -> List[Dict[str, Any]]:
        """Load specific sessions by name."""
        sessions = []
        for name in session_names:
            manifest_path = self.sessions_path / name / 'manifest.yaml'
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    manifest = yaml.safe_load(f) or {}
                session_data = manifest.get('session', {})
                session_data['name'] = name
                sessions.append(session_data)
        return sessions

    def build_weekly_newsletter(
        self,
        featured_sessions: Optional[List[str]] = None,
        custom_intro: Optional[str] = None
    ) -> Newsletter:
        """
        Build a weekly newsletter.

        Args:
            featured_sessions: Specific sessions to feature (or auto-select recent)
            custom_intro: Custom introduction text

        Returns:
            Newsletter object
        """
        # Get sessions to feature
        if featured_sessions:
            sessions = self._load_featured_sessions(featured_sessions)
        else:
            sessions = self._get_recent_sessions(days=7)[:3]

        # Generate content
        subject = self._generate_subject('weekly', sessions)
        preview_text = self._generate_preview('weekly', sessions)
        html_content = self._generate_weekly_html(sessions, custom_intro)
        plain_text = self._generate_weekly_plain(sessions, custom_intro)

        return Newsletter(
            subject=subject,
            preview_text=preview_text,
            html_content=html_content,
            plain_text=plain_text,
            sessions_featured=[s.get('name', '') for s in sessions],
            newsletter_type='weekly',
        )

    def build_new_release_newsletter(
        self,
        session_name: str,
        launch_text: Optional[str] = None
    ) -> Newsletter:
        """
        Build a newsletter for a new session release.

        Args:
            session_name: Name of the new session
            launch_text: Custom launch announcement text

        Returns:
            Newsletter object
        """
        sessions = self._load_featured_sessions([session_name])
        if not sessions:
            raise ValueError(f"Session not found: {session_name}")

        session = sessions[0]

        subject = f"New Journey: {session.get('title', session_name)}"
        preview_text = f"A new dreamweaving experience awaits: {session.get('theme', 'transformation')}"

        html_content = self._generate_release_html(session, launch_text)
        plain_text = self._generate_release_plain(session, launch_text)

        return Newsletter(
            subject=subject,
            preview_text=preview_text,
            html_content=html_content,
            plain_text=plain_text,
            sessions_featured=[session_name],
            newsletter_type='new_release',
        )

    def build_theme_newsletter(
        self,
        theme: str,
        session_names: List[str],
        custom_intro: Optional[str] = None
    ) -> Newsletter:
        """
        Build a themed newsletter (e.g., "Healing Journeys").

        Args:
            theme: Theme name for the newsletter
            session_names: Sessions to feature under this theme
            custom_intro: Custom introduction

        Returns:
            Newsletter object
        """
        sessions = self._load_featured_sessions(session_names)

        subject = f"Dreamweaving: {theme.title()}"
        preview_text = f"Explore our {theme.lower()} journeys for deep transformation"

        html_content = self._generate_theme_html(theme, sessions, custom_intro)
        plain_text = self._generate_theme_plain(theme, sessions, custom_intro)

        return Newsletter(
            subject=subject,
            preview_text=preview_text,
            html_content=html_content,
            plain_text=plain_text,
            sessions_featured=session_names,
            newsletter_type='theme',
        )

    def _generate_subject(
        self,
        newsletter_type: str,
        sessions: List[Dict[str, Any]]
    ) -> str:
        """Generate email subject line."""
        if not sessions:
            return "Sacred Digital Dreamweaver: New Journeys Await"

        first_session = sessions[0]
        title = first_session.get('title', 'New Journey')

        subjects = [
            f"New Journeys: {title}",
            f"This Week's Dreamweaving: {title}",
            f"Transform with {title}",
            f"Your Journey Awaits: {title}",
        ]

        # Use hash to consistently pick same subject for same content
        idx = hash(title) % len(subjects)
        return subjects[idx]

    def _generate_preview(
        self,
        newsletter_type: str,
        sessions: List[Dict[str, Any]]
    ) -> str:
        """Generate email preview text."""
        if not sessions:
            return "Discover new guided hypnosis journeys for transformation and growth"

        themes = [s.get('theme', s.get('title', '')) for s in sessions[:2]]
        return f"Explore {' and '.join(themes)} through guided dreamweaving"

    def _generate_weekly_html(
        self,
        sessions: List[Dict[str, Any]],
        custom_intro: Optional[str]
    ) -> str:
        """Generate weekly newsletter HTML."""
        intro = custom_intro or "Welcome to this week's Dreamweaving collection. New journeys await."

        sessions_html = ""
        for session in sessions:
            sessions_html += self._session_card_html(session)

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sacred Digital Dreamweaver</title>
</head>
<body style="margin: 0; padding: 0; background-color: {self.colors['background']}; font-family: Georgia, serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: {self.colors['background']};">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: {self.colors['secondary']}; border-radius: 8px;">

                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px; text-align: center;">
                            <h1 style="color: {self.colors['primary']}; margin: 0; font-size: 28px; font-weight: normal;">
                                Sacred Digital Dreamweaver
                            </h1>
                            <p style="color: {self.colors['text']}; margin: 10px 0 0; font-size: 14px; opacity: 0.7;">
                                Weekly Journey Collection
                            </p>
                        </td>
                    </tr>

                    <!-- Introduction -->
                    <tr>
                        <td style="padding: 20px 40px;">
                            <p style="color: {self.colors['text']}; font-size: 16px; line-height: 1.6; margin: 0;">
                                {intro}
                            </p>
                        </td>
                    </tr>

                    <!-- Sessions -->
                    <tr>
                        <td style="padding: 20px 40px;">
                            <h2 style="color: {self.colors['primary']}; font-size: 20px; margin: 0 0 20px; font-weight: normal;">
                                This Week's Journeys
                            </h2>
                            {sessions_html}
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px 40px; text-align: center; border-top: 1px solid rgba(212, 175, 55, 0.2);">
                            <p style="color: {self.colors['text']}; font-size: 14px; opacity: 0.7; margin: 0;">
                                Rest well. Dream deep.
                            </p>
                            <p style="color: {self.colors['text']}; font-size: 12px; opacity: 0.5; margin: 20px 0 0;">
                                <a href="{{{{unsubscribe}}}}" style="color: {self.colors['text']};">Unsubscribe</a>
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    def _session_card_html(self, session: Dict[str, Any]) -> str:
        """Generate HTML for a single session card."""
        title = session.get('title', session.get('name', 'Journey'))
        description = session.get('description', '')
        duration = session.get('duration', 25)
        outcome = session.get('desired_outcome', 'transformation')

        # Truncate description
        if len(description) > 150:
            description = description[:147] + '...'

        return f"""
                            <div style="background-color: rgba(15, 15, 26, 0.5); border-radius: 8px; padding: 20px; margin-bottom: 20px; border-left: 3px solid {self.colors['primary']};">
                                <h3 style="color: {self.colors['text']}; font-size: 18px; margin: 0 0 10px; font-weight: normal;">
                                    {title}
                                </h3>
                                <p style="color: {self.colors['text']}; font-size: 14px; line-height: 1.5; margin: 0 0 15px; opacity: 0.8;">
                                    {description}
                                </p>
                                <p style="margin: 0;">
                                    <span style="color: {self.colors['accent']}; font-size: 12px;">
                                        {duration} min • {outcome.replace('_', ' ').title()}
                                    </span>
                                </p>
                            </div>
"""

    def _generate_weekly_plain(
        self,
        sessions: List[Dict[str, Any]],
        custom_intro: Optional[str]
    ) -> str:
        """Generate weekly newsletter plain text."""
        intro = custom_intro or "Welcome to this week's Dreamweaving collection. New journeys await."

        lines = [
            "SACRED DIGITAL DREAMWEAVER",
            "Weekly Journey Collection",
            "",
            intro,
            "",
            "THIS WEEK'S JOURNEYS",
            "-" * 40,
            "",
        ]

        for session in sessions:
            title = session.get('title', session.get('name', 'Journey'))
            description = session.get('description', '')
            duration = session.get('duration', 25)
            outcome = session.get('desired_outcome', 'transformation')

            lines.extend([
                title.upper(),
                f"{duration} min | {outcome.replace('_', ' ').title()}",
                description[:200] if description else '',
                "",
            ])

        lines.extend([
            "-" * 40,
            "Rest well. Dream deep.",
            "",
            "Unsubscribe: {{unsubscribe}}",
        ])

        return '\n'.join(lines)

    def _generate_release_html(
        self,
        session: Dict[str, Any],
        launch_text: Optional[str]
    ) -> str:
        """Generate new release newsletter HTML."""
        title = session.get('title', session.get('name', 'New Journey'))
        description = session.get('description', '')
        theme = session.get('theme', '')
        duration = session.get('duration', 25)
        outcome = session.get('desired_outcome', 'transformation')

        intro = launch_text or f"A new journey has emerged from the depths. {title} is now available."

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: {self.colors['background']}; font-family: Georgia, serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: {self.colors['background']};">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: {self.colors['secondary']}; border-radius: 8px;">

                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px; text-align: center;">
                            <p style="color: {self.colors['accent']}; margin: 0 0 10px; font-size: 14px; text-transform: uppercase; letter-spacing: 2px;">
                                New Release
                            </p>
                            <h1 style="color: {self.colors['primary']}; margin: 0; font-size: 32px; font-weight: normal;">
                                {title}
                            </h1>
                        </td>
                    </tr>

                    <!-- Announcement -->
                    <tr>
                        <td style="padding: 20px 40px;">
                            <p style="color: {self.colors['text']}; font-size: 18px; line-height: 1.6; margin: 0; text-align: center;">
                                {intro}
                            </p>
                        </td>
                    </tr>

                    <!-- Details -->
                    <tr>
                        <td style="padding: 20px 40px;">
                            <div style="background-color: rgba(15, 15, 26, 0.5); border-radius: 8px; padding: 30px; text-align: center;">
                                <p style="color: {self.colors['text']}; font-size: 16px; line-height: 1.6; margin: 0 0 20px;">
                                    {description}
                                </p>
                                <p style="color: {self.colors['accent']}; font-size: 14px; margin: 0;">
                                    {duration} minutes • {outcome.replace('_', ' ').title()}
                                </p>
                            </div>
                        </td>
                    </tr>

                    <!-- CTA -->
                    <tr>
                        <td style="padding: 30px 40px; text-align: center;">
                            <a href="{{{{journey_url}}}}" style="display: inline-block; background-color: {self.colors['primary']}; color: {self.colors['secondary']}; padding: 15px 40px; text-decoration: none; border-radius: 4px; font-size: 16px;">
                                Begin Your Journey
                            </a>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px 40px; text-align: center; border-top: 1px solid rgba(212, 175, 55, 0.2);">
                            <p style="color: {self.colors['text']}; font-size: 14px; opacity: 0.7; margin: 0;">
                                Rest well. Dream deep.
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    def _generate_release_plain(
        self,
        session: Dict[str, Any],
        launch_text: Optional[str]
    ) -> str:
        """Generate new release newsletter plain text."""
        title = session.get('title', session.get('name', 'New Journey'))
        description = session.get('description', '')
        duration = session.get('duration', 25)
        outcome = session.get('desired_outcome', 'transformation')

        intro = launch_text or f"A new journey has emerged from the depths. {title} is now available."

        return f"""NEW RELEASE

{title.upper()}

{intro}

{description}

Duration: {duration} minutes
Focus: {outcome.replace('_', ' ').title()}

Begin your journey: {{{{journey_url}}}}

---
Rest well. Dream deep.

Unsubscribe: {{{{unsubscribe}}}}
"""

    def _generate_theme_html(
        self,
        theme: str,
        sessions: List[Dict[str, Any]],
        custom_intro: Optional[str]
    ) -> str:
        """Generate themed newsletter HTML."""
        intro = custom_intro or f"Explore our collection of {theme.lower()} journeys."

        sessions_html = ""
        for session in sessions:
            sessions_html += self._session_card_html(session)

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: {self.colors['background']}; font-family: Georgia, serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: {self.colors['background']};">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: {self.colors['secondary']}; border-radius: 8px;">

                    <tr>
                        <td style="padding: 40px 40px 20px; text-align: center;">
                            <h1 style="color: {self.colors['primary']}; margin: 0; font-size: 28px; font-weight: normal;">
                                {theme.title()} Journeys
                            </h1>
                        </td>
                    </tr>

                    <tr>
                        <td style="padding: 20px 40px;">
                            <p style="color: {self.colors['text']}; font-size: 16px; line-height: 1.6; margin: 0;">
                                {intro}
                            </p>
                        </td>
                    </tr>

                    <tr>
                        <td style="padding: 20px 40px;">
                            {sessions_html}
                        </td>
                    </tr>

                    <tr>
                        <td style="padding: 30px 40px 40px; text-align: center; border-top: 1px solid rgba(212, 175, 55, 0.2);">
                            <p style="color: {self.colors['text']}; font-size: 14px; opacity: 0.7; margin: 0;">
                                Rest well. Dream deep.
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    def _generate_theme_plain(
        self,
        theme: str,
        sessions: List[Dict[str, Any]],
        custom_intro: Optional[str]
    ) -> str:
        """Generate themed newsletter plain text."""
        intro = custom_intro or f"Explore our collection of {theme.lower()} journeys."

        lines = [
            f"{theme.upper()} JOURNEYS",
            "",
            intro,
            "",
            "-" * 40,
            "",
        ]

        for session in sessions:
            title = session.get('title', session.get('name', 'Journey'))
            duration = session.get('duration', 25)

            lines.extend([
                title,
                f"{duration} min",
                "",
            ])

        lines.extend([
            "-" * 40,
            "Rest well. Dream deep.",
        ])

        return '\n'.join(lines)

    def save_newsletter(
        self,
        newsletter: Newsletter,
        base_name: Optional[str] = None
    ) -> Dict[str, Path]:
        """Save newsletter files."""
        if base_name is None:
            date_str = newsletter.created_at.strftime('%Y-%m-%d')
            base_name = f"newsletter-{newsletter.newsletter_type}-{date_str}"

        paths = {}

        # Save HTML
        html_path = self.output_path / f"{base_name}.html"
        with open(html_path, 'w') as f:
            f.write(newsletter.html_content)
        paths['html'] = html_path

        # Save plain text
        txt_path = self.output_path / f"{base_name}.txt"
        with open(txt_path, 'w') as f:
            f.write(newsletter.plain_text)
        paths['txt'] = txt_path

        # Save metadata
        meta_path = self.output_path / f"{base_name}.yaml"
        with open(meta_path, 'w') as f:
            f.write(newsletter.to_yaml())
        paths['meta'] = meta_path

        return paths


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Build newsletters')
    parser.add_argument('--type', default='weekly',
                       choices=['weekly', 'release', 'theme'],
                       help='Newsletter type')
    parser.add_argument('--sessions', nargs='+', help='Sessions to feature')
    parser.add_argument('--theme', help='Theme name (for theme type)')
    parser.add_argument('--save', action='store_true', help='Save to files')

    args = parser.parse_args()

    builder = NewsletterBuilder()

    if args.type == 'weekly':
        newsletter = builder.build_weekly_newsletter(args.sessions)
    elif args.type == 'release' and args.sessions:
        newsletter = builder.build_new_release_newsletter(args.sessions[0])
    elif args.type == 'theme' and args.theme and args.sessions:
        newsletter = builder.build_theme_newsletter(args.theme, args.sessions)
    else:
        print("Invalid arguments. Use --help for usage.")
        exit(1)

    if args.save:
        paths = builder.save_newsletter(newsletter)
        print(f"Saved: {paths}")
    else:
        print(f"Subject: {newsletter.subject}")
        print(f"Preview: {newsletter.preview_text}")
        print("\n" + "="*50 + "\n")
        print(newsletter.plain_text)
