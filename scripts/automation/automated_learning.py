#!/usr/bin/env python3
"""
Automated Learning Pipeline

Automatically collects feedback and updates the knowledge base:
1. Fetches YouTube analytics for uploaded videos (48hrs+ old)
2. Extracts performance insights and patterns
3. Updates lessons_learned.yaml with actionable findings
4. Correlates session attributes with performance

Designed to run:
- Daily: Quick analytics fetch for recent uploads
- Weekly: Deep analysis and lesson extraction

Usage:
    # Daily quick check (fetch analytics for videos 48hrs+ old)
    python -m scripts.automation.automated_learning --daily

    # Weekly deep analysis (extract patterns, update lessons)
    python -m scripts.automation.automated_learning --weekly

    # Process specific video
    python -m scripts.automation.automated_learning --video-id VIDEO_ID

    # Dry run (don't update knowledge base)
    python -m scripts.automation.automated_learning --weekly --dry-run
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.automation.state_db import StateDatabase
from scripts.automation.youtube_client import YouTubeClient

logger = logging.getLogger(__name__)

# Minimum age before fetching analytics (hours)
MIN_VIDEO_AGE_HOURS = 48

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    'excellent': {
        'views_per_day': 100,
        'avg_view_duration_percent': 60,
        'like_ratio': 0.05,  # 5% of views
        'comment_ratio': 0.01,  # 1% of views
    },
    'good': {
        'views_per_day': 50,
        'avg_view_duration_percent': 45,
        'like_ratio': 0.03,
        'comment_ratio': 0.005,
    },
    'average': {
        'views_per_day': 20,
        'avg_view_duration_percent': 30,
        'like_ratio': 0.02,
        'comment_ratio': 0.002,
    },
}


class AutomatedLearning:
    """Automated feedback collection and learning system."""

    def __init__(self, dry_run: bool = False):
        """Initialize the learning system.

        Args:
            dry_run: If True, don't update knowledge base
        """
        self.dry_run = dry_run
        self.db = StateDatabase()
        self.youtube = None
        self.knowledge_path = PROJECT_ROOT / 'knowledge'
        self.lessons_path = self.knowledge_path / 'lessons_learned.yaml'

        # Try to initialize YouTube client
        try:
            self.youtube = YouTubeClient()
        except Exception as e:
            logger.warning(f"YouTube client not available: {e}")

    def run_daily(self) -> Dict[str, Any]:
        """Run daily analytics collection.

        Fetches analytics for videos uploaded 48+ hours ago that
        don't have recent analytics data.

        Returns:
            Summary of collected data
        """
        logger.info("=== Running Daily Analytics Collection ===")

        if not self.youtube:
            logger.error("YouTube client not initialized")
            return {'error': 'YouTube client not available'}

        # Get uploaded videos that need analytics
        videos_to_check = self._get_videos_needing_analytics()
        logger.info(f"Found {len(videos_to_check)} videos to check")

        results = {
            'checked': 0,
            'updated': 0,
            'errors': 0,
            'videos': [],
        }

        for video in videos_to_check:
            try:
                analytics = self._fetch_video_analytics(video['youtube_video_id'])
                if analytics:
                    self._store_analytics(video['session_name'], video['youtube_video_id'], analytics)
                    results['updated'] += 1
                    results['videos'].append({
                        'session': video['session_name'],
                        'video_id': video['youtube_video_id'],
                        'views': analytics.get('views', 0),
                        'avg_duration': analytics.get('avg_view_duration_percent', 0),
                    })
                results['checked'] += 1
            except Exception as e:
                logger.error(f"Error fetching analytics for {video['session_name']}: {e}")
                results['errors'] += 1

        logger.info(f"Daily collection complete: {results['updated']} videos updated")
        return results

    def run_weekly(self) -> Dict[str, Any]:
        """Run weekly deep analysis and lesson extraction.

        Analyzes all video performance data and:
        1. Identifies top/bottom performing videos
        2. Correlates session attributes with performance
        3. Extracts actionable patterns
        4. Updates lessons_learned.yaml

        Returns:
            Summary of insights extracted
        """
        logger.info("=== Running Weekly Deep Analysis ===")

        # First, run daily collection to ensure data is fresh
        daily_results = self.run_daily()

        # Get all videos with analytics
        videos_with_data = self._get_videos_with_analytics()
        logger.info(f"Analyzing {len(videos_with_data)} videos with analytics data")

        if len(videos_with_data) < 3:
            logger.warning("Not enough data for meaningful analysis (need 3+ videos)")
            return {'warning': 'Insufficient data', 'daily': daily_results}

        # Analyze performance patterns
        insights = self._analyze_performance_patterns(videos_with_data)

        # Extract lessons
        lessons = self._extract_lessons(insights)

        # Update knowledge base
        if not self.dry_run and lessons:
            self._update_lessons_learned(lessons)
            logger.info(f"Updated lessons_learned.yaml with {len(lessons)} new insights")
        elif self.dry_run:
            logger.info(f"[DRY RUN] Would add {len(lessons)} lessons")

        return {
            'daily': daily_results,
            'videos_analyzed': len(videos_with_data),
            'insights': insights,
            'lessons_added': len(lessons),
            'lessons': lessons if self.dry_run else None,
        }

    def _get_videos_needing_analytics(self) -> List[Dict]:
        """Get uploaded videos that need analytics fetched."""
        cursor = self.db.conn.cursor()

        # Get videos uploaded 48+ hours ago without recent analytics
        min_age = datetime.now() - timedelta(hours=MIN_VIDEO_AGE_HOURS)

        cursor.execute("""
            SELECT session_name, youtube_video_id, youtube_uploaded_at, topic
            FROM sessions
            WHERE uploaded_to_youtube = 1
            AND youtube_video_id IS NOT NULL
            AND youtube_uploaded_at < ?
            AND (
                analytics_fetched_at IS NULL
                OR analytics_fetched_at < datetime('now', '-1 day')
            )
            ORDER BY youtube_uploaded_at DESC
            LIMIT 20
        """, (min_age.isoformat(),))

        return [dict(row) for row in cursor.fetchall()]

    def _get_videos_with_analytics(self) -> List[Dict]:
        """Get all videos that have analytics data."""
        cursor = self.db.conn.cursor()

        cursor.execute("""
            SELECT
                s.session_name,
                s.youtube_video_id,
                s.topic,
                s.youtube_uploaded_at,
                s.quality_score,
                s.video_duration_seconds,
                va.views,
                va.likes,
                va.comments,
                va.avg_view_duration_seconds,
                va.avg_view_duration_percent,
                va.fetched_at
            FROM sessions s
            JOIN video_analytics va ON s.youtube_video_id = va.video_id
            WHERE s.uploaded_to_youtube = 1
            ORDER BY va.fetched_at DESC
        """)

        return [dict(row) for row in cursor.fetchall()]

    def _fetch_video_analytics(self, video_id: str) -> Optional[Dict]:
        """Fetch analytics for a specific video."""
        try:
            # Get basic video stats
            video_info = self.youtube.get_video_info(video_id)
            if not video_info:
                return None

            stats = video_info.get('statistics', {})
            content_details = video_info.get('contentDetails', {})

            # Parse duration
            duration_str = content_details.get('duration', 'PT0S')
            duration_seconds = self._parse_duration(duration_str)

            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))

            # Try to get watch time analytics (requires YouTube Analytics API)
            avg_view_duration = None
            avg_view_percent = None
            try:
                analytics = self.youtube.get_video_analytics(video_id, days=7)
                if analytics and 'averageViewDuration' in analytics:
                    avg_view_duration = analytics['averageViewDuration']
                    if duration_seconds > 0:
                        avg_view_percent = (avg_view_duration / duration_seconds) * 100
            except Exception as e:
                logger.debug(f"Could not fetch detailed analytics: {e}")

            return {
                'views': views,
                'likes': likes,
                'comments': comments,
                'duration_seconds': duration_seconds,
                'avg_view_duration_seconds': avg_view_duration,
                'avg_view_duration_percent': avg_view_percent,
                'like_ratio': (likes / views * 100) if views > 0 else 0,
                'comment_ratio': (comments / views * 100) if views > 0 else 0,
            }

        except Exception as e:
            logger.error(f"Error fetching analytics for {video_id}: {e}")
            return None

    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
        if not match:
            return 0
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds

    def _store_analytics(self, session_name: str, video_id: str, analytics: Dict):
        """Store analytics data in database."""
        cursor = self.db.conn.cursor()

        # Ensure video_analytics table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                session_name TEXT NOT NULL,
                views INTEGER,
                likes INTEGER,
                comments INTEGER,
                avg_view_duration_seconds REAL,
                avg_view_duration_percent REAL,
                like_ratio REAL,
                comment_ratio REAL,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(video_id, date(fetched_at))
            )
        """)

        # Insert analytics record
        cursor.execute("""
            INSERT OR REPLACE INTO video_analytics
            (video_id, session_name, views, likes, comments,
             avg_view_duration_seconds, avg_view_duration_percent,
             like_ratio, comment_ratio, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            video_id,
            session_name,
            analytics.get('views'),
            analytics.get('likes'),
            analytics.get('comments'),
            analytics.get('avg_view_duration_seconds'),
            analytics.get('avg_view_duration_percent'),
            analytics.get('like_ratio'),
            analytics.get('comment_ratio'),
            datetime.now().isoformat(),
        ))

        # Update session record
        cursor.execute("""
            UPDATE sessions
            SET analytics_fetched_at = ?
            WHERE session_name = ?
        """, (datetime.now().isoformat(), session_name))

        self.db.conn.commit()

    def _analyze_performance_patterns(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze performance patterns across videos."""
        if not videos:
            return {}

        # Calculate performance scores
        for video in videos:
            video['performance_score'] = self._calculate_performance_score(video)

        # Sort by performance
        videos_sorted = sorted(videos, key=lambda x: x['performance_score'], reverse=True)

        # Identify top and bottom performers
        top_count = max(1, len(videos) // 4)  # Top 25%
        bottom_count = max(1, len(videos) // 4)  # Bottom 25%

        top_performers = videos_sorted[:top_count]
        bottom_performers = videos_sorted[-bottom_count:]

        # Analyze what makes top performers different
        insights = {
            'total_videos': len(videos),
            'avg_views': sum(v.get('views', 0) for v in videos) / len(videos),
            'avg_retention': sum(v.get('avg_view_duration_percent', 0) or 0 for v in videos) / len(videos),
            'top_performers': [{
                'session': v['session_name'],
                'topic': v.get('topic', ''),
                'views': v.get('views', 0),
                'retention': v.get('avg_view_duration_percent'),
                'score': v['performance_score'],
            } for v in top_performers],
            'bottom_performers': [{
                'session': v['session_name'],
                'topic': v.get('topic', ''),
                'views': v.get('views', 0),
                'retention': v.get('avg_view_duration_percent'),
                'score': v['performance_score'],
            } for v in bottom_performers],
            'patterns': self._find_patterns(top_performers, bottom_performers),
        }

        return insights

    def _calculate_performance_score(self, video: Dict) -> float:
        """Calculate a normalized performance score (0-100)."""
        score = 0

        # Views component (0-40 points)
        views = video.get('views', 0)
        if views >= 1000:
            score += 40
        elif views >= 500:
            score += 30
        elif views >= 100:
            score += 20
        elif views >= 50:
            score += 10

        # Retention component (0-40 points)
        retention = video.get('avg_view_duration_percent') or 0
        if retention >= 60:
            score += 40
        elif retention >= 45:
            score += 30
        elif retention >= 30:
            score += 20
        elif retention >= 20:
            score += 10

        # Engagement component (0-20 points)
        like_ratio = video.get('like_ratio', 0)
        if like_ratio >= 5:
            score += 10
        elif like_ratio >= 3:
            score += 7
        elif like_ratio >= 1:
            score += 3

        comment_ratio = video.get('comment_ratio', 0)
        if comment_ratio >= 1:
            score += 10
        elif comment_ratio >= 0.5:
            score += 7
        elif comment_ratio >= 0.1:
            score += 3

        return score

    def _find_patterns(self, top: List[Dict], bottom: List[Dict]) -> List[Dict]:
        """Find patterns that differentiate top from bottom performers."""
        patterns = []

        # Analyze topic keywords
        top_topics = ' '.join(v.get('topic', '') for v in top).lower()
        bottom_topics = ' '.join(v.get('topic', '') for v in bottom).lower()

        # Check for theme patterns
        themes = ['sleep', 'confidence', 'healing', 'spiritual', 'nature', 'cosmic', 'adventure']
        for theme in themes:
            top_count = top_topics.count(theme)
            bottom_count = bottom_topics.count(theme)
            if top_count > bottom_count and top_count > 0:
                patterns.append({
                    'type': 'theme_positive',
                    'theme': theme,
                    'message': f"'{theme}' theme appears more in top performers",
                })
            elif bottom_count > top_count and bottom_count > 0:
                patterns.append({
                    'type': 'theme_negative',
                    'theme': theme,
                    'message': f"'{theme}' theme appears more in bottom performers",
                })

        # Analyze duration patterns
        top_durations = [v.get('video_duration_seconds', 0) or 0 for v in top]
        bottom_durations = [v.get('video_duration_seconds', 0) or 0 for v in bottom]

        if top_durations and bottom_durations:
            avg_top_duration = sum(top_durations) / len(top_durations) / 60  # minutes
            avg_bottom_duration = sum(bottom_durations) / len(bottom_durations) / 60

            if abs(avg_top_duration - avg_bottom_duration) > 5:  # 5+ minute difference
                patterns.append({
                    'type': 'duration',
                    'message': f"Top performers avg {avg_top_duration:.0f} min vs bottom {avg_bottom_duration:.0f} min",
                    'top_avg': avg_top_duration,
                    'bottom_avg': avg_bottom_duration,
                })

        return patterns

    def _extract_lessons(self, insights: Dict) -> List[Dict]:
        """Extract actionable lessons from insights."""
        lessons = []
        timestamp = datetime.now().isoformat()

        # Generate lessons from patterns
        for pattern in insights.get('patterns', []):
            if pattern['type'] == 'theme_positive':
                lessons.append({
                    'category': 'content',
                    'timestamp': timestamp,
                    'source': 'automated_analysis',
                    'insight': f"Sessions with '{pattern['theme']}' theme perform above average",
                    'action': f"Prioritize creating more {pattern['theme']}-themed sessions",
                    'confidence': 'medium',
                })
            elif pattern['type'] == 'theme_negative':
                lessons.append({
                    'category': 'content',
                    'timestamp': timestamp,
                    'source': 'automated_analysis',
                    'insight': f"Sessions with '{pattern['theme']}' theme tend to underperform",
                    'action': f"Review and improve {pattern['theme']}-themed sessions or reduce frequency",
                    'confidence': 'medium',
                })
            elif pattern['type'] == 'duration':
                optimal = pattern['top_avg']
                lessons.append({
                    'category': 'audio',
                    'timestamp': timestamp,
                    'source': 'automated_analysis',
                    'insight': f"Optimal video duration appears to be around {optimal:.0f} minutes",
                    'action': f"Target {optimal:.0f}-minute duration for new sessions",
                    'confidence': 'medium',
                })

        # Add overall performance summary
        if insights.get('avg_retention'):
            retention = insights['avg_retention']
            if retention < 30:
                lessons.append({
                    'category': 'content',
                    'timestamp': timestamp,
                    'source': 'automated_analysis',
                    'insight': f"Average retention is {retention:.1f}% - below target",
                    'action': "Review induction sections and first 2 minutes of content",
                    'confidence': 'high',
                })
            elif retention > 50:
                lessons.append({
                    'category': 'content',
                    'timestamp': timestamp,
                    'source': 'automated_analysis',
                    'insight': f"Average retention is excellent at {retention:.1f}%",
                    'action': "Current content pacing is working well - maintain approach",
                    'confidence': 'high',
                })

        return lessons

    def _update_lessons_learned(self, new_lessons: List[Dict]):
        """Update the lessons_learned.yaml file."""
        # Load existing lessons
        existing = {}
        if self.lessons_path.exists():
            try:
                with open(self.lessons_path) as f:
                    existing = yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Could not load existing lessons: {e}")

        # Initialize structure if needed
        if 'lessons' not in existing:
            existing['lessons'] = []
        if 'metadata' not in existing:
            existing['metadata'] = {}

        # Add new lessons (avoid duplicates based on insight text)
        existing_insights = {l.get('insight', '') for l in existing['lessons']}

        added = 0
        for lesson in new_lessons:
            if lesson.get('insight') not in existing_insights:
                existing['lessons'].append(lesson)
                existing_insights.add(lesson.get('insight'))
                added += 1

        # Update metadata
        existing['metadata']['last_automated_update'] = datetime.now().isoformat()
        existing['metadata']['total_automated_lessons'] = sum(
            1 for l in existing['lessons'] if l.get('source') == 'automated_analysis'
        )

        # Save
        with open(self.lessons_path, 'w') as f:
            yaml.dump(existing, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Added {added} new lessons to {self.lessons_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Automated Learning Pipeline')
    parser.add_argument('--daily', action='store_true', help='Run daily analytics collection')
    parser.add_argument('--weekly', action='store_true', help='Run weekly deep analysis')
    parser.add_argument('--video-id', help='Process specific video ID')
    parser.add_argument('--dry-run', action='store_true', help="Don't update knowledge base")
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    learner = AutomatedLearning(dry_run=args.dry_run)

    if args.daily:
        results = learner.run_daily()
        print(f"\n=== Daily Collection Results ===")
        print(f"Videos checked: {results.get('checked', 0)}")
        print(f"Analytics updated: {results.get('updated', 0)}")
        if results.get('videos'):
            print("\nUpdated videos:")
            for v in results['videos']:
                print(f"  - {v['session']}: {v['views']} views, {v['avg_duration']:.1f}% retention")

    elif args.weekly:
        results = learner.run_weekly()
        print(f"\n=== Weekly Analysis Results ===")
        print(f"Videos analyzed: {results.get('videos_analyzed', 0)}")
        print(f"Lessons added: {results.get('lessons_added', 0)}")

        if results.get('insights'):
            insights = results['insights']
            print(f"\nAverage views: {insights.get('avg_views', 0):.0f}")
            print(f"Average retention: {insights.get('avg_retention', 0):.1f}%")

            if insights.get('top_performers'):
                print("\nTop performers:")
                for v in insights['top_performers'][:3]:
                    print(f"  - {v['session']}: {v['views']} views, score={v['score']:.0f}")

            if insights.get('patterns'):
                print("\nPatterns found:")
                for p in insights['patterns']:
                    print(f"  - {p['message']}")

        if args.dry_run and results.get('lessons'):
            print("\n[DRY RUN] Lessons that would be added:")
            for lesson in results['lessons']:
                print(f"  - [{lesson['category']}] {lesson['insight']}")

    elif args.video_id:
        print(f"Processing video: {args.video_id}")
        analytics = learner._fetch_video_analytics(args.video_id)
        if analytics:
            print(f"Views: {analytics['views']}")
            print(f"Likes: {analytics['likes']}")
            print(f"Comments: {analytics['comments']}")
            print(f"Retention: {analytics.get('avg_view_duration_percent', 'N/A')}%")
        else:
            print("Could not fetch analytics")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
