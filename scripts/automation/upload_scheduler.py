#!/usr/bin/env python3
"""
Upload Scheduler

Selects and uploads videos to YouTube based on quality scores and analytics.

Usage:
    # Upload next video (auto-select based on quality)
    python -m scripts.automation.upload_scheduler

    # Upload specific session
    python -m scripts.automation.upload_scheduler --session my-session

    # Upload as unlisted (for testing)
    python -m scripts.automation.upload_scheduler --privacy unlisted

    # Dry run
    python -m scripts.automation.upload_scheduler --dry-run
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class UploadScheduler:
    """Selects and uploads videos to YouTube."""

    def __init__(self, config: Dict[str, Any], db, youtube_client, analytics_optimizer=None):
        """Initialize upload scheduler.

        Args:
            config: Configuration dictionary
            db: StateDatabase instance
            youtube_client: YouTubeClient instance
            analytics_optimizer: Optional AnalyticsOptimizer for timing
        """
        self.config = config
        self.db = db
        self.youtube = youtube_client
        self.analytics = analytics_optimizer

    def select_next_upload(self) -> Optional[Dict[str, Any]]:
        """Select next video to upload based on configured strategy.

        Strategy options:
        - quality: Highest quality score first
        - fifo: Oldest first
        - priority: Manual priority, then quality

        Returns:
            Session dict or None if queue is empty
        """
        strategy = self.config['upload']['selection_strategy']
        logger.info(f"Selecting next upload (strategy: {strategy})")

        session = self.db.get_next_upload(strategy=strategy)

        if session:
            logger.info(f"Selected: {session['session_name']} (score: {session.get('quality_score', 'N/A')})")
        else:
            logger.info("No sessions available for upload")

        return session

    def upload_video(
        self,
        session: Dict[str, Any],
        privacy_status: str = 'public',
        dry_run: bool = False
    ) -> Optional[str]:
        """Upload video to YouTube.

        Args:
            session: Session dict from database
            privacy_status: public | private | unlisted
            dry_run: If True, don't actually upload

        Returns:
            YouTube video ID or None on failure
        """
        session_name = session['session_name']
        session_path = Path(session['session_path'])

        logger.info(f"Preparing to upload: {session_name}")

        # Load metadata
        metadata = self._load_metadata(session_path)
        if not metadata:
            logger.error("Failed to load metadata")
            return None

        # Find video file
        video_path = Path(session['video_path'])
        if not video_path.exists():
            # Try alternative paths
            video_path = session_path / 'output' / 'youtube_package' / 'final_video.mp4'
            if not video_path.exists():
                video_path = session_path / 'output' / 'video' / 'session_final.mp4'

        if not video_path.exists():
            logger.error(f"Video file not found: {video_path}")
            return None

        # Find thumbnail
        thumbnail_path = self._find_thumbnail(session_path)

        # Build description with website link
        description = self._build_description(metadata, session)

        # Get tags
        tags = metadata.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',')]

        logger.info(f"Title: {metadata.get('title', 'Untitled')[:60]}...")
        logger.info(f"Video: {video_path}")
        logger.info(f"Thumbnail: {thumbnail_path}")
        logger.info(f"Tags: {len(tags)} tags")
        logger.info(f"Privacy: {privacy_status}")

        if dry_run:
            logger.info("[DRY RUN] Would upload video")
            return "DRY_RUN_VIDEO_ID"

        try:
            video_id = self.youtube.upload_video(
                video_path=str(video_path),
                title=metadata.get('title', session_name)[:100],
                description=description,
                tags=tags,
                category_id=self.config['upload']['category_id'],
                privacy_status=privacy_status,
                made_for_kids=False,
                is_short=False,
                thumbnail_path=str(thumbnail_path) if thumbnail_path else None,
            )

            logger.info(f"Upload successful! Video ID: {video_id}")

            # Update database
            self.db.mark_youtube_uploaded(session_name, video_id)
            self.db.log_upload(
                session_name=session_name,
                upload_type='youtube_long',
                video_id=video_id,
                url=f'https://www.youtube.com/watch?v={video_id}',
                success=True,
            )

            return video_id

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            self.db.log_upload(
                session_name=session_name,
                upload_type='youtube_long',
                success=False,
                error_message=str(e),
            )
            return None

    def _load_metadata(self, session_path: Path) -> Optional[Dict]:
        """Load YouTube metadata from session.

        Args:
            session_path: Path to session directory

        Returns:
            Metadata dict or None
        """
        # Try youtube_package first
        metadata_path = session_path / 'output' / 'youtube_package' / 'metadata.yaml'
        if metadata_path.exists():
            try:
                with open(metadata_path) as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"Failed to load {metadata_path}: {e}")

        # Try manifest as fallback
        manifest_path = session_path / 'manifest.yaml'
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    manifest = yaml.safe_load(f)
                return {
                    'title': manifest.get('session', {}).get('title', session_path.name),
                    'description': manifest.get('session', {}).get('description', ''),
                    'tags': manifest.get('youtube', {}).get('tags', []),
                }
            except Exception as e:
                logger.warning(f"Failed to load {manifest_path}: {e}")

        return {'title': session_path.name, 'description': '', 'tags': []}

    def _find_thumbnail(self, session_path: Path) -> Optional[Path]:
        """Find thumbnail image for session.

        Args:
            session_path: Path to session directory

        Returns:
            Path to thumbnail or None
        """
        candidates = [
            session_path / 'output' / 'youtube_package' / 'thumbnail.png',
            session_path / 'output' / 'youtube_thumbnail.png',
            session_path / 'output' / 'thumbnail.png',
            session_path / 'images' / 'thumbnail.png',
        ]

        for path in candidates:
            if path.exists():
                return path

        return None

    def _build_description(self, metadata: Dict, session: Dict) -> str:
        """Build YouTube description with website link.

        Args:
            metadata: Loaded metadata
            session: Session database record

        Returns:
            Formatted description
        """
        description = metadata.get('description', '')

        # Get website URL
        website_url = session.get('website_url')
        if not website_url:
            website_url = f"https://www.salars.net/dreamweavings/{session['session_name']}"

        # Add footer with links
        footer = f"""

