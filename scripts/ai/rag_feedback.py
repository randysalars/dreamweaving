"""
RAG Feedback Tracker - Tracks query effectiveness for self-improving knowledge retrieval.

This module provides:
1. Query tracking: Record what queries were used for each session
2. Effectiveness correlation: Link queries to session outcomes
3. Query pattern boosting: Identify and boost successful query patterns
4. Semantic caching: Cache frequently successful queries

Part of the Recursive Improver system for self-improving Dreamweaving sessions.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml
import hashlib
import json


@dataclass
class QueryRecord:
    """Records a RAG query and its context."""

    query_id: str
    query_text: str
    query_embedding_hash: str  # Hash of embedding for deduplication
    created_at: datetime

    # Query context
    session_name: Optional[str] = None
    content_type: Optional[str] = None  # archetype, realm, frequency, etc.
    query_purpose: str = "generation"  # generation, research, validation

    # Results
    result_count: int = 0
    result_ids: List[str] = field(default_factory=list)
    top_scores: List[float] = field(default_factory=list)  # Top 3 similarity scores
    execution_time_ms: float = 0.0

    # Outcome tracking (set later)
    session_outcome_id: Optional[str] = None
    outcome_quality_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueryRecord':
        if data.get('created_at') and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class QueryPatternEffectiveness:
    """Tracks effectiveness of a query pattern over time."""

    pattern_hash: str  # Hash of normalized query
    canonical_query: str  # Representative query text
    content_type: str

    # Usage tracking
    times_used: int = 0
    sessions_used_in: List[str] = field(default_factory=list)

    # Effectiveness metrics
    avg_quality_score: float = 50.0
    avg_result_relevance: float = 0.5  # Average top similarity score
    success_rate: float = 0.0  # Percentage of successful sessions using this

    # Time tracking
    first_used: Optional[datetime] = None
    last_used: Optional[datetime] = None

    # Context where effective
    best_outcomes: List[str] = field(default_factory=list)  # Outcomes where this works well
    best_topics: List[str] = field(default_factory=list)  # Topics where this works well

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        for key in ['first_used', 'last_used']:
            if data.get(key) and isinstance(data[key], datetime):
                data[key] = data[key].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueryPatternEffectiveness':
        for key in ['first_used', 'last_used']:
            if data.get(key) and isinstance(data[key], str):
                data[key] = datetime.fromisoformat(data[key])
        return cls(**data)


class RAGFeedbackTracker:
    """
    Tracks RAG query effectiveness and correlates with session outcomes.

    Manages:
    - rag_query_records.yaml: Individual query records
    - rag_query_patterns.yaml: Aggregated pattern effectiveness
    - rag_query_cache.yaml: Semantic query cache
    """

    # Cache settings
    MAX_CACHE_SIZE = 500
    CACHE_SCORE_THRESHOLD = 70.0  # Minimum effectiveness to cache

    def __init__(self, store_path: Path):
        """
        Initialize RAG feedback tracker.

        Args:
            store_path: Path to knowledge/feedback/ directory
        """
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)

        self.queries_file = self.store_path / 'rag_query_records.yaml'
        self.patterns_file = self.store_path / 'rag_query_patterns.yaml'
        self.cache_file = self.store_path / 'rag_query_cache.yaml'

        self._initialize_files()

    def _initialize_files(self):
        """Create empty files if they don't exist."""
        for file_path in [self.queries_file, self.patterns_file, self.cache_file]:
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    yaml.dump({'records': []}, f)

    def _load_yaml(self, file_path: Path) -> Dict:
        """Load YAML file safely."""
        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) or {'records': []}
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
            return {'records': []}

    def _save_yaml(self, file_path: Path, data: Dict):
        """Save YAML file with backup."""
        if file_path.exists():
            backup_path = file_path.with_suffix('.yaml.bak')
            file_path.rename(backup_path)

        try:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            backup_path = file_path.with_suffix('.yaml.bak')
            if backup_path.exists():
                backup_path.rename(file_path)
            raise e

    # -------------------------------------------------------------------------
    # Query Recording
    # -------------------------------------------------------------------------

    def record_query(
        self,
        query_text: str,
        results: List[Dict[str, Any]],
        session_name: Optional[str] = None,
        content_type: Optional[str] = None,
        query_purpose: str = "generation",
        execution_time_ms: float = 0.0,
        embedding: Optional[List[float]] = None,
    ) -> str:
        """
        Record a RAG query and its results.

        Args:
            query_text: The query string
            results: List of result dicts with 'id' and 'score' keys
            session_name: Associated session name
            content_type: Type of content queried
            query_purpose: Purpose of query
            execution_time_ms: Query execution time
            embedding: Optional query embedding for hash

        Returns:
            query_id: ID of recorded query
        """
        # Generate IDs
        query_id = self._generate_query_id(query_text)
        embedding_hash = self._hash_embedding(embedding) if embedding else self._hash_text(query_text)

        record = QueryRecord(
            query_id=query_id,
            query_text=query_text,
            query_embedding_hash=embedding_hash,
            created_at=datetime.now(),
            session_name=session_name,
            content_type=content_type,
            query_purpose=query_purpose,
            result_count=len(results),
            result_ids=[r.get('id', '') for r in results[:10]],
            top_scores=[r.get('score', 0.0) for r in results[:3]],
            execution_time_ms=execution_time_ms,
        )

        # Save record
        data = self._load_yaml(self.queries_file)
        data['records'].append(record.to_dict())
        data['last_updated'] = datetime.now().isoformat()
        self._save_yaml(self.queries_file, data)

        # Update pattern tracking
        self._update_pattern(query_text, content_type, results)

        return query_id

    def link_query_to_outcome(
        self,
        query_id: str,
        outcome_id: str,
        quality_score: float
    ):
        """
        Link a query to its session outcome.

        Called after session generation completes.
        """
        data = self._load_yaml(self.queries_file)

        for record in data.get('records', []):
            if record.get('query_id') == query_id:
                record['session_outcome_id'] = outcome_id
                record['outcome_quality_score'] = quality_score
                break

        self._save_yaml(self.queries_file, data)

        # Update pattern effectiveness with outcome
        query_record = self.get_query(query_id)
        if query_record:
            self._update_pattern_with_outcome(
                query_record.query_text,
                query_record.content_type,
                quality_score,
                query_record.session_name
            )

    def get_query(self, query_id: str) -> Optional[QueryRecord]:
        """Get a query record by ID."""
        data = self._load_yaml(self.queries_file)
        for record in data.get('records', []):
            if record.get('query_id') == query_id:
                return QueryRecord.from_dict(record)
        return None

    def get_queries_for_session(self, session_name: str) -> List[QueryRecord]:
        """Get all queries used for a session."""
        data = self._load_yaml(self.queries_file)
        return [
            QueryRecord.from_dict(r)
            for r in data.get('records', [])
            if r.get('session_name') == session_name
        ]

    # -------------------------------------------------------------------------
    # Pattern Tracking
    # -------------------------------------------------------------------------

    def _update_pattern(
        self,
        query_text: str,
        content_type: Optional[str],
        results: List[Dict]
    ):
        """Update or create pattern tracking record."""
        pattern_hash = self._hash_query_pattern(query_text)
        content_type = content_type or "general"

        data = self._load_yaml(self.patterns_file)
        records = data.get('records', [])

        # Find existing pattern
        existing_idx = next(
            (i for i, r in enumerate(records) if r.get('pattern_hash') == pattern_hash),
            None
        )

        if existing_idx is not None:
            pattern = QueryPatternEffectiveness.from_dict(records[existing_idx])
        else:
            pattern = QueryPatternEffectiveness(
                pattern_hash=pattern_hash,
                canonical_query=query_text,
                content_type=content_type,
                first_used=datetime.now()
            )

        # Update usage
        pattern.times_used += 1
        pattern.last_used = datetime.now()

        # Update relevance score
        if results:
            top_score = results[0].get('score', 0.0) if results else 0.0
            alpha = 0.3
            pattern.avg_result_relevance = (
                (1 - alpha) * pattern.avg_result_relevance +
                alpha * top_score
            )

        # Save
        if existing_idx is not None:
            records[existing_idx] = pattern.to_dict()
        else:
            records.append(pattern.to_dict())

        data['records'] = records
        data['last_updated'] = datetime.now().isoformat()
        self._save_yaml(self.patterns_file, data)

    def _update_pattern_with_outcome(
        self,
        query_text: str,
        content_type: Optional[str],
        quality_score: float,
        session_name: Optional[str] = None
    ):
        """Update pattern effectiveness with session outcome."""
        pattern_hash = self._hash_query_pattern(query_text)

        data = self._load_yaml(self.patterns_file)
        records = data.get('records', [])

        for i, record in enumerate(records):
            if record.get('pattern_hash') == pattern_hash:
                pattern = QueryPatternEffectiveness.from_dict(record)

                # Update quality score
                alpha = 0.3
                pattern.avg_quality_score = (
                    (1 - alpha) * pattern.avg_quality_score +
                    alpha * quality_score
                )

                # Track session
                if session_name and session_name not in pattern.sessions_used_in:
                    pattern.sessions_used_in.append(session_name)
                    pattern.sessions_used_in = pattern.sessions_used_in[-20:]

                # Update success rate
                successful = sum(1 for s in pattern.sessions_used_in if quality_score >= 70)
                pattern.success_rate = successful / max(len(pattern.sessions_used_in), 1)

                records[i] = pattern.to_dict()
                break

        data['records'] = records
        self._save_yaml(self.patterns_file, data)

        # Update cache if highly effective
        if quality_score >= self.CACHE_SCORE_THRESHOLD:
            self._add_to_cache(query_text, content_type, quality_score)

    def get_effective_patterns(
        self,
        content_type: Optional[str] = None,
        min_uses: int = 3,
        min_quality: float = 60.0,
        limit: int = 20
    ) -> List[QueryPatternEffectiveness]:
        """
        Get patterns ranked by effectiveness.

        Args:
            content_type: Filter by content type
            min_uses: Minimum times used
            min_quality: Minimum quality score
            limit: Maximum to return

        Returns:
            List of effective patterns sorted by quality score
        """
        data = self._load_yaml(self.patterns_file)
        patterns = []

        for record in data.get('records', []):
            if record.get('times_used', 0) < min_uses:
                continue
            if record.get('avg_quality_score', 0) < min_quality:
                continue
            if content_type and record.get('content_type') != content_type:
                continue

            patterns.append(QueryPatternEffectiveness.from_dict(record))

        # Sort by quality score
        patterns.sort(key=lambda p: p.avg_quality_score, reverse=True)

        return patterns[:limit]

    def suggest_queries(
        self,
        topic: str,
        desired_outcome: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: int = 5
    ) -> List[str]:
        """
        Suggest effective queries for a given context.

        Based on patterns that worked well for similar topics/outcomes.
        """
        effective = self.get_effective_patterns(
            content_type=content_type,
            min_uses=2,
            min_quality=65.0,
            limit=limit * 3
        )

        # Simple relevance scoring based on keyword overlap
        suggestions = []
        topic_words = set(topic.lower().split())

        for pattern in effective:
            query_words = set(pattern.canonical_query.lower().split())
            overlap = len(topic_words & query_words)
            if overlap > 0:
                suggestions.append((pattern.canonical_query, pattern.avg_quality_score + overlap * 5))

        # Sort by combined score
        suggestions.sort(key=lambda x: x[1], reverse=True)

        return [s[0] for s in suggestions[:limit]]

    # -------------------------------------------------------------------------
    # Semantic Caching
    # -------------------------------------------------------------------------

    def _add_to_cache(
        self,
        query_text: str,
        content_type: Optional[str],
        quality_score: float
    ):
        """Add a successful query to the cache."""
        data = self._load_yaml(self.cache_file)
        cache = data.get('records', [])

        cache_key = self._hash_query_pattern(query_text)

        # Check if already cached
        existing = next((c for c in cache if c.get('cache_key') == cache_key), None)

        if existing:
            # Update score
            existing['quality_score'] = max(existing.get('quality_score', 0), quality_score)
            existing['last_used'] = datetime.now().isoformat()
            existing['use_count'] = existing.get('use_count', 0) + 1
        else:
            # Add new cache entry
            cache.append({
                'cache_key': cache_key,
                'query_text': query_text,
                'content_type': content_type or 'general',
                'quality_score': quality_score,
                'created_at': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat(),
                'use_count': 1,
            })

        # Trim cache if too large
        if len(cache) > self.MAX_CACHE_SIZE:
            # Remove lowest scoring entries
            cache.sort(key=lambda c: c.get('quality_score', 0), reverse=True)
            cache = cache[:self.MAX_CACHE_SIZE]

        data['records'] = cache
        data['last_updated'] = datetime.now().isoformat()
        self._save_yaml(self.cache_file, data)

    def get_cached_query(
        self,
        query_text: str,
        similarity_threshold: float = 0.9
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a similar query is cached.

        For now uses exact hash matching. Could be extended with
        embedding similarity.
        """
        cache_key = self._hash_query_pattern(query_text)
        data = self._load_yaml(self.cache_file)

        for entry in data.get('records', []):
            if entry.get('cache_key') == cache_key:
                # Update use count
                entry['use_count'] = entry.get('use_count', 0) + 1
                entry['last_used'] = datetime.now().isoformat()
                self._save_yaml(self.cache_file, data)
                return entry

        return None

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        data = self._load_yaml(self.cache_file)
        cache = data.get('records', [])

        if not cache:
            return {'size': 0, 'avg_quality': 0, 'total_uses': 0}

        return {
            'size': len(cache),
            'avg_quality': sum(c.get('quality_score', 0) for c in cache) / len(cache),
            'total_uses': sum(c.get('use_count', 0) for c in cache),
            'content_types': list(set(c.get('content_type', 'general') for c in cache)),
        }

    # -------------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------------

    def _generate_query_id(self, query_text: str) -> str:
        """Generate unique query ID."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_input = f"{query_text}-{timestamp}"
        short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"query-{short_hash}"

    def _hash_query_pattern(self, query_text: str) -> str:
        """Hash normalized query for pattern matching."""
        # Normalize: lowercase, remove extra whitespace
        normalized = ' '.join(query_text.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()[:12]

    def _hash_text(self, text: str) -> str:
        """Hash text content."""
        return hashlib.md5(text.encode()).hexdigest()[:12]

    def _hash_embedding(self, embedding: List[float]) -> str:
        """Hash embedding vector."""
        # Round to reduce precision, then hash
        rounded = [round(x, 4) for x in embedding[:10]]
        return hashlib.md5(json.dumps(rounded).encode()).hexdigest()[:12]

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about RAG feedback."""
        queries_data = self._load_yaml(self.queries_file)
        patterns_data = self._load_yaml(self.patterns_file)

        queries = queries_data.get('records', [])
        patterns = patterns_data.get('records', [])

        # Query stats
        queries_with_outcomes = [q for q in queries if q.get('outcome_quality_score')]
        avg_quality = (
            sum(q.get('outcome_quality_score', 0) for q in queries_with_outcomes) /
            max(len(queries_with_outcomes), 1)
        )

        # Pattern stats
        effective_patterns = [p for p in patterns if p.get('avg_quality_score', 0) >= 70]

        cache_stats = self.get_cache_stats()

        return {
            'total_queries': len(queries),
            'queries_with_outcomes': len(queries_with_outcomes),
            'avg_outcome_quality': round(avg_quality, 1),
            'total_patterns': len(patterns),
            'effective_patterns': len(effective_patterns),
            'cache_size': cache_stats['size'],
            'cache_total_uses': cache_stats['total_uses'],
        }


# Factory function
def create_rag_feedback_tracker(project_root: Path) -> RAGFeedbackTracker:
    """Create a RAG feedback tracker with standard configuration."""
    feedback_path = project_root / 'knowledge' / 'feedback'
    return RAGFeedbackTracker(feedback_path)
