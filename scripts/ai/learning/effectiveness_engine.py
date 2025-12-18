"""
Effectiveness Engine - Calculates and ranks lesson effectiveness.

This module provides the scoring algorithm for lesson effectiveness,
enabling the system to prioritize lessons that have proven to improve
session outcomes.

Key features:
- Weighted composite scoring across multiple metrics
- Time decay for lesson relevance
- Context-aware recommendations
- Minimum application threshold (3+ uses before scoring)

Part of the Recursive Improver system for self-improving Dreamweaving sessions.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import math

from .feedback_store import FeedbackStore, LessonEffectivenessRecord


@dataclass
class EffectivenessWeights:
    """Configuration for effectiveness scoring weights."""
    success_rate: float = 0.25      # Did generation succeed?
    quality_impact: float = 0.20    # Quality score impact
    retention_impact: float = 0.25  # YouTube retention delta
    engagement_impact: float = 0.15 # YouTube engagement delta
    recency: float = 0.10           # Recent lessons preferred
    consistency: float = 0.05       # Consistent results preferred


class EffectivenessEngine:
    """
    Calculates and ranks lesson effectiveness.

    The effectiveness score is a weighted composite of:
    - Success rate (25%): How often generation succeeds with this lesson
    - Quality impact (20%): Average quality score delta
    - Retention impact (25%): YouTube retention improvement vs baseline
    - Engagement impact (15%): YouTube engagement improvement vs baseline
    - Recency (10%): Recent lessons weighted higher (time decay)
    - Consistency (5%): Lower variance = higher consistency

    Lessons need at least MIN_APPLICATIONS (3) before being ranked,
    to prevent over-fitting to small samples.
    """

    # Minimum applications before scoring kicks in
    MIN_APPLICATIONS = 3

    # Time decay half-life in days
    DECAY_HALF_LIFE_DAYS = 60

    # Baseline metrics for comparison
    DEFAULT_BASELINE = {
        'avg_quality_score': 65.0,
        'avg_retention_pct': 35.0,
        'avg_engagement_rate': 0.03,
    }

    def __init__(
        self,
        feedback_store: FeedbackStore,
        weights: Optional[EffectivenessWeights] = None,
        baseline_metrics: Optional[Dict[str, float]] = None
    ):
        """
        Initialize effectiveness engine.

        Args:
            feedback_store: FeedbackStore instance for data access
            weights: Custom weights (uses defaults if None)
            baseline_metrics: Baseline metrics for comparison
        """
        self.feedback_store = feedback_store
        self.weights = weights or EffectivenessWeights()
        self._baseline_metrics = baseline_metrics or self.DEFAULT_BASELINE.copy()

    @property
    def baseline_metrics(self) -> Dict[str, float]:
        """Get baseline metrics, recalculating if needed."""
        return self._baseline_metrics

    def recalculate_baseline(self):
        """
        Recalculate baseline metrics from actual outcomes.

        Should be called periodically (e.g., weekly) to update baselines
        based on real session performance.
        """
        outcomes = self.feedback_store.get_outcomes_with_youtube_metrics()

        if len(outcomes) < 10:
            # Not enough data, keep defaults
            return

        quality_scores = [o.quality_score for o in outcomes if o.quality_score]
        retention_scores = [o.avg_retention_pct for o in outcomes if o.avg_retention_pct]
        engagement_rates = [o.engagement_rate for o in outcomes if o.engagement_rate]

        if quality_scores:
            self._baseline_metrics['avg_quality_score'] = sum(quality_scores) / len(quality_scores)
        if retention_scores:
            self._baseline_metrics['avg_retention_pct'] = sum(retention_scores) / len(retention_scores)
        if engagement_rates:
            self._baseline_metrics['avg_engagement_rate'] = sum(engagement_rates) / len(engagement_rates)

    def calculate_effectiveness(self, lesson_id: str) -> float:
        """
        Calculate composite effectiveness score for a lesson.

        Args:
            lesson_id: The lesson ID

        Returns:
            Score from 0-100, where 50 is neutral
        """
        record = self.feedback_store.get_lesson_effectiveness(lesson_id)

        if not record or record.times_applied < self.MIN_APPLICATIONS:
            return 50.0  # Default neutral score for untested lessons

        scores = {}

        # 1. Success rate (0-100)
        # 100% success = 100, 0% success = 0
        scores['success_rate'] = record.success_rate * 100

        # 2. Quality impact (normalized to 0-100)
        # Quality centered at 50, ±10 points quality = ±50 score
        quality_delta = record.avg_quality_impact - self._baseline_metrics['avg_quality_score']
        scores['quality_impact'] = 50 + (quality_delta * 5)
        scores['quality_impact'] = max(0, min(100, scores['quality_impact']))

        # 3. Retention impact (normalized to 0-100)
        # ±25% retention = ±50 score
        retention_delta = record.avg_retention_impact
        scores['retention_impact'] = 50 + (retention_delta * 2)
        scores['retention_impact'] = max(0, min(100, scores['retention_impact']))

        # 4. Engagement impact (normalized to 0-100)
        # ±0.05 engagement rate = ±50 score
        engagement_delta = record.avg_engagement_impact
        scores['engagement_impact'] = 50 + (engagement_delta * 1000)
        scores['engagement_impact'] = max(0, min(100, scores['engagement_impact']))

        # 5. Recency (0-100, decays over time)
        if record.last_applied:
            days_since_used = (datetime.now() - record.last_applied).days
            decay_factor = 0.5 ** (days_since_used / self.DECAY_HALF_LIFE_DAYS)
            scores['recency'] = 100 * decay_factor
        else:
            scores['recency'] = 50.0

        # 6. Consistency (0-100, based on variance)
        # Lower variance = higher consistency
        # Variance of 100 = score of 0, variance of 0 = score of 100
        scores['consistency'] = max(0, 100 - (record.quality_variance * 0.5))

        # Weighted composite
        composite = (
            scores['success_rate'] * self.weights.success_rate +
            scores['quality_impact'] * self.weights.quality_impact +
            scores['retention_impact'] * self.weights.retention_impact +
            scores['engagement_impact'] * self.weights.engagement_impact +
            scores['recency'] * self.weights.recency +
            scores['consistency'] * self.weights.consistency
        )

        return min(100, max(0, composite))

    def get_ranked_lessons(
        self,
        lessons: List[Dict[str, Any]],
        category: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get lessons ranked by effectiveness.

        Args:
            lessons: List of lesson dicts from LessonsManager
            category: Optional category filter ('audio', 'content', etc.)
            context: Optional context for relevance boosting
            limit: Maximum number to return

        Returns:
            List of lesson dicts with 'effectiveness_score' added, sorted by score
        """
        ranked = []

        for lesson in lessons:
            # Filter by category if specified
            if category and lesson.get('category') != category:
                continue

            lesson_id = lesson.get('id')
            if not lesson_id:
                continue

            # Calculate base effectiveness score
            score = self.calculate_effectiveness(lesson_id)

            # Apply context boost if provided
            if context and lesson_id:
                context_boost = self._calculate_context_boost(lesson_id, context)
                score = score * (1 + 0.2 * context_boost)  # Max 20% boost

            ranked.append({
                **lesson,
                'effectiveness_score': round(score, 1),
            })

        # Sort by effectiveness (highest first)
        ranked.sort(key=lambda x: x.get('effectiveness_score', 0), reverse=True)

        return ranked[:limit]

    def _calculate_context_boost(
        self,
        lesson_id: str,
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate context relevance boost (0-1).

        Boosts score if this lesson has performed well in similar contexts.
        """
        record = self.feedback_store.get_lesson_effectiveness(lesson_id)
        if not record:
            return 0.0

        context_key = self._context_to_key(context)

        # Check if this context is in best contexts
        if context_key in record.best_contexts:
            return 1.0

        # Check if similar context exists
        for best_ctx in record.best_contexts:
            if self._contexts_similar(context_key, best_ctx):
                return 0.5

        # Check context effectiveness scores
        if context_key in record.context_effectiveness:
            ctx_score = record.context_effectiveness[context_key]
            # Normalize: 75+ = full boost, 50 = no boost, <50 = negative
            return max(0, (ctx_score - 50) / 50)

        return 0.0

    def _context_to_key(self, context: Dict[str, Any]) -> str:
        """Convert context dict to a comparable key."""
        # Use topic or theme as primary key
        topic = context.get('topic', '')
        outcome = context.get('desired_outcome', '')

        # Extract key words
        key_parts = []
        if topic:
            # Simple keyword extraction
            words = topic.lower().split()
            key_words = [w for w in words if len(w) > 4][:3]
            key_parts.extend(key_words)
        if outcome:
            key_parts.append(outcome.lower())

        return '-'.join(sorted(key_parts)) or 'general'

    def _contexts_similar(self, ctx1: str, ctx2: str) -> bool:
        """Check if two context keys are similar."""
        parts1 = set(ctx1.split('-'))
        parts2 = set(ctx2.split('-'))

        # Similar if >50% overlap
        if not parts1 or not parts2:
            return False

        overlap = len(parts1 & parts2)
        total = len(parts1 | parts2)

        return overlap / total > 0.5

    def record_outcome(
        self,
        lesson_id: str,
        outcome_metrics: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Record an outcome and update lesson effectiveness.

        Convenience method that wraps feedback_store.update_effectiveness.

        Args:
            lesson_id: The lesson ID
            outcome_metrics: Dict with 'generation_success', 'quality_score', etc.
            context: Optional context for tracking
        """
        from .feedback_store import OutcomeRecord

        # Create minimal outcome record for effectiveness update
        outcome = OutcomeRecord(
            record_id=f"inline-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            session_name="inline-update",
            created_at=datetime.now(),
            generation_success=outcome_metrics.get('generation_success', False),
            quality_score=outcome_metrics.get('quality_score', 50.0),
        )

        context_key = self._context_to_key(context) if context else None

        self.feedback_store.update_effectiveness(
            lesson_id=lesson_id,
            outcome=outcome,
            context_key=context_key
        )

        # Update stored effectiveness score
        new_score = self.calculate_effectiveness(lesson_id)
        self.feedback_store.set_effectiveness_score(lesson_id, new_score)

    def recalculate_all_rankings(self):
        """
        Recalculate effectiveness scores for all tracked lessons.

        Should be called periodically (e.g., weekly) to ensure
        scores reflect latest data and time decay.
        """
        records = self.feedback_store.get_all_effectiveness_records()

        for record in records:
            score = self.calculate_effectiveness(record.lesson_id)
            self.feedback_store.set_effectiveness_score(record.lesson_id, score)

        # Also recalculate baselines
        self.recalculate_baseline()

    def get_top_lessons(
        self,
        lessons: List[Dict[str, Any]],
        category: Optional[str] = None,
        min_applications: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get the most effective lessons.

        Args:
            lessons: List of all lessons
            category: Optional category filter
            min_applications: Override minimum applications threshold
            limit: Max to return

        Returns:
            Top lessons by effectiveness
        """
        min_apps = min_applications if min_applications is not None else self.MIN_APPLICATIONS

        ranked = self.get_ranked_lessons(
            lessons=lessons,
            category=category,
            limit=limit * 2  # Get more to filter
        )

        # Filter by application count
        filtered = []
        for lesson in ranked:
            record = self.feedback_store.get_lesson_effectiveness(lesson.get('id'))
            if record and record.times_applied >= min_apps:
                filtered.append(lesson)

        return filtered[:limit]

    def get_underperforming_lessons(
        self,
        lessons: List[Dict[str, Any]],
        threshold: float = 40.0,
        min_applications: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get lessons that consistently underperform.

        These are candidates for archiving or revision.

        Args:
            lessons: List of all lessons
            threshold: Score below which lesson is considered underperforming
            min_applications: Minimum applications to be evaluated

        Returns:
            List of underperforming lessons
        """
        underperformers = []

        for lesson in lessons:
            lesson_id = lesson.get('id')
            if not lesson_id:
                continue

            record = self.feedback_store.get_lesson_effectiveness(lesson_id)
            if not record or record.times_applied < min_applications:
                continue

            score = self.calculate_effectiveness(lesson_id)
            if score < threshold:
                underperformers.append({
                    **lesson,
                    'effectiveness_score': round(score, 1),
                    'times_applied': record.times_applied,
                    'success_rate': round(record.success_rate * 100, 1),
                })

        # Sort by worst first
        underperformers.sort(key=lambda x: x.get('effectiveness_score', 100))

        return underperformers

    def suggest_lesson_improvements(
        self,
        lesson: Dict[str, Any]
    ) -> List[str]:
        """
        Suggest improvements for an underperforming lesson.

        Args:
            lesson: Lesson dict with effectiveness data

        Returns:
            List of improvement suggestions
        """
        suggestions = []
        lesson_id = lesson.get('id')

        if not lesson_id:
            return ["Cannot analyze lesson without ID"]

        record = self.feedback_store.get_lesson_effectiveness(lesson_id)
        if not record:
            return ["No effectiveness data available"]

        # Analyze weak points
        if record.success_rate < 0.7:
            suggestions.append(
                f"Low success rate ({record.success_rate*100:.0f}%). "
                "Consider making the lesson more specific or actionable."
            )

        if record.quality_variance > 200:
            suggestions.append(
                f"High variance ({record.quality_variance:.0f}). "
                "Results are inconsistent. Consider narrowing the lesson's scope."
            )

        if record.worst_contexts:
            suggestions.append(
                f"Performs poorly in contexts: {', '.join(record.worst_contexts[:3])}. "
                "Consider adding context-specific guidance or splitting into multiple lessons."
            )

        if record.avg_quality_impact < 50:
            suggestions.append(
                f"Below average quality impact ({record.avg_quality_impact:.0f}). "
                "Review if the lesson's action is effective."
            )

        if not suggestions:
            suggestions.append("No specific issues identified. Consider archiving if consistently low scoring.")

        return suggestions


# Factory function
def create_effectiveness_engine(project_root: Path) -> EffectivenessEngine:
    """
    Create an effectiveness engine with standard configuration.

    Args:
        project_root: Path to project root

    Returns:
        Configured EffectivenessEngine instance
    """
    feedback_path = project_root / 'knowledge' / 'feedback'
    feedback_store = FeedbackStore(feedback_path)
    return EffectivenessEngine(feedback_store)
