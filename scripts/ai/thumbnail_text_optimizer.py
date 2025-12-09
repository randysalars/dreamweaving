#!/usr/bin/env python3
"""
Thumbnail Text Optimizer for Sacred Digital Dreamweaver

LLM-powered optimization of thumbnail text for maximum CTR.
Transforms long manifest titles into punchy 2-5 word headlines.

Based on the Viral Thumbnail System principles:
- 2-5 punchy words maximum
- Power verbs: Forge, Enter, Unlock, Awaken, Discover, Transform
- Curiosity gap - raise question but don't answer
- Emotional trigger words

Usage:
    from scripts.ai.thumbnail_text_optimizer import optimize_thumbnail_text

    spec = optimize_thumbnail_text(
        manifest_title="The Iron Soul Forge - Ancient Alchemy for Inner Strength",
        outcome="empowerment",
        archetypes=["Forge-Father", "Alchemist"],
        theme="mythic transformation"
    )

    print(spec.title)      # "FORGE YOUR SOUL"
    print(spec.subtitle)   # "Into Iron"
    print(spec.power_words)  # ["forge", "soul", "iron"]
"""

import os
import sys
import json
import random
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

import yaml

# Try to import Anthropic client
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


PROJECT_ROOT = Path(__file__).parent.parent.parent


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ThumbnailTextSpec:
    """Optimized text specification for a thumbnail."""
    title: str                          # 2-5 word UPPERCASE title
    subtitle: Optional[str] = None      # Optional short tagline
    power_words: List[str] = field(default_factory=list)
    curiosity_hook: Optional[str] = None  # The "impossible moment" concept
    variants: List[str] = field(default_factory=list)  # Alternative title options


# =============================================================================
# POWER WORDS BY OUTCOME (from copywriting_templates.yaml and viral system)
# =============================================================================

POWER_VERBS = [
    "FORGE", "ENTER", "UNLOCK", "AWAKEN", "DISCOVER", "TRANSFORM",
    "IGNITE", "UNLEASH", "EMBRACE", "RECLAIM", "REVEAL", "ACTIVATE",
    "JOURNEY", "ASCEND", "DESCEND", "CROSS", "OPEN", "RELEASE"
]

POWER_NOUNS = [
    "SOUL", "POWER", "TRUTH", "LIGHT", "SHADOW", "FIRE", "IRON",
    "GOLD", "SPIRIT", "HEART", "GATE", "PORTAL", "TEMPLE", "THRONE",
    "CROWN", "FLAME", "STAR", "DREAM", "EDEN", "COSMOS"
]

OUTCOME_POWER_WORDS = {
    "healing": ["HEAL", "RESTORE", "RELEASE", "MEND", "RENEW", "EMBRACE"],
    "transformation": ["TRANSFORM", "BECOME", "EMERGE", "EVOLVE", "TRANSCEND", "SHIFT"],
    "empowerment": ["FORGE", "IGNITE", "RECLAIM", "UNLEASH", "AWAKEN", "RISE"],
    "confidence": ["STAND", "OWN", "CLAIM", "EMBODY", "RADIATE", "COMMAND"],
    "relaxation": ["RELEASE", "SURRENDER", "MELT", "FLOAT", "DRIFT", "REST"],
    "spiritual_growth": ["ASCEND", "EXPAND", "ILLUMINATE", "CONNECT", "ALIGN", "OPEN"],
    "abundance": ["RECEIVE", "OVERFLOW", "ATTRACT", "ALLOW", "MAGNETIZE", "WELCOME"],
    "clarity": ["SEE", "KNOW", "REVEAL", "ILLUMINATE", "CLEAR", "UNDERSTAND"],
    "sleep": ["DRIFT", "DESCEND", "SURRENDER", "RELEASE", "FLOAT", "REST"],
    "shadow_work": ["FACE", "EMBRACE", "INTEGRATE", "TRANSFORM", "RECLAIM", "CONFRONT"],
    "default": ["JOURNEY", "DISCOVER", "EXPLORE", "EXPERIENCE", "ENTER", "BEGIN"]
}

