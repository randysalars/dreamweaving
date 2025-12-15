#!/usr/bin/env python3
"""
Nightly Builder

Orchestrates nightly video generation (9pm-3am MST):
1. Fetches unused topics from Notion RAG database
2. Runs auto_generate.py for each topic
3. Computes quality scores
4. Updates state database

Usage:
    # Generate 5 sessions (default)
    python -m scripts.automation.nightly_builder

    # Generate specific count
    python -m scripts.automation.nightly_builder --count 3

    # Dry run (no actual generation)
    python -m scripts.automation.nightly_builder --dry-run

    # Use specific topic instead of Notion
    python -m scripts.automation.nightly_builder --topic "Finding Inner Peace"
"""

import argparse
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib3.exceptions import ProtocolError
from requests.exceptions import ConnectionError, ChunkedEncodingError

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / '.env')

from scripts.automation.config_loader import load_config, setup_logging
from scripts.automation.state_db import StateDatabase
from scripts.automation.quality_scorer import compute_quality_score
from scripts.automation.topic_validator import validate_topic, TopicValidation
from scripts.automation.topic_enhancer import enhance_topic, TopicEnhancement

logger = logging.getLogger(__name__)


def retry_on_connection_error(max_retries: int = 3, delay: float = 5.0):
    """Decorator to retry on connection errors.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds

    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, ProtocolError, ChunkedEncodingError,
                        OSError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Connection error on attempt {attempt + 1}/{max_retries}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"Connection error after {max_retries} attempts: {e}"
                        )
            raise last_error
        return wrapper
    return decorator


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug.

    Args:
        text: Input text

    Returns:
        Kebab-case slug
    """
    # Lowercase
    slug = text.lower()
    # Remove special characters
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Trim
    slug = slug.strip('-')
    # Limit length
    return slug[:50]


