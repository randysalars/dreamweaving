"""
Email Sequence Generator
Creates automated email sequences for product launches and nurturing.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from ..core.llm import LLMClient
from ..schemas.positioning_brief import PositioningBrief

logger = logging.getLogger(__name__)


class EmailType(Enum):
    WELCOME = "welcome"
    VALUE = "value"
    STORY = "story"
    OBJECTION = "objection"
    SOCIAL_PROOF = "social_proof"
    URGENCY = "urgency"
    LAST_CHANCE = "last_chance"
    ABANDONED = "abandoned"


@dataclass
class Email:
    """Single email in a sequence."""
    type: EmailType
    subject: str
    preview_text: str
    body: str
    cta_text: str = "Learn More"
    cta_url: str = ""
    send_delay_hours: int = 0  # Hours after sequence start


@dataclass
class EmailSequence:
    """Complete email sequence."""
    name: str
    description: str
    emails: List[Email] = field(default_factory=list)
    
    @property
    def total_days(self) -> int:
        if not self.emails:
            return 0
        return max(e.send_delay_hours for e in self.emails) // 24


class EmailSequenceGenerator:
    """
    Generates automated email sequences for product launches.
    
    Sequence types:
    - Welcome sequence (post-signup)
    - Launch sequence (product launch)
    - Abandoned cart sequence
    - Nurture sequence (ongoing value)
    """
    
    def __init__(self, templates_dir: Path = None):
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "templates"
        self.llm = LLMClient()
    
    def generate_welcome_sequence(
        self,
        product_title: str,
        positioning: PositioningBrief,
        num_emails: int = 5
    ) -> EmailSequence:
        """
        Generate a welcome/nurture sequence.
        
        Day 0: Welcome + quick win
        Day 1: Share your story
        Day 3: Core value delivery
        Day 5: Address main objection
        Day 7: Soft pitch
        """
        logger.info(f"📧 Generating welcome sequence for: {product_title}")
        
        emails = []
        
        # Email 1: Welcome + Quick Win
        emails.append(Email(
            type=EmailType.WELCOME,
            subject=f"Welcome! Here's your first step to {self._extract_desire(positioning)}",
            preview_text="Plus a quick win you can use today...",
            body=self._generate_welcome_email(positioning),
            cta_text="Get Started",
            send_delay_hours=0
        ))
        
        # Email 2: Story
        emails.append(Email(
            type=EmailType.STORY,
            subject="Why I created this (my story)",
            preview_text="It wasn't always this way...",
            body=self._generate_story_email(positioning),
            send_delay_hours=24
        ))
        
        # Email 3: Value
        emails.append(Email(
            type=EmailType.VALUE,
            subject=f"The #1 mistake people make with {self._extract_topic(positioning)}",
            preview_text="And how to avoid it...",
            body=self._generate_value_email(positioning),
            cta_text="Learn More",
            send_delay_hours=72
        ))
        
        # Email 4: Objection Handling
        objections = getattr(positioning, 'objections', None)
        if objections:
            main_objection = objections[0]
            emails.append(Email(
                type=EmailType.OBJECTION,
                subject=f'"{getattr(main_objection, "objection", str(main_objection))}" — Let me address that',
                preview_text="Because I hear this a lot...",
                body=self._generate_objection_email(main_objection),
                send_delay_hours=120
            ))
        
        # Email 5: Soft Pitch
        emails.append(Email(
            type=EmailType.VALUE,
            subject=f"Ready to {positioning.core_promise.lower()}?",
            preview_text=f"Here's what {product_title} includes...",
            body=self._generate_pitch_email(product_title, positioning),
            cta_text="See What's Inside",
            send_delay_hours=168
        ))
        
        return EmailSequence(
            name=f"{product_title} Welcome Sequence",
            description="5-email welcome sequence for new subscribers",
            emails=emails
        )
    
    def generate_launch_sequence(
        self,
        product_title: str,
        positioning: PositioningBrief,
        launch_duration_days: int = 7
    ) -> EmailSequence:
        """
        Generate a product launch sequence.
        
        Pre-launch: Anticipation building
        Day 1: Doors open
        Day 2: Deep value
        Day 4: Social proof
        Day 6: Urgency
        Day 7: Last chance
        """
        logger.info(f"🚀 Generating launch sequence for: {product_title}")
        
        emails = []
        
        # Day -1: Pre-launch teaser
        emails.append(Email(
            type=EmailType.VALUE,
            subject=f"Something new is coming tomorrow...",
            preview_text=f"Hint: It's about {self._extract_topic(positioning)}",
            body=f"""
