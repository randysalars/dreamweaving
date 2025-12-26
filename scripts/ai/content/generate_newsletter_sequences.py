#!/usr/bin/env python3
"""
Newsletter Sequence Generator

Generates 10-email sequences for all 12 newsletter categories following
the strategic blueprint from Notion. Each sequence follows a "mythic
onboarding arc" designed to build epistemic trust and audience formation.

Usage:
    python3 scripts/ai/content/generate_newsletter_sequences.py --category dreamweavings
    python3 scripts/ai/content/generate_newsletter_sequences.py --all
    python3 scripts/ai/content/generate_newsletter_sequences.py --all --upload
"""

import argparse
import json
import os
import sys
import requests
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import anthropic
except ImportError:
    print("Please install anthropic: pip install anthropic")
    sys.exit(1)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class NewsletterCategory:
    """Newsletter category definition"""
    name: str
    slug: str
    icon: str
    tone: str
    enemy: str
    description: str


@dataclass
class EmailSequenceItem:
    """Single email in a sequence"""
    sequence_order: int
    purpose: str
    subject_pattern: str
    delay_days: int
    psychological_job: str


@dataclass
class GeneratedEmail:
    """Generated email content"""
    category_slug: str
    subject: str
    preview_text: str
    body_html: str
    body_text: str
    sequence_order: int
    delay_days: int
    status: str = "draft"


# =============================================================================
# CATEGORY DEFINITIONS
# =============================================================================

CATEGORIES = [
    NewsletterCategory(
        name="Artificial Intelligence",
        slug="ai",
        icon="🤖",
        tone="clear-eyed, non-alarmist",
        enemy="tool worship or panic",
        description="AI is neither savior nor threat"
    ),
    NewsletterCategory(
        name="Learning & Consciousness",
        slug="consciousness",
        icon="🧠",
        tone="slow, integrative",
        enemy="information gluttony",
        description="Learning isn't about information"
    ),
    NewsletterCategory(
        name="Survival & Self-Reliance",
        slug="survival",
        icon="🏕️",
        tone="sober, adaptive",
        enemy="fear-based accumulation",
        description="Survival is adaptability, not stockpiles"
    ),
    NewsletterCategory(
        name="Health & Wellness",
        slug="health",
        icon="💚",
        tone="grounded, anti-biohacking hype",
        enemy="obsession masquerading as discipline",
        description="Health isn't discipline. It's feedback."
    ),
    NewsletterCategory(
        name="Wealth & Abundance",
        slug="wealth",
        icon="💰",
        tone="calm, long-range",
        enemy="short-term thinking disguised as ambition",
        description="Wealth is stability, time, and leverage"
    ),
    NewsletterCategory(
        name="Love & Relationships",
        slug="love",
        icon="❤️",
        tone="precise, compassionate",
        enemy="intensity mistaken for intimacy",
        description="Love is clarity over intensity"
    ),
    NewsletterCategory(
        name="Happiness & Joy",
        slug="happiness",
        icon="😊",
        tone="paradoxical, disarming",
        enemy="optimization of feelings",
        description="Happiness is depth over mood"
    ),
    NewsletterCategory(
        name="Spirituality & Inner Growth",
        slug="spirituality",
        icon="✨",
        tone="discerning, rooted",
        enemy="sensation without integration",
        description="Spirituality is discernment, not sensation"
    ),
    NewsletterCategory(
        name="Poetry & Creative Expression",
        slug="poetry",
        icon="📜",
        tone="quiet, invitational",
        enemy="performance over presence",
        description="Poetry is attention made visible"
    ),
    NewsletterCategory(
        name="Dreamweavings",
        slug="dreamweavings",
        icon="🌀",
        tone="liminal, reverent",
        enemy="escapism framed as spirituality",
        description="Inner landscapes, integrated"
    ),
    NewsletterCategory(
        name="Old West",
        slug="old-west",
        icon="🤠",
        tone="mythic, grounded",
        enemy="nostalgia without understanding",
        description="Myth, reality, and character"
    ),
    NewsletterCategory(
        name="Treasure & Discovery",
        slug="treasure",
        icon="💎",
        tone="patient, pattern-oriented",
        enemy="luck obsession",
        description="Pattern recognition and patience"
    ),
]

