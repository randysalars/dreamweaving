"""
Dreamweaving Automation System

Automated pipeline for:
1. Nightly video generation from Notion RAG topics
2. Daily YouTube uploads with quality-based selection
3. Daily YouTube Shorts from website-only content
4. Automatic archiving of uploaded sessions

Usage:
    # Generate sessions
    python -m scripts.automation.nightly_builder --count 5

    # Upload to YouTube
    python -m scripts.automation.upload_scheduler

    # Generate and upload shorts
    python -m scripts.automation.shorts_generator

    # Archive uploaded sessions
    python -m scripts.automation.archive_manager
"""

from .state_db import StateDatabase
from .config_loader import load_config

__all__ = [
    'StateDatabase',
    'load_config',
]
