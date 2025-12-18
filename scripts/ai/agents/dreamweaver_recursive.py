#!/usr/bin/env python3
"""
Dreamweaver Recursive Agent - Self-improving session generation.

This module implements the recursive improvement agent specifically for
Dreamweaver session generation. It integrates with auto_generate.py to:

1. Retrieve and rank lessons before generation
2. Inject lessons into the generation context
3. Record outcomes after generation completes
4. Schedule YouTube analytics tracking for later metrics

Part of the Recursive Improver system for self-improving Dreamweaving sessions.
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.ai.recursive_improver import RecursiveImprover
from scripts.ai.learning.feedback_store import FeedbackStore, OutcomeRecord


@dataclass
class GenerationContext:
    """Context for a session generation."""
    topic: str
    duration_minutes: int
    desired_outcome: Optional[str] = None
    style: Optional[str] = None
    archetypes: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'topic': self.topic,
            'duration': self.duration_minutes,
            'desired_outcome': self.desired_outcome,
            'style': self.style,
            'archetypes': self.archetypes,
        }


@dataclass
class AppliedLessons:
    """Container for lessons applied during generation."""
    lesson_ids: List[str]
    lessons_context: str
    categories: Dict[str, int]  # category -> count

    def to_manifest_entry(self) -> Dict[str, Any]:
        """Format for inclusion in manifest.yaml."""
        return {
            'applied_lessons': self.lesson_ids,
            'lesson_count': len(self.lesson_ids),
            'categories': self.categories,
        }


class DreamweaverRecursiveAgent:
    """
    Recursive improvement agent for Dreamweaver session generation.

    This agent handles the complete lifecycle of lesson integration:

    Pre-Generation:
    - Retrieves relevant lessons based on topic, duration, and outcome
    - Ranks lessons by effectiveness score
    - Generates prompt context from top lessons

    Post-Generation:
    - Records immediate outcome metrics (success, quality score)
    - Schedules YouTube analytics tracking
    - Updates lesson effectiveness based on outcomes

    Usage:
        agent = DreamweaverRecursiveAgent()

        # Before generation
        applied = agent.prepare_generation(
            topic="Finding Inner Peace",
            duration=25,
            desired_outcome="relaxation"
        )

        # Inject into generation prompt
        prompt += applied.lessons_context

        # After generation
        agent.record_generation_outcome(
            session_name="finding-inner-peace-20251217",
            applied_lessons=applied,
            metrics={
                'generation_success': True,
                'quality_score': 78.5,
                'stages_completed': ['voice', 'mixing', 'mastering'],
            }
        )
    """

    # Default lesson limits
    DEFAULT_LESSON_LIMIT = 10

    # Categories relevant to script generation
    SCRIPT_CATEGORIES = ['content', 'audio', 'feedback']

    def __init__(
        self,
        project_root: Optional[Path] = None,
        recursive_improver: Optional[RecursiveImprover] = None
    ):
        """
        Initialize the Dreamweaver recursive agent.

        Args:
            project_root: Path to project root (defaults to detection)
            recursive_improver: Existing RecursiveImprover instance (creates new if None)
        """
        self.project_root = project_root or PROJECT_ROOT
        self.improver = recursive_improver or RecursiveImprover(self.project_root)

    def prepare_generation(
        self,
        topic: str,
        duration_minutes: int,
        desired_outcome: Optional[str] = None,
        style: Optional[str] = None,
        limit: int = DEFAULT_LESSON_LIMIT
    ) -> AppliedLessons:
        """
        Prepare lessons for session generation.

        Retrieves and ranks lessons relevant to the given topic and context,
        then generates a prompt context string for injection into generation.

        Args:
            topic: Session topic/theme
            duration_minutes: Target duration in minutes
            desired_outcome: Desired outcome (healing, relaxation, transformation, etc.)
            style: Session style (guided, ambient, etc.)
            limit: Maximum lessons to apply

        Returns:
            AppliedLessons with IDs, context string, and category breakdown
        """
        # Create context for retrieval
        context = GenerationContext(
            topic=topic,
            duration_minutes=duration_minutes,
            desired_outcome=desired_outcome,
            style=style,
        )

        # Get ranked lessons from all relevant categories
        all_lessons = []
        category_counts = {}

        for category in self.SCRIPT_CATEGORIES:
            category_lessons = self.improver.get_ranked_lessons(
                topic=topic,
                duration=duration_minutes,
                desired_outcome=desired_outcome,
                category=category,
                limit=limit // len(self.SCRIPT_CATEGORIES) + 1,
            )

            if category_lessons:
                all_lessons.extend(category_lessons)
                category_counts[category] = len(category_lessons)

        # Also get general lessons without category filter
        general_lessons = self.improver.get_ranked_lessons(
            topic=topic,
            duration=duration_minutes,
            desired_outcome=desired_outcome,
            category=None,  # All categories
            limit=limit // 2,
        )

        # Merge and deduplicate by ID
        seen_ids = set()
        merged_lessons = []

        for lesson in all_lessons + general_lessons:
            lesson_id = lesson.get('id')
            if lesson_id and lesson_id not in seen_ids:
                seen_ids.add(lesson_id)
                merged_lessons.append(lesson)

        # Sort by effectiveness and take top N
        merged_lessons.sort(
            key=lambda x: x.get('effectiveness_score', 50),
            reverse=True
        )
        top_lessons = merged_lessons[:limit]

        # Generate context string
        lessons_context = self.improver.get_lessons_context_string(top_lessons)

        # Extract lesson IDs
        lesson_ids = [l.get('id') for l in top_lessons if l.get('id')]

        return AppliedLessons(
            lesson_ids=lesson_ids,
            lessons_context=lessons_context,
            categories=category_counts,
        )

    def record_generation_outcome(
        self,
        session_name: str,
        applied_lessons: AppliedLessons,
        metrics: Dict[str, Any],
        youtube_video_id: Optional[str] = None,
        manifest_path: Optional[Path] = None,
    ) -> str:
        """
        Record the outcome of a session generation.

        Records immediate metrics and optionally schedules YouTube
        analytics tracking for delayed metrics.

        Args:
            session_name: Name of the generated session
            applied_lessons: AppliedLessons from prepare_generation
            metrics: Dict with:
                - generation_success: bool - Did generation complete?
                - quality_score: Optional[float] - Quality assessment (0-100)
                - stages_completed: List[str] - Which stages completed
                - stages_failed: List[str] - Which stages failed
                - execution_time_seconds: Optional[float]
                - estimated_cost_usd: Optional[float]
            youtube_video_id: Optional YouTube video ID for delayed tracking
            manifest_path: Optional path to session manifest for enrichment

        Returns:
            outcome_id: ID of the recorded outcome
        """
        # Load manifest for additional context if provided
        manifest_context = {}
        if manifest_path and manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    manifest = yaml.safe_load(f)
                    session_info = manifest.get('session', {})
                    manifest_context = {
                        'style': session_info.get('style'),
                        'desired_outcome': session_info.get('desired_outcome'),
                        'archetypes': [a.get('name') for a in manifest.get('archetypes', [])],
                    }
            except Exception:
                pass

        # Record with recursive improver
        outcome_id = self.improver.record_session_outcome(
            session_name=session_name,
            applied_lessons=applied_lessons.lesson_ids,
            metrics=metrics,
            youtube_video_id=youtube_video_id,
        )

        return outcome_id

    def update_manifest_with_lessons(
        self,
        manifest_path: Path,
        applied_lessons: AppliedLessons,
    ):
        """
        Update a session manifest with applied lessons tracking.

        Adds an 'applied_lessons' section to the manifest for tracking
        which lessons were used during generation.

        Args:
            manifest_path: Path to manifest.yaml
            applied_lessons: AppliedLessons from prepare_generation
        """
        if not manifest_path.exists():
            return

        try:
            with open(manifest_path, 'r') as f:
                manifest = yaml.safe_load(f) or {}

            # Add recursive improvement tracking section
            manifest['recursive_improvement'] = {
                'applied_lessons': applied_lessons.lesson_ids,
                'lesson_count': len(applied_lessons.lesson_ids),
                'categories': applied_lessons.categories,
                'applied_at': datetime.now().isoformat(),
            }

            with open(manifest_path, 'w') as f:
                yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

        except Exception as e:
            print(f"Warning: Could not update manifest with lessons: {e}")

    def get_session_lessons_report(
        self,
        session_name: str,
        manifest_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Generate a report of lessons applied to a session.

        Args:
            session_name: Session name
            manifest_path: Optional manifest path

        Returns:
            Dict with lesson application details
        """
        # Get outcome record if available
        outcome = self.improver.feedback_store.get_session_outcome(session_name)

        report = {
            'session_name': session_name,
            'outcome_recorded': outcome is not None,
        }

        if outcome:
            report.update({
                'lessons_applied': outcome.lesson_ids,
                'lesson_count': len(outcome.lesson_ids),
                'generation_success': outcome.generation_success,
                'quality_score': outcome.quality_score,
                'youtube_tracked': outcome.youtube_video_id is not None,
                'youtube_metrics': {
                    'retention': outcome.avg_retention_pct,
                    'engagement': outcome.engagement_rate,
                    'views': outcome.views_30d,
                }
            })

        # Check manifest for additional info
        if manifest_path and manifest_path.exists():
            try:
                with open(manifest_path, 'r') as f:
                    manifest = yaml.safe_load(f)
                    ri_section = manifest.get('recursive_improvement', {})
                    if ri_section:
                        report['manifest_tracking'] = ri_section
            except Exception:
                pass

        return report


