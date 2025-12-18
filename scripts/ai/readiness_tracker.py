#!/usr/bin/env python3
"""
Dreamweaver Readiness Tracker

Tracks purchase readiness signals without manipulation.

Philosophy:
- Track signals, never manufacture urgency
- Readiness emerges naturally over time
- Trust first, offering second
- 6+ months of trust before any selling

Readiness Signals (from strategy):
- Multiple email opens (4-6)
- Replies to emails (huge signal)
- Return after absence
- Long subscription duration
- Scroll depth on articles
- Repeat visits to same content
- Previous purchases

Anti-Signals (do NOT sell to):
- New subscribers (<30 days)
- Low engagement (<30% open rate)
- No replies ever
- Never opened an email
- Unsubscribed and re-subscribed (respect their hesitation)
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import yaml


class ReadinessStage(Enum):
    """Purchase readiness stages"""
    NOT_READY = "not_ready"           # Trust building phase
    EARLY_SIGNALS = "early_signals"   # Some positive engagement
    WARMING = "warming"               # Multiple positive signals
    READY = "ready"                   # Strong signals, offer appropriate
    LOYAL = "loyal"                   # Previous purchaser, high trust


@dataclass
class EngagementEvent:
    """A single engagement event"""
    event_type: str  # open, click, reply, visit, scroll, purchase
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)


@dataclass
class SubscriberProfile:
    """Complete profile for readiness analysis"""
    email: str
    subscribed_at: datetime

    # Email engagement
    emails_received: int = 0
    emails_opened: int = 0
    email_clicks: int = 0
    replies: int = 0

    # Website engagement
    article_visits: int = 0
    scroll_depths: List[float] = field(default_factory=list)  # 0-100%
    repeat_visits: int = 0
    youtube_clicks: int = 0

    # Purchase history
    purchases: int = 0
    total_spent: float = 0.0
    last_purchase_at: Optional[datetime] = None

    # Engagement patterns
    last_email_open: Optional[datetime] = None
    last_article_visit: Optional[datetime] = None
    returned_after_absence: bool = False
    absence_days: int = 0

    # Computed
    readiness_stage: ReadinessStage = ReadinessStage.NOT_READY
    readiness_score: float = 0.0

    # Events history
    events: List[EngagementEvent] = field(default_factory=list)


class ReadinessTracker:
    """
    Tracks subscriber readiness for purchase.

    Key Principles:
    - Never sell to someone not ready
    - Trust takes 6+ months to build
    - Replies are the strongest signal
    - Return after absence = high intent
    """

    # Minimum trust thresholds
    MIN_DAYS_FOR_OFFER = 180  # 6 months
    MIN_OPENS_FOR_OFFER = 4
    REPLY_WEIGHT = 3.0  # Replies count 3x

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_path = self.project_root / "data" / "readiness_data.json"
        self.profiles: Dict[str, SubscriberProfile] = {}
        self._load_data()

    def _load_data(self):
        """Load subscriber profiles"""
        if self.data_path.exists():
            with open(self.data_path) as f:
                data = json.load(f)

            for email, profile_data in data.get("profiles", {}).items():
                self.profiles[email] = SubscriberProfile(
                    email=email,
                    subscribed_at=datetime.fromisoformat(profile_data["subscribed_at"]),
                    emails_received=profile_data.get("emails_received", 0),
                    emails_opened=profile_data.get("emails_opened", 0),
                    email_clicks=profile_data.get("email_clicks", 0),
                    replies=profile_data.get("replies", 0),
                    article_visits=profile_data.get("article_visits", 0),
                    scroll_depths=profile_data.get("scroll_depths", []),
                    repeat_visits=profile_data.get("repeat_visits", 0),
                    youtube_clicks=profile_data.get("youtube_clicks", 0),
                    purchases=profile_data.get("purchases", 0),
                    total_spent=profile_data.get("total_spent", 0.0),
                    last_purchase_at=(
                        datetime.fromisoformat(profile_data["last_purchase_at"])
                        if profile_data.get("last_purchase_at") else None
                    ),
                    last_email_open=(
                        datetime.fromisoformat(profile_data["last_email_open"])
                        if profile_data.get("last_email_open") else None
                    ),
                    last_article_visit=(
                        datetime.fromisoformat(profile_data["last_article_visit"])
                        if profile_data.get("last_article_visit") else None
                    ),
                    returned_after_absence=profile_data.get("returned_after_absence", False),
                    absence_days=profile_data.get("absence_days", 0),
                    readiness_stage=ReadinessStage(profile_data.get("readiness_stage", "not_ready")),
                    readiness_score=profile_data.get("readiness_score", 0.0)
                )

    def _save_data(self):
        """Save subscriber profiles"""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

        data = {"profiles": {}}
        for email, profile in self.profiles.items():
            data["profiles"][email] = {
                "subscribed_at": profile.subscribed_at.isoformat(),
                "emails_received": profile.emails_received,
                "emails_opened": profile.emails_opened,
                "email_clicks": profile.email_clicks,
                "replies": profile.replies,
                "article_visits": profile.article_visits,
                "scroll_depths": profile.scroll_depths,
                "repeat_visits": profile.repeat_visits,
                "youtube_clicks": profile.youtube_clicks,
                "purchases": profile.purchases,
                "total_spent": profile.total_spent,
                "last_purchase_at": (
                    profile.last_purchase_at.isoformat()
                    if profile.last_purchase_at else None
                ),
                "last_email_open": (
                    profile.last_email_open.isoformat()
                    if profile.last_email_open else None
                ),
                "last_article_visit": (
                    profile.last_article_visit.isoformat()
                    if profile.last_article_visit else None
                ),
                "returned_after_absence": profile.returned_after_absence,
                "absence_days": profile.absence_days,
                "readiness_stage": profile.readiness_stage.value,
                "readiness_score": profile.readiness_score
            }

        with open(self.data_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def get_or_create_profile(
        self,
        email: str,
        subscribed_at: Optional[datetime] = None
    ) -> SubscriberProfile:
        """Get existing profile or create new one"""
        if email not in self.profiles:
            self.profiles[email] = SubscriberProfile(
                email=email,
                subscribed_at=subscribed_at or datetime.now()
            )
            self._save_data()

        return self.profiles[email]

    def record_event(
        self,
        email: str,
        event_type: str,
        metadata: Optional[Dict] = None
    ):
        """
        Record an engagement event.

        Event types:
        - email_open
        - email_click
        - email_reply
        - article_visit
        - article_scroll (metadata: {depth: 0-100})
        - youtube_click
        - purchase (metadata: {amount: float})
        """
        profile = self.get_or_create_profile(email)
        now = datetime.now()

        # Record the event
        profile.events.append(EngagementEvent(
            event_type=event_type,
            timestamp=now,
            metadata=metadata or {}
        ))

        # Update profile based on event type
        if event_type == "email_open":
            profile.emails_opened += 1
            self._check_return_after_absence(profile, now)
            profile.last_email_open = now

        elif event_type == "email_click":
            profile.email_clicks += 1

        elif event_type == "email_reply":
            profile.replies += 1

        elif event_type == "article_visit":
            profile.article_visits += 1
            self._check_repeat_visit(profile, now)
            profile.last_article_visit = now

        elif event_type == "article_scroll":
            depth = (metadata or {}).get("depth", 0)
            profile.scroll_depths.append(depth)

        elif event_type == "youtube_click":
            profile.youtube_clicks += 1

        elif event_type == "purchase":
            amount = (metadata or {}).get("amount", 0)
            profile.purchases += 1
            profile.total_spent += amount
            profile.last_purchase_at = now

        # Recalculate readiness
        self._calculate_readiness(profile)
        self._save_data()

    def _check_return_after_absence(
        self,
        profile: SubscriberProfile,
        now: datetime
    ):
        """Check if this is a return after absence"""
        if profile.last_email_open:
            days_since = (now - profile.last_email_open).days
            if days_since >= 60:
                profile.returned_after_absence = True
                profile.absence_days = days_since

    def _check_repeat_visit(
        self,
        profile: SubscriberProfile,
        now: datetime
    ):
        """Check if this is a repeat visit"""
        if profile.last_article_visit:
            # Same day visits count as repeats
            if now.date() == profile.last_article_visit.date():
                profile.repeat_visits += 1

    def _calculate_readiness(self, profile: SubscriberProfile):
        """
        Calculate readiness score and stage.

        Scoring:
        - Days subscribed: up to 20 points (max at 180 days)
        - Email opens: up to 20 points (max at 10 opens)
        - Replies: up to 30 points (3 points each, max 10)
        - Return after absence: 15 points
        - Deep scroll (>70%): 5 points
        - Previous purchase: 10 points

        Stage thresholds:
        - NOT_READY: <30 points or <30 days
        - EARLY_SIGNALS: 30-50 points
        - WARMING: 50-70 points
        - READY: 70+ points AND 180+ days
        - LOYAL: Previous purchaser
        """
        score = 0.0
        now = datetime.now()
        days_subscribed = (now - profile.subscribed_at).days

        # Days subscribed (up to 20 points)
        score += min(days_subscribed / 9, 20)  # 180 days = 20 points

        # Email opens (up to 20 points)
        score += min(profile.emails_opened * 2, 20)

        # Replies (up to 30 points) - weighted heavily
        score += min(profile.replies * self.REPLY_WEIGHT * 3, 30)

        # Return after absence (15 points)
        if profile.returned_after_absence:
            score += 15

        # Deep scroll engagement (5 points)
        deep_scrolls = sum(1 for d in profile.scroll_depths if d > 70)
        if deep_scrolls > 0:
            score += min(deep_scrolls, 5)

        # Previous purchase (10 points)
        if profile.purchases > 0:
            score += 10

        profile.readiness_score = min(score, 100)

        # Determine stage
        if profile.purchases > 0:
            profile.readiness_stage = ReadinessStage.LOYAL
        elif score >= 70 and days_subscribed >= self.MIN_DAYS_FOR_OFFER:
            profile.readiness_stage = ReadinessStage.READY
        elif score >= 50:
            profile.readiness_stage = ReadinessStage.WARMING
        elif score >= 30:
            profile.readiness_stage = ReadinessStage.EARLY_SIGNALS
        else:
            profile.readiness_stage = ReadinessStage.NOT_READY

    def can_send_offer(self, email: str) -> Tuple[bool, str]:
        """
        Check if we can ethically send an offer to this subscriber.

        Returns:
            (can_send, reason)
        """
        if email not in self.profiles:
            return False, "Unknown subscriber"

        profile = self.profiles[email]
        now = datetime.now()
        days_subscribed = (now - profile.subscribed_at).days

        # Hard rules - never violate
        if days_subscribed < self.MIN_DAYS_FOR_OFFER:
            remaining = self.MIN_DAYS_FOR_OFFER - days_subscribed
            return False, f"Trust building phase ({remaining} days remaining)"

        if profile.emails_opened < self.MIN_OPENS_FOR_OFFER:
            return False, f"Need {self.MIN_OPENS_FOR_OFFER}+ email opens (has {profile.emails_opened})"

        # Check readiness stage
        if profile.readiness_stage in [ReadinessStage.NOT_READY, ReadinessStage.EARLY_SIGNALS]:
            return False, f"Not ready (stage: {profile.readiness_stage.value})"

        # Ready to receive offer
        if profile.readiness_stage == ReadinessStage.LOYAL:
            return True, "Loyal customer - seasonal offers welcome"

        if profile.readiness_stage == ReadinessStage.READY:
            return True, "Strong readiness signals - gentle offer appropriate"

        if profile.readiness_stage == ReadinessStage.WARMING:
            return True, "Warming - soft mention only, not direct offer"

        return False, "Unknown state"

    def get_ready_subscribers(
        self,
        min_stage: ReadinessStage = ReadinessStage.WARMING
    ) -> List[SubscriberProfile]:
        """Get subscribers at or above a readiness stage"""
        stage_order = [
            ReadinessStage.NOT_READY,
            ReadinessStage.EARLY_SIGNALS,
            ReadinessStage.WARMING,
            ReadinessStage.READY,
            ReadinessStage.LOYAL
        ]

        min_index = stage_order.index(min_stage)

        return [
            profile for profile in self.profiles.values()
            if stage_order.index(profile.readiness_stage) >= min_index
        ]

    def get_insights(self) -> Dict:
        """Get insights about subscriber readiness"""
        total = len(self.profiles)
        if total == 0:
            return {"total": 0}

        # Count by stage
        by_stage = {}
        for stage in ReadinessStage:
            count = sum(
                1 for p in self.profiles.values()
                if p.readiness_stage == stage
            )
            by_stage[stage.value] = count

        # Calculate averages
        avg_score = sum(p.readiness_score for p in self.profiles.values()) / total
        avg_opens = sum(p.emails_opened for p in self.profiles.values()) / total
        total_replies = sum(p.replies for p in self.profiles.values())

        # Find top signals
        with_replies = sum(1 for p in self.profiles.values() if p.replies > 0)
        returned = sum(1 for p in self.profiles.values() if p.returned_after_absence)
        purchasers = sum(1 for p in self.profiles.values() if p.purchases > 0)

        return {
            "total": total,
            "by_stage": by_stage,
            "average_readiness_score": round(avg_score, 1),
            "average_email_opens": round(avg_opens, 1),
            "total_replies": total_replies,
            "subscribers_who_replied": with_replies,
            "returned_after_absence": returned,
            "previous_purchasers": purchasers,
            "ready_for_offer": by_stage.get("ready", 0) + by_stage.get("loyal", 0)
        }

    def get_subscriber_journey(self, email: str) -> Optional[Dict]:
        """Get detailed journey information for a subscriber"""
        if email not in self.profiles:
            return None

        profile = self.profiles[email]
        now = datetime.now()
        days_subscribed = (now - profile.subscribed_at).days

        can_offer, reason = self.can_send_offer(email)

        return {
            "email": email,
            "subscribed_at": profile.subscribed_at.isoformat(),
            "days_subscribed": days_subscribed,
            "readiness_stage": profile.readiness_stage.value,
            "readiness_score": round(profile.readiness_score, 1),
            "can_receive_offer": can_offer,
            "offer_reason": reason,
            "engagement": {
                "emails_opened": profile.emails_opened,
                "email_clicks": profile.email_clicks,
                "replies": profile.replies,
                "article_visits": profile.article_visits,
                "youtube_clicks": profile.youtube_clicks,
                "avg_scroll_depth": (
                    round(sum(profile.scroll_depths) / len(profile.scroll_depths), 1)
                    if profile.scroll_depths else 0
                )
            },
            "signals": {
                "returned_after_absence": profile.returned_after_absence,
                "absence_days": profile.absence_days,
                "has_replied": profile.replies > 0,
                "previous_purchaser": profile.purchases > 0
            },
            "purchases": {
                "count": profile.purchases,
                "total_spent": profile.total_spent,
                "last_purchase": (
                    profile.last_purchase_at.isoformat()
                    if profile.last_purchase_at else None
                )
            }
        }


def main():
    """CLI for readiness tracker"""
    import argparse

    parser = argparse.ArgumentParser(description="Dreamweaver Readiness Tracker")
    parser.add_argument("--insights", action="store_true", help="Show readiness insights")
    parser.add_argument("--ready", action="store_true", help="List subscribers ready for offers")
    parser.add_argument("--journey", type=str, help="Show journey for email address")
    parser.add_argument("--check", type=str, help="Check if we can send offer to email")

    args = parser.parse_args()

    tracker = ReadinessTracker()

    if args.insights:
        insights = tracker.get_insights()
        print("\n=== Readiness Insights ===")
        print(f"Total subscribers: {insights['total']}")
        print(f"\nBy Stage:")
        for stage, count in insights.get("by_stage", {}).items():
            pct = (count / insights['total'] * 100) if insights['total'] > 0 else 0
            print(f"  {stage}: {count} ({pct:.1f}%)")
        print(f"\nEngagement:")
        print(f"  Average readiness score: {insights.get('average_readiness_score', 0)}")
        print(f"  Average email opens: {insights.get('average_email_opens', 0)}")
        print(f"  Total replies received: {insights.get('total_replies', 0)}")
        print(f"  Subscribers who replied: {insights.get('subscribers_who_replied', 0)}")
        print(f"\nStrong Signals:")
        print(f"  Returned after absence: {insights.get('returned_after_absence', 0)}")
        print(f"  Previous purchasers: {insights.get('previous_purchasers', 0)}")
        print(f"\nReady for gentle offer: {insights.get('ready_for_offer', 0)}")

    elif args.ready:
        ready = tracker.get_ready_subscribers(ReadinessStage.WARMING)
        print(f"\n=== Subscribers Ready for Offers ({len(ready)}) ===")
        for profile in sorted(ready, key=lambda p: p.readiness_score, reverse=True):
            print(f"\n  {profile.email}")
            print(f"    Stage: {profile.readiness_stage.value}")
            print(f"    Score: {profile.readiness_score:.1f}")
            print(f"    Replies: {profile.replies}")
            can_offer, reason = tracker.can_send_offer(profile.email)
            print(f"    Can offer: {can_offer} ({reason})")

    elif args.journey:
        journey = tracker.get_subscriber_journey(args.journey)
        if journey:
            print(f"\n=== Journey for {args.journey} ===")
            print(json.dumps(journey, indent=2))
        else:
            print(f"No data for {args.journey}")

    elif args.check:
        can_offer, reason = tracker.can_send_offer(args.check)
        print(f"\nCan send offer to {args.check}:")
        print(f"  Result: {'YES' if can_offer else 'NO'}")
        print(f"  Reason: {reason}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
