#!/usr/bin/env python3
"""
Notion YouTube Sync for Dreamweaving

Syncs YouTube competitor analysis data to Notion databases for manual review
and knowledge management. Creates/updates structured databases for:
- Competitor Channels
- Top Videos
- Title Patterns
- Tag Clusters
- Our Channel Metrics
- Seasonal Trends

Usage:
    # Sync all competitor data to Notion
    python3 scripts/ai/notion_youtube_sync.py --sync-all

    # Sync specific database
    python3 scripts/ai/notion_youtube_sync.py --sync competitor_channels

    # Create databases (first time setup)
    python3 scripts/ai/notion_youtube_sync.py --create-databases

    # View sync status
    python3 scripts/ai/notion_youtube_sync.py --status

Dependencies:
    pip install notion-client pyyaml
"""

import os
import sys
import json
import argparse
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

try:
    from notion_client import Client
    HAS_NOTION = True
except ImportError:
    HAS_NOTION = False
    print("Warning: notion-client not installed. Run: pip install notion-client")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "youtube_config.yaml"
NOTION_CONFIG_PATH = PROJECT_ROOT / "config" / "notion_config.yaml"
COMPETITOR_DATA_PATH = PROJECT_ROOT / "knowledge" / "youtube_competitor_data"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """Load YouTube config from YAML."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")

    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def load_notion_config() -> Dict[str, Any]:
    """Load Notion config and get token."""
    if not NOTION_CONFIG_PATH.exists():
        raise FileNotFoundError(f"Notion config not found: {NOTION_CONFIG_PATH}")

    with open(NOTION_CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    # Resolve environment variables
    def resolve_env(obj):
        if isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            var_name = obj[2:-1]
            return os.environ.get(var_name, obj)
        elif isinstance(obj, dict):
            return {k: resolve_env(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [resolve_env(item) for item in obj]
        return obj

    return resolve_env(config)


def get_notion_client() -> Client:
    """Initialize Notion client with token."""
    if not HAS_NOTION:
        raise ImportError("notion-client not installed")

    config = load_notion_config()
    token = config["notion"]["integration_token"]

    if not token or token.startswith("${"):
        raise ValueError(
            "NOTION_TOKEN not set. Create an integration at "
            "https://www.notion.so/profile/integrations and set the token."
        )

    return Client(auth=token)


class NotionYouTubeSync:
    """
    Syncs YouTube competitor analysis to Notion databases.

    Database Schema:

    1. Competitor Channels
       - Channel Name (title)
       - Channel ID (text)
       - Subscribers (number)
       - Total Views (number)
       - Video Count (number)
       - Category (multi-select)
       - Avg Views Per Video (number)
       - Growth Notes (rich text)
       - Last Updated (date)

    2. Top Videos
       - Video Title (title)
       - Video ID (text)
       - Channel (text)
       - Views (number)
       - Likes (number)
       - Comments (number)
       - Duration (text)
       - Publish Date (date)
       - Engagement Rate (number)
       - Category (multi-select)
       - Tags (multi-select, first 10)
       - Why It Works (rich text)
       - Title Pattern (text)

    3. Title Patterns
       - Pattern Name (title)
       - Pattern Template (text)
       - Avg CTR Estimate (number)
       - Example Titles (rich text)
       - Best For (multi-select)
       - Video Count (number)

    4. Tag Clusters
       - Tag Name (title)
       - Search Volume (select: high/medium/low)
       - Competition (select: high/medium/low)
       - Category (multi-select)
       - Avg Engagement (number)
       - Related Tags (rich text)

    5. Our Channel Metrics
       - Video Title (title)
       - Video ID (text)
       - Views (number)
       - Likes (number)
       - Comments (number)
       - Engagement Rate (number)
       - Publish Date (date)
       - vs Benchmark (text)
       - Category (select)
       - Improvements (rich text)

    6. Seasonal Trends
       - Month (title)
       - Year (number)
       - Interest Themes (rich text)
       - Recommended Topics (multi-select)
       - Best Upload Days (text)
       - Notes (rich text)
    """

    # Database schemas for creation
    DATABASE_SCHEMAS = {
        "competitor_channels": {
            "title": "YouTube Competitor Channels",
            "properties": {
                "Channel Name": {"title": {}},
                "Channel ID": {"rich_text": {}},
                "Subscribers": {"number": {"format": "number_with_commas"}},
                "Total Views": {"number": {"format": "number_with_commas"}},
                "Video Count": {"number": {"format": "number"}},
                "Category": {
                    "multi_select": {
                        "options": [
                            {"name": "meditation", "color": "blue"},
                            {"name": "hypnosis", "color": "purple"},
                            {"name": "sleep", "color": "green"},
                            {"name": "affirmations", "color": "yellow"},
                            {"name": "binaural_beats", "color": "orange"},
                            {"name": "spiritual", "color": "pink"},
                        ]
                    }
                },
                "Avg Views Per Video": {"number": {"format": "number_with_commas"}},
                "Growth Notes": {"rich_text": {}},
                "Last Updated": {"date": {}},
            }
        },
        "top_videos": {
            "title": "YouTube Top Videos",
            "properties": {
                "Video Title": {"title": {}},
                "Video ID": {"rich_text": {}},
                "Channel": {"rich_text": {}},
                "Views": {"number": {"format": "number_with_commas"}},
                "Likes": {"number": {"format": "number_with_commas"}},
                "Comments": {"number": {"format": "number"}},
                "Duration": {"rich_text": {}},
                "Publish Date": {"date": {}},
                "Engagement Rate": {"number": {"format": "percent"}},
                "Category": {
                    "multi_select": {
                        "options": [
                            {"name": "meditation", "color": "blue"},
                            {"name": "hypnosis", "color": "purple"},
                            {"name": "sleep", "color": "green"},
                            {"name": "affirmations", "color": "yellow"},
                            {"name": "binaural_beats", "color": "orange"},
                            {"name": "spiritual", "color": "pink"},
                        ]
                    }
                },
                "Tags": {"multi_select": {"options": []}},  # Dynamic
                "Why It Works": {"rich_text": {}},
                "Title Pattern": {"rich_text": {}},
            }
        },
        "title_patterns": {
            "title": "YouTube Title Patterns",
            "properties": {
                "Pattern Name": {"title": {}},
                "Pattern Template": {"rich_text": {}},
                "Avg CTR Estimate": {"number": {"format": "percent"}},
                "Example Titles": {"rich_text": {}},
                "Best For": {
                    "multi_select": {
                        "options": [
                            {"name": "meditation", "color": "blue"},
                            {"name": "hypnosis", "color": "purple"},
                            {"name": "sleep", "color": "green"},
                            {"name": "affirmations", "color": "yellow"},
                            {"name": "binaural_beats", "color": "orange"},
                            {"name": "spiritual", "color": "pink"},
                        ]
                    }
                },
                "Video Count": {"number": {"format": "number"}},
                "Priority": {
                    "select": {
                        "options": [
                            {"name": "high", "color": "red"},
                            {"name": "medium", "color": "yellow"},
                            {"name": "low", "color": "gray"},
                        ]
                    }
                },
            }
        },
        "tag_clusters": {
            "title": "YouTube Tag Clusters",
            "properties": {
                "Tag Name": {"title": {}},
                "Search Volume": {
                    "select": {
                        "options": [
                            {"name": "high", "color": "green"},
                            {"name": "medium", "color": "yellow"},
                            {"name": "low", "color": "gray"},
                        ]
                    }
                },
                "Competition": {
                    "select": {
                        "options": [
                            {"name": "high", "color": "red"},
                            {"name": "medium", "color": "yellow"},
                            {"name": "low", "color": "green"},
                        ]
                    }
                },
                "Category": {
                    "multi_select": {
                        "options": [
                            {"name": "meditation", "color": "blue"},
                            {"name": "hypnosis", "color": "purple"},
                            {"name": "sleep", "color": "green"},
                            {"name": "affirmations", "color": "yellow"},
                            {"name": "binaural_beats", "color": "orange"},
                            {"name": "spiritual", "color": "pink"},
                        ]
                    }
                },
                "Avg Engagement": {"number": {"format": "percent"}},
                "Video Count": {"number": {"format": "number"}},
                "Related Tags": {"rich_text": {}},
            }
        },
        "our_channel_metrics": {
            "title": "Our Channel Metrics",
            "properties": {
                "Video Title": {"title": {}},
                "Video ID": {"rich_text": {}},
                "Views": {"number": {"format": "number_with_commas"}},
                "Likes": {"number": {"format": "number_with_commas"}},
                "Comments": {"number": {"format": "number"}},
                "Engagement Rate": {"number": {"format": "percent"}},
                "Publish Date": {"date": {}},
                "vs Benchmark": {"rich_text": {}},
                "Category": {
                    "select": {
                        "options": [
                            {"name": "meditation", "color": "blue"},
                            {"name": "hypnosis", "color": "purple"},
                            {"name": "sleep", "color": "green"},
                            {"name": "affirmations", "color": "yellow"},
                            {"name": "binaural_beats", "color": "orange"},
                            {"name": "spiritual", "color": "pink"},
                        ]
                    }
                },
                "Improvements": {"rich_text": {}},
            }
        },
        "seasonal_trends": {
            "title": "YouTube Seasonal Trends",
            "properties": {
                "Month": {"title": {}},
                "Year": {"number": {"format": "number"}},
                "Interest Themes": {"rich_text": {}},
                "Recommended Topics": {"multi_select": {"options": []}},
                "Best Upload Days": {"rich_text": {}},
                "Video Count Sample": {"number": {"format": "number"}},
                "Notes": {"rich_text": {}},
            }
        },
    }

    def __init__(self):
        self.client = get_notion_client()
        self.config = load_config()
        self.notion_config = load_notion_config()
        self.workspace_root = self.notion_config["notion"]["workspace_root"]

        # Load database IDs from config
        self.database_ids = self.config.get("notion", {}).get("databases", {})

    def create_databases(self, parent_page_id: Optional[str] = None) -> Dict[str, str]:
        """
        Create all YouTube competitor databases in Notion.

        Args:
            parent_page_id: ID of parent page to create databases under.
                          Uses workspace root if not specified.

        Returns:
            Dict mapping database names to their IDs
        """
        parent_id = parent_page_id or self.workspace_root
        created_ids = {}

        for db_name, schema in self.DATABASE_SCHEMAS.items():
            logger.info(f"Creating database: {schema['title']}")

            try:
                response = self.client.databases.create(
                    parent={"page_id": parent_id},
                    title=[{"type": "text", "text": {"content": schema["title"]}}],
                    properties=schema["properties"]
                )

                db_id = response["id"]
                created_ids[db_name] = db_id
                logger.info(f"  Created: {db_id}")

            except Exception as e:
                logger.error(f"  Failed to create {db_name}: {e}")

        # Save to config
        self._save_database_ids(created_ids)

        return created_ids

    def _save_database_ids(self, db_ids: Dict[str, str]):
        """Save database IDs to youtube_config.yaml"""
        config = load_config()

        if "notion" not in config:
            config["notion"] = {}
        if "databases" not in config["notion"]:
            config["notion"]["databases"] = {}

        config["notion"]["databases"].update(db_ids)

        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Saved database IDs to {CONFIG_PATH}")

    def _load_yaml_data(self, filename: str) -> Optional[Dict]:
        """Load YAML data from competitor data directory."""
        filepath = COMPETITOR_DATA_PATH / filename
        if filepath.exists():
            with open(filepath) as f:
                return yaml.safe_load(f)
        return None

    def sync_competitor_channels(self):
        """Sync competitor channel data to Notion."""
        db_id = self.database_ids.get("competitor_channels")
        if not db_id:
            logger.error("No database ID for competitor_channels. Run --create-databases first.")
            return

        data = self._load_yaml_data("competitor_channels.yaml")
        if not data or "channels" not in data:
            logger.warning("No competitor channel data found")
            return

        synced = 0
        for category, channels in data["channels"].items():
            for channel in channels:
                try:
                    # Check if channel already exists
                    existing = self._find_by_property(
                        db_id, "Channel ID", channel.get("channel_id", "")
                    )

                    properties = self._build_channel_properties(channel, category)

                    if existing:
                        # Update existing
                        self.client.pages.update(
                            page_id=existing["id"],
                            properties=properties
                        )
                        logger.debug(f"Updated: {channel.get('name')}")
                    else:
                        # Create new
                        self.client.pages.create(
                            parent={"database_id": db_id},
                            properties=properties
                        )
                        logger.debug(f"Created: {channel.get('name')}")

                    synced += 1

                except Exception as e:
                    logger.error(f"Failed to sync channel {channel.get('name')}: {e}")

        logger.info(f"Synced {synced} competitor channels")

    def _build_channel_properties(self, channel: Dict, category: str) -> Dict:
        """Build Notion properties for a channel."""
        views = channel.get("total_views", 0)
        videos = channel.get("video_count", 1)

        return {
            "Channel Name": {"title": [{"text": {"content": channel.get("name", "Unknown")}}]},
            "Channel ID": {"rich_text": [{"text": {"content": channel.get("channel_id", "")}}]},
            "Subscribers": {"number": channel.get("subscribers", 0)},
            "Total Views": {"number": views},
            "Video Count": {"number": videos},
            "Category": {"multi_select": [{"name": category}]},
            "Avg Views Per Video": {"number": views // videos if videos > 0 else 0},
            "Growth Notes": {"rich_text": [{"text": {"content": channel.get("notes", "")}}]},
            "Last Updated": {"date": {"start": datetime.now().isoformat()[:10]}},
        }

    def sync_top_videos(self):
        """Sync top videos data to Notion."""
        db_id = self.database_ids.get("top_videos")
        if not db_id:
            logger.error("No database ID for top_videos. Run --create-databases first.")
            return

        data = self._load_yaml_data("top_videos.yaml")
        if not data or "videos" not in data:
            logger.warning("No top videos data found")
            return

        synced = 0
        for video in data["videos"][:100]:  # Limit to top 100
            try:
                existing = self._find_by_property(
                    db_id, "Video ID", video.get("video_id", "")
                )

                properties = self._build_video_properties(video)

                if existing:
                    self.client.pages.update(
                        page_id=existing["id"],
                        properties=properties
                    )
                else:
                    self.client.pages.create(
                        parent={"database_id": db_id},
                        properties=properties
                    )

                synced += 1

            except Exception as e:
                logger.error(f"Failed to sync video {video.get('title', '')[:30]}: {e}")

        logger.info(f"Synced {synced} top videos")

    def _build_video_properties(self, video: Dict) -> Dict:
        """Build Notion properties for a video."""
        # Get first 10 tags for multi-select
        tags = video.get("tags", [])[:10]
        tag_options = [{"name": tag[:100]} for tag in tags if tag]  # Notion limit

        # Calculate engagement rate
        views = video.get("views", 1)
        likes = video.get("likes", 0)
        engagement = likes / views if views > 0 else 0

        # Parse publish date
        pub_date = video.get("publish_date", "")
        if pub_date:
            try:
                date_obj = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                pub_date = date_obj.strftime("%Y-%m-%d")
            except:
                pub_date = None

        properties = {
            "Video Title": {"title": [{"text": {"content": video.get("title", "Unknown")[:2000]}}]},
            "Video ID": {"rich_text": [{"text": {"content": video.get("video_id", "")}}]},
            "Channel": {"rich_text": [{"text": {"content": video.get("channel_title", "")[:2000]}}]},
            "Views": {"number": views},
            "Likes": {"number": likes},
            "Comments": {"number": video.get("comments", 0)},
            "Duration": {"rich_text": [{"text": {"content": video.get("duration", "")}}]},
            "Engagement Rate": {"number": engagement},
            "Category": {"multi_select": [{"name": cat} for cat in video.get("categories", [])[:5]]},
            "Why It Works": {"rich_text": [{"text": {"content": video.get("analysis", "")[:2000]}}]},
            "Title Pattern": {"rich_text": [{"text": {"content": video.get("title_pattern", "")[:2000]}}]},
        }

        if pub_date:
            properties["Publish Date"] = {"date": {"start": pub_date}}

        if tag_options:
            properties["Tags"] = {"multi_select": tag_options}

        return properties

    def sync_title_patterns(self):
        """Sync title patterns to Notion."""
        db_id = self.database_ids.get("title_patterns")
        if not db_id:
            logger.error("No database ID for title_patterns. Run --create-databases first.")
            return

        data = self._load_yaml_data("title_patterns.yaml")
        if not data or "patterns" not in data:
            logger.warning("No title pattern data found")
            return

        synced = 0
        for pattern in data["patterns"]:
            try:
                pattern_name = pattern.get("name", pattern.get("pattern", "Unknown"))
                existing = self._find_by_title(db_id, pattern_name)

                properties = self._build_pattern_properties(pattern)

                if existing:
                    self.client.pages.update(
                        page_id=existing["id"],
                        properties=properties
                    )
                else:
                    self.client.pages.create(
                        parent={"database_id": db_id},
                        properties=properties
                    )

                synced += 1

            except Exception as e:
                logger.error(f"Failed to sync pattern: {e}")

        logger.info(f"Synced {synced} title patterns")

    def _build_pattern_properties(self, pattern: Dict) -> Dict:
        """Build Notion properties for a title pattern."""
        examples = pattern.get("examples", [])
        examples_text = "\n".join(f"- {ex}" for ex in examples[:10])

        categories = pattern.get("categories", [])

        # Determine priority based on CTR
        ctr = pattern.get("avg_ctr", 0)
        if ctr >= 0.05:
            priority = "high"
        elif ctr >= 0.03:
            priority = "medium"
        else:
            priority = "low"

        return {
            "Pattern Name": {"title": [{"text": {"content": pattern.get("name", "Unknown")[:2000]}}]},
            "Pattern Template": {"rich_text": [{"text": {"content": pattern.get("pattern", "")[:2000]}}]},
            "Avg CTR Estimate": {"number": ctr},
            "Example Titles": {"rich_text": [{"text": {"content": examples_text[:2000]}}]},
            "Best For": {"multi_select": [{"name": cat} for cat in categories[:5]]},
            "Video Count": {"number": pattern.get("video_count", 0)},
            "Priority": {"select": {"name": priority}},
        }

    def sync_tag_clusters(self):
        """Sync tag clusters to Notion."""
        db_id = self.database_ids.get("tag_clusters")
        if not db_id:
            logger.error("No database ID for tag_clusters. Run --create-databases first.")
            return

        data = self._load_yaml_data("tag_clusters.yaml")
        if not data or "tags" not in data:
            logger.warning("No tag cluster data found")
            return

        synced = 0
        for tag_name, tag_data in list(data["tags"].items())[:200]:  # Limit
            try:
                existing = self._find_by_title(db_id, tag_name)

                properties = self._build_tag_properties(tag_name, tag_data)

                if existing:
                    self.client.pages.update(
                        page_id=existing["id"],
                        properties=properties
                    )
                else:
                    self.client.pages.create(
                        parent={"database_id": db_id},
                        properties=properties
                    )

                synced += 1

            except Exception as e:
                logger.error(f"Failed to sync tag {tag_name}: {e}")

        logger.info(f"Synced {synced} tag clusters")

    def _build_tag_properties(self, tag_name: str, tag_data: Dict) -> Dict:
        """Build Notion properties for a tag cluster."""
        # Determine volume level
        count = tag_data.get("video_count", 0)
        if count >= 50:
            volume = "high"
        elif count >= 20:
            volume = "medium"
        else:
            volume = "low"

        # Estimate competition (inverse of avg engagement in high-count tags)
        avg_eng = tag_data.get("avg_engagement", 0)
        if avg_eng >= 0.04:
            competition = "low"  # High engagement = low competition
        elif avg_eng >= 0.02:
            competition = "medium"
        else:
            competition = "high"

        related = tag_data.get("related_tags", [])
        related_text = ", ".join(related[:20])

        return {
            "Tag Name": {"title": [{"text": {"content": tag_name[:2000]}}]},
            "Search Volume": {"select": {"name": volume}},
            "Competition": {"select": {"name": competition}},
            "Category": {"multi_select": [{"name": cat} for cat in tag_data.get("categories", [])[:5]]},
            "Avg Engagement": {"number": avg_eng},
            "Video Count": {"number": count},
            "Related Tags": {"rich_text": [{"text": {"content": related_text[:2000]}}]},
        }

    def sync_our_channel_metrics(self):
        """Sync our channel metrics to Notion."""
        db_id = self.database_ids.get("our_channel_metrics")
        if not db_id:
            logger.error("No database ID for our_channel_metrics. Run --create-databases first.")
            return

        data = self._load_yaml_data("our_channel_metrics.yaml")
        if not data or "videos" not in data:
            logger.warning("No our channel metrics data found")
            return

        synced = 0
        for video in data["videos"]:
            try:
                existing = self._find_by_property(
                    db_id, "Video ID", video.get("video_id", "")
                )

                properties = self._build_our_video_properties(video)

                if existing:
                    self.client.pages.update(
                        page_id=existing["id"],
                        properties=properties
                    )
                else:
                    self.client.pages.create(
                        parent={"database_id": db_id},
                        properties=properties
                    )

                synced += 1

            except Exception as e:
                logger.error(f"Failed to sync our video {video.get('title', '')[:30]}: {e}")

        logger.info(f"Synced {synced} our channel videos")

    def _build_our_video_properties(self, video: Dict) -> Dict:
        """Build Notion properties for our channel video."""
        views = video.get("views", 1)
        likes = video.get("likes", 0)
        engagement = likes / views if views > 0 else 0

        improvements = video.get("improvements", [])
        improvements_text = "\n".join(f"- {imp}" for imp in improvements)

        pub_date = video.get("publish_date", "")
        if pub_date:
            try:
                date_obj = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                pub_date = date_obj.strftime("%Y-%m-%d")
            except:
                pub_date = None

        properties = {
            "Video Title": {"title": [{"text": {"content": video.get("title", "Unknown")[:2000]}}]},
            "Video ID": {"rich_text": [{"text": {"content": video.get("video_id", "")}}]},
            "Views": {"number": views},
            "Likes": {"number": likes},
            "Comments": {"number": video.get("comments", 0)},
            "Engagement Rate": {"number": engagement},
            "vs Benchmark": {"rich_text": [{"text": {"content": video.get("vs_benchmark", "")[:2000]}}]},
            "Improvements": {"rich_text": [{"text": {"content": improvements_text[:2000]}}]},
        }

        if pub_date:
            properties["Publish Date"] = {"date": {"start": pub_date}}

        if video.get("category"):
            properties["Category"] = {"select": {"name": video["category"]}}

        return properties

    def sync_seasonal_trends(self):
        """Sync seasonal trends to Notion."""
        db_id = self.database_ids.get("seasonal_trends")
        if not db_id:
            logger.error("No database ID for seasonal_trends. Run --create-databases first.")
            return

        data = self._load_yaml_data("seasonal_trends.yaml")
        if not data or "months" not in data:
            logger.warning("No seasonal trends data found")
            return

        synced = 0
        current_year = datetime.now().year

        for month_name, month_data in data["months"].items():
            try:
                # Create unique title with year
                title = f"{month_name.title()} {current_year}"
                existing = self._find_by_title(db_id, title)

                properties = self._build_seasonal_properties(title, month_name, month_data, current_year)

                if existing:
                    self.client.pages.update(
                        page_id=existing["id"],
                        properties=properties
                    )
                else:
                    self.client.pages.create(
                        parent={"database_id": db_id},
                        properties=properties
                    )

                synced += 1

            except Exception as e:
                logger.error(f"Failed to sync month {month_name}: {e}")

        logger.info(f"Synced {synced} seasonal trends")

    def _build_seasonal_properties(self, title: str, month: str, data: Dict, year: int) -> Dict:
        """Build Notion properties for seasonal trends."""
        # Format interest themes
        interest = data.get("interest_boost", {})
        interest_text = "\n".join(f"- {theme}: +{pct}%" for theme, pct in interest.items())

        topics = data.get("recommended_themes", [])

        return {
            "Month": {"title": [{"text": {"content": title}}]},
            "Year": {"number": year},
            "Interest Themes": {"rich_text": [{"text": {"content": interest_text[:2000]}}]},
            "Recommended Topics": {"multi_select": [{"name": t[:100]} for t in topics[:10]]},
            "Best Upload Days": {"rich_text": [{"text": {"content": data.get("best_upload_days", "")[:2000]}}]},
            "Video Count Sample": {"number": data.get("video_count", 0)},
            "Notes": {"rich_text": [{"text": {"content": data.get("notes", "")[:2000]}}]},
        }

    def _find_by_property(self, database_id: str, property_name: str, value: str) -> Optional[Dict]:
        """Find a page in database by a text property value."""
        if not value:
            return None

        try:
            response = self.client.databases.query(
                database_id=database_id,
                filter={
                    "property": property_name,
                    "rich_text": {"equals": value}
                },
                page_size=1
            )

            results = response.get("results", [])
            return results[0] if results else None

        except Exception as e:
            logger.debug(f"Query failed: {e}")
            return None

    def _find_by_title(self, database_id: str, title: str) -> Optional[Dict]:
        """Find a page in database by title."""
        if not title:
            return None

        try:
            response = self.client.databases.query(
                database_id=database_id,
                filter={
                    "property": "title",  # Notion uses "title" for title property queries
                    "title": {"equals": title}
                },
                page_size=1
            )

            results = response.get("results", [])
            return results[0] if results else None

        except Exception as e:
            logger.debug(f"Title query failed: {e}")
            return None

    def sync_all(self):
        """Sync all data to Notion databases."""
        logger.info("Starting full Notion sync...")

        self.sync_competitor_channels()
        self.sync_top_videos()
        self.sync_title_patterns()
        self.sync_tag_clusters()
        self.sync_our_channel_metrics()
        self.sync_seasonal_trends()

        logger.info("Notion sync complete!")

    def get_status(self) -> Dict[str, Any]:
        """Get sync status for all databases."""
        status = {
            "databases": {},
            "data_files": {},
            "last_sync": None
        }

        # Check database IDs
        for db_name in self.DATABASE_SCHEMAS.keys():
            db_id = self.database_ids.get(db_name)
            status["databases"][db_name] = {
                "id": db_id,
                "configured": bool(db_id)
            }

            if db_id:
                try:
                    response = self.client.databases.retrieve(database_id=db_id)
                    status["databases"][db_name]["title"] = "".join(
                        t.get("plain_text", "") for t in response.get("title", [])
                    )
                    status["databases"][db_name]["accessible"] = True
                except:
                    status["databases"][db_name]["accessible"] = False

        # Check data files
        data_files = [
            "competitor_channels.yaml",
            "top_videos.yaml",
            "title_patterns.yaml",
            "tag_clusters.yaml",
            "our_channel_metrics.yaml",
            "seasonal_trends.yaml"
        ]

        for filename in data_files:
            filepath = COMPETITOR_DATA_PATH / filename
            status["data_files"][filename] = {
                "exists": filepath.exists(),
                "size": filepath.stat().st_size if filepath.exists() else 0,
                "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                           if filepath.exists() else None
            }

        return status


def main():
    parser = argparse.ArgumentParser(
        description="Sync YouTube competitor data to Notion"
    )

    parser.add_argument(
        "--create-databases",
        action="store_true",
        help="Create all Notion databases (first time setup)"
    )
    parser.add_argument(
        "--parent-page",
        type=str,
        help="Parent page ID for database creation"
    )
    parser.add_argument(
        "--sync",
        type=str,
        choices=[
            "competitor_channels", "top_videos", "title_patterns",
            "tag_clusters", "our_channel_metrics", "seasonal_trends"
        ],
        help="Sync specific database"
    )
    parser.add_argument(
        "--sync-all",
        action="store_true",
        help="Sync all databases"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show sync status"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        syncer = NotionYouTubeSync()

        if args.create_databases:
            db_ids = syncer.create_databases(args.parent_page)
            print("\nCreated databases:")
            for name, db_id in db_ids.items():
                print(f"  {name}: {db_id}")
            print(f"\nDatabase IDs saved to {CONFIG_PATH}")
            print("Add these databases to your Notion workspace and share with integration.")

        elif args.sync:
            sync_method = getattr(syncer, f"sync_{args.sync}", None)
            if sync_method:
                sync_method()
            else:
                print(f"Unknown database: {args.sync}")

        elif args.sync_all:
            syncer.sync_all()

        elif args.status:
            status = syncer.get_status()
            print("\n=== Notion YouTube Sync Status ===\n")

            print("Databases:")
            for name, info in status["databases"].items():
                configured = "✓" if info["configured"] else "✗"
                accessible = "accessible" if info.get("accessible") else "not accessible"
                print(f"  {configured} {name}: {info.get('id', 'not configured')} ({accessible})")

            print("\nData Files:")
            for name, info in status["data_files"].items():
                exists = "✓" if info["exists"] else "✗"
                size = f"{info['size']:,} bytes" if info["exists"] else "missing"
                print(f"  {exists} {name}: {size}")

        else:
            parser.print_help()

    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