Hi there,

Tomorrow I'm releasing something I've been working on for months.

It's called {product_title}, and it's designed to help you {positioning.core_promise.lower()}.

Keep an eye on your inbox tomorrow.

Talk soon,
[Your Name]
""",
            send_delay_hours=0
        ))
        
        # Day 0: Launch
        emails.append(Email(
            type=EmailType.VALUE,
            subject=f"🎉 {product_title} is LIVE",
            preview_text=f"Your path to {positioning.core_promise.lower()} starts here",
            body=self._generate_launch_email(product_title, positioning),
            cta_text="Get Instant Access",
            send_delay_hours=24
        ))
        
        # Day 2: Deep Value
        emails.append(Email(
            type=EmailType.VALUE,
            subject=f"What makes {product_title} different",
            preview_text=positioning.differentiator[:50],
            body=f"""
Hey,

Quick question: {self._get_first_objection_text(positioning)}

I get it.

Here's why {product_title} is different:

{positioning.differentiator}

{self._format_features(positioning)}

See for yourself:
[CTA]

[Your Name]
""",
            cta_text="See What's Inside",
            send_delay_hours=72
        ))
        
        # Day 4: Social Proof
        emails.append(Email(
            type=EmailType.SOCIAL_PROOF,
            subject="What students are saying...",
            preview_text="Real results from real people",
            body=f"""
Hey,

I wanted to share some messages I've received about {product_title}:

"[Testimonial 1]"
— [Name], [Role]

"[Testimonial 2]"
— [Name], [Role]

These aren't cherry-picked. They're representative of what happens when you {positioning.core_promise.lower()}.

Ready to join them?
[CTA]

[Your Name]
""",
            cta_text="Join Them",
            send_delay_hours=120
        ))
        
        # Day 6: Urgency
        emails.append(Email(
            type=EmailType.URGENCY,
            subject=f"⏰ {product_title} closes in 48 hours",
            preview_text="After that, doors close",
            body=f"""
Just a heads up:

{product_title} closes to new students in 48 hours.

After that, I'm closing enrollment to focus on supporting current students.

If you've been on the fence, now's the time to decide.

→ Will you keep doing what you're doing?
→ Or will you finally {positioning.core_promise.lower()}?

[CTA]

[Your Name]

P.S. Remember, there's a 30-day money-back guarantee. Zero risk.
""",
            cta_text="Enroll Before Doors Close",
            send_delay_hours=168
        ))
        
        # Day 7: Last Chance
        emails.append(Email(
            type=EmailType.LAST_CHANCE,
            subject=f"[FINAL] Doors closing in 3 hours",
            preview_text=f"Last chance for {product_title}",
            body=f"""
This is it.

{product_title} closes in 3 hours.

After that, you'll have to wait until next time (and I don't know when that will be).

If you want to {positioning.core_promise.lower()}, this is your moment.

[CTA]

See you inside (I hope),
[Your Name]
""",
            cta_text="Get In Before It's Gone",
            send_delay_hours=192
        ))
        
        return EmailSequence(
            name=f"{product_title} Launch Sequence",
            description=f"{launch_duration_days}-day launch sequence",
            emails=emails
        )
    
    def _extract_desire(self, positioning: PositioningBrief) -> str:
        """Extract the core desire from positioning."""
        promise = positioning.core_promise.lower()
        if promise.startswith("you will "):
            return promise[9:]
        return promise
    
    def _extract_topic(self, positioning: PositioningBrief) -> str:
        """Extract the main topic."""
        # Simple extraction from positioning
        words = positioning.core_promise.split()
        if len(words) > 3:
            return " ".join(words[-3:])
        return positioning.core_promise
    
    def _get_first_objection_text(self, positioning: PositioningBrief) -> str:
        """Safely get the first objection text."""
        objections = getattr(positioning, 'objections', None)
        if objections and len(objections) > 0:
            obj = objections[0]
            # Handle both dict-like and object-like access
            if hasattr(obj, 'objection'):
                return obj.objection
            elif isinstance(obj, dict):
                return obj.get('objection', str(obj))
            return str(obj)
        return "Have you been burned by courses before?"
    
    def _generate_welcome_email(self, positioning: PositioningBrief) -> str:
        """Generate welcome email body."""
        return f"""
