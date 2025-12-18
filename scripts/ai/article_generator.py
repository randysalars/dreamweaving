#!/usr/bin/env python3
"""
Dreamweaver Article Generator

Generates trust-building, SEO-optimized articles that:
- Stand alone even if reader never subscribes
- Attract search traffic for emotional/spiritual queries
- Build recognition before asking for anything
- Use consistent Dreamweaver voice

Philosophy: "The content must stand alone even if they never subscribe."
"""

import os
import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ArticleType(Enum):
    """Types of trust-building articles"""
    QUIET_REFLECTION = "quiet_reflection"      # "A quiet reflection for those who..."
    GUIDED_JOURNEY = "guided_journey"          # Preview of a Dreamweaving theme
    SEASONAL = "seasonal"                      # Christmas, Advent, Easter, etc.
    SYMBOLIC_STORY = "symbolic_story"          # Mythic/archetypal narratives
    FAITH_EXPLORATION = "faith_exploration"    # When faith feels thin, etc.
    INNER_LIFE = "inner_life"                  # The interior landscape


@dataclass
class ArticleSpec:
    """Specification for article generation"""
    title: str
    article_type: ArticleType
    target_keywords: List[str]
    emotional_state: str  # What the reader is feeling when they search
    word_count_target: int = 1200
    tone: str = "gentle, honest, permission-giving"
    seasonal_context: Optional[str] = None
    related_dreamweaving: Optional[str] = None


class ArticleGenerator:
    """
    Generates Dreamweaver-voice articles for trust building and SEO.

    Key Principles:
    - Recognition signals: "You're not strange for feeling this"
    - Safety signaling: No pressure, no selling
    - Emotional resonance before opt-in
    - Evergreen content that ages well
    """

    # Voice Guidelines
    VOICE_GUIDELINES = """
    DREAMWEAVER VOICE CHARACTERISTICS:

    Tone:
    - Gentle but not soft
    - Honest but not harsh
    - Spacious - leave room for the reader
    - Permission-giving, never prescriptive

    Recognition Signals (use these):
    - "You're not strange for feeling this."
    - "Many people carry this quietly."
    - "This doesn't mean something is wrong."
    - "You don't have to fix this immediately."

    Structure:
    - Open with recognition of the reader's state
    - Explore without prescribing solutions
    - Use "we" and "many people" rather than "you should"
    - Close with permission or blessing, not call to action

    Forbidden:
    - "Subscribe to learn more"
    - "Buy now"
    - Urgency language
    - Hype or enthusiasm
    - Lists of tips
    - Productivity framing
    - Self-help tone

    The article must help whether or not they ever return.
    """

    # SEO Guidelines
    SEO_GUIDELINES = """
    SEO APPROACH FOR DREAMWEAVER:

    Target Searches (emotional/spiritual intent):
    - "when faith feels thin"
    - "quiet spiritual reflection"
    - "meditation for loneliness"
    - "feeling spiritually tired"
    - "guided meditation meaning"
    - "something feels missing spiritually"

    Keyword Placement:
    - Primary keyword in title (naturally)
    - Primary keyword in first paragraph
    - Related keywords throughout (not forced)
    - Meta description should match search intent

    Content Structure:
    - H1: Main title (includes primary keyword)
    - Opening paragraph: Acknowledge reader's search intent
    - Body: Explore the theme deeply
    - Closing: Permission, not pitch

    What NOT to optimize for:
    - Click-bait headlines
    - Trending topics
    - High-volume commercial keywords
    - Anything that attracts the wrong audience
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the article generator"""
        self.project_root = Path(__file__).parent.parent.parent
        self.config_path = config_path or self.project_root / "config" / "seo_keywords.yaml"
        self.templates_path = self.project_root / "knowledge" / "article_templates.yaml"
        self.output_path = self.project_root / "content" / "articles"

        # Ensure output directory exists
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Load configurations
        self.keywords = self._load_keywords()
        self.templates = self._load_templates()

        # Initialize Anthropic client if available
        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            self.client = anthropic.Anthropic()
            self.ai_enabled = True
        else:
            self.client = None
            self.ai_enabled = False

    def _load_keywords(self) -> Dict:
        """Load SEO keyword configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f) or {}
        return {}

    def _load_templates(self) -> Dict:
        """Load article templates"""
        if self.templates_path.exists():
            with open(self.templates_path) as f:
                return yaml.safe_load(f) or {}
        return {}

    def generate_article(
        self,
        spec: ArticleSpec,
        model: str = "claude-sonnet-4-20250514"
    ) -> Dict[str, Any]:
        """
        Generate a trust-building article.

        Args:
            spec: Article specification
            model: Claude model to use

        Returns:
            Dictionary with article content and metadata
        """
        if not self.ai_enabled:
            return {
                "success": False,
                "error": "AI generation not available. Set ANTHROPIC_API_KEY."
            }

        # Build prompt
        prompt = self._build_prompt(spec)

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.content[0].text

            # Parse the generated content
            result = self._parse_generated_content(content, spec)

            # Save the article
            self._save_article(result)

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _build_prompt(self, spec: ArticleSpec) -> str:
        """Build the generation prompt"""

        # Get template for this article type
        template_guidance = self.templates.get(spec.article_type.value, "")

        prompt = f"""You are writing a Dreamweaver article. This is for a website that creates
