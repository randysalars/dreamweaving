#!/usr/bin/env python3
"""
Dreamweaver Segment Manager

Quiet segmentation by:
- Interests: light, rest, faith, imagination
- Arrival source: gift, article, youtube
- Engagement level: replier, engaged, moderate, passive

Philosophy:
- Never announce segmentation
- Never change core tone based on segment
- Segmentation shapes what they receive, not how they're treated
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

from .email_scheduler import EmailScheduler, Subscriber


class Interest(Enum):
    """Content interest categories"""
    LIGHT = "light"           # Transformation, awakening, hope
    REST = "rest"             # Peace, relaxation, sleep
    FAITH = "faith"           # Spiritual, religious, sacred
    IMAGINATION = "imagination"  # Creative, mythic, visionary


class ArrivalSource(Enum):
    """How subscriber found Dreamweaver"""
    ARTICLE = "article"       # Via blog/website article
    YOUTUBE = "youtube"       # Via YouTube content
    GIFT = "gift"             # Received as gift
    DIRECT = "direct"         # Direct subscription
    SOCIAL = "social"         # Via social media


class EngagementLevel(Enum):
    """Subscriber engagement classification"""
    REPLIER = "replier"       # Has replied (most valuable)
    ENGAGED = "engaged"       # >70% open rate
    MODERATE = "moderate"     # 30-70% open rate
    PASSIVE = "passive"       # <30% open rate or inactive


@dataclass
class Segment:
    """A segment definition"""
    name: str
    description: str
    filters: Dict
    subscribers: List[str] = None

    def __post_init__(self):
        if self.subscribers is None:
            self.subscribers = []


class SegmentManager:
    """
    Manages subscriber segments for Dreamweaver.

    Key Rules:
    - Segmentation is invisible to subscribers
    - Tone remains consistent across all segments
    - Segments influence content, not voice
    """

    # Pre-defined segments
    BUILT_IN_SEGMENTS = {
        "repliers": {
            "description": "Subscribers who have replied (most valuable)",
            "filters": {"engagement": "replier"}
        },
        "engaged": {
            "description": "Highly engaged readers (>70% opens)",
            "filters": {"engagement": "engaged"}
        },
        "seekers_of_rest": {
            "description": "Interested in rest, peace, sleep content",
            "filters": {"interests": ["rest"]}
        },
        "seekers_of_light": {
            "description": "Interested in transformation, hope",
            "filters": {"interests": ["light"]}
        },
        "faith_oriented": {
            "description": "Interested in spiritual/faith content",
            "filters": {"interests": ["faith"]}
        },
        "creative_seekers": {
            "description": "Interested in imagination, myth",
            "filters": {"interests": ["imagination"]}
        },
        "gift_recipients": {
            "description": "Originally received Dreamweaver as gift",
            "filters": {"source": "gift"}
        },
        "youtube_arrivals": {
            "description": "Found us via YouTube",
            "filters": {"source": "youtube"}
        },
        "article_readers": {
            "description": "Found us via articles",
            "filters": {"source": "article"}
        },
        "new_subscribers": {
            "description": "Subscribed in last 30 days",
            "filters": {"days_since_subscribe": 30}
        },
        "long_term": {
            "description": "Subscribed over 6 months ago",
            "filters": {"min_days_subscribed": 180}
        },
        "returners": {
            "description": "Returned after absence (opened after 60+ days)",
            "filters": {"returned_after_days": 60}
        },
        "purchase_ready": {
            "description": "Shows readiness signals for purchase",
            "filters": {"readiness_score": 0.7}
        }
    }

    def __init__(self, scheduler: Optional[EmailScheduler] = None):
        """Initialize segment manager"""
        self.scheduler = scheduler or EmailScheduler()
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.custom_segments_path = self.project_root / "config" / "custom_segments.yaml"

    def get_segment(self, segment_name: str) -> List[str]:
        """
        Get list of subscribers in a segment.

        Args:
            segment_name: Name of segment (built-in or custom)

        Returns:
            List of email addresses
        """
        if segment_name in self.BUILT_IN_SEGMENTS:
            filters = self.BUILT_IN_SEGMENTS[segment_name]["filters"]
            return self._apply_filters(filters)
        else:
            # Check custom segments
            custom = self._load_custom_segments()
            if segment_name in custom:
                return self._apply_filters(custom[segment_name]["filters"])

        return []

    def _apply_filters(self, filters: Dict) -> List[str]:
        """Apply filters to get matching subscribers"""
        matching = []
        now = datetime.now()

        for email, subscriber in self.scheduler.subscribers.items():
            if self._matches_filters(subscriber, filters, now):
                matching.append(email)

        return matching

    def _matches_filters(
        self,
        subscriber: Subscriber,
        filters: Dict,
        now: datetime
    ) -> bool:
        """Check if subscriber matches all filters"""

        # Engagement filter
        if "engagement" in filters:
            if subscriber.engagement_level != filters["engagement"]:
                return False

        # Interests filter (any match)
        if "interests" in filters:
            if not any(i in subscriber.interests for i in filters["interests"]):
                return False

        # Source filter
        if "source" in filters:
            if subscriber.source != filters["source"]:
                return False

        # Days since subscribe (new subscribers)
        if "days_since_subscribe" in filters:
            days = (now - subscriber.subscribed_at).days
            if days > filters["days_since_subscribe"]:
                return False

        # Min days subscribed (long-term)
        if "min_days_subscribed" in filters:
            days = (now - subscriber.subscribed_at).days
            if days < filters["min_days_subscribed"]:
                return False

        # Returned after absence
        if "returned_after_days" in filters:
            if subscriber.last_open_at and subscriber.last_email_at:
                gap = (subscriber.last_open_at - subscriber.last_email_at).days
                if gap < filters["returned_after_days"]:
                    return False
            else:
                return False

        # Readiness score
        if "readiness_score" in filters:
            score = self.calculate_readiness_score(subscriber)
            if score < filters["readiness_score"]:
                return False

        return True

    def calculate_readiness_score(self, subscriber: Subscriber) -> float:
        """
        Calculate purchase readiness score.

        Signals (from strategy docs):
        - Multiple email opens (4-6)
        - Replies (huge signal)
        - Return after absence
        - Long subscription duration
        - Previous purchases

        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.0

        # Email opens (up to 0.3)
        if subscriber.emails_received > 0:
            open_rate = subscriber.emails_opened / subscriber.emails_received
            score += min(open_rate * 0.4, 0.3)

        # Replies (huge signal - up to 0.3)
        if subscriber.replies > 0:
            score += min(subscriber.replies * 0.15, 0.3)

        # Subscription duration (up to 0.2)
        days_subscribed = (datetime.now() - subscriber.subscribed_at).days
        if days_subscribed > 180:  # 6+ months
            score += 0.2
        elif days_subscribed > 90:  # 3+ months
            score += 0.15
        elif days_subscribed > 30:  # 1+ month
            score += 0.1

        # Previous purchases (up to 0.2)
        if subscriber.purchases > 0:
            score += min(subscriber.purchases * 0.1, 0.2)

        return min(score, 1.0)

    def tag_subscriber(
        self,
        email: str,
        tags: List[str],
        remove: bool = False
    ):
        """
        Add or remove tags from subscriber.

        Tags are used for quiet segmentation.
        """
        if email not in self.scheduler.subscribers:
            return

        subscriber = self.scheduler.subscribers[email]

        if remove:
            subscriber.tags = [t for t in subscriber.tags if t not in tags]
        else:
            for tag in tags:
                if tag not in subscriber.tags:
                    subscriber.tags.append(tag)

        self.scheduler._save_subscribers()

    def update_interests(
        self,
        email: str,
        interests: List[str]
    ):
        """
        Update subscriber interests based on behavior.

        Interests are inferred, not asked.
        """
        if email not in self.scheduler.subscribers:
            return

        subscriber = self.scheduler.subscribers[email]

        for interest in interests:
            if interest not in subscriber.interests:
                subscriber.interests.append(interest)

        self.scheduler._save_subscribers()

    def get_segment_stats(self) -> Dict:
        """Get statistics for all segments"""
        stats = {}

        for name, config in self.BUILT_IN_SEGMENTS.items():
            members = self.get_segment(name)
            stats[name] = {
                "description": config["description"],
                "count": len(members)
            }

        return stats

    def suggest_content_for_segment(
        self,
        segment_name: str
    ) -> Dict:
        """
        Suggest content themes for a segment.

        Note: This shapes content, not voice.
        Tone remains Dreamweaver-consistent always.
        """
        suggestions = {
            "repliers": {
                "themes": ["deeper exploration", "personal journey", "advanced practices"],
                "tone_note": "Same gentle tone, can explore deeper themes"
            },
            "seekers_of_rest": {
                "themes": ["sleep journeys", "peace meditations", "letting go"],
                "tone_note": "Emphasize rest and permission"
            },
            "seekers_of_light": {
                "themes": ["transformation", "hope", "renewal"],
                "tone_note": "Hopeful but not pushy"
            },
            "faith_oriented": {
                "themes": ["sacred journeys", "spiritual practices", "devotional"],
                "tone_note": "Reverent, non-denominational"
            },
            "creative_seekers": {
                "themes": ["mythic journeys", "imagination", "creative flow"],
                "tone_note": "Evocative imagery, symbolic language"
            },
            "gift_recipients": {
                "themes": ["welcome", "gentle introduction", "no pressure"],
                "tone_note": "Extra gentle, they didn't seek us out"
            },
            "new_subscribers": {
                "themes": ["foundation", "what we're about", "slow introduction"],
                "tone_note": "Build trust first, no selling"
            },
            "purchase_ready": {
                "themes": ["seasonal offerings", "gentle invitations"],
                "tone_note": "Still gentle, but invitation is appropriate"
            }
        }

        return suggestions.get(segment_name, {
            "themes": ["general correspondence"],
            "tone_note": "Standard Dreamweaver voice"
        })

    def _load_custom_segments(self) -> Dict:
        """Load custom segment definitions"""
        if self.custom_segments_path.exists():
            import yaml
            with open(self.custom_segments_path) as f:
                return yaml.safe_load(f) or {}
        return {}


