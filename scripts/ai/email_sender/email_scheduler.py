#!/usr/bin/env python3
"""
Dreamweaver Email Scheduler

Implements trust-based email scheduling with:
- 7-day minimum between non-transactional emails
- Seasonal calendar awareness
- Segment-based targeting
- Readiness signal tracking

Philosophy: "We write when there is something worth sitting with."
"""

import os
import yaml
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib

# Optional Resend integration
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False


class EmailType(Enum):
    """Email types with their rules"""
    INITIATION = "initiation"           # Welcome, no CTA
    CORRESPONDENCE = "correspondence"   # Core letters
    RITUAL = "ritual"                   # Seasonal/sacred
    INVITATION = "invitation"           # Soft offers
    SEQUENCE = "sequence"               # Multi-email nurture sequence
    GIFT_GIVER = "gift_giver"          # Transactional
    GIFT_RECIPIENT = "gift_recipient"   # Transactional


@dataclass
class EmailRecord:
    """Record of a sent email"""
    email_id: str
    email_type: str
    recipient: str
    sent_at: datetime
    subject: str
    opened: bool = False
    clicked: bool = False
    replied: bool = False
    tags: List[str] = field(default_factory=list)


@dataclass
class Subscriber:
    """Subscriber profile with engagement data"""
    email: str
    subscribed_at: datetime
    source: str  # article, youtube, gift, direct
    interests: List[str] = field(default_factory=list)  # light, rest, faith, imagination
    emails_received: int = 0
    emails_opened: int = 0
    replies: int = 0
    purchases: int = 0
    last_email_at: Optional[datetime] = None
    last_open_at: Optional[datetime] = None
    active_sequence: Optional[str] = None  # slug of the active sequence
    sequence_index: int = 0  # 0 if no sequence, 1-10 if active
    tags: List[str] = field(default_factory=list)

    @property
    def engagement_level(self) -> str:
        """Calculate engagement level"""
        if self.replies > 0:
            return "replier"  # Most valuable
        if self.emails_opened > 0 and self.emails_received > 0:
            open_rate = self.emails_opened / self.emails_received
            if open_rate > 0.7:
                return "engaged"
            elif open_rate > 0.3:
                return "moderate"
        return "passive"

    @property
    def days_since_last_email(self) -> Optional[int]:
        """Days since last email sent"""
        if self.last_email_at:
            return (datetime.now() - self.last_email_at).days
        return None

    @property
    def is_ready_for_email(self) -> bool:
        """Check if 7-day rule allows sending"""
        if self.last_email_at is None:
            return True
        return self.days_since_last_email >= 7