guided inner journeys for people seeking peace, meaning, and spiritual depth.

{self.VOICE_GUIDELINES}

{self.SEO_GUIDELINES}

ARTICLE SPECIFICATION:
- Title: {spec.title}
- Type: {spec.article_type.value}
- Target Keywords: {', '.join(spec.target_keywords)}
- Reader's Emotional State: {spec.emotional_state}
- Word Count Target: {spec.word_count_target}
- Tone: {spec.tone}
{f'- Seasonal Context: {spec.seasonal_context}' if spec.seasonal_context else ''}
{f'- Related Dreamweaving: {spec.related_dreamweaving}' if spec.related_dreamweaving else ''}

{template_guidance}

CRITICAL REQUIREMENTS:
1. The article must help the reader whether or not they ever subscribe or return
2. No calls to action to subscribe, buy, or "learn more"
3. End with permission or blessing, not a pitch
4. Use recognition signals naturally
5. Match the emotional search intent
6. Write in the Dreamweaver voice consistently

OUTPUT FORMAT:
Please provide the article in this exact format:

---META---
title: [SEO-optimized title]
meta_description: [155 characters max, matches search intent]
primary_keyword: [main keyword]
secondary_keywords: [comma-separated]
estimated_reading_time: [X minutes]
---END_META---

---ARTICLE---
[Full article content in markdown]
---END_ARTICLE---

---SNIPPET---
[2-3 sentence excerpt for social sharing]
---END_SNIPPET---

Generate the article now:
"""
        return prompt

    def _parse_generated_content(
        self,
        content: str,
        spec: ArticleSpec
    ) -> Dict[str, Any]:
        """Parse the generated content into structured format"""

        result = {
            "success": True,
            "spec": {
                "title": spec.title,
                "type": spec.article_type.value,
                "keywords": spec.target_keywords
            },
            "generated_at": datetime.now().isoformat()
        }

        # Parse META section
        if "---META---" in content and "---END_META---" in content:
            meta_section = content.split("---META---")[1].split("---END_META---")[0]
            meta = {}
            for line in meta_section.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip()
            result["meta"] = meta

        # Parse ARTICLE section
        if "---ARTICLE---" in content and "---END_ARTICLE---" in content:
            article = content.split("---ARTICLE---")[1].split("---END_ARTICLE---")[0]
            result["article"] = article.strip()

        # Parse SNIPPET section
        if "---SNIPPET---" in content and "---END_SNIPPET---" in content:
            snippet = content.split("---SNIPPET---")[1].split("---END_SNIPPET---")[0]
            result["snippet"] = snippet.strip()

        return result

    def _save_article(self, result: Dict):
        """Save the generated article"""
        if not result.get("success") or not result.get("article"):
            return

        # Generate filename from title
        title = result.get("meta", {}).get("title", "untitled")
        slug = title.lower().replace(" ", "-").replace("'", "")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")[:50]

        filename = f"{datetime.now().strftime('%Y%m%d')}_{slug}.md"
        filepath = self.output_path / filename

        # Build markdown file
        meta = result.get("meta", {})
        content = f"""---
title: "{meta.get('title', '')}"
description: "{meta.get('meta_description', '')}"
keywords: "{meta.get('secondary_keywords', '')}"
reading_time: "{meta.get('estimated_reading_time', '')}"
type: "{result['spec']['type']}"
generated: "{result['generated_at']}"
---

