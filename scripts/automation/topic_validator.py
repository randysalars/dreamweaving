#!/usr/bin/env python3
"""
Topic Validator for Dreamweaving Sessions

Validates whether a topic from Notion RAG is suitable for creating
a hypnotic dreamweaving journey. Uses Claude Haiku for fast, cheap validation.

Usage:
    from scripts.automation.topic_validator import validate_topic, TopicValidation

    result = validate_topic("Finding Inner Peace Through Nature")
    if result.is_valid:
        # proceed with generation
    else:
        print(f"Skipped: {result.reason}")
"""

import logging
import os
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import Anthropic client
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


@dataclass
class TopicValidation:
    """Result of topic validation."""
    is_valid: bool
    reason: str
    suggested_topic: Optional[str] = None  # If invalid, might suggest a related valid topic
    confidence: float = 1.0


# Keywords that indicate NON-dreamweaving content
# Note: Use specific phrases to avoid false positives (e.g., "meeting notes" not "meeting")
INVALID_KEYWORDS = [
    # Business/marketing content
    "marketing plan", "sales funnel", "revenue", "business plan", "roi",
    "conversion rate", "landing page", "email campaign", "seo ", " seo",
    "analytics data", "traffic source", "paypal button", "pricing tier",
    "subscription model", "checkout flow", "payment gateway", " aeo",

    # Technical/coding content
    "source code", "coding for", "api endpoint", "database schema",
    "deploy to", "server config", "github repo", "python script",
    "javascript code", "debug the", "bug fix", "implementation plan",
    "recursive agent", "mcp server", "claude code",

    # Administrative/meta content
    "meeting notes", "todo list", "planning session", "project notes",
    "readme file", "documentation for", "instructions for", "how to guide",
    "tutorial on", "schedule for",

    # Non-journey specific
    "copywriting template", "headline formula", "thumbnail design",
    "youtube upload", "batch process", "automation script", "cron job",
    "script library", "legal requirements", "order delivery",
]

# Keywords that indicate VALID dreamweaving content
VALID_KEYWORDS = [
    # Journey types
    "journey", "meditation", "hypnosis", "trance", "visualization",
    "pathworking", "guided", "dreamweaving", "inner", "sacred",

    # Themes
    "healing", "transformation", "awakening", "spiritual", "soul",
    "consciousness", "peace", "calm", "relaxation", "sleep",
    "confidence", "empowerment", "shadow work", "integration",

    # Archetypal/mystical
    "archetype", "eden", "garden", "temple", "cosmic", "celestial",
    "ancient", "divine", "light", "energy", "chakra", "kundalini",
    "spirit", "guide", "angel", "wisdom", "higher self", "subconscious",

    # Emotional states
    "anxiety", "stress", "fear", "grief", "trauma", "pain",
    "love", "joy", "gratitude", "forgiveness", "acceptance",

    # Outcomes
    "overcome", "release", "let go", "embrace", "discover",
    "unlock", "awaken", "transform", "heal", "restore",
]


def quick_keyword_check(topic: str) -> Optional[TopicValidation]:
    """
    Fast keyword-based pre-filter before LLM validation.
    Returns validation result if confident, None if LLM check needed.
    """
    topic_lower = topic.lower()

    # Check for strong invalid indicators
    for keyword in INVALID_KEYWORDS:
        if keyword in topic_lower:
            return TopicValidation(
                is_valid=False,
                reason=f"Contains non-dreamweaving keyword: '{keyword}'",
                confidence=0.9
            )

    # Check for strong valid indicators
    valid_count = sum(1 for kw in VALID_KEYWORDS if kw in topic_lower)
    if valid_count >= 2:
        return TopicValidation(
            is_valid=True,
            reason=f"Contains {valid_count} dreamweaving keywords",
            confidence=0.85
        )

    # Uncertain - need LLM check
    return None


def validate_with_llm(topic: str) -> TopicValidation:
    """
    Use Claude Haiku to validate if topic is suitable for dreamweaving.
    """
    if not HAS_ANTHROPIC:
        logger.warning("Anthropic not available, defaulting to valid")
        return TopicValidation(is_valid=True, reason="LLM validation unavailable", confidence=0.5)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set, defaulting to valid")
        return TopicValidation(is_valid=True, reason="API key not configured", confidence=0.5)

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are a content validator for a hypnotic audio journey production system called "Dreamweaving".

A valid dreamweaving topic should be suitable for creating a 20-30 minute guided hypnotic meditation/visualization journey. Valid topics include:
- Personal transformation themes (healing, confidence, overcoming fears)
- Spiritual/mystical journeys (garden of eden, temple visits, cosmic travel)
- Emotional processing (grief, anxiety, stress relief, self-love)
- Archetypal encounters (meeting inner guides, shadow work)
- Relaxation and sleep journeys
- Creative visualization experiences

