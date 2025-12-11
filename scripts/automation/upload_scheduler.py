#!/usr/bin/env python3
"""
Upload Scheduler

Selects and uploads videos to YouTube based on quality scores and analytics.

Features:
- SEO-optimized title and description generation
- Automatic playlist assignment (Dreamweaving playlist)
- Optimized tag selection (under 500 chars)
- Proper YouTube metadata formatting

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
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from scripts.automation.playlist_classifier import PlaylistClassifier

logger = logging.getLogger(__name__)

# Legacy: Dreamweaving master playlist ID (now managed via PlaylistClassifier)
DREAMWEAVING_PLAYLIST_ID = "PLUza-jvPB6FycwFSty1CWCiqTCxSbj90l"

# Optimized tag set for Dreamweaving content (curated for SEO, under 500 chars total)
# Format: priority tags first, niche tags later
DREAMWEAVING_BASE_TAGS = [
    # Primary high-volume tags
    "guided meditation",
    "sleep hypnosis",
    "deep sleep",
    "meditation for sleep",
    "relaxation",
    # Secondary targeting tags
    "hypnosis",
    "guided hypnosis",
    "meditation music",
    "sleep meditation",
    "calming music",
    # Niche differentiators
    "dreamweaving",
    "spiritual journey",
    "inner peace",
    "theta waves",
    "binaural beats",
    # Long-tail tags
    "guided visualization",
    "hypnotherapy",
    "deep relaxation",
]

# Theme-specific tag mappings
THEME_TAGS = {
    "spiritual": ["spiritual awakening", "mystical journey", "soul healing", "divine connection"],
    "nature": ["nature sounds", "forest meditation", "garden meditation", "peaceful nature"],
    "cosmic": ["astral projection", "cosmic journey", "starlight meditation", "universe meditation"],
    "healing": ["healing meditation", "emotional healing", "inner healing", "self healing"],
    "sleep": ["fall asleep fast", "insomnia relief", "bedtime meditation", "sleep music"],
    "confidence": ["confidence boost", "self confidence", "inner strength", "empowerment"],
    "anxiety": ["anxiety relief", "stress relief", "calming meditation", "peace of mind"],
    "adventure": ["guided adventure", "inner journey", "exploration meditation", "discovery"],
}


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
        self.playlist_classifier = PlaylistClassifier()

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
        """Upload video to YouTube with optimized metadata.

        Features:
        - SEO-optimized title and description
        - Automatic playlist assignment
        - Optimized tag selection
        - Thumbnail upload

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

        # Load and enhance metadata
        metadata = self._load_metadata(session_path)
        if not metadata:
            logger.error("Failed to load metadata")
            return None

        # Generate optimized title if needed
        title = self._generate_optimized_title(metadata, session_name, session_path)

        # Find video file
        video_path = Path(session['video_path']) if session.get('video_path') else None
        if not video_path or not video_path.exists():
            # Try alternative paths
            video_path = session_path / 'output' / 'youtube_package' / 'final_video.mp4'
            if not video_path.exists():
                video_path = session_path / 'output' / 'video' / 'session_final.mp4'

        if not video_path.exists():
            logger.error(f"Video file not found: {video_path}")
            return None

        # Find thumbnail
        thumbnail_path = self._find_thumbnail(session_path)

        # Build SEO-optimized description
        description = self._build_description(metadata, session, session_path)

        # Generate optimized tags (under 500 chars)
        tags = self._generate_optimized_tags(metadata, session_name)

        # Calculate tag character count
        tag_chars = sum(len(t) for t in tags) + len(tags) - 1  # tags + commas

        logger.info(f"Title: {title[:60]}...")
        logger.info(f"Video: {video_path}")
        logger.info(f"Thumbnail: {thumbnail_path}")
        logger.info(f"Tags: {len(tags)} tags ({tag_chars} chars)")
        logger.info(f"Privacy: {privacy_status}")

        if dry_run:
            logger.info("[DRY RUN] Would upload video")
            logger.info(f"[DRY RUN] Would add to playlist: {DREAMWEAVING_PLAYLIST_ID}")
            return "DRY_RUN_VIDEO_ID"

        try:
            video_id = self.youtube.upload_video(
                video_path=str(video_path),
                title=title[:100],
                description=description,
                tags=tags,
                category_id=self.config['upload']['category_id'],
                privacy_status=privacy_status,
                made_for_kids=False,
                is_short=False,
                thumbnail_path=str(thumbnail_path) if thumbnail_path else None,
                # Always declare altered/synthetic content for Dreamweaving
                # Sessions use AI-generated voice (TTS) and AI-generated images
                contains_synthetic_media=True,
            )

            logger.info(f"Upload successful! Video ID: {video_id}")

            # Classify and add to playlists
            try:
                # Build session data for classification
                session_data = self._build_classification_data(session, session_path, metadata)
                classification = self.playlist_classifier.get_playlists_for_session(session_data)

                logger.info(
                    f"Playlist classification: {classification['primary']} "
                    f"(confidence: {classification['confidence']:.2f}, "
                    f"matches: {classification['match_count']})"
                )

                # Add to all matched playlists
                added_count = 0
                failed_count = 0
                for playlist_id in classification['playlists']:
                    if playlist_id:
                        try:
                            if self.youtube.add_to_playlist(video_id, playlist_id):
                                added_count += 1
                                logger.debug(f"Added to playlist: {playlist_id}")
                            else:
                                failed_count += 1
                                logger.warning(f"Failed to add to playlist: {playlist_id}")
                        except Exception as e:
                            failed_count += 1
                            logger.warning(f"Playlist {playlist_id} failed: {e}")

                logger.info(f"Added to {added_count} playlist(s)")
                if failed_count > 0:
                    logger.warning(f"Failed to add to {failed_count} playlist(s)")

                if classification['needs_review']:
                    logger.warning(
                        f"Low confidence classification ({classification['confidence']:.2f}) - "
                        "manual review recommended"
                    )

                # Log classification details for debugging
                if classification.get('details'):
                    logger.debug("Classification details:")
                    for detail in classification['details'][:3]:
                        logger.debug(f"  - {detail['name']}: {detail['confidence']:.3f} ({detail['type']})")

            except Exception as e:
                logger.warning(f"Playlist classification failed, using fallback: {e}")
                # Fallback to legacy single playlist
                try:
                    if self.youtube.add_to_playlist(video_id, DREAMWEAVING_PLAYLIST_ID):
                        logger.info("Added to Dreamweaving playlist (fallback)")
                except Exception as fallback_e:
                    logger.warning(f"Fallback playlist assignment also failed: {fallback_e}")

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

    def _generate_optimized_title(
        self,
        metadata: Dict,
        session_name: str,
        session_path: Path
    ) -> str:
        """Generate SEO-optimized YouTube title.

        Format patterns that work well:
        - "POWERFUL [Benefit] Meditation | [Theme] Guided Journey"
        - "[Theme] Hypnosis For [Benefit] | Deep Sleep Meditation"
        - "30-Minute [Theme] Journey | [Outcome] Meditation"

        Args:
            metadata: Loaded metadata
            session_name: Session identifier
            session_path: Path to session

        Returns:
            Optimized title (max 100 chars)
        """
        # First try explicit title from metadata
        if metadata.get('title') and len(metadata['title']) > 20:
            title = metadata['title']
            # Ensure it's not just the session name
            if title.lower() != session_name.lower().replace('-', ' '):
                return title[:100]

        # Load manifest for more context
        manifest_path = session_path / 'manifest.yaml'
        manifest = {}
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    manifest = yaml.safe_load(f) or {}
            except Exception:
                pass

        # Extract topic and outcome
        session_info = manifest.get('session', {})
        voice_info = manifest.get('voice', {})

        # Try to get a good topic from multiple sources
        topic = session_info.get('topic', session_name.replace('-', ' ').title())

        # If topic is too short/generic, try voice description
        if len(topic) < 10 or topic.lower() == session_name.lower().replace('-', ' '):
            voice_desc = voice_info.get('description', '')
            if voice_desc and len(voice_desc) > len(topic):
                topic = voice_desc

        # Also check session title if available
        session_title = session_info.get('title', '')
        if session_title and len(session_title) > len(topic):
            topic = session_title

        outcome = session_info.get('desired_outcome', session_info.get('style', 'relaxation'))
        duration = session_info.get('duration_minutes', 25)
        # Convert duration from seconds if needed
        if isinstance(duration, int) and duration > 100:
            duration = duration // 60

        # Clean up topic
        topic = topic.replace('_', ' ').strip()

        # Generate title based on outcome type
        outcome_lower = outcome.lower() if outcome else 'relaxation'

        if 'sleep' in outcome_lower or 'sleep' in topic.lower():
            title = f"Deep Sleep Hypnosis | {topic} | Fall Asleep Fast"
        elif 'confidence' in outcome_lower:
            title = f"POWERFUL Confidence Meditation | {topic} | Build Inner Strength"
        elif 'healing' in outcome_lower:
            title = f"Healing Meditation | {topic} | Guided Journey for Inner Peace"
        elif 'spiritual' in outcome_lower or 'spiritual' in topic.lower():
            title = f"Spiritual Journey | {topic} | {duration}-Minute Deep Meditation"
        elif 'transform' in outcome_lower:
            title = f"Transformative Hypnosis | {topic} | Deep Inner Journey"
        else:
            # Default format
            title = f"{topic} | Guided Meditation & Hypnosis | Deep Relaxation"

        # Ensure proper capitalization
        # Don't lowercase small words after pipe separators
        small_words = {'for', 'and', 'the', 'a', 'an', 'in', 'on', 'of', 'to', 'with'}
        words = title.split()
        after_separator = True  # Start of title is like after separator
        for i, word in enumerate(words):
            if word == '|':
                after_separator = True
                continue
            if after_separator or word.lower() not in small_words:
                if not word.isupper():  # Preserve intentional ALL CAPS
                    words[i] = word.capitalize()
                after_separator = False
            else:
                words[i] = word.lower()
        title = ' '.join(words)

        return title[:100]

    def _generate_optimized_tags(
        self,
        metadata: Dict,
        session_name: str
    ) -> List[str]:
        """Generate optimized tag list under 500 characters.

        Strategy:
        - Start with high-volume base tags
        - Add theme-specific tags
        - Add session-specific keywords
        - Trim to stay under 495 chars (buffer for safety)

        Args:
            metadata: Loaded metadata
            session_name: Session identifier

        Returns:
            List of optimized tags
        """
        MAX_CHARS = 495  # Leave 5 char buffer from 500 limit

        tags = []

        # Start with base dreamweaving tags
        tags.extend(DREAMWEAVING_BASE_TAGS)

        # Detect theme from session name and metadata
        session_lower = session_name.lower()
        title_lower = metadata.get('title', '').lower()
        combined = f"{session_lower} {title_lower}"

        # Add theme-specific tags
        for theme, theme_tags in THEME_TAGS.items():
            if theme in combined:
                tags.extend(theme_tags)
                break  # Only add one theme's tags

        # Add any existing tags from metadata (but validate them)
        existing_tags = metadata.get('tags', [])
        if isinstance(existing_tags, str):
            existing_tags = [t.strip() for t in existing_tags.split(',')]

        for tag in existing_tags:
            tag = tag.strip().lower()
            if tag and tag not in [t.lower() for t in tags] and len(tag) < 50:
                tags.append(tag)

        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower not in seen:
                seen.add(tag_lower)
                unique_tags.append(tag)

        # Trim to fit under MAX_CHARS
        final_tags = []
        char_count = 0
        for tag in unique_tags:
            # +1 for comma separator (except first)
            separator = 1 if final_tags else 0
            if char_count + len(tag) + separator <= MAX_CHARS:
                final_tags.append(tag)
                char_count += len(tag) + separator
            else:
                break

        logger.debug(f"Generated {len(final_tags)} tags ({char_count} chars)")
        return final_tags

    def _build_classification_data(
        self,
        session: Dict[str, Any],
        session_path: Path,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build session data dict for playlist classification.

        Args:
            session: Session dict from database
            session_path: Path to session directory
            metadata: Loaded metadata dict

        Returns:
            Session data dict for PlaylistClassifier
        """
        # Load manifest for full context
        manifest = {}
        manifest_path = session_path / 'manifest.yaml'
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    manifest = yaml.safe_load(f) or {}
            except Exception as e:
                logger.debug(f"Could not load manifest: {e}")

        session_info = manifest.get('session', {})
        youtube_info = manifest.get('youtube', {})

        # Get duration, handling seconds vs minutes
        duration = session_info.get('duration', manifest.get('duration', 25))
        if isinstance(duration, (int, float)) and duration > 100:
            duration = int(duration) // 60

        return {
            'title': (
                metadata.get('title') or
                youtube_info.get('optimized_title') or
                youtube_info.get('title') or
                session_info.get('topic') or
                session['session_name']
            ),
            'description': (
                metadata.get('description') or
                session_info.get('description') or
                manifest.get('description', '')
            ),
            'tags': metadata.get('tags', youtube_info.get('tags', [])),
            'duration_minutes': duration,
            'archetypes': manifest.get('archetypes', []),
            'manifest': manifest
        }

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
        # Priority: youtube_thumbnail.png (with text overlay) > youtube_package > others
        candidates = [
            session_path / 'output' / 'youtube_thumbnail.png',  # Canonical - with text
            session_path / 'output' / 'youtube_package' / 'thumbnail.png',
            session_path / 'output' / 'thumbnail.png',
            session_path / 'images' / 'thumbnail.png',
        ]

        for path in candidates:
            if path.exists():
                return path

        return None

    def _build_description(
        self,
        metadata: Dict,
        session: Dict,
        session_path: Optional[Path] = None
    ) -> str:
        """Build SEO-optimized YouTube description.

        Includes:
        - Main description from metadata/manifest
        - Benefits and what to expect
        - Website link for full experience
        - Subscribe CTA
        - Relevant hashtags

        Args:
            metadata: Loaded metadata
            session: Session database record
            session_path: Optional path for loading additional context

        Returns:
            Formatted description (max 5000 chars)
        """
        session_name = session['session_name']

        # Get base description
        description = metadata.get('description', '')

        # If no description, generate from manifest
        if not description and session_path:
            manifest_path = session_path / 'manifest.yaml'
            if manifest_path.exists():
                try:
                    with open(manifest_path) as f:
                        manifest = yaml.safe_load(f) or {}
                    session_info = manifest.get('session', {})
                    topic = session_info.get('topic', session_name.replace('-', ' '))
                    outcome = session_info.get('desired_outcome', 'deep relaxation')
                    duration = session_info.get('duration_minutes', 25)

                    description = f"""Experience a {duration}-minute guided journey into {topic}.

This session uses hypnotic techniques, theta wave binaural beats, and immersive soundscapes to help you achieve {outcome}.

🎧 Best experienced with headphones in a quiet, comfortable space.

What you'll experience:
• Progressive relaxation and deep breathing
• Guided visualization journey
• Theta wave binaural beats (4-7 Hz)
• Return to wakefulness feeling refreshed

⚠️ Do not listen while driving or operating machinery."""
                except Exception:
                    pass

        # Ensure we have at least a basic description
        if not description:
            description = """A guided meditation and hypnosis journey designed for deep relaxation.

🎧 Best experienced with headphones in a quiet, comfortable space.

This session features:
• Professional voice guidance
• Theta wave binaural beats
• Immersive ambient soundscapes
• Gentle return to full awareness

⚠️ Do not listen while driving or operating machinery."""

        # Get website URL
        website_url = session.get('website_url')
        if not website_url:
            website_url = f"https://www.salars.net/dreamweavings/{session_name}"

        # Build footer with links and CTAs
        footer = f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌙 Full Experience with Enhanced Audio:
{website_url}

📺 Subscribe for new guided journeys weekly:
https://www.youtube.com/@RandySalars?sub_confirmation=1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#GuidedMeditation #SleepHypnosis #DeepSleep #Meditation #Relaxation #Hypnosis #BinauralBeats #ThetaWaves #SpiritualJourney #InnerPeace #Dreamweaving
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
