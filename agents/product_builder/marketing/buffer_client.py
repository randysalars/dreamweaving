"""
Buffer Client
Schedules social media posts via Buffer API.
"""

import logging
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import requests

logger = logging.getLogger(__name__)


@dataclass
class BufferScheduleResult:
    """Result of scheduling posts to Buffer."""
    success: bool
    scheduled_count: int
    failed_count: int
    message: str
    scheduled_ids: List[str] = None
    errors: List[str] = None


class BufferClient:
    """
    Client for Buffer API to schedule social posts.
    
    Requires BUFFER_ACCESS_TOKEN environment variable.
    Get your token from: https://buffer.com/developers/apps
    
    Supported platforms via Buffer:
    - Twitter/X
    - LinkedIn
    - Instagram
    - Facebook
    - TikTok (via Buffer)
    """
    
    API_BASE = "https://api.bufferapp.com/1"
    
    # Buffer profile service types
    PLATFORM_TO_SERVICE = {
        "twitter": "twitter",
        "linkedin": "linkedin",
        "instagram": "instagram",
        "tiktok": "tiktok",
        "youtube": None,  # Not supported by Buffer
    }
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.getenv("BUFFER_ACCESS_TOKEN", "")
        self._profiles_cache = None
        
        if not self.access_token:
            logger.warning("No BUFFER_ACCESS_TOKEN set. Get one from buffer.com/developers/apps")
    
    def get_profiles(self) -> List[Dict]:
        """Get all connected social profiles."""
        if self._profiles_cache:
            return self._profiles_cache
        
        if not self.access_token:
            return []
        
        try:
            response = requests.get(
                f"{self.API_BASE}/profiles.json",
                params={"access_token": self.access_token},
                timeout=30
            )
            
            if response.status_code == 200:
                self._profiles_cache = response.json()
                return self._profiles_cache
            else:
                logger.error(f"Failed to get profiles: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Buffer API error: {e}")
            return []
    
    def get_profile_for_platform(self, platform: str) -> Optional[Dict]:
        """Get the first profile for a given platform."""
        service = self.PLATFORM_TO_SERVICE.get(platform.lower())
        if not service:
            return None
        
        profiles = self.get_profiles()
        for profile in profiles:
            if profile.get("service") == service:
                return profile
        
        return None
    
    def schedule_post(
        self,
        profile_id: str,
        text: str,
        scheduled_at: datetime = None,
        media_urls: List[str] = None
    ) -> Dict:
        """
        Schedule a single post to Buffer.
        
        Args:
            profile_id: Buffer profile ID
            text: Post content
            scheduled_at: When to post (None = add to queue)
            media_urls: Optional media attachments
            
        Returns:
            Buffer API response
        """
        if not self.access_token:
            return {"success": False, "error": "No access token"}
        
        data = {
            "access_token": self.access_token,
            "profile_ids[]": profile_id,
            "text": text,
        }
        
        if scheduled_at:
            data["scheduled_at"] = int(scheduled_at.timestamp())
        
        if media_urls:
            for i, url in enumerate(media_urls):
                data[f"media[photo][{i}]"] = url
        
        try:
            response = requests.post(
                f"{self.API_BASE}/updates/create.json",
                data=data,
                timeout=30
            )
            
            return response.json()
        except Exception as e:
            logger.error(f"Buffer schedule error: {e}")
            return {"success": False, "error": str(e)}
    
    def schedule_from_package(
        self,
        social_package,
        launch_date: datetime,
        dry_run: bool = False
    ) -> BufferScheduleResult:
        """
        Schedule all posts from a SocialPromoPackage.
        
        Args:
            social_package: SocialPromoPackage from social_promo_generator
            launch_date: When to launch (Day 0)
            dry_run: If True, validate without actually scheduling
            
        Returns:
            BufferScheduleResult with summary
        """
        logger.info(f"📅 Scheduling {len(social_package.posts)} posts to Buffer")
        logger.info(f"   Launch date: {launch_date.strftime('%Y-%m-%d')}")
        
        if not self.access_token:
            return BufferScheduleResult(
                success=False,
                scheduled_count=0,
                failed_count=len(social_package.posts),
                message="No BUFFER_ACCESS_TOKEN set",
                errors=["Missing access token"]
            )
        
        scheduled_ids = []
        errors = []
        skipped = 0
        
        for post in social_package.posts:
            platform = post.platform.value
            
            # Skip unsupported platforms
            if platform == "youtube":
                skipped += 1
                continue
            
            # Get profile for platform
            profile = self.get_profile_for_platform(platform)
            if not profile:
                errors.append(f"No {platform} profile connected to Buffer")
                continue
            
            # Calculate scheduled time
            scheduled_day = post.scheduled_day
            post_date = launch_date + timedelta(days=scheduled_day)
            
            # Parse best time and set hour
            if post.best_time:
                # e.g., "9am-11am" -> use 10am
                try:
                    time_parts = post.best_time.split("-")
                    hour_str = time_parts[0].strip().lower()
                    if "pm" in hour_str:
                        hour = int(hour_str.replace("pm", "")) + 12
                        if hour == 24:
                            hour = 12
                    else:
                        hour = int(hour_str.replace("am", ""))
                    post_date = post_date.replace(hour=hour, minute=0, second=0)
                except:
                    post_date = post_date.replace(hour=10, minute=0, second=0)
            else:
                post_date = post_date.replace(hour=10, minute=0, second=0)
            
            if dry_run:
                logger.info(f"   [DRY RUN] Would schedule: {platform} - {post_date}")
                scheduled_ids.append(f"dry_run_{len(scheduled_ids)}")
            else:
                result = self.schedule_post(
                    profile_id=profile["id"],
                    text=post.full_content,
                    scheduled_at=post_date
                )
                
                if result.get("success"):
                    scheduled_ids.append(result.get("updates", [{}])[0].get("id", "unknown"))
                    logger.info(f"   ✅ Scheduled: {platform} - {post_date}")
                else:
                    error_msg = result.get("error") or result.get("message") or "Unknown error"
                    errors.append(f"{platform}: {error_msg}")
                    logger.warning(f"   ❌ Failed: {platform} - {error_msg}")
        
        success = len(scheduled_ids) > 0 and len(errors) == 0
        
        return BufferScheduleResult(
            success=success,
            scheduled_count=len(scheduled_ids),
            failed_count=len(errors),
            message=f"Scheduled {len(scheduled_ids)} posts" + (f" ({skipped} skipped)" if skipped else ""),
            scheduled_ids=scheduled_ids,
            errors=errors if errors else None
        )
    
    def list_pending(self, profile_id: str = None) -> List[Dict]:
        """List pending scheduled posts."""
        if not self.access_token:
            return []
        
        profiles = [{"id": profile_id}] if profile_id else self.get_profiles()
        pending = []
        
        for profile in profiles:
            try:
                response = requests.get(
                    f"{self.API_BASE}/profiles/{profile['id']}/updates/pending.json",
                    params={"access_token": self.access_token},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    pending.extend(data.get("updates", []))
            except Exception as e:
                logger.error(f"Error fetching pending: {e}")
        
        return pending
    
    def clear_queue(self, profile_id: str) -> bool:
        """Clear all pending posts for a profile."""
        pending = self.list_pending(profile_id)
        
        for post in pending:
            try:
                requests.post(
                    f"{self.API_BASE}/updates/{post['id']}/destroy.json",
                    data={"access_token": self.access_token},
                    timeout=30
                )
            except Exception as e:
                logger.error(f"Error deleting post: {e}")
                return False
        
        return True


def schedule_to_buffer(
    social_package,
    launch_date: datetime,
    access_token: str = None,
    dry_run: bool = False
) -> BufferScheduleResult:
    """
    Convenience function to schedule a social package to Buffer.
    
    Args:
        social_package: SocialPromoPackage from SocialPromoGenerator
        launch_date: When to launch (Day 0)
        access_token: Buffer access token (or use BUFFER_ACCESS_TOKEN env var)
        dry_run: If True, validate without scheduling
        
    Returns:
        BufferScheduleResult
    """
    client = BufferClient(access_token)
    return client.schedule_from_package(social_package, launch_date, dry_run)
