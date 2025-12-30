#!/usr/bin/env python3
"""
Insert Dreamweaver Email Templates into Salarsu Database

This script inserts the email templates from the "Build Dreamweaver Business"
Notion page into the EmailTemplate table in the PostgreSQL database.

Templates follow the 4-layer email architecture:
1. Initiation - Welcome, sets tone
2. Correspondence - Reflective letters
3. Ritual - Seasonal (Advent, Easter, New Year)
4. Invitation - Gentle offers

Usage:
    python3 scripts/email/insert_dreamweaver_templates.py [--dry-run]
    python3 scripts/email/insert_dreamweaver_templates.py --list
    python3 scripts/email/insert_dreamweaver_templates.py --delete-all
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Load .env for DATABASE_URL
# Try Salarsu .env first (has DATABASE_URL), then dreamweaving .env
try:
    from dotenv import load_dotenv
    salarsu_env = Path("/home/rsalars/Projects/salarsu/frontend/.env")
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


# =============================================================================
# EMAIL TEMPLATES FROM NOTION "Build Dreamweaver Business" PAGE
# These are the EXACT templates - do not modify the copy without reviewing Notion
# =============================================================================

DREAMWEAVER_TEMPLATES: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 1. INITIATION EMAIL (sent immediately after signup)
    # -------------------------------------------------------------------------
    {
        "name": "dreamweaver_initiation",
        "subject": "A quiet welcome",
        "category": "correspondence",
        "trigger_event": "subscriber_created",
        "is_active": True,
        "variables": json.dumps(["first_name", "unsubscribe_url"]),
        "body": """Hello{{#first_name}}, {{first_name}}{{/first_name}},

I wanted to welcome you quietly.

You won't hear from Dreamweaver often.
When you do, it will be intentional.

These messages aren't campaigns or announcements.
They are closer to letters — reflections meant to be read slowly, or saved for later.

There's nothing you need to do.
Nothing to keep up with.
Nothing to buy.

Just know this:
You're welcome to be here, exactly as you are.

I'll write again when there's something worth sitting with.

Until then,
— Dreamweaver

---
If you'd prefer not to receive these letters, you can unsubscribe here: {{unsubscribe_url}}"""
    },

    # -------------------------------------------------------------------------
    # 2. CORRESPONDENCE EMAIL (the core recurring letter)
    # -------------------------------------------------------------------------
    {
        "name": "dreamweaver_correspondence",
        "subject": "A quiet reflection",
        "category": "correspondence",
        "trigger_event": "manual",
        "is_active": True,
        "variables": json.dumps(["first_name", "unsubscribe_url"]),
        "body": """Hello{{#first_name}}, {{first_name}}{{/first_name}},

Lately I've been thinking about how easily we carry more than we were meant to.

Responsibilities accumulate.
Noise accumulates.
Expectations accumulate.

And often, without realizing it, the inner life becomes crowded.

There is something quietly radical about pausing.
Not fixing.
Not solving.
Just noticing what is asking to be tended.

Sometimes meaning doesn't arrive as clarity.
Sometimes it arrives as permission to rest.

If this reflection meets you where you are, take it with you.
If not, let it pass gently.

Until next time,
— Dreamweaver

---
If you'd prefer not to receive these letters: {{unsubscribe_url}}"""
    },

    # -------------------------------------------------------------------------
    # 3. RITUAL EMAIL - ADVENT/CHRISTMAS
    # -------------------------------------------------------------------------
    {
        "name": "dreamweaver_ritual_advent",
        "subject": "As the season turns",
        "category": "ritual",
        "trigger_event": "seasonal_advent",
        "is_active": True,
        "variables": json.dumps(["first_name", "unsubscribe_url"]),
        "body": """Hello{{#first_name}}, {{first_name}}{{/first_name}},

As this season arrives, many people feel pressure to mark it loudly.
To explain it.
To perform it.
To keep pace with it.

But some moments are meant to be entered quietly.

If you're carrying weariness, you don't need to resolve it.
If you're carrying hope, you don't need to defend it.

Let this season be what it is.
Let yourself be where you are.

May light arrive gently.
May rest be allowed.
May meaning come without force.

Holding you in this moment,
— Dreamweaver

---
{{unsubscribe_url}}"""
    },

    # -------------------------------------------------------------------------
    # 4. RITUAL EMAIL - EASTER/RENEWAL
    # -------------------------------------------------------------------------
    {
        "name": "dreamweaver_ritual_easter",
        "subject": "On entering this season",
        "category": "ritual",
        "trigger_event": "seasonal_easter",
        "is_active": True,
        "variables": json.dumps(["first_name", "unsubscribe_url"]),
        "body": """Hello{{#first_name}}, {{first_name}}{{/first_name}},

Spring asks something of us that winter did not:
to let what was buried begin to rise.

This is not always comfortable.
Growth can feel like pressure.
Renewal can feel like grief for what is ending.

But there is no rush.

What rises, rises in its own time.
What heals, heals in its own way.

May you find gentleness with yourself in this season.
May what needs to emerge be welcomed without force.

With quiet hope,
— Dreamweaver

---
{{unsubscribe_url}}"""
    },

    # -------------------------------------------------------------------------
    # 5. RITUAL EMAIL - NEW YEAR
    # -------------------------------------------------------------------------
    {
        "name": "dreamweaver_ritual_newyear",
        "subject": "Entering the year gently",
        "category": "ritual",
        "trigger_event": "seasonal_newyear",
        "is_active": True,
        "variables": json.dumps(["first_name", "unsubscribe_url"]),
        "body": """Hello{{#first_name}}, {{first_name}}{{/first_name}},

A new year does not require reinvention.

It does not ask you to fix everything that felt unfinished.
It does not demand resolution or certainty.

A new year simply offers a threshold—
a quiet invitation to notice what you carry,
and to choose what you wish to continue carrying.

You don't need a plan.
You don't need a word for the year.
You don't need to improve.

You are allowed to simply begin again.
As you are.
From where you are.

May this year hold what you need.
May it release what you don't.

Gently,
— Dreamweaver

---
{{unsubscribe_url}}"""
    },

    # -------------------------------------------------------------------------
    # 6. INVITATION EMAIL (gentle offer)
    # -------------------------------------------------------------------------
    {
        "name": "dreamweaver_invitation",
        "subject": "An invitation, if it serves you",
        "category": "invitation",
        "trigger_event": "manual",
        "is_active": True,
        "variables": json.dumps(["first_name", "dreamweaving_title", "dreamweaving_url", "unsubscribe_url"]),
        "body": """Hello{{#first_name}}, {{first_name}}{{/first_name}},

I wanted to let you know about something that now exists.

It's a Dreamweaving created for those who've been feeling stretched thin —
a guided inner journey focused on rest, meaning, and return.

{{#dreamweaving_title}}
"{{dreamweaving_title}}"
{{dreamweaving_url}}
{{/dreamweaving_title}}

There's no urgency.
No expectation.

If it feels like something you'd like to spend time with, you're welcome to explore it.

If not, that's completely okay.
These letters will continue either way.

Thank you for being here,
— Dreamweaver

---
{{unsubscribe_url}}"""
    },

    # -------------------------------------------------------------------------
    # 7. GIFT GIVER EMAIL (sent to person who gave the gift)
    # -------------------------------------------------------------------------
    {
        "name": "dreamweaver_gift_giver",
        "subject": "Your gift has been received",
        "category": "transactional",
        "trigger_event": "gift_created",
        "is_active": True,
        "variables": json.dumps(["giver_name", "recipient_name", "dreamweaving_title", "delivery_date", "unsubscribe_url"]),
        "body": """Hello{{#giver_name}}, {{giver_name}}{{/giver_name}},

Thank you for the gift you've given.

{{#recipient_name}}
It will be delivered to {{recipient_name}} on {{delivery_date}}, quietly and respectfully.
{{/recipient_name}}
{{^recipient_name}}
It will be delivered on {{delivery_date}}, quietly and respectfully.
{{/recipient_name}}

Nothing more is required from you.

Gifts like this matter more than we often realize.
They create space.
They offer rest.
They remind someone they're not alone.

Thank you for choosing to give in this way.

With gratitude,
— Dreamweaver

---
{{unsubscribe_url}}"""
    },

    # -------------------------------------------------------------------------
    # 8. GIFT RECIPIENT EMAIL (sent to person receiving the gift)
    # -------------------------------------------------------------------------
    {
        "name": "dreamweaver_gift_recipient",
        "subject": "A gift for you",
        "category": "transactional",
        "trigger_event": "gift_delivered",
        "is_active": True,
        "variables": json.dumps(["recipient_name", "giver_name", "giver_message", "dreamweaving_title", "download_url", "unsubscribe_url"]),
        "body": """Hello{{#recipient_name}}, {{recipient_name}}{{/recipient_name}},

Someone offered this Dreamweaving for you.

{{#giver_name}}
From: {{giver_name}}
{{/giver_name}}

{{#giver_message}}
"{{giver_message}}"
{{/giver_message}}

There's no expectation attached to it.
No response required.
No timeline to follow.

It's simply an invitation to pause, when and if you wish.

{{#dreamweaving_title}}
"{{dreamweaving_title}}"
{{/dreamweaving_title}}

You can receive it here:
{{download_url}}

May it meet you kindly,
— Dreamweaver

---
{{unsubscribe_url}}"""
    },

    # -------------------------------------------------------------------------
    # 9. THANK YOU EMAIL (after first download, 24h delay)
    # -------------------------------------------------------------------------
    {
        "name": "dreamweaver_thankyou",
        "subject": "Thank you for spending time with us",
        "category": "correspondence",
        "trigger_event": "first_download",
        "is_active": True,
        "variables": json.dumps(["first_name", "dreamweaving_title", "unsubscribe_url"]),
        "body": """Hello{{#first_name}}, {{first_name}}{{/first_name}},

Thank you for spending time with Dreamweaver.

{{#dreamweaving_title}}
I hope "{{dreamweaving_title}}" met you where you needed to be met.
{{/dreamweaving_title}}

There's nothing you need to do now.
No feedback form.
No review request.
No next steps.

Simply know that this space exists whenever you need it.

If the experience moved something in you—
if it helped, or didn't, or surprised you—
you're welcome to reply to this letter.

But you don't have to.

Thank you for trusting us with your attention.

Quietly,
— Dreamweaver

---
{{unsubscribe_url}}"""
    },

    # -------------------------------------------------------------------------
    # 10. GIFT WELCOME EMAIL (after gift redemption)
    # -------------------------------------------------------------------------
    {
        "name": "dreamweaver_gift_welcome",
        "subject": "Welcome, take your time",
        "category": "correspondence",
        "trigger_event": "gift_redeemed",
        "is_active": True,
        "variables": json.dumps(["recipient_name", "dreamweaving_title", "unsubscribe_url"]),
        "body": """Hello{{#recipient_name}}, {{recipient_name}}{{/recipient_name}},

Welcome to Dreamweaver.

Someone thought of you—and here you are.

{{#dreamweaving_title}}
"{{dreamweaving_title}}" is yours to experience whenever feels right.
{{/dreamweaving_title}}

There's no pressure to listen now.
No expiration.
No sequence to follow.

When you're ready, it will be waiting.

If you'd ever like to receive occasional letters from Dreamweaver—
quiet reflections, not promotions—
you're welcome to stay subscribed.

But if you'd prefer not to, that's completely fine.
This message is just a welcome, not a beginning of something you didn't ask for.

Take your time.

Gently,
— Dreamweaver

---
{{unsubscribe_url}}"""
    },
]


