#!/usr/bin/env python3
"""
Topic Enhancer for Dreamweaving Sessions

Rewrites generic, misspelled, or low-quality topic titles into SEO-friendly,
descriptive titles suitable for YouTube and web publishing.

Usage:
    from scripts.automation.topic_enhancer import enhance_topic, TopicEnhancement

    result = enhance_topic("Japanase")
    if result.was_enhanced:
        print(f"Original: {result.original}")
        print(f"Enhanced: {result.enhanced_title}")
        print(f"SEO Title: {result.seo_title}")
"""

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional, List

logger = logging.getLogger(__name__)

# Try to import Anthropic client
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


@dataclass
class TopicEnhancement:
    """Result of topic enhancement."""
    original: str
    enhanced_title: str  # Clean, descriptive session title
    seo_title: str  # YouTube-optimized title with keywords
    was_enhanced: bool
    reason: str
    suggested_tags: List[str] = field(default_factory=list)
    theme_category: Optional[str] = None  # healing, transformation, relaxation, etc.


# Generic/problematic patterns that need enhancement
NEEDS_ENHANCEMENT_PATTERNS = [
    # Too short or single word
    (r'^[A-Za-z]{1,12}$', "Single word topic - needs expansion"),
    # Misspellings of common words
    (r'japanase|japenese|japnese', "Misspelled 'Japanese'"),
    (r'mediteranean|mediteranian', "Misspelled 'Mediterranean'"),
    (r'buddist|budhist|budist', "Misspelled 'Buddhist'"),
    (r'christain|cristian', "Misspelled 'Christian'"),
    (r'hawaian|hawian', "Misspelled 'Hawaiian'"),
    (r'indiginous|indigenious', "Misspelled 'Indigenous'"),
    # Too generic
    (r'^(love|peace|calm|sleep|relax|heal|hope|faith|joy)$', "Single generic word"),
    (r'^(nature|forest|ocean|water|fire|earth|air)$', "Single element word"),
    # All caps or weird casing
    (r'^[A-Z\s]+$', "All caps - needs normalization"),
    # Just a nationality/culture without context
    (r'^(japanese|chinese|indian|celtic|norse|greek|egyptian|mayan|aztec)$',
     "Just a culture name - needs dreamweaving context"),
]


def needs_enhancement(topic: str) -> tuple[bool, str]:
    """
    Check if a topic needs enhancement.

    Returns:
        Tuple of (needs_enhancement, reason)
    """
    topic_lower = topic.lower().strip()

    # Check length
    if len(topic_lower) < 5:
        return True, "Topic too short"

    # Check word count
    words = topic_lower.split()
    if len(words) == 1:
        return True, "Single word topic"

    # Check for patterns
    for pattern, reason in NEEDS_ENHANCEMENT_PATTERNS:
        if re.search(pattern, topic_lower, re.IGNORECASE):
            return True, reason

    # Check if already has dreamweaving context
    dreamweaving_keywords = [
        'journey', 'meditation', 'hypnosis', 'dreamweaving', 'visualization',
        'healing', 'transformation', 'awakening', 'pathworking', 'guided',
        'trance', 'relaxation', 'sleep', 'inner', 'sacred'
    ]

    has_context = any(kw in topic_lower for kw in dreamweaving_keywords)
    if not has_context and len(words) <= 3:
        return True, "Missing dreamweaving context"

    return False, "Topic appears adequate"


def enhance_with_llm(topic: str) -> TopicEnhancement:
    """
    Use Claude to enhance a topic into an SEO-friendly title.
    """
    if not HAS_ANTHROPIC:
        logger.warning("Anthropic not available, returning basic enhancement")
        return _basic_enhancement(topic)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set, returning basic enhancement")
        return _basic_enhancement(topic)

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are a title optimizer for a hypnotic guided meditation/dreamweaving YouTube channel called "Sacred Digital Dreamweaver".

Given this raw topic: "{topic}"

Create an enhanced, SEO-friendly title that:
1. Fixes any spelling errors
2. Expands generic words into descriptive phrases
3. Adds dreamweaving/meditation context if missing
4. Is compelling and click-worthy for YouTube
5. Includes relevant keywords for search

Examples of good transformations:
- "Japanase" → "Japanese Zen Garden Meditation | Finding Inner Peace Through Ancient Wisdom"
- "Love" → "Unconditional Self-Love Meditation | Healing Your Heart and Embracing Worthiness"
- "Celtic" → "Celtic Sacred Grove Journey | Meeting Ancient Druids in the Mystical Forest"
- "Sleep" → "Deep Sleep Hypnosis | Drift Into Peaceful Slumber with Healing Frequencies"
- "Anxiety" → "Release Anxiety & Find Calm | Guided Meditation for Stress Relief"

