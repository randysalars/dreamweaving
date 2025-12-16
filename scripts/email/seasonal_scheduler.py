#!/usr/bin/env python3
"""
Dreamweaver Seasonal Email Scheduler

Implements the 12-month email rhythm from the "Build Dreamweaver Business" strategy.
Reads the seasonal calendar config and queues appropriate emails to the email_queue table.

Usage:
    # Check if any emails should be sent today
    python3 scripts/email/seasonal_scheduler.py --check-today

    # Dry run (show what would be queued)
    python3 scripts/email/seasonal_scheduler.py --check-today --dry-run

    # Show calendar for a specific month
    python3 scripts/email/seasonal_scheduler.py --month december

    # Show full year calendar
    python3 scripts/email/seasonal_scheduler.py --show-year

    # Force queue a specific template
    python3 scripts/email/seasonal_scheduler.py --force-template dreamweaver_ritual_advent

Designed to run via systemd timer (weekly check).
"""

import os
import sys
import json
import argparse
import secrets
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import yaml

# Load environment variables
try:
    from dotenv import load_dotenv
    salarsu_env = Path("/media/rsalars/elements/Projects/salarsu/frontend/.env")
    dreamweaving_env = Path(__file__).parent.parent.parent / ".env"

    if salarsu_env.exists():
        load_dotenv(salarsu_env)
    if dreamweaving_env.exists():
        load_dotenv(dreamweaving_env, override=False)
except ImportError:
    pass

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("Error: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)


# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "seasonal_calendar.yaml"


def load_calendar() -> Dict[str, Any]:
    """Load the seasonal calendar configuration."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Calendar config not found: {CONFIG_PATH}")

    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def get_db_connection():
    """Get database connection from DATABASE_URL."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not set in environment")

    return psycopg2.connect(database_url)


def get_month_name(month_num: int) -> str:
    """Convert month number to lowercase name."""
    months = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    return months[month_num - 1]


def get_active_subscribers(conn) -> List[Dict]:
    """Get all active newsletter subscribers."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, email, first_name, newsletter_subscribed, newsletter_categories
            FROM users
            WHERE newsletter_subscribed = true
              AND email IS NOT NULL
            ORDER BY email
        """)
        return cur.fetchall()


def get_template_by_name(conn, template_name: str) -> Optional[Dict]:
    """Get email template by name."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, name, subject, body, variables
            FROM email_templates
            WHERE name = %s AND is_active = true
        """, (template_name,))
        return cur.fetchone()


def check_email_sent_recently(conn, template_name: str, days: int = 7) -> bool:
    """Check if this template was sent in the last N days."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM email_queue
            WHERE template_name = %s
              AND created_at > NOW() - INTERVAL '%s days'
        """, (template_name, days))
        count = cur.fetchone()[0]
        return count > 0


def queue_seasonal_email(
    conn,
    template_name: str,
    subject_override: Optional[str],
    subscribers: List[Dict],
    dry_run: bool = False
) -> int:
    """Queue a seasonal email for all subscribers."""
    template = get_template_by_name(conn, template_name)
    if not template:
        print(f"  Warning: Template '{template_name}' not found or inactive")
        return 0

    subject = subject_override or template["subject"]
    queued = 0

    with conn.cursor() as cur:
        for subscriber in subscribers:
            # Build template variables
            variables = {
                "first_name": subscriber.get("first_name") or "",
                "unsubscribe_url": f"https://www.salars.net/unsubscribe?email={subscriber['email']}"
            }

            if dry_run:
                print(f"    [DRY RUN] Would queue to: {subscriber['email']}")
                queued += 1
            else:
                # Generate queue ID
                queue_id = f"clw{secrets.token_hex(12)}"

                # Insert into email_queue
                cur.execute("""
                    INSERT INTO email_queue
                    (id, to_email, subject, body, template_name, template_variables,
                     status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, 'pending', NOW(), NOW())
                """, (
                    queue_id,
                    subscriber["email"],
                    subject,
                    template["body"],
                    template_name,
                    json.dumps(variables)
                ))
                queued += 1

        if not dry_run:
            conn.commit()

    return queued