---
Experience the full journey with enhanced audio: {website_url}

Subscribe for more guided journeys and meditations.

#Dreamweaving #GuidedMeditation #Hypnosis #SpiritualJourney #Meditation #Relaxation
"""

        return (description + footer)[:5000]

    def run(
        self,
        session_name: Optional[str] = None,
        privacy_status: str = 'public',
        dry_run: bool = False
    ) -> Optional[str]:
        """Run upload workflow.

        Args:
            session_name: Specific session to upload (or auto-select)
            privacy_status: YouTube privacy status
            dry_run: If True, don't actually upload

        Returns:
            YouTube video ID or None
        """
        # Select session
        if session_name:
            session = self.db.get_session(session_name)
            if not session:
                logger.error(f"Session not found: {session_name}")
                return None
        else:
            session = self.select_next_upload()
            if not session:
                logger.info("No videos available for upload")
                return None

        # Check timing (if analytics available)
        if self.analytics and not dry_run:
            if not self.analytics.should_upload_now('long'):
                next_time = self.analytics.get_next_upload_time('long')
                logger.info(f"Not optimal upload time. Next window: {next_time}")
                # Continue anyway (manual trigger overrides)

        # Upload
        return self.upload_video(session, privacy_status, dry_run)

    def get_upload_queue(self, limit: int = 10) -> list:
        """Get list of sessions queued for upload.

        Args:
            limit: Maximum sessions to return

        Returns:
            List of session dicts
        """
        sessions = self.db.query(
            """
            SELECT session_name, topic, quality_score, created_at
            FROM sessions
            WHERE uploaded_to_youtube = 0
              AND generation_status = 'complete'
              AND video_path IS NOT NULL
            ORDER BY quality_score DESC, created_at ASC
            LIMIT ?
            """,
            (limit,)
        )
        return sessions


def main():
    """Main entry point."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from scripts.automation.config_loader import load_config, setup_logging
    from scripts.automation.state_db import StateDatabase
    from scripts.automation.youtube_client import YouTubeClient
    from scripts.automation.analytics_optimizer import AnalyticsOptimizer

    parser = argparse.ArgumentParser(description='Upload Scheduler')
    parser.add_argument('--session', type=str, help='Specific session to upload')
    parser.add_argument('--privacy', type=str, default='public',
                       choices=['public', 'private', 'unlisted'],
                       help='Privacy status')
    parser.add_argument('--dry-run', action='store_true', help='Dry run')
    parser.add_argument('--queue', action='store_true', help='Show upload queue')
    parser.add_argument('--config', type=str, help='Config file path')

    args = parser.parse_args()

    config = load_config(Path(args.config) if args.config else None)
    setup_logging(config)

    db = StateDatabase(Path(config['database']['path']))
    db.init_schema()

    youtube = YouTubeClient(Path(config['youtube']['credentials_dir']))
    analytics = AnalyticsOptimizer(youtube, db)

    scheduler = UploadScheduler(config, db, youtube, analytics)

    if args.queue:
        print("\n=== Upload Queue ===")
        queue = scheduler.get_upload_queue(limit=10)
        if not queue:
            print("Queue is empty")
        else:
            for i, session in enumerate(queue, 1):
                score = session.get('quality_score', 'N/A')
                topic = session.get('topic', '')[:40]
                print(f"{i}. {session['session_name']} (score: {score}) - {topic}...")
    else:
        video_id = scheduler.run(
            session_name=args.session,
            privacy_status=args.privacy,
            dry_run=args.dry_run,
        )

        if video_id:
            print(f"\nUpload complete!")
            print(f"Video ID: {video_id}")
            if video_id != "DRY_RUN_VIDEO_ID":
                print(f"URL: https://www.youtube.com/watch?v={video_id}")
        else:
            print("\nUpload failed or no videos available")

    db.close()


if __name__ == '__main__':
    main()
