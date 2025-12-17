"""
Cross-Promotion Engine.

Suggests related content links for discovery and engagement.
"""

import yaml
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set, Tuple
from collections import defaultdict
import math


@dataclass
class ContentLink:
    """Represents a suggested content link."""
    session_name: str
    title: str
    relevance_score: float
    link_type: str  # related, series, complementary, next_level
    explanation: str


@dataclass
class PromotionSuggestions:
    """Collection of cross-promotion suggestions."""
    source_session: str
    related_sessions: List[ContentLink]
    series_links: List[ContentLink]
    complementary_content: List[ContentLink]
    journey_progression: List[ContentLink]


class CrossPromotionEngine:
    """
    Cross-Promotion Engine.

    Analyzes content relationships to suggest cross-promotion
    opportunities that enhance user discovery and engagement.
    """

    # Journey family progressions
    JOURNEY_PROGRESSIONS = {
        'eden_garden': [
            'eden_garden',
            'celestial_journey',
            'cosmic_forge',
        ],
        'underworld_descent': [
            'underworld_descent',
            'temple_initiation',
            'cosmic_forge',
        ],
        'celestial_journey': [
            'celestial_journey',
            'cosmic_forge',
            'temple_initiation',
        ],
        'temple_initiation': [
            'temple_initiation',
            'cosmic_forge',
            'celestial_journey',
        ],
        'ocean_depths': [
            'ocean_depths',
            'underworld_descent',
            'eden_garden',
        ],
    }

    # Depth level progressions
    DEPTH_PROGRESSIONS = {
        'layer1': ['layer1', 'layer2'],
        'layer2': ['layer2', 'layer3'],
        'layer3': ['layer3', 'ipsissimus'],
        'ipsissimus': ['ipsissimus'],
    }

    # Outcome complementary pairs
    COMPLEMENTARY_OUTCOMES = {
        'healing': ['relaxation', 'self_knowledge', 'spiritual_growth'],
        'transformation': ['empowerment', 'self_knowledge', 'spiritual_growth'],
        'empowerment': ['confidence', 'transformation', 'healing'],
        'relaxation': ['healing', 'spiritual_growth'],
        'spiritual_growth': ['transformation', 'self_knowledge', 'healing'],
        'self_knowledge': ['transformation', 'spiritual_growth', 'healing'],
        'confidence': ['empowerment', 'transformation'],
        'creativity': ['transformation', 'spiritual_growth'],
    }

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parents[2]
        self.sessions_path = self.project_root / 'sessions'

        # Cache session data
        self._session_cache: Dict[str, Dict] = {}
        self._load_all_sessions()

    def _load_all_sessions(self):
        """Load and cache all session manifests."""
        for session_dir in self.sessions_path.iterdir():
            if not session_dir.is_dir():
                continue
            if session_dir.name.startswith(('_', '.', 'shorts')):
                continue

            manifest_path = session_dir / 'manifest.yaml'
            if manifest_path.exists():
                try:
                    with open(manifest_path, 'r') as f:
                        data = yaml.safe_load(f) or {}
                        self._session_cache[session_dir.name] = data.get('session', {})
                except Exception:
                    continue

    def _get_session(self, session_name: str) -> Optional[Dict[str, Any]]:
        """Get cached session data."""
        if session_name not in self._session_cache:
            manifest_path = self.sessions_path / session_name / 'manifest.yaml'
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    self._session_cache[session_name] = data.get('session', {})
        return self._session_cache.get(session_name)

    def _calculate_similarity(
        self,
        session_a: Dict[str, Any],
        session_b: Dict[str, Any]
    ) -> float:
        """Calculate content similarity between two sessions."""
        score = 0.0

        # Same journey family
        if session_a.get('journey_family') == session_b.get('journey_family'):
            score += 0.3

        # Same desired outcome
        if session_a.get('desired_outcome') == session_b.get('desired_outcome'):
            score += 0.25

        # Same depth level
        if session_a.get('depth_level') == session_b.get('depth_level'):
            score += 0.1

        # Shared archetypes
        arch_a = set(session_a.get('archetypes', []))
        arch_b = set(session_b.get('archetypes', []))
        if arch_a and arch_b:
            shared = len(arch_a & arch_b)
            total = len(arch_a | arch_b)
            score += 0.2 * (shared / total if total > 0 else 0)

        # Similar duration (within 10 minutes)
        dur_a = session_a.get('duration', 25)
        dur_b = session_b.get('duration', 25)
        if abs(dur_a - dur_b) <= 10:
            score += 0.1

        # Theme similarity (keyword overlap in title/description)
        text_a = f"{session_a.get('title', '')} {session_a.get('description', '')}".lower()
        text_b = f"{session_b.get('title', '')} {session_b.get('description', '')}".lower()
        words_a = set(re.findall(r'\w+', text_a))
        words_b = set(re.findall(r'\w+', text_b))
        common_words = words_a & words_b - {'the', 'a', 'an', 'and', 'or', 'of', 'to', 'in'}
        if len(words_a | words_b) > 0:
            score += 0.15 * (len(common_words) / len(words_a | words_b))

        return min(score, 1.0)

    def find_related_sessions(
        self,
        session_name: str,
        min_similarity: float = 0.3,
        max_results: int = 5
    ) -> List[ContentLink]:
        """Find sessions related by content similarity."""
        source = self._get_session(session_name)
        if not source:
            return []

        results = []

        for other_name, other_data in self._session_cache.items():
            if other_name == session_name:
                continue

            similarity = self._calculate_similarity(source, other_data)

            if similarity >= min_similarity:
                results.append(ContentLink(
                    session_name=other_name,
                    title=other_data.get('title', other_name),
                    relevance_score=similarity,
                    link_type='related',
                    explanation=self._explain_relationship(source, other_data),
                ))

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]

    def _explain_relationship(
        self,
        session_a: Dict[str, Any],
        session_b: Dict[str, Any]
    ) -> str:
        """Generate explanation for why sessions are related."""
        reasons = []

        if session_a.get('journey_family') == session_b.get('journey_family'):
            reasons.append(f"Same journey family: {session_a.get('journey_family')}")

        if session_a.get('desired_outcome') == session_b.get('desired_outcome'):
            reasons.append(f"Same outcome: {session_a.get('desired_outcome')}")

        arch_a = set(session_a.get('archetypes', []))
        arch_b = set(session_b.get('archetypes', []))
        shared = arch_a & arch_b
        if shared:
            reasons.append(f"Shared archetypes: {', '.join(list(shared)[:2])}")

        if not reasons:
            reasons.append("Similar themes and content")

        return "; ".join(reasons)

    def find_series_sessions(self, session_name: str) -> List[ContentLink]:
        """Find sessions that form a series or sequence."""
        source = self._get_session(session_name)
        if not source:
            return []

        results = []
        journey_family = source.get('journey_family', '')

        # Check for numbered series in title
        title = source.get('title', session_name)
        series_match = re.search(r'(.*?)\s*(?:part|chapter|session|volume)\s*(\d+)', title, re.I)

        if series_match:
            series_name = series_match.group(1).strip()
            # Find other parts
            for other_name, other_data in self._session_cache.items():
                if other_name == session_name:
                    continue

                other_title = other_data.get('title', other_name)
                if series_name.lower() in other_title.lower():
                    results.append(ContentLink(
                        session_name=other_name,
                        title=other_title,
                        relevance_score=0.95,
                        link_type='series',
                        explanation=f"Part of '{series_name}' series",
                    ))

        # Check journey family progression
        if journey_family and journey_family in self.JOURNEY_PROGRESSIONS:
            progression = self.JOURNEY_PROGRESSIONS[journey_family]
            for other_name, other_data in self._session_cache.items():
                if other_name == session_name:
                    continue

                other_family = other_data.get('journey_family', '')
                if other_family in progression and other_family != journey_family:
                    results.append(ContentLink(
                        session_name=other_name,
                        title=other_data.get('title', other_name),
                        relevance_score=0.8,
                        link_type='series',
                        explanation=f"Journey progression: {journey_family} → {other_family}",
                    ))

        return results[:5]

    def find_complementary_content(self, session_name: str) -> List[ContentLink]:
        """Find content that complements the source session."""
        source = self._get_session(session_name)
        if not source:
            return []

        results = []
        outcome = source.get('desired_outcome', '')

        # Get complementary outcomes
        complementary = self.COMPLEMENTARY_OUTCOMES.get(outcome, [])

        for other_name, other_data in self._session_cache.items():
            if other_name == session_name:
                continue

            other_outcome = other_data.get('desired_outcome', '')

            if other_outcome in complementary:
                # Check for different journey family (variety)
                if other_data.get('journey_family') != source.get('journey_family'):
                    score = 0.85
                else:
                    score = 0.7

                results.append(ContentLink(
                    session_name=other_name,
                    title=other_data.get('title', other_name),
                    relevance_score=score,
                    link_type='complementary',
                    explanation=f"Complements {outcome} with {other_outcome}",
                ))

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:5]

    def find_next_level_content(self, session_name: str) -> List[ContentLink]:
        """Find content for progression to deeper levels."""
        source = self._get_session(session_name)
        if not source:
            return []

        results = []
        current_depth = source.get('depth_level', 'layer2')
        journey_family = source.get('journey_family', '')
        outcome = source.get('desired_outcome', '')

        # Get next depth levels
        next_depths = []
        if current_depth in self.DEPTH_PROGRESSIONS:
            possible = self.DEPTH_PROGRESSIONS[current_depth]
            next_depths = [d for d in possible if d != current_depth]

        for other_name, other_data in self._session_cache.items():
            if other_name == session_name:
                continue

            other_depth = other_data.get('depth_level', 'layer2')
            other_family = other_data.get('journey_family', '')
            other_outcome = other_data.get('desired_outcome', '')

            # Look for deeper sessions in same family
            if other_depth in next_depths:
                score = 0.7

                # Bonus for same journey family
                if other_family == journey_family:
                    score += 0.15

                # Bonus for same outcome
                if other_outcome == outcome:
                    score += 0.1

                results.append(ContentLink(
                    session_name=other_name,
                    title=other_data.get('title', other_name),
                    relevance_score=min(score, 1.0),
                    link_type='next_level',
                    explanation=f"Progression from {current_depth} to {other_depth}",
                ))

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:3]

    def get_all_suggestions(self, session_name: str) -> PromotionSuggestions:
        """Get all cross-promotion suggestions for a session."""
        return PromotionSuggestions(
            source_session=session_name,
            related_sessions=self.find_related_sessions(session_name),
            series_links=self.find_series_sessions(session_name),
            complementary_content=self.find_complementary_content(session_name),
            journey_progression=self.find_next_level_content(session_name),
        )

    def generate_end_screen_links(
        self,
        session_name: str,
        num_links: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Generate end screen link suggestions for YouTube.

        Returns formatted suggestions for video end screens.
        """
        suggestions = self.get_all_suggestions(session_name)

        # Prioritize: series > progression > related
        candidates = []

        for link in suggestions.series_links:
            candidates.append({
                'session': link.session_name,
                'title': link.title,
                'type': 'series',
                'cta': "Continue the Journey",
                'score': link.relevance_score + 0.2,
            })

        for link in suggestions.journey_progression:
            candidates.append({
                'session': link.session_name,
                'title': link.title,
                'type': 'progression',
                'cta': "Go Deeper",
                'score': link.relevance_score + 0.1,
            })

        for link in suggestions.related_sessions:
            candidates.append({
                'session': link.session_name,
                'title': link.title,
                'type': 'related',
                'cta': "You Might Also Enjoy",
                'score': link.relevance_score,
            })

        # Sort and dedupe
        candidates.sort(key=lambda x: x['score'], reverse=True)
        seen = set()
        unique = []
        for c in candidates:
            if c['session'] not in seen:
                seen.add(c['session'])
                unique.append(c)

        return unique[:num_links]

    def generate_description_links(
        self,
        session_name: str,
        max_links: int = 5
    ) -> str:
        """
        Generate related content section for video description.

        Returns formatted markdown for description.
        """
        suggestions = self.get_all_suggestions(session_name)

        lines = []
        lines.append("\n📍 Related Journeys:\n")

        # Combine all suggestions
        all_links = []
        for link in suggestions.series_links + suggestions.related_sessions + suggestions.complementary_content:
            all_links.append(link)

        # Dedupe and sort
        seen = set()
        unique = []
        for link in sorted(all_links, key=lambda x: x.relevance_score, reverse=True):
            if link.session_name not in seen:
                seen.add(link.session_name)
                unique.append(link)

        for link in unique[:max_links]:
            # Format: Title - link placeholder
            lines.append(f"• {link.title}")
            lines.append(f"  {link.explanation}")
            lines.append("")

        return "\n".join(lines)

    def build_content_graph(self) -> Dict[str, Any]:
        """
        Build a graph of content relationships for visualization.

        Returns graph data suitable for network visualization.
        """
        nodes = []
        edges = []

        for session_name, data in self._session_cache.items():
            nodes.append({
                'id': session_name,
                'title': data.get('title', session_name),
                'outcome': data.get('desired_outcome', ''),
                'family': data.get('journey_family', ''),
                'depth': data.get('depth_level', 'layer2'),
            })

        # Build edges based on relationships
        processed = set()
        for session_name in self._session_cache:
            suggestions = self.get_all_suggestions(session_name)

            for link in suggestions.related_sessions:
                edge_key = tuple(sorted([session_name, link.session_name]))
                if edge_key not in processed:
                    processed.add(edge_key)
                    edges.append({
                        'source': session_name,
                        'target': link.session_name,
                        'type': link.link_type,
                        'weight': link.relevance_score,
                    })

        return {
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'total_sessions': len(nodes),
                'total_connections': len(edges),
                'avg_connections': len(edges) / len(nodes) if nodes else 0,
            }
        }


# CLI interface
if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Cross-Promotion Engine')
    parser.add_argument('action', choices=['suggest', 'endscreen', 'description', 'graph'],
                       help='Action to perform')
    parser.add_argument('--session', help='Session name')

    args = parser.parse_args()

    engine = CrossPromotionEngine()

    if args.action == 'suggest' and args.session:
        suggestions = engine.get_all_suggestions(args.session)
        print(f"\n=== Cross-Promotion for {args.session} ===")

        print("\n📚 Series Links:")
        for link in suggestions.series_links:
            print(f"  • {link.title} ({link.relevance_score:.2f})")
            print(f"    {link.explanation}")

        print("\n🔗 Related Sessions:")
        for link in suggestions.related_sessions:
            print(f"  • {link.title} ({link.relevance_score:.2f})")
            print(f"    {link.explanation}")

        print("\n✨ Complementary Content:")
        for link in suggestions.complementary_content:
            print(f"  • {link.title} ({link.relevance_score:.2f})")
            print(f"    {link.explanation}")

        print("\n⬆️ Journey Progression:")
        for link in suggestions.journey_progression:
            print(f"  • {link.title} ({link.relevance_score:.2f})")
            print(f"    {link.explanation}")

    elif args.action == 'endscreen' and args.session:
        links = engine.generate_end_screen_links(args.session)
        print(f"\n=== End Screen Links for {args.session} ===")
        for link in links:
            print(f"\n{link['cta']}:")
            print(f"  {link['title']}")
            print(f"  Type: {link['type']}, Score: {link['score']:.2f}")

    elif args.action == 'description' and args.session:
        desc = engine.generate_description_links(args.session)
        print(desc)

    elif args.action == 'graph':
        graph = engine.build_content_graph()
        print(json.dumps(graph, indent=2))
