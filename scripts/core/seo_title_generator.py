"""
SEO Title Generator for Dreamweaving Sessions

Generates optimized page titles following these principles:
1. Length: 50-60 characters (max 70 with suffix)
2. Primary keyword at start
3. Emotionally engaging
4. Distinct from full video title
5. Naturally readable

Input sources:
- Full video title
- Session topic/theme
- Category
- Archetypes
"""

import re
import hashlib
from typing import Optional, List, Dict


# Maximum lengths
MAX_SEO_TITLE = 60  # Before suffix
TARGET_SEO_TITLE = 50  # Optimal
SUFFIX = " | Salars Dreamweaver"  # Added by frontend (22 chars)

# Redundant phrases to strip (order matters - longer first)
REDUNDANT_PHRASES = [
    "Guided Meditation to ",
    "Guided Meditation for ",
    "Guided Meditation ",
    "Guided Hypnosis to ",
    "Guided Hypnosis for ",
    "Guided Hypnosis ",
    "Guided Visualization to ",
    "Guided Visualization for ",
    "Guided Visualization ",
    "Deep Meditation ",
    "Celtic Guided Meditation",
    "Native American Guided Meditation",
    "Binaural Beats",
    "Theta Binaural",
    "Delta Binaural",
    "Alpha Binaural",
    "Theta Waves",
    "Delta Waves",
    "Alpha Waves",
    "432Hz",
    "528Hz",
    "Deep Trance",
    "Deep Relaxation",
    "Hypnotic Journey",
    "Dreamweaver Journey",
    "Dreamweaving",
]

# Category-specific title templates (fallback when title is too long)
CATEGORY_TEMPLATES = {
    "healing-journeys": "{core} Healing Journey",
    "shadow-depths": "{core} Shadow Work",
    "cosmic-space": "Cosmic {core}",
    "nature-elements": "{core} Nature Meditation",
    "archetypal-encounters": "{core} Archetypal Journey",
    "spiritual-religious": "Sacred {core} Journey",
    "personal-development": "{core} Empowerment",
    "sensory-body": "{core} Embodiment",
}

# Category codes for SKU generation
CATEGORY_CODES = {
    "healing-journeys": "HEL",
    "shadow-depths": "SHD",
    "cosmic-space": "COS",
    "nature-elements": "NAT",
    "archetypal-encounters": "ARC",
    "spiritual-religious": "SPI",
    "personal-development": "DEV",
    "sensory-body": "SEN",
}


def generate_seo_title(
    full_title: str,
    topic: str = "",
    category: str = "",
    archetypes: Optional[List[str]] = None,
) -> str:
    """
    Generate an SEO-optimized page title.

    Algorithm:
    1. Extract core concept from title (before first pipe/dash)
    2. Strip redundant phrases
    3. If still too long, use category template with core noun
    4. Ensure keyword-rich and emotionally engaging
    5. Cap at 50-60 characters

    Args:
        full_title: The complete video/session title
        topic: Optional topic description
        category: Optional category slug
        archetypes: Optional list of archetype names

    Returns:
        Optimized title string (without site suffix)
    """
    if not full_title:
        return "Dreamweaver Journey"

    # Step 1: Extract core concept
    core = _extract_core_concept(full_title, topic)

    # Step 2: Strip redundant phrases
    clean = _strip_redundant_phrases(core)

    # Step 3: Check length and apply templates if needed
    if len(clean) <= TARGET_SEO_TITLE:
        return clean

    # Try category-based template
    if category and category in CATEGORY_TEMPLATES:
        core_noun = _extract_core_noun(clean)
        if core_noun:
            templated = CATEGORY_TEMPLATES[category].format(core=core_noun)
            if len(templated) <= MAX_SEO_TITLE:
                return templated

    # Step 4: Smart truncation
    truncated = _smart_truncate(clean, TARGET_SEO_TITLE)

    return truncated