INVALID topics include:
- Business/marketing content
- Technical/coding instructions
- Administrative notes or plans
- Meta-content about the dreamweaving system itself
- Lists, schedules, or todo items
- Product descriptions or sales copy

Evaluate this topic: "{topic}"

Respond with EXACTLY this format (no other text):
VALID: yes/no
REASON: [brief explanation]
SUGGESTED: [if invalid, suggest a related valid dreamweaving topic, or "none"]"""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text.strip()
        lines = text.split('\n')

        is_valid = False
        reason = "Could not parse response"
        suggested = None

        for line in lines:
            line = line.strip()
            if line.startswith("VALID:"):
                is_valid = "yes" in line.lower()
            elif line.startswith("REASON:"):
                reason = line.replace("REASON:", "").strip()
            elif line.startswith("SUGGESTED:"):
                suggested_text = line.replace("SUGGESTED:", "").strip()
                if suggested_text.lower() != "none":
                    suggested = suggested_text

        return TopicValidation(
            is_valid=is_valid,
            reason=reason,
            suggested_topic=suggested,
            confidence=0.95
        )

    except Exception as e:
        logger.error(f"LLM validation failed: {e}")
        # Default to valid on error to avoid blocking the pipeline
        return TopicValidation(
            is_valid=True,
            reason=f"LLM validation error: {str(e)[:50]}",
            confidence=0.3
        )


def validate_topic(topic: str, use_llm: bool = True) -> TopicValidation:
    """
    Validate whether a topic is suitable for dreamweaving.

    Args:
        topic: The topic title from Notion
        use_llm: Whether to use LLM for uncertain cases (default True)

    Returns:
        TopicValidation with is_valid, reason, and optional suggested_topic
    """
    if not topic or len(topic.strip()) < 3:
        return TopicValidation(
            is_valid=False,
            reason="Topic is empty or too short",
            confidence=1.0
        )

    topic = topic.strip()

    # Quick keyword check first
    quick_result = quick_keyword_check(topic)
    if quick_result is not None:
        logger.debug(f"Quick validation for '{topic}': {quick_result.is_valid} ({quick_result.reason})")
        return quick_result

    # Use LLM for uncertain cases
    if use_llm:
        logger.debug(f"Using LLM validation for uncertain topic: '{topic}'")
        return validate_with_llm(topic)

    # Without LLM, default to valid for uncertain cases
    return TopicValidation(
        is_valid=True,
        reason="Passed basic validation (LLM disabled)",
        confidence=0.6
    )


def batch_validate_topics(topics: list, use_llm: bool = True) -> dict:
    """
    Validate multiple topics and return categorized results.

    Returns:
        Dict with 'valid', 'invalid', and 'uncertain' lists
    """
    results = {'valid': [], 'invalid': [], 'uncertain': []}

    for topic in topics:
        result = validate_topic(topic, use_llm=use_llm)

        if result.confidence < 0.6:
            results['uncertain'].append({'topic': topic, 'result': result})
        elif result.is_valid:
            results['valid'].append({'topic': topic, 'result': result})
        else:
            results['invalid'].append({'topic': topic, 'result': result})

    return results


# CLI for testing
if __name__ == "__main__":
    import sys

    test_topics = [
        # Should be VALID
        "Finding Inner Peace Through Nature",
        "Healing Your Inner Child",
        "Journey to the Garden of Eden",
        "Overcoming Fear and Anxiety",
        "Meeting Your Spirit Guide",
        "Deep Sleep Relaxation",
        "Shadow Work Integration",
        "Cosmic Consciousness Awakening",

        # Should be INVALID
        "Marketing Plan for Q4",
        "Landing Page Code",
        "SEO AEO Strategy",
        "Paypal Buttons Implementation",
        "Recursive agents for RAG",
        "YouTube Upload Schedule",
        "Email Campaign Setup",
        "Coding for dreamweaving",  # Meta/technical
    ]

    if len(sys.argv) > 1:
        # Validate specific topic
        topic = " ".join(sys.argv[1:])
        result = validate_topic(topic)
        print(f"\nTopic: {topic}")
        print(f"Valid: {result.is_valid}")
        print(f"Reason: {result.reason}")
        print(f"Confidence: {result.confidence:.0%}")
        if result.suggested_topic:
            print(f"Suggested: {result.suggested_topic}")
    else:
        # Run test suite
        print("=" * 60)
        print("TOPIC VALIDATOR TEST SUITE")
        print("=" * 60)

        for topic in test_topics:
            result = validate_topic(topic, use_llm=True)
            status = "✅" if result.is_valid else "❌"
            print(f"{status} {topic[:45]:<45} | {result.reason[:35]}")

        print()
        print("=" * 60)
