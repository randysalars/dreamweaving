"""
Website Recursive Agent Package.

This package contains components for the self-improving website agent:

- AnalyticsClient: Google Analytics 4 integration
- ContentTracker: Track page performance metrics
- ContentImprover: Auto-generate content improvements
- SEOOptimizer: Auto-optimize SEO based on rankings
- WebsiteRecursiveAgent: Main orchestrator
"""

from .analytics_client import AnalyticsClient, PageMetrics
from .content_tracker import ContentTracker, PagePerformance
from .content_improver import ContentImprover, ImprovementSuggestion
from .seo_optimizer import SEOOptimizer, SEOAnalysis
from .website_recursive import (
    WebsiteRecursiveAgent,
    WebsiteContext,
    create_website_recursive_agent,
)

__all__ = [
    # Analytics
    'AnalyticsClient',
    'PageMetrics',
    # Content tracking
    'ContentTracker',
    'PagePerformance',
    # Content improvement
    'ContentImprover',
    'ImprovementSuggestion',
    # SEO
    'SEOOptimizer',
    'SEOAnalysis',
    # Main agent
    'WebsiteRecursiveAgent',
    'WebsiteContext',
    'create_website_recursive_agent',
]
