#!/usr/bin/env python3
"""
Analytics Optimizer

Determines optimal upload times based on YouTube channel analytics.

Usage:
    from scripts.automation.analytics_optimizer import AnalyticsOptimizer

    optimizer = AnalyticsOptimizer(youtube_client, db)
    times = optimizer.get_optimal_upload_times()
    print(f"Best time for long videos: {times['optimal_long_upload_time']}")
    print(f"Best time for shorts: {times['optimal_shorts_upload_time']}")

CLI:
    python -m scripts.automation.analytics_optimizer --fetch
    python -m scripts.automation.analytics_optimizer --show
"""

import argparse
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Default fallback times (MST)
DEFAULT_LONG_UPLOAD_TIME = "12:00"
DEFAULT_SHORTS_UPLOAD_TIME = "08:00"

# Timezone offset: MST is UTC-7
MST_OFFSET = -7


class AnalyticsOptimizer:
    """Determines optimal upload times from YouTube analytics."""

    def __init__(self, youtube_client, db):
        """Initialize optimizer.

        Args:
            youtube_client: YouTubeClient instance
            db: StateDatabase instance
        """
        self.youtube = youtube_client
        self.db = db

    def get_optimal_upload_times(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get optimal upload times.

        Uses cached analytics if available and recent (< 7 days).
        Otherwise fetches fresh analytics from YouTube.

        Args:
            force_refresh: If True, always fetch fresh analytics

        Returns:
            Dict with optimal times and metadata
        """
        # Check cache
        if not force_refresh:
            cached = self.db.get_latest_analytics()
            if cached and self._is_cache_valid(cached):
                logger.info("Using cached analytics")
                return {
                    'optimal_long_upload_time': cached['optimal_long_upload_time'],
                    'optimal_shorts_upload_time': cached['optimal_shorts_upload_time'],
                    'best_day_of_week': cached['best_day_of_week'],
                    'source': 'cache',
                    'fetched_at': cached['fetched_at'],
                }

        # Fetch fresh analytics
        logger.info("Fetching fresh analytics from YouTube")
        try:
            return self._fetch_and_analyze()
        except Exception as e:
            logger.error(f"Failed to fetch analytics: {e}")
            return self._get_fallback_times()

    def _is_cache_valid(self, cached: Dict) -> bool:
        """Check if cached analytics are still valid.

        Args:
            cached: Cached analytics record

        Returns:
            True if cache is still valid (< 7 days old)
        """
        try:
            fetched_at = datetime.fromisoformat(cached['fetched_at'])
            age = datetime.now() - fetched_at
            return age.days < 7
        except Exception:
            return False

    def _fetch_and_analyze(self) -> Dict[str, Any]:
        """Fetch analytics and determine optimal times.

        Returns:
            Dict with optimal times
        """
        # Get hourly analytics
        hourly_data = self.youtube.get_hourly_analytics(days=28)

        if 'error' in hourly_data:
            logger.warning(f"Analytics error: {hourly_data['error']}")
            return self._get_fallback_times()

        # Get daily analytics for best day
        daily_data = self.youtube.get_channel_analytics(days=90)

        # Analyze hourly patterns
        hourly_views = hourly_data.get('hourly_views', {})
        optimal_long = self._find_optimal_long_time(hourly_views)
        optimal_shorts = self._find_optimal_shorts_time(hourly_views)

        # Analyze daily patterns
        best_day = self._find_best_day(daily_data)

        # Save to cache
        self.db.save_analytics(
            optimal_long_time=optimal_long,
            optimal_shorts_time=optimal_shorts,
            best_day=best_day,
            analytics_json=json.dumps({
                'hourly_views': hourly_views,
                'daily_totals': daily_data.get('totals', {}),
            })
        )

        return {
            'optimal_long_upload_time': optimal_long,
            'optimal_shorts_upload_time': optimal_shorts,
            'best_day_of_week': best_day,
            'source': 'youtube_api',
            'fetched_at': datetime.now().isoformat(),
        }

    def _find_optimal_long_time(self, hourly_views: Dict[str, int]) -> str:
        """Find optimal upload time for long-form videos.

        Strategy: Upload 2-3 hours before peak viewing time
        to allow YouTube's algorithm to index and recommend.

        Args:
            hourly_views: Dict of hour -> view count

        Returns:
            Optimal time in HH:MM format (MST)
        """
        if not hourly_views:
            return DEFAULT_LONG_UPLOAD_TIME

        # Convert to list for easier analysis
        hours = [(int(h), v) for h, v in hourly_views.items()]
        hours.sort(key=lambda x: x[1], reverse=True)

        # Find peak hour (UTC)
        peak_hour_utc = hours[0][0]

        # Upload 3 hours before peak
        upload_hour_utc = (peak_hour_utc - 3) % 24

        # Convert to MST
        upload_hour_mst = (upload_hour_utc + MST_OFFSET) % 24

        # Format as HH:00
        return f"{upload_hour_mst:02d}:00"

    def _find_optimal_shorts_time(self, hourly_views: Dict[str, int]) -> str:
        """Find optimal upload time for shorts.

        Strategy: Shorts perform best in morning commute hours.
        Look for morning peak (6am-10am) or use default.

        Args:
            hourly_views: Dict of hour -> view count

        Returns:
            Optimal time in HH:MM format (MST)
        """
        if not hourly_views:
            return DEFAULT_SHORTS_UPLOAD_TIME

        # Focus on morning hours (5am-12pm UTC = evening-morning MST)
        morning_hours = {h: v for h, v in hourly_views.items()
                        if 12 <= int(h) <= 18}  # UTC -> MST morning

        if morning_hours:
            peak_hour_utc = max(morning_hours.keys(), key=lambda h: morning_hours[h])
            upload_hour_utc = (int(peak_hour_utc) - 1) % 24
            upload_hour_mst = (upload_hour_utc + MST_OFFSET) % 24
            return f"{upload_hour_mst:02d}:00"

        return DEFAULT_SHORTS_UPLOAD_TIME

    def _find_best_day(self, daily_data: Dict) -> int:
        """Find best day of week for uploads.

        Args:
            daily_data: Daily analytics data

        Returns:
            Best day (0=Monday, 6=Sunday)
        """
        if 'daily_data' not in daily_data:
            return 2  # Default: Wednesday

        # Aggregate views by day of week
        day_views = {i: 0 for i in range(7)}

        for day in daily_data['daily_data']:
            try:
                date = datetime.strptime(day['date'], '%Y-%m-%d')
                dow = date.weekday()
                day_views[dow] += day.get('views', 0)
            except Exception:
                continue

        if not any(day_views.values()):
            return 2  # Default: Wednesday

        # Find best day
        best_day = max(day_views.keys(), key=lambda d: day_views[d])
        return best_day

    def _get_fallback_times(self) -> Dict[str, Any]:
        """Get fallback times when analytics unavailable.

        Returns:
            Dict with default times
        """
        return {
            'optimal_long_upload_time': DEFAULT_LONG_UPLOAD_TIME,
            'optimal_shorts_upload_time': DEFAULT_SHORTS_UPLOAD_TIME,
            'best_day_of_week': 2,  # Wednesday
            'source': 'fallback',
            'fetched_at': datetime.now().isoformat(),
        }

    def should_upload_now(self, upload_type: str = 'long') -> bool:
        """Check if current time is within optimal upload window.

        Args:
            upload_type: 'long' or 'shorts'

        Returns:
            True if current time is good for uploading
        """
        times = self.get_optimal_upload_times()

        if upload_type == 'shorts':
            optimal_time = times['optimal_shorts_upload_time']
        else:
            optimal_time = times['optimal_long_upload_time']

        # Parse optimal time
        try:
            optimal_hour = int(optimal_time.split(':')[0])
            current_hour = datetime.now().hour

            # Allow 1 hour window
            return abs(current_hour - optimal_hour) <= 1
        except Exception:
            return True  # Default to allow

    def get_next_upload_time(self, upload_type: str = 'long') -> datetime:
        """Get next optimal upload datetime.

        Args:
            upload_type: 'long' or 'shorts'

        Returns:
            Next optimal upload datetime
        """
        times = self.get_optimal_upload_times()

        if upload_type == 'shorts':
            optimal_time = times['optimal_shorts_upload_time']
        else:
            optimal_time = times['optimal_long_upload_time']

        try:
            optimal_hour = int(optimal_time.split(':')[0])
            optimal_minute = int(optimal_time.split(':')[1])

            now = datetime.now()
            next_upload = now.replace(hour=optimal_hour, minute=optimal_minute, second=0, microsecond=0)

            # If time has passed today, schedule for tomorrow
            if next_upload <= now:
                next_upload += timedelta(days=1)

            return next_upload
        except Exception:
            # Default: tomorrow at noon
            tomorrow = datetime.now() + timedelta(days=1)
            return tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)


def main():
    """Main entry point."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from scripts.automation.config_loader import load_config, setup_logging
    from scripts.automation.state_db import StateDatabase
    from scripts.automation.youtube_client import YouTubeClient

    parser = argparse.ArgumentParser(description='Analytics Optimizer')
    parser.add_argument('--fetch', action='store_true', help='Fetch fresh analytics')
    parser.add_argument('--show', action='store_true', help='Show optimal times')
    parser.add_argument('--config', type=str, help='Config file path')

    args = parser.parse_args()

    config = load_config(Path(args.config) if args.config else None)
    setup_logging(config)

    db = StateDatabase(Path(config['database']['path']))
    db.init_schema()

    youtube = YouTubeClient(Path(config['youtube']['credentials_dir']))

    optimizer = AnalyticsOptimizer(youtube, db)

    if args.fetch:
        print("Fetching analytics from YouTube...")
        times = optimizer.get_optimal_upload_times(force_refresh=True)
    else:
        times = optimizer.get_optimal_upload_times()

    if args.show or args.fetch:
        print("\n=== Optimal Upload Times (MST) ===")
        print(f"Long-form videos: {times['optimal_long_upload_time']}")
        print(f"Shorts: {times['optimal_shorts_upload_time']}")
        print(f"Best day: {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][times['best_day_of_week']]}")
        print(f"Source: {times['source']}")
        print(f"Fetched: {times['fetched_at']}")

        next_long = optimizer.get_next_upload_time('long')
        next_short = optimizer.get_next_upload_time('shorts')
        print(f"\nNext long upload: {next_long.strftime('%Y-%m-%d %H:%M')}")
        print(f"Next short upload: {next_short.strftime('%Y-%m-%d %H:%M')}")

    db.close()


if __name__ == '__main__':
    main()
