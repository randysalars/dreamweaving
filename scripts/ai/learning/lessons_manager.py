#!/usr/bin/env python3
"""
Lessons Manager for Dreamweaving Self-Learning System

Manages the knowledge base:
- Records lessons learned from feedback
- Retrieves relevant lessons for new sessions
- Tracks improvement over time
- Provides recommendations based on accumulated knowledge

Usage:
    python3 scripts/ai/learning/lessons_manager.py show
    python3 scripts/ai/learning/lessons_manager.py add --category analytics --lesson "Text here"
    python3 scripts/ai/learning/lessons_manager.py recommend --theme spiritual
    python3 scripts/ai/learning/lessons_manager.py stats
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict


KNOWLEDGE_BASE_PATH = Path('knowledge')
LESSONS_FILE = KNOWLEDGE_BASE_PATH / 'lessons_learned.yaml'
BEST_PRACTICES_FILE = KNOWLEDGE_BASE_PATH / 'best_practices.md'


class LessonsManager:
    """Manages the lessons learned knowledge base."""

    def __init__(self, knowledge_path: Path = KNOWLEDGE_BASE_PATH):
        self.knowledge_path = knowledge_path
        self.lessons_path = knowledge_path / 'lessons_learned.yaml'
        self.lessons = self._load_lessons()

    def _load_lessons(self) -> Dict:
        """Load lessons from file."""
        if self.lessons_path.exists():
            with open(self.lessons_path, 'r') as f:
                return yaml.safe_load(f) or {}
        return {
            "analytics_insights": [],
            "viewer_feedback": [],
            "code_improvements": [],
            "session_patterns": [],
            "general_learnings": [],
        }

    def _save_lessons(self):
        """Save lessons to file."""
        self.lessons_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.lessons_path, 'w') as f:
            yaml.dump(self.lessons, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def add_lesson(
        self,
        category: str,
        lesson: str,
        source: str = "manual",
        tags: List[str] = None,
        importance: str = "medium"
    ):
        """Add a new lesson to the knowledge base."""
        entry = {
            "date": datetime.now().isoformat()[:10],
            "lesson": lesson,
            "source": source,
            "tags": tags or [],
            "importance": importance,
            "applied_count": 0,
        }

        if category not in self.lessons:
            self.lessons[category] = []

        self.lessons[category].append(entry)
        self._save_lessons()

        return entry

    def get_lessons(
        self,
        category: str = None,
        importance: str = None,
        tags: List[str] = None,
        since_days: int = None
    ) -> List[Dict]:
        """Retrieve lessons with optional filtering."""
        all_lessons = []

        # Collect from specified category or all
        if category:
            all_lessons = self.lessons.get(category, [])
        else:
            for cat_lessons in self.lessons.values():
                if isinstance(cat_lessons, list):
                    all_lessons.extend(cat_lessons)

        # Apply filters
        if importance:
            all_lessons = [l for l in all_lessons if l.get('importance') == importance]

        if tags:
            all_lessons = [l for l in all_lessons if any(t in l.get('tags', []) for t in tags)]

        if since_days:
            cutoff = (datetime.now() - timedelta(days=since_days)).isoformat()[:10]
            all_lessons = [l for l in all_lessons if l.get('date', '') >= cutoff]

        return all_lessons

    def get_recommendations(
        self,
        theme: str = None,
        session_type: str = None,
        duration: int = None
    ) -> Dict:
        """Get recommendations based on accumulated knowledge."""
        recommendations = {
            "script": [],
            "audio": [],
            "video": [],
            "general": [],
        }

        # Gather relevant lessons
        all_lessons = self.get_lessons()

        # Theme-based recommendations
        if theme:
            theme_lessons = [l for l in all_lessons if theme.lower() in str(l).lower()]
            for lesson in theme_lessons[:5]:
                recommendations["general"].append(lesson["lesson"])

        # Analytics-based (what works)
        analytics = self.lessons.get("analytics_insights", [])
        high_retention = [l for l in analytics if "retention" in str(l).lower() and "good" in str(l).lower()]
        for lesson in high_retention[:3]:
            recommendations["script"].append(f"Analytics showed: {lesson['lesson']}")

        # Viewer feedback (what they want)
        feedback = self.lessons.get("viewer_feedback", [])
        positive = [l for l in feedback if l.get("importance") in ["high", "critical"]]
        for lesson in positive[:3]:
            recommendations["general"].append(f"Viewers: {lesson['lesson']}")

        # Duration-specific
        if duration:
            if duration > 45 * 60:  # Over 45 minutes
                recommendations["script"].append(
                    "For longer sessions, ensure varied pacing to maintain engagement"
                )
            elif duration < 20 * 60:  # Under 20 minutes
                recommendations["script"].append(
                    "Short sessions should have concise but complete structure"
                )

        # Best practices integration
        best_practices = self._load_best_practices()
        if best_practices:
            recommendations["general"].extend(best_practices[:3])

        return recommendations

    def _load_best_practices(self) -> List[str]:
        """Load best practices from markdown file."""
        practices = []

        if BEST_PRACTICES_FILE.exists():
            with open(BEST_PRACTICES_FILE, 'r') as f:
                content = f.read()

            # Extract bullet points
            import re
            bullets = re.findall(r'^[-*]\s+(.+)$', content, re.MULTILINE)
            practices = bullets[:10]

        return practices

    def get_statistics(self) -> Dict:
        """Get statistics about the knowledge base."""
        stats = {
            "total_lessons": 0,
            "by_category": {},
            "by_importance": Counter(),
            "recent_30_days": 0,
            "most_common_tags": Counter(),
        }

        cutoff = (datetime.now() - timedelta(days=30)).isoformat()[:10]

        for category, lessons in self.lessons.items():
            if isinstance(lessons, list):
                stats["by_category"][category] = len(lessons)
                stats["total_lessons"] += len(lessons)

                for lesson in lessons:
                    stats["by_importance"][lesson.get("importance", "unknown")] += 1

                    if lesson.get("date", "") >= cutoff:
                        stats["recent_30_days"] += 1

                    for tag in lesson.get("tags", []):
                        stats["most_common_tags"][tag] += 1

        stats["by_importance"] = dict(stats["by_importance"])
        stats["most_common_tags"] = dict(stats["most_common_tags"].most_common(10))

        return stats

    def mark_lesson_applied(self, category: str = None, lesson_text: str = None,
                            lesson_id: str = None, session_name: str = None):
        """
        Mark a lesson as applied (increment counter).

        Can be called with either:
        - category + lesson_text (legacy API)
        - lesson_id + session_name (new ID-based API)
        """
        if lesson_id:
            # ID-based lookup - search all categories
            for cat in self.lessons:
                if isinstance(self.lessons[cat], list):
                    for lesson in self.lessons[cat]:
                        if lesson.get("id") == lesson_id:
                            lesson["applied_count"] = lesson.get("applied_count", 0) + 1
                            lesson["last_applied"] = datetime.now().isoformat()[:10]
                            if session_name:
                                applied_to = lesson.get("applied_to", [])
                                if session_name not in applied_to:
                                    applied_to.append(session_name)
                                    # Keep last 20 sessions
                                    lesson["applied_to"] = applied_to[-20:]
                            self._save_lessons()
                            return True
            return False

        # Legacy text-based lookup
        if category in self.lessons:
            for lesson in self.lessons[category]:
                if lesson.get("lesson") == lesson_text:
                    lesson["applied_count"] = lesson.get("applied_count", 0) + 1
                    lesson["last_applied"] = datetime.now().isoformat()[:10]
                    self._save_lessons()
                    return True
        return False

    def cleanup_old_lessons(self, days: int = 180):
        """Archive lessons older than specified days."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()[:10]
        archived = []

        for category in self.lessons:
            if isinstance(self.lessons[category], list):
                old_lessons = [l for l in self.lessons[category] if l.get("date", "") < cutoff]
                archived.extend(old_lessons)

                # Keep recent and high-importance lessons
                self.lessons[category] = [
                    l for l in self.lessons[category]
                    if l.get("date", "") >= cutoff or l.get("importance") in ["high", "critical"]
                ]

        if archived:
            # Save to archive
            archive_path = self.knowledge_path / 'archived_lessons.yaml'
            existing_archive = []
            if archive_path.exists():
                with open(archive_path, 'r') as f:
                    existing_archive = yaml.safe_load(f) or []

            existing_archive.extend(archived)

            with open(archive_path, 'w') as f:
                yaml.dump(existing_archive, f, default_flow_style=False, allow_unicode=True)

            self._save_lessons()

        return len(archived)


