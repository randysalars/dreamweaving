"""
Content Scheduler Agent.

Calculates optimal posting times based on analytics and audience behavior.
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import math


@dataclass
class TimeSlot:
    """Represents a posting time slot."""
    day_of_week: int  # 0=Monday, 6=Sunday
    hour: int         # 0-23
    score: float      # 0-1 effectiveness score
    reason: str


@dataclass
class ScheduleRecommendation:
    """Recommendation for content scheduling."""
    session_name: str
    recommended_slots: List[TimeSlot]
    best_slot: TimeSlot
    audience_notes: List[str]
    seasonal_factors: Dict[str, float]


class ContentScheduler:
    """
    Content Scheduler Agent.

    Analyzes performance data and audience patterns to recommend
    optimal posting times for Dreamweaving content.
    """

    # Base posting time preferences (meditation/hypnosis content)
    # Score multipliers for different times
    BASE_TIME_SCORES = {
        # Early morning (meditation seekers)
        (5, 7): 0.7,
        # Morning routine
        (7, 9): 0.8,
        # Mid-morning
        (9, 11): 0.6,
        # Lunch break
        (11, 13): 0.5,
        # Afternoon slump
        (14, 16): 0.6,
        # Early evening (wind down)
        (17, 19): 0.7,
        # Prime time (relaxation)
        (19, 21): 0.95,
        # Late evening (sleep content)
        (21, 23): 1.0,
        # Night owls
        (23, 24): 0.8,
        (0, 2): 0.6,
        # Dead zone
        (2, 5): 0.3,
    }

    # Day of week multipliers
    DAY_SCORES = {
        0: 0.85,  # Monday (back to work, need relaxation)
        1: 0.80,  # Tuesday
        2: 0.85,  # Wednesday (midweek stress)
        3: 0.80,  # Thursday
        4: 0.90,  # Friday (weekend prep)
        5: 0.95,  # Saturday (leisure time)
        6: 1.00,  # Sunday (prime relaxation day)
    }

    # Content type optimal times
    CONTENT_TYPE_TIMES = {
        'sleep': {
            'best_hours': [21, 22, 23],
            'best_days': [0, 6],  # Sunday/Monday nights
            'avoid_hours': [9, 10, 11, 12, 13, 14, 15],
        },
        'relaxation': {
            'best_hours': [19, 20, 21],
            'best_days': [4, 5, 6],  # Weekend
            'avoid_hours': [6, 7, 8, 9],
        },
        'healing': {
            'best_hours': [10, 11, 19, 20],
            'best_days': [5, 6],  # Weekend mornings
            'avoid_hours': [0, 1, 2, 3, 4],
        },
        'transformation': {
            'best_hours': [20, 21],
            'best_days': [5, 6],
            'avoid_hours': [6, 7, 8, 14, 15],
        },
        'empowerment': {
            'best_hours': [7, 8, 9, 19],  # Morning motivation
            'best_days': [0, 1],  # Start of week
            'avoid_hours': [22, 23, 0, 1],
        },
        'spiritual': {
            'best_hours': [5, 6, 20, 21],  # Sacred times
            'best_days': [6],  # Sunday
            'avoid_hours': [12, 13, 14, 15],
        },
    }

    # Seasonal adjustments (Northern Hemisphere focus)
    SEASONAL_FACTORS = {
        # month: {category: multiplier}
        1: {'transformation': 1.3, 'healing': 1.1},  # New Year resolutions
        2: {'healing': 1.2, 'self-love': 1.3},  # Valentine's
        3: {'spiritual': 1.2, 'transformation': 1.1},  # Spring equinox
        4: {'spiritual': 1.1, 'nature': 1.2},  # Easter/Spring
        5: {'relaxation': 1.1, 'nature': 1.2},  # Spring
        6: {'relaxation': 1.2, 'cosmic': 1.1},  # Summer solstice
        7: {'relaxation': 1.2, 'nature': 1.1},  # Summer
        8: {'transformation': 1.1, 'spiritual': 1.0},  # Late summer
        9: {'transformation': 1.2, 'spiritual': 1.1},  # Fall equinox
        10: {'shadow-work': 1.4, 'transformation': 1.2},  # Halloween
        11: {'healing': 1.2, 'gratitude': 1.3},  # Thanksgiving
        12: {'spiritual': 1.3, 'healing': 1.2, 'sleep': 1.2},  # Winter solstice/holidays
    }

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parents[2]
        self.sessions_path = self.project_root / 'sessions'
        self.analytics_path = self.project_root / 'knowledge' / 'analytics_history'

    def _load_session_manifest(self, session_name: str) -> Optional[Dict[str, Any]]:
        """Load manifest from session directory."""
        manifest_path = self.sessions_path / session_name / 'manifest.yaml'
        if not manifest_path.exists():
            return None
        with open(manifest_path, 'r') as f:
            return yaml.safe_load(f)

    def _get_content_type(self, session_name: str) -> str:
        """Determine content type from session manifest."""
        manifest = self._load_session_manifest(session_name)
        if not manifest:
            return 'relaxation'  # Default

        session = manifest.get('session', {})
        outcome = session.get('desired_outcome', '').lower()

        if outcome in self.CONTENT_TYPE_TIMES:
            return outcome

        # Infer from other fields
        title = session.get('title', '').lower()
        if 'sleep' in title:
            return 'sleep'
        if 'heal' in title:
            return 'healing'
        if 'transform' in title:
            return 'transformation'
        if 'power' in title or 'confidence' in title:
            return 'empowerment'
        if 'spirit' in title or 'sacred' in title:
            return 'spiritual'

        return 'relaxation'

    def _calculate_time_score(
        self,
        hour: int,
        day: int,
        content_type: str
    ) -> Tuple[float, str]:
        """Calculate posting score for a specific time."""
        # Base time score
        base_score = 0.5  # Default
        for (start, end), score in self.BASE_TIME_SCORES.items():
            if start <= hour < end:
                base_score = score
                break

        # Day multiplier
        day_mult = self.DAY_SCORES.get(day, 0.8)

        # Content type adjustments
        type_prefs = self.CONTENT_TYPE_TIMES.get(content_type, {})
        type_mult = 1.0
        reason_parts = []

        if hour in type_prefs.get('best_hours', []):
            type_mult = 1.3
            reason_parts.append(f"peak time for {content_type}")
        elif hour in type_prefs.get('avoid_hours', []):
            type_mult = 0.5
            reason_parts.append(f"suboptimal for {content_type}")

        if day in type_prefs.get('best_days', []):
            type_mult *= 1.2
            reason_parts.append("best day of week")

        # Calculate final score
        score = base_score * day_mult * type_mult
        score = min(score, 1.0)

        # Build reason string
        reason = f"Base: {base_score:.2f}, Day: {day_mult:.2f}, Type: {type_mult:.2f}"
        if reason_parts:
            reason += f" ({', '.join(reason_parts)})"

        return score, reason

    def _get_seasonal_factor(
        self,
        content_type: str,
        month: Optional[int] = None
    ) -> Dict[str, float]:
        """Get seasonal adjustment factors."""
        if month is None:
            month = datetime.now().month

        monthly_factors = self.SEASONAL_FACTORS.get(month, {})

        return {
            'month': month,
            'factors': monthly_factors,
            'boost': monthly_factors.get(content_type, 1.0),
        }

    def recommend_posting_time(
        self,
        session_name: str,
        num_slots: int = 5
    ) -> ScheduleRecommendation:
        """
        Recommend optimal posting times for a session.

        Args:
            session_name: Session to schedule
            num_slots: Number of time slots to recommend

        Returns:
            ScheduleRecommendation with ranked time slots
        """
        content_type = self._get_content_type(session_name)

        # Score all possible slots
        all_slots = []
        for day in range(7):
            for hour in range(24):
                score, reason = self._calculate_time_score(hour, day, content_type)
                slot = TimeSlot(
                    day_of_week=day,
                    hour=hour,
                    score=score,
                    reason=reason,
                )
                all_slots.append(slot)

        # Sort by score
        all_slots.sort(key=lambda x: x.score, reverse=True)

        # Get top slots
        recommended = all_slots[:num_slots]

        # Audience notes
        audience_notes = self._generate_audience_notes(content_type)

        # Seasonal factors
        seasonal = self._get_seasonal_factor(content_type)

        return ScheduleRecommendation(
            session_name=session_name,
            recommended_slots=recommended,
            best_slot=recommended[0],
            audience_notes=audience_notes,
            seasonal_factors=seasonal,
        )

    def _generate_audience_notes(self, content_type: str) -> List[str]:
        """Generate audience behavior notes for content type."""
        notes = []

        type_notes = {
            'sleep': [
                "Sleep content performs best 9-11pm local time",
                "Sunday and Monday nights have highest engagement",
                "Avoid morning posts - contradicts sleep intent",
            ],
            'relaxation': [
                "Weekend evenings are prime relaxation time",
                "Friday afternoon posts capture wind-down seekers",
                "Steady performance throughout week",
            ],
            'healing': [
                "Weekend mornings attract healing seekers",
                "Emotional content needs time for engagement",
                "Avoid posting during busy work hours",
            ],
            'transformation': [
                "Deep content needs dedicated time - weekends best",
                "Evening posts allow for full listening",
                "New moon phases may boost engagement",
            ],
            'empowerment': [
                "Monday morning posts capture fresh-start energy",
                "Early morning resonates with go-getters",
                "Avoid late night - empowerment is daytime energy",
            ],
            'spiritual': [
                "Sunday has traditional spiritual resonance",
                "Dawn and dusk are sacred transition times",
                "Solstices and equinoxes boost spiritual content",
            ],
        }

        notes = type_notes.get(content_type, [
            "Evening posts generally perform well",
            "Weekends see higher engagement",
            "Consider your audience's timezone",
        ])

        return notes

    def create_content_calendar(
        self,
        sessions: List[str],
        start_date: Optional[datetime] = None,
        posts_per_week: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Create a content calendar for multiple sessions.

        Args:
            sessions: List of session names to schedule
            start_date: Calendar start date (default: next Monday)
            posts_per_week: Target posts per week

        Returns:
            List of scheduled posts with dates and times
        """
        if start_date is None:
            # Start next Monday
            today = datetime.now()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            start_date = today + timedelta(days=days_until_monday)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        calendar = []
        current_date = start_date

        # Optimal posting days for meditation content
        preferred_days = [6, 0, 4]  # Sun, Mon, Fri

        for session in sessions:
            rec = self.recommend_posting_time(session, num_slots=3)
            best_slot = rec.best_slot

            # Find next occurrence of the best day
            while current_date.weekday() != best_slot.day_of_week:
                current_date += timedelta(days=1)

            post_time = current_date.replace(hour=best_slot.hour)

            calendar.append({
                'session': session,
                'date': post_time.isoformat(),
                'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][best_slot.day_of_week],
                'time': f"{best_slot.hour:02d}:00",
                'score': best_slot.score,
                'notes': rec.audience_notes[:2],
            })

            # Move to next slot (at least 2 days apart)
            current_date += timedelta(days=2)

        return calendar

    def analyze_posting_patterns(self) -> Dict[str, Any]:
        """
        Analyze historical posting patterns and performance.

        Returns insights about what's working.
        """
        # This would integrate with YouTube analytics
        # For now, return recommendations based on content analysis

        sessions_by_type = defaultdict(list)

        for session_dir in self.sessions_path.iterdir():
            if not session_dir.is_dir():
                continue
            if session_dir.name.startswith(('_', '.', 'shorts')):
                continue

            content_type = self._get_content_type(session_dir.name)
            sessions_by_type[content_type].append(session_dir.name)

        return {
            'content_distribution': {k: len(v) for k, v in sessions_by_type.items()},
            'recommendations': [
                "Diversify content types if one dominates",
                "Match posting time to content type",
                "Consider seasonal themes",
            ],
            'optimal_schedule': {
                'sleep': "Sun-Tue, 9-11pm",
                'relaxation': "Fri-Sun, 7-9pm",
                'healing': "Sat-Sun, 10am or 7pm",
                'transformation': "Sat, 8pm",
                'empowerment': "Mon, 7am",
                'spiritual': "Sun, 6am or 8pm",
            }
        }

    def get_next_optimal_slot(
        self,
        content_type: str = 'relaxation'
    ) -> Dict[str, Any]:
        """Get the next optimal posting slot from now."""
        now = datetime.now()

        # Check next 7 days
        best_slot = None
        best_score = 0
        best_datetime = None

        for day_offset in range(7):
            check_date = now + timedelta(days=day_offset)
            day = check_date.weekday()

            for hour in range(24):
                # Skip hours that have passed today
                if day_offset == 0 and hour <= now.hour:
                    continue

                score, reason = self._calculate_time_score(hour, day, content_type)

                if score > best_score:
                    best_score = score
                    best_slot = TimeSlot(day, hour, score, reason)
                    best_datetime = check_date.replace(hour=hour, minute=0, second=0)

        return {
            'datetime': best_datetime.isoformat() if best_datetime else None,
            'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][best_slot.day_of_week],
            'hour': best_slot.hour,
            'score': best_slot.score,
            'reason': best_slot.reason,
        }