def main():
    """CLI for segment manager"""
    import argparse

    parser = argparse.ArgumentParser(description="Dreamweaver Segment Manager")
    parser.add_argument("--list", action="store_true", help="List all segments")
    parser.add_argument("--get", type=str, help="Get subscribers in segment")
    parser.add_argument("--stats", action="store_true", help="Show segment statistics")
    parser.add_argument("--suggest", type=str, help="Get content suggestions for segment")

    args = parser.parse_args()

    manager = SegmentManager()

    if args.list:
        print("\n=== Available Segments ===")
        for name, config in manager.BUILT_IN_SEGMENTS.items():
            print(f"  {name}: {config['description']}")

    elif args.get:
        members = manager.get_segment(args.get)
        print(f"\n=== {args.get} ({len(members)} members) ===")
        for email in members[:20]:
            print(f"  - {email}")
        if len(members) > 20:
            print(f"  ... and {len(members) - 20} more")

    elif args.stats:
        stats = manager.get_segment_stats()
        print("\n=== Segment Statistics ===")
        for name, data in stats.items():
            print(f"  {name}: {data['count']} ({data['description']})")

    elif args.suggest:
        suggestions = manager.suggest_content_for_segment(args.suggest)
        print(f"\n=== Content Suggestions for {args.suggest} ===")
        print(f"Themes: {', '.join(suggestions.get('themes', []))}")
        print(f"Tone Note: {suggestions.get('tone_note', 'Standard')}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
