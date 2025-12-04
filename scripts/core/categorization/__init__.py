"""
Dreamweaving Content Categorization Module

Provides intelligent auto-categorization for dreamweaving sessions
based on multiple content signals.
"""

from .analyzer import ContentAnalyzer, CategoryMatch, categorize_session, get_available_categories
from .keywords import CATEGORY_KEYWORDS, ARCHETYPE_CATEGORIES, FREQUENCY_CATEGORIES

__all__ = [
    'ContentAnalyzer',
    'CategoryMatch',
    'categorize_session',
    'get_available_categories',
    'CATEGORY_KEYWORDS',
    'ARCHETYPE_CATEGORIES',
    'FREQUENCY_CATEGORIES',
]
