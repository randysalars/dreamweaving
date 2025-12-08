"""
AI Integration Module for Dreamweaving

This module provides AI-powered generation capabilities:
- Script generation (SSML)
- Manifest generation
- Midjourney prompt generation
- VTT subtitle generation
- Quality scoring
- Self-learning system
- Notion knowledge base RAG integration

Usage:
    # Generate VTT subtitles
    python3 -m scripts.ai.vtt_generator sessions/{session}

    # Generate Midjourney prompts
    python3 -m scripts.ai.prompt_generator sessions/{session}

    # Score session quality
    python3 -m scripts.ai.quality_scorer sessions/{session}

    # Analyze feedback
    python3 -m scripts.ai.learning.feedback_analyzer --analytics data.json

    # Review code quality
    python3 -m scripts.ai.learning.code_reviewer --path scripts/

    # Manage lessons learned
    python3 -m scripts.ai.learning.lessons_manager show

    # Query Notion knowledge base
    python3 -m scripts.ai.notion_knowledge_retriever --search "Navigator"
    python3 -m scripts.ai.knowledge_tools --query "shadow healing journey"

    # Index Notion content for semantic search
    python3 -m scripts.ai.notion_knowledge_retriever --export knowledge/notion_export/
    python3 -m scripts.ai.notion_embeddings_pipeline --index
"""

__version__ = "1.0.0"
__author__ = "Dreamweaving AI OS"

# Submodules
from . import learning

# Convenience imports for common functions
from .vtt_generator import (
    parse_ssml_to_segments,
    generate_vtt,
    get_audio_duration,
)

from .prompt_generator import (
    generate_thumbnail_prompt,
    generate_scene_prompts,
    STYLE_PRESETS,
)

from .quality_scorer import (
    score_ssml,
    score_manifest,
    score_audio,
    generate_full_report,
)

__all__ = [
    # VTT Generation
    'parse_ssml_to_segments',
    'generate_vtt',
    'get_audio_duration',
    # Prompt Generation
    'generate_thumbnail_prompt',
    'generate_scene_prompts',
    'STYLE_PRESETS',
    # Quality Scoring
    'score_ssml',
    'score_manifest',
    'score_audio',
    'generate_full_report',
]
