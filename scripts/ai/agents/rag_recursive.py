"""
RAG Recursive Agent - Self-improving knowledge retrieval.

This agent enhances RAG queries by:
1. Tracking which queries produce good sessions
2. Boosting successful query patterns
3. Using relationship traversal for richer context
4. Implementing semantic query caching

Part of the Recursive Improver system for self-improving Dreamweaving sessions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import time

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


@dataclass
class RAGContext:
    """Container for RAG query context and results."""

    topic: str
    desired_outcome: Optional[str] = None
    archetypes: List[str] = field(default_factory=list)

    # Query tracking
    query_ids: List[str] = field(default_factory=list)
    queries_executed: List[str] = field(default_factory=list)

    # Results
    context_data: Dict[str, Any] = field(default_factory=dict)
    token_estimate: int = 0

    # Cache hits
    cache_hits: int = 0
    cache_misses: int = 0

    def to_prompt_context(self) -> str:
        """Format context for injection into prompts."""
        lines = [
            "# Knowledge Context",
            "",
        ]

        # Archetypes
        if self.context_data.get('archetypes_data'):
            lines.append("## Archetypes")
            for arch in self.context_data['archetypes_data']:
                name = arch.get('Name', arch.get('name', 'Unknown'))
                shadow = arch.get('Shadow Aspect', '')
                gift = arch.get('Gift', '')
                lines.append(f"- **{name}**: Shadow={shadow}, Gift={gift}")

                # Include expanded realms
                if arch.get('realms_expanded'):
                    for realm in arch['realms_expanded'][:2]:
                        realm_name = realm.get('Name', realm.get('name', ''))
                        atmosphere = realm.get('Atmosphere', '')[:100]
                        lines.append(f"  - Realm: {realm_name} - {atmosphere}")
            lines.append("")

        # Frequencies
        if self.context_data.get('frequencies_data'):
            lines.append("## Frequencies")
            for freq in self.context_data['frequencies_data']:
                name = freq.get('Name', freq.get('name', ''))
                hz = freq.get('Hz Range', '')
                state = freq.get('Brainwave State', '')
                lines.append(f"- **{name}**: {hz} Hz, {state}")
            lines.append("")

        # Lore
        if self.context_data.get('lore_data'):
            lines.append("## Relevant Lore")
            for lore in self.context_data['lore_data'][:3]:
                name = lore.get('Name', lore.get('title', ''))
                desc = lore.get('Description', lore.get('content', ''))[:150]
                lines.append(f"- **{name}**: {desc}...")
            lines.append("")

        # Suggested queries for future use
        if self.context_data.get('suggested_queries'):
            lines.append("## Suggested Query Patterns")
            for q in self.context_data['suggested_queries']:
                lines.append(f"- {q}")
            lines.append("")

        return "\n".join(lines)


class RAGRecursiveAgent:
    """
    Self-improving RAG agent for knowledge retrieval.

    Capabilities:
    1. Smart query construction based on past effectiveness
    2. Deep relationship traversal for rich context
    3. Query effectiveness tracking
    4. Semantic caching for fast retrieval
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
    ):
        """
        Initialize RAG recursive agent.

        Args:
            project_root: Path to project root
        """
        self.project_root = project_root or PROJECT_ROOT

        # Lazy-loaded components
        self._feedback_tracker = None
        self._embeddings_pipeline = None

    def _get_feedback_tracker(self):
        """Get or create RAG feedback tracker."""
        if self._feedback_tracker is None:
            try:
                from scripts.ai.rag_feedback import RAGFeedbackTracker
                feedback_path = self.project_root / "knowledge" / "feedback"
                self._feedback_tracker = RAGFeedbackTracker(feedback_path)
            except ImportError:
                return None
        return self._feedback_tracker

    def _get_embeddings_pipeline(self):
        """Get or create embeddings pipeline."""
        if self._embeddings_pipeline is None:
            try:
                from scripts.ai.notion_embeddings_pipeline import NotionEmbeddingsPipeline
                self._embeddings_pipeline = NotionEmbeddingsPipeline()
            except ImportError:
                return None
        return self._embeddings_pipeline

    def prepare_context(
        self,
        topic: str,
        desired_outcome: Optional[str] = None,
        archetypes: Optional[List[str]] = None,
        depth: int = 2,
        use_cache: bool = True,
        max_tokens: int = 2000,
    ) -> RAGContext:
        """
        Prepare rich context for session generation.

        Uses deep relationship traversal and query effectiveness
        tracking to provide optimal context.

        Args:
            topic: Session topic/theme
            desired_outcome: Desired transformation outcome
            archetypes: Specific archetypes to include
            depth: Relationship traversal depth
            use_cache: Whether to check query cache first
            max_tokens: Token budget for context

        Returns:
            RAGContext with prepared knowledge
        """
        context = RAGContext(
            topic=topic,
            desired_outcome=desired_outcome,
            archetypes=archetypes or [],
        )

        tracker = self._get_feedback_tracker()

        # Check cache for effective queries
        cache_hits = 0
        if use_cache and tracker:
            # Try to find cached effective queries for this topic
            cached = tracker.get_cached_query(topic)
            if cached:
                cache_hits += 1
                context.cache_hits = cache_hits

        # Build rich context using deep traversal
        try:
            from scripts.ai.knowledge_tools import build_rich_context

            start_time = time.time()
            context.context_data = build_rich_context(
                topic=topic,
                desired_outcome=desired_outcome,
                archetypes=archetypes,
                depth=depth,
                max_tokens_estimate=max_tokens,
            )
            execution_time = (time.time() - start_time) * 1000

            context.token_estimate = context.context_data.get('token_estimate', 0)

            # Record the query
            if tracker:
                query_id = tracker.record_query(
                    query_text=topic,
                    results=[],  # build_rich_context doesn't return traditional results
                    session_name=None,  # Will be linked later
                    content_type="rich_context",
                    query_purpose="generation",
                    execution_time_ms=execution_time,
                )
                context.query_ids.append(query_id)
                context.queries_executed.append(topic)

        except ImportError:
            # Fallback if knowledge_tools not available
            context.context_data = {
                'topic': topic,
                'desired_outcome': desired_outcome,
                'archetypes_data': [],
                'frequencies_data': [],
                'lore_data': [],
            }

        # Execute additional semantic searches if we have embeddings
        pipeline = self._get_embeddings_pipeline()
        if pipeline and tracker:
            # Get suggested queries from feedback
            suggestions = tracker.suggest_queries(
                topic=topic,
                desired_outcome=desired_outcome,
                limit=3
            )

            for query in suggestions:
                if context.token_estimate >= max_tokens:
                    break

                start_time = time.time()
                try:
                    results = pipeline.search(query, limit=3)
                    execution_time = (time.time() - start_time) * 1000

                    # Record query
                    query_id = tracker.record_query(
                        query_text=query,
                        results=[{'id': r.get('id', ''), 'score': r.get('score', 0)} for r in results],
                        content_type="semantic_search",
                        query_purpose="generation",
                        execution_time_ms=execution_time,
                    )
                    context.query_ids.append(query_id)
                    context.queries_executed.append(query)

                    # Add results to context (avoiding duplicates)
                    for result in results:
                        content = result.get('content', '')[:200]
                        if content and content not in str(context.context_data):
                            if 'additional_content' not in context.context_data:
                                context.context_data['additional_content'] = []
                            context.context_data['additional_content'].append({
                                'query': query,
                                'content': content,
                                'score': result.get('score', 0),
                            })
                            context.token_estimate += 50

                except Exception:
                    pass

        context.cache_misses = len(context.queries_executed) - context.cache_hits

        return context

    def record_outcome(
        self,
        context: RAGContext,
        session_name: str,
        outcome_id: str,
        quality_score: float,
    ):
        """
        Record the outcome of queries used for a session.

        Links queries to session outcomes for effectiveness tracking.

        Args:
            context: RAGContext from prepare_context
            session_name: Name of generated session
            outcome_id: Outcome record ID
            quality_score: Quality score of generated session
        """
        tracker = self._get_feedback_tracker()
        if not tracker:
            return

        # Link each query to the outcome
        for query_id in context.query_ids:
            tracker.link_query_to_outcome(
                query_id=query_id,
                outcome_id=outcome_id,
                quality_score=quality_score,
            )

    def get_effective_queries(
        self,
        content_type: Optional[str] = None,
        min_quality: float = 70.0,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get queries that have proven effective.

        Args:
            content_type: Filter by content type
            min_quality: Minimum quality score
            limit: Maximum to return

        Returns:
            List of effective query patterns with scores
        """
        tracker = self._get_feedback_tracker()
        if not tracker:
            return []

        patterns = tracker.get_effective_patterns(
            content_type=content_type,
            min_quality=min_quality,
            limit=limit,
        )

        return [
            {
                'query': p.canonical_query,
                'content_type': p.content_type,
                'quality_score': p.avg_quality_score,
                'times_used': p.times_used,
                'success_rate': p.success_rate,
            }
            for p in patterns
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG agent statistics."""
        tracker = self._get_feedback_tracker()
        if not tracker:
            return {'error': 'Feedback tracker not available'}

        stats = tracker.get_statistics()
        cache_stats = tracker.get_cache_stats()

        return {
            **stats,
            'cache_size': cache_stats.get('size', 0),
            'cache_hit_rate': 'N/A',  # Would need to track hits/misses over time
        }


# Factory function
def create_rag_recursive_agent(project_root: Optional[Path] = None) -> RAGRecursiveAgent:
    """Create a RAG recursive agent with standard configuration."""
    return RAGRecursiveAgent(project_root=project_root or PROJECT_ROOT)
