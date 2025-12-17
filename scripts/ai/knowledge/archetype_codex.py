"""
Archetype Codex Agent.

Deep archetype relationship mapping for coherent session design.
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set, Tuple
from collections import defaultdict
from enum import Enum


class ArchetypeRole(Enum):
    """Roles an archetype can play in a journey."""
    GUIDE = "guide"
    CHALLENGER = "challenger"
    ALLY = "ally"
    THRESHOLD_GUARDIAN = "threshold_guardian"
    SHADOW = "shadow"
    MENTOR = "mentor"
    SHAPESHIFTER = "shapeshifter"
    HERALD = "herald"
    TRICKSTER = "trickster"


class JourneyPhase(Enum):
    """Phases of the hero's journey where archetypes appear."""
    ORDINARY_WORLD = "ordinary_world"
    CALL_TO_ADVENTURE = "call_to_adventure"
    REFUSAL = "refusal"
    MEETING_MENTOR = "meeting_mentor"
    CROSSING_THRESHOLD = "crossing_threshold"
    TESTS_ALLIES_ENEMIES = "tests_allies_enemies"
    APPROACH = "approach"
    ORDEAL = "ordeal"
    REWARD = "reward"
    ROAD_BACK = "road_back"
    RESURRECTION = "resurrection"
    RETURN_WITH_ELIXIR = "return_with_elixir"


@dataclass
class Archetype:
    """Represents an archetype with full relational data."""
    name: str
    description: str
    shadow_aspect: str
    gift: str
    typical_roles: List[ArchetypeRole]
    journey_phases: List[JourneyPhase]
    associated_symbols: List[str] = field(default_factory=list)
    voice_qualities: List[str] = field(default_factory=list)
    transformation_path: str = ""
    related_archetypes: List[str] = field(default_factory=list)
    cautions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'shadow_aspect': self.shadow_aspect,
            'gift': self.gift,
            'typical_roles': [r.value for r in self.typical_roles],
            'journey_phases': [p.value for p in self.journey_phases],
            'associated_symbols': self.associated_symbols,
            'voice_qualities': self.voice_qualities,
            'transformation_path': self.transformation_path,
            'related_archetypes': self.related_archetypes,
            'cautions': self.cautions,
        }


@dataclass
class ArchetypeRelation:
    """Represents a relationship between archetypes."""
    archetype_a: str
    archetype_b: str
    relation_type: str  # complementary, polar, evolutionary, shadow_pair
    dynamics: str  # Description of how they interact
    narrative_potential: str  # Story possibilities