class EmailScheduler:
    """
    Trust-based email scheduling system.

    Core Rules:
    - Never send more than 1 email in 7 days (except transactional)
    - No urgency language
    - Ritual emails never sell
    - Invitation emails max 1/month
    """

    # Transactional email types (exempt from 7-day rule)
    TRANSACTIONAL_TYPES = {EmailType.GIFT_GIVER, EmailType.GIFT_RECIPIENT}

    # Minimum days between non-transactional emails
    MIN_DAYS_BETWEEN_EMAILS = 7

    # Maximum invitation emails per month
    MAX_INVITATIONS_PER_MONTH = 1

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the email scheduler"""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.config_path = config_path or self.project_root / "config" / "email_config.yaml"
        self.history_path = self.project_root / "data" / "email_history.json"
        self.subscribers_path = self.project_root / "data" / "subscribers.json"

        # Ensure data directory exists
        (self.project_root / "data").mkdir(exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Load email history
        self.history = self._load_history()

        # Load subscribers
        self.subscribers = self._load_subscribers()

        # Initialize Resend if available
        if RESEND_AVAILABLE and os.getenv("RESEND_API_KEY"):
            resend.api_key = os.getenv("RESEND_API_KEY")
            self.resend_enabled = True
        else:
            self.resend_enabled = False

    def _load_config(self) -> Dict:
        """Load email configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {
            "sender_email": "dreamweaver@salars.net",
            "sender_name": "Dreamweaver",
            "min_days_between_emails": 7,
            "max_invitations_per_month": 1
        }

    def _load_sequence(self, slug: str) -> Optional[Dict]:
        """Load a sequence definition from YAML"""
        seq_path = self.project_root / "config" / "sequences" / f"{slug}.yaml"
        if seq_path.exists():
            with open(seq_path) as f:
                return yaml.safe_load(f)
        return None

    def trigger_sequence(self, recipient: str, sequence_slug: str) -> bool:
        """Manually trigger a sequence for a subscriber"""
        if recipient not in self.subscribers:
            # Create subscriber if doesn't exist
            self.subscribers[recipient] = Subscriber(
                email=recipient,
                subscribed_at=datetime.now(),
                source="sequence_trigger"
            )
        
        subscriber = self.subscribers[recipient]
        sequence = self._load_sequence(sequence_slug)
        
        if not sequence:
            print(f"Error: Sequence '{sequence_slug}' not found.")
            return False
            
        subscriber.active_sequence = sequence_slug
        subscriber.sequence_index = 0  # Ready for first email
        self._save_subscribers()
        print(f"Triggered sequence '{sequence_slug}' for {recipient}")
        return True

    def process_sequences(self) -> List[Dict]:
        """Process all active sequences and send pending emails"""
        results = []
        for email, subscriber in self.subscribers.items():
            if not subscriber.active_sequence:
                continue
            
            # Check if 7-day rule allows
            if not subscriber.is_ready_for_email:
                continue
            
            sequence = self._load_sequence(subscriber.active_sequence)
            if not sequence:
                continue
                
            next_index = subscriber.sequence_index + 1
            emails = sequence.get("emails", [])
            
            # Find the email for the next index
            next_email = next((e for e in emails if e["index"] == next_index), None)
            
            if next_email:
                # Load actual content if exists
                content_path = self.project_root / "config" / "sequences" / "content" / subscriber.active_sequence / f"{next_index:03d}.txt"
                content = f"Theme: {next_email['theme']}\n\n(Sequence Content Placeholder)"
                
                if content_path.exists():
                    with open(content_path, "r") as f:
                        file_content = f.read()
                        # Extract subject if it's on first line (standard format: Subject: ...)
                        if file_content.startswith("Subject:"):
                            first_line_end = file_content.find("\n")
                            # subject = file_content[8:first_line_end].strip() # Use YAML subject as source of truth for now or parse?
                            content = file_content[first_line_end:].strip()
                        else:
                            content = file_content
                
                # Schedule/Send the email
                res = self.schedule_email(
                    recipient=email,
                    email_type=EmailType.SEQUENCE,
                    subject=next_email["subject"],
                    content=content,
                    tags=[f"seq:{subscriber.active_sequence}", f"idx:{next_index}"]
                )
                
                # Add subject to return for logging
                res["subject"] = next_email["subject"]
                
                if res.get("success"):
                    subscriber.sequence_index = next_index
                    # If this was the last email, clear the active sequence
                    if next_index >= max(e["index"] for e in emails):
                        subscriber.active_sequence = None
                    results.append(res)
            else:
                # Sequence finished or index out of bounds
                subscriber.active_sequence = None
        
        if results:
            self._save_subscribers()
        
        return results

    def _load_history(self) -> List[EmailRecord]:
        """Load email sending history"""
        if self.history_path.exists():
            with open(self.history_path) as f:
                data = json.load(f)
                return [
                    EmailRecord(
                        email_id=r["email_id"],
                        email_type=r["email_type"],
                        recipient=r["recipient"],
                        sent_at=datetime.fromisoformat(r["sent_at"]),
                        subject=r["subject"],
                        opened=r.get("opened", False),
                        clicked=r.get("clicked", False),
                        replied=r.get("replied", False),
                        tags=r.get("tags", [])
                    )
                    for r in data
                ]
        return []

    def _save_history(self):
        """Save email history"""
        data = [
            {
                "email_id": r.email_id,
                "email_type": r.email_type,
                "recipient": r.recipient,
                "sent_at": r.sent_at.isoformat(),
                "subject": r.subject,
                "opened": r.opened,
                "clicked": r.clicked,
                "replied": r.replied,
                "tags": r.tags
            }
            for r in self.history
        ]
        with open(self.history_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_subscribers(self) -> Dict[str, Subscriber]:
        """Load subscriber data"""
        if self.subscribers_path.exists():
            with open(self.subscribers_path) as f:
                data = json.load(f)
                return {
                    email: Subscriber(
                        email=email,
                        subscribed_at=datetime.fromisoformat(s["subscribed_at"]),
                        source=s.get("source", "direct"),
                        interests=s.get("interests", []),
                        emails_received=s.get("emails_received", 0),
                        emails_opened=s.get("emails_opened", 0),
                        replies=s.get("replies", 0),
                        purchases=s.get("purchases", 0),
                        last_email_at=datetime.fromisoformat(s["last_email_at"]) if s.get("last_email_at") else None,
                        last_open_at=datetime.fromisoformat(s["last_open_at"]) if s.get("last_open_at") else None,
                        active_sequence=s.get("active_sequence"),
                        sequence_index=s.get("sequence_index", 0),
                        tags=s.get("tags", [])
                    )
                    for email, s in data.items()
                }
        return {}

    def _save_subscribers(self):
        """Save subscriber data"""
        data = {
            email: {
                "subscribed_at": s.subscribed_at.isoformat(),
                "source": s.source,
                "interests": s.interests,
                "emails_received": s.emails_received,
                "emails_opened": s.emails_opened,
                "replies": s.replies,
                "purchases": s.purchases,
                "last_email_at": s.last_email_at.isoformat() if s.last_email_at else None,
                "last_open_at": s.last_open_at.isoformat() if s.last_open_at else None,
                "active_sequence": s.active_sequence,
                "sequence_index": s.sequence_index,
                "tags": s.tags
            }
            for email, s in self.subscribers.items()
        }
        with open(self.subscribers_path, "w") as f:
            json.dump(data, f, indent=2)

    def can_send_email(
        self,
        recipient: str,
        email_type: EmailType
    ) -> tuple[bool, Optional[str]]:
        """
        Check if an email can be sent based on rules.

        Returns:
            (can_send, reason_if_not)
        """
        # Transactional emails always allowed
        if email_type in self.TRANSACTIONAL_TYPES:
            return True, None

        # Check subscriber exists
        if recipient not in self.subscribers:
            return True, None  # New subscriber, allow

        subscriber = self.subscribers[recipient]

        # Check 7-day rule
        if not subscriber.is_ready_for_email:
            days_left = self.MIN_DAYS_BETWEEN_EMAILS - subscriber.days_since_last_email
            return False, f"7-day rule: {days_left} days until next email allowed"

        # Check invitation frequency
        if email_type == EmailType.INVITATION:
            invitations_this_month = self._count_invitations_this_month(recipient)
            if invitations_this_month >= self.MAX_INVITATIONS_PER_MONTH:
                return False, f"Maximum {self.MAX_INVITATIONS_PER_MONTH} invitation(s) per month reached"

        return True, None

    def _count_invitations_this_month(self, recipient: str) -> int:
        """Count invitation emails sent this month"""
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        count = 0
        for record in self.history:
            if (record.recipient == recipient and
                record.email_type == EmailType.INVITATION.value and
                record.sent_at >= month_start):
                count += 1
        return count

    def get_eligible_recipients(
        self,
        email_type: EmailType,
        segment: Optional[str] = None,
        interests: Optional[List[str]] = None
    ) -> List[str]:
        """
        Get list of recipients eligible for this email type.

        Args:
            email_type: Type of email to send
            segment: Optional segment filter (engaged, moderate, passive, replier)
            interests: Optional interest filters

        Returns:
            List of eligible email addresses
        """
        eligible = []

        for email, subscriber in self.subscribers.items():
            # Check can_send rules
            can_send, _ = self.can_send_email(email, email_type)
            if not can_send:
                continue

            # Check segment filter
            if segment and subscriber.engagement_level != segment:
                continue

            # Check interest filter
            if interests:
                if not any(i in subscriber.interests for i in interests):
                    continue

            eligible.append(email)

        return eligible

    def schedule_email(
        self,
        recipient: str,
        email_type: EmailType,
        subject: str,
        content: str,
        send_at: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Schedule an email for sending.

        Args:
            recipient: Email address
            email_type: Type of email
            subject: Email subject
            content: HTML content
            send_at: Optional scheduled send time (defaults to now)
            tags: Optional tags for tracking

        Returns:
            Result dictionary with status
        """
        # Validate rules
        can_send, reason = self.can_send_email(recipient, email_type)
        if not can_send:
            return {
                "success": False,
                "error": reason,
                "blocked_by": "scheduling_rules"
            }

        # Generate email ID
        email_id = hashlib.md5(
            f"{recipient}{datetime.now().isoformat()}{email_type.value}".encode()
        ).hexdigest()[:12]

        # Determine send time
        send_time = send_at or datetime.now()

        # Create record
        record = EmailRecord(
            email_id=email_id,
            email_type=email_type.value,
            recipient=recipient,
            sent_at=send_time,
            subject=subject,
            tags=tags or []
        )

        # If sending now and Resend is available
        if send_at is None and self.resend_enabled:
            try:
                result = resend.Emails.send({
                    "from": f"{self.config.get('sender_name', 'Dreamweaver')} <{self.config.get('sender_email', 'dreamweaver@salars.net')}>",
                    "to": recipient,
                    "subject": subject,
                    "html": content
                })
                record.email_id = result.get("id", email_id)
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "blocked_by": "resend_api"
                }

        # Update history
        self.history.append(record)
        self._save_history()

        # Update subscriber
        if recipient in self.subscribers:
            self.subscribers[recipient].emails_received += 1
            self.subscribers[recipient].last_email_at = send_time
        else:
            # Create new subscriber record
            self.subscribers[recipient] = Subscriber(
                email=recipient,
                subscribed_at=datetime.now(),
                source="direct",
                emails_received=1,
                last_email_at=send_time
            )
        self._save_subscribers()

        return {
            "success": True,
            "email_id": record.email_id,
            "scheduled_for": send_time.isoformat(),
            "type": email_type.value
        }

    def record_open(self, email_id: str):
        """Record that an email was opened"""
        for record in self.history:
            if record.email_id == email_id:
                record.opened = True
                if record.recipient in self.subscribers:
                    self.subscribers[record.recipient].emails_opened += 1
                    self.subscribers[record.recipient].last_open_at = datetime.now()
                break
        self._save_history()
        self._save_subscribers()

    def record_reply(self, email_id: str):
        """Record that an email received a reply (MOST IMPORTANT METRIC)"""
        for record in self.history:
            if record.email_id == email_id:
                record.replied = True
                if record.recipient in self.subscribers:
                    self.subscribers[record.recipient].replies += 1
                break
        self._save_history()
        self._save_subscribers()

    def get_stats(self) -> Dict[str, Any]:
        """Get email statistics"""
        total_sent = len(self.history)
        total_opened = sum(1 for r in self.history if r.opened)
        total_replied = sum(1 for r in self.history if r.replied)

        by_type = {}
        for email_type in EmailType:
            type_records = [r for r in self.history if r.email_type == email_type.value]
            by_type[email_type.value] = {
                "sent": len(type_records),
                "opened": sum(1 for r in type_records if r.opened),
                "replied": sum(1 for r in type_records if r.replied)
            }

        engagement_levels = {
            "replier": 0,
            "engaged": 0,
            "moderate": 0,
            "passive": 0
        }
        for subscriber in self.subscribers.values():
            engagement_levels[subscriber.engagement_level] += 1

        return {
            "total_subscribers": len(self.subscribers),
            "total_emails_sent": total_sent,
            "total_opens": total_opened,
            "total_replies": total_replied,  # Most important metric
            "reply_rate": total_replied / total_sent if total_sent > 0 else 0,
            "by_type": by_type,
            "engagement_distribution": engagement_levels
        }

    def get_upcoming_calendar(self, days: int = 30) -> List[Dict]:
        """
        Get upcoming email calendar based on seasonal schedule.

        Args:
            days: Number of days to look ahead

        Returns:
            List of planned email events
        """
        calendar_path = self.project_root / "config" / "email_calendar.yaml"
        if not calendar_path.exists():
            return []

        with open(calendar_path) as f:
            calendar = yaml.safe_load(f)

        now = datetime.now()
        current_month = now.strftime("%B").lower()

        upcoming = []
        if current_month in calendar:
            month_config = calendar[current_month]
            for email_type in month_config.get("types", []):
                upcoming.append({
                    "type": email_type,
                    "theme": month_config.get("theme", ""),
                    "suggested": True
                })

        return upcoming


def main():
    """CLI for email scheduler"""
    import argparse

    parser = argparse.ArgumentParser(description="Dreamweaver Email Scheduler")
    parser.add_argument("--stats", action="store_true", help="Show email statistics")
    parser.add_argument("--eligible", type=str, help="List eligible recipients for email type")
    parser.add_argument("--calendar", action="store_true", help="Show upcoming email calendar")
    parser.add_argument("--check", type=str, help="Check if recipient can receive email")
    parser.add_argument("--trigger-sequence", nargs=2, metavar=("EMAIL", "SEQUENCE"), help="Trigger a sequence for a subscriber")
    parser.add_argument("--process-sequences", action="store_true", help="Process all active sequences")

    args = parser.parse_args()

    scheduler = EmailScheduler()

    if args.stats:
        stats = scheduler.get_stats()
        print("\n=== Dreamweaver Email Statistics ===")
        print(f"Total Subscribers: {stats['total_subscribers']}")
        print(f"Total Emails Sent: {stats['total_emails_sent']}")
        print(f"Reply Rate: {stats['reply_rate']:.1%} (most important metric)")
        print("\nEngagement Distribution:")
        for level, count in stats['engagement_distribution'].items():
            print(f"  {level}: {count}")
        print("\nBy Email Type:")
        for type_name, type_stats in stats['by_type'].items():
            print(f"  {type_name}: {type_stats['sent']} sent, {type_stats['replied']} replied")

    elif args.eligible:
        try:
            email_type = EmailType(args.eligible)
            eligible = scheduler.get_eligible_recipients(email_type)
            print(f"\n=== Eligible for {args.eligible} ===")
            print(f"Count: {len(eligible)}")
            for email in eligible[:10]:
                print(f"  - {email}")
            if len(eligible) > 10:
                print(f"  ... and {len(eligible) - 10} more")
        except ValueError:
            print(f"Unknown email type: {args.eligible}")
            print(f"Valid types: {[t.value for t in EmailType]}")

    elif args.calendar:
        upcoming = scheduler.get_upcoming_calendar()
        print("\n=== Upcoming Email Calendar ===")
        for event in upcoming:
            print(f"  [{event['type']}] {event['theme']}")

    elif args.check:
        for email_type in EmailType:
            can_send, reason = scheduler.can_send_email(args.check, email_type)
            status = "OK" if can_send else f"BLOCKED: {reason}"
            print(f"  {email_type.value}: {status}")

    elif args.trigger_sequence:
        email, sequence = args.trigger_sequence
        scheduler.trigger_sequence(email, sequence)

    elif args.process_sequences:
        results = scheduler.process_sequences()
        print(f"\n=== Processed Sequences ===")
        print(f"Sent {len(results)} emails")
        for res in results:
            print(f"  - {res.get('email_id')}: {res.get('type')}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
