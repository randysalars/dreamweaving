#!/usr/bin/env python3
"""
Recursive Improvement Scheduler

Orchestrates automated improvement cycles:
1. Process pending YouTube outcome checks (daily 3 AM)
2. Recalculate lesson rankings (weekly Sunday 4 AM)
3. Sync YouTube analytics for tracked videos (daily 5 AM)
4. Knowledge optimization and gap detection (weekly Monday 6 AM)

This module connects YouTube performance data to lesson effectiveness,
closing the feedback loop for self-improving session generation.

Usage:
    # Run specific job
    python3 scripts/automation/recursive_improvement_scheduler.py --job process_pending
    python3 scripts/automation/recursive_improvement_scheduler.py --job recalculate_rankings
    python3 scripts/automation/recursive_improvement_scheduler.py --job sync_youtube
    python3 scripts/automation/recursive_improvement_scheduler.py --job optimize_knowledge

    # Run all jobs (for testing)
    python3 scripts/automation/recursive_improvement_scheduler.py --all

    # Dry run (show what would happen)
    python3 scripts/automation/recursive_improvement_scheduler.py --job process_pending --dry-run
"""

import argparse
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class JobResult:
    """Result of a scheduled job execution."""
    job_name: str
    success: bool
    items_processed: int
    errors: List[str]
    duration_seconds: float
    details: Dict[str, Any]


