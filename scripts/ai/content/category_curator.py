"""
Category Curator Agent.

Auto-organizes and tags Dreamweaving content for better discovery.
"""

import os
import yaml
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set
from datetime import datetime
from collections import Counter


@dataclass
class ContentCategory:
    """Represents a content category."""
    name: str
    slug: str
    description: str
    keywords: List[str]
    sessions: List[str] = field(default_factory=list)
    parent_category: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'keywords': self.keywords,
            'sessions': self.sessions,
            'parent_category': self.parent_category,
        }


class CategoryCurator:
    """
    Category Curator Agent.

    Automatically categorizes and tags Dreamweaving sessions
    based on their manifest data and content analysis.
    """

    # Primary categories with their keywords
    CATEGORY_DEFINITIONS = {
        'healing': {
            'name': 'Healing Journeys',
            'description': 'Sessions focused on emotional and spiritual healing',
            'keywords': ['healing', 'restore', 'repair', 'mend', 'recovery', 'wellness',
                        'trauma', 'wound', 'integration', 'wholeness'],
        },
        'transformation': {
            'name': 'Transformation',
            'description': 'Deep change and metamorphosis experiences',
            'keywords': ['transform', 'change', 'metamorphosis', 'rebirth', 'evolution',
                        'alchemical', 'transmute', 'shift', 'breakthrough'],
        },
        'empowerment': {
            'name': 'Empowerment',
            'description': 'Sessions for building personal power and confidence',
            'keywords': ['power', 'strength', 'confidence', 'courage', 'warrior',
                        'sovereign', 'authority', 'boundaries', 'assertive'],
        },
        'relaxation': {
            'name': 'Relaxation & Sleep',
            'description': 'Deep relaxation and sleep support',
            'keywords': ['relax', 'sleep', 'calm', 'peace', 'rest', 'soothe',
                        'gentle', 'quiet', 'serenity', 'tranquil'],
        },
        'spiritual': {
            'name': 'Spiritual Growth',
            'description': 'Journeys for spiritual development and awakening',
            'keywords': ['spiritual', 'sacred', 'divine', 'soul', 'enlighten',
                        'transcend', 'unity', 'cosmic', 'mystical', 'awakening'],
        },
        'shadow': {
            'name': 'Shadow Work',
            'description': 'Integration of shadow aspects',
            'keywords': ['shadow', 'dark', 'unconscious', 'hidden', 'depth',
                        'underworld', 'descent', 'facing', 'integrate'],
        },
        'nature': {
            'name': 'Nature Journeys',
            'description': 'Nature-based healing and connection',
            'keywords': ['nature', 'forest', 'garden', 'eden', 'ocean', 'mountain',
                        'earth', 'elements', 'natural', 'wilderness'],
        },
        'cosmic': {
            'name': 'Cosmic & Stellar',
            'description': 'Journeys through cosmic realms',
            'keywords': ['cosmic', 'space', 'star', 'astral', 'celestial', 'galaxy',
                        'universe', 'nebula', 'planet', 'stellar'],
        },
        'archetypal': {
            'name': 'Archetypal Journeys',
            'description': 'Encounters with archetypal figures',
            'keywords': ['archetype', 'guide', 'wise', 'elder', 'goddess', 'god',
                        'hero', 'journey', 'myth', 'legend'],
        },
        'creativity': {
            'name': 'Creativity & Inspiration',
            'description': 'Unlocking creative potential',
            'keywords': ['creative', 'art', 'inspiration', 'muse', 'imagination',
                        'vision', 'expression', 'artist', 'create'],
        },
    }

    # Tag categories with extraction patterns
    TAG_PATTERNS = {
        'duration': {
            'short': (0, 15),
            'medium': (15, 30),
            'long': (30, 60),
        },
        'depth_level': ['layer1', 'layer2', 'layer3', 'ipsissimus'],
        'journey_family': [
            'celestial_journey', 'eden_garden', 'underworld_descent',
            'temple_initiation', 'cosmic_forge', 'ocean_depths',
        ],
        'brainwave_target': ['alpha', 'theta', 'delta', 'gamma'],
    }

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parents[3]
        self.sessions_path = self.project_root / 'sessions'
        self.knowledge_path = self.project_root / 'knowledge'
        self.categories_file = self.knowledge_path / 'categories.yaml'

        # Initialize categories
        self.categories: Dict[str, ContentCategory] = {}
        self._init_categories()

    def _init_categories(self):
        """Initialize category objects from definitions."""
        for slug, defn in self.CATEGORY_DEFINITIONS.items():
            self.categories[slug] = ContentCategory(
                name=defn['name'],
                slug=slug,
                description=defn['description'],
                keywords=defn['keywords'],
            )

    def _load_session_manifest(self, session_name: str) -> Optional[Dict[str, Any]]:
        """Load manifest from session directory."""
        manifest_path = self.sessions_path / session_name / 'manifest.yaml'
        if not manifest_path.exists():
            return None
        with open(manifest_path, 'r') as f:
            return yaml.safe_load(f)

    def _extract_text_content(self, session_name: str) -> str:
        """Extract all text content from session for analysis."""
        text_parts = []
        session_dir = self.sessions_path / session_name

        # Manifest
        manifest = self._load_session_manifest(session_name)
        if manifest:
            session = manifest.get('session', {})
            text_parts.extend([
                session.get('title', ''),
                session.get('description', ''),
                session.get('theme', ''),
                ' '.join(session.get('archetypes', [])),
            ])

        # Script if available
        script_path = session_dir / 'working_files' / 'script.ssml'
        if script_path.exists():
            with open(script_path, 'r') as f:
                script_text = f.read()
                # Remove SSML tags
                script_text = re.sub(r'<[^>]+>', ' ', script_text)
                text_parts.append(script_text[:5000])  # First 5000 chars

        return ' '.join(text_parts).lower()

    def categorize_session(self, session_name: str) -> Dict[str, Any]:
        """
        Categorize a single session.

        Returns:
            Dict with:
            - primary_category: Main category slug
            - secondary_categories: List of additional categories
            - tags: Auto-generated tags
            - confidence: Confidence score (0-1)
        """
        manifest = self._load_session_manifest(session_name)
        if not manifest:
            return {'error': f'Session not found: {session_name}'}

        session = manifest.get('session', {})
        text_content = self._extract_text_content(session_name)

        # Score each category
        category_scores: Dict[str, float] = {}
        for slug, category in self.categories.items():
            score = self._calculate_category_score(
                category.keywords,
                text_content,
                session.get('desired_outcome', ''),
            )
            category_scores[slug] = score

        # Sort by score
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Primary and secondary categories
        primary = sorted_categories[0][0] if sorted_categories[0][1] > 0.1 else 'uncategorized'
        secondary = [
            cat for cat, score in sorted_categories[1:4]
            if score > 0.15
        ]

        # Generate tags
        tags = self._generate_tags(session, text_content)

        # Calculate confidence
        confidence = min(sorted_categories[0][1] * 2, 1.0)

        return {
            'session_name': session_name,
            'primary_category': primary,
            'secondary_categories': secondary,
            'tags': tags,
            'confidence': confidence,
            'scores': dict(sorted_categories[:5]),
        }

    def _calculate_category_score(
        self,
        keywords: List[str],
        text_content: str,
        desired_outcome: str
    ) -> float:
        """Calculate how well content matches a category."""
        score = 0.0

        # Keyword frequency
        keyword_hits = sum(
            text_content.count(kw.lower())
            for kw in keywords
        )
        score += min(keyword_hits / 10, 0.5)

        # Direct outcome match
        for kw in keywords:
            if kw in desired_outcome.lower():
                score += 0.3
                break

        return min(score, 1.0)

    def _generate_tags(
        self,
        session: Dict[str, Any],
        text_content: str
    ) -> List[str]:
        """Generate relevant tags for a session."""
        tags: Set[str] = set()

        # Duration tag
        duration = session.get('duration', 25)
        for tag, (min_dur, max_dur) in self.TAG_PATTERNS['duration'].items():
            if min_dur <= duration < max_dur:
                tags.add(f'duration-{tag}')
                break
        else:
            tags.add('duration-extended')

        # Depth level
        depth = session.get('depth_level', 'layer2')
        if depth in self.TAG_PATTERNS['depth_level']:
            tags.add(depth.replace('_', '-'))

        # Journey family
        family = session.get('journey_family', '')
        if family:
            tags.add(family.replace('_', '-'))

        # Desired outcome
        outcome = session.get('desired_outcome', '')
        if outcome:
            tags.add(outcome.replace('_', '-'))

        # Archetypes
        for archetype in session.get('archetypes', [])[:3]:
            tags.add(archetype.lower().replace(' ', '-'))

        # Content-based tags
        content_tags = self._extract_content_tags(text_content)
        tags.update(content_tags)

        return sorted(list(tags))[:15]  # Max 15 tags

    def _extract_content_tags(self, text_content: str) -> Set[str]:
        """Extract tags from text content."""
        tags: Set[str] = set()

        # Check for specific themes
        theme_keywords = {
            'binaural': ['binaural', 'brainwave', 'frequency'],
            'guided': ['guided', 'journey', 'visualization'],
            'meditation': ['meditation', 'meditative', 'mindfulness'],
            'hypnosis': ['hypnosis', 'hypnotic', 'trance'],
            'asmr': ['whisper', 'soft voice', 'asmr'],
            'lucid': ['lucid', 'lucid dream', 'dream'],
            'astral': ['astral', 'out of body', 'travel'],
        }

        for tag, keywords in theme_keywords.items():
            if any(kw in text_content for kw in keywords):
                tags.add(tag)

        return tags

    def categorize_all_sessions(self) -> List[Dict[str, Any]]:
        """Categorize all sessions in the project."""
        results = []

        for session_dir in self.sessions_path.iterdir():
            if not session_dir.is_dir():
                continue
            if session_dir.name.startswith(('_', '.')):
                continue

            result = self.categorize_session(session_dir.name)
            if 'error' not in result:
                results.append(result)

        return results

    def build_category_index(self) -> Dict[str, ContentCategory]:
        """Build index of categories with their sessions."""
        # Reset session lists
        for category in self.categories.values():
            category.sessions = []

        # Categorize all sessions
        results = self.categorize_all_sessions()

        # Assign sessions to categories
        for result in results:
            primary = result['primary_category']
            if primary in self.categories:
                self.categories[primary].sessions.append(result['session_name'])

            for secondary in result['secondary_categories']:
                if secondary in self.categories:
                    self.categories[secondary].sessions.append(result['session_name'])

        return self.categories

    def save_category_index(self) -> Path:
        """Save category index to YAML file."""
        index = self.build_category_index()

        data = {
            'generated_at': datetime.now().isoformat(),
            'categories': {
                slug: cat.to_dict()
                for slug, cat in index.items()
            }
        }

        with open(self.categories_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

        return self.categories_file

    def suggest_tags_for_session(self, session_name: str) -> List[str]:
        """Suggest additional tags for a session."""
        result = self.categorize_session(session_name)
        if 'error' in result:
            return []

        return result['tags']

    def find_similar_sessions(
        self,
        session_name: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find sessions similar to a given session."""
        target = self.categorize_session(session_name)
        if 'error' in target:
            return []

        target_tags = set(target['tags'])
        target_categories = {target['primary_category']} | set(target['secondary_categories'])

        results = []
        for session_dir in self.sessions_path.iterdir():
            if not session_dir.is_dir():
                continue
            if session_dir.name == session_name:
                continue
            if session_dir.name.startswith(('_', '.')):
                continue

            other = self.categorize_session(session_dir.name)
            if 'error' in other:
                continue

            other_tags = set(other['tags'])
            other_categories = {other['primary_category']} | set(other['secondary_categories'])

            # Calculate similarity
            tag_overlap = len(target_tags & other_tags) / max(len(target_tags | other_tags), 1)
            cat_overlap = len(target_categories & other_categories) / max(len(target_categories | other_categories), 1)

            similarity = (tag_overlap * 0.6) + (cat_overlap * 0.4)

            results.append({
                'session_name': session_dir.name,
                'similarity': similarity,
                'shared_tags': list(target_tags & other_tags),
                'primary_category': other['primary_category'],
            })

        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]

    def get_category_statistics(self) -> Dict[str, Any]:
        """Get statistics about category distribution."""
        results = self.categorize_all_sessions()

        category_counts = Counter(r['primary_category'] for r in results)
        tag_counts = Counter(tag for r in results for tag in r['tags'])

        avg_confidence = sum(r['confidence'] for r in results) / max(len(results), 1)

        return {
            'total_sessions': len(results),
            'category_distribution': dict(category_counts),
            'top_tags': dict(tag_counts.most_common(20)),
            'average_confidence': avg_confidence,
            'uncategorized': category_counts.get('uncategorized', 0),
        }


# CLI interface
if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Category Curator')
    parser.add_argument('action', choices=['categorize', 'index', 'similar', 'stats'],
                       help='Action to perform')
    parser.add_argument('--session', help='Session name (for categorize/similar)')
    parser.add_argument('--save', action='store_true', help='Save results')

    args = parser.parse_args()

    curator = CategoryCurator()

    if args.action == 'categorize':
        if args.session:
            result = curator.categorize_session(args.session)
            print(json.dumps(result, indent=2))
        else:
            results = curator.categorize_all_sessions()
            for r in results:
                print(f"{r['session_name']}: {r['primary_category']} ({r['confidence']:.2f})")

    elif args.action == 'index':
        if args.save:
            path = curator.save_category_index()
            print(f"Saved to: {path}")
        else:
            index = curator.build_category_index()
            for slug, cat in index.items():
                print(f"\n{cat.name} ({len(cat.sessions)} sessions)")
                for session in cat.sessions[:5]:
                    print(f"  - {session}")

    elif args.action == 'similar' and args.session:
        similar = curator.find_similar_sessions(args.session)
        for s in similar:
            print(f"{s['session_name']}: {s['similarity']:.2f} ({s['primary_category']})")

    elif args.action == 'stats':
        stats = curator.get_category_statistics()
        print(json.dumps(stats, indent=2))