{result['article']}
"""

        with open(filepath, "w") as f:
            f.write(content)

        result["saved_to"] = str(filepath)

    def suggest_articles(
        self,
        count: int = 5,
        season: Optional[str] = None
    ) -> List[ArticleSpec]:
        """
        Suggest article topics based on SEO keywords and season.

        Args:
            count: Number of suggestions
            season: Optional season filter (winter, spring, summer, autumn)

        Returns:
            List of ArticleSpec suggestions
        """
        suggestions = []

        # Core evergreen topics
        evergreen_topics = [
            ArticleSpec(
                title="A Quiet Reflection for Those Who Feel Tired",
                article_type=ArticleType.QUIET_REFLECTION,
                target_keywords=["spiritual fatigue", "feeling tired spiritually", "exhausted soul"],
                emotional_state="Feeling spiritually drained, overwhelmed by life"
            ),
            ArticleSpec(
                title="When Faith Feels Thin",
                article_type=ArticleType.FAITH_EXPLORATION,
                target_keywords=["faith feels thin", "struggling with faith", "spiritual doubt"],
                emotional_state="Questioning faith, feeling distant from belief"
            ),
            ArticleSpec(
                title="For Those Who Feel Something is Missing",
                article_type=ArticleType.INNER_LIFE,
                target_keywords=["something feels missing", "spiritual longing", "meaning crisis"],
                emotional_state="Vague sense of incompleteness, searching for meaning"
            ),
            ArticleSpec(
                title="A Meditation for When You Can't Meditate",
                article_type=ArticleType.GUIDED_JOURNEY,
                target_keywords=["can't meditate", "meditation for beginners", "simple meditation"],
                emotional_state="Wanting to meditate but feeling too scattered or unable"
            ),
            ArticleSpec(
                title="The Gift of Not Knowing",
                article_type=ArticleType.SYMBOLIC_STORY,
                target_keywords=["uncertainty spirituality", "not knowing", "spiritual surrender"],
                emotional_state="Struggling with uncertainty, wanting control"
            )
        ]

        # Seasonal topics
        seasonal_topics = {
            "winter": [
                ArticleSpec(
                    title="A Christmas Reflection for Those Who Feel Alone",
                    article_type=ArticleType.SEASONAL,
                    target_keywords=["Christmas loneliness", "alone at Christmas", "holiday solitude"],
                    emotional_state="Feeling isolated during the holiday season",
                    seasonal_context="Christmas/Winter holidays"
                ),
                ArticleSpec(
                    title="On Waiting: An Advent Reflection",
                    article_type=ArticleType.SEASONAL,
                    target_keywords=["Advent reflection", "spiritual waiting", "Advent meditation"],
                    emotional_state="In a season of anticipation and waiting",
                    seasonal_context="Advent"
                )
            ],
            "spring": [
                ArticleSpec(
                    title="When Renewal Doesn't Come Easily",
                    article_type=ArticleType.SEASONAL,
                    target_keywords=["spring renewal", "Easter hope", "struggling with hope"],
                    emotional_state="Feeling disconnected from spring's promise of renewal",
                    seasonal_context="Easter/Spring"
                )
            ],
            "autumn": [
                ArticleSpec(
                    title="A Reflection on Letting Go",
                    article_type=ArticleType.SEASONAL,
                    target_keywords=["letting go spiritually", "autumn reflection", "release meditation"],
                    emotional_state="Holding on to what needs releasing",
                    seasonal_context="Autumn"
                )
            ]
        }

        # Add evergreen topics
        suggestions.extend(evergreen_topics[:count])

        # Add seasonal topics if applicable
        if season and season.lower() in seasonal_topics:
            suggestions.extend(seasonal_topics[season.lower()])

        return suggestions[:count]

    def analyze_existing_content(self) -> Dict:
        """Analyze existing articles for gaps and opportunities"""
        analysis = {
            "total_articles": 0,
            "by_type": {},
            "by_keyword": {},
            "gaps": [],
            "suggestions": []
        }

        # Count existing articles
        if self.output_path.exists():
            for file in self.output_path.glob("*.md"):
                analysis["total_articles"] += 1

        # Identify gaps based on keyword config
        covered_keywords = set()
        target_keywords = set(self.keywords.get("primary", []))

        for kw in target_keywords - covered_keywords:
            analysis["gaps"].append(kw)

        return analysis


def main():
    """CLI for article generator"""
    import argparse

    parser = argparse.ArgumentParser(description="Dreamweaver Article Generator")
    parser.add_argument("--suggest", action="store_true", help="Suggest article topics")
    parser.add_argument("--season", type=str, help="Season for suggestions")
    parser.add_argument("--generate", type=str, help="Generate article from topic")
    parser.add_argument("--analyze", action="store_true", help="Analyze content gaps")
    parser.add_argument("--count", type=int, default=5, help="Number of suggestions")

    args = parser.parse_args()

    generator = ArticleGenerator()

    if args.suggest:
        suggestions = generator.suggest_articles(
            count=args.count,
            season=args.season
        )
        print("\n=== Suggested Articles ===")
        for i, spec in enumerate(suggestions, 1):
            print(f"\n{i}. {spec.title}")
            print(f"   Type: {spec.article_type.value}")
            print(f"   Keywords: {', '.join(spec.target_keywords)}")
            print(f"   Reader State: {spec.emotional_state}")

    elif args.generate:
        # Create spec from topic
        spec = ArticleSpec(
            title=args.generate,
            article_type=ArticleType.QUIET_REFLECTION,
            target_keywords=[args.generate.lower()],
            emotional_state="Seeking reflection on this topic"
        )
        result = generator.generate_article(spec)
        if result.get("success"):
            print(f"\n=== Article Generated ===")
            print(f"Saved to: {result.get('saved_to', 'N/A')}")
            print(f"Title: {result.get('meta', {}).get('title', 'N/A')}")
        else:
            print(f"Error: {result.get('error')}")

    elif args.analyze:
        analysis = generator.analyze_existing_content()
        print("\n=== Content Analysis ===")
        print(f"Total Articles: {analysis['total_articles']}")
        print(f"Keyword Gaps: {len(analysis['gaps'])}")
        for gap in analysis['gaps'][:10]:
            print(f"  - {gap}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