# CLI interface
if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Content Scheduler')
    parser.add_argument('action', choices=['recommend', 'calendar', 'analyze', 'next'],
                       help='Action to perform')
    parser.add_argument('--session', help='Session name')
    parser.add_argument('--sessions', help='Comma-separated session names')
    parser.add_argument('--type', default='relaxation', help='Content type')

    args = parser.parse_args()

    scheduler = ContentScheduler()

    if args.action == 'recommend' and args.session:
        rec = scheduler.recommend_posting_time(args.session)
        print(f"\n=== Scheduling {args.session} ===")
        print(f"\nBest slot: {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][rec.best_slot.day_of_week]} at {rec.best_slot.hour}:00")
        print(f"Score: {rec.best_slot.score:.2f}")
        print(f"\nTop 5 slots:")
        for slot in rec.recommended_slots:
            day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][slot.day_of_week]
            print(f"  {day_name} {slot.hour:02d}:00 - Score: {slot.score:.2f}")
        print(f"\nAudience notes:")
        for note in rec.audience_notes:
            print(f"  - {note}")

    elif args.action == 'calendar' and args.sessions:
        sessions = [s.strip() for s in args.sessions.split(',')]
        calendar = scheduler.create_content_calendar(sessions)
        print("\n=== Content Calendar ===")
        for entry in calendar:
            print(f"\n{entry['date'][:10]} ({entry['day']}) at {entry['time']}")
            print(f"  Session: {entry['session']}")
            print(f"  Score: {entry['score']:.2f}")

    elif args.action == 'analyze':
        analysis = scheduler.analyze_posting_patterns()
        print(json.dumps(analysis, indent=2))

    elif args.action == 'next':
        next_slot = scheduler.get_next_optimal_slot(args.type)
        print(f"\n=== Next Optimal Slot for {args.type} ===")
        print(f"Date: {next_slot['datetime'][:10]}")
        print(f"Time: {next_slot['hour']:02d}:00 ({next_slot['day']})")
        print(f"Score: {next_slot['score']:.2f}")
        print(f"Reason: {next_slot['reason']}")
