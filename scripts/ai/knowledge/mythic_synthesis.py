"""
Mythic Synthesis Agent.

Blends mythologies coherently for rich, multi-layered session design.
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set, Tuple
from collections import defaultdict


@dataclass
class MythTradition:
    """Represents a mythological tradition."""
    name: str
    origin: str
    core_themes: List[str]
    cosmology: str
    key_deities: List[str]
    sacred_places: List[str]
    symbols: List[str]
    compatible_traditions: List[str]
    cautions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'origin': self.origin,
            'core_themes': self.core_themes,
            'cosmology': self.cosmology,
            'key_deities': self.key_deities,
            'sacred_places': self.sacred_places,
            'symbols': self.symbols,
            'compatible_traditions': self.compatible_traditions,
            'cautions': self.cautions,
        }


@dataclass
class MythBlend:
    """Represents a synthesized blend of mythological elements."""
    name: str
    traditions: List[str]
    unified_theme: str
    elements: Dict[str, Any]
    narrative_arc: str
    coherence_score: float
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'traditions': self.traditions,
            'unified_theme': self.unified_theme,
            'elements': self.elements,
            'narrative_arc': self.narrative_arc,
            'coherence_score': self.coherence_score,
            'warnings': self.warnings,
        }


class MythicSynthesis:
    """
    Mythic Synthesis Agent.

    Blends mythological traditions coherently, respecting
    sacred contexts while creating rich narrative tapestries.
    """

    MYTH_TRADITIONS = {
        'greek': MythTradition(
            name='Greek',
            origin='Ancient Greece',
            core_themes=['fate', 'hubris', 'transformation', 'heroic journey', 'divine intervention'],
            cosmology='Olympus above, Hades below, mortal realm between',
            key_deities=['Zeus', 'Athena', 'Apollo', 'Aphrodite', 'Hermes', 'Artemis'],
            sacred_places=['Mount Olympus', 'Delphi', 'Eleusis', 'Underworld', 'Labyrinth'],
            symbols=['lightning bolt', 'owl', 'lyre', 'caduceus', 'laurel'],
            compatible_traditions=['roman', 'egyptian', 'hermetic'],
            cautions=['Avoid trivializing; respect as living tradition for some'],
        ),
        'norse': MythTradition(
            name='Norse',
            origin='Scandinavia',
            core_themes=['fate (wyrd)', 'sacrifice', 'cosmic cycles', 'honor', 'ragnarok'],
            cosmology='Nine worlds on Yggdrasil, Asgard to Hel',
            key_deities=['Odin', 'Thor', 'Freyja', 'Frigg', 'Loki', 'Freyr'],
            sacred_places=['Yggdrasil', 'Asgard', 'Valhalla', 'Hel', 'Midgard'],
            symbols=['Mjolnir', 'ravens', 'Yggdrasil', 'runes', 'valknut'],
            compatible_traditions=['celtic', 'germanic', 'shamanic'],
            cautions=['Avoid modern misappropriation; respect as ancestor tradition'],
        ),
        'egyptian': MythTradition(
            name='Egyptian',
            origin='Ancient Egypt',
            core_themes=['death and rebirth', 'cosmic order (Ma\'at)', 'divine kingship', 'afterlife journey'],
            cosmology='Sky goddess arches over earth; Duat underworld',
            key_deities=['Ra', 'Osiris', 'Isis', 'Thoth', 'Anubis', 'Horus'],
            sacred_places=['Pyramids', 'Temple of Karnak', 'Hall of Ma\'at', 'Duat', 'Nile'],
            symbols=['ankh', 'eye of Horus', 'scarab', 'djed pillar', 'feather of Ma\'at'],
            compatible_traditions=['greek', 'hermetic', 'gnostic'],
            cautions=['Respect funerary contexts; avoid shallow exoticism'],
        ),
        'celtic': MythTradition(
            name='Celtic',
            origin='Ancient Britain, Ireland, Gaul',
            core_themes=['otherworld journeys', 'transformation', 'nature spirits', 'cycles', 'sovereignty'],
            cosmology='Three realms: land, sea, sky; Otherworld alongside',
            key_deities=['Brigid', 'Cernunnos', 'The Morrigan', 'Lugh', 'Danu'],
            sacred_places=['sacred groves', 'wells', 'sidhe mounds', 'Tir na nOg', 'stone circles'],
            symbols=['triskelion', 'oak', 'mistletoe', 'cauldron', 'salmon'],
            compatible_traditions=['norse', 'shamanic', 'druidic'],
            cautions=['Distinguish Celtic from modern interpretations'],
        ),
        'hindu': MythTradition(
            name='Hindu',
            origin='Indian subcontinent',
            core_themes=['dharma', 'karma', 'moksha', 'divine play (lila)', 'cycles of creation'],
            cosmology='Brahman as ultimate; trimurti (Brahma, Vishnu, Shiva); multiple lokas',
            key_deities=['Brahma', 'Vishnu', 'Shiva', 'Shakti', 'Ganesha', 'Krishna'],
            sacred_places=['Mount Meru', 'Ganges', 'temples', 'chakras within body'],
            symbols=['om', 'lotus', 'trishula', 'conch', 'wheel'],
            compatible_traditions=['buddhist', 'yogic', 'tantric'],
            cautions=['Living tradition - approach with deep respect; avoid appropriation'],
        ),
        'buddhist': MythTradition(
            name='Buddhist',
            origin='Indian subcontinent, spread across Asia',
            core_themes=['suffering and liberation', 'emptiness', 'compassion', 'enlightenment', 'impermanence'],
            cosmology='Wheel of samsara; pure lands; buddha realms',
            key_deities=['Buddha', 'Avalokiteshvara', 'Tara', 'Manjushri', 'Amitabha'],
            sacred_places=['Bodhi tree', 'pure lands', 'stupas', 'monastery'],
            symbols=['lotus', 'wheel', 'bodhi tree', 'empty throne', 'endless knot'],
            compatible_traditions=['hindu', 'taoist', 'tibetan'],
            cautions=['Respect contemplative depth; avoid superficial use'],
        ),
        'christian': MythTradition(
            name='Christian',
            origin='Middle East, spread globally',
            core_themes=['redemption', 'grace', 'incarnation', 'resurrection', 'divine love'],
            cosmology='Heaven, earth, resurrection; Kingdom of God',
            key_deities=['God (Trinity)', 'Christ', 'Holy Spirit', 'Mary', 'angels'],
            sacred_places=['Jerusalem', 'garden (Eden)', 'wilderness', 'mountain (Sinai, Tabor)', 'heaven'],
            symbols=['cross', 'fish', 'dove', 'lamb', 'bread and wine', 'light'],
            compatible_traditions=['jewish', 'gnostic', 'hermetic'],
            cautions=['Highly sacred for billions; use with reverence; avoid syncretism that offends'],
        ),
        'jewish': MythTradition(
            name='Jewish',
            origin='Middle East',
            core_themes=['covenant', 'exile and return', 'law and grace', 'sacred history', 'tikkun olam'],
            cosmology='Creation from word; angelic hierarchies; world to come',
            key_deities=['YHWH', 'Shekinah', 'angels (Michael, Gabriel)'],
            sacred_places=['Temple', 'Sinai', 'burning bush', 'promised land'],
            symbols=['menorah', 'star of David', 'Torah scroll', 'shofar'],
            compatible_traditions=['christian', 'kabbalistic', 'islamic'],
            cautions=['Living tradition - deep respect required; avoid appropriation'],
        ),
        'shamanic': MythTradition(
            name='Shamanic',
            origin='Various indigenous traditions worldwide',
            core_themes=['spirit journey', 'healing', 'nature connection', 'power animals', 'world tree'],
            cosmology='Upper, middle, lower worlds; spirit realms',
            key_deities=['Great Spirit', 'power animals', 'ancestors', 'nature spirits'],
            sacred_places=['world tree', 'sacred mountain', 'cave', 'fire circle'],
            symbols=['drum', 'feather', 'medicine wheel', 'bones', 'animal totems'],
            compatible_traditions=['norse', 'celtic', 'native american'],
            cautions=['Many living traditions - do not appropriate specific indigenous practices'],
        ),
        'hermetic': MythTradition(
            name='Hermetic',
            origin='Greco-Egyptian synthesis',
            core_themes=['as above so below', 'transformation', 'divine mind', 'correspondences'],
            cosmology='Emanation from One; planetary spheres; microcosm/macrocosm',
            key_deities=['Hermes Trismegistus', 'planetary intelligences'],
            sacred_places=['temple of wisdom', 'chamber of initiation'],
            symbols=['caduceus', 'emerald tablet', 'ouroboros', 'hexagram'],
            compatible_traditions=['greek', 'egyptian', 'kabbalistic', 'alchemical'],
            cautions=['Esoteric tradition - ensure coherent understanding'],
        ),
        'gnostic': MythTradition(
            name='Gnostic',
            origin='Early Christian era, Middle East',
            core_themes=['divine spark', 'liberation from matter', 'sophia', 'pleroma', 'gnosis'],
            cosmology='Pleroma (fullness) above; material realm as shadow; spark within',
            key_deities=['Sophia', 'Christ as revealer', 'Aeons', 'True God'],
            sacred_places=['pleroma', 'bridal chamber', 'treasury of light'],
            symbols=['pearl', 'light', 'mirror', 'seed'],
            compatible_traditions=['christian', 'hermetic', 'neoplatonic'],
            cautions=['Complex theology - represent accurately; not orthodox Christian'],
        ),
    }

    # Synthesis rules for blending traditions
    SYNTHESIS_RULES = {
        'universal_themes': [
            'journey/return', 'death/rebirth', 'sacred marriage',
            'descent to underworld', 'ascent to heaven', 'transformation',
            'encounter with divine', 'restoration of wholeness',
        ],
        'compatible_cosmologies': {
            'vertical': ['greek', 'norse', 'hermetic', 'christian', 'jewish', 'gnostic'],
            'cyclical': ['hindu', 'buddhist', 'celtic'],
            'shamanic_worlds': ['shamanic', 'norse', 'celtic'],
        },
        'forbidden_blends': [
            # Pairs that shouldn't be casually mixed
            ('christian', 'satanic'),  # Obviously
            ('jewish', 'nazi_symbols'),  # Obviously
        ],
        'requires_care': [
            ('christian', 'pagan'),
            ('hindu', 'buddhist'),  # Different ultimate goals
            ('indigenous', 'any'),  # Appropriation concerns
        ],
    }

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parents[3]
        self.knowledge_path = self.project_root / 'knowledge'

    def get_tradition(self, name: str) -> Optional[MythTradition]:
        """Get a mythological tradition by name."""
        return self.MYTH_TRADITIONS.get(name.lower())

    def find_common_themes(self, traditions: List[str]) -> List[str]:
        """Find themes common across multiple traditions."""
        if not traditions:
            return []

        theme_sets = []
        for trad_name in traditions:
            trad = self.get_tradition(trad_name)
            if trad:
                theme_sets.append(set(trad.core_themes))

        if not theme_sets:
            return []

        # Find intersection
        common = theme_sets[0]
        for theme_set in theme_sets[1:]:
            common = common & theme_set

        return list(common)

    def check_compatibility(self, traditions: List[str]) -> Dict[str, Any]:
        """
        Check if traditions can be blended coherently.

        Returns compatibility analysis with score and warnings.
        """
        if len(traditions) < 2:
            return {'compatible': True, 'score': 1.0, 'warnings': []}

        warnings = []
        score = 1.0

        tradition_objects = [self.get_tradition(t) for t in traditions]
        tradition_objects = [t for t in tradition_objects if t is not None]

        if len(tradition_objects) < len(traditions):
            warnings.append("Some traditions not found in database")
            score -= 0.1

        # Check explicit compatibility
        for i, trad1 in enumerate(tradition_objects):
            for trad2 in tradition_objects[i+1:]:
                trad1_name = trad1.name.lower()
                trad2_name = trad2.name.lower()

                # Check if explicitly compatible
                if trad2_name not in [t.lower() for t in trad1.compatible_traditions]:
                    if trad1_name not in [t.lower() for t in trad2.compatible_traditions]:
                        warnings.append(f"{trad1.name} and {trad2.name} not explicitly compatible")
                        score -= 0.15

        # Check for 'requires care' combinations
        trad_names_lower = [t.lower() for t in traditions]
        for pair in self.SYNTHESIS_RULES['requires_care']:
            if pair[0] in trad_names_lower:
                if pair[1] == 'any' or pair[1] in trad_names_lower:
                    warnings.append(f"Combining {pair[0]} with other traditions requires cultural sensitivity")
                    score -= 0.1

        # Collect all cautions
        for trad in tradition_objects:
            for caution in trad.cautions:
                if caution not in warnings:
                    warnings.append(f"{trad.name}: {caution}")

        return {
            'compatible': score >= 0.6,
            'score': max(0, score),
            'warnings': warnings,
            'common_themes': self.find_common_themes(traditions),
        }

    def find_bridging_elements(self, tradition_a: str, tradition_b: str) -> Dict[str, Any]:
        """Find elements that can bridge two traditions."""
        trad_a = self.get_tradition(tradition_a)
        trad_b = self.get_tradition(tradition_b)

        if not trad_a or not trad_b:
            return {'bridges': [], 'shared_symbols': [], 'shared_places': []}

        # Find shared or similar symbols
        symbols_a = set(s.lower() for s in trad_a.symbols)
        symbols_b = set(s.lower() for s in trad_b.symbols)
        shared_symbols = symbols_a & symbols_b

        # Find shared themes
        themes_a = set(t.lower() for t in trad_a.core_themes)
        themes_b = set(t.lower() for t in trad_b.core_themes)
        shared_themes = themes_a & themes_b

        # Find bridging deities/figures
        bridging_figures = []
        if 'hermetic' in [tradition_a.lower(), tradition_b.lower()]:
            if 'greek' in [tradition_a.lower(), tradition_b.lower()]:
                bridging_figures.append('Hermes/Thoth - messenger between realms')
            if 'egyptian' in [tradition_a.lower(), tradition_b.lower()]:
                bridging_figures.append('Thoth - wisdom keeper')

        # Universal bridges
        universal_bridges = [
            'Tree of Life / World Tree - universal axis mundi',
            'Sacred Mountain - meeting place of heaven and earth',
            'Water/River - purification and transition',
            'Light/Sun - divine presence',
            'Guide/Psychopomp - journey companion',
        ]

        return {
            'shared_symbols': list(shared_symbols),
            'shared_themes': list(shared_themes),
            'bridging_figures': bridging_figures,
            'universal_bridges': universal_bridges,
        }

    def synthesize(
        self,
        traditions: List[str],
        desired_theme: str,
        desired_outcome: str
    ) -> MythBlend:
        """
        Create a coherent synthesis of mythological traditions.

        Args:
            traditions: List of tradition names to blend
            desired_theme: Central theme for the synthesis
            desired_outcome: Desired transformation outcome

        Returns:
            MythBlend with synthesized elements
        """
        compatibility = self.check_compatibility(traditions)
        warnings = compatibility['warnings'].copy()

        # Gather elements from each tradition
        elements = {
            'deities': [],
            'places': [],
            'symbols': [],
            'themes': [],
        }

        for trad_name in traditions:
            trad = self.get_tradition(trad_name)
            if trad:
                # Select most relevant elements for the theme
                elements['deities'].extend(trad.key_deities[:2])
                elements['places'].extend(trad.sacred_places[:2])
                elements['symbols'].extend(trad.symbols[:3])
                elements['themes'].extend(trad.core_themes[:2])

        # Remove duplicates while preserving order
        for key in elements:
            elements[key] = list(dict.fromkeys(elements[key]))

        # Design narrative arc based on universal themes
        universal_themes = self.SYNTHESIS_RULES['universal_themes']
        matching_themes = [t for t in universal_themes if t.lower() in desired_theme.lower()]

        if matching_themes:
            narrative_arc = f"Journey of {matching_themes[0]} through {' and '.join(traditions)}"
        else:
            narrative_arc = f"Quest for {desired_outcome} drawing from {' and '.join(traditions)}"

        # Generate unified theme
        common = self.find_common_themes(traditions)
        if common:
            unified_theme = f"{desired_theme}, united by {common[0]}"
        else:
            unified_theme = f"{desired_theme}, bridged by universal symbols"

        # Calculate coherence
        coherence = compatibility['score']
        if len(common) >= 2:
            coherence += 0.1
        if desired_theme.lower() in str(universal_themes).lower():
            coherence += 0.1
        coherence = min(1.0, coherence)

        return MythBlend(
            name=f"{desired_theme.replace(' ', '_').lower()}_synthesis",
            traditions=traditions,
            unified_theme=unified_theme,
            elements=elements,
            narrative_arc=narrative_arc,
            coherence_score=coherence,
            warnings=warnings,
        )

    def suggest_synthesis_for_outcome(
        self,
        desired_outcome: str,
        max_traditions: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Suggest tradition blends suited to a desired outcome.

        Args:
            desired_outcome: healing, transformation, empowerment, etc.
            max_traditions: Maximum traditions to blend

        Returns:
            List of suggested blends with rationale
        """
        outcome_mappings = {
            'healing': ['shamanic', 'greek', 'egyptian'],
            'transformation': ['egyptian', 'alchemical', 'gnostic'],
            'empowerment': ['norse', 'greek', 'hindu'],
            'spiritual_growth': ['christian', 'buddhist', 'hermetic'],
            'self_knowledge': ['gnostic', 'hermetic', 'buddhist'],
            'relaxation': ['buddhist', 'celtic', 'hindu'],
            'confidence': ['norse', 'greek', 'celtic'],
            'creativity': ['celtic', 'greek', 'shamanic'],
        }

        suggested = outcome_mappings.get(desired_outcome.lower(), ['greek', 'hermetic'])
        suggestions = []

        # Single tradition option
        for trad_name in suggested[:2]:
            trad = self.get_tradition(trad_name)
            if trad:
                suggestions.append({
                    'traditions': [trad_name],
                    'rationale': f"{trad.name} mythology supports {desired_outcome} through themes of {', '.join(trad.core_themes[:2])}",
                    'coherence': 1.0,
                })

        # Blend option
        if len(suggested) >= 2 and max_traditions >= 2:
            blend = self.synthesize(suggested[:2], desired_outcome, desired_outcome)
            suggestions.append({
                'traditions': suggested[:2],
                'rationale': f"Blend of {' and '.join(suggested[:2])} creates rich {desired_outcome} narrative",
                'coherence': blend.coherence_score,
                'blend': blend,
            })

        return suggestions

    def design_mythic_journey(
        self,
        traditions: List[str],
        theme: str,
        outcome: str,
        duration_minutes: int = 25
    ) -> Dict[str, Any]:
        """
        Design a complete mythic journey structure.

        Returns detailed journey design with tradition elements.
        """
        synthesis = self.synthesize(traditions, theme, outcome)

        # Design phases
        phases = []

        # Opening - establish setting
        phases.append({
            'name': 'Threshold',
            'duration': 3,
            'mythic_element': f"Standing at the gates of {synthesis.elements['places'][0] if synthesis.elements['places'] else 'the sacred realm'}",
            'purpose': 'Establish sacred container',
        })

        # Descent/Journey
        phases.append({
            'name': 'Journey',
            'duration': int(duration_minutes * 0.5),
            'mythic_element': f"Guided by {synthesis.elements['deities'][0] if synthesis.elements['deities'] else 'ancient wisdom'}",
            'purpose': 'Main mythic narrative',
            'symbols': synthesis.elements['symbols'][:3],
        })

        # Encounter
        phases.append({
            'name': 'Encounter',
            'duration': int(duration_minutes * 0.25),
            'mythic_element': f"Meeting with {synthesis.elements['deities'][1] if len(synthesis.elements['deities']) > 1 else 'the divine presence'}",
            'purpose': 'Transformative encounter',
        })

        # Integration
        phases.append({
            'name': 'Return',
            'duration': int(duration_minutes * 0.15),
            'mythic_element': f"Carrying the gift of {outcome}",
            'purpose': 'Integration and grounding',
        })

        return {
            'synthesis': synthesis.to_dict(),
            'phases': phases,
            'total_duration': duration_minutes,
            'narrative_arc': synthesis.narrative_arc,
            'warnings': synthesis.warnings,
        }


