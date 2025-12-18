"""
Website Recursive Agent - Self-improving website content optimization.

This agent enhances website performance by:
1. Tracking page metrics through Google Analytics
2. Identifying top performers and underperformers
3. Extracting success patterns from high-performing content
4. Generating improvement suggestions for underperformers
5. Optimizing SEO across the site
6. Learning from applied improvements

Part of the Recursive Improver system for self-improving Dreamweaving content.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .analytics_client import AnalyticsClient, PageMetrics
from .content_tracker import ContentTracker, PagePerformance
from .content_improver import ContentImprover, ImprovementSuggestion
from .seo_optimizer import SEOOptimizer, SEOAnalysis

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


@dataclass
class WebsiteContext:
    """Container for website optimization context."""

    # Performance snapshot
    total_pages: int = 0
    avg_engagement_score: float = 0.0

    # Status breakdown
    improving_count: int = 0
    declining_count: int = 0
    needs_attention_count: int = 0

    # Dreamweaving-specific
    dreamweaving_count: int = 0
    dreamweaving_avg_engagement: float = 0.0

    # SEO summary
    avg_seo_score: float = 0.0
    uncovered_keywords: int = 0

    # Pending actions
    pending_improvements: int = 0
    high_priority_actions: List[str] = field(default_factory=list)

    # Timestamps
    last_updated: Optional[str] = None

    def to_summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            "# Website Performance Summary",
            "",
            f"**Last Updated:** {self.last_updated or 'Never'}",
            "",
            "## Overview",
            f"- Total tracked pages: {self.total_pages}",
            f"- Average engagement score: {self.avg_engagement_score:.1f}",
            f"- Average SEO score: {self.avg_seo_score:.1f}",
            "",
            "## Status Breakdown",
            f"- Improving: {self.improving_count}",
            f"- Declining: {self.declining_count}",
            f"- Needs attention: {self.needs_attention_count}",
            "",
            "## Dreamweaving Content",
            f"- Dreamweaving pages: {self.dreamweaving_count}",
            f"- Average engagement: {self.dreamweaving_avg_engagement:.1f}",
            "",
            "## Pending Actions",
            f"- Improvement suggestions: {self.pending_improvements}",
            f"- Uncovered keywords: {self.uncovered_keywords}",
        ]

        if self.high_priority_actions:
            lines.append("")
            lines.append("## High Priority")
            for action in self.high_priority_actions[:5]:
                lines.append(f"- {action}")

        return "\n".join(lines)


class WebsiteRecursiveAgent:
    """
    Self-improving website agent for content optimization.

    Capabilities:
    1. Performance monitoring via Google Analytics
    2. Success pattern extraction from top performers
    3. Improvement suggestion generation
    4. SEO optimization recommendations
    5. Outcome tracking and learning
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
    ):
        """
        Initialize website recursive agent.

        Args:
            project_root: Path to project root
        """
        self.project_root = project_root or PROJECT_ROOT

        # Lazy-loaded components
        self._analytics_client = None
        self._content_tracker = None
        self._content_improver = None
        self._seo_optimizer = None

    def _get_analytics_client(self) -> AnalyticsClient:
        """Get or create analytics client."""
        if self._analytics_client is None:
            self._analytics_client = AnalyticsClient(project_root=self.project_root)
        return self._analytics_client

    def _get_content_tracker(self) -> ContentTracker:
        """Get or create content tracker."""
        if self._content_tracker is None:
            self._content_tracker = ContentTracker(
                project_root=self.project_root,
                analytics_client=self._get_analytics_client(),
            )
        return self._content_tracker

    def _get_content_improver(self) -> ContentImprover:
        """Get or create content improver."""
        if self._content_improver is None:
            self._content_improver = ContentImprover(
                project_root=self.project_root,
                content_tracker=self._get_content_tracker(),
            )
        return self._content_improver

    def _get_seo_optimizer(self) -> SEOOptimizer:
        """Get or create SEO optimizer."""
        if self._seo_optimizer is None:
            self._seo_optimizer = SEOOptimizer(project_root=self.project_root)
        return self._seo_optimizer

    def get_context(self) -> WebsiteContext:
        """
        Get current website context.

        Returns:
            WebsiteContext with performance snapshot and pending actions
        """
        context = WebsiteContext()

        # Get content tracker data
        tracker = self._get_content_tracker()
        all_pages = tracker.track_all_pages()

        if all_pages:
            context.total_pages = len(all_pages)
            context.avg_engagement_score = sum(
                p.current_engagement_score for p in all_pages
            ) / len(all_pages)

            # Status breakdown
            context.improving_count = len([
                p for p in all_pages if p.status == "improving"
            ])
            context.declining_count = len([
                p for p in all_pages if p.status == "declining"
            ])
            context.needs_attention_count = len([
                p for p in all_pages if p.status == "needs_attention"
            ])

            # Dreamweaving specific
            dreamweavings = [p for p in all_pages if p.content_type == "dreamweaving"]
            if dreamweavings:
                context.dreamweaving_count = len(dreamweavings)
                context.dreamweaving_avg_engagement = sum(
                    p.current_engagement_score for p in dreamweavings
                ) / len(dreamweavings)

        # Get SEO data
        seo = self._get_seo_optimizer()
        opportunities = seo.identify_opportunities()
        context.uncovered_keywords = len([
            o for o in opportunities if not o.currently_ranking
        ])

        if seo._analyses:
            context.avg_seo_score = sum(
                a.seo_score for a in seo._analyses.values()
            ) / len(seo._analyses)

        # Get improvement suggestions
        improver = self._get_content_improver()
        pending = improver.get_pending_suggestions()
        context.pending_improvements = len(pending)

        # Identify high priority actions
        high_priority = []

        # Declining pages need immediate attention
        for page in all_pages:
            if page.status == "declining":
                high_priority.append(
                    f"Page declining: {page.page_path} "
                    f"({page.engagement_trend:+.1f} pts)"
                )

        # High priority improvement suggestions
        for suggestion in pending:
            if suggestion.priority == "high":
                high_priority.append(
                    f"Improve: {suggestion.page_path} - {suggestion.suggestion_type}"
                )

        context.high_priority_actions = high_priority[:10]
        context.last_updated = datetime.now().isoformat()

        return context

    def run_improvement_cycle(self) -> Dict[str, Any]:
        """
        Run a complete improvement cycle.

        Steps:
        1. Update performance tracking for all pages
        2. Extract success patterns from top performers
        3. Generate suggestions for underperformers
        4. Identify SEO opportunities
        5. Return prioritized action list

        Returns:
            Dict with cycle results and recommendations
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'pages_tracked': 0,
            'patterns_extracted': 0,
            'suggestions_generated': 0,
            'seo_opportunities': 0,
            'priority_actions': [],
        }

        # Step 1: Update performance tracking
        tracker = self._get_content_tracker()
        all_pages = tracker.track_all_pages()
        results['pages_tracked'] = len(all_pages)

        # Step 2: Extract success patterns
        improver = self._get_content_improver()
        patterns = improver.extract_patterns()
        results['patterns_extracted'] = len(patterns)

        # Step 3: Generate suggestions for underperformers
        suggestions = improver.suggest_improvements_for_underperformers(limit=10)
        total_suggestions = sum(len(s) for s in suggestions.values())
        results['suggestions_generated'] = total_suggestions

        # Step 4: Identify SEO opportunities
        seo = self._get_seo_optimizer()
        opportunities = seo.identify_opportunities()
        results['seo_opportunities'] = len([
            o for o in opportunities if not o.currently_ranking
        ])

        # Step 5: Build prioritized action list
        priority_actions = []

        # Declining pages
        declining = tracker.get_declining_pages(limit=5)
        for page in declining:
            priority_actions.append({
                'type': 'declining_page',
                'page_path': page.page_path,
                'engagement_trend': page.engagement_trend,
                'priority': 'high',
                'action': 'Investigate and improve content',
            })

        # High-priority suggestions
        for page_path, page_suggestions in suggestions.items():
            for s in page_suggestions:
                if s.priority == 'high':
                    priority_actions.append({
                        'type': 'improvement',
                        'page_path': s.page_path,
                        'suggestion': s.suggested_value,
                        'priority': s.priority,
                        'estimated_impact': s.estimated_engagement_delta,
                    })

        # Keyword opportunities
        for opp in opportunities[:5]:
            if not opp.currently_ranking:
                priority_actions.append({
                    'type': 'keyword_opportunity',
                    'keyword': opp.keyword,
                    'relevance': opp.relevance_score,
                    'action': opp.action,
                    'priority': 'medium',
                })

        results['priority_actions'] = priority_actions[:15]

        return results

    def get_page_optimization_plan(
        self,
        page_path: str,
    ) -> Dict[str, Any]:
        """
        Get a complete optimization plan for a specific page.

        Args:
            page_path: Page to optimize

        Returns:
            Dict with comprehensive optimization plan
        """
        plan = {
            'page_path': page_path,
            'timestamp': datetime.now().isoformat(),
        }

        # Get current performance
        tracker = self._get_content_tracker()
        performance = tracker.track_page(page_path)

        if performance:
            plan['performance'] = {
                'engagement_score': performance.current_engagement_score,
                'views': performance.current_views,
                'status': performance.status,
                'trend': performance.engagement_trend,
            }

        # Get improvement suggestions
        improver = self._get_content_improver()
        suggestions = improver.suggest_improvements(page_path)

        plan['suggestions'] = [
            {
                'type': s.suggestion_type,
                'priority': s.priority,
                'current': s.current_value,
                'suggested': s.suggested_value,
                'rationale': s.rationale,
                'estimated_impact': s.estimated_engagement_delta,
            }
            for s in suggestions
        ]

        # Get SEO plan (if page is analyzed)
        seo = self._get_seo_optimizer()
        seo_plan = seo.get_optimization_plan(page_path)

        if 'error' not in seo_plan:
            plan['seo'] = seo_plan

        return plan

    def record_improvement_outcome(
        self,
        page_path: str,
        suggestion_id: str,
        success: bool,
        engagement_delta: float,
    ) -> None:
        """
        Record the outcome of an applied improvement.

        Args:
            page_path: Page that was improved
            suggestion_id: ID of applied suggestion
            success: Whether improvement was successful
            engagement_delta: Actual engagement change
        """
        improver = self._get_content_improver()
        improver.record_outcome(page_path, suggestion_id, engagement_delta)

    def get_dreamweaving_insights(self) -> Dict[str, Any]:
        """
        Get insights specific to dreamweaving content.

        Returns:
            Dict with dreamweaving-specific analytics and recommendations
        """
        tracker = self._get_content_tracker()
        dw_performance = tracker.get_dreamweaving_performance()

        insights = {
            'overview': dw_performance,
            'recommendations': [],
        }

        # Generate dreamweaving-specific recommendations
        if dw_performance.get('declining_count', 0) > 0:
            insights['recommendations'].append(
                "Review declining dreamweaving sessions for content freshness"
            )

        if dw_performance.get('avg_engagement_score', 0) < 50:
            insights['recommendations'].append(
                "Consider adding more engaging elements (video previews, testimonials)"
            )

        # Top performers insights
        top = dw_performance.get('top_3', [])
        if top:
            insights['top_performers'] = [
                {
                    'path': p.page_path,
                    'engagement': p.current_engagement_score,
                    'views': p.current_views,
                }
                for p in top
            ]

        return insights

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        tracker_stats = self._get_content_tracker().get_statistics()
        improver_stats = self._get_content_improver().get_statistics()
        seo_stats = self._get_seo_optimizer().get_statistics()

        return {
            'content_tracker': tracker_stats,
            'content_improver': improver_stats,
            'seo_optimizer': seo_stats,
            'analytics_available': self._get_analytics_client().is_available(),
        }


# Factory function
def create_website_recursive_agent(
    project_root: Optional[Path] = None,
) -> WebsiteRecursiveAgent:
    """Create a website recursive agent with standard configuration."""
    return WebsiteRecursiveAgent(project_root=project_root or PROJECT_ROOT)