Welcome! I'm so glad you're here.

You signed up because you want to {positioning.core_promise.lower()}.

And I'm going to help you get there.

But first, here's a quick win you can use TODAY:

[Quick Win Tip]

Try this, and reply to let me know how it goes.

Talk soon,
[Your Name]

P.S. Keep an eye on your inbox. Tomorrow I'll share something personal...
"""
    
    def _generate_story_email(self, positioning: PositioningBrief) -> str:
        """Generate story email body."""
        pain = positioning.audience.pain_points[0] if positioning.audience.pain_points else "stuck"
        return f"""
Hey,

I wanted to share something personal with you today.

Years ago, I was exactly where you are now.

{pain}. Sound familiar?

I tried everything. Books. Courses. Advice from "experts."

Nothing worked.

Until I discovered [key insight].

That's when everything changed.

And that's why I created what I'm going to share with you.

More on that soon.

[Your Name]
"""
    
    def _generate_value_email(self, positioning: PositioningBrief) -> str:
        """Generate value email body."""
        return f"""
Quick question:

What's the biggest thing holding you back from {positioning.core_promise.lower()}?

For most people, it's one of these:

{chr(10).join(f"- {pain}" for pain in positioning.audience.pain_points[:3])}

Here's the thing...

[Value insight]

[Actionable tip]

Try this and let me know how it goes.

[Your Name]
"""
    
    def _generate_objection_email(self, objection) -> str:
        """Generate objection-handling email body."""
        return f"""
I hear this a lot:

"{objection.objection}"

And I get it. Totally valid concern.

Here's my response:

{objection.preemption}

Does that help?

If you have other questions, just reply to this email. I read everything.

[Your Name]
"""
    
    def _generate_pitch_email(self, title: str, positioning: PositioningBrief) -> str:
        """Generate soft pitch email body."""
        return f"""
Over the past few days, I've shared:

- [Recap point 1]
- [Recap point 2]
- [Recap point 3]

But if you want the complete system to {positioning.core_promise.lower()}, I've put together something special.

It's called {title}.

Here's what's inside:
[Brief overview]

Interested? Check it out here:
[CTA]

[Your Name]
"""
    
    def _generate_launch_email(self, title: str, positioning: PositioningBrief) -> str:
        """Generate launch day email body."""
        return f"""
It's here.

{title} is officially live.

This is the complete system to {positioning.core_promise.lower()}.

Inside, you'll get:
{self._format_features(positioning)}

Plus:
- Full lifetime access
- 30-day money-back guarantee
- [Bonus 1]
- [Bonus 2]

Ready to get started?

[CTA]

[Your Name]

P.S. Doors are only open for [X days]. Don't wait.
"""
    
    def _format_features(self, positioning: PositioningBrief) -> str:
        """Format features as a list."""
        return "\n".join([
            f"✓ {positioning.differentiator}",
            f"✓ Designed for {positioning.audience.primary_persona}",
            f"✓ Step-by-step system"
        ])
    
    def export_to_file(self, sequence: EmailSequence, output_path: Path) -> str:
        """Export sequence to a markdown file."""
        content = f"# {sequence.name}\n\n"
        content += f"{sequence.description}\n\n"
        content += f"**Total Duration:** {sequence.total_days} days\n\n"
        content += "---\n\n"
        
        for i, email in enumerate(sequence.emails, 1):
            days = email.send_delay_hours // 24
            content += f"## Email {i}: {email.type.value.title()}\n\n"
            content += f"**Send:** Day {days}\n\n"
            content += f"**Subject:** {email.subject}\n\n"
            content += f"**Preview:** {email.preview_text}\n\n"
            content += f"**CTA:** {email.cta_text}\n\n"
            content += "### Body\n\n"
            content += f"```\n{email.body}\n```\n\n"
            content += "---\n\n"
        
        output_path.write_text(content)
        logger.info(f"✅ Email sequence exported: {output_path}")
        return str(output_path)