Respond with EXACTLY this format (no other text):
ENHANCED_TITLE: [Clean descriptive title, 5-10 words]
SEO_TITLE: [YouTube-optimized title with | separator and keywords, 10-15 words max]
CATEGORY: [One of: healing, transformation, relaxation, sleep, spiritual, confidence, shadow_work, nature, cosmic, cultural]
TAGS: [comma-separated list of 5-7 relevant tags]
REASON: [Brief explanation of changes made]"""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text.strip()
        lines = text.split('\n')

        enhanced_title = topic  # fallback
        seo_title = topic
        category = None
        tags = []
        reason = "Enhanced by LLM"

        for line in lines:
            line = line.strip()
            if line.startswith("ENHANCED_TITLE:"):
                enhanced_title = line.replace("ENHANCED_TITLE:", "").strip()
            elif line.startswith("SEO_TITLE:"):
                seo_title = line.replace("SEO_TITLE:", "").strip()
            elif line.startswith("CATEGORY:"):
                category = line.replace("CATEGORY:", "").strip().lower()
            elif line.startswith("TAGS:"):
                tags_str = line.replace("TAGS:", "").strip()
                tags = [t.strip() for t in tags_str.split(',')]
            elif line.startswith("REASON:"):
                reason = line.replace("REASON:", "").strip()

        return TopicEnhancement(
            original=topic,
            enhanced_title=enhanced_title,
            seo_title=seo_title,
            was_enhanced=True,
            reason=reason,
            suggested_tags=tags,
            theme_category=category
        )

    except Exception as e:
        logger.error(f"LLM enhancement failed: {e}")
        return _basic_enhancement(topic)


def _basic_enhancement(topic: str) -> TopicEnhancement:
    """
    Basic enhancement without LLM - fixes obvious issues.
    """
    original = topic
    enhanced = topic.strip()

    # Fix common misspellings
    misspelling_fixes = {
        'japanase': 'Japanese',
        'japenese': 'Japanese',
        'japnese': 'Japanese',
        'mediteranean': 'Mediterranean',
        'mediteranian': 'Mediterranean',
        'buddist': 'Buddhist',
        'budhist': 'Buddhist',
        'christain': 'Christian',
        'cristian': 'Christian',
        'hawaian': 'Hawaiian',
        'hawian': 'Hawaiian',
        'indiginous': 'Indigenous',
        'indigenious': 'Indigenous',
    }

    for wrong, correct in misspelling_fixes.items():
        if wrong in enhanced.lower():
            enhanced = re.sub(wrong, correct, enhanced, flags=re.IGNORECASE)

    # Title case
    enhanced = enhanced.title()

    # Add generic context for single words
    words = enhanced.split()
    if len(words) == 1:
        word = words[0]
        # Map single words to expanded titles
        single_word_expansions = {
            'japanese': 'Japanese Zen Meditation Journey',
            'chinese': 'Chinese Taoist Meditation Journey',
            'celtic': 'Celtic Sacred Grove Journey',
            'norse': 'Norse Mythology Meditation Journey',
            'greek': 'Greek Temple Meditation Journey',
            'egyptian': 'Egyptian Temple Meditation Journey',
            'mayan': 'Mayan Sacred Calendar Journey',
            'love': 'Self-Love Healing Meditation',
            'peace': 'Finding Inner Peace Meditation',
            'calm': 'Deep Calm Relaxation Journey',
            'sleep': 'Deep Sleep Hypnosis Journey',
            'relax': 'Deep Relaxation Meditation',
            'heal': 'Healing Light Meditation',
            'hope': 'Rekindling Hope Meditation',
            'faith': 'Deepening Faith Journey',
            'joy': 'Cultivating Joy Meditation',
            'nature': 'Nature Healing Meditation',
            'forest': 'Enchanted Forest Journey',
            'ocean': 'Ocean Depths Meditation',
            'water': 'Healing Waters Meditation',
            'fire': 'Sacred Fire Transformation',
            'earth': 'Earth Grounding Meditation',
            'air': 'Breath of Life Meditation',
        }

        lower_word = word.lower()
        if lower_word in single_word_expansions:
            enhanced = single_word_expansions[lower_word]

    # Create SEO title
    seo_title = f"{enhanced} | Guided Meditation & Binaural Beats"

    was_enhanced = enhanced != original
    reason = "Basic enhancement applied" if was_enhanced else "No changes needed"

    return TopicEnhancement(
        original=original,
        enhanced_title=enhanced,
        seo_title=seo_title,
        was_enhanced=was_enhanced,
        reason=reason,
        suggested_tags=['meditation', 'guided meditation', 'binaural beats', 'relaxation'],
        theme_category='general'
    )


def enhance_topic(topic: str, use_llm: bool = True) -> TopicEnhancement:
    """
    Enhance a topic title to be more descriptive and SEO-friendly.

    Args:
        topic: The raw topic title
        use_llm: Whether to use LLM for enhancement (default True)

    Returns:
        TopicEnhancement with original and enhanced titles
    """
    if not topic or len(topic.strip()) < 2:
        return TopicEnhancement(
            original=topic or "",
            enhanced_title="Guided Meditation Journey",
            seo_title="Guided Meditation Journey | Binaural Beats & Relaxation",
            was_enhanced=True,
            reason="Empty topic - using default",
            theme_category='general'
        )

    topic = topic.strip()

    # Check if enhancement is needed
    needs_it, reason = needs_enhancement(topic)

    if not needs_it:
        # Topic is already good - just return it with SEO formatting
        seo_title = topic
        if '|' not in topic:
            seo_title = f"{topic} | Guided Meditation & Binaural Beats"

        return TopicEnhancement(
            original=topic,
            enhanced_title=topic,
            seo_title=seo_title,
            was_enhanced=False,
            reason="Topic already adequate",
            theme_category=_detect_category(topic)
        )

    logger.info(f"Topic '{topic}' needs enhancement: {reason}")

    # Enhance the topic
    if use_llm:
        return enhance_with_llm(topic)
    else:
        return _basic_enhancement(topic)


def _detect_category(topic: str) -> str:
    """Detect theme category from topic text."""
    topic_lower = topic.lower()

    category_keywords = {
        'healing': ['heal', 'repair', 'restore', 'recovery', 'wellness'],
        'transformation': ['transform', 'change', 'evolve', 'become', 'shift'],
        'relaxation': ['relax', 'calm', 'peace', 'serene', 'tranquil'],
        'sleep': ['sleep', 'slumber', 'rest', 'dream', 'night'],
        'spiritual': ['spirit', 'soul', 'divine', 'sacred', 'holy'],
        'confidence': ['confidence', 'courage', 'strength', 'power', 'worth'],
        'shadow_work': ['shadow', 'dark', 'fear', 'trauma', 'wound'],
        'nature': ['nature', 'forest', 'ocean', 'garden', 'mountain'],
        'cosmic': ['cosmic', 'star', 'universe', 'astral', 'celestial'],
        'cultural': ['japanese', 'celtic', 'norse', 'greek', 'egyptian', 'mayan'],
    }

    for category, keywords in category_keywords.items():
        if any(kw in topic_lower for kw in keywords):
            return category

    return 'general'


# CLI for testing
if __name__ == "__main__":
    import sys

    test_topics = [
        # Should be enhanced
        "Japanase",
        "Love",
        "Celtic",
        "Sleep",
        "peace",
        "HEALING",
        "forest",

        # Should NOT be enhanced (already good)
        "Japanese Zen Garden Meditation",
        "Finding Inner Peace Through Nature",
        "Deep Sleep Hypnosis for Restful Slumber",
        "Celtic Sacred Grove Journey",
    ]

    if len(sys.argv) > 1:
        # Enhance specific topic
        topic = " ".join(sys.argv[1:])
        result = enhance_topic(topic)
        print(f"\n{'='*60}")
        print(f"Original:     {result.original}")
        print(f"Enhanced:     {result.enhanced_title}")
        print(f"SEO Title:    {result.seo_title}")
        print(f"Was Enhanced: {result.was_enhanced}")
        print(f"Reason:       {result.reason}")
        print(f"Category:     {result.theme_category}")
        print(f"Tags:         {', '.join(result.suggested_tags)}")
        print(f"{'='*60}")
    else:
        # Run test suite
        print("=" * 70)
        print("TOPIC ENHANCER TEST SUITE")
        print("=" * 70)

        for topic in test_topics:
            result = enhance_topic(topic, use_llm=True)
            status = "+" if result.was_enhanced else "="
            print(f"{status} '{topic}' → '{result.enhanced_title}'")
            if result.was_enhanced:
                print(f"  SEO: {result.seo_title}")
                print(f"  Reason: {result.reason}")
            print()