# Outcome-to-visual-theme emotional keywords
OUTCOME_EMOTIONAL_KEYWORDS = {
    "healing": ["golden", "light", "embrace", "sanctuary", "restoration"],
    "transformation": ["phoenix", "emergence", "threshold", "metamorphosis", "becoming"],
    "empowerment": ["forge", "iron", "fire", "power", "strength", "sovereignty"],
    "confidence": ["crown", "throne", "radiance", "certainty", "presence"],
    "relaxation": ["peace", "stillness", "float", "calm", "serene", "gentle"],
    "spiritual_growth": ["cosmic", "star", "infinite", "sacred", "divine", "mystic"],
    "abundance": ["gold", "overflow", "river", "blessing", "treasure", "prosperity"],
    "clarity": ["crystal", "clear", "vision", "truth", "knowing", "insight"],
    "sleep": ["dream", "night", "moon", "drift", "cloud", "gentle"],
    "shadow_work": ["mirror", "shadow", "depths", "integration", "wholeness", "reclamation"],
    "default": ["journey", "path", "discovery", "inner", "sacred", "transformative"]
}


# =============================================================================
# TEMPLATE PATTERNS FOR TITLE GENERATION
# =============================================================================

TITLE_PATTERNS = [
    "{VERB} YOUR {NOUN}",       # "FORGE YOUR SOUL"
    "{VERB} THE {NOUN}",        # "ENTER THE GATE"
    "THE {ADJECTIVE} {NOUN}",   # "THE IRON FORGE"
    "{NOUN} {VERB}",            # "SOUL AWAKENS"
    "{VERB} INTO {NOUN}",       # "DESCEND INTO SHADOW"
    "BEYOND THE {NOUN}",        # "BEYOND THE VEIL"
    "THE {NOUN} WITHIN",        # "THE POWER WITHIN"
    "{NOUN} OF {NOUN}",         # "FORGE OF SOULS"
]

ADJECTIVES = [
    "SACRED", "ANCIENT", "COSMIC", "ETERNAL", "DIVINE", "INNER",
    "IRON", "GOLDEN", "CRYSTAL", "HIDDEN", "AWAKENED", "MYSTIC"
]


# =============================================================================
# LLM-BASED OPTIMIZATION
# =============================================================================

def _get_llm_client():
    """Get Anthropic client if available."""
    if not HAS_ANTHROPIC:
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    return anthropic.Anthropic(api_key=api_key)


def _build_optimization_prompt(
    manifest_title: str,
    outcome: str,
    archetypes: List[str],
    theme: str,
    power_words: List[str]
) -> str:
    """Build the LLM prompt for title optimization."""

    return f"""You are a YouTube thumbnail text optimizer specializing in spiritual/meditation content.

Your task: Transform this session title into a PUNCHY 2-5 word thumbnail headline.

RULES FROM THE VIRAL THUMBNAIL SYSTEM:
1. Use 2-5 words MAXIMUM (shorter is better)
2. Use POWER VERBS: {', '.join(POWER_VERBS[:10])}
3. Create CURIOSITY GAP - raise a question but don't answer it
4. Use UPPERCASE for the title
5. Emotional trigger words work: {', '.join(power_words[:6])}

SESSION CONTEXT:
- Original Title: {manifest_title}
- Outcome: {outcome}
- Archetypes: {', '.join(archetypes) if archetypes else 'None specified'}
- Theme: {theme}

EXAMPLES OF GOOD THUMBNAIL TITLES:
- "FORGE YOUR SOUL" (3 words, power verb + emotional noun)
- "ENTER THE GATE" (3 words, action + mystery)
- "AWAKEN POWER" (2 words, verb + noun)
- "THE IRON PATH" (3 words, evocative adjective + noun)
- "TRANSFORM WITHIN" (2 words, verb + direction)

Generate exactly 3 title options, ranked by CTR potential.

Return ONLY a JSON object with this structure:
{{
    "primary_title": "YOUR BEST 2-5 WORD TITLE",
    "subtitle": "Optional 2-3 word tagline or null",
    "variants": ["SECOND OPTION", "THIRD OPTION"],
    "power_words_used": ["word1", "word2"],
    "curiosity_hook": "The intriguing concept this title creates"
}}"""


