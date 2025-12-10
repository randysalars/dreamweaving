#!/usr/bin/env python3
"""
Archetype Selector - Intelligent Recurring Archetype Selection

Selects archetypes based on:
1. Session outcome alignment
2. Listener relationship history
3. Recency penalty (avoid overuse)
4. Family diversity
5. Synergies with other selected archetypes

Usage:
    from archetype_selector import ArchetypeSelector

    selector = ArchetypeSelector()
    archetypes = selector.select_archetypes(
        outcome="healing",
        journey_phases=["journey", "helm_deep_trance"],
        count=3,
        prefer_recurring=True
    )
"""

import yaml
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ArchetypeEntry:
    """Represents an archetype with all its metadata."""
    archetype_id: str
    name: str
    family: str
    definition: dict
    attributes: dict
    tradition_equivalents: dict
    applications: dict
    templates: dict
    relationships: dict

    @property
    def primary_color(self) -> str:
        return self.attributes.get('primary_color', 'white')

    @property
    def frequency_hz(self) -> float:
        return self.attributes.get('frequency_hz', 528)

    @property
    def outcome_alignment(self) -> list:
        return self.applications.get('outcome_alignment', [])

    @property
    def journey_phases(self) -> list:
        return self.applications.get('journey_phases', [])


@dataclass
class SelectedArchetype:
    """Archetype selected for a session with encounter details."""
    archetype_id: str
    name: str
    family: str
    role: str  # primary, secondary, support
    encounter_type: str  # first_encounter, return_encounter, transformation
    relationship_level: int  # 1-4
    appearance_section: str  # journey, helm_deep_trance, integration
    templates: dict
    attributes: dict
    description: str = ""  # Brief definition from codex
    symbol: str = ""  # Visual symbol representation
    qualities: list = field(default_factory=list)  # Archetype qualities/attributes
    score: float = 0.0


