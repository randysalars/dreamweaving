"""
Social Promo Generator
Creates promotional content for social media platforms.
"""

import logging
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, field
from enum import Enum

from ..core.llm import LLMClient
from ..schemas.positioning_brief import PositioningBrief

logger = logging.getLogger(__name__)


class Platform(Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"


class PostType(Enum):
    """Type of social post."""
    LAUNCH = "launch"
    PROBLEM = "problem"
    TRANSFORMATION = "transformation"
    THREAD = "thread"
    TESTIMONIAL = "testimonial"
    FAQ = "faq"
    TIP = "tip"
    STORY = "story"
    CTA = "cta"
    ENGAGEMENT = "engagement"


@dataclass
class SocialPost:
    """Single social media post."""
    platform: Platform
    content: str
    hashtags: List[str] = field(default_factory=list)
    media_suggestion: str = ""
    hook: str = ""  # First line / attention grabber
    post_type: PostType = PostType.LAUNCH
    scheduled_day: int = 0  # Day relative to launch (0 = launch day)
    best_time: str = ""  # Recommended posting time
    
    @property
    def character_count(self) -> int:
        return len(self.content)
    
    @property
    def full_content(self) -> str:
        """Content with hashtags appended."""
        if self.hashtags:
            return f"{self.content}\n\n{' '.join(f'#{h}' for h in self.hashtags)}"
        return self.content


@dataclass
class ContentCalendar:
    """Suggested posting schedule."""
    product_title: str
    launch_date_note: str = "Set your launch date, then follow this schedule"
    schedule: List[Dict] = field(default_factory=list)


@dataclass
class SocialPromoPackage:
    """Complete social promo package for a product."""
    product_title: str
    posts: List[SocialPost] = field(default_factory=list)
    calendar: ContentCalendar = None
    
    def by_platform(self, platform: Platform) -> List[SocialPost]:
        return [p for p in self.posts if p.platform == platform]
    
    def by_type(self, post_type: PostType) -> List[SocialPost]:
        return [p for p in self.posts if p.post_type == post_type]
    
    def by_day(self, day: int) -> List[SocialPost]:
        return [p for p in self.posts if p.scheduled_day == day]


class SocialPromoGenerator:
    """
    Generates promotional content for social media.
    
    Creates platform-optimized content:
    - Twitter/X: 280 chars, hooks, threads
    - LinkedIn: Professional, value-first
    - Instagram: Visual-first, story-driven
    - YouTube: Descriptions, titles, tags
    - TikTok: Hooks, trends, short-form
    """
    
    # Platform limits
    LIMITS = {
        Platform.TWITTER: 280,
        Platform.LINKEDIN: 3000,
        Platform.INSTAGRAM: 2200,
        Platform.YOUTUBE: 5000,
        Platform.TIKTOK: 150
    }
    
    def __init__(self, templates_dir: Path = None):
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "templates"
        self.llm = LLMClient()
    
    def generate_promo_package(
        self,
        title: str,
        positioning: PositioningBrief,
        chapters: List[Dict] = None
    ) -> SocialPromoPackage:
        """
        Generate a complete social promo package.
        
        Args:
            title: Product title
            positioning: Positioning brief
            chapters: Optional chapter details
            
        Returns:
            SocialPromoPackage with posts for all platforms
        """
        logger.info(f"📱 Generating social promo package for: {title}")
        
        posts = []
        
        # Twitter posts
        posts.extend(self._generate_twitter_posts(title, positioning))
        
        # LinkedIn posts
        posts.extend(self._generate_linkedin_posts(title, positioning))
        
        # Instagram captions
        posts.extend(self._generate_instagram_posts(title, positioning))
        
        # YouTube descriptions
        posts.extend(self._generate_youtube_content(title, positioning))
        
        # TikTok hooks
        posts.extend(self._generate_tiktok_posts(title, positioning))
        
        # Additional post types
        posts.extend(self._generate_testimonial_templates(title, positioning))
        posts.extend(self._generate_faq_posts(title, positioning))
        posts.extend(self._generate_engagement_posts(title, positioning))
        
        # Generate content calendar
        calendar = self._generate_content_calendar(title, posts)
        
        logger.info(f"✅ Generated {len(posts)} social posts")
        
        return SocialPromoPackage(
            product_title=title,
            posts=posts,
            calendar=calendar
        )
    
    def _get_current_solutions(self, positioning: PositioningBrief) -> List[str]:
        """Safely get current solutions from positioning audience."""
        audience = getattr(positioning, 'audience', None)
        if audience:
            solutions = getattr(audience, 'current_solutions', None)
            if solutions:
                return solutions[:3]
        # Default fallback
        return ["Books", "Online courses", "YouTube tutorials"]
    
    def _generate_twitter_posts(
        self, 
        title: str, 
        positioning: PositioningBrief
    ) -> List[SocialPost]:
        """Generate Twitter/X posts."""
        posts = []
        
        # Launch announcement
        posts.append(SocialPost(
            platform=Platform.TWITTER,
            hook="🚀 It's live.",
            content=f"""🚀 It's live.

{title} is now available.

If you want to {positioning.core_promise.lower()}, this is your path.

→ [Link in bio]""",
            hashtags=["launch", "newproduct"],
            media_suggestion="Product cover image or mockup"
        ))
        
        # Problem-focused post
        pain = positioning.audience.pain_points[0] if positioning.audience.pain_points else "stuck"
        posts.append(SocialPost(
            platform=Platform.TWITTER,
            hook=f"The real reason you're {pain.lower()}:",
            content=f"""The real reason you're {pain.lower()}:

It's not lack of information.
It's not lack of time.
It's not lack of motivation.

It's lack of a SYSTEM.

That's what I built. Link in bio.""",
            hashtags=[]
        ))
        
        # Thread starter (first tweet)
        posts.append(SocialPost(
            platform=Platform.TWITTER,
            hook="I spent 3 months building this.",
            content=f"""I spent 3 months building this.

Here's what's inside {title}:

🧵 (thread)""",
            hashtags=[],
            media_suggestion="Thread visual or carousel"
        ))
        
        # Transformation post
        posts.append(SocialPost(
            platform=Platform.TWITTER,
            hook="Before vs After",
            content=f"""Before: {positioning.audience.pain_points[0] if positioning.audience.pain_points else 'Confused'}

After: {positioning.core_promise}

The difference? A system that actually works.

{title} drops today.""",
            hashtags=[]
        ))
        
        return posts
    
    def _generate_linkedin_posts(
        self, 
        title: str, 
        positioning: PositioningBrief
    ) -> List[SocialPost]:
        """Generate LinkedIn posts."""
        posts = []
        
        # Launch post
        posts.append(SocialPost(
            platform=Platform.LINKEDIN,
            hook="Today I'm launching something I've worked on for months.",
            content=f"""Today I'm launching something I've worked on for months.

It's called {title}.

Here's why I built it:

I kept seeing people struggle with {positioning.audience.pain_points[0].lower() if positioning.audience.pain_points else 'the same problems'}.

They'd try everything:
{chr(10).join(f'• {sol}' for sol in self._get_current_solutions(positioning))}

But nothing stuck.

Because they were missing a core piece: {positioning.differentiator}

That's what {title} provides.

If you want to {positioning.core_promise.lower()}, link in comments.

Would love to hear your thoughts. 👇""",
            hashtags=["launch", "onlinelearning", "personaldevelopment"],
            media_suggestion="Professional product image"
        ))
        
        # Value post
        posts.append(SocialPost(
            platform=Platform.LINKEDIN,
            hook="Most advice about this topic is wrong.",
            content=f"""Most advice about {positioning.core_promise.lower().split()[0:3]} is wrong.

Here's what actually works:

1. {positioning.belief_shifts[0] if hasattr(positioning, 'belief_shifts') else 'Shift your mindset first'}
2. Build systems, not habits
3. Focus on outcomes, not outputs

I dive deep into this in my new program.

Link in comments if you want to learn more.""",
            hashtags=[]
        ))
        
        return posts
    
    def _generate_instagram_posts(
        self, 
        title: str, 
        positioning: PositioningBrief
    ) -> List[SocialPost]:
        """Generate Instagram captions."""
        posts = []
        
        # Carousel announcement
        posts.append(SocialPost(
            platform=Platform.INSTAGRAM,
            hook="New drop 🔥",
            content=f"""New drop 🔥

Introducing {title}

If you've been waiting for the right moment to finally {positioning.core_promise.lower()}...

This is it.

What's inside:
📚 Complete system
🎯 Step-by-step guidance  
💡 Practical frameworks
🎁 Bonus materials

Link in bio to get started.

Save this post ✨""",
            hashtags=["launch", "newprogram", "selfimprovement", "transformation", "goals"],
            media_suggestion="Carousel with key features"
        ))
        
        # Story-style post
        posts.append(SocialPost(
            platform=Platform.INSTAGRAM,
            hook="Real talk...",
            content=f"""Real talk...

A year ago I was {positioning.audience.pain_points[0].lower() if positioning.audience.pain_points else 'stuck'} too.

Now? {positioning.core_promise}

The difference wasn't motivation.
It wasn't discipline.
It wasn't willpower.

It was having the right SYSTEM.

That's what I created for you.

Link in bio 🔗""",
            hashtags=["realtalk", "transformation", "beforeandafter"],
            media_suggestion="Before/after or personal photo"
        ))
        
        return posts
    
    def _generate_youtube_content(
        self, 
        title: str, 
        positioning: PositioningBrief
    ) -> List[SocialPost]:
        """Generate YouTube descriptions and titles."""
        posts = []
        
        # Video description
        posts.append(SocialPost(
            platform=Platform.YOUTUBE,
            hook=f"How to {positioning.core_promise}",
            content=f"""How to {positioning.core_promise} (Complete System)

In this video, I'm breaking down the exact system I use to {positioning.core_promise.lower()}.

📌 TIMESTAMPS
0:00 - Introduction
1:00 - The Problem
3:00 - Why Most Advice Fails
5:00 - The System
10:00 - Step-by-Step Walkthrough
15:00 - Common Mistakes
18:00 - Next Steps

🔗 RESOURCES
→ {title}: [LINK]
→ Free Guide: [LINK]

📱 CONNECT
→ Instagram: @yourhandle
→ Twitter: @yourhandle

If this was helpful, hit the like button and subscribe for more.

#shorts #{positioning.core_promise.split()[0].lower()}""",
            hashtags=[],
            media_suggestion="Engaging thumbnail with text overlay"
        ))
        
        # Video title options
        posts.append(SocialPost(
            platform=Platform.YOUTUBE,
            hook="Title Options",
            content=f"""VIDEO TITLE OPTIONS:

1. How to {positioning.core_promise} (Even If You've Failed Before)

2. I {positioning.core_promise.replace('You will ', '')} in 30 Days — Here's How

3. Stop {positioning.audience.pain_points[0].lower() if positioning.audience.pain_points else 'Making This Mistake'}: Do This Instead

4. The ONLY System You Need to {positioning.core_promise.replace('You will ', '')}

5. Why 95% of People Fail at {positioning.core_promise.split()[-1].title()} (And How to Succeed)""",
            hashtags=[],
            media_suggestion=""
        ))
        
        return posts
    
    def _generate_tiktok_posts(
        self, 
        title: str, 
        positioning: PositioningBrief
    ) -> List[SocialPost]:
        """Generate TikTok hooks and captions."""
        posts = []
        
        # Hook 1: Problem callout
        pain = positioning.audience.pain_points[0] if positioning.audience.pain_points else "stuck"
        posts.append(SocialPost(
            platform=Platform.TIKTOK,
            hook="POV:",
            content=f"""POV: You finally found a system for {positioning.core_promise.lower().split()[-2:]}

Yes, it actually works 🎯

Link in bio""",
            hashtags=["fyp", "learnontiktok"],
            post_type=PostType.PROBLEM,
            scheduled_day=0,
            best_time="7pm-9pm"
        ))
        
        # Hook 2: Transformation
        posts.append(SocialPost(
            platform=Platform.TIKTOK,
            hook="This changed everything",
            content=f"""This changed everything for my {positioning.core_promise.split()[-1].lower()} 👀

#storytime #transformation""",
            hashtags=["storytime", "transformation"],
            post_type=PostType.TRANSFORMATION,
            scheduled_day=1,
            best_time="12pm-2pm"
        ))
        
        # Hook 3: Quick tip
        posts.append(SocialPost(
            platform=Platform.TIKTOK,
            hook="The #1 mistake",
            content=f"""The #1 mistake people make with {positioning.core_promise.split()[-1].lower()}:

They try too hard 🤦

Here's the fix 👇""",
            hashtags=["tips", "advice"],
            post_type=PostType.TIP,
            scheduled_day=3,
            best_time="5pm-7pm"
        ))
        
        return posts
    
    def _generate_testimonial_templates(
        self, 
        title: str, 
        positioning: PositioningBrief
    ) -> List[SocialPost]:
        """Generate testimonial post templates."""
        posts = []
        
        # Twitter testimonial template
        posts.append(SocialPost(
            platform=Platform.TWITTER,
            hook="[TESTIMONIAL TEMPLATE]",
            content=f""""[Student name] just messaged me this:

'[Specific result they achieved]'

This is what {title} is about.

Not theory. Results.

[Link]""",
            hashtags=[],
            post_type=PostType.TESTIMONIAL,
            scheduled_day=5,
            best_time="9am-11am",
            media_suggestion="Screenshot of testimonial"
        ))
        
        # Instagram testimonial
        posts.append(SocialPost(
            platform=Platform.INSTAGRAM,
            hook="[TESTIMONIAL TEMPLATE]",
            content=f"""Got this message this morning and had to share 🥹

"[Quote from customer about their transformation]"

This is why I do what I do.

Seeing people {positioning.core_promise.lower()} makes every late night worth it.

[Customer name], thank you for trusting me with your journey. 🙏

If you're ready for your own transformation → Link in bio""",
            hashtags=["testimonial", "results", "clientlove"],
            post_type=PostType.TESTIMONIAL,
            scheduled_day=7,
            best_time="6pm-8pm",
            media_suggestion="Screenshot or video testimonial"
        ))
        
        return posts
    
    def _generate_faq_posts(
        self, 
        title: str, 
        positioning: PositioningBrief
    ) -> List[SocialPost]:
        """Generate FAQ-style posts from objections."""
        posts = []
        
        objections = getattr(positioning, 'objections', None)
        if objections:
            for i, obj in enumerate(objections[:3]):
                obj_text = getattr(obj, 'objection', str(obj)) if hasattr(obj, 'objection') else (obj.get('objection', str(obj)) if isinstance(obj, dict) else str(obj))
                preemption = getattr(obj, 'preemption', 'I totally understand.') if hasattr(obj, 'preemption') else (obj.get('preemption', 'I totally understand.') if isinstance(obj, dict) else 'I totally understand.')
                posts.append(SocialPost(
                    platform=Platform.TWITTER,
                    hook=f"FAQ: {obj_text}",
                    content=f""""{obj_text}"

I hear this a lot.

Here's my answer:

{preemption}

Does that help?""",
                    hashtags=[],
                    post_type=PostType.FAQ,
                    scheduled_day=4 + i,
                    best_time="2pm-4pm"
                ))
        
        return posts
    
    def _generate_engagement_posts(
        self, 
        title: str, 
        positioning: PositioningBrief
    ) -> List[SocialPost]:
        """Generate engagement-focused posts."""
        posts = []
        
        # Question post
        posts.append(SocialPost(
            platform=Platform.TWITTER,
            hook="Quick question:",
            content=f"""Quick question:

What's the #1 thing holding you back from {positioning.core_promise.lower()}?

Reply below 👇

(I read every response)""",
            hashtags=[],
            post_type=PostType.ENGAGEMENT,
            scheduled_day=-1,  # Pre-launch
            best_time="10am-12pm"
        ))
        
        # Poll post (LinkedIn)
        posts.append(SocialPost(
            platform=Platform.LINKEDIN,
            hook="Be honest:",
            content=f"""Be honest: 

What's your biggest challenge with {positioning.core_promise.split()[-1].lower()}?

A) Not enough time
B) Don't know where to start  
C) Tried everything, nothing works
D) Other (comment below)

Vote below and I'll share what's worked for me. 👇""",
            hashtags=[],
            post_type=PostType.ENGAGEMENT,
            scheduled_day=-2,  # Pre-launch
            best_time="8am-10am"
        ))
        
        # Behind the scenes
        posts.append(SocialPost(
            platform=Platform.INSTAGRAM,
            hook="Behind the scenes 🎬",
            content=f"""Behind the scenes 🎬

Working on something big...

Can't wait to share it with you.

Drop a 🔥 if you want first access.""",
            hashtags=["bts", "comingsoon", "sneakpeek"],
            post_type=PostType.ENGAGEMENT,
            scheduled_day=-3,
            best_time="7pm-9pm",
            media_suggestion="Work-in-progress screenshot or video"
        ))
        
        return posts
    
    def _generate_content_calendar(
        self, 
        title: str, 
        posts: List[SocialPost]
    ) -> ContentCalendar:
        """Generate a content calendar from posts."""
        schedule = []
        
        # Group by day
        days = sorted(set(p.scheduled_day for p in posts if p.scheduled_day != 0))
        
        # Pre-launch
        pre_launch = [p for p in posts if p.scheduled_day < 0]
        if pre_launch:
            for d in sorted(set(p.scheduled_day for p in pre_launch)):
                day_posts = [p for p in posts if p.scheduled_day == d]
                schedule.append({
                    "day": f"L{d}",  # e.g., L-3, L-2, L-1
                    "label": f"{abs(d)} days before launch",
                    "posts": [
                        {
                            "platform": p.platform.value,
                            "type": p.post_type.value,
                            "best_time": p.best_time or "varies",
                            "hook": p.hook[:50] + "..." if len(p.hook) > 50 else p.hook
                        }
                        for p in day_posts
                    ]
                })
        
        # Launch day
        launch_posts = [p for p in posts if p.scheduled_day == 0]
        if launch_posts:
            schedule.append({
                "day": "L0",
                "label": "🚀 LAUNCH DAY",
                "posts": [
                    {
                        "platform": p.platform.value,
                        "type": p.post_type.value,
                        "best_time": p.best_time or "varies",
                        "hook": p.hook[:50] + "..." if len(p.hook) > 50 else p.hook
                    }
                    for p in launch_posts
                ]
            })
        
        # Post-launch
        for d in range(1, 8):
            day_posts = [p for p in posts if p.scheduled_day == d]
            if day_posts:
                schedule.append({
                    "day": f"L+{d}",
                    "label": f"{d} day{'s' if d > 1 else ''} after launch",
                    "posts": [
                        {
                            "platform": p.platform.value,
                            "type": p.post_type.value,
                            "best_time": p.best_time or "varies",
                            "hook": p.hook[:50] + "..." if len(p.hook) > 50 else p.hook
                        }
                        for p in day_posts
                    ]
                })
        
        return ContentCalendar(
            product_title=title,
            schedule=schedule
        )
    
    def export_to_file(self, package: SocialPromoPackage, output_path: Path) -> str:
        """Export social package to markdown file."""
        content = f"# Social Promo Package: {package.product_title}\n\n"
        
        # Content Calendar section
        if package.calendar and package.calendar.schedule:
            content += "## 📅 Content Calendar\n\n"
            content += f"*{package.calendar.launch_date_note}*\n\n"
            content += "| Day | Platform | Type | Best Time | Hook |\n"
            content += "|-----|----------|------|-----------|------|\n"
            for day_entry in package.calendar.schedule:
                for post in day_entry.get("posts", []):
                    content += f"| {day_entry['day']} | {post['platform'].title()} | {post['type']} | {post['best_time']} | {post['hook']} |\n"
            content += "\n---\n\n"
        
        # Posts by platform
        for platform in Platform:
            platform_posts = package.by_platform(platform)
            if platform_posts:
                content += f"## {platform.value.title()}\n\n"
                
                for i, post in enumerate(platform_posts, 1):
                    content += f"### Post {i}: {post.post_type.value.title()}\n\n"
                    if post.hook:
                        content += f"**Hook:** {post.hook}\n\n"
                    if post.scheduled_day != 0:
                        if post.scheduled_day < 0:
                            content += f"**Schedule:** {abs(post.scheduled_day)} days before launch\n\n"
                        else:
                            content += f"**Schedule:** Day {post.scheduled_day} after launch\n\n"
                    if post.best_time:
                        content += f"**Best Time:** {post.best_time}\n\n"
                    content += f"**Characters:** {post.character_count}\n\n"
                    content += f"```\n{post.full_content}\n```\n\n"
                    if post.media_suggestion:
                        content += f"**Media:** {post.media_suggestion}\n\n"
                    content += "---\n\n"
        
        output_path.write_text(content)
        logger.info(f"✅ Social package exported: {output_path}")
        return str(output_path)

