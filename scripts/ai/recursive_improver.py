"""
Recursive Improver - Main orchestrator for self-improving agents.

This module provides the central orchestrator that coordinates three
recursive agent types:
1. Dreamweaver Recursive Agent - Session generation improvement
2. RAG Recursive Agent - Knowledge retrieval optimization
3. Website Recursive Agent - Content auto-improvement

The Recursive Improver is the "killer feature" that enables the
Dreamweaving system to continuously evolve and improve based on
real-world performance data.

Usage:
    from scripts.ai.recursive_improver import RecursiveImprover

    improver = RecursiveImprover(project_root)

    # Get ranked lessons for session generation
    lessons = improver.get_ranked_lessons(topic="healing journey", duration=25)

    # Record outcome after generation
    improver.record_session_outcome(session_name, applied_lessons, metrics)

    # Run improvement cycle
    improver.run_improvement_cycle()
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml

from .learning.feedback_store import FeedbackStore, OutcomeRecord, generate_record_id
from .learning.effectiveness_engine import EffectivenessEngine
from .learning.lessons_manager import LessonsManager


@dataclass
class ImprovementCycle:
    """Tracks a single improvement cycle."""

    cycle_id: str
    agent_type: str  # 'dreamweaver', 'rag', 'website'
    started_at: datetime
    completed_at: Optional[datetime] = None

    # Input context
    inputs: Dict[str, Any] = field(default_factory=dict)

    # Results
    outputs: Dict[str, Any] = field(default_factory=dict)
    lessons_applied: List[str] = field(default_factory=list)
    lessons_promoted: List[str] = field(default_factory=list)
    lessons_demoted: List[str] = field(default_factory=list)
    lessons_created: List[str] = field(default_factory=list)
    lessons_archived: List[str] = field(default_factory=list)

    # Metrics
    sessions_analyzed: int = 0
    outcomes_processed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            'cycle_id': self.cycle_id,
            'agent_type': self.agent_type,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'lessons_applied': self.lessons_applied,
            'lessons_promoted': self.lessons_promoted,
            'lessons_demoted': self.lessons_demoted,
            'lessons_created': self.lessons_created,
            'lessons_archived': self.lessons_archived,
            'sessions_analyzed': self.sessions_analyzed,
            'outcomes_processed': self.outcomes_processed,
        }
        return data


class RecursiveImprover:
    """
    Main orchestrator for recursive self-improvement.

    Coordinates:
    - Lesson retrieval and ranking
    - Outcome recording
    - Improvement cycles (daily/weekly)
    - Lesson promotion/demotion
    - Knowledge base optimization
    """

    # Thresholds for lesson management
    PROMOTION_THRESHOLD = 70.0   # Score above which to promote confidence
    DEMOTION_THRESHOLD = 40.0    # Score below which to demote confidence
    ARCHIVE_THRESHOLD = 30.0     # Score below which to archive
    MIN_APPLICATIONS_FOR_ACTION = 5  # Minimum uses before promotion/demotion

    def __init__(self, project_root: Path):
        """
        Initialize recursive improver.

        Args:
            project_root: Path to project root directory
        """
        self.project_root = Path(project_root)

        # Initialize components
        self.feedback_store = FeedbackStore(
            self.project_root / 'knowledge' / 'feedback'
        )
        self.effectiveness_engine = EffectivenessEngine(self.feedback_store)
        self.lessons_manager = LessonsManager(
            self.project_root / 'knowledge'
        )

        # Track current improvement cycle
        self.current_cycle: Optional[ImprovementCycle] = None

        # Cycle history file
        self.cycles_file = self.project_root / 'knowledge' / 'feedback' / 'improvement_cycles.yaml'

    # -------------------------------------------------------------------------
    # Lesson Retrieval (for session generation)
    # -------------------------------------------------------------------------

    def get_ranked_lessons(
        self,
        topic: Optional[str] = None,
        duration: Optional[int] = None,
        desired_outcome: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get lessons ranked by effectiveness for a given context.

        This is the primary method called during session generation
        to retrieve lessons that should be applied.

        Args:
            topic: Session topic (e.g., "healing journey in forest")
            duration: Target duration in minutes
            desired_outcome: Desired outcome (e.g., "healing", "confidence")
            category: Filter by category (e.g., "audio", "content")
            limit: Maximum number of lessons to return

        Returns:
            List of lesson dicts with 'effectiveness_score' added
        """
        # Build context for relevance matching
        context = {
            'topic': topic or '',
            'duration': duration or 25,
            'desired_outcome': desired_outcome or '',
        }

        # Get all lessons
        all_lessons = self.lessons_manager.get_lessons()

        # Get ranked lessons from effectiveness engine
        ranked = self.effectiveness_engine.get_ranked_lessons(
            lessons=all_lessons,
            category=category,
            context=context,
            limit=limit * 2  # Get more to filter
        )

        # Filter by confidence (only apply high/medium confidence)
        filtered = [
            l for l in ranked
            if l.get('confidence', 'medium') in ['high', 'medium']
        ]

        return filtered[:limit]

    def get_lessons_context_string(
        self,
        lessons: List[Dict[str, Any]]
    ) -> str:
        """
        Build a context string from lessons for prompt injection.

        Args:
            lessons: List of lesson dicts to format

        Returns:
            Formatted string suitable for including in prompts
        """
        if not lessons:
            return "(No specific lessons to apply)"

        lines = []
        lines.append("## LESSONS FROM PAST SESSIONS")
        lines.append("Apply these proven insights from previous successful sessions:")
        lines.append("")

        for i, lesson in enumerate(lessons, 1):
            category = lesson.get('category', 'general').upper()
            finding = lesson.get('finding', lesson.get('lesson', ''))
            action = lesson.get('action', '')
            score = lesson.get('effectiveness_score', 50)

            lines.append(f"{i}. [{category}] {finding}")
            if action:
                lines.append(f"   ACTION: {action}")
            lines.append(f"   (Effectiveness: {score:.0f}/100)")
            lines.append("")

        return '\n'.join(lines)

    # -------------------------------------------------------------------------
    # Outcome Recording (after session generation)
    # -------------------------------------------------------------------------

    def record_session_outcome(
        self,
        session_name: str,
        applied_lessons: List[str],
        metrics: Dict[str, Any],
        youtube_video_id: Optional[str] = None
    ) -> str:
        """
        Record the outcome of a session generation.

        Should be called after each session is generated to track
        which lessons were applied and immediate metrics.

        Args:
            session_name: Name of the generated session
            applied_lessons: List of lesson IDs that were applied
            metrics: Dict with generation metrics:
                - generation_success: bool
                - quality_score: float (0-100)
                - audio_duration_actual: float (seconds)
                - duration_deviation_pct: float
            youtube_video_id: Optional video ID for later YouTube metrics

        Returns:
            record_id of the outcome record
        """
        # Create outcome record
        record = OutcomeRecord(
            record_id=generate_record_id(session_name),
            session_name=session_name,
            created_at=datetime.now(),
            lesson_ids=applied_lessons,
            topic=metrics.get('topic', ''),
            duration_target=metrics.get('duration_target', 25),
            mode=metrics.get('mode', 'standard'),
            desired_outcome=metrics.get('desired_outcome', ''),
            generation_success=metrics.get('generation_success', False),
            audio_duration_actual=metrics.get('audio_duration_actual', 0.0),
            duration_deviation_pct=metrics.get('duration_deviation_pct', 0.0),
            quality_score=metrics.get('quality_score', 50.0),
            youtube_video_id=youtube_video_id,
            youtube_pending=youtube_video_id is not None,
        )

        # Store outcome
        record_id = self.feedback_store.record_outcome(record)

        # Update effectiveness for each applied lesson
        context_key = self._build_context_key(metrics)
        for lesson_id in applied_lessons:
            self.feedback_store.update_effectiveness(
                lesson_id=lesson_id,
                outcome=record,
                context_key=context_key
            )

            # Mark lesson as applied in lessons_learned.yaml
            self.lessons_manager.mark_lesson_applied(
                lesson_id=lesson_id,
                session_name=session_name
            )

        # Schedule YouTube metrics check if video ID provided
        if youtube_video_id:
            self.feedback_store.schedule_outcome_check(
                outcome=record,
                youtube_video_id=youtube_video_id,
                days_to_wait=7
            )

        return record_id

    def _build_context_key(self, metrics: Dict[str, Any]) -> str:
        """Build context key from metrics for effectiveness tracking."""
        parts = []

        topic = metrics.get('topic', '')
        if topic:
            # Extract key words
            words = topic.lower().split()
            key_words = [w for w in words if len(w) > 4][:3]
            parts.extend(key_words)

        outcome = metrics.get('desired_outcome', '')
        if outcome:
            parts.append(outcome.lower())

        return '-'.join(sorted(parts)) or 'general'

    # -------------------------------------------------------------------------
    # Improvement Cycles
    # -------------------------------------------------------------------------

    def run_improvement_cycle(
        self,
        agent_type: str = 'dreamweaver',
        days_lookback: int = 7
    ) -> ImprovementCycle:
        """
        Run a full improvement cycle.

        This is the core "recursive" operation that:
        1. Collects recent session outcomes
        2. Analyzes which lessons helped/hurt
        3. Promotes/demotes lesson confidence
        4. Detects new patterns to create lessons
        5. Archives ineffective lessons
        6. Updates best practices

        Args:
            agent_type: Which agent type ('dreamweaver', 'rag', 'website')
            days_lookback: Days of history to analyze

        Returns:
            ImprovementCycle with results
        """
        cycle = ImprovementCycle(
            cycle_id=f"{agent_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            agent_type=agent_type,
            started_at=datetime.now(),
            inputs={'days_lookback': days_lookback},
        )

        self.current_cycle = cycle

        try:
            # 1. Collect recent outcomes
            outcomes = self.feedback_store.get_recent_outcomes(days=days_lookback)
            cycle.sessions_analyzed = len(outcomes)

            # 2. Recalculate all effectiveness scores
            self.effectiveness_engine.recalculate_all_rankings()

            # 3. Process pending YouTube checks
            pending = self.feedback_store.get_pending_checks(ready_only=True)
            cycle.outcomes_processed = len(pending)
            # Note: Actual YouTube fetching happens in scheduler

            # 4. Promote/demote lessons based on effectiveness
            self._adjust_lesson_confidence(cycle)

            # 5. Detect patterns and create new lessons
            self._detect_and_create_lessons(outcomes, cycle)

            # 6. Archive ineffective lessons
            self._archive_ineffective_lessons(cycle)

            # 7. Update best practices
            self._update_best_practices()

            cycle.completed_at = datetime.now()
            cycle.outputs['status'] = 'success'

        except Exception as e:
            cycle.completed_at = datetime.now()
            cycle.outputs['status'] = 'error'
            cycle.outputs['error'] = str(e)

        # Save cycle history
        self._save_cycle(cycle)

        return cycle

    def _adjust_lesson_confidence(self, cycle: ImprovementCycle):
        """Promote or demote lesson confidence based on effectiveness."""
        all_lessons = self.lessons_manager.get_lessons()

        for lesson in all_lessons:
            lesson_id = lesson.get('id')
            if not lesson_id:
                continue

            record = self.feedback_store.get_lesson_effectiveness(lesson_id)
            if not record or record.times_applied < self.MIN_APPLICATIONS_FOR_ACTION:
                continue

            score = self.effectiveness_engine.calculate_effectiveness(lesson_id)
            current_confidence = lesson.get('confidence', 'medium')

            # Promotion
            if score >= self.PROMOTION_THRESHOLD and current_confidence != 'high':
                self.lessons_manager.update_lesson_confidence(lesson_id, 'high')
                cycle.lessons_promoted.append(lesson_id)

            # Demotion
            elif score <= self.DEMOTION_THRESHOLD and current_confidence == 'high':
                self.lessons_manager.update_lesson_confidence(lesson_id, 'medium')
                cycle.lessons_demoted.append(lesson_id)

            elif score <= self.DEMOTION_THRESHOLD and current_confidence == 'medium':
                self.lessons_manager.update_lesson_confidence(lesson_id, 'low')
                cycle.lessons_demoted.append(lesson_id)

    def _detect_and_create_lessons(
        self,
        outcomes: List[OutcomeRecord],
        cycle: ImprovementCycle
    ):
        """Detect patterns in successful sessions and create new lessons."""
        # Group high-performing sessions
        high_performers = [o for o in outcomes if o.quality_score >= 80]

        if len(high_performers) < 3:
            return  # Not enough data

        # Look for common attributes
        # (This is a simplified version - could be expanded with ML)

        # Check for topic patterns
        topics = [o.topic.lower() for o in high_performers if o.topic]
        common_words = self._find_common_words(topics)

        if common_words:
            # Create lesson suggestion (not auto-created, logged for review)
            suggestion = {
                'pattern': 'topic_correlation',
                'common_words': common_words,
                'sample_size': len(high_performers),
                'suggestion': f"Topics containing '{common_words[0]}' tend to perform well"
            }
            cycle.outputs['lesson_suggestions'] = cycle.outputs.get('lesson_suggestions', [])
            cycle.outputs['lesson_suggestions'].append(suggestion)

    def _find_common_words(self, texts: List[str], min_occurrences: int = 3) -> List[str]:
        """Find commonly occurring words across texts."""
        word_counts: Dict[str, int] = {}
        for text in texts:
            words = set(text.split())
            for word in words:
                if len(word) > 4:  # Skip short words
                    word_counts[word] = word_counts.get(word, 0) + 1

        common = [
            word for word, count in word_counts.items()
            if count >= min_occurrences
        ]

        return sorted(common, key=lambda w: word_counts[w], reverse=True)[:5]

    def _archive_ineffective_lessons(self, cycle: ImprovementCycle):
        """Archive lessons that consistently underperform."""
        all_lessons = self.lessons_manager.get_lessons()

        for lesson in all_lessons:
            lesson_id = lesson.get('id')
            if not lesson_id:
                continue

            record = self.feedback_store.get_lesson_effectiveness(lesson_id)
            if not record or record.times_applied < self.MIN_APPLICATIONS_FOR_ACTION * 2:
                continue  # Need more data before archiving

            score = self.effectiveness_engine.calculate_effectiveness(lesson_id)

            if score <= self.ARCHIVE_THRESHOLD:
                self.lessons_manager.archive_lesson(lesson_id)
                cycle.lessons_archived.append(lesson_id)

    def _update_best_practices(self):
        """Regenerate best_practices.md from top lessons."""
        best_practices_path = self.project_root / 'knowledge' / 'best_practices.md'

        all_lessons = self.lessons_manager.get_lessons()
        top_lessons = self.effectiveness_engine.get_top_lessons(
            lessons=all_lessons,
            limit=20
        )

        if not top_lessons:
            return

        # Group by category
        by_category: Dict[str, List[Dict]] = {}
        for lesson in top_lessons:
            category = lesson.get('category', 'general')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(lesson)

        # Generate markdown
        lines = [
            "# Best Practices",
            "",
            "> Auto-generated from top-performing lessons.",
            f"> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
        ]

        for category, lessons in sorted(by_category.items()):
            lines.append(f"## {category.title()}")
            lines.append("")
            for lesson in lessons:
                finding = lesson.get('finding', lesson.get('lesson', ''))
                action = lesson.get('action', '')
                score = lesson.get('effectiveness_score', 50)

                lines.append(f"- **{finding}**")
                if action:
                    lines.append(f"  - {action}")
                lines.append(f"  - _(Effectiveness: {score:.0f}/100)_")
                lines.append("")

        # Append manual sections if they exist
        if best_practices_path.exists():
            with open(best_practices_path, 'r') as f:
                content = f.read()
                # Look for manual sections marked with <!-- MANUAL -->
                if '<!-- MANUAL -->' in content:
                    manual_section = content.split('<!-- MANUAL -->')[1]
                    lines.append("<!-- MANUAL -->")
                    lines.append(manual_section)

        with open(best_practices_path, 'w') as f:
            f.write('\n'.join(lines))

    def _save_cycle(self, cycle: ImprovementCycle):
        """Save cycle to history file."""
        if self.cycles_file.exists():
            with open(self.cycles_file, 'r') as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        cycles = data.get('cycles', [])
        cycles.append(cycle.to_dict())

        # Keep only last 100 cycles
        cycles = cycles[-100:]

        data['cycles'] = cycles
        data['last_updated'] = datetime.now().isoformat()

        with open(self.cycles_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    # -------------------------------------------------------------------------
    # Statistics and Reporting
    # -------------------------------------------------------------------------

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the recursive improvement system."""
        feedback_stats = self.feedback_store.get_statistics()
        all_lessons = self.lessons_manager.get_lessons()

        # Count lessons by confidence
        by_confidence = {'high': 0, 'medium': 0, 'low': 0}
        for lesson in all_lessons:
            conf = lesson.get('confidence', 'medium')
            by_confidence[conf] = by_confidence.get(conf, 0) + 1

        # Get cycle history
        cycles = []
        if self.cycles_file.exists():
            with open(self.cycles_file, 'r') as f:
                data = yaml.safe_load(f) or {}
                cycles = data.get('cycles', [])

        return {
            **feedback_stats,
            'total_lessons': len(all_lessons),
            'lessons_by_confidence': by_confidence,
            'improvement_cycles_run': len(cycles),
            'last_cycle': cycles[-1] if cycles else None,
        }

    def get_improvement_report(self, days: int = 30) -> str:
        """Generate a human-readable improvement report."""
        stats = self.get_statistics()

        lines = [
            "# Recursive Improvement Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## Overview",
            f"- Total sessions tracked: {stats['total_outcomes']}",
            f"- Generation success rate: {stats['success_rate']*100:.1f}%",
            f"- Sessions with YouTube metrics: {stats['outcomes_with_youtube']}",
            "",
            "## Lessons",
            f"- Total lessons: {stats['total_lessons']}",
            f"- High confidence: {stats['lessons_by_confidence']['high']}",
            f"- Medium confidence: {stats['lessons_by_confidence']['medium']}",
            f"- Low confidence: {stats['lessons_by_confidence']['low']}",
            f"- Average effectiveness: {stats['average_effectiveness']:.1f}/100",
            "",
            "## Improvement Cycles",
            f"- Cycles run: {stats['improvement_cycles_run']}",
        ]

        if stats.get('last_cycle'):
            last = stats['last_cycle']
            lines.extend([
                f"- Last cycle: {last.get('cycle_id', 'unknown')}",
                f"- Sessions analyzed: {last.get('sessions_analyzed', 0)}",
                f"- Lessons promoted: {len(last.get('lessons_promoted', []))}",
                f"- Lessons demoted: {len(last.get('lessons_demoted', []))}",
                f"- Lessons archived: {len(last.get('lessons_archived', []))}",
            ])

        return '\n'.join(lines)


# Factory function
def create_recursive_improver(project_root: Optional[Path] = None) -> RecursiveImprover:
    """
    Create a RecursiveImprover with default configuration.

    Args:
        project_root: Path to project root (uses current if None)

    Returns:
        Configured RecursiveImprover instance
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    return RecursiveImprover(project_root)
