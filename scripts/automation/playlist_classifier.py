#!/usr/bin/env python3
"""
Playlist Classifier - Automatic YouTube playlist assignment for Dreamweaving videos.

Uses multi-signal content analysis to match sessions to appropriate playlists.

Usage:
    from scripts.automation.playlist_classifier import PlaylistClassifier, classify_session

    # Classify a session
    result = classify_session(Path('sessions/my-session'))
    print(result['primary'])  # Best match playlist name
    print(result['playlists'])  # List of playlist IDs to add video to

    # Direct classifier usage
    classifier = PlaylistClassifier()
    session_data = {
        'title': 'Healing Journey',
        'description': 'A restorative meditation...',
        'tags': ['healing', 'meditation'],
        'duration_minutes': 25,
        'manifest': {...}
    }
    result = classifier.get_playlists_for_session(session_data)
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

logger = logging.getLogger(__name__)

# Default config path
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / 'config' / 'youtube_playlists.yaml'


@dataclass
class PlaylistMatch:
    """Represents a playlist match with confidence score."""
    playlist_id: str
    name: str
    slug: str
    confidence: float
    signals: Dict[str, float] = field(default_factory=dict)
    playlist_type: str = 'content'  # 'content', 'format', 'duration', 'series'
    requires_manual_review: bool = False


class PlaylistClassifier:
    """
    Multi-signal playlist classifier for Dreamweaving videos.

    Analyzes session metadata and routes to appropriate YouTube playlists.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize with playlist configuration.

        Args:
            config_path: Path to youtube_playlists.yaml. Uses default if not provided.
        """
        if config_path is None:
            config_path = DEFAULT_CONFIG_PATH

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.playlists = self._build_playlist_registry()
        self.weights = self.config.get('classification', {}).get('weights', {
            'title': 0.35,
            'description': 0.25,
            'tags': 0.15,
            'manifest_outcome': 0.15,
            'archetypes': 0.10
        })

    def _load_config(self) -> dict:
        """Load playlist configuration from YAML."""
        if not self.config_path.exists():
            logger.warning(f"Config not found: {self.config_path}")
            return {}

        with open(self.config_path) as f:
            return yaml.safe_load(f) or {}

    def _build_playlist_registry(self) -> Dict[str, dict]:
        """Build unified registry from all playlist types."""
        registry = {}

        # Merge all playlist types
        for playlist_type in ['content_playlists', 'format_playlists',
                              'duration_playlists', 'series_playlists']:
            playlists = self.config.get(playlist_type, {})
            for slug, data in playlists.items():
                data = dict(data)  # Copy to avoid modifying config
                data['type'] = playlist_type.replace('_playlists', '')
                data['slug'] = slug
                registry[slug] = data

        return registry

    def classify(self, session_data: Dict[str, Any]) -> List[PlaylistMatch]:
        """
        Classify session and return ranked playlist matches.

        Args:
            session_data: Dict containing:
                - title: Session/video title
                - description: Full description
                - tags: List of tags
                - duration_minutes: Session duration
                - manifest: Full manifest data (optional)
                - archetypes: List of archetype dicts (optional)

        Returns:
            List of PlaylistMatch objects sorted by confidence (highest first)
        """
        matches = []

        # Score content-based and format-based playlists
        for slug, playlist in self.playlists.items():
            if playlist['type'] in ['content', 'format']:
                score, signals = self._score_content_match(session_data, playlist)
                if score > 0:
                    matches.append(PlaylistMatch(
                        playlist_id=playlist.get('youtube_id', ''),
                        name=playlist['name'],
                        slug=slug,
                        confidence=score,
                        signals=signals,
                        playlist_type=playlist['type'],
                        requires_manual_review=playlist.get('manual_assignment', False)
                    ))

            elif playlist['type'] == 'series':
                # Series playlists use keywords but flag for manual review
                score, signals = self._score_content_match(session_data, playlist)
                if score > 0.3:  # Lower threshold for series suggestions
                    matches.append(PlaylistMatch(
                        playlist_id=playlist.get('youtube_id', ''),
                        name=playlist['name'],
                        slug=slug,
                        confidence=score,
                        signals=signals,
                        playlist_type='series',
                        requires_manual_review=True
                    ))

        # Check duration-based playlists
        duration_matches = self._check_duration_playlists(session_data)
        matches.extend(duration_matches)

        # Sort by confidence (highest first)
        matches.sort(key=lambda m: m.confidence, reverse=True)

        return matches

    def _score_content_match(
        self,
        session_data: Dict[str, Any],
        playlist: dict
    ) -> Tuple[float, Dict[str, float]]:
        """
        Score how well session matches a content playlist.

        Returns (total_score, signal_breakdown).
        """
        signals = {
            'title': 0.0,
            'description': 0.0,
            'tags': 0.0,
            'manifest_outcome': 0.0,
            'archetypes': 0.0
        }

        keywords = playlist.get('keywords', {})
        primary_keywords = keywords.get('primary', [])
        secondary_keywords = keywords.get('secondary', [])

        # Check for deprioritize keywords (lowers score if present)
        deprioritize = playlist.get('deprioritize_if', {}).get('keywords', [])
        combined_text = self._get_combined_text(session_data).lower()
        deprioritize_factor = 1.0
        for kw in deprioritize:
            if kw.lower() in combined_text:
                deprioritize_factor = 0.5
                break

        # Signal 1: Title matching (highest weight)
        title = session_data.get('title', '').lower()
        signals['title'] = self._match_keywords(title, primary_keywords, secondary_keywords)

        # Signal 2: Description matching
        description = session_data.get('description', '').lower()
        signals['description'] = self._match_keywords(description, primary_keywords, secondary_keywords)

        # Signal 3: Tags matching
        tags = session_data.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',')]
        tags_text = ' '.join(str(t) for t in tags).lower()
        signals['tags'] = self._match_keywords(tags_text, primary_keywords, secondary_keywords)

        # Signal 4: Manifest fields (desired_outcome, style)
        manifest = session_data.get('manifest', {})
        manifest_fields = playlist.get('manifest_fields', {})
        signals['manifest_outcome'] = self._match_manifest_fields(manifest, manifest_fields)

        # Signal 5: Archetype matching
        archetypes = self._extract_archetypes(session_data)
        signals['archetypes'] = self._match_keywords(
            ' '.join(archetypes).lower(),
            primary_keywords,
            secondary_keywords
        )

        # Calculate weighted total
        total = (
            signals['title'] * self.weights.get('title', 0.35) +
            signals['description'] * self.weights.get('description', 0.25) +
            signals['tags'] * self.weights.get('tags', 0.15) +
            signals['manifest_outcome'] * self.weights.get('manifest_outcome', 0.15) +
            signals['archetypes'] * self.weights.get('archetypes', 0.10)
        )

        # Apply deprioritize factor
        total *= deprioritize_factor

        return min(total, 1.0), signals

    def _match_keywords(
        self,
        text: str,
        primary: List[str],
        secondary: List[str]
    ) -> float:
        """
        Match text against keyword lists.

        Returns 0-1 score with diminishing returns.
        """
        if not text:
            return 0.0

        # Count matches (primary worth more)
        primary_matches = sum(1 for kw in primary if kw.lower() in text)
        secondary_matches = sum(1 for kw in secondary if kw.lower() in text)

        # Weighted score
        score = (primary_matches * 1.0 + secondary_matches * 0.5)

        if not primary and not secondary:
            return 0.0

        # Normalize with diminishing returns
        # Scoring: 1 primary = 0.5, 1 secondary = 0.35
        # Additional matches add less (diminishing returns)
        if score == 0:
            return 0.0

        # Different base score for primary vs secondary matches
        if primary_matches >= 1:
            # At least one primary match: start at 0.5
            base = 0.5
            additional = (score - 1) * 0.1
        else:
            # Only secondary matches: start at 0.35
            base = 0.35
            additional = (score - 0.5) * 0.1

        normalized = min(base + additional, 1.0)
        return normalized

    def _match_manifest_fields(self, manifest: dict, required_fields: dict) -> float:
        """Check if manifest fields match required values."""
        if not required_fields or not manifest:
            return 0.0

        matches = 0
        total = len(required_fields)

        for field_path, acceptable_values in required_fields.items():
            # Handle nested paths like 'session.desired_outcome' or 'sound_bed.percussion.enabled'
            value = self._get_nested_value(manifest, field_path)

            if value is None:
                # Try with 'session.' prefix
                value = self._get_nested_value(manifest, f'session.{field_path}')

            if value is not None:
                if isinstance(acceptable_values, list):
                    if value in acceptable_values or str(value).lower() in [str(v).lower() for v in acceptable_values]:
                        matches += 1
                elif isinstance(acceptable_values, dict):
                    # Handle nested dict matching (e.g., percussion.enabled = true)
                    if self._dict_matches(value, acceptable_values):
                        matches += 1
                elif value == acceptable_values:
                    matches += 1

        return matches / total if total > 0 else 0.0

    def _dict_matches(self, actual: Any, expected: dict) -> bool:
        """Check if actual value matches expected dict structure."""
        if not isinstance(actual, dict):
            return False

        for key, expected_value in expected.items():
            if key not in actual:
                return False
            if isinstance(expected_value, dict):
                if not self._dict_matches(actual[key], expected_value):
                    return False
            elif actual[key] != expected_value:
                return False

        return True

    def _get_nested_value(self, data: dict, path: str) -> Any:
        """Get nested dictionary value from dot-separated path."""
        if not data:
            return None

        keys = path.split('.')
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def _check_duration_playlists(self, session_data: Dict[str, Any]) -> List[PlaylistMatch]:
        """Check if session matches any duration-based playlists."""
        matches = []
        duration = session_data.get('duration_minutes', 0)

        if not duration:
            # Try to get from manifest
            manifest = session_data.get('manifest', {})
            duration = manifest.get('session', {}).get('duration', 0)
            if not duration:
                duration = manifest.get('duration', 0)

            # Handle duration as dict (e.g., {'target_minutes': 25, 'sections': {...}})
            if isinstance(duration, dict):
                duration = duration.get('target_minutes', 0)

            # Handle duration in seconds (>100 likely means seconds)
            if isinstance(duration, (int, float)) and duration > 100:
                duration = int(duration) // 60

        if not duration:
            return matches

        for slug, playlist in self.config.get('duration_playlists', {}).items():
            duration_range = playlist.get('duration_range', {})
            min_mins = duration_range.get('min_minutes', 0)
            max_mins = duration_range.get('max_minutes', 999)

            if min_mins <= duration <= max_mins:
                # Also check for keyword matches to boost confidence
                keywords = playlist.get('keywords', {})
                primary = keywords.get('primary', [])
                secondary = keywords.get('secondary', [])

                combined_text = self._get_combined_text(session_data).lower()
                keyword_boost = self._match_keywords(combined_text, primary, secondary) * 0.1

                matches.append(PlaylistMatch(
                    playlist_id=playlist.get('youtube_id', ''),
                    name=playlist['name'],
                    slug=slug,
                    confidence=0.85 + keyword_boost,  # Duration is a strong signal
                    signals={'duration': 1.0, 'keywords': keyword_boost},
                    playlist_type='duration'
                ))

        return matches

    def _extract_archetypes(self, session_data: Dict[str, Any]) -> List[str]:
        """Extract archetype names from session data."""
        archetypes = []

        # Direct archetypes field
        arch_data = session_data.get('archetypes', [])
        if isinstance(arch_data, list):
            for arch in arch_data:
                if isinstance(arch, dict):
                    name = arch.get('name', arch.get('archetype', ''))
                    if name:
                        archetypes.append(name)
                elif isinstance(arch, str):
                    archetypes.append(arch)

        # From manifest
        manifest = session_data.get('manifest', {})
        manifest_archetypes = manifest.get('archetypes', [])
        if isinstance(manifest_archetypes, list):
            for arch in manifest_archetypes:
                if isinstance(arch, dict):
                    name = arch.get('name', arch.get('archetype', ''))
                    if name and name not in archetypes:
                        archetypes.append(name)
                elif isinstance(arch, str) and arch not in archetypes:
                    archetypes.append(arch)

        return archetypes

    def _get_combined_text(self, session_data: Dict[str, Any]) -> str:
        """Combine all text fields for searching."""
        parts = [
            session_data.get('title', ''),
            session_data.get('description', ''),
        ]

        tags = session_data.get('tags', [])
        if isinstance(tags, list):
            parts.append(' '.join(str(t) for t in tags))
        elif isinstance(tags, str):
            parts.append(tags)

        return ' '.join(parts)

    def get_playlists_for_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: get playlist assignments for a session.

        Args:
            session_data: Session metadata dict

        Returns:
            Dict with:
                - playlists: List of playlist IDs to add video to
                - primary: Best match playlist name
                - primary_slug: Best match playlist slug
                - confidence: Highest confidence score
                - needs_review: Whether manual review is suggested
                - details: Full match details for logging
        """
        matches = self.classify(session_data)
        config = self.config.get('classification', {})

        min_confidence = config.get('min_confidence', 0.4)
        max_playlists = config.get('max_playlists_per_video', 3)
        include_master = config.get('always_include_master', True)
        high_confidence = config.get('high_confidence', 0.7)

        # Filter by confidence threshold
        qualifying_matches = [m for m in matches if m.confidence >= min_confidence]

        # Apply multi-match strategy
        strategy = config.get('multi_match_strategy', 'top_n')
        if strategy == 'top_n':
            top_n = config.get('multi_match_count', 3)
            selected_matches = qualifying_matches[:top_n]
        else:  # 'all'
            selected_matches = qualifying_matches[:max_playlists]

        # Build playlist ID list
        playlist_ids = []

        # Add master playlist if configured
        if include_master:
            master = self.config.get('master_playlist', {})
            master_id = master.get('youtube_id', '')
            if master_id:
                playlist_ids.append(master_id)

        # Add matched playlists
        for match in selected_matches:
            if match.playlist_id and match.playlist_id not in playlist_ids:
                playlist_ids.append(match.playlist_id)

        # Use fallback if no matches
        if not selected_matches:
            fallback = self.config.get('fallback_playlist', {})
            fallback_id = fallback.get('youtube_id', '')
            if fallback_id:
                playlist_ids.append(fallback_id)

        # Determine if manual review is needed
        needs_review = (
            len(selected_matches) == 0 or
            (len(selected_matches) > 0 and selected_matches[0].confidence < high_confidence) or
            any(m.requires_manual_review for m in selected_matches)
        )

        primary_match = selected_matches[0] if selected_matches else None

        return {
            'playlists': playlist_ids,
            'primary': primary_match.name if primary_match else 'Uncategorized',
            'primary_slug': primary_match.slug if primary_match else 'uncategorized',
            'confidence': primary_match.confidence if primary_match else 0.0,
            'needs_review': needs_review,
            'match_count': len(selected_matches),
            'details': [
                {
                    'name': m.name,
                    'slug': m.slug,
                    'confidence': round(m.confidence, 3),
                    'type': m.playlist_type,
                    'signals': {k: round(v, 3) for k, v in m.signals.items()},
                    'manual_review': m.requires_manual_review
                }
                for m in matches[:5]  # Top 5 for logging
            ]
        }