def _extract_core_concept(title: str, topic: str) -> str:
    """Extract the core concept from a full title."""
    # Try title first - split on common delimiters
    if " | " in title:
        core = title.split(" | ")[0].strip()
    elif " - " in title:
        # Be careful with em-dashes vs hyphens in words
        parts = title.split(" - ")
        core = parts[0].strip()
        # If first part is very short, include second part
        if len(core) < 15 and len(parts) > 1:
            core = f"{parts[0].strip()}: {parts[1].strip()}"
    elif " — " in title:  # Em-dash
        core = title.split(" — ")[0].strip()
    elif " – " in title:  # En-dash
        core = title.split(" – ")[0].strip()
    else:
        core = title.strip()

    # Handle colon-separated titles (like "Title: Long Description")
    # Only split if description is very long
    if ": " in core and len(core) > 50:
        parts = core.split(": ", 1)
        # Keep just the main title if the rest is a long description
        if len(parts[1]) > 30:
            core = parts[0].strip()

    # If core is too generic or short, try topic
    if len(core) < 10 and topic:
        topic_core = topic.split(" | ")[0].strip() if " | " in topic else topic.strip()
        if " - " in topic_core:
            topic_core = topic_core.split(" - ")[0].strip()
        if len(topic_core) > len(core) and len(topic_core) <= MAX_SEO_TITLE:
            core = topic_core

    # Clean up any trailing colons or dashes
    core = core.rstrip(" :-–—|")

    return core


def _strip_redundant_phrases(text: str) -> str:
    """Remove SEO-redundant phrases from title."""
    result = text

    for phrase in REDUNDANT_PHRASES:
        # Case-insensitive replacement
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        result = pattern.sub("", result).strip()

    # Clean up double spaces and trailing punctuation
    result = re.sub(r'\s+', ' ', result).strip()
    result = result.rstrip(" |-:,–—")

    # Remove any leftover empty parentheses or brackets
    result = re.sub(r'\(\s*\)', '', result)
    result = re.sub(r'\[\s*\]', '', result)

    # Remove trailing 's' from stripped phrases (e.g., "Dreamweavings" -> "s")
    result = re.sub(r'\s+s$', '', result, flags=re.IGNORECASE)
    result = result.strip()

    return result


def _extract_core_noun(text: str) -> str:
    """Extract the primary noun phrase from text."""
    # Common patterns: "The X of Y", "X Journey", "X Meditation"
    patterns = [
        r'^The\s+(.+?)\s+(?:of|in|to|for)\s+(.+?)$',  # "The Forest of Lost Instincts"
        r'^(.+?)\s+(?:Journey|Meditation|Experience|Gateway|Path)$',
        r'^(.+?):\s+(.+?)$',  # "Title: Subtitle"
        r'^(.+?)\s*$',  # Fallback: entire text
    ]

    for pattern in patterns:
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            # For "The X of Y" pattern, return just the subject
            if pattern.startswith(r'^The'):
                noun = match.group(1).strip()
            elif match.lastindex and match.lastindex >= 2:
                # For patterns with two groups, combine them smartly
                noun = f"{match.group(1).strip()}: {match.group(2).strip()}"
            else:
                noun = match.group(1).strip()

            # Ensure it's not too long and not too short
            if 3 < len(noun) < 35:
                return noun.strip()

    # Fallback: first 30 chars at word boundary
    if len(text) > 30:
        truncated = text[:30]
        last_space = truncated.rfind(' ')
        if last_space > 15:
            return truncated[:last_space].strip()
        return truncated.strip()

    return text.strip()


def _smart_truncate(text: str, max_length: int) -> str:
    """Truncate at word boundary, preserving meaning."""
    if len(text) <= max_length:
        return text

    # Find last space before limit
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')

    if last_space > max_length // 2:
        truncated = truncated[:last_space].rstrip(" |-:,–—")
    else:
        # No good break point, just truncate
        truncated = truncated.rstrip(" |-:,–—")

    return truncated


