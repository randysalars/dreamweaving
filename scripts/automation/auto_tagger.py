"""
Auto-Tagger Agent.

ML-based content tagging for Dreamweaving sessions.
"""

import yaml
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set, Tuple
from collections import Counter
import math


@dataclass
class TagSuggestion:
    """Represents a suggested tag with confidence."""
    tag: str
    confidence: float
    source: str  # content, keyword, pattern, category
    explanation: str


@dataclass
class TaggingResult:
    """Result of auto-tagging a session."""
    session_name: str
    suggested_tags: List[TagSuggestion]
    category_tags: List[str]
    theme_tags: List[str]
    technique_tags: List[str]
    duration_tag: str
    depth_tag: str


class AutoTagger:
    """
    Auto-Tagger Agent.

    Uses keyword extraction, pattern matching, and content analysis
    to automatically suggest tags for Dreamweaving sessions.
    """

    # Tag categories with keywords
    TAG_CATEGORIES = {
        # Outcome-based tags
        'healing': ['heal', 'restore', 'repair', 'mend', 'recovery', 'wellness', 'integration'],
        'transformation': ['transform', 'change', 'metamorphosis', 'rebirth', 'evolve', 'shift'],
        'empowerment': ['power', 'strength', 'confidence', 'courage', 'boundary', 'assertive'],
        'relaxation': ['relax', 'sleep', 'calm', 'peace', 'rest', 'soothe', 'tranquil'],
        'spiritual': ['spiritual', 'sacred', 'divine', 'soul', 'transcend', 'awakening'],

        # Theme-based tags
        'shadow-work': ['shadow', 'dark', 'unconscious', 'hidden', 'depth', 'underworld'],
        'nature': ['forest', 'garden', 'ocean', 'mountain', 'earth', 'nature', 'wilderness'],
        'cosmic': ['cosmic', 'space', 'star', 'galaxy', 'universe', 'celestial', 'astral'],
        'archetypal': ['archetype', 'guide', 'wise', 'elder', 'goddess', 'hero', 'journey'],
        'inner-child': ['child', 'innocent', 'play', 'wonder', 'young', 'inner-child'],

        # Technique-based tags
        'binaural': ['binaural', 'brainwave', 'frequency', 'hertz', 'theta', 'alpha', 'delta'],
        'guided-meditation': ['meditation', 'meditative', 'mindfulness', 'awareness'],
        'hypnosis': ['hypnosis', 'hypnotic', 'trance', 'suggestion', 'induction'],
        'visualization': ['visualize', 'imagine', 'imagery', 'vision', 'picture'],
        'breathwork': ['breath', 'breathing', 'inhale', 'exhale', 'pranayama'],

        # Setting-based tags
        'temple': ['temple', 'sanctuary', 'altar', 'sacred-space', 'shrine'],
        'garden': ['garden', 'eden', 'paradise', 'grove', 'botanical'],
        'cave': ['cave', 'cavern', 'underground', 'descent', 'depths'],
        'celestial': ['heaven', 'sky', 'cloud', 'angelic', 'divine-realm'],
        'mythical': ['myth', 'legend', 'ancient', 'mystical', 'magical'],
    }

    # Duration categories
    DURATION_TAGS = {
        'short': (0, 15),      # 0-15 minutes
        'medium': (15, 25),    # 15-25 minutes
        'standard': (25, 35),  # 25-35 minutes
        'long': (35, 60),      # 35-60 minutes
        'extended': (60, 999), # 60+ minutes
    }

    # Depth level mappings
    DEPTH_TAGS = {
        'layer1': 'beginner-friendly',
        'layer2': 'intermediate',
        'layer3': 'advanced',
        'ipsissimus': 'master-level',
    }

    # Pattern-based tag extraction
    PATTERN_TAGS = [
        (r'\b432\s*hz\b', '432hz'),
        (r'\b528\s*hz\b', '528hz'),
        (r'\btheta\s*wave', 'theta'),
        (r'\balpha\s*wave', 'alpha'),
        (r'\bdelta\s*wave', 'delta'),
        (r'\blucid\s*dream', 'lucid-dreaming'),
        (r'\bout\s*of\s*body', 'astral-projection'),
        (r'\bpast\s*life', 'past-life'),
        (r'\binner\s*child', 'inner-child'),
        (r'\bshadow\s*work', 'shadow-work'),
        (r'\bself[\s-]?love', 'self-love'),
        (r'\bself[\s-]?compassion', 'self-compassion'),
        (r'\banxiety', 'anxiety-relief'),
        (r'\bstress', 'stress-relief'),
        (r'\btrauma', 'trauma-healing'),
        (r'\bgrief', 'grief-support'),
        (r'\bforgiveness', 'forgiveness'),
        (r'\babundance', 'abundance'),
        (r'\bmanifestation', 'manifestation'),
    ]

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parents[2]
        self.sessions_path = self.project_root / 'sessions'
        self.knowledge_path = self.project_root / 'knowledge'

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
                session.get('desired_outcome', ''),
                session.get('journey_family', ''),
            ])

        # Script if available
        script_path = session_dir / 'working_files' / 'script.ssml'
        if script_path.exists():
            with open(script_path, 'r') as f:
                script_text = f.read()
                # Remove SSML tags
                script_text = re.sub(r'<[^>]+>', ' ', script_text)
                text_parts.append(script_text)

        return ' '.join(text_parts).lower()

    def _calculate_keyword_score(
        self,
        keywords: List[str],
        text: str
    ) -> Tuple[float, int]:
        """Calculate score based on keyword frequency."""
        total_hits = 0
        for keyword in keywords:
            count = len(re.findall(r'\b' + re.escape(keyword) + r'\w*', text))
            total_hits += count

        # Normalize score (0-1)
        score = min(total_hits / 10, 1.0)
        return score, total_hits

    def _extract_pattern_tags(self, text: str) -> List[TagSuggestion]:
        """Extract tags based on regex patterns."""
        suggestions = []

        for pattern, tag in self.PATTERN_TAGS:
            if re.search(pattern, text, re.IGNORECASE):
                suggestions.append(TagSuggestion(
                    tag=tag,
                    confidence=0.9,
                    source='pattern',
                    explanation=f"Pattern '{pattern}' matched in content",
                ))

        return suggestions

    def _get_duration_tag(self, duration: int) -> str:
        """Get duration category tag."""
        for tag, (min_dur, max_dur) in self.DURATION_TAGS.items():
            if min_dur <= duration < max_dur:
                return f"duration-{tag}"
        return "duration-extended"

    def _get_depth_tag(self, depth_level: str) -> str:
        """Get depth level tag."""
        return self.DEPTH_TAGS.get(depth_level.lower(), 'intermediate')

    def auto_tag(self, session_name: str) -> TaggingResult:
        """
        Auto-generate tags for a session.

        Args:
            session_name: Name of the session directory

        Returns:
            TaggingResult with all suggested tags
        """
        manifest = self._load_session_manifest(session_name)
        if not manifest:
            return TaggingResult(
                session_name=session_name,
                suggested_tags=[],
                category_tags=[],
                theme_tags=[],
                technique_tags=[],
                duration_tag='',
                depth_tag='',
            )

        session = manifest.get('session', {})
        text_content = self._extract_text_content(session_name)

        all_suggestions = []
        category_tags = []
        theme_tags = []
        technique_tags = []

        # Category-based tagging
        for category, keywords in self.TAG_CATEGORIES.items():
            score, hits = self._calculate_keyword_score(keywords, text_content)
            if score > 0.2:  # Threshold for inclusion
                suggestion = TagSuggestion(
                    tag=category,
                    confidence=score,
                    source='keyword',
                    explanation=f"Found {hits} keyword matches for '{category}'",
                )
                all_suggestions.append(suggestion)

                # Categorize the tag
                if category in ['healing', 'transformation', 'empowerment', 'relaxation', 'spiritual']:
                    category_tags.append(category)
                elif category in ['shadow-work', 'nature', 'cosmic', 'archetypal', 'inner-child']:
                    theme_tags.append(category)
                elif category in ['binaural', 'guided-meditation', 'hypnosis', 'visualization', 'breathwork']:
                    technique_tags.append(category)
                else:
                    theme_tags.append(category)

        # Pattern-based tagging
        pattern_suggestions = self._extract_pattern_tags(text_content)
        all_suggestions.extend(pattern_suggestions)

        # Manifest-based tags
        if session.get('archetypes'):
            for archetype in session['archetypes'][:3]:
                suggestion = TagSuggestion(
                    tag=archetype.lower().replace(' ', '-'),
                    confidence=0.95,
                    source='manifest',
                    explanation=f"Archetype '{archetype}' from manifest",
                )
                all_suggestions.append(suggestion)

        if session.get('journey_family'):
            family_tag = session['journey_family'].replace('_', '-')
            all_suggestions.append(TagSuggestion(
                tag=family_tag,
                confidence=0.95,
                source='manifest',
                explanation=f"Journey family from manifest",
            ))

        if session.get('desired_outcome'):
            outcome_tag = session['desired_outcome'].replace('_', '-')
            all_suggestions.append(TagSuggestion(
                tag=outcome_tag,
                confidence=0.95,
                source='manifest',
                explanation=f"Desired outcome from manifest",
            ))
            category_tags.append(outcome_tag)

        # Duration and depth tags
        duration = session.get('duration', 25)
        depth_level = session.get('depth_level', 'layer2')

        duration_tag = self._get_duration_tag(duration)
        depth_tag = self._get_depth_tag(depth_level)

        # Sort by confidence
        all_suggestions.sort(key=lambda x: x.confidence, reverse=True)

        return TaggingResult(
            session_name=session_name,
            suggested_tags=all_suggestions[:15],  # Top 15
            category_tags=list(set(category_tags)),
            theme_tags=list(set(theme_tags)),
            technique_tags=list(set(technique_tags)),
            duration_tag=duration_tag,
            depth_tag=depth_tag,
        )

    def update_manifest_tags(
        self,
        session_name: str,
        min_confidence: float = 0.5
    ) -> Dict[str, Any]:
        """
        Update session manifest with auto-generated tags.

        Args:
            session_name: Session to update
            min_confidence: Minimum confidence for tag inclusion

        Returns:
            Updated tag structure
        """
        result = self.auto_tag(session_name)

        # Filter by confidence
        accepted_tags = [
            s.tag for s in result.suggested_tags
            if s.confidence >= min_confidence
        ]

        # Add structured tags
        accepted_tags.append(result.duration_tag)
        accepted_tags.append(result.depth_tag)

        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in accepted_tags:
            if tag and tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        return {
            'tags': unique_tags,
            'category_tags': result.category_tags,
            'theme_tags': result.theme_tags,
            'technique_tags': result.technique_tags,
            'meta': {
                'duration': result.duration_tag,
                'depth': result.depth_tag,
            }
        }

    def batch_tag_sessions(
        self,
        min_confidence: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Tag all sessions in the project."""
        results = []

        for session_dir in self.sessions_path.iterdir():
            if not session_dir.is_dir():
                continue
            if session_dir.name.startswith(('_', '.', 'shorts')):
                continue

            result = self.auto_tag(session_dir.name)
            results.append({
                'session': session_dir.name,
                'tags': [s.tag for s in result.suggested_tags if s.confidence >= min_confidence],
                'top_category': result.category_tags[0] if result.category_tags else None,
            })

        return results

    def suggest_missing_tags(self, session_name: str) -> List[TagSuggestion]:
        """
        Suggest tags that might be missing from a session.

        Compares current tags to auto-detected tags.
        """
        manifest = self._load_session_manifest(session_name)
        if not manifest:
            return []

        current_tags = set(manifest.get('session', {}).get('tags', []))
        result = self.auto_tag(session_name)

        missing = []
        for suggestion in result.suggested_tags:
            if suggestion.tag not in current_tags and suggestion.confidence >= 0.5:
                missing.append(suggestion)

        return missing

    def find_similar_by_tags(
        self,
        session_name: str,
        min_overlap: int = 3
    ) -> List[Dict[str, Any]]:
        """Find sessions with similar tags."""
        target_result = self.auto_tag(session_name)
        target_tags = set(s.tag for s in target_result.suggested_tags)

        similar = []

        for session_dir in self.sessions_path.iterdir():
            if not session_dir.is_dir():
                continue
            if session_dir.name == session_name:
                continue
            if session_dir.name.startswith(('_', '.', 'shorts')):
                continue

            other_result = self.auto_tag(session_dir.name)
            other_tags = set(s.tag for s in other_result.suggested_tags)

            overlap = target_tags & other_tags
            if len(overlap) >= min_overlap:
                similar.append({
                    'session': session_dir.name,
                    'overlap_count': len(overlap),
                    'shared_tags': list(overlap),
                })

        similar.sort(key=lambda x: x['overlap_count'], reverse=True)
        return similar[:5]


# CLI interface
if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Auto-Tagger')
    parser.add_argument('action', choices=['tag', 'batch', 'missing', 'similar'],
                       help='Action to perform')
    parser.add_argument('--session', help='Session name')
    parser.add_argument('--confidence', type=float, default=0.5,
                       help='Minimum confidence threshold')

    args = parser.parse_args()

    tagger = AutoTagger()

    if args.action == 'tag' and args.session:
        result = tagger.auto_tag(args.session)
        print(f"\n=== Tags for {args.session} ===")
        print(f"Duration: {result.duration_tag}")
        print(f"Depth: {result.depth_tag}")
        print(f"\nCategory tags: {', '.join(result.category_tags)}")
        print(f"Theme tags: {', '.join(result.theme_tags)}")
        print(f"Technique tags: {', '.join(result.technique_tags)}")
        print(f"\nAll suggestions:")
        for s in result.suggested_tags:
            print(f"  {s.tag} ({s.confidence:.2f}) - {s.source}: {s.explanation}")

    elif args.action == 'batch':
        results = tagger.batch_tag_sessions(args.confidence)
        for r in results:
            print(f"{r['session']}: {', '.join(r['tags'][:5])}")

    elif args.action == 'missing' and args.session:
        missing = tagger.suggest_missing_tags(args.session)
        print(f"\n=== Missing tags for {args.session} ===")
        for s in missing:
            print(f"  {s.tag} ({s.confidence:.2f}) - {s.explanation}")

    elif args.action == 'similar' and args.session:
        similar = tagger.find_similar_by_tags(args.session)
        print(f"\n=== Sessions similar to {args.session} ===")
        for s in similar:
            print(f"  {s['session']} ({s['overlap_count']} shared tags)")
            print(f"    Tags: {', '.join(s['shared_tags'][:5])}")