def optimize_thumbnail_text_llm(
    manifest_title: str,
    outcome: str = "default",
    archetypes: Optional[List[str]] = None,
    theme: str = ""
) -> Optional[ThumbnailTextSpec]:
    """
    Use LLM to optimize thumbnail text.

    Returns None if LLM is not available.
    """
    client = _get_llm_client()
    if not client:
        return None

    archetypes = archetypes or []
    power_words = OUTCOME_POWER_WORDS.get(outcome, OUTCOME_POWER_WORDS["default"])

    prompt = _build_optimization_prompt(
        manifest_title=manifest_title,
        outcome=outcome,
        archetypes=archetypes,
        theme=theme,
        power_words=power_words
    )

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Cost-efficient for simple tasks
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse response
        response_text = response.content[0].text.strip()

        # Extract JSON from response
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]

        data = json.loads(response_text)

        return ThumbnailTextSpec(
            title=data.get("primary_title", manifest_title.upper()[:30]),
            subtitle=data.get("subtitle"),
            power_words=data.get("power_words_used", []),
            curiosity_hook=data.get("curiosity_hook"),
            variants=data.get("variants", [])
        )

    except Exception as e:
        print(f"LLM optimization failed: {e}")
        return None


# =============================================================================
# RULE-BASED FALLBACK OPTIMIZATION
# =============================================================================

def _extract_key_words(title: str) -> List[str]:
    """Extract important words from a title."""
    # Remove common filler words
    filler_words = {
        "the", "a", "an", "of", "for", "to", "in", "on", "with", "and",
        "your", "my", "our", "into", "from", "-", "–", "|", ":"
    }

    words = title.lower().replace("-", " ").replace("–", " ").split()
    return [w for w in words if w not in filler_words and len(w) > 2]


def _generate_pattern_title(key_words: List[str], outcome: str) -> str:
    """Generate a title using pattern matching."""
    power_verbs = OUTCOME_POWER_WORDS.get(outcome, OUTCOME_POWER_WORDS["default"])

    # Try to find a noun from the title
    noun = None
    for word in key_words:
        if word.upper() in POWER_NOUNS:
            noun = word.upper()
            break

    if not noun and key_words:
        # Use the most distinctive word as noun
        noun = max(key_words, key=len).upper()

    if not noun:
        noun = random.choice(POWER_NOUNS)

    verb = random.choice(power_verbs)

    # Choose a pattern
    patterns = [
        f"{verb} YOUR {noun}",
        f"{verb} THE {noun}",
        f"THE {random.choice(ADJECTIVES)} {noun}",
        f"{verb} {noun}",
    ]

    return random.choice(patterns)


def optimize_thumbnail_text_rules(
    manifest_title: str,
    outcome: str = "default",
    archetypes: Optional[List[str]] = None,
    theme: str = ""
) -> ThumbnailTextSpec:
    """
    Rule-based fallback for thumbnail text optimization.

    Used when LLM is not available.
    """
    archetypes = archetypes or []

    # Extract key words from original title
    key_words = _extract_key_words(manifest_title)

    # Check if any archetype name is a good hook
    archetype_words = []
    for arch in archetypes:
        archetype_words.extend(_extract_key_words(arch))

    # Combine with theme keywords
    theme_words = _extract_key_words(theme)
    all_words = key_words + archetype_words + theme_words

    # Generate title using patterns
    title = _generate_pattern_title(all_words, outcome)

    # Ensure title is not too long (max 5 words)
    words = title.split()
    if len(words) > 5:
        title = " ".join(words[:5])

    # Generate variants
    variants = []
    for _ in range(2):
        variant = _generate_pattern_title(all_words, outcome)
        if variant != title:
            variants.append(variant)

    # Get power words used
    power_words = [w for w in OUTCOME_POWER_WORDS.get(outcome, []) if w in title]

    return ThumbnailTextSpec(
        title=title,
        subtitle=None,
        power_words=power_words,
        curiosity_hook=f"What lies within the {all_words[0] if all_words else 'journey'}?",
        variants=variants[:2]
    )