class RecursiveImprovementScheduler:
    """
    Orchestrates recursive improvement automation.

    Handles the connection between:
    - Session generation outcomes
    - YouTube analytics data
    - Lesson effectiveness scoring
    - Knowledge base optimization
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        dry_run: bool = False
    ):
        """
        Initialize scheduler.

        Args:
            project_root: Path to project root
            dry_run: If True, don't make actual changes
        """
        self.project_root = project_root or PROJECT_ROOT
        self.dry_run = dry_run

        # Load configuration
        self.config = self._load_config()

        # Lazy-loaded components
        self._youtube_client = None
        self._feedback_store = None
        self._effectiveness_engine = None
        self._recursive_improver = None

    def _load_config(self) -> Dict[str, Any]:
        """Load recursive improvement config from automation_config.yaml."""
        config_path = self.project_root / "config" / "automation_config.yaml"

        if config_path.exists():
            with open(config_path, 'r') as f:
                full_config = yaml.safe_load(f) or {}
                return full_config.get('recursive_improvement', {})

        # Default config
        return {
            'enabled': True,
            'min_applications': 3,
            'youtube_check_delay_days': 7,
        }

    def _get_youtube_client(self):
        """Get or create YouTube client."""
        if self._youtube_client is None:
            try:
                from scripts.automation.youtube_client import YouTubeClient
                self._youtube_client = YouTubeClient()
            except Exception as e:
                logger.error(f"Failed to initialize YouTube client: {e}")
                return None
        return self._youtube_client

    def _get_feedback_store(self):
        """Get or create FeedbackStore."""
        if self._feedback_store is None:
            from scripts.ai.learning.feedback_store import FeedbackStore
            feedback_path = self.project_root / "knowledge" / "feedback"
            self._feedback_store = FeedbackStore(feedback_path)
        return self._feedback_store

    def _get_effectiveness_engine(self):
        """Get or create EffectivenessEngine."""
        if self._effectiveness_engine is None:
            from scripts.ai.learning.effectiveness_engine import (
                EffectivenessEngine,
            )
            self._effectiveness_engine = EffectivenessEngine(
                feedback_store=self._get_feedback_store()
            )
        return self._effectiveness_engine

    def _get_recursive_improver(self):
        """Get or create RecursiveImprover."""
        if self._recursive_improver is None:
            from scripts.ai.recursive_improver import RecursiveImprover
            self._recursive_improver = RecursiveImprover(self.project_root)
        return self._recursive_improver

    # ==================== Job 1: Process Pending Outcomes ====================

    def process_pending_outcomes(self) -> JobResult:
        """
        Process sessions awaiting YouTube metrics.

        Checks sessions that:
        1. Have a YouTube video ID
        2. Were uploaded at least N days ago (youtube_check_delay_days)
        3. Haven't had YouTube metrics fetched yet

        For each, fetches YouTube analytics and updates lesson effectiveness.
        """
        start_time = datetime.now()
        job_name = "process_pending_outcomes"
        errors = []
        processed = 0
        details = {'sessions_checked': [], 'sessions_updated': []}

        logger.info(f"Starting {job_name}")

        try:
            feedback_store = self._get_feedback_store()
            youtube_client = self._get_youtube_client()

            # Get pending checks that are due
            delay_days = self.config.get('youtube_check_delay_days', 7)
            pending = feedback_store.get_pending_outcome_checks()

            ready_to_check = []
            for check in pending:
                if check.youtube_video_id:
                    age_days = (datetime.now() - check.scheduled_at).days
                    if age_days >= delay_days:
                        ready_to_check.append(check)

            logger.info(f"Found {len(ready_to_check)} pending checks ready to process")

            for check in ready_to_check:
                details['sessions_checked'].append(check.session_name)

                if self.dry_run:
                    logger.info(f"[DRY RUN] Would fetch analytics for {check.session_name}")
                    continue

                try:
                    # Fetch YouTube analytics
                    if youtube_client:
                        analytics = youtube_client.get_video_analytics(
                            video_id=check.youtube_video_id,
                            days=30  # Get 30 days of data
                        )

                        if 'error' not in analytics:
                            # Update outcome record with YouTube metrics
                            outcome = feedback_store.get_session_outcome(check.session_name)
                            if outcome:
                                # Calculate engagement rate
                                views = analytics.get('views', 0)
                                likes = analytics.get('likes', 0)
                                comments = analytics.get('comments', 0)
                                engagement_rate = (likes + comments) / max(views, 1)

                                # Update outcome
                                outcome.views_7_day = views
                                outcome.avg_retention_pct = analytics.get('averageViewPercentage')
                                outcome.likes = likes
                                outcome.comments_count = comments
                                outcome.engagement_rate = engagement_rate
                                outcome.metrics_complete = True
                                outcome.youtube_pending = False
                                outcome.measured_at = datetime.now()

                                feedback_store.update_outcome(outcome)

                                # Update effectiveness for applied lessons
                                baseline_retention = self.config.get('baseline_metrics', {}).get('avg_retention_pct', 35.0)
                                baseline_engagement = self.config.get('baseline_metrics', {}).get('avg_engagement_rate', 0.03)

                                for lesson_id in outcome.lesson_ids:
                                    # Update with immediate metrics
                                    feedback_store.update_effectiveness(
                                        lesson_id=lesson_id,
                                        outcome=outcome,
                                    )
                                    # Update with YouTube metrics
                                    if outcome.avg_retention_pct is not None:
                                        feedback_store.update_effectiveness_youtube(
                                            lesson_id=lesson_id,
                                            retention_pct=outcome.avg_retention_pct,
                                            engagement_rate=engagement_rate,
                                            baseline_retention=baseline_retention,
                                            baseline_engagement=baseline_engagement,
                                        )

                                # Remove from pending
                                feedback_store.complete_pending_check(check.record_id)

                                details['sessions_updated'].append(check.session_name)
                                processed += 1

                                logger.info(
                                    f"Updated {check.session_name}: "
                                    f"{views} views, {analytics.get('averageViewPercentage', 0):.1f}% retention"
                                )
                        else:
                            errors.append(f"{check.session_name}: {analytics.get('error')}")
                    else:
                        errors.append(f"{check.session_name}: YouTube client not available")

                except Exception as e:
                    errors.append(f"{check.session_name}: {str(e)}")
                    logger.error(f"Error processing {check.session_name}: {e}")

        except Exception as e:
            errors.append(f"Job failed: {str(e)}")
            logger.error(f"Job {job_name} failed: {e}")

        duration = (datetime.now() - start_time).total_seconds()

        return JobResult(
            job_name=job_name,
            success=len(errors) == 0,
            items_processed=processed,
            errors=errors,
            duration_seconds=duration,
            details=details,
        )

    # ==================== Job 2: Recalculate Rankings ====================

    def recalculate_rankings(self) -> JobResult:
        """
        Recalculate effectiveness scores for all lessons.

        This applies time decay and updates rankings based on
        all accumulated outcome data.
        """
        start_time = datetime.now()
        job_name = "recalculate_rankings"
        errors = []
        processed = 0
        details = {'lessons_updated': []}

        logger.info(f"Starting {job_name}")

        try:
            if self.dry_run:
                logger.info("[DRY RUN] Would recalculate all lesson rankings")
            else:
                effectiveness_engine = self._get_effectiveness_engine()

                # Recalculate baseline metrics
                effectiveness_engine.recalculate_baseline()
                logger.info("Recalculated baseline metrics")

                # Recalculate all rankings
                effectiveness_engine.recalculate_all_rankings()

                # Count updated lessons
                feedback_store = self._get_feedback_store()
                records = feedback_store.get_all_effectiveness_records()
                processed = len(records)

                for record in records:
                    details['lessons_updated'].append(record.lesson_id)

                logger.info(f"Recalculated rankings for {processed} lessons")

        except Exception as e:
            errors.append(f"Job failed: {str(e)}")
            logger.error(f"Job {job_name} failed: {e}")

        duration = (datetime.now() - start_time).total_seconds()

        return JobResult(
            job_name=job_name,
            success=len(errors) == 0,
            items_processed=processed,
            errors=errors,
            duration_seconds=duration,
            details=details,
        )

    # ==================== Job 3: Sync YouTube Analytics ====================

    def sync_youtube_analytics(self) -> JobResult:
        """
        Sync YouTube analytics for all tracked videos.

        Updates metrics for videos that haven't been checked recently.
        """
        start_time = datetime.now()
        job_name = "sync_youtube_analytics"
        errors = []
        processed = 0
        details = {'videos_synced': []}

        logger.info(f"Starting {job_name}")

        try:
            youtube_client = self._get_youtube_client()
            feedback_store = self._get_feedback_store()

            if not youtube_client:
                errors.append("YouTube client not available")
            else:
                # Get all outcomes with YouTube video IDs
                outcomes = feedback_store.get_outcomes_with_youtube_metrics()

                for outcome in outcomes:
                    if not outcome.youtube_video_id:
                        continue

                    if self.dry_run:
                        logger.info(f"[DRY RUN] Would sync analytics for {outcome.session_name}")
                        continue

                    try:
                        analytics = youtube_client.get_video_analytics(
                            video_id=outcome.youtube_video_id,
                            days=30
                        )

                        if 'error' not in analytics:
                            views = analytics.get('views', 0)
                            likes = analytics.get('likes', 0)
                            comments = analytics.get('comments', 0)
                            engagement_rate = (likes + comments) / max(views, 1)

                            outcome.views_30d = views
                            outcome.avg_retention_pct = analytics.get('averageViewPercentage')
                            outcome.likes = likes
                            outcome.comments = comments
                            outcome.engagement_rate = engagement_rate

                            feedback_store.update_outcome(outcome)

                            details['videos_synced'].append(outcome.session_name)
                            processed += 1

                    except Exception as e:
                        errors.append(f"{outcome.session_name}: {str(e)}")

        except Exception as e:
            errors.append(f"Job failed: {str(e)}")
            logger.error(f"Job {job_name} failed: {e}")

        duration = (datetime.now() - start_time).total_seconds()

        return JobResult(
            job_name=job_name,
            success=len(errors) == 0,
            items_processed=processed,
            errors=errors,
            duration_seconds=duration,
            details=details,
        )

    # ==================== Job 4: Optimize Knowledge ====================

    def optimize_knowledge(self) -> JobResult:
        """
        Knowledge optimization and gap detection.

        Analyzes lesson effectiveness to:
        1. Identify underperforming lessons
        2. Suggest improvements
        3. Archive consistently poor lessons
        4. Recalculate baselines
        """
        start_time = datetime.now()
        job_name = "optimize_knowledge"
        errors = []
        processed = 0
        details = {
            'underperforming': [],
            'archived': [],
            'suggestions': [],
        }

        logger.info(f"Starting {job_name}")

        try:
            if self.dry_run:
                logger.info("[DRY RUN] Would optimize knowledge base")
            else:
                effectiveness_engine = self._get_effectiveness_engine()
                feedback_store = self._get_feedback_store()

                # Load all lessons
                lessons_path = self.project_root / "knowledge" / "lessons_learned.yaml"
                if lessons_path.exists():
                    with open(lessons_path, 'r') as f:
                        data = yaml.safe_load(f) or {}
                        lessons = data.get('lessons', [])
                else:
                    lessons = []

                # Find underperforming lessons
                archive_threshold = self.config.get('archive_threshold', 30.0)
                min_applications = self.config.get('min_applications', 3)

                underperforming = effectiveness_engine.get_underperforming_lessons(
                    lessons=lessons,
                    threshold=40.0,
                    min_applications=min_applications,
                )

                for lesson in underperforming:
                    details['underperforming'].append({
                        'id': lesson.get('id'),
                        'score': lesson.get('effectiveness_score'),
                        'success_rate': lesson.get('success_rate'),
                    })

                    # Generate improvement suggestions
                    suggestions = effectiveness_engine.suggest_lesson_improvements(lesson)
                    details['suggestions'].extend([
                        f"{lesson.get('id')}: {s}" for s in suggestions
                    ])

                    # Archive if below threshold
                    if lesson.get('effectiveness_score', 50) < archive_threshold:
                        details['archived'].append(lesson.get('id'))
                        # Mark as archived in effectiveness record
                        record = feedback_store.get_lesson_effectiveness(lesson.get('id'))
                        if record:
                            record.archived = True
                            feedback_store.save_effectiveness_record(record)

                    processed += 1

                logger.info(
                    f"Found {len(underperforming)} underperforming lessons, "
                    f"archived {len(details['archived'])}"
                )

        except Exception as e:
            errors.append(f"Job failed: {str(e)}")
            logger.error(f"Job {job_name} failed: {e}")

        duration = (datetime.now() - start_time).total_seconds()

        return JobResult(
            job_name=job_name,
            success=len(errors) == 0,
            items_processed=processed,
            errors=errors,
            duration_seconds=duration,
            details=details,
        )

    # ==================== Run Improvement Cycle ====================

    def run_improvement_cycle(self, agent_type: str = 'dreamweaver') -> Dict[str, Any]:
        """
        Run a complete improvement cycle.

        This is the main entry point for manual improvement runs.

        Args:
            agent_type: Type of agent to improve (dreamweaver, rag, website)

        Returns:
            Cycle results including all job results
        """
        logger.info(f"Starting improvement cycle for {agent_type}")
        start_time = datetime.now()

        results = {}

        # Run jobs in order
        results['process_pending'] = self.process_pending_outcomes()
        results['sync_youtube'] = self.sync_youtube_analytics()
        results['recalculate_rankings'] = self.recalculate_rankings()
        results['optimize_knowledge'] = self.optimize_knowledge()

        duration = (datetime.now() - start_time).total_seconds()

        return {
            'agent_type': agent_type,
            'started_at': start_time.isoformat(),
            'duration_seconds': duration,
            'jobs': {k: v.__dict__ for k, v in results.items()},
            'success': all(r.success for r in results.values()),
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Recursive Improvement Scheduler'
    )
    parser.add_argument(
        '--job',
        choices=['process_pending', 'recalculate_rankings', 'sync_youtube', 'optimize_knowledge'],
        help='Specific job to run'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all jobs (improvement cycle)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would happen without making changes'
    )
    parser.add_argument(
        '--agent',
        default='dreamweaver',
        choices=['dreamweaver', 'rag', 'website'],
        help='Agent type for improvement cycle'
    )

    args = parser.parse_args()

    scheduler = RecursiveImprovementScheduler(dry_run=args.dry_run)

    if args.all:
        results = scheduler.run_improvement_cycle(agent_type=args.agent)
        print(yaml.dump(results, default_flow_style=False))

    elif args.job:
        job_map = {
            'process_pending': scheduler.process_pending_outcomes,
            'recalculate_rankings': scheduler.recalculate_rankings,
            'sync_youtube': scheduler.sync_youtube_analytics,
            'optimize_knowledge': scheduler.optimize_knowledge,
        }

        result = job_map[args.job]()
        print(f"\n=== {result.job_name} ===")
        print(f"Success: {result.success}")
        print(f"Processed: {result.items_processed}")
        print(f"Duration: {result.duration_seconds:.1f}s")
        if result.errors:
            print(f"Errors: {result.errors}")
        if result.details:
            print(f"Details: {yaml.dump(result.details, default_flow_style=False)}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
