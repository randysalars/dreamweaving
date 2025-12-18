"""
Feedback Store - Persistent storage for outcome records and lesson effectiveness.

This module provides data models and storage for tracking:
- Session outcome records (immediate + delayed metrics)
- Lesson effectiveness scores
- Pending outcome checks (scheduled for YouTube metrics)

Part of the Recursive Improver system for self-improving Dreamweaving sessions.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import hashlib


@dataclass
class OutcomeRecord:
    """Records the outcome of a session generation with applied lessons."""

    record_id: str
    session_name: str
    created_at: datetime
    lesson_ids: List[str] = field(default_factory=list)

    # Input context
    topic: str = ""
    duration_target: int = 25
    mode: str = "standard"
    desired_outcome: str = ""

    # Immediate outcomes (measured at generation time)
    generation_success: bool = False
    audio_duration_actual: float = 0.0
    duration_deviation_pct: float = 0.0
    quality_score: float = 50.0  # 0-100 from quality_scorer.py

    # YouTube metrics (measured later, 7+ days)
    youtube_video_id: Optional[str] = None
    measured_at: Optional[datetime] = None
    views_7_day: Optional[int] = None
    avg_retention_pct: Optional[float] = None
    engagement_rate: Optional[float] = None
    likes: Optional[int] = None
    comments_count: Optional[int] = None
    comments_sentiment: Optional[float] = None  # -1 to 1

    # Status flags
    metrics_complete: bool = False
    youtube_pending: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML storage."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        if data['measured_at']:
            data['measured_at'] = data['measured_at'].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OutcomeRecord':
        """Create from dictionary."""
        # Convert ISO strings back to datetime
        if data.get('created_at') and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('measured_at') and isinstance(data['measured_at'], str):
            data['measured_at'] = datetime.fromisoformat(data['measured_at'])
        return cls(**data)


@dataclass
class LessonEffectivenessRecord:
    """Tracks effectiveness of a single lesson over time."""

    lesson_id: str

    # Application tracking
    times_applied: int = 0
    times_successful: int = 0  # generation succeeded

    # Aggregate metrics (running averages)
    success_rate: float = 0.0  # times_successful / times_applied
    avg_quality_impact: float = 50.0  # Average quality score when applied
    avg_retention_impact: float = 0.0  # Average retention delta vs baseline
    avg_engagement_impact: float = 0.0  # Average engagement delta vs baseline

    # Variance tracking (for consistency score)
    quality_variance: float = 0.0
    _quality_m2: float = 0.0  # For Welford's algorithm

    # Time tracking
    first_applied: Optional[datetime] = None
    last_applied: Optional[datetime] = None
    last_successful: Optional[datetime] = None

    # Context relevance
    best_contexts: List[str] = field(default_factory=list)  # Topics where effective
    worst_contexts: List[str] = field(default_factory=list)  # Topics where ineffective
    context_effectiveness: Dict[str, float] = field(default_factory=dict)

    # Computed score (set by EffectivenessEngine)
    effectiveness_score: float = 50.0  # 0-100, weighted composite

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML storage."""
        data = asdict(self)
        # Convert datetime objects
        for key in ['first_applied', 'last_applied', 'last_successful']:
            if data.get(key) and isinstance(data[key], datetime):
                data[key] = data[key].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LessonEffectivenessRecord':
        """Create from dictionary."""
        for key in ['first_applied', 'last_applied', 'last_successful']:
            if data.get(key) and isinstance(data[key], str):
                data[key] = datetime.fromisoformat(data[key])
        return cls(**data)


@dataclass
class PendingOutcomeCheck:
    """Tracks sessions awaiting outcome measurement."""

    record_id: str
    session_name: str
    youtube_video_id: Optional[str]
    scheduled_at: datetime
    check_type: str = "youtube"  # 'youtube' or 'immediate'
    days_to_wait: int = 7
    attempts: int = 0
    max_attempts: int = 3

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if data['scheduled_at']:
            data['scheduled_at'] = data['scheduled_at'].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PendingOutcomeCheck':
        if data.get('scheduled_at') and isinstance(data['scheduled_at'], str):
            data['scheduled_at'] = datetime.fromisoformat(data['scheduled_at'])
        return cls(**data)


