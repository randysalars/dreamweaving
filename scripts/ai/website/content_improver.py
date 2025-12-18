"""
Content Improver for Website Recursive Agent.

Auto-generates improvement suggestions for underperforming pages
based on patterns from top performers.

Features:
- Extract success patterns from top performers
- Generate specific improvement suggestions
- Track improvement outcomes
- Learn from what works
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import json
import re

from .content_tracker import ContentTracker, PagePerformance

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


@dataclass
class ImprovementSuggestion:
    """A suggested improvement for a page."""

    page_path: str
    suggestion_type: str  # title | content | structure | cta | media | meta
    priority: str  # high | medium | low

    # The suggestion
    current_value: str = ""
    suggested_value: str = ""
    rationale: str = ""

    # Impact estimate
    estimated_engagement_delta: float = 0.0

    # Source patterns
    based_on_patterns: List[str] = field(default_factory=list)

    # Tracking
    id: str = ""
    status: str = "pending"  # pending | applied | rejected | tested
    created_at: Optional[str] = None
    applied_at: Optional[str] = None

    # Outcome (if applied)
    actual_engagement_delta: Optional[float] = None


@dataclass
class SuccessPattern:
    """A pattern extracted from successful content."""

    pattern_type: str  # title | hook | structure | cta | media_placement
    pattern_description: str
    examples: List[str] = field(default_factory=list)

    # Effectiveness
    avg_engagement_score: float = 0.0
    occurrences: int = 0

    # Application scope
    content_types: List[str] = field(default_factory=list)


class ContentImprover:
    """
    Generate improvement suggestions for website content.

    Approach:
    1. Analyze top performers to extract success patterns
    2. Analyze underperformers to identify gaps
    3. Generate specific, actionable suggestions
    4. Track outcomes when suggestions are applied
    5. Learn and refine pattern recognition
    """

    # Improvement types with priorities
    IMPROVEMENT_TYPES = {
        'title': {'priority': 'high', 'impact_estimate': 10.0},
        'hook': {'priority': 'high', 'impact_estimate': 8.0},
        'cta': {'priority': 'medium', 'impact_estimate': 6.0},
        'structure': {'priority': 'medium', 'impact_estimate': 5.0},
        'media': {'priority': 'medium', 'impact_estimate': 7.0},
        'meta': {'priority': 'low', 'impact_estimate': 3.0},
    }

    def __init__(
        self,
        project_root: Optional[Path] = None,
        content_tracker: Optional[ContentTracker] = None,
    ):
        """
        Initialize content improver.

        Args:
            project_root: Path to project root
            content_tracker: Content tracker (created if not provided)
        """
        self.project_root = project_root or PROJECT_ROOT
        self.content_tracker = content_tracker or ContentTracker(
            project_root=self.project_root
        )

        # Data storage
        self.data_dir = self.project_root / "knowledge" / "website_improvements"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.patterns_file = self.data_dir / "success_patterns.yaml"
        self.suggestions_file = self.data_dir / "improvement_suggestions.yaml"
        self.outcomes_file = self.data_dir / "improvement_outcomes.yaml"

        # Load existing data
        self._patterns: List[SuccessPattern] = []
        self._suggestions: Dict[str, List[ImprovementSuggestion]] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Load patterns and suggestions from disk."""
        # Load patterns
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file) as f:
                    data = yaml.safe_load(f) or []
                self._patterns = [
                    SuccessPattern(**p) for p in data
                ]
            except Exception:
                self._patterns = []

        # Load suggestions
        if self.suggestions_file.exists():
            try:
                with open(self.suggestions_file) as f:
                    data = yaml.safe_load(f) or {}
                self._suggestions = {
                    path: [ImprovementSuggestion(**s) for s in suggestions]
                    for path, suggestions in data.items()
                }
            except Exception:
                self._suggestions = {}

    def _save_patterns(self) -> None:
        """Save patterns to disk."""
        data = [
            {
                'pattern_type': p.pattern_type,
                'pattern_description': p.pattern_description,
                'examples': p.examples,
                'avg_engagement_score': p.avg_engagement_score,
                'occurrences': p.occurrences,
                'content_types': p.content_types,
            }
            for p in self._patterns
        ]
        with open(self.patterns_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    def _save_suggestions(self) -> None:
        """Save suggestions to disk."""
        data = {
            path: [
                {
                    'page_path': s.page_path,
                    'suggestion_type': s.suggestion_type,
                    'priority': s.priority,
                    'current_value': s.current_value,
                    'suggested_value': s.suggested_value,
                    'rationale': s.rationale,
                    'estimated_engagement_delta': s.estimated_engagement_delta,
                    'based_on_patterns': s.based_on_patterns,
                    'id': s.id,
                    'status': s.status,
                    'created_at': s.created_at,
                    'applied_at': s.applied_at,
                    'actual_engagement_delta': s.actual_engagement_delta,
                }
                for s in suggestions
            ]
            for path, suggestions in self._suggestions.items()
        }
        with open(self.suggestions_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    def extract_patterns(self) -> List[SuccessPattern]:
        """
        Extract success patterns from top performing pages.

        Analyzes:
        - Title patterns (length, keywords, structure)
        - Hook patterns (first paragraph structure)
        - CTA patterns (placement, wording)
        - Media patterns (video/audio presence)
        - Structure patterns (sections, headings)

        Returns:
            List of extracted success patterns
        """
        top_performers = self.content_tracker.get_top_performers(limit=20)

        patterns = []

        # Analyze title patterns
        title_patterns = self._extract_title_patterns(top_performers)
        patterns.extend(title_patterns)

        # Analyze structure patterns
        structure_patterns = self._extract_structure_patterns(top_performers)
        patterns.extend(structure_patterns)

        # Analyze media patterns
        media_patterns = self._extract_media_patterns(top_performers)
        patterns.extend(media_patterns)

        # Update stored patterns
        self._patterns = patterns
        self._save_patterns()

        return patterns

    def _extract_title_patterns(
        self,
        performers: List[PagePerformance],
    ) -> List[SuccessPattern]:
        """Extract patterns from successful page titles."""
        patterns = []

        # Collect titles
        titles = [p.page_title for p in performers if p.page_title]

        if not titles:
            return patterns

        # Analyze title length
        avg_length = sum(len(t) for t in titles) / len(titles)
        if 40 <= avg_length <= 60:
            patterns.append(SuccessPattern(
                pattern_type='title',
                pattern_description=f"Optimal title length: {int(avg_length)} characters",
                examples=titles[:3],
                avg_engagement_score=sum(
                    p.current_engagement_score for p in performers
                ) / len(performers),
                occurrences=len(performers),
                content_types=['all'],
            ))

        # Look for common patterns
        # Power words
        power_words = ['sacred', 'journey', 'transform', 'discover', 'unlock', 'healing']
        titles_with_power = [
            t for t in titles
            if any(w in t.lower() for w in power_words)
        ]
        if len(titles_with_power) >= 3:
            patterns.append(SuccessPattern(
                pattern_type='title',
                pattern_description="Use power words (sacred, journey, transform, etc.)",
                examples=titles_with_power[:3],
                avg_engagement_score=70.0,  # Estimated
                occurrences=len(titles_with_power),
                content_types=['dreamweaving', 'article'],
            ))

        return patterns

    def _extract_structure_patterns(
        self,
        performers: List[PagePerformance],
    ) -> List[SuccessPattern]:
        """Extract patterns from page structure."""
        patterns = []

        # Pattern: Pages with media have higher engagement
        media_pages = [p for p in performers if p.has_video or p.has_audio]
        if len(media_pages) >= 3:
            avg_engagement = sum(
                p.current_engagement_score for p in media_pages
            ) / len(media_pages)
            patterns.append(SuccessPattern(
                pattern_type='media',
                pattern_description="Include video or audio content",
                examples=[p.page_path for p in media_pages[:3]],
                avg_engagement_score=avg_engagement,
                occurrences=len(media_pages),
                content_types=['dreamweaving', 'article'],
            ))

        return patterns

    def _extract_media_patterns(
        self,
        performers: List[PagePerformance],
    ) -> List[SuccessPattern]:
        """Extract patterns related to media usage."""
        patterns = []

        # Analyze by content type
        dreamweavings = [p for p in performers if p.content_type == 'dreamweaving']

        if dreamweavings:
            with_audio = [p for p in dreamweavings if p.has_audio]
            if len(with_audio) >= 2:
                patterns.append(SuccessPattern(
                    pattern_type='media',
                    pattern_description="Dreamweaving pages with audio have higher engagement",
                    examples=[p.page_path for p in with_audio[:3]],
                    avg_engagement_score=sum(
                        p.current_engagement_score for p in with_audio
                    ) / len(with_audio),
                    occurrences=len(with_audio),
                    content_types=['dreamweaving'],
                ))

        return patterns

    def suggest_improvements(
        self,
        page_path: str,
    ) -> List[ImprovementSuggestion]:
        """
        Generate improvement suggestions for a specific page.

        Args:
            page_path: Path of page to improve

        Returns:
            List of improvement suggestions
        """
        # Get current performance
        performance = self.content_tracker.track_page(page_path)
        if not performance:
            return []

        # Get success patterns
        if not self._patterns:
            self.extract_patterns()

        suggestions = []

        # Generate suggestions based on patterns
        for pattern in self._patterns:
            # Check if pattern applies to this content type
            if (
                pattern.content_types != ['all']
                and performance.content_type not in pattern.content_types
            ):
                continue

            # Generate suggestion based on pattern type
            suggestion = self._generate_suggestion(
                page_path=page_path,
                performance=performance,
                pattern=pattern,
            )

            if suggestion:
                suggestions.append(suggestion)

        # Store suggestions
        self._suggestions[page_path] = suggestions
        self._save_suggestions()

        return suggestions

    def _generate_suggestion(
        self,
        page_path: str,
        performance: PagePerformance,
        pattern: SuccessPattern,
    ) -> Optional[ImprovementSuggestion]:
        """Generate a specific suggestion from a pattern."""
        import uuid

        suggestion_type = pattern.pattern_type
        config = self.IMPROVEMENT_TYPES.get(suggestion_type, {})

        suggestion = ImprovementSuggestion(
            id=str(uuid.uuid4())[:8],
            page_path=page_path,
            suggestion_type=suggestion_type,
            priority=config.get('priority', 'medium'),
            current_value=self._get_current_value(performance, pattern),
            suggested_value=pattern.pattern_description,
            rationale=f"Based on {pattern.occurrences} top performers. "
                     f"Avg engagement: {pattern.avg_engagement_score:.1f}",
            estimated_engagement_delta=config.get('impact_estimate', 5.0),
            based_on_patterns=[pattern.pattern_description],
            created_at=datetime.now().isoformat(),
            status='pending',
        )

        return suggestion

    def _get_current_value(
        self,
        performance: PagePerformance,
        pattern: SuccessPattern,
    ) -> str:
        """Get current value for comparison with pattern."""
        if pattern.pattern_type == 'title':
            return performance.page_title
        if pattern.pattern_type == 'media':
            if performance.has_video:
                return "Has video"
            if performance.has_audio:
                return "Has audio"
            return "No media"
        return f"Current engagement: {performance.current_engagement_score:.1f}"

    def suggest_improvements_for_underperformers(
        self,
        limit: int = 10,
    ) -> Dict[str, List[ImprovementSuggestion]]:
        """
        Generate suggestions for all underperforming pages.

        Args:
            limit: Maximum pages to process

        Returns:
            Dict mapping page paths to their suggestions
        """
        underperformers = self.content_tracker.get_pages_needing_attention(limit=limit)

        all_suggestions = {}
        for page in underperformers:
            suggestions = self.suggest_improvements(page.page_path)
            if suggestions:
                all_suggestions[page.page_path] = suggestions

        return all_suggestions

    def mark_suggestion_applied(
        self,
        page_path: str,
        suggestion_id: str,
    ) -> bool:
        """
        Mark a suggestion as applied.

        Args:
            page_path: Page path
            suggestion_id: Suggestion ID

        Returns:
            True if marked successfully
        """
        if page_path not in self._suggestions:
            return False

        for suggestion in self._suggestions[page_path]:
            if suggestion.id == suggestion_id:
                suggestion.status = 'applied'
                suggestion.applied_at = datetime.now().isoformat()
                self._save_suggestions()
                return True

        return False

    def record_outcome(
        self,
        page_path: str,
        suggestion_id: str,
        engagement_delta: float,
    ) -> bool:
        """
        Record the outcome of an applied suggestion.

        Args:
            page_path: Page path
            suggestion_id: Suggestion ID
            engagement_delta: Actual engagement change

        Returns:
            True if recorded successfully
        """
        if page_path not in self._suggestions:
            return False

        for suggestion in self._suggestions[page_path]:
            if suggestion.id == suggestion_id:
                suggestion.actual_engagement_delta = engagement_delta
                suggestion.status = 'tested'
                self._save_suggestions()

                # Update pattern effectiveness based on outcome
                self._update_pattern_effectiveness(suggestion, engagement_delta)
                return True

        return False

    def _update_pattern_effectiveness(
        self,
        suggestion: ImprovementSuggestion,
        actual_delta: float,
    ) -> None:
        """Update pattern effectiveness based on measured outcome."""
        # Find and update the pattern
        for pattern in self._patterns:
            if pattern.pattern_description in suggestion.based_on_patterns:
                # Exponential moving average update
                alpha = 0.3  # Learning rate
                estimated = suggestion.estimated_engagement_delta
                pattern.avg_engagement_score = (
                    alpha * actual_delta + (1 - alpha) * estimated
                )

        self._save_patterns()

    def get_pending_suggestions(
        self,
        page_path: Optional[str] = None,
    ) -> List[ImprovementSuggestion]:
        """Get pending suggestions (not yet applied)."""
        if page_path:
            return [
                s for s in self._suggestions.get(page_path, [])
                if s.status == 'pending'
            ]

        all_pending = []
        for suggestions in self._suggestions.values():
            all_pending.extend([s for s in suggestions if s.status == 'pending'])

        return all_pending

    def get_statistics(self) -> Dict[str, Any]:
        """Get improver statistics."""
        all_suggestions = []
        for suggestions in self._suggestions.values():
            all_suggestions.extend(suggestions)

        return {
            'total_patterns': len(self._patterns),
            'total_suggestions': len(all_suggestions),
            'pending_suggestions': len([
                s for s in all_suggestions if s.status == 'pending'
            ]),
            'applied_suggestions': len([
                s for s in all_suggestions if s.status == 'applied'
            ]),
            'tested_suggestions': len([
                s for s in all_suggestions if s.status == 'tested'
            ]),
            'pages_with_suggestions': len(self._suggestions),
        }
