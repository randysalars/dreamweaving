"""
Google Analytics 4 Client for Website Recursive Agent.

Fetches page performance metrics from GA4 to drive content optimization.
Uses the GA4 Data API (google-analytics-data).

Configuration:
- GA_MEASUREMENT_ID: G-F8GVPD8N2H
- GA_STREAM_ID: 13137691426
- Site: https://www.salars.net
"""

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


@dataclass
class PageMetrics:
    """Metrics for a single page."""

    page_path: str
    page_title: str

    # Traffic metrics
    views: int = 0
    unique_visitors: int = 0
    sessions: int = 0

    # Engagement metrics
    avg_engagement_time_seconds: float = 0.0
    bounce_rate: float = 0.0
    scroll_depth_avg: float = 0.0

    # Conversion metrics
    conversions: int = 0
    conversion_rate: float = 0.0

    # Time range
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None

    # Computed engagement score (0-100)
    engagement_score: float = 0.0

    def compute_engagement_score(self) -> float:
        """
        Compute engagement score based on multiple factors.

        Weighted formula:
        - Avg engagement time: 40% (normalized to 0-100)
        - Bounce rate: 30% (inverted - lower is better)
        - Scroll depth: 20% (direct percentage)
        - Conversion rate: 10% (normalized to 0-100)
        """
        # Normalize engagement time (assume 120s = 100%)
        time_score = min(100, (self.avg_engagement_time_seconds / 120) * 100)

        # Invert bounce rate (0% bounce = 100, 100% bounce = 0)
        bounce_score = 100 - (self.bounce_rate * 100)

        # Scroll depth is already 0-100
        scroll_score = self.scroll_depth_avg * 100

        # Normalize conversion rate (assume 5% = 100%)
        conversion_score = min(100, (self.conversion_rate / 0.05) * 100)

        # Weighted average
        self.engagement_score = (
            time_score * 0.40 +
            bounce_score * 0.30 +
            scroll_score * 0.20 +
            conversion_score * 0.10
        )

        return self.engagement_score


@dataclass
class AnalyticsConfig:
    """Configuration for Google Analytics."""

    property_id: str = ""  # GA4 property ID (numeric)
    measurement_id: str = ""  # G-XXXXXXX format
    credentials_path: Optional[str] = None

    @classmethod
    def from_env(cls) -> 'AnalyticsConfig':
        """Load configuration from environment variables."""
        return cls(
            property_id=os.environ.get('GA_PROPERTY_ID', ''),
            measurement_id=os.environ.get('GA_MEASUREMENT_ID', 'G-F8GVPD8N2H'),
            credentials_path=os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'),
        )


