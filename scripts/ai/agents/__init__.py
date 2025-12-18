"""
AI Agents for Dreamweaving Recursive Improvement System.

This package contains specialized recursive improvement agents:

- DreamweaverRecursiveAgent: Self-improving session generation
- RAGRecursiveAgent: Self-improving knowledge retrieval
- (Future) WebsiteRecursiveAgent: Self-improving content marketing
"""

from .dreamweaver_recursive import (
    DreamweaverRecursiveAgent,
    AppliedLessons,
    GenerationContext,
    get_lessons_for_generation,
    record_generation_outcome,
)

from .rag_recursive import (
    RAGRecursiveAgent,
    RAGContext,
    create_rag_recursive_agent,
)

__all__ = [
    # Dreamweaver agent
    'DreamweaverRecursiveAgent',
    'AppliedLessons',
    'GenerationContext',
    'get_lessons_for_generation',
    'record_generation_outcome',
    # RAG agent
    'RAGRecursiveAgent',
    'RAGContext',
    'create_rag_recursive_agent',
]
