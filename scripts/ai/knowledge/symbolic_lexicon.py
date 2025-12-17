"""
Symbolic Lexicon Agent.

Cross-references symbols across spiritual traditions for coherent session design.
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set
from collections import defaultdict


@dataclass
class Symbol:
    """Represents a symbol with cross-tradition mappings."""
    name: str
    tradition: str
    meaning: str
    associations: List[str] = field(default_factory=list)
    elements: List[str] = field(default_factory=list)
    colors: List[str] = field(default_factory=list)
    archetypes: List[str] = field(default_factory=list)
    related_symbols: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'tradition': self.tradition,
            'meaning': self.meaning,
            'associations': self.associations,
            'elements': self.elements,
            'colors': self.colors,
            'archetypes': self.archetypes,
            'related_symbols': self.related_symbols,
        }


@dataclass
class SymbolRelation:
    """Represents a relationship between symbols across traditions."""
    symbol_a: str
    tradition_a: str
    symbol_b: str
    tradition_b: str
    relation_type: str  # equivalent, complementary, opposing, derivative
    strength: float  # 0-1
    notes: str = ""


class SymbolicLexicon:
    """
    Symbolic Lexicon Agent.

    Provides cross-tradition symbol lookup, relationship mapping,
    and coherence checking for session design.
    """

    # Core symbol database organized by tradition
    SYMBOL_DATABASE = {
        'alchemy': {
            'gold': Symbol(
                name='Gold',
                tradition='alchemy',
                meaning='Spiritual perfection, enlightenment, the Great Work completed',
                associations=['sun', 'consciousness', 'immortality'],
                elements=['fire'],
                colors=['gold', 'yellow'],
                archetypes=['Philosopher', 'Adept'],
                related_symbols=['Sol', 'Philosopher\'s Stone'],
            ),
            'silver': Symbol(
                name='Silver',
                tradition='alchemy',
                meaning='Lunar consciousness, intuition, purification',
                associations=['moon', 'feminine', 'reflection'],
                elements=['water'],
                colors=['silver', 'white'],
                archetypes=['Priestess', 'Seer'],
                related_symbols=['Luna', 'Mercury'],
            ),
            'mercury': Symbol(
                name='Mercury',
                tradition='alchemy',
                meaning='Transformation, communication, the messenger',
                associations=['quicksilver', 'fluidity', 'bridge'],
                elements=['water', 'air'],
                colors=['silver', 'iridescent'],
                archetypes=['Messenger', 'Trickster'],
                related_symbols=['Hermes', 'Thoth'],
            ),
            'sulfur': Symbol(
                name='Sulfur',
                tradition='alchemy',
                meaning='Active principle, will, masculine energy',
                associations=['fire', 'desire', 'animation'],
                elements=['fire'],
                colors=['yellow', 'red'],
                archetypes=['Warrior', 'Creator'],
                related_symbols=['Sol', 'Fire'],
            ),
            'salt': Symbol(
                name='Salt',
                tradition='alchemy',
                meaning='Body, matter, crystallization, preservation',
                associations=['earth', 'stability', 'purification'],
                elements=['earth'],
                colors=['white', 'grey'],
                archetypes=['Guardian', 'Preserver'],
                related_symbols=['Earth', 'Crystal'],
            ),
        },
        'kabbalah': {
            'kether': Symbol(
                name='Kether',
                tradition='kabbalah',
                meaning='Crown, divine will, source of all',
                associations=['unity', 'primordial point', 'pure being'],
                elements=['spirit'],
                colors=['white', 'brilliant'],
                archetypes=['Ancient of Days', 'Source'],
                related_symbols=['Crown', 'Point'],
            ),
            'chokmah': Symbol(
                name='Chokmah',
                tradition='kabbalah',
                meaning='Wisdom, masculine principle, dynamic force',
                associations=['father', 'zodiac', 'yod'],
                elements=['fire'],
                colors=['grey', 'silver'],
                archetypes=['Father', 'Wise One'],
                related_symbols=['Abba', 'Stars'],
            ),
            'binah': Symbol(
                name='Binah',
                tradition='kabbalah',
                meaning='Understanding, feminine principle, form',
                associations=['mother', 'throne', 'sea'],
                elements=['water'],
                colors=['black', 'indigo'],
                archetypes=['Mother', 'Crone'],
                related_symbols=['Aima', 'Saturn'],
            ),
            'tiphareth': Symbol(
                name='Tiphareth',
                tradition='kabbalah',
                meaning='Beauty, harmony, the self, Christ consciousness',
                associations=['sun', 'heart', 'sacrifice'],
                elements=['fire', 'air'],
                colors=['gold', 'yellow'],
                archetypes=['Sacrificed God', 'Healer'],
                related_symbols=['Sun', 'Heart'],
            ),
            'malkuth': Symbol(
                name='Malkuth',
                tradition='kabbalah',
                meaning='Kingdom, physical world, manifestation',
                associations=['earth', 'bride', 'completion'],
                elements=['earth'],
                colors=['russet', 'olive', 'citrine', 'black'],
                archetypes=['Queen', 'Bride'],
                related_symbols=['Earth', 'Temple'],
            ),
        },
        'tarot': {
            'fool': Symbol(
                name='The Fool',
                tradition='tarot',
                meaning='Beginnings, innocence, leap of faith',
                associations=['zero', 'potential', 'journey'],
                elements=['air'],
                colors=['white', 'yellow'],
                archetypes=['Fool', 'Innocent'],
                related_symbols=['Aleph', 'Spirit'],
            ),
            'magician': Symbol(
                name='The Magician',
                tradition='tarot',
                meaning='Will, manifestation, skill, power',
                associations=['one', 'mercury', 'tools'],
                elements=['all four'],
                colors=['red', 'white'],
                archetypes=['Magician', 'Creator'],
                related_symbols=['Beth', 'Mercury'],
            ),
            'high_priestess': Symbol(
                name='The High Priestess',
                tradition='tarot',
                meaning='Intuition, mystery, the unconscious',
                associations=['moon', 'veil', 'hidden knowledge'],
                elements=['water'],
                colors=['blue', 'silver'],
                archetypes=['Priestess', 'Oracle'],
                related_symbols=['Gimel', 'Moon'],
            ),
            'empress': Symbol(
                name='The Empress',
                tradition='tarot',
                meaning='Abundance, nature, fertility, nurturing',
                associations=['venus', 'garden', 'mother'],
                elements=['earth'],
                colors=['green', 'pink'],
                archetypes=['Mother', 'Nurturer'],
                related_symbols=['Daleth', 'Venus'],
            ),
            'tower': Symbol(
                name='The Tower',
                tradition='tarot',
                meaning='Sudden change, revelation, breaking down',
                associations=['lightning', 'destruction', 'awakening'],
                elements=['fire'],
                colors=['red', 'black', 'orange'],
                archetypes=['Destroyer', 'Liberator'],
                related_symbols=['Peh', 'Mars'],
            ),
        },
        'christian': {
            'cross': Symbol(
                name='Cross',
                tradition='christian',
                meaning='Sacrifice, redemption, intersection of divine and human',
                associations=['crucifixion', 'salvation', 'faith'],
                elements=['all four'],
                colors=['gold', 'red', 'white'],
                archetypes=['Redeemer', 'Sacrificed King'],
                related_symbols=['Tree of Life', 'Ankh'],
            ),
            'dove': Symbol(
                name='Dove',
                tradition='christian',
                meaning='Holy Spirit, peace, purity, divine messenger',
                associations=['baptism', 'spirit', 'noah'],
                elements=['air'],
                colors=['white', 'gold'],
                archetypes=['Spirit', 'Messenger'],
                related_symbols=['Bird', 'Wing'],
            ),
            'lamb': Symbol(
                name='Lamb',
                tradition='christian',
                meaning='Innocence, sacrifice, Christ as savior',
                associations=['passover', 'blood', 'redemption'],
                elements=['earth'],
                colors=['white', 'red'],
                archetypes=['Innocent', 'Sacrifice'],
                related_symbols=['Ram', 'Shepherd'],
            ),
        },
        'egyptian': {
            'ankh': Symbol(
                name='Ankh',
                tradition='egyptian',
                meaning='Life, immortality, divine breath',
                associations=['breath', 'eternity', 'gods'],
                elements=['air', 'spirit'],
                colors=['gold', 'turquoise'],
                archetypes=['Life-Giver', 'Immortal'],
                related_symbols=['Cross', 'Key'],
            ),
            'eye_of_horus': Symbol(
                name='Eye of Horus',
                tradition='egyptian',
                meaning='Protection, healing, restoration, royal power',
                associations=['falcon', 'moon', 'wholeness'],
                elements=['air', 'fire'],
                colors=['blue', 'gold'],
                archetypes=['Protector', 'Healer'],
                related_symbols=['Third Eye', 'All-Seeing Eye'],
            ),
            'scarab': Symbol(
                name='Scarab',
                tradition='egyptian',
                meaning='Rebirth, transformation, solar resurrection',
                associations=['khepri', 'dawn', 'rolling sun'],
                elements=['earth', 'fire'],
                colors=['black', 'gold', 'blue'],
                archetypes=['Transformer', 'Sun-Bringer'],
                related_symbols=['Beetle', 'Sun Disk'],
            ),
        },
    }

    # Cross-tradition equivalences
    CROSS_TRADITION_MAP = [
        SymbolRelation('gold', 'alchemy', 'tiphareth', 'kabbalah', 'equivalent', 0.9,
                      'Both represent solar consciousness and spiritual perfection'),
        SymbolRelation('silver', 'alchemy', 'binah', 'kabbalah', 'complementary', 0.8,
                      'Both represent lunar/feminine receptive principle'),
        SymbolRelation('mercury', 'alchemy', 'magician', 'tarot', 'equivalent', 0.95,
                      'Mercury/Hermes correspondence'),
        SymbolRelation('kether', 'kabbalah', 'fool', 'tarot', 'equivalent', 0.9,
                      'Pure potential and divine unity'),
        SymbolRelation('cross', 'christian', 'tiphareth', 'kabbalah', 'equivalent', 0.85,
                      'Sacrifice and redemption at heart center'),
        SymbolRelation('ankh', 'egyptian', 'cross', 'christian', 'derivative', 0.7,
                      'Both represent life and divine intersection'),
        SymbolRelation('eye_of_horus', 'egyptian', 'high_priestess', 'tarot', 'complementary', 0.75,
                      'Both represent inner sight and hidden knowledge'),
        SymbolRelation('scarab', 'egyptian', 'tower', 'tarot', 'complementary', 0.6,
                      'Both involve transformation through destruction/rebirth'),
    ]

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parents[3]
        self.knowledge_path = self.project_root / 'knowledge'
        self.cross_tradition_file = self.knowledge_path / 'symbols' / 'cross_tradition_map.yaml'

        # Build indexes
        self._symbol_by_name: Dict[str, List[Symbol]] = defaultdict(list)
        self._symbol_by_element: Dict[str, List[Symbol]] = defaultdict(list)
        self._symbol_by_archetype: Dict[str, List[Symbol]] = defaultdict(list)
        self._build_indexes()

    def _build_indexes(self):
        """Build lookup indexes for efficient queries."""
        for tradition, symbols in self.SYMBOL_DATABASE.items():
            for key, symbol in symbols.items():
                self._symbol_by_name[symbol.name.lower()].append(symbol)
                for element in symbol.elements:
                    self._symbol_by_element[element.lower()].append(symbol)
                for archetype in symbol.archetypes:
                    self._symbol_by_archetype[archetype.lower()].append(symbol)

    def get_symbol(self, name: str, tradition: Optional[str] = None) -> Optional[Symbol]:
        """Get a symbol by name, optionally filtered by tradition."""
        name_lower = name.lower()

        # Try exact match in specific tradition
        if tradition:
            trad_symbols = self.SYMBOL_DATABASE.get(tradition.lower(), {})
            for key, symbol in trad_symbols.items():
                if symbol.name.lower() == name_lower or key == name_lower:
                    return symbol

        # Search all traditions
        matches = self._symbol_by_name.get(name_lower, [])
        return matches[0] if matches else None

    def find_symbols_by_element(self, element: str) -> List[Symbol]:
        """Find all symbols associated with an element."""
        return self._symbol_by_element.get(element.lower(), [])

    def find_symbols_by_archetype(self, archetype: str) -> List[Symbol]:
        """Find all symbols associated with an archetype."""
        return self._symbol_by_archetype.get(archetype.lower(), [])

    def find_cross_tradition_equivalents(self, symbol_name: str, tradition: str) -> List[Dict[str, Any]]:
        """Find equivalent or related symbols in other traditions."""
        results = []
        symbol_lower = symbol_name.lower()
        tradition_lower = tradition.lower()

        for relation in self.CROSS_TRADITION_MAP:
            if (relation.symbol_a == symbol_lower and relation.tradition_a == tradition_lower):
                target = self.get_symbol(relation.symbol_b, relation.tradition_b)
                if target:
                    results.append({
                        'symbol': target,
                        'relation_type': relation.relation_type,
                        'strength': relation.strength,
                        'notes': relation.notes,
                    })
            elif (relation.symbol_b == symbol_lower and relation.tradition_b == tradition_lower):
                target = self.get_symbol(relation.symbol_a, relation.tradition_a)
                if target:
                    results.append({
                        'symbol': target,
                        'relation_type': relation.relation_type,
                        'strength': relation.strength,
                        'notes': relation.notes,
                    })

        return sorted(results, key=lambda x: x['strength'], reverse=True)

    def check_symbol_coherence(self, symbols: List[tuple]) -> Dict[str, Any]:
        """
        Check if a set of symbols forms a coherent symbolic language.

        Args:
            symbols: List of (name, tradition) tuples

        Returns:
            Coherence analysis with score and recommendations
        """
        if len(symbols) < 2:
            return {'coherent': True, 'score': 1.0, 'issues': [], 'recommendations': []}

        symbol_objects = []
        for name, tradition in symbols:
            symbol = self.get_symbol(name, tradition)
            if symbol:
                symbol_objects.append(symbol)

        if len(symbol_objects) < 2:
            return {'coherent': True, 'score': 1.0, 'issues': [], 'recommendations': []}

        issues = []
        recommendations = []
        score = 1.0

        # Check element coherence
        all_elements = set()
        for s in symbol_objects:
            all_elements.update(s.elements)

        if len(all_elements) > 3:
            issues.append(f"Too many elements ({len(all_elements)}): may dilute focus")
            score -= 0.1

        # Check for opposing elements without resolution
        opposing = [
            ('fire', 'water'),
            ('earth', 'air'),
        ]
        for e1, e2 in opposing:
            if e1 in all_elements and e2 in all_elements:
                # Check if there's a bridging element
                if 'spirit' not in all_elements:
                    issues.append(f"Opposing elements {e1}/{e2} without unifying spirit element")
                    recommendations.append(f"Consider adding a spirit/transcendence symbol to bridge {e1}/{e2}")
                    score -= 0.15

        # Check archetype coherence
        all_archetypes = set()
        for s in symbol_objects:
            all_archetypes.update(a.lower() for a in s.archetypes)

        # Flag potential conflicts
        conflict_archetypes = [
            ('destroyer', 'preserver'),
            ('innocent', 'trickster'),
        ]
        for a1, a2 in conflict_archetypes:
            if a1 in all_archetypes and a2 in all_archetypes:
                issues.append(f"Potentially conflicting archetypes: {a1}/{a2}")
                recommendations.append(f"Ensure narrative journey shows transformation between {a1} and {a2}")
                score -= 0.1

        # Check for cross-tradition relations
        traditions_used = set(s.tradition for s in symbol_objects)
        if len(traditions_used) > 1:
            # Check if there are known relations
            has_relations = False
            for i, s1 in enumerate(symbol_objects):
                for s2 in symbol_objects[i+1:]:
                    if s1.tradition != s2.tradition:
                        relations = self.find_cross_tradition_equivalents(
                            s1.name.lower().replace(' ', '_'),
                            s1.tradition
                        )
                        for rel in relations:
                            if rel['symbol'].name.lower() == s2.name.lower():
                                has_relations = True
                                break

            if not has_relations and len(traditions_used) > 2:
                issues.append("Multiple traditions without established symbolic bridges")
                recommendations.append("Consider adding symbols that bridge traditions (e.g., Mercury/Hermes)")
                score -= 0.15

        return {
            'coherent': score >= 0.7,
            'score': max(0, score),
            'issues': issues,
            'recommendations': recommendations,
            'elements_used': list(all_elements),
            'archetypes_used': list(all_archetypes),
            'traditions_used': list(traditions_used),
        }

    def suggest_complementary_symbols(
        self,
        symbol_name: str,
        tradition: str,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """Suggest symbols that complement the given symbol."""
        symbol = self.get_symbol(symbol_name, tradition)
        if not symbol:
            return []

        suggestions = []

        # Same tradition, complementary elements
        trad_symbols = self.SYMBOL_DATABASE.get(tradition.lower(), {})
        for key, candidate in trad_symbols.items():
            if candidate.name == symbol.name:
                continue

            score = 0
            reasons = []

            # Shared elements
            shared_elements = set(symbol.elements) & set(candidate.elements)
            if shared_elements:
                score += 0.3
                reasons.append(f"Shared element: {', '.join(shared_elements)}")

            # Complementary archetypes
            shared_archetypes = set(a.lower() for a in symbol.archetypes) & \
                               set(a.lower() for a in candidate.archetypes)
            if shared_archetypes:
                score += 0.3
                reasons.append(f"Shared archetype: {', '.join(shared_archetypes)}")

            # Related symbols
            if any(r.lower() in candidate.name.lower() for r in symbol.related_symbols):
                score += 0.2
                reasons.append("Directly related symbol")

            if score > 0:
                suggestions.append({
                    'symbol': candidate,
                    'score': score,
                    'reasons': reasons,
                })

        # Cross-tradition equivalents
        for equiv in self.find_cross_tradition_equivalents(symbol_name, tradition):
            suggestions.append({
                'symbol': equiv['symbol'],
                'score': equiv['strength'] * 0.8,
                'reasons': [f"Cross-tradition {equiv['relation_type']}: {equiv['notes']}"],
            })

        # Sort and limit
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        return suggestions[:count]

    def get_all_symbols(self, tradition: Optional[str] = None) -> List[Symbol]:
        """Get all symbols, optionally filtered by tradition."""
        if tradition:
            trad_symbols = self.SYMBOL_DATABASE.get(tradition.lower(), {})
            return list(trad_symbols.values())

        all_symbols = []
        for symbols in self.SYMBOL_DATABASE.values():
            all_symbols.extend(symbols.values())
        return all_symbols

    def save_cross_tradition_map(self) -> Path:
        """Save the cross-tradition map to YAML."""
        self.cross_tradition_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'cross_tradition_relations': [
                {
                    'symbol_a': r.symbol_a,
                    'tradition_a': r.tradition_a,
                    'symbol_b': r.symbol_b,
                    'tradition_b': r.tradition_b,
                    'relation_type': r.relation_type,
                    'strength': r.strength,
                    'notes': r.notes,
                }
                for r in self.CROSS_TRADITION_MAP
            ]
        }

        with open(self.cross_tradition_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

        return self.cross_tradition_file


# CLI interface
if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Symbolic Lexicon')
    parser.add_argument('action', choices=['lookup', 'equivalents', 'coherence', 'suggest', 'list'],
                       help='Action to perform')
    parser.add_argument('--symbol', help='Symbol name')
    parser.add_argument('--tradition', help='Tradition name')
    parser.add_argument('--symbols', help='Comma-separated symbol:tradition pairs for coherence check')

    args = parser.parse_args()

    lexicon = SymbolicLexicon()

    if args.action == 'lookup' and args.symbol:
        symbol = lexicon.get_symbol(args.symbol, args.tradition)
        if symbol:
            print(json.dumps(symbol.to_dict(), indent=2))
        else:
            print(f"Symbol not found: {args.symbol}")

    elif args.action == 'equivalents' and args.symbol and args.tradition:
        equivs = lexicon.find_cross_tradition_equivalents(args.symbol, args.tradition)
        for equiv in equivs:
            print(f"{equiv['symbol'].tradition}: {equiv['symbol'].name}")
            print(f"  Type: {equiv['relation_type']}, Strength: {equiv['strength']}")
            print(f"  Notes: {equiv['notes']}")

    elif args.action == 'coherence' and args.symbols:
        pairs = [tuple(p.split(':')) for p in args.symbols.split(',')]
        result = lexicon.check_symbol_coherence(pairs)
        print(json.dumps(result, indent=2))

    elif args.action == 'suggest' and args.symbol and args.tradition:
        suggestions = lexicon.suggest_complementary_symbols(args.symbol, args.tradition)
        for s in suggestions:
            print(f"{s['symbol'].tradition}: {s['symbol'].name} (score: {s['score']:.2f})")
            for reason in s['reasons']:
                print(f"  - {reason}")

    elif args.action == 'list':
        symbols = lexicon.get_all_symbols(args.tradition)
        for s in symbols:
            print(f"{s.tradition}: {s.name} - {s.meaning[:50]}...")