# ============================================================================
# Utility Functions
# ============================================================================

def classify_session(session_path: Path) -> Dict[str, Any]:
    """
    Convenience function to classify a session from its path.

    Args:
        session_path: Path to session directory

    Returns:
        Playlist assignment result
    """
    session_path = Path(session_path)

    # Load manifest
    manifest_path = session_path / 'manifest.yaml'
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with open(manifest_path) as f:
        manifest = yaml.safe_load(f) or {}

    # Extract session data
    session_info = manifest.get('session', {})
    youtube_info = manifest.get('youtube', {})

    # Get duration, handling various formats
    duration = session_info.get('duration', manifest.get('duration', 0))

    # Handle duration as dict (e.g., {'target_minutes': 25, 'sections': {...}})
    if isinstance(duration, dict):
        duration = duration.get('target_minutes', 0)

    # Handle duration in seconds (>100 likely means seconds)
    if isinstance(duration, (int, float)) and duration > 100:
        duration = int(duration) // 60

    # Build session data dict
    session_data = {
        'title': (
            youtube_info.get('optimized_title') or
            youtube_info.get('title') or
            session_info.get('topic') or
            manifest.get('topic', session_path.name)
        ),
        'description': (
            session_info.get('description') or
            manifest.get('description', '')
        ),
        'tags': youtube_info.get('tags', []),
        'duration_minutes': duration,
        'archetypes': manifest.get('archetypes', []),
        'manifest': manifest
    }

    classifier = PlaylistClassifier()
    return classifier.get_playlists_for_session(session_data)