# Mapping slug to category for quick lookup
CATEGORY_MAP = {cat.slug: cat for cat in CATEGORIES}


# =============================================================================
# EMAIL SEQUENCE STRUCTURE
# =============================================================================

EMAIL_SEQUENCE = [
    EmailSequenceItem(
        sequence_order=1,
        purpose="Orientation",
        subject_pattern="{topic} Isn't What Most People Think It Is",
        delay_days=0,
        psychological_job="Set expectations. Eliminate the wrong audience. Increase trust. Explain why this topic is misunderstood."
    ),
    EmailSequenceItem(
        sequence_order=2,
        purpose="Resonance",
        subject_pattern="The Problem Beneath the Problem",
        delay_days=7,
        psychological_job="Trigger recognition, not urgency. Name the invisible frustration they haven't articulated."
    ),
    EmailSequenceItem(
        sequence_order=3,
        purpose="Reframe",
        subject_pattern="A Better Mental Model",
        delay_days=14,
        psychological_job="Give them language they didn't have before. Introduce a simple but deep frame they can't unsee."
    ),
    EmailSequenceItem(
        sequence_order=4,
        purpose="Story",
        subject_pattern="How People Miss the Point",
        delay_days=21,
        psychological_job="Lower defenses through narrative. Tell a story where effort was applied in the wrong direction."
    ),
    EmailSequenceItem(
        sequence_order=5,
        purpose="Authority",
        subject_pattern="What We've Learned Watching This for Years",
        delay_days=28,
        psychological_job="Establish earned perspective, not credentials. Patterns you've seen repeat across time."
    ),
    EmailSequenceItem(
        sequence_order=6,
        purpose="Practice",
        subject_pattern="One Small Shift That Changes Everything",
        delay_days=35,
        psychological_job="Give them an experience, not advice. A single actionable experiment."
    ),
    EmailSequenceItem(
        sequence_order=7,
        purpose="Identity",
        subject_pattern="The Kind of Person This Attracts",
        delay_days=42,
        psychological_job="Turn reader into participant. Describe the type of mind that resonates here. Subtle identity formation."
    ),
    EmailSequenceItem(
        sequence_order=8,
        purpose="Contrast",
        subject_pattern="Why Popular Advice Fails Here",
        delay_days=49,
        psychological_job="Differentiate without attacking. Show why surface-level advice collapses under complexity."
    ),
    EmailSequenceItem(
        sequence_order=9,
        purpose="Invitation",
        subject_pattern="Go Deeper If You Want",
        delay_days=56,
        psychological_job="Soft transition to deeper content, not a sale. Link to long-form article or Dreamweaving. No pressure."
    ),
    EmailSequenceItem(
        sequence_order=10,
        purpose="Ritual",
        subject_pattern="This Is How to Use This Space",
        delay_days=63,
        psychological_job="Set a long-term relationship rhythm. Explain how often you write, how to engage, how to step away guilt-free."
    ),
]


# =============================================================================
# SUBJECT LINE TEMPLATES (from Notion)
# =============================================================================