def generate_sku(category: str, slug: str) -> str:
    """
    Generate a unique product SKU.

    Format: DW-{CAT}-{THEME}-{NUM}
    Example: DW-HEL-FOREST-42
    """
    cat_code = CATEGORY_CODES.get(category, "GEN")

    # Extract theme from slug (first 2-3 meaningful words)
    words = slug.replace("-", " ").split()
    # Filter out common words
    stop_words = {"the", "a", "an", "of", "in", "to", "for", "and", "or", "journey", "meditation"}
    meaningful = [w for w in words if w.lower() not in stop_words and len(w) >= 3]

    # Take first 2 meaningful words
    theme_parts = meaningful[:2] if meaningful else words[:2]
    theme = "".join(p[:3].upper() for p in theme_parts)[:6]

    if not theme:
        theme = "GEN"

    # Hash for uniqueness
    hash_num = int(hashlib.md5(slug.encode()).hexdigest()[:4], 16) % 100

    return f"DW-{cat_code}-{theme}-{hash_num:02d}"


def generate_seo_metadata(
    full_title: str,
    topic: str = "",
    category: str = "",
    slug: str = "",
    archetypes: Optional[List[str]] = None,
    description: str = "",
) -> Dict[str, str]:
    """
    Generate complete SEO metadata package.

    Returns dict with:
    - meta_title: Optimized page title (50-60 chars)
    - meta_description: 155-char description
    - h1_title: Display heading (can be longer)
    - primary_keyword: Zero-competition keyword
    - sku: Product SKU
    - image_alt_text: Alt text for images
    """
    # Generate optimized title
    meta_title = generate_seo_title(full_title, topic, category, archetypes)

    # H1 is the display title (can be the full core concept)
    h1_title = _extract_core_concept(full_title, topic)

    # Meta description (155 chars max)
    if description:
        # Truncate at word boundary
        if len(description) > 155:
            meta_description = description[:155].rsplit(' ', 1)[0]
            if not meta_description.endswith('.'):
                meta_description = meta_description.rstrip('.,;:') + '...'
        else:
            meta_description = description
    else:
        meta_description = f"Experience {meta_title} - a transformative Dreamweaver guided meditation journey with binaural beats and hypnotic language patterns."
        if len(meta_description) > 155:
            meta_description = meta_description[:155].rsplit(' ', 1)[0] + '...'

    # Zero-competition keyword (brand + generic term)
    primary_keyword = f"{h1_title} - Dreamweaver Guided Meditation"

    # SKU generation
    sku = generate_sku(category or "archetypal", slug or "unknown")

    # Image alt text
    image_alt_text = f"{meta_title} - Dreamweaver meditation journey artwork"

    return {
        "meta_title": meta_title,
        "meta_description": meta_description,
        "h1_title": h1_title,
        "primary_keyword": primary_keyword,
        "sku": sku,
        "image_alt_text": image_alt_text,
    }


# For testing/debugging
if __name__ == "__main__":
    test_titles = [
        "The Forest of Lost Instincts | Guided Meditation to Reclaim Your Primal Wisdom | Theta Binaural Beats",
        "Journey to Tir na nOg - The Land of Eternal Youth | Celtic Guided Meditation",
        "The Iron Soul Forge | Guided Hypnosis for Unbreakable Courage",
        "Ascent to Olympus: The Throne of Zeus | Explore Zeus' Divine Power",
        "Shadow Healing Journey - Integrating Your Dark Side",
        "The Garden of Eden Pathworking | Experience Paradise | 432Hz Binaural Beats",
        "Carnegie's Steel Empire Dreamweaving: Step into the shoes of Andrew Carnegie, a Scottish immigrant",
        "Spirit Animal Journey: Native American beliefs often incorporate Spirit or Totem Animals",
        "The Crystal Cavern of Cellular Memory-Journey: Explore a cavern where crystals resonate",
        "Celestial Voyage Through the Cosmos | Deep Space Meditation | Delta Waves",
    ]

    print("=" * 70)
    print("SEO Title Generator Test")
    print("=" * 70)

    for title in test_titles:
        seo_title = generate_seo_title(title)
        print(f"\nOriginal ({len(title)} chars):")
        print(f"  {title[:70]}{'...' if len(title) > 70 else ''}")
        print(f"SEO Title ({len(seo_title)} chars):")
        print(f"  {seo_title}")

        # Also test full metadata
        meta = generate_seo_metadata(title, category="healing-journeys", slug="test-session")
        print(f"SKU: {meta['sku']}")
