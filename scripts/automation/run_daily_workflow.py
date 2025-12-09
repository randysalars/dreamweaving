#!/usr/bin/env python3
"""
Daily Workflow Runner

Unified script for running the complete daily YouTube workflow:
1. Generate sessions (nightly builder)
2. Upload long-form video
3. Create and upload short

Usage:
    # Full workflow (all steps)
    python scripts/automation/run_daily_workflow.py

    # Dry run (preview only)
    python scripts/automation/run_daily_workflow.py --dry-run

    # Run specific steps
    python scripts/automation/run_daily_workflow.py --generate
    python scripts/automation/run_daily_workflow.py --upload
    python scripts/automation/run_daily_workflow.py --shorts

    # Generate only (with custom count)
    python scripts/automation/run_daily_workflow.py --generate --count 3

    # Upload only (unlisted for testing)
    python scripts/automation/run_daily_workflow.py --upload --privacy unlisted

    # Status check
    python scripts/automation/run_daily_workflow.py --status
"""

import argparse
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.automation.config_loader import load_config, setup_logging
from scripts.automation.state_db import StateDatabase

logger = logging.getLogger(__name__)


class DailyWorkflowRunner:
    """Orchestrates the complete daily YouTube workflow."""

    def __init__(self, config: Dict, db: StateDatabase):
        self.config = config
        self.db = db
        self.results: List[Dict] = []

    def run_step(
        self,
        step_name: str,
        module: str,
        args: List[str],
        dry_run: bool = False
    ) -> Dict:
        """Run a single workflow step.

        Args:
            step_name: Human-readable step name
            module: Python module path
            args: Additional arguments
            dry_run: Whether this is a dry run

        Returns:
            Result dict with success status
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"STEP: {step_name}")
        logger.info(f"{'='*60}")

        cmd = [sys.executable, '-m', module] + args
        if dry_run:
            cmd.append('--dry-run')

        logger.info(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout
            )

            # Log output
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    logger.info(f"  {line}")
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    logger.warning(f"  [stderr] {line}")

            success = result.returncode == 0
            return {
                'step': step_name,
                'success': success,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
            }

        except subprocess.TimeoutExpired:
            logger.error(f"{step_name} timed out after 1 hour")
            return {
                'step': step_name,
                'success': False,
                'error': 'Timeout after 1 hour',
            }
        except Exception as e:
            logger.error(f"{step_name} failed: {e}")
            return {
                'step': step_name,
                'success': False,
                'error': str(e),
            }

    def run_generate(
        self,
        count: int = 5,
        dry_run: bool = False,
        topics: Optional[List[str]] = None
    ) -> Dict:
        """Run nightly generation step.

        Args:
            count: Number of sessions to generate
            dry_run: Dry run mode
            topics: Specific topics (optional)

        Returns:
            Result dict
        """
        args = ['--count', str(count)]
        if topics:
            for topic in topics:
                args.extend(['--topic', topic])

        return self.run_step(
            'Session Generation',
            'scripts.automation.nightly_builder',
            args,
            dry_run=dry_run,
        )

    def run_upload(
        self,
        privacy: str = 'public',
        session: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict:
        """Run upload step.

        Args:
            privacy: Video privacy status
            session: Specific session (optional)
            dry_run: Dry run mode

        Returns:
            Result dict
        """
        args = ['--privacy', privacy]
        if session:
            args.extend(['--session', session])

        return self.run_step(
            'Video Upload',
            'scripts.automation.upload_scheduler',
            args,
            dry_run=dry_run,
        )

    def run_shorts(
        self,
        privacy: str = 'public',
        session: Optional[str] = None,
        preview: bool = False,
        dry_run: bool = False
    ) -> Dict:
        """Run shorts generation step.

        Args:
            privacy: Video privacy status
            session: Specific session (optional)
            preview: Preview only (no upload)
            dry_run: Dry run mode

        Returns:
            Result dict
        """
        args = ['--privacy', privacy]
        if session:
            args.extend(['--session', session])
        if preview:
            args.append('--preview')

        return self.run_step(
            'Shorts Generation & Upload',
            'scripts.automation.shorts_generator',
            args,
            dry_run=dry_run,
        )

    def run_full_workflow(
        self,
        count: int = 5,
        privacy: str = 'public',
        dry_run: bool = False
    ) -> List[Dict]:
        """Run the complete daily workflow.

        Args:
            count: Number of sessions to generate
            privacy: Video privacy status
            dry_run: Dry run mode

        Returns:
            List of result dicts for each step
        """
        results = []

        # Step 1: Generate sessions
        logger.info("\n" + "="*80)
        logger.info("PHASE 1: SESSION GENERATION")
        logger.info("="*80)
        result = self.run_generate(count=count, dry_run=dry_run)
        results.append(result)

        if not result['success'] and not dry_run:
            logger.warning("Generation failed, but continuing with upload if videos exist...")

        # Step 2: Upload long-form video
        logger.info("\n" + "="*80)
        logger.info("PHASE 2: LONG-FORM VIDEO UPLOAD")
        logger.info("="*80)
        result = self.run_upload(privacy=privacy, dry_run=dry_run)
        results.append(result)

        # Step 3: Create and upload short
        logger.info("\n" + "="*80)
        logger.info("PHASE 3: SHORTS CREATION & UPLOAD")
        logger.info("="*80)
        result = self.run_shorts(privacy=privacy, dry_run=dry_run)
        results.append(result)

        return results

    def get_status(self) -> Dict:
        """Get current workflow status from database.

        Returns:
            Status dict with counts and states
        """
        try:
            # Query sessions by state
            cursor = self.db.conn.cursor()

            # Count sessions by generation status
            cursor.execute("""
                SELECT generation_status, COUNT(*) as count
                FROM sessions
                GROUP BY generation_status
            """)
            status_counts = {row[0]: row[1] for row in cursor.fetchall()}

            # Get recently generated (last 24 hours)
            cursor.execute("""
                SELECT session_name, generation_status, created_at
                FROM sessions
                WHERE created_at > datetime('now', '-24 hours')
                ORDER BY created_at DESC
            """)
            recent = [
                {'name': row[0], 'status': row[1], 'created': row[2]}
                for row in cursor.fetchall()
            ]

            # Get upload-ready sessions (completed but not uploaded)
            cursor.execute("""
                SELECT session_name, quality_score
                FROM sessions
                WHERE generation_status = 'complete' AND uploaded_to_youtube = 0
                ORDER BY quality_score DESC
            """)
            upload_ready = [
                {'name': row[0], 'score': row[1]}
                for row in cursor.fetchall()
            ]

            # Get shorts candidates (on website but not on YouTube)
            cursor.execute("""
                SELECT session_name
                FROM sessions
                WHERE uploaded_to_website = 1 AND uploaded_to_youtube = 0
            """)
            shorts_candidates = [row[0] for row in cursor.fetchall()]

            return {
                'status_counts': status_counts,
                'recent_sessions': recent,
                'upload_ready': upload_ready,
                'shorts_candidates': shorts_candidates,
            }

        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {'error': str(e)}


def print_status(status: Dict) -> None:
    """Print formatted status information."""
    print("\n" + "="*60)
    print("DAILY WORKFLOW STATUS")
    print("="*60)

    print("\n--- Session Counts by Status ---")
    for state, count in status.get('status_counts', {}).items():
        print(f"  {state}: {count}")

    print("\n--- Recent Sessions (24h) ---")
    for session in status.get('recent_sessions', [])[:10]:
        print(f"  [{session['status']}] {session['name']}")

    print("\n--- Ready for Upload ---")
    for session in status.get('upload_ready', [])[:5]:
        score = session.get('score', 0) or 0
        print(f"  {session['name']} (score: {score:.1f})")

    print("\n--- Shorts Candidates (website-only) ---")
    for name in status.get('shorts_candidates', [])[:5]:
        print(f"  {name}")

    if status.get('error'):
        print(f"\n[ERROR] {status['error']}")


def print_results(results: List[Dict]) -> None:
    """Print formatted results summary."""
    print("\n" + "="*60)
    print("WORKFLOW RESULTS SUMMARY")
    print("="*60)

    for result in results:
        step = result['step']
        if result['success']:
            print(f"  [OK] {step}")
        else:
            error = result.get('error', f"Exit code {result.get('returncode')}")
            print(f"  [FAIL] {step} - {error}")


def main():
    parser = argparse.ArgumentParser(
        description='Daily Workflow Runner - Unified YouTube automation'
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--all', action='store_true', default=True,
        help='Run all steps (default)'
    )
    mode_group.add_argument(
        '--generate', action='store_true',
        help='Run generation step only'
    )
    mode_group.add_argument(
        '--upload', action='store_true',
        help='Run upload step only'
    )
    mode_group.add_argument(
        '--shorts', action='store_true',
        help='Run shorts step only'
    )
    mode_group.add_argument(
        '--status', action='store_true',
        help='Show workflow status'
    )

    # Common options
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Dry run mode (no actual changes)'
    )
    parser.add_argument(
        '--privacy', type=str, default='public',
        choices=['public', 'private', 'unlisted'],
        help='YouTube privacy status'
    )

    # Generation options
    parser.add_argument(
        '--count', type=int, default=5,
        help='Number of sessions to generate'
    )
    parser.add_argument(
        '--topic', type=str, action='append',
        help='Specific topic(s) for generation'
    )

    # Session selection
    parser.add_argument(
        '--session', type=str,
        help='Specific session for upload/shorts'
    )
    parser.add_argument(
        '--preview', action='store_true',
        help='Shorts preview only (no upload)'
    )

    # Config
    parser.add_argument(
        '--config', type=str,
        help='Config file path'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Load config
    config = load_config(Path(args.config) if args.config else None)
    setup_logging(config)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize database
    db = StateDatabase(Path(config['database']['path']))
    db.init_schema()

    # Create runner
    runner = DailyWorkflowRunner(config, db)

    try:
        if args.status:
            status = runner.get_status()
            print_status(status)
            return 0

        elif args.generate:
            result = runner.run_generate(
                count=args.count,
                topics=args.topic,
                dry_run=args.dry_run,
            )
            print_results([result])
            return 0 if result['success'] else 1

        elif args.upload:
            result = runner.run_upload(
                privacy=args.privacy,
                session=args.session,
                dry_run=args.dry_run,
            )
            print_results([result])
            return 0 if result['success'] else 1

        elif args.shorts:
            result = runner.run_shorts(
                privacy=args.privacy,
                session=args.session,
                preview=args.preview,
                dry_run=args.dry_run,
            )
            print_results([result])
            return 0 if result['success'] else 1

        else:
            # Full workflow
            results = runner.run_full_workflow(
                count=args.count,
                privacy=args.privacy,
                dry_run=args.dry_run,
            )
            print_results(results)

            # Return failure if any step failed
            all_success = all(r['success'] for r in results)
            return 0 if all_success else 1

    finally:
        db.close()


if __name__ == '__main__':
    sys.exit(main())
