"""
ContentAnalyzer for automatic dreamweaving categorization.

Uses weighted multi-signal approach to match session content to categories.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .keywords import CATEGORY_KEYWORDS, ARCHETYPE_CATEGORIES, FREQUENCY_CATEGORIES


@dataclass
class CategoryMatch:
    """Represents a category match with confidence score."""
    slug: str
    name: str
    confidence: float
    signals: Dict[str, float]  # Individual signal scores

    def __repr__(self):
        return f"CategoryMatch({self.slug}, confidence={self.confidence:.2f})"


class ContentAnalyzer:
    """
    Multi-signal content analyzer for automatic categorization.

    Weights:
    - Title keywords: 0.30
    - Description/topic: 0.25
    - Archetypes: 0.20
    - Theme metadata: 0.15
    - Binaural frequency: 0.10
    """

    # Signal weights
    WEIGHT_TITLE = 0.30
    WEIGHT_DESCRIPTION = 0.25
    WEIGHT_ARCHETYPES = 0.20
    WEIGHT_THEME = 0.15
    WEIGHT_FREQUENCY = 0.10

    # Confidence thresholds
    HIGH_CONFIDENCE = 0.7
    MEDIUM_CONFIDENCE = 0.4

    def __init__(self):
        self.category_keywords = CATEGORY_KEYWORDS
        self.archetype_categories = ARCHETYPE_CATEGORIES
        self.frequency_categories = FREQUENCY_CATEGORIES

        # Build category name mapping
        self.category_names = self._build_category_names()

    def _build_category_names(self) -> Dict[str, str]:
        """Build slug to display name mapping."""
        names = {}
        for slug in self.category_keywords:
            # Convert slug to title case name
            name = slug.replace("-", " ").title()
            names[slug] = name
        return names

    def analyze(self, session_data: Dict) -> List[CategoryMatch]:
        """
        Analyze session data and return ranked category matches.

        Args:
            session_data: Dict containing:
                - title: Session title
                - description: Session description/topic
                - archetypes: List of archetype names
                - theme: Theme string or list
                - binaural_frequency: Target frequency in Hz or band name
                - tags: Optional list of tags

        Returns:
            List of CategoryMatch objects sorted by confidence (highest first)
        """
        scores: Dict[str, Dict[str, float]] = {
            slug: {"title": 0, "description": 0, "archetypes": 0, "theme": 0, "frequency": 0}
            for slug in self.category_keywords
        }

        # Signal 1: Title keywords
        title = session_data.get("title", "")
        title_scores = self._match_text(title, weight_multiplier=1.5)
        for slug, score in title_scores.items():
            scores[slug]["title"] = score

        # Signal 2: Description/topic
        description = session_data.get("description", "")
        topic = session_data.get("topic", "")
        combined_text = f"{description} {topic}"
        desc_scores = self._match_text(combined_text, weight_multiplier=1.0)
        for slug, score in desc_scores.items():
            scores[slug]["description"] = score

        # Signal 3: Archetypes
        archetypes = session_data.get("archetypes", [])
        if isinstance(archetypes, str):
            archetypes = [archetypes]
        arch_scores = self._match_archetypes(archetypes)
        for slug, score in arch_scores.items():
            scores[slug]["archetypes"] = score

        # Signal 4: Theme metadata
        theme = session_data.get("theme", "")
        if isinstance(theme, list):
            theme = " ".join(theme)
        tags = session_data.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        theme_text = f"{theme} {' '.join(tags)}"
        theme_scores = self._match_text(theme_text, weight_multiplier=1.2)
        for slug, score in theme_scores.items():
            scores[slug]["theme"] = score

        # Signal 5: Binaural frequency
        frequency = session_data.get("binaural_frequency", None)
        freq_scores = self._match_frequency(frequency)
        for slug, score in freq_scores.items():
            scores[slug]["frequency"] = score

        # Calculate weighted total scores
        matches = []
        for slug, signal_scores in scores.items():
            total = (
                signal_scores["title"] * self.WEIGHT_TITLE +
                signal_scores["description"] * self.WEIGHT_DESCRIPTION +
                signal_scores["archetypes"] * self.WEIGHT_ARCHETYPES +
                signal_scores["theme"] * self.WEIGHT_THEME +
                signal_scores["frequency"] * self.WEIGHT_FREQUENCY
            )

            if total > 0:
                matches.append(CategoryMatch(
                    slug=slug,
                    name=self.category_names.get(slug, slug),
                    confidence=min(total, 1.0),  # Cap at 1.0
                    signals=signal_scores
                ))

        # Sort by confidence (highest first)
        matches.sort(key=lambda m: m.confidence, reverse=True)

        return matches

    def _match_text(self, text: str, weight_multiplier: float = 1.0) -> Dict[str, float]:
        """
        Match text against category keywords.

        Returns dict of slug -> score (0-1 range).
        """
        if not text:
            return {}

        text_lower = text.lower()
        scores = {}

        for slug, keywords in self.category_keywords.items():
            primary = keywords.get("primary", [])
            secondary = keywords.get("secondary", [])
            priority = keywords.get("priority", 100)

            score = 0.0
            primary_matches = 0
            secondary_matches = 0

            # Check primary keywords (weight: 1.0)
            for keyword in primary:
                if self._keyword_in_text(keyword.lower(), text_lower):
                    primary_matches += 1
                    score += 1.0 * weight_multiplier

            # Check secondary keywords (weight: 0.5)
            for keyword in secondary:
                if self._keyword_in_text(keyword.lower(), text_lower):
                    secondary_matches += 1
                    score += 0.5 * weight_multiplier

            # Normalize by total possible keywords
            total_keywords = len(primary) + len(secondary) * 0.5
            if total_keywords > 0 and score > 0:
                # Normalize to 0-1 range with diminishing returns
                normalized = min(score / (total_keywords * 0.3), 1.0)

                # Apply priority bonus (lower priority = higher bonus)
                priority_bonus = 1.0 + (100 - min(priority, 100)) / 500
                scores[slug] = normalized * priority_bonus

        return scores

    def _keyword_in_text(self, keyword: str, text: str) -> bool:
        """Check if keyword appears in text with word boundary awareness."""
        # For multi-word keywords, check exact phrase
        if " " in keyword:
            return keyword in text

        # For single words, use word boundaries
        pattern = r'\b' + re.escape(keyword) + r'\b'
        return bool(re.search(pattern, text))

    def _match_archetypes(self, archetypes: List[str]) -> Dict[str, float]:
        """
        Match archetypes to categories.

        Returns dict of slug -> score (0-1 range).
        """
        if not archetypes:
            return {}

        scores = {}

        for archetype in archetypes:
            arch_lower = archetype.lower()

            # Direct archetype mapping
            for arch_name, categories in self.archetype_categories.items():
                if arch_lower == arch_name.lower() or arch_lower in arch_name.lower():
                    for cat_slug in categories:
                        if cat_slug in scores:
                            scores[cat_slug] = min(scores[cat_slug] + 0.5, 1.0)
                        else:
                            scores[cat_slug] = 0.5

            # Also check keywords for archetype names
            for slug, keywords in self.category_keywords.items():
                primary = keywords.get("primary", [])
                if arch_lower in [k.lower() for k in primary]:
                    if slug in scores:
                        scores[slug] = min(scores[slug] + 0.3, 1.0)
                    else:
                        scores[slug] = 0.3

        return scores

    def _match_frequency(self, frequency) -> Dict[str, float]:
        """
        Match binaural frequency to category hints.

        Args:
            frequency: Hz value (number) or band name (string like "theta")

        Returns dict of slug -> score (0-1 range).
        """
        if not frequency:
            return {}

        scores = {}
        band = None

        # Determine band from frequency or string
        if isinstance(frequency, (int, float)):
            if frequency < 4:
                band = "delta"
            elif frequency < 8:
                band = "theta"
            elif frequency < 12:
                band = "alpha"
            elif frequency < 30:
                band = "beta"
            else:
                band = "gamma"
        elif isinstance(frequency, str):
            band = frequency.lower()

        if band and band in self.frequency_categories:
            for cat_slug in self.frequency_categories[band]:
                scores[cat_slug] = 0.7  # Strong hint from frequency

        return scores

    def categorize_with_fallback(self, session_data: Dict) -> Dict:
        """
        Categorize session with fallback logic for low confidence.

        Returns dict with:
            - category: Selected category slug
            - auto: Whether auto-categorized (True) or fallback (False)
            - confidence: Confidence score
            - alternatives: Top alternative categories
            - review_suggested: Whether manual review is recommended
            - needs_review: Whether categorization failed and needs manual assignment
        """
        matches = self.analyze(session_data)

        if not matches:
            # No matches at all - use safe default
            return {
                "category": "guided-visualization",  # Safe default
                "auto": False,
                "confidence": 0.0,
                "alternatives": [],
                "review_suggested": False,
                "needs_review": True,
                "message": "No category keywords matched. Using default."
            }

        top_match = matches[0]
        alternatives = [m.slug for m in matches[1:4]]  # Top 3 alternatives

        if top_match.confidence >= self.HIGH_CONFIDENCE:
            # High confidence - auto-assign
            return {
                "category": top_match.slug,
                "auto": True,
                "confidence": top_match.confidence,
                "alternatives": alternatives,
                "review_suggested": False,
                "needs_review": False,
                "message": f"High confidence match: {top_match.name}"
            }

        if top_match.confidence >= self.MEDIUM_CONFIDENCE:
            # Medium confidence - assign but suggest review
            return {
                "category": top_match.slug,
                "auto": True,
                "confidence": top_match.confidence,
                "alternatives": alternatives,
                "review_suggested": True,
                "needs_review": False,
                "message": f"Medium confidence match: {top_match.name}. Review suggested."
            }

        # Low confidence - assign best guess but flag for review
        return {
            "category": top_match.slug,
            "auto": False,
            "confidence": top_match.confidence,
            "alternatives": alternatives,
            "review_suggested": True,
            "needs_review": True,
            "message": f"Low confidence ({top_match.confidence:.2f}). Manual review recommended."
        }

    def explain_categorization(self, session_data: Dict) -> str:
        """
        Generate human-readable explanation of categorization decision.

        Useful for debugging and understanding category assignments.
        """
        matches = self.analyze(session_data)
        result = self.categorize_with_fallback(session_data)

        lines = [
            "=" * 60,
            "CATEGORIZATION ANALYSIS",
            "=" * 60,
            "",
            f"Selected Category: {result['category']}",
            f"Confidence: {result['confidence']:.2%}",
            f"Auto-assigned: {result['auto']}",
            f"Review suggested: {result['review_suggested']}",
            "",
            "Signal Breakdown (Top Match):",
            "-" * 40,
        ]

        if matches:
            top = matches[0]
            lines.extend([
                f"  Title signal:       {top.signals['title']:.2f} (weight: {self.WEIGHT_TITLE})",
                f"  Description signal: {top.signals['description']:.2f} (weight: {self.WEIGHT_DESCRIPTION})",
                f"  Archetypes signal:  {top.signals['archetypes']:.2f} (weight: {self.WEIGHT_ARCHETYPES})",
                f"  Theme signal:       {top.signals['theme']:.2f} (weight: {self.WEIGHT_THEME})",
                f"  Frequency signal:   {top.signals['frequency']:.2f} (weight: {self.WEIGHT_FREQUENCY})",
                "",
                "Top 5 Category Matches:",
                "-" * 40,
            ])

            for i, match in enumerate(matches[:5], 1):
                lines.append(f"  {i}. {match.name} ({match.slug}): {match.confidence:.2%}")

        if result.get("alternatives"):
            lines.extend([
                "",
                "Alternatives considered:",
                "-" * 40,
            ])
            for alt in result["alternatives"]:
                lines.append(f"  - {alt}")

        lines.extend([
            "",
            "=" * 60,
        ])

        return "\n".join(lines)


def get_available_categories() -> List[Dict[str, str]]:
    """
    Get list of all available categories for display/selection.

    Returns list of dicts with slug and name.
    """
    categories = []
    for slug in sorted(CATEGORY_KEYWORDS.keys()):
        name = slug.replace("-", " ").title()
        priority = CATEGORY_KEYWORDS[slug].get("priority", 100)
        categories.append({
            "slug": slug,
            "name": name,
            "priority": priority
        })

    # Sort by priority
    categories.sort(key=lambda c: c["priority"])
    return categories


# Convenience function for direct use
def categorize_session(session_data: Dict) -> Dict:
    """
    Quick categorization function.

    Args:
        session_data: Dict with title, description, archetypes, theme, binaural_frequency

    Returns:
        Categorization result dict
    """
    analyzer = ContentAnalyzer()
    return analyzer.categorize_with_fallback(session_data)