SUBJECT_TEMPLATES = {
    "health": [
        "Health Isn't What Most People Think It Is",
        "The Problem Beneath \"Being Healthy\"",
        "A Simpler Way to Think About the Body",
        "When Discipline Quietly Stops Working",
        "A Pattern I've Seen Repeat for Years",
        "One Small Shift That Changes Everything",
        "Who This Approach Tends to Resonate With",
        "Why Most Health Advice Breaks Over Time",
        "Something Deeper, If You Want It",
        "How to Use This Space Without Pressure",
    ],
    "wealth": [
        "Wealth Is Not About Getting Rich",
        "The Anxiety Money Can't Solve",
        "A Better Way to Think About Security",
        "When Effort Stops Compounding",
        "What Quiet Wealth Usually Looks Like",
        "One Question Worth Sitting With",
        "The Kind of Person This Appeals To",
        "Why Popular Money Advice Fails",
        "A Longer Exploration, If You're Curious",
        "How This Fits Into a Long Life",
    ],
    "love": [
        "Love Is Often Misunderstood",
        "The Friction No One Talks About",
        "A Calmer Model of Connection",
        "When Chemistry Becomes Confusing",
        "A Pattern I've Watched Repeat",
        "One Thing to Notice This Week",
        "Who This Way of Thinking Fits",
        "Why Advice About Love Breaks Down",
        "Something Deeper You May Appreciate",
        "How to Stay Without Pressure",
    ],
    "happiness": [
        "Happiness Isn't a Feeling",
        "The Subtle Trap of Wanting to Feel Better",
        "A Different Way to Think About Joy",
        "When Chasing Happiness Backfires",
        "What Actually Holds Over Time",
        "One Small Reframe to Try",
        "Who This Perspective Resonates With",
        "Why Positivity Advice Often Fails",
        "A Longer Reflection, If You Want It",
        "How to Engage Without Optimizing",
    ],
    "dreamweavings": [
        "This Isn't Escapism",
        "Why Inner Imagery Is Often Misused",
        "A Clearer Way to Understand Dreamweaving",
        "When Symbolism Loses Its Power",
        "A Pattern That Separates Depth From Fantasy",
        "One Gentle Practice to Try",
        "Who This Work Tends to Call",
        "Why Surface-Level Mysticism Fails",
        "Something Deeper to Sit With",
        "How to Approach This Space",
    ],
    "spirituality": [
        "Spirituality Isn't About Experience",
        "The Quiet Confusion Many People Feel",
        "A Grounded Way to Think About the Inner Life",
        "When Intensity Replaces Truth",
        "What Discernment Looks Like in Practice",
        "One Small Act of Attention",
        "Who This Path Often Fits",
        "Why Spiritual Advice Breaks Down",
        "A Deeper Reflection, If You Want It",
        "How to Walk This Without Pressure",
    ],
    "poetry": [
        "Poetry Isn't About Expression",
        "Why Most Writing Feels Empty",
        "A Simpler Way to Understand Poetry",
        "When Craft Overpowers Presence",
        "What Endures on the Page",
        "One Way to Listen More Closely",
        "Who Poetry Actually Serves",
        "Why Performance Weakens Language",
        "Something Deeper to Read",
        "How to Visit This Space",
    ],
    "survival": [
        "Survival Is Often Misunderstood",
        "The Fear Beneath Preparedness",
        "A Better Model of Readiness",
        "When Stockpiling Becomes a Crutch",
        "What Actually Carries People Through",
        "One Shift That Increases Resilience",
        "Who This Thinking Resonates With",
        "Why Popular Survival Advice Fails",
        "A Deeper Look, If You Want It",
        "How to Think Long-Term",
    ],
    "old-west": [
        "The Old West Wasn't What Movies Show",
        "The Deeper Story Most People Miss",
        "A Truer Way to See That Era",
        "When Myth Replaces Understanding",
        "Patterns That Still Matter Today",
        "One Detail Worth Noticing",
        "Who This History Resonates With",
        "Why Nostalgia Distorts Truth",
        "A Longer Exploration, If You're Curious",
        "How to Walk This Terrain",
    ],
    "treasure": [
        "Treasure Hunting Isn't About Luck",
        "The Mistake Most People Make",
        "A Better Way to Think About Finds",
        "When Hope Replaces Method",
        "What Successful Searchers Share",
        "One Way to Sharpen Your Eye",
        "Who This Craft Fits",
        "Why Shortcuts Fail Here",
        "A Deeper Dive, If You Want It",
        "How to Stay With the Search",
    ],
    "ai": [
        "AI Is Neither Savior Nor Threat",
        "The Fear Beneath the Debate",
        "A Clearer Way to Think About Intelligence",
        "When Tools Get Mistaken for Minds",
        "A Pattern Emerging Already",
        "One Question Worth Asking",
        "Who This Perspective Resonates With",
        "Why Extreme Views Collapse",
        "A Longer Reflection, If You Want It",
        "How to Stay Oriented",
    ],
    "consciousness": [
        "Learning Isn't About Information",
        "The Hidden Cost of Knowing Too Much",
        "A Better Model of Understanding",
        "When Input Replaces Integration",
        "What Real Learning Looks Like",
        "One Small Practice to Try",
        "Who This Way of Learning Fits",
        "Why Most Learning Advice Fails",
        "A Deeper Inquiry, If You Want It",
        "How to Use This Thoughtfully",
    ],
}