# =============================================================================
# MAIN OPTIMIZATION FUNCTION
# =============================================================================

def optimize_thumbnail_text(
    manifest_title: str,
    outcome: str = "default",
    archetypes: Optional[List[str]] = None,
    theme: str = "",
    prefer_llm: bool = True
) -> ThumbnailTextSpec:
    """
    Optimize thumbnail text for maximum CTR.

    Args:
        manifest_title: Original session title from manifest
        outcome: Session outcome (healing, transformation, etc.)
        archetypes: List of archetype names used in session
        theme: Session theme or description
        prefer_llm: If True, try LLM first then fall back to rules

    Returns:
        ThumbnailTextSpec with optimized title and variants

    Example:
        >>> spec = optimize_thumbnail_text(
        ...     manifest_title="The Iron Soul Forge - Ancient Alchemy",
        ...     outcome="empowerment",
        ...     archetypes=["Forge-Father"]
        ... )
        >>> print(spec.title)
        "FORGE YOUR SOUL"
    """
    # Normalize outcome
    outcome = outcome.lower().replace(" ", "_").replace("-", "_")
    if outcome not in OUTCOME_POWER_WORDS:
        outcome = "default"

    # Try LLM first if preferred
    if prefer_llm:
        spec = optimize_thumbnail_text_llm(
            manifest_title=manifest_title,
            outcome=outcome,
            archetypes=archetypes,
            theme=theme
        )
        if spec:
            return spec

    # Fall back to rule-based optimization
    return optimize_thumbnail_text_rules(
        manifest_title=manifest_title,
        outcome=outcome,
        archetypes=archetypes,
        theme=theme
    )


def get_outcome_power_words(outcome: str) -> List[str]:
    """Get power words for a specific outcome."""
    outcome = outcome.lower().replace(" ", "_").replace("-", "_")
    return OUTCOME_POWER_WORDS.get(outcome, OUTCOME_POWER_WORDS["default"])


def get_outcome_emotional_keywords(outcome: str) -> List[str]:
    """Get emotional keywords for a specific outcome."""
    outcome = outcome.lower().replace(" ", "_").replace("-", "_")
    return OUTCOME_EMOTIONAL_KEYWORDS.get(outcome, OUTCOME_EMOTIONAL_KEYWORDS["default"])


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI for testing thumbnail text optimization."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Optimize thumbnail text for YouTube CTR"
    )
    parser.add_argument("title", help="Original manifest title")
    parser.add_argument("--outcome", "-o", default="default", help="Session outcome")
    parser.add_argument("--archetypes", "-a", nargs="+", help="Archetype names")
    parser.add_argument("--theme", "-t", default="", help="Session theme")
    parser.add_argument("--no-llm", action="store_true", help="Use rules only, no LLM")

    args = parser.parse_args()

    spec = optimize_thumbnail_text(
        manifest_title=args.title,
        outcome=args.outcome,
        archetypes=args.archetypes,
        theme=args.theme,
        prefer_llm=not args.no_llm
    )

    print("\n" + "=" * 60)
    print("THUMBNAIL TEXT OPTIMIZATION RESULTS")
    print("=" * 60)
    print(f"\nOriginal: {args.title}")
    print(f"Outcome:  {args.outcome}")
    print()
    print(f"PRIMARY TITLE: {spec.title}")
    if spec.subtitle:
        print(f"Subtitle:      {spec.subtitle}")
    print()
    if spec.variants:
        print("VARIANTS:")
        for i, v in enumerate(spec.variants, 1):
            print(f"  {i}. {v}")
    print()
    if spec.power_words:
        print(f"Power Words: {', '.join(spec.power_words)}")
    if spec.curiosity_hook:
        print(f"Curiosity Hook: {spec.curiosity_hook}")
    print("=" * 60)


if __name__ == "__main__":
    main()