def check_today(calendar: Dict, dry_run: bool = False):
    """Check if any emails should be sent today and queue them."""
    today = date.today()
    month_name = get_month_name(today.month)
    day_of_month = today.day

    print(f"\nChecking calendar for {today.strftime('%B %d, %Y')}...")
    print(f"Month: {month_name.capitalize()}")

    # Get month config
    month_config = calendar.get("months", {}).get(month_name)
    if not month_config:
        print(f"  No configuration for {month_name}")
        return

    print(f"  Theme: {month_config.get('theme', 'N/A')}")
    print(f"  Emotional state: {month_config.get('emotional_state', 'N/A')}")

    # Check special dates (no-email windows)
    special_dates = calendar.get("special_dates", {})
    for special_name, special_config in special_dates.items():
        if isinstance(special_config, dict) and special_config.get("behavior") == "no_emails":
            start = special_config.get("window_start", "")
            end = special_config.get("window_end", "")
            if start and end:
                start_month, start_day = map(int, start.split("-"))
                end_month, end_day = map(int, end.split("-"))

                # Check if today falls within the window
                in_window = False
                if start_month == end_month:
                    # Same month window (e.g., 12-20 to 12-26)
                    in_window = (today.month == start_month and
                                 start_day <= today.day <= end_day)
                else:
                    # Cross-month window (e.g., 12-31 to 01-02)
                    in_window = ((today.month == start_month and today.day >= start_day) or
                                 (today.month == end_month and today.day <= end_day))

                if in_window:
                    print(f"\n  In special window '{special_name}' - no emails today")
                    print(f"  Reason: {special_config.get('notes', 'N/A')}")
                    return

    # Check if today matches any scheduled email
    emails = month_config.get("emails", [])
    emails_to_send = []

    for email in emails:
        if email.get("day") == day_of_month:
            emails_to_send.append(email)

    if not emails_to_send:
        print(f"\n  No emails scheduled for day {day_of_month}")
        print(f"  Scheduled days this month: {[e.get('day') for e in emails]}")
        return

    # Connect to database
    conn = get_db_connection()

    try:
        # Get subscribers
        subscribers = get_active_subscribers(conn)
        print(f"\n  Active subscribers: {len(subscribers)}")

        if len(subscribers) == 0:
            print("  No subscribers to email")
            return

        # Queue each scheduled email
        for email in emails_to_send:
            template_name = email.get("template")
            subject_override = email.get("subject_override")
            notes = email.get("notes", "")

            print(f"\n  Scheduled email:")
            print(f"    Template: {template_name}")
            print(f"    Subject: {subject_override or '(use template default)'}")
            print(f"    Notes: {notes}")

            # Check if recently sent (prevent duplicates)
            min_days = calendar.get("defaults", {}).get("min_days_between_emails", 7)
            if check_email_sent_recently(conn, template_name, min_days):
                print(f"    Skipping: Template was sent in last {min_days} days")
                continue

            # Queue the email
            queued = queue_seasonal_email(
                conn, template_name, subject_override, subscribers, dry_run
            )
            print(f"    Queued: {queued} emails")

    finally:
        conn.close()


def show_month(calendar: Dict, month_name: str):
    """Display the email schedule for a specific month."""
    month_config = calendar.get("months", {}).get(month_name.lower())
    if not month_config:
        print(f"No configuration for {month_name}")
        return

    print(f"\n{'='*60}")
    print(f"  {month_name.upper()}")
    print(f"{'='*60}")
    print(f"Theme: {month_config.get('theme', 'N/A')}")
    print(f"Emotional state: {month_config.get('emotional_state', 'N/A')}")
    print()

    emails = month_config.get("emails", [])
    print(f"Scheduled emails ({len(emails)}):")
    for email in emails:
        day = email.get("day")
        template = email.get("template")
        subject = email.get("subject_override") or "(template default)"
        notes = email.get("notes", "")
        print(f"  Day {day:2d}: {template}")
        print(f"          Subject: {subject}")
        if notes:
            print(f"          Notes: {notes}")
        print()

    optional = month_config.get("optional_invitation", {})
    if optional.get("enabled"):
        print(f"Optional invitation: {optional.get('template', 'N/A')}")
        print(f"  Notes: {optional.get('notes', 'N/A')}")
    else:
        print(f"Optional invitation: Disabled")
        if optional.get("notes"):
            print(f"  Reason: {optional.get('notes')}")


def show_year(calendar: Dict):
    """Display the full year calendar summary."""
    print("\n" + "="*70)
    print("  DREAMWEAVER 12-MONTH EMAIL RHYTHM")
    print("="*70)

    months = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]

    total_emails = 0

    for month in months:
        config = calendar.get("months", {}).get(month, {})
        emails = config.get("emails", [])
        theme = config.get("theme", "N/A")
        days = [e.get("day") for e in emails]

        total_emails += len(emails)

        print(f"\n{month.upper():12s} | {len(emails)} email(s) on days {days}")
        print(f"             | Theme: {theme}")

    print(f"\n{'='*70}")
    print(f"Total planned emails per year: {total_emails}")
    print(f"Average per month: {total_emails/12:.1f}")
    print()

    # Show anti-patterns
    anti_patterns = calendar.get("anti_patterns", [])
    if anti_patterns:
        print("ANTI-PATTERNS (never do these):")
        for pattern in anti_patterns[:5]:
            print(f"  - {pattern}")


def force_template(calendar: Dict, template_name: str, dry_run: bool = False):
    """Force queue a specific template to all subscribers."""
    print(f"\nForcing template: {template_name}")

    conn = get_db_connection()

    try:
        # Get template
        template = get_template_by_name(conn, template_name)
        if not template:
            print(f"Error: Template '{template_name}' not found")
            return

        print(f"  Subject: {template['subject']}")

        # Get subscribers
        subscribers = get_active_subscribers(conn)
        print(f"  Subscribers: {len(subscribers)}")

        if len(subscribers) == 0:
            print("  No subscribers to email")
            return

        # Queue
        queued = queue_seasonal_email(conn, template_name, None, subscribers, dry_run)
        print(f"  Queued: {queued} emails")

    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Dreamweaver Seasonal Email Scheduler"
    )
    parser.add_argument(
        "--check-today",
        action="store_true",
        help="Check if any emails should be sent today and queue them"
    )
    parser.add_argument(
        "--month",
        help="Show calendar for a specific month"
    )
    parser.add_argument(
        "--show-year",
        action="store_true",
        help="Show full year calendar summary"
    )
    parser.add_argument(
        "--force-template",
        help="Force queue a specific template to all subscribers"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    try:
        calendar = load_calendar()

        if args.check_today:
            check_today(calendar, args.dry_run)
        elif args.month:
            show_month(calendar, args.month)
        elif args.show_year:
            show_year(calendar)
        elif args.force_template:
            force_template(calendar, args.force_template, args.dry_run)
        else:
            # Default: show current month
            today = date.today()
            show_month(calendar, get_month_name(today.month))

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
