"""
Content Performance Tracker for Website Recursive Agent.

Tracks page performance over time and identifies trends:
- Improving pages (engagement going up)
- Declining pages (engagement going down)
- Stable high performers
- Pages needing attention
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml
import json

from .analytics_client import AnalyticsClient, PageMetrics

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


@dataclass
class PagePerformance:
    """Performance tracking for a single page."""

    page_path: str
    page_title: str

    # Current metrics
    current_views: int = 0
    current_engagement_score: float = 0.0
    current_bounce_rate: float = 0.0
    current_avg_time: float = 0.0

    # Historical metrics (previous period)
    previous_views: int = 0
    previous_engagement_score: float = 0.0

    # Trends (positive = improving)
    views_trend: float = 0.0  # Percentage change
    engagement_trend: float = 0.0  # Points change

    # Classification
    status: str = "unknown"  # improving | declining | stable | needs_attention

    # Timestamps
    last_updated: Optional[str] = None
    first_tracked: Optional[str] = None

    # Content metadata
    content_type: str = "page"  # page | dreamweaving | article | landing
    has_video: bool = False
    has_audio: bool = False

    def compute_trends(self) -> None:
        """Compute trend indicators from current vs previous metrics."""
        # Views trend (percentage change)
        if self.previous_views > 0:
            self.views_trend = (
                (self.current_views - self.previous_views) / self.previous_views
            ) * 100
        else:
            self.views_trend = 100.0 if self.current_views > 0 else 0.0

        # Engagement trend (points change)
        self.engagement_trend = (
            self.current_engagement_score - self.previous_engagement_score
        )

        # Classify status
        self._classify_status()

    def _classify_status(self) -> None:
        """Classify page status based on metrics and trends."""
        # High performer thresholds
        HIGH_ENGAGEMENT = 70.0
        IMPROVING_THRESHOLD = 5.0  # +5 points engagement
        DECLINING_THRESHOLD = -5.0  # -5 points engagement
        MIN_VIEWS_FOR_ANALYSIS = 20

        # Not enough data
        if self.current_views < MIN_VIEWS_FOR_ANALYSIS:
            self.status = "insufficient_data"
            return

        # Check if improving
        if self.engagement_trend >= IMPROVING_THRESHOLD:
            self.status = "improving"
            return

        # Check if declining
        if self.engagement_trend <= DECLINING_THRESHOLD:
            self.status = "declining"
            return

        # High performer
        if self.current_engagement_score >= HIGH_ENGAGEMENT:
            self.status = "stable_high"
            return

        # Low performer with traffic (needs attention)
        if self.current_engagement_score < 40.0 and self.current_views >= 50:
            self.status = "needs_attention"
            return

        # Otherwise stable
        self.status = "stable"


class ContentTracker:
    """
    Track content performance across the website.

    Features:
    - Historical performance tracking
    - Trend detection (improving vs declining)
    - Page classification
    - Content type categorization
    - Performance snapshots for comparison
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        analytics_client: Optional[AnalyticsClient] = None,
    ):
        """
        Initialize content tracker.

        Args:
            project_root: Path to project root
            analytics_client: Analytics client (created if not provided)
        """
        self.project_root = project_root or PROJECT_ROOT
        self.analytics_client = analytics_client or AnalyticsClient(
            project_root=self.project_root
        )

        # Performance data storage
        self.data_dir = self.project_root / "knowledge" / "website_performance"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.history_file = self.data_dir / "performance_history.yaml"
        self.snapshots_dir = self.data_dir / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

        # Load existing history
        self._history: Dict[str, Dict] = {}
        self._load_history()

    def _load_history(self) -> None:
        """Load performance history from disk."""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    self._history = yaml.safe_load(f) or {}
            except Exception:
                self._history = {}

    def _save_history(self) -> None:
        """Save performance history to disk."""
        with open(self.history_file, 'w') as f:
            yaml.dump(self._history, f, default_flow_style=False)

    def track_page(
        self,
        page_path: str,
        content_type: str = "page",
        has_video: bool = False,
        has_audio: bool = False,
    ) -> Optional[PagePerformance]:
        """
        Track a page's performance.

        Args:
            page_path: Page path to track
            content_type: Type of content
            has_video: Whether page has video
            has_audio: Whether page has audio

        Returns:
            PagePerformance with current and trend data
        """
        # Get current metrics
        current_metrics = self.analytics_client.get_page_metrics(page_path, days=30)
        if not current_metrics:
            return None

        # Get previous period metrics
        previous_metrics = self._get_previous_period_metrics(page_path)

        # Build performance record
        performance = PagePerformance(
            page_path=page_path,
            page_title=current_metrics.page_title,
            current_views=current_metrics.views,
            current_engagement_score=current_metrics.engagement_score,
            current_bounce_rate=current_metrics.bounce_rate,
            current_avg_time=current_metrics.avg_engagement_time_seconds,
            previous_views=previous_metrics.get('views', 0),
            previous_engagement_score=previous_metrics.get('engagement_score', 0),
            content_type=content_type,
            has_video=has_video,
            has_audio=has_audio,
            last_updated=datetime.now().isoformat(),
            first_tracked=self._history.get(page_path, {}).get(
                'first_tracked', datetime.now().isoformat()
            ),
        )

        # Compute trends
        performance.compute_trends()

        # Update history
        self._update_history(page_path, performance)

        return performance

    def _get_previous_period_metrics(self, page_path: str) -> Dict[str, Any]:
        """Get metrics from the previous snapshot."""
        if page_path not in self._history:
            return {}

        history = self._history[page_path]
        snapshots = history.get('snapshots', [])

        if not snapshots:
            return {}

        # Get the most recent snapshot (which becomes "previous")
        return snapshots[-1]

    def _update_history(self, page_path: str, performance: PagePerformance) -> None:
        """Update history with new performance data."""
        now = datetime.now().isoformat()

        if page_path not in self._history:
            self._history[page_path] = {
                'page_path': page_path,
                'page_title': performance.page_title,
                'content_type': performance.content_type,
                'first_tracked': now,
                'snapshots': [],
            }

        # Add current as a new snapshot
        self._history[page_path]['snapshots'].append({
            'timestamp': now,
            'views': performance.current_views,
            'engagement_score': performance.current_engagement_score,
            'bounce_rate': performance.current_bounce_rate,
            'avg_time': performance.current_avg_time,
        })

        # Keep only last 12 snapshots (monthly for a year)
        if len(self._history[page_path]['snapshots']) > 12:
            self._history[page_path]['snapshots'] = (
                self._history[page_path]['snapshots'][-12:]
            )

        # Update current status
        self._history[page_path]['current_status'] = performance.status
        self._history[page_path]['last_updated'] = now

        self._save_history()

    def track_all_pages(
        self,
        days: int = 30,
        min_views: int = 10,
    ) -> List[PagePerformance]:
        """
        Track all pages with sufficient traffic.

        Args:
            days: Days to look back for metrics
            min_views: Minimum views to track

        Returns:
            List of PagePerformance records
        """
        all_metrics = self.analytics_client.get_all_pages_metrics(
            days=days,
            min_views=min_views,
        )

        results = []
        for metrics in all_metrics:
            # Detect content type from path
            content_type = self._detect_content_type(metrics.page_path)

            performance = self.track_page(
                page_path=metrics.page_path,
                content_type=content_type,
            )

            if performance:
                results.append(performance)

        return results

    def _detect_content_type(self, page_path: str) -> str:
        """Detect content type from page path."""
        if '/dreamweavings/' in page_path or page_path.startswith('/dreamweavings'):
            return 'dreamweaving'
        if '/articles/' in page_path:
            return 'article'
        if '/blog/' in page_path:
            return 'blog'
        if page_path in ['/', '/about', '/contact']:
            return 'landing'
        return 'page'

    def get_improving_pages(self, limit: int = 10) -> List[PagePerformance]:
        """Get pages with improving performance."""
        all_tracked = self.track_all_pages()
        improving = [p for p in all_tracked if p.status == "improving"]
        improving.sort(key=lambda p: p.engagement_trend, reverse=True)
        return improving[:limit]

    def get_declining_pages(self, limit: int = 10) -> List[PagePerformance]:
        """Get pages with declining performance."""
        all_tracked = self.track_all_pages()
        declining = [p for p in all_tracked if p.status == "declining"]
        declining.sort(key=lambda p: p.engagement_trend)  # Most declining first
        return declining[:limit]

    def get_pages_needing_attention(self, limit: int = 10) -> List[PagePerformance]:
        """Get pages that need attention (high traffic, low engagement)."""
        all_tracked = self.track_all_pages()
        needs_attention = [
            p for p in all_tracked
            if p.status in ["needs_attention", "declining"]
        ]
        # Sort by views (highest traffic underperformers first)
        needs_attention.sort(key=lambda p: p.current_views, reverse=True)
        return needs_attention[:limit]

    def get_top_performers(self, limit: int = 10) -> List[PagePerformance]:
        """Get best performing pages."""
        all_tracked = self.track_all_pages()
        top = [
            p for p in all_tracked
            if p.status in ["stable_high", "improving"]
        ]
        top.sort(key=lambda p: p.current_engagement_score, reverse=True)
        return top[:limit]

    def get_dreamweaving_performance(self) -> Dict[str, Any]:
        """Get aggregate performance for dreamweaving pages."""
        all_tracked = self.track_all_pages()
        dreamweavings = [
            p for p in all_tracked
            if p.content_type == "dreamweaving"
        ]

        if not dreamweavings:
            return {'count': 0}

        total_views = sum(p.current_views for p in dreamweavings)
        avg_engagement = sum(
            p.current_engagement_score for p in dreamweavings
        ) / len(dreamweavings)

        improving = len([p for p in dreamweavings if p.status == "improving"])
        declining = len([p for p in dreamweavings if p.status == "declining"])

        return {
            'count': len(dreamweavings),
            'total_views': total_views,
            'avg_engagement_score': round(avg_engagement, 2),
            'improving_count': improving,
            'declining_count': declining,
            'top_3': sorted(
                dreamweavings,
                key=lambda p: p.current_engagement_score,
                reverse=True,
            )[:3],
        }

    def create_snapshot(self, label: Optional[str] = None) -> str:
        """
        Create a full snapshot of current performance.

        Args:
            label: Optional label for the snapshot

        Returns:
            Snapshot filename
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"snapshot_{timestamp}.yaml"

        if label:
            filename = f"snapshot_{timestamp}_{label}.yaml"

        snapshot_file = self.snapshots_dir / filename

        # Get all current performance data
        all_tracked = self.track_all_pages()

        snapshot_data = {
            'timestamp': datetime.now().isoformat(),
            'label': label,
            'summary': {
                'total_pages': len(all_tracked),
                'total_views': sum(p.current_views for p in all_tracked),
                'avg_engagement': (
                    sum(p.current_engagement_score for p in all_tracked)
                    / len(all_tracked) if all_tracked else 0
                ),
                'status_breakdown': {
                    'improving': len([p for p in all_tracked if p.status == "improving"]),
                    'declining': len([p for p in all_tracked if p.status == "declining"]),
                    'stable_high': len([p for p in all_tracked if p.status == "stable_high"]),
                    'needs_attention': len([p for p in all_tracked if p.status == "needs_attention"]),
                },
            },
            'pages': [
                {
                    'page_path': p.page_path,
                    'page_title': p.page_title,
                    'content_type': p.content_type,
                    'views': p.current_views,
                    'engagement_score': p.current_engagement_score,
                    'status': p.status,
                }
                for p in all_tracked
            ],
        }

        with open(snapshot_file, 'w') as f:
            yaml.dump(snapshot_data, f, default_flow_style=False)

        return filename

    def get_statistics(self) -> Dict[str, Any]:
        """Get tracker statistics."""
        return {
            'tracked_pages': len(self._history),
            'history_file': str(self.history_file),
            'snapshots_count': len(list(self.snapshots_dir.glob('*.yaml'))),
            'content_types': list(set(
                h.get('content_type', 'unknown')
                for h in self._history.values()
            )),
        }
