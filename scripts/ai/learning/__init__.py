"""
Learning Module for Dreamweaving

Self-improving system that learns from:
- YouTube analytics (views, retention, engagement)
- Viewer comments (sentiment, suggestions)
- Code quality reviews (patterns, improvements)
- Session performance (quality metrics)

Stores insights in knowledge/ directory:
- knowledge/lessons_learned.yaml - Accumulated lessons
- knowledge/best_practices.md - Evolving best practices
- knowledge/code_improvements/ - Code quality tracking

Usage:
    # Analyze YouTube analytics
    python3 -m scripts.ai.learning.feedback_analyzer --analytics analytics.json

    # Analyze viewer comments
    python3 -m scripts.ai.learning.feedback_analyzer --comments comments.txt

    # Review code quality
    python3 -m scripts.ai.learning.code_reviewer

    # Show accumulated lessons
    python3 -m scripts.ai.learning.lessons_manager show

    # Get recommendations for new session
    python3 -m scripts.ai.learning.lessons_manager recommend --theme spiritual
"""

__version__ = "1.0.0"

from .feedback_analyzer import (
    analyze_youtube_analytics,
    analyze_comments,
    analyze_session_performance,
    FeedbackAnalysis,
)

from .code_reviewer import (
    CodeReviewer,
    CodeIssue,
)

from .lessons_manager import (
    LessonsManager,
)
