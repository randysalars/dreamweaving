"""
Type definitions for the Notion Content Agent.

Provides dataclasses and TypedDicts for type safety and clarity.
"""

from dataclasses import dataclass, field
from typing import TypedDict, Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class ProcessingStatus(Enum):
    """Status of article processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Article:
    """Represents an article to be processed."""
    id: str
    title: str
    status: str
    url: str
    content: str = ""
    is_virtual: bool = False
    instructions: Optional[str] = None
    source_type: str = "Page"  # Page, Block Item, AI Task

    @classmethod
    def from_notion_dict(cls, data: Dict[str, Any]) -> "Article":
        """Create Article from Notion API response dictionary."""
        properties = data.get("properties", {})

        # Extract title from nested structure
        title_prop = properties.get("Name") or properties.get("Title") or {}
        title = "Untitled"
        if title_prop.get("title"):
            title_parts = title_prop["title"]
            if title_parts:
                title = title_parts[0].get("plain_text", "Untitled")

        # Extract status
        status_prop = properties.get("Status", {})
        status = status_prop.get("select", {}).get("name", "Unknown")

        # Check if virtual (AI-generated task)
        is_virtual = str(data.get("id", "")).startswith("ai-task-")

        return cls(
            id=data.get("id", ""),
            title=title,
            status=status,
            url=data.get("url", ""),
            is_virtual=is_virtual,
            instructions=properties.get("Instructions", ""),
            source_type=properties.get("Type", "Page")
        )


@dataclass
class ProcessingResult:
    """Result of processing a single article."""
    article_id: str
    success: bool
    output_path: Optional[str] = None
    website_path: Optional[str] = None
    error: Optional[str] = None
    tokens_used: int = 0
    processing_time: float = 0.0

    def __str__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"ProcessingResult({self.article_id}: {status})"


@dataclass
class HubCard:
    """Represents a card in a hub page."""
    title: str
    description: str
    href: str
    emoji: str = "📄"


@dataclass
class WebsiteArtifact:
    """Represents generated website artifact."""
    article_path: str
    hub_path: Optional[str] = None
    snippet_path: Optional[str] = None


@dataclass
class MonetizationElements:
    """Generated monetization content."""
    inline_ad: str
    landing_page: str
    product_recommendation: str


class NotionArticleDict(TypedDict, total=False):
    """Type definition for Notion article response."""
    id: str
    properties: Dict[str, Any]
    url: str
    created_time: str
    last_edited_time: str


@dataclass
class ProcessingMetrics:
    """Tracks processing statistics."""
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

    def record_article(self, result: ProcessingResult) -> None:
        """Record result from processing an article."""
        if result.success:
            self.articles_processed += 1
        else:
            self.articles_failed += 1
            if result.error:
                self.errors.append(result.error)

        self.total_tokens_used += result.tokens_used
        self.total_processing_time += result.processing_time

    def record_success(self, tokens: int = 0, processing_time: float = 0.0) -> None:
        """Record a successfully processed article."""
        self.articles_processed += 1
        self.total_tokens_used += tokens
        self.total_processing_time += processing_time

    def record_failure(self, error: str = "", tokens: int = 0) -> None:
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

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        self.cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        self.cache_misses += 1

    @property
    def duration_seconds(self) -> float:
        """Get total duration in seconds."""
        return (datetime.now() - self.start_time).total_seconds()

    @property
    def total_processed(self) -> int:
        """Get total articles processed (alias for compatibility)."""
        return self.articles_processed + self.articles_failed

    @property
    def total_successful(self) -> int:
        """Get successful articles (alias)."""
        return self.articles_processed

    @property
    def total_failed(self) -> int:
        """Get failed articles (alias)."""
        return self.articles_failed

    @property
    def success_rate(self) -> float:
        """Get success rate as a percentage."""
        total = self.articles_processed + self.articles_failed
        if total == 0:
            return 0.0
        return self.articles_processed / total

    @property
    def articles_per_hour(self) -> float:
        """Get processing rate in articles per hour."""
        hours = self.duration_seconds / 3600
        if hours < 0.001:  # Avoid division by zero
            return 0.0
        return self.articles_processed / hours

    @property
    def cache_hit_rate(self) -> float:
        """Get cache hit rate as a percentage."""
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "duration_seconds": self.duration_seconds,
            "articles_processed": self.articles_processed,
            "articles_failed": self.articles_failed,
            "articles_skipped": self.articles_skipped,
            "success_rate": f"{self.success_rate:.1%}",
            "total_tokens": self.total_tokens_used,
            "avg_processing_time": f"{self.avg_processing_time:.2f}s",
            "articles_per_hour": f"{self.articles_per_hour:.1f}",
            "api_calls": self.api_calls,
            "cache_hit_rate": f"{self.cache_hit_rate:.1%}",
            "recent_errors": self.errors[-10:],  # Last 10 errors
        }

    def print_summary(self) -> None:
        """Print formatted metrics summary."""
        print("\n" + "=" * 50)
        print("Processing Summary")
        print("=" * 50)
        print(f"Duration: {self.duration_seconds:.1f}s")
        print(f"Articles: {self.articles_processed} processed, {self.articles_failed} failed, {self.articles_skipped} skipped")
        print(f"Success Rate: {self.success_rate:.1%}")
        print(f"Tokens Used: {self.total_tokens_used:,}")
        print(f"Avg Processing Time: {self.avg_processing_time:.2f}s")
        print(f"Throughput: {self.articles_per_hour:.1f} articles/hour")
        print(f"API Calls: {self.api_calls}")
        print(f"Cache Hit Rate: {self.cache_hit_rate:.1%}")
        if self.errors:
            print(f"Recent Errors: {len(self.errors)}")
            for err in self.errors[-3:]:
                print(f"  - {err[:80]}...")
        print("=" * 50)

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