class AnalyticsClient:
    """
    Google Analytics 4 client for fetching page metrics.

    Uses the GA4 Data API to retrieve:
    - Page views and unique visitors
    - Engagement time and bounce rate
    - Scroll depth (if configured)
    - Conversion events
    """

    def __init__(
        self,
        config: Optional[AnalyticsConfig] = None,
        project_root: Optional[Path] = None,
    ):
        """
        Initialize Analytics client.

        Args:
            config: Analytics configuration (from env if not provided)
            project_root: Path to project root
        """
        self.config = config or AnalyticsConfig.from_env()
        self.project_root = project_root or PROJECT_ROOT

        # Cache directory for analytics data
        self.cache_dir = self.project_root / "knowledge" / "website_analytics"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Lazy-loaded client
        self._client = None
        self._client_available = None

    def _get_client(self):
        """Get or create GA4 Data API client."""
        if self._client is None:
            try:
                from google.analytics.data_v1beta import BetaAnalyticsDataClient

                # Use default credentials or explicit path
                if self.config.credentials_path:
                    self._client = BetaAnalyticsDataClient.from_service_account_file(
                        self.config.credentials_path
                    )
                else:
                    self._client = BetaAnalyticsDataClient()

                self._client_available = True
            except ImportError:
                self._client_available = False
            except Exception:
                self._client_available = False

        return self._client if self._client_available else None

    def is_available(self) -> bool:
        """Check if GA4 client is available and configured."""
        if self._client_available is None:
            self._get_client()
        return bool(self._client_available and self.config.property_id)

    def get_page_metrics(
        self,
        page_path: str,
        days: int = 30,
    ) -> Optional[PageMetrics]:
        """
        Fetch metrics for a specific page.

        Args:
            page_path: Page path (e.g., '/dreamweavings/session-name')
            days: Number of days to look back

        Returns:
            PageMetrics if available, None otherwise
        """
        client = self._get_client()
        if not client:
            return self._get_cached_metrics(page_path)

        try:
            from google.analytics.data_v1beta.types import (
                DateRange,
                Dimension,
                Metric,
                RunReportRequest,
                FilterExpression,
                Filter,
            )

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            request = RunReportRequest(
                property=f"properties/{self.config.property_id}",
                date_ranges=[
                    DateRange(
                        start_date=start_date.strftime('%Y-%m-%d'),
                        end_date=end_date.strftime('%Y-%m-%d'),
                    )
                ],
                dimensions=[
                    Dimension(name="pagePath"),
                    Dimension(name="pageTitle"),
                ],
                metrics=[
                    Metric(name="screenPageViews"),
                    Metric(name="totalUsers"),
                    Metric(name="sessions"),
                    Metric(name="averageSessionDuration"),
                    Metric(name="bounceRate"),
                ],
                dimension_filter=FilterExpression(
                    filter=Filter(
                        field_name="pagePath",
                        string_filter=Filter.StringFilter(
                            match_type=Filter.StringFilter.MatchType.EXACT,
                            value=page_path,
                        ),
                    ),
                ),
            )

            response = client.run_report(request)

            if not response.rows:
                return None

            row = response.rows[0]
            metrics = PageMetrics(
                page_path=page_path,
                page_title=row.dimension_values[1].value,
                views=int(row.metric_values[0].value),
                unique_visitors=int(row.metric_values[1].value),
                sessions=int(row.metric_values[2].value),
                avg_engagement_time_seconds=float(row.metric_values[3].value),
                bounce_rate=float(row.metric_values[4].value),
                date_range_start=start_date.strftime('%Y-%m-%d'),
                date_range_end=end_date.strftime('%Y-%m-%d'),
            )
            metrics.compute_engagement_score()

            # Cache the result
            self._cache_metrics(metrics)

            return metrics

        except Exception as e:
            # Fall back to cache
            return self._get_cached_metrics(page_path)

    def get_all_pages_metrics(
        self,
        days: int = 30,
        min_views: int = 10,
    ) -> List[PageMetrics]:
        """
        Fetch metrics for all pages.

        Args:
            days: Number of days to look back
            min_views: Minimum views to include page

        Returns:
            List of PageMetrics sorted by views (descending)
        """
        client = self._get_client()
        if not client:
            return self._get_all_cached_metrics()

        try:
            from google.analytics.data_v1beta.types import (
                DateRange,
                Dimension,
                Metric,
                RunReportRequest,
                OrderBy,
            )

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            request = RunReportRequest(
                property=f"properties/{self.config.property_id}",
                date_ranges=[
                    DateRange(
                        start_date=start_date.strftime('%Y-%m-%d'),
                        end_date=end_date.strftime('%Y-%m-%d'),
                    )
                ],
                dimensions=[
                    Dimension(name="pagePath"),
                    Dimension(name="pageTitle"),
                ],
                metrics=[
                    Metric(name="screenPageViews"),
                    Metric(name="totalUsers"),
                    Metric(name="sessions"),
                    Metric(name="averageSessionDuration"),
                    Metric(name="bounceRate"),
                ],
                order_bys=[
                    OrderBy(
                        metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"),
                        desc=True,
                    )
                ],
                limit=100,  # Top 100 pages
            )

            response = client.run_report(request)

            results = []
            for row in response.rows:
                views = int(row.metric_values[0].value)
                if views < min_views:
                    continue

                page_path = row.dimension_values[0].value
                metrics = PageMetrics(
                    page_path=page_path,
                    page_title=row.dimension_values[1].value,
                    views=views,
                    unique_visitors=int(row.metric_values[1].value),
                    sessions=int(row.metric_values[2].value),
                    avg_engagement_time_seconds=float(row.metric_values[3].value),
                    bounce_rate=float(row.metric_values[4].value),
                    date_range_start=start_date.strftime('%Y-%m-%d'),
                    date_range_end=end_date.strftime('%Y-%m-%d'),
                )
                metrics.compute_engagement_score()
                results.append(metrics)

                # Cache each result
                self._cache_metrics(metrics)

            return results

        except Exception:
            return self._get_all_cached_metrics()

    def get_top_performers(
        self,
        n: int = 10,
        days: int = 30,
        min_engagement_score: float = 60.0,
    ) -> List[PageMetrics]:
        """
        Get top performing pages by engagement score.

        Args:
            n: Number of top performers to return
            days: Number of days to look back
            min_engagement_score: Minimum engagement score

        Returns:
            List of PageMetrics sorted by engagement score
        """
        all_metrics = self.get_all_pages_metrics(days=days)

        # Filter by minimum engagement score
        filtered = [m for m in all_metrics if m.engagement_score >= min_engagement_score]

        # Sort by engagement score
        filtered.sort(key=lambda m: m.engagement_score, reverse=True)

        return filtered[:n]

    def get_underperformers(
        self,
        n: int = 10,
        days: int = 30,
        min_views: int = 50,
        max_engagement_score: float = 40.0,
    ) -> List[PageMetrics]:
        """
        Get underperforming pages (high traffic, low engagement).

        These are pages with improvement potential.

        Args:
            n: Number of underperformers to return
            days: Number of days to look back
            min_views: Minimum views (to ensure enough traffic for analysis)
            max_engagement_score: Maximum engagement score to be considered underperforming

        Returns:
            List of PageMetrics sorted by views (descending)
        """
        all_metrics = self.get_all_pages_metrics(days=days, min_views=min_views)

        # Filter by low engagement score
        filtered = [m for m in all_metrics if m.engagement_score <= max_engagement_score]

        # Sort by views (high traffic underperformers first)
        filtered.sort(key=lambda m: m.views, reverse=True)

        return filtered[:n]

    def _cache_metrics(self, metrics: PageMetrics) -> None:
        """Cache metrics to disk."""
        # Create safe filename from path
        safe_name = metrics.page_path.replace('/', '_').strip('_')
        if not safe_name:
            safe_name = 'home'

        cache_file = self.cache_dir / f"{safe_name}.json"

        data = {
            'page_path': metrics.page_path,
            'page_title': metrics.page_title,
            'views': metrics.views,
            'unique_visitors': metrics.unique_visitors,
            'sessions': metrics.sessions,
            'avg_engagement_time_seconds': metrics.avg_engagement_time_seconds,
            'bounce_rate': metrics.bounce_rate,
            'scroll_depth_avg': metrics.scroll_depth_avg,
            'conversions': metrics.conversions,
            'conversion_rate': metrics.conversion_rate,
            'engagement_score': metrics.engagement_score,
            'date_range_start': metrics.date_range_start,
            'date_range_end': metrics.date_range_end,
            'cached_at': datetime.now().isoformat(),
        }

        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _get_cached_metrics(self, page_path: str) -> Optional[PageMetrics]:
        """Get metrics from cache."""
        safe_name = page_path.replace('/', '_').strip('_')
        if not safe_name:
            safe_name = 'home'

        cache_file = self.cache_dir / f"{safe_name}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file) as f:
                data = json.load(f)

            return PageMetrics(
                page_path=data['page_path'],
                page_title=data.get('page_title', ''),
                views=data.get('views', 0),
                unique_visitors=data.get('unique_visitors', 0),
                sessions=data.get('sessions', 0),
                avg_engagement_time_seconds=data.get('avg_engagement_time_seconds', 0),
                bounce_rate=data.get('bounce_rate', 0),
                scroll_depth_avg=data.get('scroll_depth_avg', 0),
                conversions=data.get('conversions', 0),
                conversion_rate=data.get('conversion_rate', 0),
                engagement_score=data.get('engagement_score', 0),
                date_range_start=data.get('date_range_start'),
                date_range_end=data.get('date_range_end'),
            )
        except Exception:
            return None

    def _get_all_cached_metrics(self) -> List[PageMetrics]:
        """Get all cached metrics."""
        results = []

        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file) as f:
                    data = json.load(f)

                metrics = PageMetrics(
                    page_path=data['page_path'],
                    page_title=data.get('page_title', ''),
                    views=data.get('views', 0),
                    unique_visitors=data.get('unique_visitors', 0),
                    sessions=data.get('sessions', 0),
                    avg_engagement_time_seconds=data.get('avg_engagement_time_seconds', 0),
                    bounce_rate=data.get('bounce_rate', 0),
                    engagement_score=data.get('engagement_score', 0),
                )
                results.append(metrics)
            except Exception:
                continue

        # Sort by views
        results.sort(key=lambda m: m.views, reverse=True)
        return results