# Integration helpers for auto_generate.py

def get_lessons_for_generation(
    topic: str,
    duration_minutes: int,
    desired_outcome: Optional[str] = None,
    project_root: Optional[Path] = None,
) -> Tuple[List[str], str]:
    """
    Convenience function to get lessons for generation.

    Returns:
        Tuple of (lesson_ids, context_string)
    """
    agent = DreamweaverRecursiveAgent(project_root=project_root)
    applied = agent.prepare_generation(
        topic=topic,
        duration_minutes=duration_minutes,
        desired_outcome=desired_outcome,
    )
    return applied.lesson_ids, applied.lessons_context


def record_generation_outcome(
    session_name: str,
    lesson_ids: List[str],
    generation_success: bool,
    quality_score: Optional[float] = None,
    stages_completed: Optional[List[str]] = None,
    stages_failed: Optional[List[str]] = None,
    execution_time_seconds: Optional[float] = None,
    estimated_cost_usd: Optional[float] = None,
    youtube_video_id: Optional[str] = None,
    project_root: Optional[Path] = None,
) -> str:
    """
    Convenience function to record generation outcome.

    Returns:
        outcome_id
    """
    agent = DreamweaverRecursiveAgent(project_root=project_root)

    metrics = {
        'generation_success': generation_success,
        'quality_score': quality_score,
        'stages_completed': stages_completed or [],
        'stages_failed': stages_failed or [],
        'execution_time_seconds': execution_time_seconds,
        'estimated_cost_usd': estimated_cost_usd,
    }

    # Create minimal AppliedLessons
    applied = AppliedLessons(
        lesson_ids=lesson_ids,
        lessons_context='',  # Not needed for recording
        categories={},
    )

    return agent.record_generation_outcome(
        session_name=session_name,
        applied_lessons=applied,
        metrics=metrics,
        youtube_video_id=youtube_video_id,
    )