# =============================================================================
# CONTENT GENERATION
# =============================================================================

def get_system_prompt(category: NewsletterCategory) -> str:
    """Generate the system prompt for email content generation"""
    return f"""You are writing email content for Salars.net's {category.name} newsletter sequence.

VOICE & TONE:
- {category.tone}
- Calm, declarative statements
- No emojis, no hype, no clickbait
- No urgency or pressure language
- Use "if you want..." instead of "you should..."
- Create epistemic trust, not marketing excitement

THE "ENEMY" TO ADDRESS:
This topic's enemy is: {category.enemy}
Subtly critique this without attacking specific people or brands.

STRUCTURE FOR EACH EMAIL:
1. Opening Hook (2-3 sentences) - Name an invisible frustration or misunderstanding
2. Core Insight (3-4 paragraphs) - Calm, authoritative content that reframes the topic
3. Identity Whisper (1 paragraph) - Subtle "if this resonates..." framing
4. Soft Close (1-2 sentences) - No pressure, no countdowns, just calm conclusion

FORMATTING:
- Use HTML: <p> tags for paragraphs, <em> for emphasis (sparingly)
- NO bullet lists, NO headers in email body
- Short paragraphs (2-4 sentences each)
- Total length: 300-400 words

OUTPUT FORMAT:
Return a JSON object with:
{{
  "subject": "The email subject line",
  "preview_text": "A 50-80 character preview snippet",
  "body_html": "<p>Full HTML content...</p>",
  "body_text": "Plain text version without HTML tags"
}}"""


