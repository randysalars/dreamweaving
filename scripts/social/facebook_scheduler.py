#!/usr/bin/env python3
"""
Dreamweaver Facebook Group Scheduler

Automates posting to Facebook groups with proper spacing and tracking.

Philosophy:
- Link in first comment only (never in post body)
- 10-15 minute spacing between posts
- Track warm vs cold groups
- No manipulation, just service

Rules:
- Never spam (max 30 posts/day across all groups)
- Respect group rules
- Provide value before links
- Track engagement for optimization
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import yaml


class GroupTemperature(Enum):
    """How receptive the group has been"""
    COLD = "cold"           # New or unresponsive
    WARMING = "warming"     # Some engagement
    WARM = "warm"           # Good engagement
    HOT = "hot"             # High engagement, loyal


class PostType(Enum):
    """Types of Facebook posts"""
    VALUE_ONLY = "value_only"           # Pure value, no promotion
    SOFT_SHARE = "soft_share"           # Value + gentle share
    SESSION_SHARE = "session_share"     # Sharing a specific session
    SEASONAL = "seasonal"               # Holiday/seasonal content
    ENGAGEMENT = "engagement"           # Questions, discussions


@dataclass
class FacebookGroup:
    """A Facebook group we post to"""
    name: str
    group_id: str
    temperature: GroupTemperature = GroupTemperature.COLD
    category: str = "general"  # meditation, spiritual, sleep, etc.

    # Tracking
    posts_this_week: int = 0
    last_post_at: Optional[datetime] = None
    total_posts: int = 0
    total_engagements: int = 0  # likes + comments

    # Rules
    max_posts_per_week: int = 3
    allows_links: bool = True
    link_in_comments_only: bool = True

    # Notes
    notes: str = ""

    def can_post_today(self) -> Tuple[bool, str]:
        """Check if we can post to this group today"""
        if self.last_post_at:
            hours_since = (datetime.now() - self.last_post_at).total_seconds() / 3600
            if hours_since < 24:
                return False, f"Posted {hours_since:.1f} hours ago (need 24h gap)"

        if self.posts_this_week >= self.max_posts_per_week:
            return False, f"Hit weekly limit ({self.max_posts_per_week} posts)"

        return True, "Ready to post"

    def engagement_rate(self) -> float:
        """Calculate engagement rate"""
        if self.total_posts == 0:
            return 0.0
        return self.total_engagements / self.total_posts


@dataclass
class ScheduledPost:
    """A post scheduled for a group"""
    group: FacebookGroup
    post_type: PostType
    content: str
    first_comment: Optional[str] = None  # For links
    scheduled_time: Optional[datetime] = None

    # Tracking
    posted: bool = False
    posted_at: Optional[datetime] = None
    engagements: int = 0


class FacebookScheduler:
    """
    Manages Facebook group posting schedule.

    Key Rules:
    - Max 30 posts per day across all groups
    - 10-15 minute spacing between posts
    - Links ONLY in first comment
    - Never post same content to same group twice in a week
    """

    MAX_DAILY_POSTS = 30
    MIN_MINUTES_BETWEEN_POSTS = 10
    MAX_MINUTES_BETWEEN_POSTS = 15

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.groups_config_path = self.project_root / "config" / "facebook_groups.yaml"
        self.templates_path = self.project_root / "templates" / "social" / "facebook_posts.yaml"
        self.history_path = self.project_root / "data" / "facebook_history.json"

        self.groups: Dict[str, FacebookGroup] = {}
        self.scheduled_posts: List[ScheduledPost] = []
        self.posts_today = 0
        self.last_post_time: Optional[datetime] = None

        self._load_groups()
        self._load_history()

    def _load_groups(self):
        """Load groups from config"""
        if self.groups_config_path.exists():
            with open(self.groups_config_path) as f:
                config = yaml.safe_load(f) or {}

            for group_id, data in config.get("groups", {}).items():
                self.groups[group_id] = FacebookGroup(
                    name=data.get("name", group_id),
                    group_id=group_id,
                    temperature=GroupTemperature(data.get("temperature", "cold")),
                    category=data.get("category", "general"),
                    max_posts_per_week=data.get("max_posts_per_week", 3),
                    allows_links=data.get("allows_links", True),
                    link_in_comments_only=data.get("link_in_comments_only", True),
                    notes=data.get("notes", "")
                )

    def _load_history(self):
        """Load posting history"""
        if self.history_path.exists():
            with open(self.history_path) as f:
                history = json.load(f)

            # Update group stats from history
            for group_id, stats in history.get("group_stats", {}).items():
                if group_id in self.groups:
                    group = self.groups[group_id]
                    group.total_posts = stats.get("total_posts", 0)
                    group.total_engagements = stats.get("total_engagements", 0)

                    if stats.get("last_post_at"):
                        group.last_post_at = datetime.fromisoformat(stats["last_post_at"])

            # Count posts this week for each group
            week_ago = datetime.now() - timedelta(days=7)
            for post in history.get("posts", []):
                post_time = datetime.fromisoformat(post["posted_at"])
                if post_time > week_ago:
                    group_id = post.get("group_id")
                    if group_id in self.groups:
                        self.groups[group_id].posts_this_week += 1

            # Count posts today
            today = datetime.now().date()
            self.posts_today = sum(
                1 for post in history.get("posts", [])
                if datetime.fromisoformat(post["posted_at"]).date() == today
            )

    def _save_groups(self):
        """Save groups config"""
        config = {"groups": {}}
        for group_id, group in self.groups.items():
            config["groups"][group_id] = {
                "name": group.name,
                "temperature": group.temperature.value,
                "category": group.category,
                "max_posts_per_week": group.max_posts_per_week,
                "allows_links": group.allows_links,
                "link_in_comments_only": group.link_in_comments_only,
                "notes": group.notes
            }

        self.groups_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.groups_config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    def _save_history(self, posts: List[dict]):
        """Save posting history"""
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing or create new
        if self.history_path.exists():
            with open(self.history_path) as f:
                history = json.load(f)
        else:
            history = {"posts": [], "group_stats": {}}

        # Add new posts
        history["posts"].extend(posts)

        # Update group stats
        for group_id, group in self.groups.items():
            history["group_stats"][group_id] = {
                "total_posts": group.total_posts,
                "total_engagements": group.total_engagements,
                "last_post_at": group.last_post_at.isoformat() if group.last_post_at else None
            }

        with open(self.history_path, "w") as f:
            json.dump(history, f, indent=2, default=str)

    def add_group(
        self,
        name: str,
        group_id: str,
        category: str = "general",
        max_posts_per_week: int = 3
    ):
        """Add a new Facebook group to track"""
        self.groups[group_id] = FacebookGroup(
            name=name,
            group_id=group_id,
            category=category,
            max_posts_per_week=max_posts_per_week
        )
        self._save_groups()

    def get_available_groups(
        self,
        category: Optional[str] = None,
        min_temperature: Optional[GroupTemperature] = None
    ) -> List[FacebookGroup]:
        """Get groups that can receive posts today"""
        available = []

        for group in self.groups.values():
            can_post, _ = group.can_post_today()
            if not can_post:
                continue

            if category and group.category != category:
                continue

            if min_temperature:
                temp_order = [GroupTemperature.COLD, GroupTemperature.WARMING,
                              GroupTemperature.WARM, GroupTemperature.HOT]
                if temp_order.index(group.temperature) < temp_order.index(min_temperature):
                    continue

            available.append(group)

        return available

    def create_daily_schedule(
        self,
        post_templates: List[Dict],
        target_groups: Optional[List[str]] = None,
        max_posts: Optional[int] = None
    ) -> List[ScheduledPost]:
        """
        Create a day's posting schedule.

        Args:
            post_templates: List of content templates to use
            target_groups: Specific group IDs (or None for all available)
            max_posts: Maximum posts (defaults to MAX_DAILY_POSTS)

        Returns:
            List of scheduled posts with times
        """
        max_posts = min(max_posts or self.MAX_DAILY_POSTS, self.MAX_DAILY_POSTS)
        remaining_posts = max_posts - self.posts_today

        if remaining_posts <= 0:
            return []

        # Get available groups
        if target_groups:
            groups = [g for g in self.groups.values() if g.group_id in target_groups]
        else:
            groups = self.get_available_groups()

        if not groups:
            return []

        # Distribute posts across groups
        scheduled = []
        current_time = datetime.now()

        for i in range(min(remaining_posts, len(groups))):
            group = groups[i % len(groups)]
            template = post_templates[i % len(post_templates)]

            # Calculate posting time with proper spacing
            if scheduled:
                minutes_gap = random.randint(
                    self.MIN_MINUTES_BETWEEN_POSTS,
                    self.MAX_MINUTES_BETWEEN_POSTS
                )
                current_time = scheduled[-1].scheduled_time + timedelta(minutes=minutes_gap)

            # Create scheduled post
            post = ScheduledPost(
                group=group,
                post_type=PostType(template.get("type", "value_only")),
                content=template.get("content", ""),
                first_comment=template.get("first_comment"),
                scheduled_time=current_time
            )
            scheduled.append(post)

        self.scheduled_posts = scheduled
        return scheduled

    def get_schedule_summary(self) -> Dict:
        """Get summary of current schedule"""
        return {
            "posts_today": self.posts_today,
            "remaining_today": self.MAX_DAILY_POSTS - self.posts_today,
            "scheduled_count": len(self.scheduled_posts),
            "groups_available": len(self.get_available_groups()),
            "total_groups": len(self.groups),
            "next_post": (
                self.scheduled_posts[0].scheduled_time.isoformat()
                if self.scheduled_posts else None
            )
        }

    def record_post(
        self,
        group_id: str,
        post_type: PostType,
        content: str,
        engagements: int = 0
    ):
        """Record that a post was made"""
        if group_id not in self.groups:
            return

        group = self.groups[group_id]
        group.last_post_at = datetime.now()
        group.total_posts += 1
        group.posts_this_week += 1

        if engagements > 0:
            group.total_engagements += engagements
            # Update temperature based on engagement
            self._update_temperature(group)

        self.posts_today += 1

        # Save to history
        self._save_history([{
            "group_id": group_id,
            "post_type": post_type.value,
            "content_preview": content[:100],
            "posted_at": datetime.now().isoformat(),
            "engagements": engagements
        }])

        self._save_groups()

    def _update_temperature(self, group: FacebookGroup):
        """Update group temperature based on engagement"""
        rate = group.engagement_rate()

        if rate >= 10:
            group.temperature = GroupTemperature.HOT
        elif rate >= 5:
            group.temperature = GroupTemperature.WARM
        elif rate >= 2:
            group.temperature = GroupTemperature.WARMING
        else:
            group.temperature = GroupTemperature.COLD

    def get_group_stats(self) -> Dict:
        """Get statistics for all groups"""
        stats = {
            "by_temperature": {},
            "by_category": {},
            "top_performing": [],
            "needs_attention": []
        }

        # Group by temperature
        for temp in GroupTemperature:
            groups = [g for g in self.groups.values() if g.temperature == temp]
            stats["by_temperature"][temp.value] = len(groups)

        # Group by category
        categories = set(g.category for g in self.groups.values())
        for cat in categories:
            groups = [g for g in self.groups.values() if g.category == cat]
            stats["by_category"][cat] = len(groups)

        # Top performing (by engagement rate)
        sorted_groups = sorted(
            self.groups.values(),
            key=lambda g: g.engagement_rate(),
            reverse=True
        )
        stats["top_performing"] = [
            {"name": g.name, "rate": g.engagement_rate()}
            for g in sorted_groups[:5]
        ]

        # Needs attention (cold groups with posts)
        cold_with_posts = [
            g for g in self.groups.values()
            if g.temperature == GroupTemperature.COLD and g.total_posts > 5
        ]
        stats["needs_attention"] = [g.name for g in cold_with_posts]

        return stats


def load_post_templates() -> List[Dict]:
    """Load post templates from config"""
    templates_path = Path(__file__).parent.parent.parent / "templates" / "social" / "facebook_posts.yaml"

    if templates_path.exists():
        with open(templates_path) as f:
            config = yaml.safe_load(f) or {}
        return config.get("templates", [])

    return []


def main():
    """CLI for Facebook scheduler"""
    import argparse

    parser = argparse.ArgumentParser(description="Dreamweaver Facebook Scheduler")
    parser.add_argument("--status", action="store_true", help="Show schedule status")
    parser.add_argument("--groups", action="store_true", help="List all groups")
    parser.add_argument("--stats", action="store_true", help="Show group statistics")
    parser.add_argument("--schedule", action="store_true", help="Create daily schedule")
    parser.add_argument("--add-group", type=str, help="Add a new group (name)")
    parser.add_argument("--group-id", type=str, help="Group ID for new group")
    parser.add_argument("--category", type=str, default="general", help="Group category")

    args = parser.parse_args()

    scheduler = FacebookScheduler()

    if args.status:
        summary = scheduler.get_schedule_summary()
        print("\n=== Facebook Schedule Status ===")
        print(f"Posts today: {summary['posts_today']} / {scheduler.MAX_DAILY_POSTS}")
        print(f"Remaining: {summary['remaining_today']}")
        print(f"Groups available: {summary['groups_available']} / {summary['total_groups']}")
        if summary['next_post']:
            print(f"Next scheduled: {summary['next_post']}")

    elif args.groups:
        print("\n=== Facebook Groups ===")
        for group in scheduler.groups.values():
            can_post, reason = group.can_post_today()
            status = "Ready" if can_post else reason
            print(f"  {group.name}")
            print(f"    Temperature: {group.temperature.value}")
            print(f"    Category: {group.category}")
            print(f"    Status: {status}")
            print(f"    Engagement rate: {group.engagement_rate():.1f}")
            print()

    elif args.stats:
        stats = scheduler.get_group_stats()
        print("\n=== Group Statistics ===")
        print("\nBy Temperature:")
        for temp, count in stats["by_temperature"].items():
            print(f"  {temp}: {count}")
        print("\nBy Category:")
        for cat, count in stats["by_category"].items():
            print(f"  {cat}: {count}")
        print("\nTop Performing:")
        for group in stats["top_performing"]:
            print(f"  {group['name']}: {group['rate']:.1f} engagements/post")
        if stats["needs_attention"]:
            print("\nNeeds Attention (cold despite activity):")
            for name in stats["needs_attention"]:
                print(f"  - {name}")

    elif args.schedule:
        templates = load_post_templates()
        if not templates:
            print("No post templates found. Create templates/social/facebook_posts.yaml")
            return

        schedule = scheduler.create_daily_schedule(templates)
        print(f"\n=== Created Schedule ({len(schedule)} posts) ===")
        for post in schedule:
            print(f"  {post.scheduled_time.strftime('%H:%M')} - {post.group.name}")
            print(f"    Type: {post.post_type.value}")
            print(f"    Preview: {post.content[:60]}...")
            print()

    elif args.add_group and args.group_id:
        scheduler.add_group(
            name=args.add_group,
            group_id=args.group_id,
            category=args.category
        )
        print(f"Added group: {args.add_group}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