class ArchetypeSelector:
    """
    Intelligent archetype selector for Dreamweaving sessions.

    Loads archetype codex and history, then provides selection
    methods that consider outcome alignment, history, and diversity.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize selector with project paths."""
        if project_root is None:
            # Try to find project root
            current = Path(__file__).resolve()
            for parent in current.parents:
                if (parent / "knowledge").exists():
                    project_root = parent
                    break
            if project_root is None:
                project_root = Path.cwd()

        self.project_root = Path(project_root)
        self.knowledge_path = self.project_root / "knowledge"

        # Load codex and history
        self.codex = self._load_codex()
        self.history = self._load_history()
        self.family_index = self._load_family_index()

        # Configuration
        self.recency_penalty_weight = 0.15
        self.relationship_bonus_weight = 0.2
        self.diversity_bonus_weight = 0.1
        self.synergy_bonus_weight = 0.1
        self.recency_cooldown_sessions = 3

    def _load_codex(self) -> dict:
        """Load archetype codex from YAML."""
        codex_path = self.knowledge_path / "archetypes" / "archetype_codex.yaml"
        if not codex_path.exists():
            logger.warning(f"Archetype codex not found at {codex_path}")
            return {}

        with open(codex_path, 'r') as f:
            data = yaml.safe_load(f)

        # Flatten the nested family structure into a flat archetype dict
        archetypes = {}
        for family_key, family_data in data.items():
            if family_key == 'metadata':
                continue
            if isinstance(family_data, dict) and 'family_metadata' in family_data:
                # This is a family section
                for arch_key, arch_data in family_data.items():
                    if arch_key == 'family_metadata':
                        continue
                    if isinstance(arch_data, dict) and 'archetype_id' in arch_data:
                        archetypes[arch_data['archetype_id']] = arch_data

        logger.info(f"Loaded {len(archetypes)} archetypes from codex")
        return archetypes

    def _load_history(self) -> dict:
        """Load archetype history from YAML."""
        history_path = self.knowledge_path / "archetypes" / "archetype_history.yaml"
        if not history_path.exists():
            logger.warning(f"Archetype history not found at {history_path}")
            return {
                'session_history': [],
                'listener_relationships': {},
                'recency_data': {'archetype_cooldowns': {}},
                'family_rotation': {'last_session_families': [], 'family_usage_counts': {}}
            }

        with open(history_path, 'r') as f:
            return yaml.safe_load(f) or {}

    def _load_family_index(self) -> dict:
        """Load family index for outcome mapping."""
        index_path = self.knowledge_path / "indexes" / "archetype_family_index.yaml"
        if not index_path.exists():
            return {}

        with open(index_path, 'r') as f:
            return yaml.safe_load(f) or {}

    def select_archetypes(
        self,
        outcome: str,
        journey_phases: Optional[list] = None,
        count: int = 3,
        exclude: Optional[list] = None,
        prefer_recurring: bool = True,
        tradition: Optional[str] = None
    ) -> list[SelectedArchetype]:
        """
        Select archetypes for a session with intelligent scoring.

        Args:
            outcome: Desired session outcome (healing, transformation, etc.)
            journey_phases: Which phases archetypes will appear in
            count: Number of archetypes to select
            exclude: Archetype IDs to exclude
            prefer_recurring: Favor archetypes with established relationships
            tradition: Optional tradition for name equivalents

        Returns:
            List of SelectedArchetype objects with encounter details
        """
        if journey_phases is None:
            journey_phases = ['journey', 'helm_deep_trance', 'integration']

        if exclude is None:
            exclude = []

        # Score all archetypes
        scored = []
        for arch_id, arch_data in self.codex.items():
            if arch_id in exclude:
                continue

            score = self._score_archetype(
                arch_id,
                arch_data,
                outcome,
                journey_phases,
                prefer_recurring
            )

            if score > 0:
                scored.append((arch_id, arch_data, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[2], reverse=True)

        # Select top archetypes with diversity consideration
        selected = self._select_with_diversity(scored, count)

        # Convert to SelectedArchetype objects
        result = []
        roles = ['primary', 'secondary', 'support']
        sections = ['journey', 'helm_deep_trance', 'integration']

        for i, (arch_id, arch_data, score) in enumerate(selected):
            encounter_type = self.get_encounter_type(arch_id)
            relationship_level = self._get_relationship_level(arch_id)

            # Extract description from definition.brief or extended
            definition = arch_data.get('definition', {})
            description = definition.get('brief', '') or definition.get('extended', '')[:200] if definition.get('extended') else ''

            # Extract symbol and qualities from attributes
            attributes = arch_data.get('attributes', {})
            symbol = attributes.get('symbol', '')
            qualities = attributes.get('qualities', [])

            result.append(SelectedArchetype(
                archetype_id=arch_id,
                name=arch_data.get('name', arch_id),
                family=arch_data.get('family', 'unknown'),
                role=roles[min(i, len(roles) - 1)],
                encounter_type=encounter_type,
                relationship_level=relationship_level,
                appearance_section=sections[min(i, len(sections) - 1)],
                templates=arch_data.get('templates', {}),
                attributes=attributes,
                description=description,
                symbol=symbol,
                qualities=qualities,
                score=score
            ))

        return result

    def _score_archetype(
        self,
        arch_id: str,
        arch_data: dict,
        outcome: str,
        journey_phases: list,
        prefer_recurring: bool
    ) -> float:
        """Calculate selection score for an archetype."""
        score = 0.0

        # 1. Outcome alignment (most important)
        outcome_alignment = arch_data.get('applications', {}).get('outcome_alignment', [])
        if outcome in outcome_alignment:
            score += 1.0
        elif any(o in outcome_alignment for o in ['all', outcome]):
            score += 0.8
        else:
            # Check if outcome is related (e.g., 'healing' related to 'relaxation')
            related_outcomes = {
                'healing': ['relaxation', 'transformation'],
                'transformation': ['release', 'healing'],
                'empowerment': ['confidence', 'courage'],
                'spiritual_growth': ['self_knowledge', 'transformation'],
            }
            if any(o in outcome_alignment for o in related_outcomes.get(outcome, [])):
                score += 0.4

        # 2. Journey phase alignment
        arch_phases = arch_data.get('applications', {}).get('journey_phases', [])
        phase_overlap = len(set(journey_phases) & set(arch_phases))
        if phase_overlap > 0:
            score += 0.3 * (phase_overlap / len(journey_phases))

        # 3. Relationship bonus (if prefer_recurring)
        if prefer_recurring:
            relationship = self.history.get('listener_relationships', {}).get(arch_id, {})
            if relationship:
                level = relationship.get('relationship_level', 1)
                # Level 2-3 gets bonus (familiar but not overused)
                if level in [2, 3]:
                    score += self.relationship_bonus_weight
                elif level == 4:
                    # Mastered - slight bonus but prefer variety
                    score += self.relationship_bonus_weight * 0.5

        # 4. Recency penalty
        cooldowns = self.history.get('recency_data', {}).get('archetype_cooldowns', {})
        sessions_since = cooldowns.get(arch_id, self.recency_cooldown_sessions + 1)
        if sessions_since < self.recency_cooldown_sessions:
            penalty = self.recency_penalty_weight * (1 - sessions_since / self.recency_cooldown_sessions)
            score -= penalty

        # 5. Intensity matching (optional)
        intensity = arch_data.get('attributes', {}).get('intensity', 'moderate')
        if outcome in ['healing', 'relaxation'] and intensity in ['gentle', 'moderate']:
            score += 0.1
        elif outcome in ['transformation', 'empowerment'] and intensity in ['strong', 'very_strong']:
            score += 0.1

        return max(0, score)  # Don't return negative scores

    def _select_with_diversity(
        self,
        scored: list,
        count: int
    ) -> list:
        """Select archetypes while ensuring family diversity."""
        selected = []
        families_used = set()

        for arch_id, arch_data, score in scored:
            if len(selected) >= count:
                break

            family = arch_data.get('family', 'unknown')

            # Allow first archetype from any family
            # For subsequent, prefer different families
            if len(selected) == 0:
                selected.append((arch_id, arch_data, score))
                families_used.add(family)
            elif family not in families_used:
                # Different family - good for diversity
                selected.append((arch_id, arch_data, score + self.diversity_bonus_weight))
                families_used.add(family)
            elif len(families_used) >= count - 1:
                # We've used enough different families, allow repeats
                selected.append((arch_id, arch_data, score))
                families_used.add(family)

        # If we don't have enough, take from same families
        if len(selected) < count:
            for arch_id, arch_data, score in scored:
                if (arch_id, arch_data, score) not in selected:
                    selected.append((arch_id, arch_data, score))
                if len(selected) >= count:
                    break

        return selected

    def get_encounter_type(self, archetype_id: str) -> str:
        """
        Determine appropriate encounter type based on history.

        Returns:
            'first_encounter' if never used
            'return_encounter' if used 1-6 times
            'integration' if used 7+ times (mastered)
        """
        relationships = self.history.get('listener_relationships', {})
        relationship = relationships.get(archetype_id, {})

        total_encounters = relationship.get('total_encounters', 0)

        if total_encounters == 0:
            return 'first_encounter'
        elif total_encounters < 7:
            return 'return_encounter'
        else:
            return 'integration'

    def _get_relationship_level(self, archetype_id: str) -> int:
        """Get relationship level (1-4) for an archetype."""
        relationships = self.history.get('listener_relationships', {})
        relationship = relationships.get(archetype_id, {})
        return relationship.get('relationship_level', 1)

    def get_ssml_template(
        self,
        archetype_id: str,
        context: str = 'encounter'
    ) -> str:
        """
        Get appropriate SSML template for an archetype.

        Args:
            archetype_id: Full archetype ID
            context: 'encounter' (uses encounter_type), 'transformation', 'integration'

        Returns:
            SSML template string
        """
        if archetype_id not in self.codex:
            logger.warning(f"Archetype {archetype_id} not found in codex")
            return ""

        templates = self.codex[archetype_id].get('templates', {})

        if context == 'encounter':
            encounter_type = self.get_encounter_type(archetype_id)
            template_key = f"{encounter_type}_ssml"
        elif context == 'transformation':
            template_key = 'transformation_ssml'
        elif context == 'integration':
            template_key = 'integration_ssml'
        else:
            template_key = f"{context}_ssml"

        return templates.get(template_key, templates.get('first_encounter_ssml', ''))

    def update_history(
        self,
        session_id: str,
        archetypes_used: list[SelectedArchetype],
        session_outcome: Optional[str] = None,
        notes: str = ""
    ) -> None:
        """
        Record archetype usage after session completion.

        Args:
            session_id: Unique session identifier
            archetypes_used: List of SelectedArchetype objects
            session_outcome: Optional outcome for tracking
            notes: Optional notes about the session
        """
        today = datetime.now().strftime("%Y-%m-%d")

        # Ensure history structure exists
        if 'session_history' not in self.history:
            self.history['session_history'] = []
        if 'listener_relationships' not in self.history:
            self.history['listener_relationships'] = {}
        if 'recency_data' not in self.history:
            self.history['recency_data'] = {'archetype_cooldowns': {}, 'last_5_sessions': []}
        if 'family_rotation' not in self.history:
            self.history['family_rotation'] = {'last_session_families': [], 'family_usage_counts': {}}

        # Add session entry
        session_entry = {
            'session_id': session_id,
            'date': today,
            'outcome': session_outcome,
            'archetypes_used': [
                {
                    'archetype_id': a.archetype_id,
                    'role': a.role,
                    'encounter_type': a.encounter_type,
                    'section': a.appearance_section
                }
                for a in archetypes_used
            ],
            'notes': notes
        }
        self.history['session_history'].append(session_entry)

        # Update listener relationships
        families_used = []
        for arch in archetypes_used:
            arch_id = arch.archetype_id
            families_used.append(arch.family)

            if arch_id not in self.history['listener_relationships']:
                self.history['listener_relationships'][arch_id] = {
                    'total_encounters': 0,
                    'first_session': session_id,
                    'first_session_date': today,
                    'encounter_history': []
                }

            rel = self.history['listener_relationships'][arch_id]
            rel['total_encounters'] += 1
            rel['last_session'] = session_id
            rel['last_session_date'] = today
            rel['encounter_history'].append({
                'session': session_id,
                'type': arch.encounter_type
            })

            # Update relationship level
            encounters = rel['total_encounters']
            if encounters >= 7:
                rel['relationship_level'] = 4
            elif encounters >= 4:
                rel['relationship_level'] = 3
            elif encounters >= 2:
                rel['relationship_level'] = 2
            else:
                rel['relationship_level'] = 1

            # Reset cooldown for used archetypes
            self.history['recency_data']['archetype_cooldowns'][arch_id] = 0

        # Increment cooldowns for unused archetypes
        for arch_id in self.history['recency_data'].get('archetype_cooldowns', {}):
            if arch_id not in [a.archetype_id for a in archetypes_used]:
                self.history['recency_data']['archetype_cooldowns'][arch_id] += 1

        # Update last 5 sessions
        last_5 = self.history['recency_data'].get('last_5_sessions', [])
        last_5.append(session_id)
        self.history['recency_data']['last_5_sessions'] = last_5[-5:]

        # Update family rotation
        self.history['family_rotation']['last_session_families'] = families_used
        for family in families_used:
            counts = self.history['family_rotation'].get('family_usage_counts', {})
            counts[family] = counts.get(family, 0) + 1
            self.history['family_rotation']['family_usage_counts'] = counts

        # Save updated history
        self._save_history()

    def _save_history(self) -> None:
        """Save history back to YAML file."""
        history_path = self.knowledge_path / "archetypes" / "archetype_history.yaml"

        # Update metadata
        if 'metadata' not in self.history:
            self.history['metadata'] = {}
        self.history['metadata']['updated'] = datetime.now().strftime("%Y-%m-%d")
        self.history['metadata']['total_sessions_tracked'] = len(self.history.get('session_history', []))
        self.history['metadata']['unique_archetypes_used'] = len(self.history.get('listener_relationships', {}))

        with open(history_path, 'w') as f:
            yaml.dump(self.history, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        logger.info(f"Saved archetype history to {history_path}")

    def get_archetype_by_id(self, archetype_id: str) -> Optional[dict]:
        """Get full archetype data by ID."""
        return self.codex.get(archetype_id)

    def get_archetypes_by_family(self, family: str) -> list[dict]:
        """Get all archetypes in a family."""
        return [
            arch for arch in self.codex.values()
            if arch.get('family') == family
        ]

    def get_archetypes_by_outcome(self, outcome: str) -> list[dict]:
        """Get all archetypes aligned with an outcome."""
        return [
            arch for arch in self.codex.values()
            if outcome in arch.get('applications', {}).get('outcome_alignment', [])
        ]


def main():
    """Demo usage of ArchetypeSelector."""
    selector = ArchetypeSelector()

    print("=== Archetype Selector Demo ===\n")

    # Select archetypes for a healing session
    print("Selecting archetypes for 'healing' outcome:\n")
    archetypes = selector.select_archetypes(
        outcome="healing",
        journey_phases=["journey", "helm_deep_trance"],
        count=3
    )

    for arch in archetypes:
        print(f"  {arch.role.upper()}: {arch.name}")
        print(f"    ID: {arch.archetype_id}")
        print(f"    Family: {arch.family}")
        print(f"    Encounter: {arch.encounter_type}")
        print(f"    Score: {arch.score:.2f}")
        print()

    # Show SSML template for first archetype
    if archetypes:
        first = archetypes[0]
        print(f"\nSSML Template for {first.name}:")
        print("-" * 40)
        template = selector.get_ssml_template(first.archetype_id, 'encounter')
        print(template[:500] + "..." if len(template) > 500 else template)


if __name__ == "__main__":
    main()
