"""
Metrics tracking for the Notion Content Agent.

Tracks processing statistics, token usage, and performance data.
"""

import json
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Generator

from rich.console import Console
from rich.table import Table
from rich.panel import Panel


@dataclass
class MetricsTracker:
    """
    Tracks and reports processing metrics.

    Usage:
        metrics = MetricsTracker()

        with metrics.track_article("article-123"):
            # Process article
            metrics.record_tokens(150)

        metrics.print_summary()
    """

    start_time: datetime = field(default_factory=datetime.now)
    articles_processed: int = 0
    articles_failed: int = 0
    articles_skipped: int = 0
    total_tokens_used: int = 0
    total_processing_time: float = 0.0
    api_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: List[str] = field(default_factory=list)
    _current_article_start: Optional[float] = field(default=None, repr=False)

    def record_success(self, tokens: int = 0, processing_time: float = 0.0) -> None:
        """Record a successfully processed article."""
        self.articles_processed += 1
        self.total_tokens_used += tokens
        self.total_processing_time += processing_time

    def record_failure(self, error: str, tokens: int = 0) -> None:
        """Record a failed article."""
        self.articles_failed += 1
        self.total_tokens_used += tokens
        if error:
            self.errors.append(error[:200])  # Truncate long errors

    def record_skip(self) -> None:
        """Record a skipped article."""
        self.articles_skipped += 1

    def record_api_call(self, tokens: int = 0) -> None:
        """Record an API call."""
        self.api_calls += 1
        self.total_tokens_used += tokens

    def record_tokens(self, tokens: int) -> None:
        """Record token usage."""
        self.total_tokens_used += tokens

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        self.cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        self.cache_misses += 1

    @contextmanager
    def track_article(self, article_id: str) -> Generator[None, None, None]:
        """
        Context manager to track article processing time.

        Usage:
            with metrics.track_article("article-123"):
                process_article()
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.total_processing_time += elapsed

    @contextmanager
    def track_api_call(self) -> Generator[None, None, None]:
        """
        Context manager to track API calls.

        Usage:
            with metrics.track_api_call():
                response = api.call()
        """
        self.api_calls += 1
        yield

    @property
    def duration_seconds(self) -> float:
        """Get total duration in seconds."""
        return (datetime.now() - self.start_time).total_seconds()

    @property
    def success_rate(self) -> float:
        """Get success rate as a decimal (0.0 to 1.0)."""
        total = self.articles_processed + self.articles_failed
        if total == 0:
            return 0.0
        return self.articles_processed / total

    @property
    def articles_per_hour(self) -> float:
        """Get processing rate in articles per hour."""
        hours = self.duration_seconds / 3600
        if hours < 0.001:
            return 0.0
        return self.articles_processed / hours

    @property
    def cache_hit_rate(self) -> float:
        """Get cache hit rate as a decimal (0.0 to 1.0)."""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total

    @property
    def avg_processing_time(self) -> float:
        """Get average processing time per article."""
        if self.articles_processed == 0:
            return 0.0
        return self.total_processing_time / self.articles_processed

    @property
    def total_articles(self) -> int:
        """Get total articles attempted."""
        return self.articles_processed + self.articles_failed + self.articles_skipped

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(self.duration_seconds, 2),
            "articles": {
                "processed": self.articles_processed,
                "failed": self.articles_failed,
                "skipped": self.articles_skipped,
                "total": self.total_articles,
            },
            "performance": {
                "success_rate": round(self.success_rate * 100, 1),
                "avg_processing_time_seconds": round(self.avg_processing_time, 2),
                "articles_per_hour": round(self.articles_per_hour, 1),
            },
            "tokens": {
                "total_used": self.total_tokens_used,
                "api_calls": self.api_calls,
            },
            "cache": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_rate": round(self.cache_hit_rate * 100, 1),
            },
            "errors": self.errors[-10:],
        }

    def to_json(self) -> str:
        """Convert metrics to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def save_to_file(self, path: Path) -> None:
        """Save metrics to a JSON file."""
        with open(path, "w") as f:
            f.write(self.to_json())

    def print_summary(self, console: Optional[Console] = None) -> None:
        """Print formatted metrics summary to console."""
        if console is None:
            console = Console()

        # Create main metrics table
        table = Table(title="Processing Summary", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="dim")
        table.add_column("Value", justify="right")

        table.add_row("Duration", f"{self.duration_seconds:.1f}s")
        table.add_row("Articles Processed", str(self.articles_processed))
        table.add_row("Articles Failed", str(self.articles_failed))
        table.add_row("Articles Skipped", str(self.articles_skipped))
        table.add_row("Success Rate", f"{self.success_rate:.1%}")
        table.add_row("Avg Processing Time", f"{self.avg_processing_time:.2f}s")
        table.add_row("Throughput", f"{self.articles_per_hour:.1f}/hour")
        table.add_row("Total Tokens", f"{self.total_tokens_used:,}")
        table.add_row("API Calls", str(self.api_calls))
        table.add_row("Cache Hit Rate", f"{self.cache_hit_rate:.1%}")

        console.print(table)

        # Print errors if any
        if self.errors:
            error_panel = Panel(
                "\n".join(f"• {err[:100]}..." if len(err) > 100 else f"• {err}"
                          for err in self.errors[-5:]),
                title=f"Recent Errors ({len(self.errors)} total)",
                border_style="red"
            )
            console.print(error_panel)

    def reset(self) -> None:
        """Reset all metrics."""
        self.start_time = datetime.now()
        self.articles_processed = 0
        self.articles_failed = 0
        self.articles_skipped = 0
        self.total_tokens_used = 0
        self.total_processing_time = 0.0
        self.api_calls = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.errors.clear()