class ArchetypeCodex:
    """
    Archetype Codex Agent.

    Provides deep archetype relationship mapping, role suggestions,
    and narrative coherence for journey design.
    """

    ARCHETYPE_DATABASE = {
        # Universal Archetypes
        'wise_elder': Archetype(
            name='Wise Elder',
            description='Ancient wisdom keeper, the one who has walked the path before',
            shadow_aspect='Dogmatic teacher, knowledge hoarder, manipulative guru',
            gift='Wisdom, guidance, perspective across time',
            typical_roles=[ArchetypeRole.MENTOR, ArchetypeRole.GUIDE],
            journey_phases=[JourneyPhase.MEETING_MENTOR, JourneyPhase.RETURN_WITH_ELIXIR],
            associated_symbols=['staff', 'book', 'mountain', 'white beard'],
            voice_qualities=['deep', 'measured', 'patient', 'ancient'],
            transformation_path='From seeker to sage through experience',
            related_archetypes=['sage', 'crone', 'hermit'],
            cautions=['Avoid making dependent on external wisdom'],
        ),
        'healer': Archetype(
            name='Healer',
            description='Restorer of wholeness, mender of wounds',
            shadow_aspect='Wounded healer who hasn\'t healed self, rescuer complex',
            gift='Restoration, compassion, integration',
            typical_roles=[ArchetypeRole.ALLY, ArchetypeRole.GUIDE],
            journey_phases=[JourneyPhase.REWARD, JourneyPhase.RESURRECTION],
            associated_symbols=['hands', 'light', 'herbs', 'water'],
            voice_qualities=['warm', 'soothing', 'gentle', 'compassionate'],
            transformation_path='From wounded to healed to healer',
            related_archetypes=['nurturer', 'medicine_woman', 'shaman'],
            cautions=['Honor listener\'s own healing capacity'],
        ),
        'warrior': Archetype(
            name='Warrior',
            description='Protector, defender, one who fights for what matters',
            shadow_aspect='Aggressor, bully, violence without purpose',
            gift='Courage, boundaries, protection, strength',
            typical_roles=[ArchetypeRole.ALLY, ArchetypeRole.CHALLENGER],
            journey_phases=[JourneyPhase.TESTS_ALLIES_ENEMIES, JourneyPhase.ORDEAL],
            associated_symbols=['sword', 'shield', 'armor', 'fire'],
            voice_qualities=['strong', 'direct', 'fierce', 'protective'],
            transformation_path='From aggressor to protector to peaceful warrior',
            related_archetypes=['guardian', 'defender', 'knight'],
            cautions=['Frame strength in service of protection, not domination'],
        ),
        'innocent': Archetype(
            name='Innocent',
            description='Pure being, untainted by world, original self',
            shadow_aspect='Naivete, denial, victim mentality',
            gift='Trust, wonder, optimism, fresh perception',
            typical_roles=[ArchetypeRole.ALLY],
            journey_phases=[JourneyPhase.ORDINARY_WORLD, JourneyPhase.RETURN_WITH_ELIXIR],
            associated_symbols=['child', 'sunrise', 'flowers', 'white'],
            voice_qualities=['light', 'wondering', 'open', 'curious'],
            transformation_path='From naive to experienced while retaining wonder',
            related_archetypes=['child', 'fool', 'pure_one'],
            cautions=['Don\'t infantilize; honor mature innocence'],
        ),
        'shadow': Archetype(
            name='Shadow',
            description='Rejected self, hidden aspects, the disowned',
            shadow_aspect='The shadow is itself shadow; danger is non-integration',
            gift='Wholeness through integration, hidden power, authenticity',
            typical_roles=[ArchetypeRole.SHADOW, ArchetypeRole.CHALLENGER],
            journey_phases=[JourneyPhase.ORDEAL, JourneyPhase.APPROACH],
            associated_symbols=['darkness', 'mirror', 'cave', 'mask'],
            voice_qualities=['various', 'often echoing listener\'s voice'],
            transformation_path='From rejected to acknowledged to integrated',
            related_archetypes=['dark_self', 'denied_one', 'rejected_child'],
            cautions=['Require safe container; don\'t force; offer return path'],
        ),
        'trickster': Archetype(
            name='Trickster',
            description='Rule breaker, boundary crosser, catalyst for change',
            shadow_aspect='Destructive chaos, manipulation, cruel pranks',
            gift='Liberation from rigid patterns, humor, creativity',
            typical_roles=[ArchetypeRole.TRICKSTER, ArchetypeRole.HERALD],
            journey_phases=[JourneyPhase.CALL_TO_ADVENTURE, JourneyPhase.TESTS_ALLIES_ENEMIES],
            associated_symbols=['coyote', 'raven', 'jester', 'crossroads'],
            voice_qualities=['playful', 'irreverent', 'quicksilver', 'mischievous'],
            transformation_path='From chaos bringer to sacred fool',
            related_archetypes=['fool', 'coyote', 'hermes', 'loki'],
            cautions=['Balance disruption with safety; clear intent'],
        ),
        'mother': Archetype(
            name='Great Mother',
            description='Nurturer, life-giver, unconditional love, earth',
            shadow_aspect='Devouring mother, smothering, withholding',
            gift='Nurturing, unconditional acceptance, life force',
            typical_roles=[ArchetypeRole.GUIDE, ArchetypeRole.ALLY],
            journey_phases=[JourneyPhase.ORDINARY_WORLD, JourneyPhase.REWARD],
            associated_symbols=['earth', 'womb', 'breast', 'cave', 'garden'],
            voice_qualities=['warm', 'embracing', 'accepting', 'nurturing'],
            transformation_path='From dependent to nurtured to self-nurturing',
            related_archetypes=['earth_mother', 'nurturer', 'goddess'],
            cautions=['Honor both comfort and growth; don\'t enable dependency'],
        ),
        'father': Archetype(
            name='Father',
            description='Provider, protector, order, structure, authority',
            shadow_aspect='Tyrant, absent father, harsh judge',
            gift='Structure, protection, guidance, approval',
            typical_roles=[ArchetypeRole.MENTOR, ArchetypeRole.THRESHOLD_GUARDIAN],
            journey_phases=[JourneyPhase.MEETING_MENTOR, JourneyPhase.RESURRECTION],
            associated_symbols=['sky', 'sun', 'throne', 'scepter'],
            voice_qualities=['authoritative', 'protective', 'grounding'],
            transformation_path='From seeking approval to self-authority',
            related_archetypes=['king', 'sage', 'patriarch'],
            cautions=['Balance authority with warmth; avoid triggering trauma'],
        ),
        'anima': Archetype(
            name='Anima',
            description='Inner feminine, soul image, bridge to unconscious',
            shadow_aspect='Seductress, unreachable ideal, possession',
            gift='Connection to unconscious, creativity, soul',
            typical_roles=[ArchetypeRole.GUIDE, ArchetypeRole.SHAPESHIFTER],
            journey_phases=[JourneyPhase.APPROACH, JourneyPhase.ORDEAL],
            associated_symbols=['moon', 'water', 'mirror', 'flower'],
            voice_qualities=['flowing', 'mysterious', 'inviting', 'deep'],
            transformation_path='From projection to integration',
            related_archetypes=['soul_image', 'muse', 'inner_woman'],
            cautions=['Present as aspect of self, not external'],
        ),
        'animus': Archetype(
            name='Animus',
            description='Inner masculine, logos, bridge to conscious action',
            shadow_aspect='Inner critic, harsh judge, aggressive force',
            gift='Clarity, action, discrimination, words',
            typical_roles=[ArchetypeRole.CHALLENGER, ArchetypeRole.ALLY],
            journey_phases=[JourneyPhase.TESTS_ALLIES_ENEMIES, JourneyPhase.ORDEAL],
            associated_symbols=['sword', 'word', 'bridge', 'lion'],
            voice_qualities=['clear', 'direct', 'assertive', 'truthful'],
            transformation_path='From critic to ally',
            related_archetypes=['inner_man', 'logos', 'guide'],
            cautions=['Present as aspect of self, not external'],
        ),
        'divine_child': Archetype(
            name='Divine Child',
            description='New potential, future self, creative possibility',
            shadow_aspect='Peter Pan, refusal to grow, fragility',
            gift='Renewal, potential, creative beginnings',
            typical_roles=[ArchetypeRole.HERALD, ArchetypeRole.ALLY],
            journey_phases=[JourneyPhase.CALL_TO_ADVENTURE, JourneyPhase.RETURN_WITH_ELIXIR],
            associated_symbols=['sun child', 'egg', 'dawn', 'seed'],
            voice_qualities=['bright', 'full of wonder', 'pure', 'hopeful'],
            transformation_path='From potential to actualized',
            related_archetypes=['puer', 'innocent', 'future_self'],
            cautions=['Balance hope with groundedness'],
        ),
        'shapeshifter': Archetype(
            name='Shapeshifter',
            description='Changing form, uncertainty, transformation in process',
            shadow_aspect='Unreliable, deceptive, identity confusion',
            gift='Flexibility, adaptation, seeing multiple perspectives',
            typical_roles=[ArchetypeRole.SHAPESHIFTER, ArchetypeRole.CHALLENGER],
            journey_phases=[JourneyPhase.TESTS_ALLIES_ENEMIES, JourneyPhase.APPROACH],
            associated_symbols=['water', 'mist', 'animal transformations'],
            voice_qualities=['changing', 'fluid', 'mysterious'],
            transformation_path='From confusion to conscious flexibility',
            related_archetypes=['trickster', 'anima', 'animus'],
            cautions=['Provide stable frame around shapeshifting'],
        ),
        'threshold_guardian': Archetype(
            name='Threshold Guardian',
            description='Test at the gate, challenge before transformation',
            shadow_aspect='Obstacle without purpose, cruelty',
            gift='Testing readiness, strengthening resolve',
            typical_roles=[ArchetypeRole.THRESHOLD_GUARDIAN, ArchetypeRole.CHALLENGER],
            journey_phases=[JourneyPhase.CROSSING_THRESHOLD, JourneyPhase.ROAD_BACK],
            associated_symbols=['door', 'gate', 'bridge', 'sphinx'],
            voice_qualities=['questioning', 'testing', 'firm'],
            transformation_path='From obstacle to ally once passed',
            related_archetypes=['gatekeeper', 'sphinx', 'cerberus'],
            cautions=['Make test passable; not meant to block permanently'],
        ),
    }

    # Relationship mappings
    ARCHETYPE_RELATIONS = [
        ArchetypeRelation(
            'wise_elder', 'innocent',
            'complementary',
            'Elder guides innocent; innocent reminds elder of wonder',
            'Mentorship stories, wisdom transmission'
        ),
        ArchetypeRelation(
            'warrior', 'healer',
            'complementary',
            'Warrior protects healing space; healer mends warrior',
            'Protection of sacred space, healing after battle'
        ),
        ArchetypeRelation(
            'shadow', 'innocent',
            'polar',
            'Shadow holds what innocent denies; integration restores both',
            'Shadow work, reclaiming lost parts'
        ),
        ArchetypeRelation(
            'mother', 'father',
            'complementary',
            'Nurturing and structure; receptive and active',
            'Inner parenting, self-care and self-discipline'
        ),
        ArchetypeRelation(
            'anima', 'animus',
            'polar',
            'Inner feminine and masculine; integration leads to wholeness',
            'Inner marriage, sacred union'
        ),
        ArchetypeRelation(
            'trickster', 'threshold_guardian',
            'dynamic',
            'Trickster bypasses what guardian protects; creative problem solving',
            'Finding unexpected solutions, sacred mischief'
        ),
        ArchetypeRelation(
            'divine_child', 'wise_elder',
            'evolutionary',
            'Child becomes elder; elder remembers child',
            'Life cycle, potential becoming wisdom'
        ),
        ArchetypeRelation(
            'shadow', 'healer',
            'transformative',
            'Healer helps integrate shadow; shadow provides healing power',
            'Wounded healer archetype, shadow integration'
        ),
    ]

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parents[3]
        self.knowledge_path = self.project_root / 'knowledge'
        self.relationship_file = self.knowledge_path / 'archetypes' / 'relationship_graph.yaml'

        # Build indexes
        self._by_role: Dict[ArchetypeRole, List[Archetype]] = defaultdict(list)
        self._by_phase: Dict[JourneyPhase, List[Archetype]] = defaultdict(list)
        self._build_indexes()

    def _build_indexes(self):
        """Build lookup indexes."""
        for archetype in self.ARCHETYPE_DATABASE.values():
            for role in archetype.typical_roles:
                self._by_role[role].append(archetype)
            for phase in archetype.journey_phases:
                self._by_phase[phase].append(archetype)

    def get_archetype(self, name: str) -> Optional[Archetype]:
        """Get an archetype by name."""
        name_lower = name.lower().replace(' ', '_')
        return self.ARCHETYPE_DATABASE.get(name_lower)

    def get_archetypes_for_role(self, role: ArchetypeRole) -> List[Archetype]:
        """Get all archetypes suited for a particular role."""
        return self._by_role.get(role, [])

    def get_archetypes_for_phase(self, phase: JourneyPhase) -> List[Archetype]:
        """Get all archetypes suited for a journey phase."""
        return self._by_phase.get(phase, [])

    def find_related_archetypes(self, name: str) -> List[Dict[str, Any]]:
        """Find archetypes related to the given one."""
        archetype = self.get_archetype(name)
        if not archetype:
            return []

        results = []
        name_lower = name.lower().replace(' ', '_')

        for relation in self.ARCHETYPE_RELATIONS:
            if relation.archetype_a == name_lower:
                related = self.get_archetype(relation.archetype_b)
                if related:
                    results.append({
                        'archetype': related,
                        'relation_type': relation.relation_type,
                        'dynamics': relation.dynamics,
                        'narrative_potential': relation.narrative_potential,
                    })
            elif relation.archetype_b == name_lower:
                related = self.get_archetype(relation.archetype_a)
                if related:
                    results.append({
                        'archetype': related,
                        'relation_type': relation.relation_type,
                        'dynamics': relation.dynamics,
                        'narrative_potential': relation.narrative_potential,
                    })

        return results

    def suggest_cast(
        self,
        desired_outcome: str,
        journey_phases: Optional[List[JourneyPhase]] = None,
        max_archetypes: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Suggest a cast of archetypes for a journey based on outcome.

        Args:
            desired_outcome: healing, transformation, empowerment, etc.
            journey_phases: Specific phases to include
            max_archetypes: Maximum number of archetypes to suggest

        Returns:
            List of archetype suggestions with roles and rationale
        """
        outcome_mappings = {
            'healing': ['healer', 'mother', 'wise_elder', 'innocent'],
            'transformation': ['shadow', 'shapeshifter', 'threshold_guardian', 'divine_child'],
            'empowerment': ['warrior', 'father', 'animus', 'threshold_guardian'],
            'self_knowledge': ['shadow', 'anima', 'animus', 'wise_elder'],
            'relaxation': ['mother', 'healer', 'innocent'],
            'spiritual_growth': ['wise_elder', 'divine_child', 'anima', 'animus'],
            'confidence': ['warrior', 'father', 'threshold_guardian'],
            'creativity': ['trickster', 'divine_child', 'shapeshifter', 'anima'],
        }

        suggested_names = outcome_mappings.get(
            desired_outcome.lower(),
            ['wise_elder', 'healer', 'shadow']
        )

        results = []
        for name in suggested_names[:max_archetypes]:
            archetype = self.get_archetype(name)
            if archetype:
                # Suggest role based on phases
                suggested_role = archetype.typical_roles[0] if archetype.typical_roles else ArchetypeRole.GUIDE

                results.append({
                    'archetype': archetype,
                    'suggested_role': suggested_role,
                    'rationale': f"Supports {desired_outcome} through {archetype.gift}",
                    'cautions': archetype.cautions,
                })

        return results

    def check_cast_dynamics(self, archetypes: List[str]) -> Dict[str, Any]:
        """
        Analyze the dynamics of a cast of archetypes.

        Returns analysis of how they'll interact and potential issues.
        """
        if len(archetypes) < 2:
            return {'dynamics': 'single_archetype', 'issues': [], 'opportunities': []}

        archetype_objects = [self.get_archetype(name) for name in archetypes]
        archetype_objects = [a for a in archetype_objects if a is not None]

        issues = []
        opportunities = []
        dynamics = []

        # Check for known relationships
        names_lower = [name.lower().replace(' ', '_') for name in archetypes]
        for relation in self.ARCHETYPE_RELATIONS:
            if relation.archetype_a in names_lower and relation.archetype_b in names_lower:
                dynamics.append({
                    'pair': (relation.archetype_a, relation.archetype_b),
                    'type': relation.relation_type,
                    'dynamics': relation.dynamics,
                    'narrative_potential': relation.narrative_potential,
                })
                opportunities.append(relation.narrative_potential)

        # Check for potential conflicts
        has_shadow = 'shadow' in names_lower
        has_innocent = 'innocent' in names_lower
        if has_shadow and has_innocent and len(archetypes) == 2:
            issues.append("Shadow and Innocent alone may need a mediating archetype")

        # Check for role coverage
        roles_covered = set()
        for archetype in archetype_objects:
            roles_covered.update(archetype.typical_roles)

        if ArchetypeRole.GUIDE not in roles_covered:
            issues.append("No clear guide archetype - consider adding one")

        if ArchetypeRole.CHALLENGER in roles_covered and ArchetypeRole.ALLY not in roles_covered:
            issues.append("Challenger without ally may feel unsupported")

        return {
            'dynamics': dynamics,
            'issues': issues,
            'opportunities': opportunities,
            'roles_covered': [r.value for r in roles_covered],
        }

    def design_journey_cast(
        self,
        phases: List[JourneyPhase],
        desired_outcome: str
    ) -> Dict[str, Any]:
        """
        Design a complete cast for a journey.

        Args:
            phases: Journey phases to cover
            desired_outcome: Primary outcome goal

        Returns:
            Cast design with archetypes assigned to phases
        """
        cast = {}
        used_archetypes = set()

        # Get outcome-appropriate archetypes
        outcome_suggestions = self.suggest_cast(desired_outcome, phases)
        outcome_names = {s['archetype'].name.lower().replace(' ', '_') for s in outcome_suggestions}

        for phase in phases:
            phase_archetypes = self.get_archetypes_for_phase(phase)

            # Prefer outcome-appropriate archetypes that also fit the phase
            best = None
            for archetype in phase_archetypes:
                arch_key = archetype.name.lower().replace(' ', '_')
                if arch_key in outcome_names and arch_key not in used_archetypes:
                    best = archetype
                    break

            # Fallback to any suitable archetype
            if not best:
                for archetype in phase_archetypes:
                    arch_key = archetype.name.lower().replace(' ', '_')
                    if arch_key not in used_archetypes:
                        best = archetype
                        break

            if best:
                arch_key = best.name.lower().replace(' ', '_')
                cast[phase.value] = {
                    'archetype': best.name,
                    'role': best.typical_roles[0].value if best.typical_roles else 'guide',
                    'gift': best.gift,
                    'voice_qualities': best.voice_qualities,
                }
                used_archetypes.add(arch_key)

        return {
            'desired_outcome': desired_outcome,
            'cast_by_phase': cast,
            'dynamics': self.check_cast_dynamics(list(used_archetypes)),
        }

    def save_relationship_graph(self) -> Path:
        """Save the relationship graph to YAML."""
        self.relationship_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'archetype_relations': [
                {
                    'archetype_a': r.archetype_a,
                    'archetype_b': r.archetype_b,
                    'relation_type': r.relation_type,
                    'dynamics': r.dynamics,
                    'narrative_potential': r.narrative_potential,
                }
                for r in self.ARCHETYPE_RELATIONS
            ]
        }

        with open(self.relationship_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

        return self.relationship_file


# CLI interface
if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Archetype Codex')
    parser.add_argument('action', choices=['lookup', 'related', 'suggest', 'dynamics', 'design'],
                       help='Action to perform')
    parser.add_argument('--archetype', help='Archetype name')
    parser.add_argument('--outcome', help='Desired outcome')
    parser.add_argument('--archetypes', help='Comma-separated archetype names')
    parser.add_argument('--phases', help='Comma-separated journey phases')

    args = parser.parse_args()

    codex = ArchetypeCodex()

    if args.action == 'lookup' and args.archetype:
        archetype = codex.get_archetype(args.archetype)
        if archetype:
            print(json.dumps(archetype.to_dict(), indent=2))
        else:
            print(f"Archetype not found: {args.archetype}")

    elif args.action == 'related' and args.archetype:
        related = codex.find_related_archetypes(args.archetype)
        for r in related:
            print(f"\n{r['archetype'].name} ({r['relation_type']})")
            print(f"  Dynamics: {r['dynamics']}")
            print(f"  Narrative: {r['narrative_potential']}")

    elif args.action == 'suggest' and args.outcome:
        suggestions = codex.suggest_cast(args.outcome)
        for s in suggestions:
            print(f"\n{s['archetype'].name} as {s['suggested_role'].value}")
            print(f"  Rationale: {s['rationale']}")
            if s['cautions']:
                print(f"  Cautions: {', '.join(s['cautions'])}")

    elif args.action == 'dynamics' and args.archetypes:
        archetypes = args.archetypes.split(',')
        dynamics = codex.check_cast_dynamics(archetypes)
        print(json.dumps(dynamics, indent=2))

    elif args.action == 'design' and args.outcome and args.phases:
        phases = [JourneyPhase(p.strip()) for p in args.phases.split(',')]
        design = codex.design_journey_cast(phases, args.outcome)
        print(json.dumps(design, indent=2, default=str))
