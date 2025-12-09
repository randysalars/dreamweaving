#!/usr/bin/env python3
"""
YouTube Client

Handles YouTube API operations:
- OAuth authentication with automatic token refresh
- Video uploads (long-form and shorts)
- Channel analytics retrieval
- Video metadata management

Based on proven OAuth implementation from Black Hawk Visions project.

Usage:
    from scripts.automation.youtube_client import YouTubeClient

    client = YouTubeClient()

    # Upload a video
    video_id = client.upload_video(
        video_path='/path/to/video.mp4',
        title='My Video Title',
        description='Video description...',
        tags=['tag1', 'tag2'],
        privacy_status='public'
    )

    # Get channel info
    info = client.get_channel_info()

    # Get analytics
    analytics = client.get_channel_analytics(days=90)

Requirements:
    pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

Setup:
    1. Go to Google Cloud Console
    2. Create OAuth 2.0 credentials
    3. Download as client_secret.json to config/youtube_credentials/
    4. First run will open browser for authentication
    5. token.json will be saved automatically
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

# OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
]

# Default credentials directory
DEFAULT_CREDENTIALS_DIR = Path(__file__).parent.parent.parent / 'config' / 'youtube_credentials'

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


class YouTubeClient:
    """YouTube API client with OAuth authentication."""

    def __init__(self, credentials_dir: Optional[Path] = None):
        """Initialize YouTube client.

        Args:
            credentials_dir: Directory containing client_secret.json and token.json
        """
        self.credentials_dir = Path(credentials_dir) if credentials_dir else DEFAULT_CREDENTIALS_DIR
        self.credentials_dir.mkdir(parents=True, exist_ok=True)

        # Check multiple locations for client_secret.json
        self.client_secret_path = self.credentials_dir / 'client_secret.json'

        # Fallback: check config/youtube_client_secret.json (existing location)
        if not self.client_secret_path.exists():
            fallback_path = Path(__file__).parent.parent.parent / 'config' / 'youtube_client_secret.json'
            if fallback_path.exists():
                self.client_secret_path = fallback_path
                logger.info(f"Using existing credentials from {fallback_path}")

        self.token_path = self.credentials_dir / 'token.json'

        self._youtube = None
        self._youtube_analytics = None
        self._credentials = None

    # ==================== Authentication ====================

    def _get_credentials(self) -> Credentials:
        """Get or refresh OAuth credentials.

        Returns:
            Valid OAuth credentials

        Raises:
            FileNotFoundError: If client_secret.json not found
            RuntimeError: If authentication fails
        """
        creds = None

        # Load existing token
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
                logger.debug("Loaded existing credentials from token.json")
            except Exception as e:
                logger.warning(f"Failed to load token.json: {e}")

        # Check if credentials are valid
        if creds and creds.valid:
            return creds

        # Try to refresh expired credentials
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self._save_credentials(creds)
                logger.info("Refreshed expired credentials")
                return creds
            except RefreshError as e:
                logger.warning(f"Failed to refresh token: {e}")
                creds = None

        # Need new authentication
        if not creds:
            if not self.client_secret_path.exists():
                raise FileNotFoundError(
                    f"client_secret.json not found at {self.client_secret_path}\n"
                    "Please download OAuth credentials from Google Cloud Console."
                )

            logger.info("Starting OAuth flow - browser will open for authentication")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.client_secret_path),
                SCOPES
            )
            creds = flow.run_local_server(port=0)
            self._save_credentials(creds)
            logger.info("Authentication successful, saved new token.json")

        return creds

    def _save_credentials(self, creds: Credentials):
        """Save credentials to token.json.

        Args:
            creds: Credentials to save
        """
        with open(self.token_path, 'w') as token:
            token.write(creds.to_json())
        logger.debug(f"Saved credentials to {self.token_path}")

    def _refresh_if_needed(self, creds: Credentials) -> Credentials:
        """Refresh credentials if expiring within 5 minutes.

        Args:
            creds: Current credentials

        Returns:
            Valid credentials (refreshed if needed)
        """
        if creds.expiry and creds.expiry - timedelta(minutes=5) < datetime.now(creds.expiry.tzinfo):
            try:
                creds.refresh(Request())
                self._save_credentials(creds)
                logger.info("Proactively refreshed credentials")
            except RefreshError as e:
                logger.warning(f"Failed to refresh: {e}")
                # Re-authenticate
                creds = self._get_credentials()
        return creds

    def _get_youtube_service(self):
        """Get authenticated YouTube Data API service.

        Returns:
            YouTube Data API service
        """
        if self._youtube is None or self._credentials is None:
            self._credentials = self._get_credentials()
            self._credentials = self._refresh_if_needed(self._credentials)
            self._youtube = build('youtube', 'v3', credentials=self._credentials)
        return self._youtube

    def _get_analytics_service(self):
        """Get authenticated YouTube Analytics API service.

        Returns:
            YouTube Analytics API service
        """
        if self._youtube_analytics is None:
            if self._credentials is None:
                self._credentials = self._get_credentials()
            self._credentials = self._refresh_if_needed(self._credentials)
            self._youtube_analytics = build('youtubeAnalytics', 'v2', credentials=self._credentials)
        return self._youtube_analytics

    # ==================== Video Upload ====================

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str] = None,
        category_id: str = '22',
        privacy_status: str = 'public',
        made_for_kids: bool = False,
        is_short: bool = False,
        notify_subscribers: bool = True,
        thumbnail_path: Optional[str] = None,
    ) -> str:
        """Upload a video to YouTube.

        Args:
            video_path: Path to video file
            title: Video title (max 100 chars)
            description: Video description (max 5000 chars)
            tags: List of tags (total max 500 chars)
            category_id: YouTube category ID (default: 22 = People & Blogs)
            privacy_status: public | private | unlisted
            made_for_kids: Whether video is made for kids
            is_short: Whether this is a YouTube Short
            notify_subscribers: Whether to notify subscribers
            thumbnail_path: Optional custom thumbnail path

        Returns:
            YouTube video ID

        Raises:
            FileNotFoundError: If video file not found
            HttpError: If upload fails
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        youtube = self._get_youtube_service()

        # Prepare title (add #Shorts if short)
        if is_short and '#Shorts' not in title:
            title = f"{title} #Shorts"

        # Truncate to limits
        title = title[:100]
        description = description[:5000]

        # Trim tags to 500 char limit
        if tags:
            tags = self._trim_tags(tags, max_chars=500)

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': category_id,
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': made_for_kids,
                'notifySubscribers': notify_subscribers,
            },
        }

        # Create media upload
        media = MediaFileUpload(
            str(video_path),
            chunksize=-1,  # Upload in one request
            resumable=True
        )

        # Execute upload with retries
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Uploading {video_path.name} (attempt {attempt + 1}/{MAX_RETRIES})")

                request = youtube.videos().insert(
                    part=','.join(body.keys()),
                    body=body,
                    media_body=media
                )

                response = self._resumable_upload(request)
                video_id = response['id']

                logger.info(f"Upload successful! Video ID: {video_id}")
                logger.info(f"URL: https://www.youtube.com/watch?v={video_id}")

                # Set thumbnail if provided
                if thumbnail_path:
                    self.set_thumbnail(video_id, thumbnail_path)

                return video_id

            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    # Retry on server errors
                    logger.warning(f"Server error {e.resp.status}, retrying in {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    logger.error(f"Upload failed: {e}")
                    raise

        raise RuntimeError(f"Upload failed after {MAX_RETRIES} attempts")

    def _resumable_upload(self, request) -> Dict:
        """Execute resumable upload with progress tracking.

        Args:
            request: YouTube API insert request

        Returns:
            Upload response
        """
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.debug(f"Upload progress: {int(status.progress() * 100)}%")
        return response

    def _trim_tags(self, tags: List[str], max_chars: int = 500) -> List[str]:
        """Trim tags to fit within character limit.

        Args:
            tags: List of tags
            max_chars: Maximum total characters

        Returns:
            Trimmed list of tags
        """
        total_chars = 0
        trimmed = []
        for tag in tags:
            tag = tag.strip()
            # +1 for comma separator
            if total_chars + len(tag) + 1 <= max_chars:
                trimmed.append(tag)
                total_chars += len(tag) + 1
            else:
                break
        return trimmed

    def set_thumbnail(self, video_id: str, thumbnail_path: str):
        """Set custom thumbnail for a video.

        Args:
            video_id: YouTube video ID
            thumbnail_path: Path to thumbnail image (JPEG or PNG)
        """
        thumbnail_path = Path(thumbnail_path)
        if not thumbnail_path.exists():
            logger.warning(f"Thumbnail not found: {thumbnail_path}")
            return

        youtube = self._get_youtube_service()

        try:
            media = MediaFileUpload(str(thumbnail_path), mimetype='image/png')
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()
            logger.info(f"Set custom thumbnail for video {video_id}")
        except HttpError as e:
            logger.error(f"Failed to set thumbnail: {e}")

    # ==================== Channel Info ====================

    def get_channel_info(self) -> Dict[str, Any]:
        """Get authenticated channel information.

        Returns:
            Channel info dict with id, title, subscriber count, etc.
        """
        youtube = self._get_youtube_service()

        request = youtube.channels().list(
            part='snippet,statistics',
            mine=True
        )
        response = request.execute()

        if not response.get('items'):
            raise RuntimeError("No channel found for authenticated user")

        channel = response['items'][0]
        return {
            'id': channel['id'],
            'title': channel['snippet']['title'],
            'description': channel['snippet'].get('description', ''),
            'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
            'video_count': int(channel['statistics'].get('videoCount', 0)),
            'view_count': int(channel['statistics'].get('viewCount', 0)),
        }

    # ==================== Analytics ====================

    def get_channel_analytics(self, days: int = 90) -> Dict[str, Any]:
        """Get channel analytics for the past N days.

        Args:
            days: Number of days to fetch (max 730)

        Returns:
            Analytics data including views by time, engagement metrics
        """
        analytics = self._get_analytics_service()

        # Get channel ID
        channel_info = self.get_channel_info()
        channel_id = channel_info['id']

        # Date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        try:
            # Basic metrics
            response = analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date,
                endDate=end_date,
                metrics='views,estimatedMinutesWatched,averageViewDuration,subscribersGained',
                dimensions='day',
                sort='day'
            ).execute()

            # Parse results
            results = {
                'channel_id': channel_id,
                'start_date': start_date,
                'end_date': end_date,
                'daily_data': [],
                'totals': {
                    'views': 0,
                    'watch_time_minutes': 0,
                    'subscribers_gained': 0,
                }
            }

            if 'rows' in response:
                for row in response['rows']:
                    day_data = {
                        'date': row[0],
                        'views': row[1],
                        'watch_time_minutes': row[2],
                        'avg_view_duration': row[3],
                        'subscribers_gained': row[4],
                    }
                    results['daily_data'].append(day_data)
                    results['totals']['views'] += row[1]
                    results['totals']['watch_time_minutes'] += row[2]
                    results['totals']['subscribers_gained'] += row[4]

            return results

        except HttpError as e:
            logger.error(f"Failed to fetch analytics: {e}")
            return {'error': str(e)}

    def get_hourly_analytics(self, days: int = 28) -> Dict[str, Any]:
        """Get hourly view patterns for optimal upload timing.

        Args:
            days: Number of days to analyze

        Returns:
            Hourly view distribution
        """
        analytics = self._get_analytics_service()
        channel_info = self.get_channel_info()
        channel_id = channel_info['id']

        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        try:
            # Views by hour (only available for last 28 days)
            response = analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date,
                endDate=end_date,
                metrics='views',
                dimensions='day,hour',
                sort='day,hour'
            ).execute()

            # Aggregate by hour
            hourly_views = {str(h).zfill(2): 0 for h in range(24)}

            if 'rows' in response:
                for row in response['rows']:
                    hour = str(row[1]).zfill(2)
                    views = row[2]
                    hourly_views[hour] += views

            return {
                'channel_id': channel_id,
                'start_date': start_date,
                'end_date': end_date,
                'hourly_views': hourly_views,
                'peak_hour': max(hourly_views, key=hourly_views.get),
            }

        except HttpError as e:
            logger.error(f"Failed to fetch hourly analytics: {e}")
            return {'error': str(e)}

    # ==================== Video Management ====================

    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get information about a specific video.

        Args:
            video_id: YouTube video ID

        Returns:
            Video info dict
        """
        youtube = self._get_youtube_service()

        response = youtube.videos().list(
            part='snippet,statistics,status',
            id=video_id
        ).execute()

        if not response.get('items'):
            return {'error': f'Video not found: {video_id}'}

        video = response['items'][0]
        return {
            'id': video['id'],
            'title': video['snippet']['title'],
            'description': video['snippet'].get('description', ''),
            'published_at': video['snippet'].get('publishedAt'),
            'view_count': int(video['statistics'].get('viewCount', 0)),
            'like_count': int(video['statistics'].get('likeCount', 0)),
            'comment_count': int(video['statistics'].get('commentCount', 0)),
            'privacy_status': video['status'].get('privacyStatus'),
        }

    def list_recent_videos(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """List recent videos on the channel.

        Args:
            max_results: Maximum number of videos to return

        Returns:
            List of video info dicts
        """
        youtube = self._get_youtube_service()
        channel_info = self.get_channel_info()
        channel_id = channel_info['id']

        # Get uploads playlist
        response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()

        uploads_playlist = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Get videos from playlist
        response = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist,
            maxResults=max_results
        ).execute()

        videos = []
        for item in response.get('items', []):
            videos.append({
                'video_id': item['snippet']['resourceId']['videoId'],
                'title': item['snippet']['title'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail': item['snippet']['thumbnails'].get('high', {}).get('url'),
            })

        return videos


# ==================== CLI ====================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='YouTube Client')
    parser.add_argument('--auth', action='store_true', help='Test authentication')
    parser.add_argument('--channel', action='store_true', help='Show channel info')
    parser.add_argument('--analytics', action='store_true', help='Show channel analytics')
    parser.add_argument('--videos', action='store_true', help='List recent videos')
    parser.add_argument('--upload', type=str, help='Upload video file')
    parser.add_argument('--title', type=str, default='Test Video', help='Video title')
    parser.add_argument('--description', type=str, default='Test upload', help='Video description')
    parser.add_argument('--privacy', type=str, default='unlisted', help='Privacy status')
    parser.add_argument('--credentials', type=str, help='Credentials directory')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    creds_dir = Path(args.credentials) if args.credentials else None
    client = YouTubeClient(creds_dir)

    if args.auth:
        print("Testing authentication...")
        try:
            client._get_credentials()
            print("Authentication successful!")
        except Exception as e:
            print(f"Authentication failed: {e}")

    if args.channel:
        print("\n=== Channel Info ===")
        info = client.get_channel_info()
        for key, value in info.items():
            print(f"{key}: {value}")

    if args.analytics:
        print("\n=== Channel Analytics (Last 90 Days) ===")
        analytics = client.get_channel_analytics(days=90)
        print(f"Total views: {analytics['totals']['views']:,}")
        print(f"Watch time: {analytics['totals']['watch_time_minutes']:,} minutes")
        print(f"Subscribers gained: {analytics['totals']['subscribers_gained']}")

    if args.videos:
        print("\n=== Recent Videos ===")
        videos = client.list_recent_videos(max_results=5)
        for v in videos:
            print(f"- {v['title']} ({v['video_id']})")

    if args.upload:
        print(f"\n=== Uploading {args.upload} ===")
        video_id = client.upload_video(
            video_path=args.upload,
            title=args.title,
            description=args.description,
            privacy_status=args.privacy
        )
        print(f"Uploaded! Video ID: {video_id}")
        print(f"URL: https://www.youtube.com/watch?v={video_id}")