# CLI interface
if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Mythic Synthesis')
    parser.add_argument('action', choices=['info', 'compatibility', 'bridge', 'synthesize', 'suggest', 'design'],
                       help='Action to perform')
    parser.add_argument('--tradition', help='Single tradition name')
    parser.add_argument('--traditions', help='Comma-separated tradition names')
    parser.add_argument('--theme', help='Desired theme')
    parser.add_argument('--outcome', help='Desired outcome')
    parser.add_argument('--duration', type=int, default=25, help='Journey duration in minutes')

    args = parser.parse_args()

    synth = MythicSynthesis()

    if args.action == 'info' and args.tradition:
        trad = synth.get_tradition(args.tradition)
        if trad:
            print(json.dumps(trad.to_dict(), indent=2))
        else:
            print(f"Tradition not found: {args.tradition}")
            print(f"Available: {', '.join(synth.MYTH_TRADITIONS.keys())}")

    elif args.action == 'compatibility' and args.traditions:
        traditions = [t.strip() for t in args.traditions.split(',')]
        result = synth.check_compatibility(traditions)
        print(json.dumps(result, indent=2))

    elif args.action == 'bridge' and args.traditions:
        traditions = [t.strip() for t in args.traditions.split(',')]
        if len(traditions) >= 2:
            result = synth.find_bridging_elements(traditions[0], traditions[1])
            print(json.dumps(result, indent=2))

    elif args.action == 'synthesize' and args.traditions and args.theme and args.outcome:
        traditions = [t.strip() for t in args.traditions.split(',')]
        blend = synth.synthesize(traditions, args.theme, args.outcome)
        print(json.dumps(blend.to_dict(), indent=2))

    elif args.action == 'suggest' and args.outcome:
        suggestions = synth.suggest_synthesis_for_outcome(args.outcome)
        for s in suggestions:
            print(f"\nTraditions: {', '.join(s['traditions'])}")
            print(f"  Rationale: {s['rationale']}")
            print(f"  Coherence: {s['coherence']:.2f}")

    elif args.action == 'design' and args.traditions and args.theme and args.outcome:
        traditions = [t.strip() for t in args.traditions.split(',')]
        design = synth.design_mythic_journey(traditions, args.theme, args.outcome, args.duration)
        print(json.dumps(design, indent=2))