def classify_all_sessions(sessions_dir: Path = None) -> Dict[str, Dict]:
    """
    Classify all sessions in the sessions directory.

    Args:
        sessions_dir: Path to sessions directory. Uses default if not provided.

    Returns:
        Dict mapping session names to classification results
    """
    if sessions_dir is None:
        sessions_dir = Path(__file__).parent.parent.parent / 'sessions'

    results = {}

    for session_path in sessions_dir.iterdir():
        if not session_path.is_dir():
            continue
        if session_path.name.startswith('_'):
            continue

        manifest_path = session_path / 'manifest.yaml'
        if not manifest_path.exists():
            continue

        try:
            result = classify_session(session_path)
            results[session_path.name] = result
        except Exception as e:
            logger.warning(f"Failed to classify {session_path.name}: {e}")
            results[session_path.name] = {'error': str(e)}

    return results


# ============================================================================
# CLI Interface
# ============================================================================

if __name__ == '__main__':
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description='Classify Dreamweaving sessions for YouTube playlists')
    parser.add_argument('session', nargs='?', help='Session name or path to classify')
    parser.add_argument('--all', action='store_true', help='Classify all sessions')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output with signal details')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    if args.all:
        results = classify_all_sessions()

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n{'='*60}")
            print("SESSION CLASSIFICATION RESULTS")
            print(f"{'='*60}\n")

            for session_name, result in sorted(results.items()):
                if 'error' in result:
                    print(f"  {session_name}: ERROR - {result['error']}")
                else:
                    conf = result['confidence']
                    status = "HIGH" if conf >= 0.7 else "MEDIUM" if conf >= 0.4 else "LOW"
                    review = " [REVIEW]" if result['needs_review'] else ""
                    print(f"  {session_name}: {result['primary']} ({conf:.2f} {status}){review}")

            print(f"\nTotal: {len(results)} sessions")

    elif args.session:
        # Resolve session path
        session_input = args.session
        if '/' in session_input or session_input.endswith('manifest.yaml'):
            session_path = Path(session_input)
            if session_path.name == 'manifest.yaml':
                session_path = session_path.parent
        else:
            session_path = Path(__file__).parent.parent.parent / 'sessions' / session_input

        if not session_path.exists():
            print(f"Session not found: {session_path}", file=sys.stderr)
            sys.exit(1)

        result = classify_session(session_path)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"CLASSIFICATION: {session_path.name}")
            print(f"{'='*60}\n")

            print(f"Primary Playlist: {result['primary']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Needs Review: {'Yes' if result['needs_review'] else 'No'}")
            print(f"Total Matches: {result['match_count']}")
            print(f"Playlists to Add: {len(result['playlists'])}")

            if args.verbose and result['details']:
                print(f"\nTop Matches:")
                for i, detail in enumerate(result['details'], 1):
                    print(f"  {i}. {detail['name']} ({detail['type']})")
                    print(f"     Confidence: {detail['confidence']:.3f}")
                    if detail['signals']:
                        signals_str = ', '.join(f"{k}={v:.2f}" for k, v in detail['signals'].items() if v > 0)
                        print(f"     Signals: {signals_str}")

    else:
        parser.print_help()
        sys.exit(1)