class NightlyBuilder:
    """Orchestrates nightly video generation."""

    def __init__(self, config: Dict[str, Any], db: StateDatabase):
        """Initialize nightly builder.

        Args:
            config: Configuration dictionary
            db: State database instance
        """
        self.config = config
        self.db = db
        self.notion_manager = None  # Lazy load

    def _get_notion_manager(self):
        """Lazy load Notion topic manager.

        Returns:
            NotionTopicManager instance
        """
        if self.notion_manager is None:
            # Import from auto_generate.py
            from scripts.ai.auto_generate import NotionTopicManager

            notion_token = os.getenv('NOTION_TOKEN')
            if not notion_token:
                raise RuntimeError("NOTION_TOKEN not set in environment")

            self.notion_manager = NotionTopicManager(
                token=notion_token,
                database_id=self.config['notion']['topic_database_id'],
                root_page_id=self.config['notion']['root_page_id'],
            )

        return self.notion_manager

    @retry_on_connection_error(max_retries=3, delay=5.0)
    def _fetch_topic_from_notion(self) -> Dict[str, Any]:
        """Fetch a random unused topic from Notion with retry logic.

        Returns:
            Topic data dict with 'title', 'id', etc.
        """
        notion = self._get_notion_manager()
        return notion.pick_random_unused()

    @retry_on_connection_error(max_retries=3, delay=5.0)
    def _mark_topic_used_with_retry(self, topic_data: Dict[str, Any]) -> None:
        """Mark a Notion topic as used with retry logic.

        Args:
            topic_data: Topic data from Notion

        Note: This method recreates the Notion manager to handle stale connections
        after long-running session generation (50+ minutes).
        """
        # Recreate Notion manager to avoid stale connection after long session
        self.notion_manager = None
        notion = self._get_notion_manager()
        notion.mark_used(topic_data)

    def _mark_topic_invalid(self, topic_data: Dict[str, Any], reason: str) -> None:
        """Mark a topic as invalid in Notion so it won't be picked again.

        Args:
            topic_data: Topic data from Notion
            reason: Why the topic is invalid
        """
        try:
            notion = self._get_notion_manager()
            page_id = topic_data.get('id')
            if not page_id:
                return

            # Update the topic with "Invalid" status
            updates = {
                "properties": {
                    "Status": {"select": {"name": "Invalid"}},
                }
            }

            # Also add a note if there's a Notes property
            if topic_data.get('is_db_row'):
                updates["properties"]["Used At"] = {
                    "date": {"start": datetime.now().isoformat()}
                }

            notion.session.patch(
                f"https://api.notion.com/v1/pages/{page_id}",
                headers=notion._headers(),
                json=updates,
                timeout=notion.timeout,
            )
            logger.info(f"Marked topic as invalid: {reason}")
        except Exception as e:
            logger.warning(f"Failed to mark topic as invalid: {e}")

    def _fetch_validated_topic(self, max_attempts: int = 10) -> Optional[Dict[str, Any]]:
        """Fetch a validated dreamweaving topic from Notion.

        Tries multiple topics until finding a valid one, marking invalid ones
        so they won't be picked again.

        Args:
            max_attempts: Maximum topics to try before giving up

        Returns:
            Validated topic data or None if no valid topics found
        """
        attempted_ids = set()

        for attempt in range(max_attempts):
            try:
                topic_data = self._fetch_topic_from_notion()
                topic_id = topic_data.get('id')

                # Avoid re-checking same topic
                if topic_id in attempted_ids:
                    continue
                attempted_ids.add(topic_id)

                topic_title = topic_data.get('title', '')
                logger.info(f"Validating topic ({attempt + 1}/{max_attempts}): {topic_title}")

                # Validate the topic
                validation = validate_topic(topic_title, use_llm=True)

                if validation.is_valid:
                    logger.info(f"Topic validated: {validation.reason}")
                    return topic_data
                else:
                    logger.warning(f"Topic invalid: {validation.reason}")
                    # Mark as invalid in Notion
                    self._mark_topic_invalid(topic_data, validation.reason)

            except RuntimeError as e:
                if "No unused topics" in str(e):
                    logger.error("No more unused topics available in Notion")
                    return None
                raise

        logger.error(f"Could not find valid topic after {max_attempts} attempts")
        return None

    def run(
        self,
        count: int = 5,
        dry_run: bool = False,
        topics: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Run nightly generation.

        Args:
            count: Number of sessions to generate
            dry_run: If True, don't actually generate
            topics: Optional list of specific topics (instead of Notion)

        Returns:
            List of result dicts with status for each session
        """
        results = []
        start_time = datetime.now()

        logger.info(f"Starting nightly build: {count} sessions, dry_run={dry_run}")

        for i in range(count):
            session_num = i + 1
            logger.info(f"\n{'='*60}")
            logger.info(f"Session {session_num}/{count}")
            logger.info(f"{'='*60}")

            try:
                # Get topic
                if topics and i < len(topics):
                    topic_title = topics[i]
                    topic_data = {'title': topic_title, 'id': None, 'is_manual': True}
                else:
                    # Fetch and validate topic from Notion
                    topic_data = self._fetch_validated_topic()
                    if topic_data is None:
                        logger.error("Could not find a valid dreamweaving topic")
                        results.append({
                            'session': None,
                            'status': 'skipped',
                            'error': 'No valid topics available',
                        })
                        continue
                    topic_title = topic_data['title']

                # Enhance topic if it's generic or needs improvement
                enhancement = enhance_topic(topic_title, use_llm=True)
                if enhancement.was_enhanced:
                    logger.info(f"Topic enhanced: '{topic_title}' → '{enhancement.enhanced_title}'")
                    topic_title = enhancement.enhanced_title
                    # Store original for reference
                    topic_data['original_title'] = topic_data.get('title', '')
                    topic_data['title'] = topic_title
                    topic_data['seo_title'] = enhancement.seo_title
                    topic_data['theme_category'] = enhancement.theme_category
                    topic_data['suggested_tags'] = enhancement.suggested_tags

                session_name = slugify(topic_title)

                # Check if already exists
                if self.db.session_exists(session_name):
                    # Add timestamp suffix
                    session_name = f"{session_name}-{datetime.now().strftime('%H%M')}"

                logger.info(f"Topic: {topic_title}")
                logger.info(f"Session name: {session_name}")

                if dry_run:
                    logger.info("[DRY RUN] Would generate session")
                    results.append({
                        'session': session_name,
                        'topic': topic_title,
                        'status': 'dry_run',
                    })
                    continue

                # Create DB record
                self.db.create_session(
                    session_name=session_name,
                    topic=topic_title,
                    notion_topic_id=topic_data.get('id')
                )

                # Generate session
                result = self._generate_session(session_name, topic_title)

                if result['success']:
                    # Mark Notion topic as used (if from Notion)
                    if not topic_data.get('is_manual') and topic_data.get('id'):
                        try:
                            self._mark_topic_used_with_retry(topic_data)
                            logger.info("Marked Notion topic as used")
                        except Exception as e:
                            logger.warning(f"Failed to mark topic as used: {e}")

                    # Compute quality score
                    session_path = PROJECT_ROOT / 'sessions' / session_name
                    quality_score = compute_quality_score(session_path)
                    logger.info(f"Quality score: {quality_score}")

                    # Update DB
                    self.db.mark_complete(
                        session_name=session_name,
                        session_path=str(session_path),
                        video_path=str(session_path / 'output' / 'youtube_package' / 'final_video.mp4'),
                        quality_score=quality_score,
                        duration_seconds=result.get('duration_seconds'),
                    )

                    # Check if uploaded to website (auto_generate does this)
                    website_url = f"https://www.salars.net/dreamweavings/{session_name}"
                    self.db.mark_website_uploaded(session_name, website_url)

                    results.append({
                        'session': session_name,
                        'topic': topic_title,
                        'status': 'success',
                        'quality_score': quality_score,
                        'duration_seconds': result.get('duration_seconds'),
                    })
                else:
                    self.db.mark_failed(session_name, result.get('error', 'Unknown error'))
                    results.append({
                        'session': session_name,
                        'topic': topic_title,
                        'status': 'failed',
                        'error': result.get('error'),
                    })

            except Exception as e:
                logger.error(f"Failed to process session {session_num}: {e}")
                results.append({
                    'session': None,
                    'status': 'error',
                    'error': str(e),
                })

        # Summary
        elapsed = (datetime.now() - start_time).total_seconds()
        success_count = sum(1 for r in results if r.get('status') == 'success')
        failed_count = sum(1 for r in results if r.get('status') in ['failed', 'error'])

        logger.info(f"\n{'='*60}")
        logger.info("NIGHTLY BUILD COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total time: {elapsed/60:.1f} minutes")
        logger.info(f"Success: {success_count}/{count}")
        logger.info(f"Failed: {failed_count}/{count}")

        return results

    def _create_session_plan(self, topic: str, session_name: str) -> Dict[str, Any]:
        """Create execution plan before spawning generation subprocess.

        This pre-flight check ensures all resources are available before
        committing to a full generation run.

        Args:
            topic: Session topic
            session_name: Session identifier

        Returns:
            Dict with plan results including blockers, warnings, cost estimate
        """
        try:
            from scripts.ai.generation_planner import GenerationPlanner

            planner = GenerationPlanner(
                project_root=PROJECT_ROOT,
                mode=self.config['generation']['mode'],
            )

            plan = planner.create_plan(
                topic=topic,
                duration_minutes=self.config['generation'].get('duration', 30),
                mode=self.config['generation']['mode'],
                image_method=self.config['generation']['image_method'],
                session_name=session_name,
            )

            return {
                'success': True,
                'has_blockers': plan.has_blockers(),
                'blockers': plan.blockers if plan.has_blockers() else [],
                'warnings': plan.warnings,
                'cost_estimate': plan.cost_estimate.total_usd if plan.cost_estimate else 0,
                'stages_count': len(plan.stages),
                'feasibility_score': plan.feasibility_score,
            }

        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return {
                'success': False,
                'has_blockers': True,
                'blockers': [f"Planning error: {e}"],
                'warnings': [],
                'cost_estimate': 0,
            }

    def _generate_session(self, session_name: str, topic: str) -> Dict[str, Any]:
        """Run auto_generate.py for a single session.

        Args:
            session_name: Session identifier
            topic: Topic title

        Returns:
            Result dict with success status and details
        """
        # First, run planning check
        self.db.update_status(session_name, 'planning')
        logger.info(f"Creating execution plan for: {topic}")

        plan_result = self._create_session_plan(topic, session_name)

        if plan_result.get('has_blockers'):
            blockers = plan_result.get('blockers', ['Unknown blocker'])
            logger.error(f"Planning found blockers: {blockers}")
            return {
                'success': False,
                'error': f"Planning blockers: {'; '.join(blockers)}",
                'plan_result': plan_result,
            }

        # Log plan summary
        logger.info(f"Plan created: ${plan_result.get('cost_estimate', 0):.2f} estimated cost")
        logger.info(f"Feasibility score: {plan_result.get('feasibility_score', 0):.0%}")

        for warning in plan_result.get('warnings', []):
            logger.warning(f"Plan warning: {warning}")

        # Proceed with generation
        self.db.update_status(session_name, 'generating')

        start_time = time.time()

        # Build command
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / 'scripts' / 'ai' / 'auto_generate.py'),
            '--topic', topic,
            '--name', session_name,
            '--mode', self.config['generation']['mode'],
            '--image-method', self.config['generation']['image_method'],
            '--nightly',  # Skip YouTube package, use aggressive cleanup
        ]

        logger.info(f"Running: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=7200,  # 2 hour timeout (SD can be slow)
            )

            duration = time.time() - start_time
            logger.info(f"Generation completed in {duration/60:.1f} minutes")

            if result.returncode == 0:
                logger.info("Generation successful")
                return {
                    'success': True,
                    'duration_seconds': int(duration),
                    'stdout': result.stdout[-2000:] if result.stdout else '',
                }
            else:
                logger.error(f"Generation failed with return code {result.returncode}")
                logger.error(f"stderr: {result.stderr[-1000:] if result.stderr else 'N/A'}")
                return {
                    'success': False,
                    'error': result.stderr[-2000:] if result.stderr else f'Return code: {result.returncode}',
                    'duration_seconds': int(duration),
                }

        except subprocess.TimeoutExpired:
            logger.error("Generation timed out after 2 hours")
            return {
                'success': False,
                'error': 'Generation timed out after 2 hours',
            }
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    def get_pending_topics(self, count: int = 5) -> List[Dict]:
        """Get list of pending topics from Notion.

        Args:
            count: Number of topics to fetch

        Returns:
            List of topic dicts
        """
        notion = self._get_notion_manager()
        topics = notion.get_unused_topics()
        return topics[:count]


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Nightly Builder')
    parser.add_argument('--count', type=int, default=5, help='Number of sessions to generate')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no actual generation)')
    parser.add_argument('--topic', type=str, action='append', help='Specific topic (can be repeated)')
    parser.add_argument('--list-topics', action='store_true', help='List pending Notion topics')
    parser.add_argument('--config', type=str, help='Config file path')

    args = parser.parse_args()

    # Load config and setup logging
    config = load_config(Path(args.config) if args.config else None)
    setup_logging(config)

    # Initialize database
    db = StateDatabase(Path(config['database']['path']))
    db.init_schema()

    # Create builder
    builder = NightlyBuilder(config, db)

    if args.list_topics:
        print("\n=== Pending Notion Topics ===")
        topics = builder.get_pending_topics(count=10)
        for i, topic in enumerate(topics, 1):
            print(f"{i}. {topic['title']}")
        print(f"\nTotal pending: {len(topics)}")
        return

    # Run generation
    results = builder.run(
        count=args.count,
        dry_run=args.dry_run,
        topics=args.topic,
    )

    # Print summary
    print("\n=== Generation Results ===")
    for result in results:
        status = result.get('status', 'unknown')
        session = result.get('session', 'N/A')
        topic = result.get('topic', 'N/A')[:40]

        if status == 'success':
            score = result.get('quality_score', 0)
            print(f"  [OK] {session} ({topic}...) - Score: {score}")
        elif status == 'dry_run':
            print(f"  [DRY] {session} ({topic}...)")
        else:
            error = result.get('error', 'Unknown')[:50]
            print(f"  [FAIL] {session} - {error}")

    db.close()


if __name__ == '__main__':
    main()