class FeedbackStore:
    """
    Persistent storage for feedback data.

    Manages:
    - outcome_records.yaml: Session outcomes
    - lesson_effectiveness.yaml: Lesson effectiveness scores
    - pending_outcome_checks.yaml: Scheduled checks for YouTube metrics
    """

    def __init__(self, store_path: Path):
        """
        Initialize feedback store.

        Args:
            store_path: Path to knowledge/feedback/ directory
        """
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)

        self.outcomes_file = self.store_path / 'outcome_records.yaml'
        self.effectiveness_file = self.store_path / 'lesson_effectiveness.yaml'
        self.pending_checks_file = self.store_path / 'pending_outcome_checks.yaml'

        # Initialize files if they don't exist
        self._initialize_files()

    def _initialize_files(self):
        """Create empty files if they don't exist."""
        for file_path in [self.outcomes_file, self.effectiveness_file, self.pending_checks_file]:
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    yaml.dump({'records': []}, f)

    def _load_yaml(self, file_path: Path) -> Dict:
        """Load YAML file safely."""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f) or {}
                return data
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
            return {'records': []}

    def _save_yaml(self, file_path: Path, data: Dict):
        """Save YAML file with backup."""
        # Create backup
        if file_path.exists():
            backup_path = file_path.with_suffix('.yaml.bak')
            file_path.rename(backup_path)

        try:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            # Restore from backup on failure
            if backup_path.exists():
                backup_path.rename(file_path)
            raise e

    # -------------------------------------------------------------------------
    # Outcome Records
    # -------------------------------------------------------------------------

    def record_outcome(self, record: OutcomeRecord) -> str:
        """
        Store an outcome record.

        Returns:
            record_id of the stored record
        """
        data = self._load_yaml(self.outcomes_file)
        records = data.get('records', [])

        # Check for existing record with same ID
        existing_idx = next(
            (i for i, r in enumerate(records) if r.get('record_id') == record.record_id),
            None
        )

        if existing_idx is not None:
            records[existing_idx] = record.to_dict()
        else:
            records.append(record.to_dict())

        data['records'] = records
        data['last_updated'] = datetime.now().isoformat()
        self._save_yaml(self.outcomes_file, data)

        return record.record_id

    def get_outcome(self, record_id: str) -> Optional[OutcomeRecord]:
        """Get an outcome record by ID."""
        data = self._load_yaml(self.outcomes_file)
        for record_data in data.get('records', []):
            if record_data.get('record_id') == record_id:
                return OutcomeRecord.from_dict(record_data)
        return None

    def get_outcomes_for_session(self, session_name: str) -> List[OutcomeRecord]:
        """Get all outcome records for a session."""
        data = self._load_yaml(self.outcomes_file)
        return [
            OutcomeRecord.from_dict(r)
            for r in data.get('records', [])
            if r.get('session_name') == session_name
        ]

    def get_session_outcome(self, session_name: str) -> Optional[OutcomeRecord]:
        """
        Get the most recent outcome record for a session by name.

        For scheduler compatibility - returns single record or None.
        """
        outcomes = self.get_outcomes_for_session(session_name)
        if not outcomes:
            return None
        # Return most recent
        return max(outcomes, key=lambda o: o.created_at)

    def update_outcome(self, outcome: OutcomeRecord) -> bool:
        """
        Update an existing outcome record.

        Args:
            outcome: The OutcomeRecord with updated fields

        Returns:
            True if updated, False if not found
        """
        data = self._load_yaml(self.outcomes_file)
        records = data.get('records', [])

        for i, record_data in enumerate(records):
            if record_data.get('record_id') == outcome.record_id:
                records[i] = outcome.to_dict()
                data['records'] = records
                data['last_updated'] = datetime.now().isoformat()
                self._save_yaml(self.outcomes_file, data)
                return True

        return False

    def get_recent_outcomes(self, days: int = 30) -> List[OutcomeRecord]:
        """Get outcomes from the last N days."""
        cutoff = datetime.now().timestamp() - (days * 86400)
        data = self._load_yaml(self.outcomes_file)
        results = []
        for record_data in data.get('records', []):
            created = record_data.get('created_at')
            if created:
                if isinstance(created, str):
                    created = datetime.fromisoformat(created)
                if created.timestamp() >= cutoff:
                    results.append(OutcomeRecord.from_dict(record_data))
        return results

    def get_outcomes_with_youtube_metrics(self) -> List[OutcomeRecord]:
        """Get outcomes that have YouTube metrics filled in."""
        data = self._load_yaml(self.outcomes_file)
        return [
            OutcomeRecord.from_dict(r)
            for r in data.get('records', [])
            if r.get('metrics_complete', False)
        ]

    def update_outcome_youtube_metrics(
        self,
        record_id: str,
        youtube_metrics: Dict[str, Any]
    ) -> bool:
        """
        Update an outcome record with YouTube metrics.

        Args:
            record_id: The outcome record ID
            youtube_metrics: Dict with views_7_day, avg_retention_pct, etc.

        Returns:
            True if updated, False if record not found
        """
        data = self._load_yaml(self.outcomes_file)
        records = data.get('records', [])

        for i, record_data in enumerate(records):
            if record_data.get('record_id') == record_id:
                record_data.update({
                    'measured_at': datetime.now().isoformat(),
                    'views_7_day': youtube_metrics.get('views'),
                    'avg_retention_pct': youtube_metrics.get('retention_pct'),
                    'engagement_rate': youtube_metrics.get('engagement_rate'),
                    'likes': youtube_metrics.get('likes'),
                    'comments_count': youtube_metrics.get('comments'),
                    'comments_sentiment': youtube_metrics.get('sentiment'),
                    'metrics_complete': True,
                    'youtube_pending': False,
                })
                records[i] = record_data
                data['records'] = records
                data['last_updated'] = datetime.now().isoformat()
                self._save_yaml(self.outcomes_file, data)
                return True

        return False

    # -------------------------------------------------------------------------
    # Lesson Effectiveness
    # -------------------------------------------------------------------------

    def get_lesson_effectiveness(self, lesson_id: str) -> Optional[LessonEffectivenessRecord]:
        """Get effectiveness record for a lesson."""
        data = self._load_yaml(self.effectiveness_file)
        for record_data in data.get('records', []):
            if record_data.get('lesson_id') == lesson_id:
                return LessonEffectivenessRecord.from_dict(record_data)
        return None

    def get_all_effectiveness_records(self) -> List[LessonEffectivenessRecord]:
        """Get all lesson effectiveness records."""
        data = self._load_yaml(self.effectiveness_file)
        return [
            LessonEffectivenessRecord.from_dict(r)
            for r in data.get('records', [])
        ]

    def update_effectiveness(
        self,
        lesson_id: str,
        outcome: OutcomeRecord,
        context_key: Optional[str] = None
    ) -> LessonEffectivenessRecord:
        """
        Update effectiveness record based on a new outcome.

        Uses Welford's online algorithm for running variance calculation.

        Args:
            lesson_id: The lesson ID
            outcome: The outcome record from the session
            context_key: Optional topic/theme key for context tracking

        Returns:
            Updated effectiveness record
        """
        data = self._load_yaml(self.effectiveness_file)
        records = data.get('records', [])

        # Find or create record
        record_idx = next(
            (i for i, r in enumerate(records) if r.get('lesson_id') == lesson_id),
            None
        )

        if record_idx is not None:
            record = LessonEffectivenessRecord.from_dict(records[record_idx])
        else:
            record = LessonEffectivenessRecord(lesson_id=lesson_id)
            record.first_applied = datetime.now()

        # Update application count
        n = record.times_applied
        record.times_applied = n + 1
        record.last_applied = datetime.now()

        # Update success tracking
        if outcome.generation_success:
            record.times_successful += 1
            record.last_successful = datetime.now()

        record.success_rate = record.times_successful / record.times_applied

        # Update quality impact using exponential moving average
        alpha = 0.3  # Weight for new observation
        quality = outcome.quality_score

        if n == 0:
            record.avg_quality_impact = quality
        else:
            record.avg_quality_impact = (
                (1 - alpha) * record.avg_quality_impact +
                alpha * quality
            )

        # Update variance using Welford's algorithm
        delta = quality - record.avg_quality_impact
        record._quality_m2 += delta * (quality - record.avg_quality_impact)
        if record.times_applied > 1:
            record.quality_variance = record._quality_m2 / (record.times_applied - 1)

        # Update context effectiveness
        if context_key:
            current_score = record.context_effectiveness.get(context_key, 50.0)
            record.context_effectiveness[context_key] = (
                (1 - alpha) * current_score + alpha * quality
            )

            # Track best/worst contexts
            if quality >= 75 and context_key not in record.best_contexts:
                record.best_contexts.append(context_key)
                # Keep only top 10
                record.best_contexts = record.best_contexts[-10:]
            elif quality < 50 and context_key not in record.worst_contexts:
                record.worst_contexts.append(context_key)
                record.worst_contexts = record.worst_contexts[-10:]

        # Save
        if record_idx is not None:
            records[record_idx] = record.to_dict()
        else:
            records.append(record.to_dict())

        data['records'] = records
        data['last_updated'] = datetime.now().isoformat()
        self._save_yaml(self.effectiveness_file, data)

        return record

    def update_effectiveness_youtube(
        self,
        lesson_id: str,
        retention_pct: float,
        engagement_rate: float,
        baseline_retention: float = 35.0,
        baseline_engagement: float = 0.03
    ):
        """
        Update effectiveness with YouTube metrics.

        Called after YouTube analytics are collected.
        """
        record = self.get_lesson_effectiveness(lesson_id)
        if not record:
            return

        alpha = 0.3

        # Update retention impact (delta from baseline)
        retention_delta = retention_pct - baseline_retention
        record.avg_retention_impact = (
            (1 - alpha) * record.avg_retention_impact +
            alpha * retention_delta
        )

        # Update engagement impact (delta from baseline)
        engagement_delta = engagement_rate - baseline_engagement
        record.avg_engagement_impact = (
            (1 - alpha) * record.avg_engagement_impact +
            alpha * engagement_delta
        )

        # Save
        data = self._load_yaml(self.effectiveness_file)
        records = data.get('records', [])
        for i, r in enumerate(records):
            if r.get('lesson_id') == lesson_id:
                records[i] = record.to_dict()
                break
        data['records'] = records
        data['last_updated'] = datetime.now().isoformat()
        self._save_yaml(self.effectiveness_file, data)

    def set_effectiveness_score(self, lesson_id: str, score: float):
        """Set the computed effectiveness score for a lesson."""
        data = self._load_yaml(self.effectiveness_file)
        records = data.get('records', [])

        for i, r in enumerate(records):
            if r.get('lesson_id') == lesson_id:
                r['effectiveness_score'] = score
                records[i] = r
                break

        data['records'] = records
        self._save_yaml(self.effectiveness_file, data)

    def save_effectiveness_record(self, record: LessonEffectivenessRecord) -> bool:
        """
        Save or update a lesson effectiveness record.

        For scheduler compatibility - saves complete record object.

        Args:
            record: The LessonEffectivenessRecord to save

        Returns:
            True if saved successfully
        """
        data = self._load_yaml(self.effectiveness_file)
        records = data.get('records', [])

        # Find existing record
        existing_idx = next(
            (i for i, r in enumerate(records) if r.get('lesson_id') == record.lesson_id),
            None
        )

        if existing_idx is not None:
            records[existing_idx] = record.to_dict()
        else:
            records.append(record.to_dict())

        data['records'] = records
        data['last_updated'] = datetime.now().isoformat()
        self._save_yaml(self.effectiveness_file, data)
        return True

    # -------------------------------------------------------------------------
    # Pending Outcome Checks
    # -------------------------------------------------------------------------

    def schedule_outcome_check(
        self,
        outcome: OutcomeRecord,
        youtube_video_id: Optional[str] = None,
        days_to_wait: int = 7
    ):
        """
        Schedule a future outcome measurement.

        Typically scheduled 7 days after publishing for YouTube metrics.
        """
        check = PendingOutcomeCheck(
            record_id=outcome.record_id,
            session_name=outcome.session_name,
            youtube_video_id=youtube_video_id,
            scheduled_at=datetime.now(),
            days_to_wait=days_to_wait
        )

        data = self._load_yaml(self.pending_checks_file)
        records = data.get('records', [])

        # Don't add duplicate
        existing = next(
            (r for r in records if r.get('record_id') == check.record_id),
            None
        )
        if existing:
            return

        records.append(check.to_dict())
        data['records'] = records
        data['last_updated'] = datetime.now().isoformat()
        self._save_yaml(self.pending_checks_file, data)

    def get_pending_checks(self, ready_only: bool = True) -> List[PendingOutcomeCheck]:
        """
        Get pending outcome checks.

        Args:
            ready_only: If True, only return checks where enough time has passed

        Returns:
            List of pending checks
        """
        data = self._load_yaml(self.pending_checks_file)
        results = []

        for record_data in data.get('records', []):
            check = PendingOutcomeCheck.from_dict(record_data)

            if ready_only:
                elapsed_days = (datetime.now() - check.scheduled_at).days
                if elapsed_days >= check.days_to_wait:
                    results.append(check)
            else:
                results.append(check)

        return results

    def mark_check_complete(self, record_id: str):
        """Mark a pending check as complete (remove it)."""
        data = self._load_yaml(self.pending_checks_file)
        records = [
            r for r in data.get('records', [])
            if r.get('record_id') != record_id
        ]
        data['records'] = records
        data['last_updated'] = datetime.now().isoformat()
        self._save_yaml(self.pending_checks_file, data)

    def get_pending_outcome_checks(self, ready_only: bool = False) -> List[PendingOutcomeCheck]:
        """Alias for get_pending_checks for scheduler compatibility."""
        return self.get_pending_checks(ready_only=ready_only)

    def complete_pending_check(self, record_id: str):
        """Alias for mark_check_complete for scheduler compatibility."""
        self.mark_check_complete(record_id)

    def increment_check_attempts(self, record_id: str) -> bool:
        """
        Increment attempt count for a check.

        Returns:
            True if under max attempts, False if should give up
        """
        data = self._load_yaml(self.pending_checks_file)
        records = data.get('records', [])

        for i, r in enumerate(records):
            if r.get('record_id') == record_id:
                r['attempts'] = r.get('attempts', 0) + 1
                if r['attempts'] >= r.get('max_attempts', 3):
                    # Remove failed check
                    records.pop(i)
                    data['records'] = records
                    self._save_yaml(self.pending_checks_file, data)
                    return False
                records[i] = r
                data['records'] = records
                self._save_yaml(self.pending_checks_file, data)
                return True

        return False

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about the feedback store."""
        outcomes_data = self._load_yaml(self.outcomes_file)
        effectiveness_data = self._load_yaml(self.effectiveness_file)
        pending_data = self._load_yaml(self.pending_checks_file)

        outcomes = outcomes_data.get('records', [])
        effectiveness = effectiveness_data.get('records', [])
        pending = pending_data.get('records', [])

        # Calculate outcome stats
        successful = sum(1 for o in outcomes if o.get('generation_success', False))
        with_youtube = sum(1 for o in outcomes if o.get('metrics_complete', False))

        # Calculate effectiveness stats
        scored_lessons = [e for e in effectiveness if e.get('times_applied', 0) >= 3]
        avg_score = sum(e.get('effectiveness_score', 50) for e in scored_lessons) / len(scored_lessons) if scored_lessons else 50

        return {
            'total_outcomes': len(outcomes),
            'successful_generations': successful,
            'success_rate': successful / len(outcomes) if outcomes else 0,
            'outcomes_with_youtube': with_youtube,
            'total_lessons_tracked': len(effectiveness),
            'lessons_with_scores': len(scored_lessons),
            'average_effectiveness': avg_score,
            'pending_checks': len(pending),
        }


# Convenience function for creating record IDs
def generate_record_id(session_name: str) -> str:
    """Generate a unique record ID for a session."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    hash_input = f"{session_name}-{timestamp}"
    short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
    return f"outcome-{short_hash}"