def format_lessons_display(lessons: List[Dict], title: str = "Lessons") -> str:
    """Format lessons for display."""
    lines = [f"\n--- {title} ({len(lessons)}) ---"]

    for lesson in lessons:
        importance = lesson.get("importance", "")
        marker = "!" if importance == "critical" else ("*" if importance == "high" else "-")

        lines.append(f"{marker} [{lesson.get('date', 'N/A')}] {lesson.get('lesson', '')}")

        if lesson.get('source'):
            lines.append(f"    Source: {lesson['source']}")

        if lesson.get('tags'):
            lines.append(f"    Tags: {', '.join(lesson['tags'])}")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Manage lessons learned')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show lessons')
    show_parser.add_argument('--category', help='Filter by category')
    show_parser.add_argument('--importance', choices=['low', 'medium', 'high', 'critical'])
    show_parser.add_argument('--days', type=int, help='Show lessons from last N days')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a lesson')
    add_parser.add_argument('--category', required=True, help='Lesson category')
    add_parser.add_argument('--lesson', required=True, help='Lesson text')
    add_parser.add_argument('--source', default='manual', help='Source of lesson')
    add_parser.add_argument('--tags', help='Comma-separated tags')
    add_parser.add_argument('--importance', default='medium',
                           choices=['low', 'medium', 'high', 'critical'])

    # Recommend command
    rec_parser = subparsers.add_parser('recommend', help='Get recommendations')
    rec_parser.add_argument('--theme', help='Session theme')
    rec_parser.add_argument('--duration', type=int, help='Target duration in minutes')

    # Stats command
    subparsers.add_parser('stats', help='Show statistics')

    # Cleanup command
    clean_parser = subparsers.add_parser('cleanup', help='Archive old lessons')
    clean_parser.add_argument('--days', type=int, default=180,
                             help='Archive lessons older than N days')

    args = parser.parse_args()

    manager = LessonsManager()

    if args.command == 'show' or args.command is None:
        lessons = manager.get_lessons(
            category=getattr(args, 'category', None),
            importance=getattr(args, 'importance', None),
            since_days=getattr(args, 'days', None)
        )
        print(format_lessons_display(lessons, "Lessons Learned"))

    elif args.command == 'add':
        tags = args.tags.split(',') if args.tags else []
        entry = manager.add_lesson(
            category=args.category,
            lesson=args.lesson,
            source=args.source,
            tags=tags,
            importance=args.importance
        )
        print(f"Added lesson to '{args.category}' category")
        print(f"  Date: {entry['date']}")
        print(f"  Importance: {entry['importance']}")

    elif args.command == 'recommend':
        duration_seconds = args.duration * 60 if args.duration else None
        recs = manager.get_recommendations(
            theme=args.theme,
            duration=duration_seconds
        )

        print("\n--- RECOMMENDATIONS ---")
        for category, items in recs.items():
            if items:
                print(f"\n{category.upper()}:")
                for item in items:
                    print(f"  - {item}")

    elif args.command == 'stats':
        stats = manager.get_statistics()

        print("\n--- KNOWLEDGE BASE STATISTICS ---")
        print(f"Total lessons: {stats['total_lessons']}")
        print(f"Lessons in last 30 days: {stats['recent_30_days']}")

        print("\nBy category:")
        for cat, count in stats['by_category'].items():
            print(f"  {cat}: {count}")

        print("\nBy importance:")
        for imp, count in stats['by_importance'].items():
            print(f"  {imp}: {count}")

        if stats['most_common_tags']:
            print("\nMost common tags:")
            for tag, count in list(stats['most_common_tags'].items())[:5]:
                print(f"  {tag}: {count}")

    elif args.command == 'cleanup':
        archived = manager.cleanup_old_lessons(args.days)
        print(f"Archived {archived} lessons older than {args.days} days")


if __name__ == "__main__":
    main()