def get_db_connection():
    """Get database connection from DATABASE_URL."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not set in environment")

    return psycopg2.connect(database_url)


def list_templates(conn):
    """List all existing Dreamweaver templates."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, name, subject, category, trigger_event, is_active, created_at
            FROM email_templates
            WHERE name LIKE 'dreamweaver_%'
            ORDER BY name
        """)
        templates = cur.fetchall()

    if not templates:
        print("No Dreamweaver templates found in database.")
        return

    print(f"\nFound {len(templates)} Dreamweaver templates:\n")
    for t in templates:
        status = "ACTIVE" if t["is_active"] else "inactive"
        print(f"  [{status}] {t['name']}")
        print(f"          Subject: {t['subject']}")
        print(f"          Category: {t['category']} | Trigger: {t['trigger_event']}")
        print(f"          Created: {t['created_at']}")
        print()


def delete_all_templates(conn, dry_run: bool = False):
    """Delete all Dreamweaver templates."""
    with conn.cursor() as cur:
        if dry_run:
            cur.execute("""
                SELECT COUNT(*) FROM email_templates WHERE name LIKE 'dreamweaver_%'
            """)
            count = cur.fetchone()[0]
            print(f"[DRY RUN] Would delete {count} Dreamweaver templates.")
        else:
            cur.execute("""
                DELETE FROM email_templates WHERE name LIKE 'dreamweaver_%'
            """)
            count = cur.rowcount
            conn.commit()
            print(f"Deleted {count} Dreamweaver templates.")


def insert_templates(conn, dry_run: bool = False):
    """Insert all Dreamweaver templates."""
    inserted = 0
    skipped = 0
    updated = 0

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for template in DREAMWEAVER_TEMPLATES:
            # Check if template already exists
            cur.execute("""
                SELECT id FROM email_templates WHERE name = %s
            """, (template["name"],))
            existing = cur.fetchone()

            if existing:
                if dry_run:
                    print(f"[DRY RUN] Would update: {template['name']}")
                    updated += 1
                else:
                    # Update existing template
                    cur.execute("""
                        UPDATE email_templates
                        SET subject = %s, body = %s, category = %s,
                            trigger_event = %s, is_active = %s, variables = %s,
                            updated_at = NOW()
                        WHERE name = %s
                    """, (
                        template["subject"],
                        template["body"],
                        template["category"],
                        template["trigger_event"],
                        template["is_active"],
                        template["variables"],
                        template["name"]
                    ))
                    print(f"Updated: {template['name']}")
                    updated += 1
            else:
                if dry_run:
                    print(f"[DRY RUN] Would insert: {template['name']}")
                    inserted += 1
                else:
                    # Insert new template (using cuid-like ID)
                    import secrets
                    template_id = f"clw{secrets.token_hex(12)}"

                    cur.execute("""
                        INSERT INTO email_templates
                        (id, name, subject, body, category, trigger_event, is_active, variables, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """, (
                        template_id,
                        template["name"],
                        template["subject"],
                        template["body"],
                        template["category"],
                        template["trigger_event"],
                        template["is_active"],
                        template["variables"]
                    ))
                    print(f"Inserted: {template['name']}")
                    inserted += 1

        if not dry_run:
            conn.commit()

    print(f"\nSummary: {inserted} inserted, {updated} updated, {skipped} skipped")
    if dry_run:
        print("\n[DRY RUN] No changes made. Run without --dry-run to apply.")


def main():
    parser = argparse.ArgumentParser(
        description="Insert Dreamweaver email templates into Salarsu database"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing Dreamweaver templates"
    )
    parser.add_argument(
        "--delete-all",
        action="store_true",
        help="Delete all Dreamweaver templates"
    )

    args = parser.parse_args()

    try:
        conn = get_db_connection()
        print("Connected to database")

        if args.list:
            list_templates(conn)
        elif args.delete_all:
            delete_all_templates(conn, args.dry_run)
        else:
            insert_templates(conn, args.dry_run)

        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
