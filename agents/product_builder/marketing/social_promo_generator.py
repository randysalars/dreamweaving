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


@dataclass
class SocialPost:
    """Single social media post."""
    platform: Platform
    content: str
    hashtags: List[str] = field(default_factory=list)
    media_suggestion: str = ""
    hook: str = ""  # First line / attention grabber
    
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
class SocialPromoPackage:
    """Complete social promo package for a product."""
    product_title: str
    posts: List[SocialPost] = field(default_factory=list)
    
    def by_platform(self, platform: Platform) -> List[SocialPost]:
        return [p for p in self.posts if p.platform == platform]


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
        
        logger.info(f"✅ Generated {len(posts)} social posts")
        
        return SocialPromoPackage(
            product_title=title,
            posts=posts
        )
    
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
{chr(10).join(f'• {sol}' for sol in positioning.audience.current_solutions[:3])}

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
    
    def export_to_file(self, package: SocialPromoPackage, output_path: Path) -> str:
        """Export social package to markdown file."""
        content = f"# Social Promo Package: {package.product_title}\n\n"
        
        for platform in Platform:
            platform_posts = package.by_platform(platform)
            if platform_posts:
                content += f"## {platform.value.title()}\n\n"
                
                for i, post in enumerate(platform_posts, 1):
                    content += f"### Post {i}\n\n"
                    if post.hook:
                        content += f"**Hook:** {post.hook}\n\n"
                    content += f"**Characters:** {post.character_count}\n\n"
                    content += f"```\n{post.full_content}\n```\n\n"
                    if post.media_suggestion:
                        content += f"**Media:** {post.media_suggestion}\n\n"
                    content += "---\n\n"
        
        output_path.write_text(content)
        logger.info(f"✅ Social package exported: {output_path}")
        return str(output_path)
