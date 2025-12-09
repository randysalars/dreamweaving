#!/usr/bin/env python3
"""
YouTube Competitor Analyzer for Dreamweaving

Fetches and analyzes competitor videos from YouTube to extract successful patterns
for titles, tags, descriptions, and engagement metrics.

Features:
- Search competitor videos by category/keyword
- Fetch video statistics (views, likes, comments)
- Extract metadata (title, description, tags, thumbnails)
- Analyze our channel performance
- Fetch comments for sentiment analysis
- Output to YAML for RAG integration

Usage:
    # Analyze a single category
    python3 scripts/ai/youtube_competitor_analyzer.py --category meditation

    # Analyze all categories
    python3 scripts/ai/youtube_competitor_analyzer.py --categories all

    # Check our channel
    python3 scripts/ai/youtube_competitor_analyzer.py --our-channel

    # Weekly sync (for cron)
    python3 scripts/ai/youtube_competitor_analyzer.py --weekly-sync

Author: Dreamweaving AI System
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import time

import yaml

# Google API imports
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    HAS_GOOGLE_API = True
except ImportError:
    HAS_GOOGLE_API = False
    print("Warning: google-api-python-client not installed. Run:")
    print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "youtube_config.yaml"
OUTPUT_PATH = PROJECT_ROOT / "knowledge" / "youtube_competitor_data"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / "logs" / "youtube_analysis.log")
    ]
)
logger = logging.getLogger(__name__)


class YouTubeCompetitorAnalyzer:
    """
    Analyzes YouTube competitors in meditation/hypnosis/spiritual niches.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the analyzer with configuration."""
        self.config_path = config_path or CONFIG_PATH
        self.config = self._load_config()
        self.youtube = None
        self._authenticated = False

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            logger.warning(f"Config file not found: {self.config_path}")
            return {}

    def _save_config(self):
        """Save configuration back to YAML file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

    def authenticate(self, use_api_key: bool = True) -> bool:
        """
        Authenticate with YouTube Data API.

        Args:
            use_api_key: If True, use API key (simpler, read-only).
                        If False, use OAuth2 (required for channel analytics).

        Returns:
            True if authentication successful, False otherwise
        """
        if not HAS_GOOGLE_API:
            logger.error("Google API client not installed")
            return False

        # Try API key first (simpler, no OAuth verification needed)
        api_key = os.environ.get('YOUTUBE_API_KEY') or self.config.get('api', {}).get('api_key')

        if use_api_key and api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=api_key)
                self._authenticated = True
                logger.info("Authenticated with YouTube API using API key")
                return True
            except Exception as e:
                logger.warning(f"API key auth failed: {e}, trying OAuth...")

        # Fall back to OAuth2
        scopes = self.config.get('api', {}).get('scopes', [
            "https://www.googleapis.com/auth/youtube.readonly"
        ])

        client_secrets = PROJECT_ROOT / self.config.get('api', {}).get(
            'client_secrets_file', 'config/youtube_client_secret.json'
        )
        token_file = PROJECT_ROOT / self.config.get('api', {}).get(
            'token_file', 'config/youtube_token.json'
        )

        creds = None

        # Load existing credentials
        if token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_file), scopes)
            except Exception as e:
                logger.warning(f"Failed to load existing credentials: {e}")

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Credentials refreshed successfully")
                except Exception as e:
                    logger.warning(f"Failed to refresh credentials: {e}")
                    creds = None

            if not creds:
                if not client_secrets.exists():
                    logger.error(f"Client secrets file not found: {client_secrets}")
                    return False

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(client_secrets), scopes
                    )
                    creds = flow.run_local_server(port=0)
                    logger.info("New credentials obtained")
                except Exception as e:
                    logger.error(f"Failed to authenticate: {e}")
                    return False

            # Save credentials
            with open(token_file, 'w') as f:
                f.write(creds.to_json())

        # Build YouTube service
        try:
            self.youtube = build('youtube', 'v3', credentials=creds)
            self._authenticated = True
            logger.info("YouTube API authenticated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to build YouTube service: {e}")
            return False

    def search_videos(
        self,
        query: str,
        max_results: int = 50,
        published_after: Optional[datetime] = None,
        order: str = "viewCount"
    ) -> List[Dict[str, Any]]:
        """
        Search for videos matching a query.

        Args:
            query: Search query string
            max_results: Maximum number of results (max 50 per request)
            published_after: Only include videos published after this date
            order: Sort order (viewCount, relevance, date, rating)

        Returns:
            List of video search results
        """
        if not self._authenticated:
            logger.error("Not authenticated. Call authenticate() first.")
            return []

        results = []
        next_page_token = None

        try:
            while len(results) < max_results:
                request_params = {
                    'q': query,
                    'part': 'snippet',
                    'type': 'video',
                    'maxResults': min(50, max_results - len(results)),
                    'order': order,
                    'regionCode': 'US',
                    'relevanceLanguage': 'en'
                }

                if published_after:
                    request_params['publishedAfter'] = published_after.isoformat() + 'Z'

                if next_page_token:
                    request_params['pageToken'] = next_page_token

                response = self.youtube.search().list(**request_params).execute()

                for item in response.get('items', []):
                    results.append({
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'channel_id': item['snippet']['channelId'],
                        'channel_title': item['snippet']['channelTitle'],
                        'published_at': item['snippet']['publishedAt'],
                        'thumbnail_url': item['snippet']['thumbnails'].get('high', {}).get('url', '')
                    })

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

                # Rate limiting
                time.sleep(0.1)

            logger.info(f"Found {len(results)} videos for query: {query}")
            return results

        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            return results

    def get_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed statistics and metadata for videos.

        Args:
            video_ids: List of video IDs

        Returns:
            List of video details with stats
        """
        if not self._authenticated:
            logger.error("Not authenticated. Call authenticate() first.")
            return []

        results = []

        # Process in batches of 50
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i + 50]

            try:
                response = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails,topicDetails',
                    id=','.join(batch)
                ).execute()

                for item in response.get('items', []):
                    stats = item.get('statistics', {})
                    snippet = item.get('snippet', {})
                    content = item.get('contentDetails', {})

                    results.append({
                        'video_id': item['id'],
                        'title': snippet.get('title', ''),
                        'description': snippet.get('description', ''),
                        'channel_id': snippet.get('channelId', ''),
                        'channel_title': snippet.get('channelTitle', ''),
                        'published_at': snippet.get('publishedAt', ''),
                        'tags': snippet.get('tags', []),
                        'category_id': snippet.get('categoryId', ''),
                        'thumbnail_url': snippet.get('thumbnails', {}).get('maxres', {}).get('url') or
                                        snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                        'duration': content.get('duration', ''),
                        'view_count': int(stats.get('viewCount', 0)),
                        'like_count': int(stats.get('likeCount', 0)),
                        'comment_count': int(stats.get('commentCount', 0)),
                        'favorite_count': int(stats.get('favoriteCount', 0))
                    })

                # Rate limiting
                time.sleep(0.1)

            except HttpError as e:
                logger.error(f"YouTube API error getting video details: {e}")

        logger.info(f"Got details for {len(results)} videos")
        return results

    def get_channel_details(self, channel_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get channel statistics and metadata.

        Args:
            channel_ids: List of channel IDs

        Returns:
            List of channel details
        """
        if not self._authenticated:
            logger.error("Not authenticated. Call authenticate() first.")
            return []

        results = []

        # Process in batches of 50
        for i in range(0, len(channel_ids), 50):
            batch = channel_ids[i:i + 50]

            try:
                response = self.youtube.channels().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(batch)
                ).execute()

                for item in response.get('items', []):
                    stats = item.get('statistics', {})
                    snippet = item.get('snippet', {})

                    results.append({
                        'channel_id': item['id'],
                        'title': snippet.get('title', ''),
                        'description': snippet.get('description', ''),
                        'custom_url': snippet.get('customUrl', ''),
                        'published_at': snippet.get('publishedAt', ''),
                        'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                        'country': snippet.get('country', ''),
                        'subscriber_count': int(stats.get('subscriberCount', 0)),
                        'view_count': int(stats.get('viewCount', 0)),
                        'video_count': int(stats.get('videoCount', 0)),
                        'hidden_subscriber_count': stats.get('hiddenSubscriberCount', False)
                    })

                time.sleep(0.1)

            except HttpError as e:
                logger.error(f"YouTube API error getting channel details: {e}")

        logger.info(f"Got details for {len(results)} channels")
        return results

    def get_video_comments(
        self,
        video_id: str,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get comments for a video.

        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments

        Returns:
            List of comment data
        """
        if not self._authenticated:
            logger.error("Not authenticated. Call authenticate() first.")
            return []

        results = []
        next_page_token = None

        try:
            while len(results) < max_results:
                request_params = {
                    'videoId': video_id,
                    'part': 'snippet',
                    'maxResults': min(100, max_results - len(results)),
                    'order': 'relevance',
                    'textFormat': 'plainText'
                }

                if next_page_token:
                    request_params['pageToken'] = next_page_token

                response = self.youtube.commentThreads().list(**request_params).execute()

                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    results.append({
                        'comment_id': item['id'],
                        'video_id': video_id,
                        'author': comment.get('authorDisplayName', ''),
                        'text': comment.get('textDisplay', ''),
                        'like_count': comment.get('likeCount', 0),
                        'published_at': comment.get('publishedAt', ''),
                        'reply_count': item['snippet'].get('totalReplyCount', 0)
                    })

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

                time.sleep(0.1)

        except HttpError as e:
            # Comments might be disabled
            if 'commentsDisabled' in str(e):
                logger.info(f"Comments disabled for video {video_id}")
            else:
                logger.error(f"YouTube API error getting comments: {e}")

        return results

    def analyze_category(
        self,
        category: str,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze videos in a specific category.

        Args:
            category: Category name from config
            save_results: Whether to save results to YAML

        Returns:
            Analysis results
        """
        if category not in self.config.get('categories', {}):
            logger.error(f"Unknown category: {category}")
            return {}

        cat_config = self.config['categories'][category]
        keywords = cat_config.get('keywords', [])
        max_results = cat_config.get('max_results', 50)
        min_views = cat_config.get('min_views', 10000)

        logger.info(f"Analyzing category: {category}")

        all_videos = []
        all_channels = set()

        # Search for each keyword
        for keyword in keywords:
            logger.info(f"  Searching: {keyword}")

            # Search videos
            search_results = self.search_videos(
                query=keyword,
                max_results=max_results,
                published_after=datetime.now() - timedelta(days=365),
                order="viewCount"
            )

            if search_results:
                video_ids = [v['video_id'] for v in search_results]

                # Get detailed stats
                video_details = self.get_video_details(video_ids)

                # Filter by minimum views
                filtered = [v for v in video_details if v['view_count'] >= min_views]

                all_videos.extend(filtered)
                all_channels.update(v['channel_id'] for v in filtered)

            time.sleep(0.5)  # Rate limiting between keywords

        # Deduplicate videos
        seen_ids = set()
        unique_videos = []
        for video in all_videos:
            if video['video_id'] not in seen_ids:
                seen_ids.add(video['video_id'])
                unique_videos.append(video)

        # Sort by views
        unique_videos.sort(key=lambda x: x['view_count'], reverse=True)

        # Get channel details
        channel_details = self.get_channel_details(list(all_channels))

        # Build results
        results = {
            'category': category,
            'analyzed_at': datetime.now().isoformat(),
            'total_videos': len(unique_videos),
            'total_channels': len(channel_details),
            'videos': unique_videos[:100],  # Top 100
            'channels': channel_details
        }

        # Save results
        if save_results:
            output_file = OUTPUT_PATH / "raw" / f"{category}_raw.yaml"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Saved raw results to {output_file}")

        return results

    def analyze_our_channel(self, save_results: bool = True) -> Dict[str, Any]:
        """
        Analyze our own channel's performance.

        Returns:
            Our channel analysis results
        """
        if not self._authenticated:
            logger.error("Not authenticated. Call authenticate() first.")
            return {}

        logger.info("Analyzing our channel...")

        try:
            # Get our channel info
            response = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                mine=True
            ).execute()

            if not response.get('items'):
                logger.error("Could not find authenticated channel")
                return {}

            channel = response['items'][0]
            channel_id = channel['id']
            uploads_playlist = channel['contentDetails']['relatedPlaylists']['uploads']

            # Save channel ID to config
            self.config['our_channel']['channel_id'] = channel_id
            self._save_config()

            # Get our videos from uploads playlist
            video_ids = []
            next_page_token = None

            while True:
                playlist_response = self.youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId=uploads_playlist,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()

                for item in playlist_response.get('items', []):
                    video_ids.append(item['contentDetails']['videoId'])

                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break

            # Get video details
            our_videos = self.get_video_details(video_ids)

            # Calculate metrics
            total_views = sum(v['view_count'] for v in our_videos)
            total_likes = sum(v['like_count'] for v in our_videos)
            total_comments = sum(v['comment_count'] for v in our_videos)

            results = {
                'channel_id': channel_id,
                'channel_name': channel['snippet']['title'],
                'analyzed_at': datetime.now().isoformat(),
                'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
                'total_views': int(channel['statistics'].get('viewCount', 0)),
                'video_count': len(our_videos),
                'avg_views': total_views // len(our_videos) if our_videos else 0,
                'avg_likes': total_likes // len(our_videos) if our_videos else 0,
                'avg_comments': total_comments // len(our_videos) if our_videos else 0,
                'engagement_rate': (total_likes + total_comments) / total_views if total_views else 0,
                'videos': our_videos
            }

            # Save results
            if save_results:
                output_file = OUTPUT_PATH / "our_channel_metrics.yaml"
                with open(output_file, 'w') as f:
                    yaml.dump(results, f, default_flow_style=False, allow_unicode=True)
                logger.info(f"Saved our channel metrics to {output_file}")

            return results

        except HttpError as e:
            logger.error(f"YouTube API error analyzing our channel: {e}")
            return {}

    def weekly_sync(self, categories: Optional[List[str]] = None):
        """
        Run weekly sync for all or specified categories.

        Args:
            categories: List of categories to sync, or None for all
        """
        if categories is None or 'all' in categories:
            categories = list(self.config.get('categories', {}).keys())

        logger.info(f"Starting weekly sync for categories: {categories}")

        results = {}
        for category in categories:
            try:
                results[category] = self.analyze_category(category)
                time.sleep(1)  # Rate limiting between categories
            except Exception as e:
                logger.error(f"Error analyzing category {category}: {e}")
                results[category] = {'error': str(e)}

        # Also check our channel
        try:
            results['our_channel'] = self.analyze_our_channel()
        except Exception as e:
            logger.error(f"Error analyzing our channel: {e}")
            results['our_channel'] = {'error': str(e)}

        # Save sync summary
        summary = {
            'sync_time': datetime.now().isoformat(),
            'categories_analyzed': list(results.keys()),
            'total_videos_found': sum(
                r.get('total_videos', 0) for r in results.values()
                if isinstance(r, dict) and 'total_videos' in r
            ),
            'total_channels_found': sum(
                r.get('total_channels', 0) for r in results.values()
                if isinstance(r, dict) and 'total_channels' in r
            )
        }

        summary_file = OUTPUT_PATH / "sync_summary.yaml"
        with open(summary_file, 'w') as f:
            yaml.dump(summary, f, default_flow_style=False)

        logger.info(f"Weekly sync complete. Summary saved to {summary_file}")
        return results


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Competitor Analyzer for Dreamweaving"
    )
    parser.add_argument(
        '--category', '-c',
        help="Analyze a single category"
    )
    parser.add_argument(
        '--categories',
        nargs='+',
        help="Analyze multiple categories (use 'all' for all)"
    )
    parser.add_argument(
        '--our-channel',
        action='store_true',
        help="Analyze our own channel"
    )
    parser.add_argument(
        '--weekly-sync',
        action='store_true',
        help="Run weekly sync for all categories"
    )
    parser.add_argument(
        '--search', '-s',
        help="Search for videos by query"
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=50,
        help="Maximum results (default: 50)"
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=CONFIG_PATH,
        help="Path to config file"
    )

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = YouTubeCompetitorAnalyzer(config_path=args.config)

    # Authenticate
    if not analyzer.authenticate():
        logger.error("Authentication failed. Exiting.")
        sys.exit(1)

    # Execute requested action
    if args.weekly_sync:
        analyzer.weekly_sync(args.categories)

    elif args.category:
        results = analyzer.analyze_category(args.category)
        print(f"\nAnalyzed {results.get('total_videos', 0)} videos in {args.category}")

    elif args.categories:
        for category in args.categories:
            if category == 'all':
                for cat in analyzer.config.get('categories', {}).keys():
                    analyzer.analyze_category(cat)
            else:
                analyzer.analyze_category(category)

    elif args.our_channel:
        results = analyzer.analyze_our_channel()
        print(f"\nOur channel: {results.get('channel_name', 'Unknown')}")
        print(f"  Subscribers: {results.get('subscriber_count', 0):,}")
        print(f"  Total views: {results.get('total_views', 0):,}")
        print(f"  Videos: {results.get('video_count', 0)}")
        print(f"  Avg views/video: {results.get('avg_views', 0):,}")
        print(f"  Engagement rate: {results.get('engagement_rate', 0):.2%}")

    elif args.search:
        results = analyzer.search_videos(args.search, max_results=args.limit)
        video_ids = [v['video_id'] for v in results]
        details = analyzer.get_video_details(video_ids)

        print(f"\nFound {len(details)} videos for '{args.search}':\n")
        for v in details[:10]:
            print(f"  {v['title'][:60]}...")
            print(f"    Views: {v['view_count']:,} | Likes: {v['like_count']:,}")
            print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
