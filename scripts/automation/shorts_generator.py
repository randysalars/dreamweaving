#!/usr/bin/env python3
"""
Shorts Generator

Creates and uploads 30-45 second YouTube Shorts from existing sessions.

Source content: Sessions uploaded to website but NOT to YouTube.
This drives traffic from shorts to the full experience on salars.net.

Usage:
    # Auto-select and generate/upload short
    python -m scripts.automation.shorts_generator

    # Generate from specific session
    python -m scripts.automation.shorts_generator --session my-session

    # Preview only (don't upload)
    python -m scripts.automation.shorts_generator --preview

    # Dry run
    python -m scripts.automation.shorts_generator --dry-run
"""

import argparse
import json
import logging
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Engagement keywords for finding best moments
HIGH_ENGAGEMENT_WORDS = [
    'see', 'feel', 'notice', 'imagine', 'visualize',
    'becoming', 'sacred', 'divine', 'light', 'energy',
    'transformation', 'healing', 'peace', 'love',
]
MEDIUM_ENGAGEMENT_WORDS = [
    'breathe', 'relax', 'deeper', 'awareness', 'presence',
    'calm', 'safe', 'comfortable', 'warm', 'floating',
]


class ShortsGenerator:
    """Generates and uploads YouTube Shorts."""

    def __init__(self, config: Dict[str, Any], db, youtube_client):
        """Initialize shorts generator.

        Args:
            config: Configuration dictionary
            db: StateDatabase instance
            youtube_client: YouTubeClient instance
        """
        self.config = config
        self.db = db
        self.youtube = youtube_client

        self.duration = config['shorts']['duration_seconds']
        self.cta_duration = config['shorts']['cta_duration_seconds']
        self.clip_duration = self.duration - self.cta_duration

    def select_source_session(self) -> Optional[Dict[str, Any]]:
        """Find session eligible for shorts creation.

        Criteria:
        - Uploaded to website (has content to link to)
        - NOT uploaded to YouTube (website-only content)
        - Shorts not yet created/uploaded
        - Has video file

        Returns:
            Session dict or None
        """
        logger.info("Selecting source session for shorts...")

        session = self.db.get_shorts_candidate()

        if session:
            logger.info(f"Selected: {session['session_name']}")
        else:
            logger.info("No sessions available for shorts")

        return session

    def generate_short(
        self,
        session: Dict[str, Any],
        output_dir: Optional[Path] = None
    ) -> Optional[Path]:
        """Generate a short video from session.

        Args:
            session: Session database record
            output_dir: Output directory (default: session output folder)

        Returns:
            Path to generated short or None on failure
        """
        session_name = session['session_name']
        session_path = Path(session['session_path'])
        video_path = Path(session['video_path'])

        if not video_path.exists():
            logger.error(f"Source video not found: {video_path}")
            return None

        if output_dir is None:
            output_dir = session_path / 'output'
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Generating short for: {session_name}")

        # Find best segment
        vtt_path = session_path / 'output' / 'youtube_package' / 'subtitles.vtt'
        best_segment = self._find_best_segment(vtt_path, video_path)
        logger.info(f"Best segment: {best_segment['start']:.1f}s - {best_segment['end']:.1f}s")

        # Create temp directory for intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Step 1: Extract clip
            clip_path = temp_path / 'clip.mp4'
            if not self._extract_clip(video_path, clip_path, best_segment['start'], self.clip_duration):
                return None

            # Step 2: Convert to vertical (9:16)
            vertical_path = temp_path / 'vertical.mp4'
            if not self._convert_to_vertical(clip_path, vertical_path):
                return None

            # Step 3: Add CTA overlay
            website_url = session.get('website_url') or f"salars.net/dreamweavings/{session_name}"
            final_path = temp_path / 'final_short.mp4'
            if not self._add_cta_overlay(vertical_path, final_path, website_url):
                return None

            # Move to output directory
            output_path = output_dir / 'short_video.mp4'
            shutil.move(str(final_path), str(output_path))

        logger.info(f"Short generated: {output_path}")

        # Update database
        self.db.mark_shorts_created(session_name, str(output_path))

        return output_path

    def _find_best_segment(
        self,
        vtt_path: Path,
        video_path: Path
    ) -> Dict[str, float]:
        """Find most engaging segment for shorts.

        Args:
            vtt_path: Path to VTT subtitles
            video_path: Path to source video

        Returns:
            Dict with start and end times
        """
        # Get video duration
        video_duration = self._get_video_duration(video_path)
        if not video_duration:
            video_duration = 1800  # Assume 30 min

        # Default: 2-3 minutes in (after pre-talk/induction starts)
        default_start = min(120, video_duration * 0.1)
        default_segment = {
            'start': default_start,
            'end': default_start + self.clip_duration,
        }

        if not vtt_path.exists():
            logger.warning("No VTT file, using default segment")
            return default_segment

        try:
            segments = self._parse_vtt(vtt_path)
            if not segments:
                return default_segment

            # Score each potential window
            best_score = 0
            best_start = default_start

            for i, segment in enumerate(segments):
                # Get text in this window
                window_end_time = segment['start_seconds'] + self.clip_duration
                window_segments = [
                    s for s in segments
                    if segment['start_seconds'] <= s['start_seconds'] < window_end_time
                ]
                window_text = ' '.join([s['text'] for s in window_segments])

                # Score based on engagement keywords
                score = 0
                for word in HIGH_ENGAGEMENT_WORDS:
                    if word in window_text.lower():
                        score += 2
                for word in MEDIUM_ENGAGEMENT_WORDS:
                    if word in window_text.lower():
                        score += 1

                # Bonus for being in journey section (after 3 min)
                if segment['start_seconds'] > 180:
                    score += 3

                # Penalty for being too early (pre-talk)
                if segment['start_seconds'] < 60:
                    score -= 5

                # Penalty for being at very end
                if segment['start_seconds'] > video_duration - 300:
                    score -= 3

                if score > best_score:
                    best_score = score
                    best_start = segment['start_seconds']

            return {
                'start': best_start,
                'end': best_start + self.clip_duration,
                'score': best_score,
            }

        except Exception as e:
            logger.warning(f"Failed to analyze VTT: {e}")
            return default_segment

    def _parse_vtt(self, vtt_path: Path) -> List[Dict]:
        """Parse VTT subtitles file.

        Args:
            vtt_path: Path to VTT file

        Returns:
            List of segment dicts with start_seconds and text
        """
        content = vtt_path.read_text(encoding='utf-8')
        segments = []

        # VTT timestamp pattern: 00:01:23.456 --> 00:01:27.890
        pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})\s*\n(.+?)(?=\n\n|\Z)'

        for match in re.finditer(pattern, content, re.DOTALL):
            start_time = match.group(1)
            text = match.group(3).strip()

            # Convert timestamp to seconds
            parts = start_time.split(':')
            seconds = (
                int(parts[0]) * 3600 +
                int(parts[1]) * 60 +
                float(parts[2])
            )

            segments.append({
                'start_seconds': seconds,
                'text': text,
            })

        return segments

    def _extract_clip(
        self,
        input_path: Path,
        output_path: Path,
        start_time: float,
        duration: float
    ) -> bool:
        """Extract clip from video.

        Args:
            input_path: Source video path
            output_path: Output clip path
            start_time: Start time in seconds
            duration: Duration in seconds

        Returns:
            True on success
        """
        try:
            subprocess.run([
                'ffmpeg', '-y',
                '-ss', str(start_time),
                '-i', str(input_path),
                '-t', str(duration),
                '-c:v', 'libx264', '-preset', 'medium',
                '-c:a', 'aac', '-b:a', '192k',
                str(output_path)
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract clip: {e.stderr.decode()}")
            return False

    def _convert_to_vertical(self, input_path: Path, output_path: Path) -> bool:
        """Convert 16:9 video to 9:16 with blur background.

        Args:
            input_path: Source video path
            output_path: Output vertical video path

        Returns:
            True on success
        """
        try:
            # Complex filter to create blur background and overlay original
            filter_complex = (
                # Split input into two streams
                "split[original][copy];"
                # Scale copy to fill 9:16, crop, and blur
                "[copy]scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920,boxblur=25:5[blurred];"
                # Scale original to fit width while maintaining aspect
                "[original]scale=1080:-1[scaled];"
                # Overlay scaled on blurred background, centered vertically
                "[blurred][scaled]overlay=(W-w)/2:(H-h)/2"
            )

            subprocess.run([
                'ffmpeg', '-y',
                '-i', str(input_path),
                '-vf', filter_complex,
                '-c:v', 'libx264', '-preset', 'medium',
                '-c:a', 'aac', '-b:a', '192k',
                str(output_path)
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to convert to vertical: {e.stderr.decode()}")
            return False

    def _add_cta_overlay(
        self,
        input_path: Path,
        output_path: Path,
        website_url: str
    ) -> bool:
        """Add CTA text overlay in last seconds.

        Args:
            input_path: Input video path
            output_path: Output video path
            website_url: Website URL to display

        Returns:
            True on success
        """
        try:
            duration = self._get_video_duration(input_path)
            if not duration:
                duration = self.clip_duration

            cta_start = max(0, duration - self.cta_duration)

            # Clean URL for display (remove https://)
            display_url = website_url.replace('https://', '').replace('http://', '')

            # FFmpeg drawtext filter
            filter_text = (
                f"drawtext=text='Full Journey':"
                f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"fontsize=48:fontcolor=white:borderw=3:bordercolor=black:"
                f"x=(w-text_w)/2:y=h*0.70:"
                f"enable='gte(t,{cta_start})',"

                f"drawtext=text='{display_url}':"
                f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"fontsize=36:fontcolor=yellow:borderw=2:bordercolor=black:"
                f"x=(w-text_w)/2:y=h*0.78:"
                f"enable='gte(t,{cta_start})'"
            )

            subprocess.run([
                'ffmpeg', '-y',
                '-i', str(input_path),
                '-vf', filter_text,
                '-c:a', 'copy',
                str(output_path)
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add CTA overlay: {e.stderr.decode()}")
            return False

    def _get_video_duration(self, video_path: Path) -> Optional[float]:
        """Get video duration in seconds.

        Args:
            video_path: Path to video

        Returns:
            Duration in seconds or None
        """
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                str(video_path)
            ], capture_output=True, text=True)
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except Exception:
            return None

    def upload_short(
        self,
        session: Dict[str, Any],
        shorts_path: Path,
        privacy_status: str = 'public',
        dry_run: bool = False
    ) -> Optional[str]:
        """Upload short to YouTube.

        Args:
            session: Session database record
            shorts_path: Path to short video
            privacy_status: YouTube privacy status
            dry_run: If True, don't actually upload

        Returns:
            YouTube video ID or None
        """
        session_name = session['session_name']
        topic = session.get('topic', session_name)

        # Build title and description
        title = f"{topic[:50]} | Guided Journey #Shorts"

        website_url = session.get('website_url') or f"https://www.salars.net/dreamweavings/{session_name}"
        description = f"""Experience the full {topic} journey:
{website_url}

#Shorts #GuidedMeditation #Dreamweaving #SpiritualJourney #Hypnosis #Meditation #Relaxation
"""

        tags = [
            'Shorts', 'YouTubeShorts',
            'GuidedMeditation', 'Meditation',
            'Dreamweaving', 'Hypnosis',
            'SpiritualJourney', 'Relaxation',
        ]

        logger.info(f"Uploading short: {title}")
        logger.info(f"Video: {shorts_path}")

        if dry_run:
            logger.info("[DRY RUN] Would upload short")
            return "DRY_RUN_SHORT_ID"

        try:
            video_id = self.youtube.upload_video(
                video_path=str(shorts_path),
                title=title,
                description=description,
                tags=tags,
                category_id=self.config['upload']['category_id'],
                privacy_status=privacy_status,
                made_for_kids=False,
                is_short=True,
            )

            logger.info(f"Short uploaded! Video ID: {video_id}")

            # Update database
            self.db.mark_shorts_uploaded(session_name, video_id)
            self.db.log_upload(
                session_name=session_name,
                upload_type='youtube_short',
                video_id=video_id,
                url=f'https://www.youtube.com/shorts/{video_id}',
                success=True,
            )

            return video_id

        except Exception as e:
            logger.error(f"Short upload failed: {e}")
            self.db.log_upload(
                session_name=session_name,
                upload_type='youtube_short',
                success=False,
                error_message=str(e),
            )
            return None

    def run(
        self,
        session_name: Optional[str] = None,
        privacy_status: str = 'public',
        preview: bool = False,
        dry_run: bool = False
    ) -> Optional[str]:
        """Run shorts generation and upload workflow.

        Args:
            session_name: Specific session (or auto-select)
            privacy_status: YouTube privacy status
            preview: Generate only, don't upload
            dry_run: Don't generate or upload

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
            session = self.select_source_session()
            if not session:
                logger.info("No sessions available for shorts")
                return None

        # Check if short already exists
        if session.get('shorts_path') and Path(session['shorts_path']).exists():
            shorts_path = Path(session['shorts_path'])
            logger.info(f"Using existing short: {shorts_path}")
        else:
            if dry_run:
                logger.info("[DRY RUN] Would generate short")
                return None

            # Generate short
            shorts_path = self.generate_short(session)
            if not shorts_path:
                logger.error("Failed to generate short")
                return None

        if preview:
            logger.info(f"Preview mode - short at: {shorts_path}")
            return None

        # Upload
        return self.upload_short(session, shorts_path, privacy_status, dry_run)


def main():
    """Main entry point."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from scripts.automation.config_loader import load_config, setup_logging
    from scripts.automation.state_db import StateDatabase
    from scripts.automation.youtube_client import YouTubeClient

    parser = argparse.ArgumentParser(description='Shorts Generator')
    parser.add_argument('--session', type=str, help='Specific session to use')
    parser.add_argument('--privacy', type=str, default='public',
                       choices=['public', 'private', 'unlisted'],
                       help='Privacy status')
    parser.add_argument('--preview', action='store_true',
                       help='Generate only, do not upload')
    parser.add_argument('--dry-run', action='store_true', help='Dry run')
    parser.add_argument('--config', type=str, help='Config file path')

    args = parser.parse_args()

    config = load_config(Path(args.config) if args.config else None)
    setup_logging(config)

    db = StateDatabase(Path(config['database']['path']))
    db.init_schema()

    youtube = YouTubeClient(Path(config['youtube']['credentials_dir']))

    generator = ShortsGenerator(config, db, youtube)

    video_id = generator.run(
        session_name=args.session,
        privacy_status=args.privacy,
        preview=args.preview,
        dry_run=args.dry_run,
    )

    if video_id:
        print(f"\nShort uploaded!")
        print(f"Video ID: {video_id}")
        if video_id != "DRY_RUN_SHORT_ID":
            print(f"URL: https://www.youtube.com/shorts/{video_id}")
    elif args.preview:
        print("\nPreview complete - short generated but not uploaded")
    else:
        print("\nNo short generated/uploaded")

    db.close()


if __name__ == '__main__':
    main()