def generate_email_content(
    category: NewsletterCategory,
    sequence_item: EmailSequenceItem,
    subject: str,
    client: anthropic.Anthropic
) -> Optional[GeneratedEmail]:
    """Generate content for a single email using Claude"""

    user_prompt = f"""Generate Email #{sequence_item.sequence_order} for the {category.name} newsletter.

SUBJECT LINE: {subject}

EMAIL PURPOSE: {sequence_item.purpose}
PSYCHOLOGICAL JOB: {sequence_item.psychological_job}

This is email {sequence_item.sequence_order} of 10 in the sequence, sent {sequence_item.delay_days} days after signup.

Write the email content now."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=get_system_prompt(category),
            messages=[{"role": "user", "content": user_prompt}]
        )

        # Extract JSON from response
        content = response.content[0].text

        # Try to parse as JSON
        # Handle case where response might have markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        data = json.loads(content.strip())

        return GeneratedEmail(
            category_slug=category.slug,
            subject=data["subject"],
            preview_text=data["preview_text"],
            body_html=data["body_html"],
            body_text=data["body_text"],
            sequence_order=sequence_item.sequence_order,
            delay_days=sequence_item.delay_days,
            status="draft"
        )

    except json.JSONDecodeError as e:
        print(f"  Error parsing JSON for email {sequence_item.sequence_order}: {e}")
        print(f"  Raw content: {content[:500]}...")
        return None
    except Exception as e:
        print(f"  Error generating email {sequence_item.sequence_order}: {e}")
        return None


def generate_category_sequence(
    category_slug: str,
    client: anthropic.Anthropic
) -> list[GeneratedEmail]:
    """Generate all 10 emails for a category"""

    category = CATEGORY_MAP.get(category_slug)
    if not category:
        print(f"Unknown category: {category_slug}")
        return []

    subjects = SUBJECT_TEMPLATES.get(category_slug, [])
    if not subjects:
        print(f"No subject templates for: {category_slug}")
        return []

    print(f"\n{category.icon} Generating {category.name} sequence...")

    emails = []
    for i, sequence_item in enumerate(EMAIL_SEQUENCE):
        subject = subjects[i] if i < len(subjects) else f"Email {sequence_item.sequence_order}"

        print(f"  [{sequence_item.sequence_order}/10] {subject}...")

        email = generate_email_content(category, sequence_item, subject, client)
        if email:
            emails.append(email)
            print(f"       Done ({len(email.body_text)} chars)")
        else:
            print(f"       FAILED")

    return emails


# =============================================================================
# API UPLOAD
# =============================================================================

def upload_email_to_api(
    email: GeneratedEmail,
    api_base: str,
    api_token: str
) -> bool:
    """Upload a single email to the admin API"""

    url = f"{api_base}/api/admin/newsletters/content"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }

    payload = {
        "category_slug": email.category_slug,
        "subject": email.subject,
        "preview_text": email.preview_text,
        "body_html": email.body_html,
        "body_text": email.body_text,
        "sequence_order": email.sequence_order,
        "delay_days": email.delay_days,
        "status": email.status
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            return True
        else:
            print(f"    API Error: {response.status_code} - {response.text[:200]}")
            return False

    except Exception as e:
        print(f"    Upload error: {e}")
        return False


def upload_category_emails(
    emails: list[GeneratedEmail],
    api_base: str,
    api_token: str
) -> tuple[int, int]:
    """Upload all emails for a category, return (success_count, fail_count)"""

    success = 0
    failed = 0

    for email in emails:
        if upload_email_to_api(email, api_base, api_token):
            success += 1
        else:
            failed += 1

    return success, failed


# =============================================================================
# FILE OUTPUT
# =============================================================================

def save_emails_to_file(emails: list[GeneratedEmail], output_dir: Path) -> str:
    """Save generated emails to a JSON file"""

    output_dir.mkdir(parents=True, exist_ok=True)

    if not emails:
        return ""

    category_slug = emails[0].category_slug
    output_file = output_dir / f"{category_slug}_sequence.json"

    data = {
        "category_slug": category_slug,
        "generated_count": len(emails),
        "emails": [asdict(e) for e in emails]
    }

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    return str(output_file)


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate newsletter email sequences"
    )
    parser.add_argument(
        "--category", "-c",
        help="Generate for a specific category slug"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Generate for all 12 categories"
    )
    parser.add_argument(
        "--upload", "-u",
        action="store_true",
        help="Upload generated content to admin API"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="output/newsletters",
        help="Output directory for JSON files"
    )
    parser.add_argument(
        "--api-base",
        default=os.getenv("SALARSU_API_BASE", "https://www.salars.net"),
        help="API base URL"
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List all available categories"
    )

    args = parser.parse_args()

    # List categories mode
    if args.list_categories:
        print("\nAvailable Newsletter Categories:")
        print("-" * 50)
        for cat in CATEGORIES:
            print(f"  {cat.icon} {cat.slug:15} - {cat.name}")
        return

    # Validate args
    if not args.category and not args.all:
        parser.print_help()
        print("\nError: Specify --category <slug> or --all")
        return

    # Initialize Claude client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return

    client = anthropic.Anthropic(api_key=api_key)

    # Determine categories to generate
    if args.all:
        categories_to_generate = [cat.slug for cat in CATEGORIES]
    else:
        categories_to_generate = [args.category]

    # Validate categories
    for slug in categories_to_generate:
        if slug not in CATEGORY_MAP:
            print(f"Error: Unknown category '{slug}'")
            print("Use --list-categories to see available options")
            return

    # Setup output directory
    output_dir = Path(args.output_dir)

    # Get API token if uploading
    api_token = None
    if args.upload:
        api_token = os.getenv("SALARSU_API_TOKEN")
        if not api_token:
            print("Error: SALARSU_API_TOKEN environment variable not set for upload")
            return

    # Generate sequences
    total_generated = 0
    total_uploaded = 0
    total_failed = 0

    for slug in categories_to_generate:
        emails = generate_category_sequence(slug, client)

        if emails:
            # Save to file
            output_file = save_emails_to_file(emails, output_dir)
            print(f"  Saved to: {output_file}")
            total_generated += len(emails)

            # Upload if requested
            if args.upload and api_token:
                print(f"  Uploading to API...")
                success, failed = upload_category_emails(
                    emails, args.api_base, api_token
                )
                total_uploaded += success
                total_failed += failed
                print(f"  Uploaded: {success}/{len(emails)}")

    # Summary
    print("\n" + "=" * 50)
    print("GENERATION COMPLETE")
    print("=" * 50)
    print(f"Categories processed: {len(categories_to_generate)}")
    print(f"Emails generated: {total_generated}")
    if args.upload:
        print(f"Emails uploaded: {total_uploaded}")
        print(f"Upload failures: {total_failed}")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()