# CLI interface for testing
def main():
    """CLI for testing the Dreamweaver recursive agent."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Dreamweaver Recursive Agent CLI'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Test lesson retrieval
    test_parser = subparsers.add_parser('test', help='Test lesson retrieval')
    test_parser.add_argument('--topic', required=True, help='Topic to test')
    test_parser.add_argument('--duration', type=int, default=25, help='Duration in minutes')
    test_parser.add_argument('--outcome', help='Desired outcome')
    test_parser.add_argument('--limit', type=int, default=10, help='Max lessons')

    # Show session report
    report_parser = subparsers.add_parser('report', help='Show session lessons report')
    report_parser.add_argument('session', help='Session name')

    args = parser.parse_args()

    if args.command == 'test':
        agent = DreamweaverRecursiveAgent()
        applied = agent.prepare_generation(
            topic=args.topic,
            duration_minutes=args.duration,
            desired_outcome=args.outcome,
            limit=args.limit,
        )

        print(f"\n=== Lessons for: {args.topic} ===")
        print(f"Duration: {args.duration} min, Outcome: {args.outcome or 'any'}")
        print(f"\nApplied Lessons ({len(applied.lesson_ids)}):")
        for lid in applied.lesson_ids:
            print(f"  - {lid}")

        print(f"\nCategories: {applied.categories}")
        print(f"\n=== Context String ===")
        print(applied.lessons_context or "(no lessons found)")

    elif args.command == 'report':
        agent = DreamweaverRecursiveAgent()
        report = agent.get_session_lessons_report(args.session)

        print(f"\n=== Lessons Report: {args.session} ===")
        print(yaml.dump(report, default_flow_style=False))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
