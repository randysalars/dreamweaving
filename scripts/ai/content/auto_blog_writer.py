"""
Auto Blog Writer Agent.

Generates blog posts from Dreamweaving session themes for salars.net.
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


@dataclass
class BlogPost:
    """Represents a generated blog post."""
    title: str
    slug: str
    meta_description: str
    content: str
    tags: List[str]
    category: str
    session_name: Optional[str] = None
    featured_image: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_frontmatter(self) -> str:
        """Generate frontmatter for the blog post."""
        frontmatter = {
            'title': self.title,
            'slug': self.slug,
            'description': self.meta_description,
            'tags': self.tags,
            'category': self.category,
            'date': self.created_at.isoformat(),
            'session': self.session_name,
        }
        if self.featured_image:
            frontmatter['image'] = self.featured_image
        return yaml.dump(frontmatter, default_flow_style=False)

    def to_markdown(self) -> str:
        """Generate full markdown with frontmatter."""
        return f"---\n{self.to_frontmatter()}---\n\n{self.content}"


class AutoBlogWriter:
    """
    Auto Blog Writer Agent.

    Generates blog posts from Dreamweaving session themes,
    leveraging the session manifest and knowledge base.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parents[3]
        self.knowledge_path = self.project_root / 'knowledge'
        self.sessions_path = self.project_root / 'sessions'
        self.output_path = self.project_root / 'output' / 'blog_drafts'
        self.output_path.mkdir(parents=True, exist_ok=True)

    def _load_session_manifest(self, session_name: str) -> Optional[Dict[str, Any]]:
        """Load manifest from session directory."""
        manifest_path = self.sessions_path / session_name / 'manifest.yaml'
        if not manifest_path.exists():
            return None
        with open(manifest_path, 'r') as f:
            return yaml.safe_load(f)

    def _load_lessons(self) -> List[Dict[str, Any]]:
        """Load lessons learned for content ideas."""
        lessons_path = self.knowledge_path / 'lessons_learned.yaml'
        if not lessons_path.exists():
            return []
        with open(lessons_path, 'r') as f:
            data = yaml.safe_load(f) or {}
            return data.get('lessons', [])

    def _generate_slug(self, title: str) -> str:
        """Generate URL-safe slug from title."""
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

    def generate_from_session(
        self,
        session_name: str,
        blog_type: str = 'experience',
        custom_angle: Optional[str] = None
    ) -> Optional[BlogPost]:
        """
        Generate a blog post from a session.

        Args:
            session_name: Name of the session directory
            blog_type: Type of blog post:
                - 'experience': What to expect from this journey
                - 'deep_dive': Deep exploration of the theme
                - 'benefits': Benefits and outcomes
                - 'technique': Hypnotic techniques explained
            custom_angle: Custom angle/focus for the post

        Returns:
            BlogPost object or None if session not found
        """
        manifest = self._load_session_manifest(session_name)
        if not manifest:
            return None

        session = manifest.get('session', {})
        title = session.get('title', session_name)
        theme = session.get('theme', '')
        description = session.get('description', '')
        desired_outcome = session.get('desired_outcome', 'transformation')
        archetypes = session.get('archetypes', [])
        journey_family = session.get('journey_family', '')

        # Generate blog content based on type
        if blog_type == 'experience':
            blog_title = f"What to Expect: {title}"
            content = self._generate_experience_post(
                title, theme, description, desired_outcome, archetypes
            )
        elif blog_type == 'deep_dive':
            blog_title = f"Deep Dive: The Symbolism of {theme or title}"
            content = self._generate_deep_dive_post(
                title, theme, description, archetypes, journey_family
            )
        elif blog_type == 'benefits':
            blog_title = f"The Transformative Power of {title}"
            content = self._generate_benefits_post(
                title, theme, description, desired_outcome
            )
        elif blog_type == 'technique':
            blog_title = f"Hypnotic Techniques in {title}"
            content = self._generate_technique_post(
                title, theme, description
            )
        else:
            blog_title = custom_angle or f"Journey into {title}"
            content = self._generate_custom_post(
                title, theme, description, custom_angle
            )

        # Determine category
        category = self._determine_category(desired_outcome, journey_family)

        # Generate tags
        tags = self._generate_tags(
            theme, desired_outcome, archetypes, journey_family
        )

        # Create meta description
        meta_description = self._generate_meta_description(
            blog_title, theme, desired_outcome
        )

        return BlogPost(
            title=blog_title,
            slug=self._generate_slug(blog_title),
            meta_description=meta_description,
            content=content,
            tags=tags,
            category=category,
            session_name=session_name,
        )

    def _generate_experience_post(
        self,
        title: str,
        theme: str,
        description: str,
        outcome: str,
        archetypes: List[str]
    ) -> str:
        """Generate 'What to Expect' style blog post."""
        archetype_text = ', '.join(archetypes[:3]) if archetypes else 'profound guides'

        return f"""# What to Expect: {title}

## Preparing for Your Journey

{description or f"This transformative journey explores the depths of {theme}, guiding you through a profound inner experience designed to support your {outcome}."}

### The Experience

When you begin this session, you'll be gently guided into a state of deep relaxation.
The journey unfolds through carefully crafted imagery and suggestion, allowing your
subconscious mind to engage with powerful symbolic content.

### What You Might Experience

- **Deep Relaxation**: A profound sense of peace and letting go
- **Vivid Imagery**: Rich visualizations that speak to your inner wisdom
- **Emotional Processing**: Safe space to process and release
- **Insight**: New understanding arising naturally
- **Transformation**: Shifts that continue to unfold after the session

### The Archetypes You'll Meet

During this journey, you may encounter {archetype_text}. These archetypal presences
serve as guides, offering wisdom and support as you navigate the inner landscape.

### After the Journey

Take time to rest after completing this session. You may wish to:
- Journal about your experience
- Drink water and ground yourself
- Notice how you feel over the coming days
- Return to the journey when called

### Is This Journey Right for You?

This session is ideal for those seeking {outcome}. If you're new to hypnotic journeying,
you'll find gentle guidance throughout. If you're experienced, you'll appreciate the
depth and sophistication of the symbolic content.

---

*Ready to begin? Find a quiet space, get comfortable, and let the journey unfold.*
"""

    def _generate_deep_dive_post(
        self,
        title: str,
        theme: str,
        description: str,
        archetypes: List[str],
        journey_family: str
    ) -> str:
        """Generate deep dive into symbolism blog post."""
        return f"""# Deep Dive: The Symbolism of {theme or title}

## Exploring the Symbolic Landscape

{theme or title} carries profound symbolic weight across cultures and traditions.
In this exploration, we'll examine the layers of meaning woven into this journey.

### The Core Symbols

The imagery in this journey draws from universal symbolic language:

**Primary Theme**: {theme or 'Inner transformation'}

{description if description else f"This journey works with the archetype of {theme}, a powerful symbol found across spiritual traditions."}

### Archetypal Presences

{self._format_archetype_section(archetypes)}

### The Journey Structure

This journey follows the {journey_family or 'classic transformational'} pattern,
a structure found in myths and initiation rites across cultures:

1. **Separation**: Leaving ordinary consciousness
2. **Descent/Journey**: Encountering the symbolic realm
3. **Transformation**: The central experience
4. **Integration**: Bringing wisdom back
5. **Return**: Grounded renewal

### Psychological Depth

From a depth psychology perspective, the symbols in this journey speak directly
to the unconscious mind. The imagery bypasses the critical faculty, allowing
genuine transformation to occur at a deep level.

### Spiritual Dimensions

For those attuned to spiritual dimensions, this journey offers contact with
timeless archetypal energies. The symbols serve as doorways to direct experience
of the sacred.

---

*The symbols are alive. They speak differently to each person.
What will they reveal to you?*
"""

    def _generate_benefits_post(
        self,
        title: str,
        theme: str,
        description: str,
        outcome: str
    ) -> str:
        """Generate benefits-focused blog post."""
        benefits_map = {
            'healing': [
                'Deep emotional release',
                'Nervous system regulation',
                'Self-compassion development',
                'Trauma integration',
            ],
            'transformation': [
                'Identity evolution',
                'Breakthrough insights',
                'Pattern interruption',
                'New possibilities opening',
            ],
            'empowerment': [
                'Confidence building',
                'Personal power reclamation',
                'Boundary strengthening',
                'Authentic expression',
            ],
            'relaxation': [
                'Stress reduction',
                'Sleep improvement',
                'Mental clarity',
                'Physical tension release',
            ],
            'spiritual_growth': [
                'Expanded awareness',
                'Connection to source',
                'Purpose clarity',
                'Inner peace',
            ],
        }

        benefits = benefits_map.get(outcome, benefits_map['transformation'])
        benefits_list = '\n'.join([f"- **{b}**" for b in benefits])

        return f"""# The Transformative Power of {title}

## Why This Journey Matters

In our fast-paced world, genuine transformation is rare. {title} offers
something precious: dedicated time and space for deep inner work.

### Key Benefits

{benefits_list}

### The Science of Transformation

Hypnotic states activate the brain's natural capacity for change. During this
journey, your brainwaves shift from alert beta to relaxed alpha and theta states,
where the mind becomes highly receptive to positive suggestion and imagery.

### Real Transformation

This isn't passive entertainment. The journey creates conditions for genuine
psychological and spiritual transformation:

1. **Safety**: A protected space for inner exploration
2. **Depth**: Access to unconscious resources
3. **Integration**: Experiences are woven into daily life
4. **Lasting Change**: Benefits continue to unfold over time

### What Makes This Different

Unlike surface-level relaxation, {title} works at the level of symbol and
archetype. These deep structures of the psyche are where real change happens.

### Your Transformation Awaits

Whether you're seeking {outcome} or simply curious about deep inner work,
this journey offers a doorway. The benefits are cumulative - each session
builds on the last.

---

*Your transformation is already beginning. The journey is just catching up.*
"""

    def _generate_technique_post(
        self,
        title: str,
        theme: str,
        description: str
    ) -> str:
        """Generate technique explanation blog post."""
        return f"""# Hypnotic Techniques in {title}

## The Craft Behind the Journey

{title} employs sophisticated hypnotic techniques refined over decades of
research and practice. Here's a glimpse into the craft.

### Language Patterns

**Embedded Commands**: Throughout the journey, carefully crafted suggestions
are woven into the narrative. Your unconscious mind receives these while
your conscious mind follows the story.

**Milton Model**: Named after Milton Erickson, these artfully vague language
patterns allow your mind to fill in personal meaning, making the journey
uniquely yours.

### Trance Induction

The journey uses progressive relaxation combined with breath awareness to
naturally guide you into a receptive state. This isn't about losing control -
it's about accessing deeper awareness.

### Symbolic Architecture

The imagery isn't random. Each symbol is chosen for its archetypal resonance,
speaking directly to the unconscious mind in its native language.

### Audio Elements

**Binaural Beats**: Precisely calibrated frequencies guide your brainwaves
into optimal states for deep work.

**Voice Processing**: The voice is processed to enhance hypnotic depth while
maintaining clarity and warmth.

### Safety Integration

Built into every journey are:
- Clear return pathways
- Grounding elements
- Post-hypnotic anchors for integration
- Safety suggestions for wellbeing

---

*The techniques serve the transformation. The transformation serves your growth.*
"""

    def _generate_custom_post(
        self,
        title: str,
        theme: str,
        description: str,
        angle: Optional[str]
    ) -> str:
        """Generate custom angle blog post."""
        return f"""# {angle or f'Journey into {title}'}

## A Personal Exploration

{description or f"This journey explores {theme or title} through carefully crafted hypnotic narrative."}

### The Invitation

Every journey begins with an invitation. Not a command, but an opening.
{title} offers this opening now.

### What Awaits

Within this experience, you'll find:

- Deep relaxation and peace
- Meaningful symbolic encounters
- Space for insight and integration
- A doorway to your own wisdom

### Your Unique Journey

While the journey has a shape, the meaning it holds for you is entirely personal.
The symbols will speak to your specific situation, your questions, your growth.

### Beginning

Find a quiet space. Get comfortable. And when you're ready, begin.

---

*The journey awaits. Your transformation awaits. You are ready.*
"""

    def _format_archetype_section(self, archetypes: List[str]) -> str:
        """Format archetypes into descriptive section."""
        if not archetypes:
            return "The journey works with universal archetypal energies that appear uniquely for each traveler."

        descriptions = {
            'guide': "The **Guide** appears to show the way through unfamiliar territory.",
            'healer': "The **Healer** offers restoration and integration of wounded parts.",
            'warrior': "The **Warrior** provides strength and courage for the journey.",
            'wise_elder': "The **Wise Elder** shares accumulated wisdom from beyond time.",
            'divine_child': "The **Divine Child** reconnects you with innocence and wonder.",
            'shadow': "The **Shadow** reveals hidden aspects seeking integration.",
        }

        sections = []
        for archetype in archetypes[:4]:
            key = archetype.lower().replace(' ', '_')
            if key in descriptions:
                sections.append(descriptions[key])
            else:
                sections.append(f"The **{archetype}** brings unique gifts to your journey.")

        return '\n\n'.join(sections)

    def _determine_category(self, outcome: str, journey_family: str) -> str:
        """Determine blog category from session attributes."""
        category_map = {
            'healing': 'healing-journeys',
            'transformation': 'transformation',
            'empowerment': 'empowerment',
            'relaxation': 'relaxation-sleep',
            'spiritual_growth': 'spiritual-growth',
            'confidence': 'empowerment',
            'self_knowledge': 'self-discovery',
        }
        return category_map.get(outcome, 'dreamweaving')

    def _generate_tags(
        self,
        theme: str,
        outcome: str,
        archetypes: List[str],
        journey_family: str
    ) -> List[str]:
        """Generate relevant tags for the post."""
        tags = ['hypnosis', 'meditation', 'dreamweaving']

        if outcome:
            tags.append(outcome.replace('_', '-'))

        if theme:
            tags.append(theme.lower().replace(' ', '-'))

        if journey_family:
            tags.append(journey_family.replace('_', '-'))

        for archetype in archetypes[:2]:
            tags.append(archetype.lower().replace(' ', '-'))

        return list(set(tags))[:8]

    def _generate_meta_description(
        self,
        title: str,
        theme: str,
        outcome: str
    ) -> str:
        """Generate SEO meta description (155 chars max)."""
        outcome_text = outcome.replace('_', ' ') if outcome else 'transformation'
        theme_text = theme or 'inner growth'

        desc = f"Explore {theme_text} through guided hypnosis. This dreamweaving journey supports {outcome_text} and deep inner work."

        if len(desc) > 155:
            desc = desc[:152] + '...'

        return desc

    def save_post(self, post: BlogPost, filename: Optional[str] = None) -> Path:
        """Save blog post to file."""
        if filename is None:
            filename = f"{post.slug}.md"

        filepath = self.output_path / filename
        with open(filepath, 'w') as f:
            f.write(post.to_markdown())

        return filepath

    def generate_batch(
        self,
        session_names: List[str],
        blog_type: str = 'experience'
    ) -> List[BlogPost]:
        """Generate blog posts for multiple sessions."""
        posts = []
        for session_name in session_names:
            post = self.generate_from_session(session_name, blog_type)
            if post:
                posts.append(post)
        return posts


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate blog posts from sessions')
    parser.add_argument('session', help='Session name')
    parser.add_argument('--type', default='experience',
                       choices=['experience', 'deep_dive', 'benefits', 'technique'],
                       help='Type of blog post')
    parser.add_argument('--save', action='store_true', help='Save to file')

    args = parser.parse_args()

    writer = AutoBlogWriter()
    post = writer.generate_from_session(args.session, args.type)

    if post:
        if args.save:
            path = writer.save_post(post)
            print(f"Saved to: {path}")
        else:
            print(post.to_markdown())
    else:
        print(f"Session not found: {args.session}")
