"""
TTL (Time-To-Live) cache for API responses.

Provides async-safe caching with automatic expiration to reduce
API calls and improve performance.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TypeVar, Generic, Optional, Callable, Dict, Any, Awaitable, Union

from constants import Defaults

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class CacheEntry(Generic[T]):
    """A single cache entry with expiration."""
    value: T
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        return datetime.now() > self.expires_at

    @property
    def age_seconds(self) -> float:
        """Get the age of this entry in seconds."""
        return (datetime.now() - self.created_at).total_seconds()


class TTLCache(Generic[T]):
    """
    Thread-safe TTL cache for API responses.

    Features:
    - Async-safe with locking
    - Automatic expiration
    - Manual invalidation
    - Statistics tracking

    Usage:
        cache = TTLCache(ttl_seconds=300)

        # Async usage
        result = await cache.get_or_fetch_async(
            key="my-key",
            fetch_fn=lambda: expensive_api_call()
        )

        # Sync usage
        result = cache.get_or_fetch(
            key="my-key",
            fetch_fn=lambda: sync_api_call()
        )
    """

    def __init__(self, ttl_seconds: int = Defaults.CACHE_TTL_SECONDS):
        self._cache: Dict[str, CacheEntry[T]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

    async def get_or_fetch_async(
        self,
        key: str,
        fetch_fn: Union[Callable[[], T], Callable[[], Awaitable[T]]]
    ) -> T:
        """
        Get value from cache or fetch and cache it (async version).

        Args:
            key: Cache key
            fetch_fn: Function to call if cache miss (sync or async)

        Returns:
            Cached or freshly fetched value
        """
        async with self._lock:
            # Check cache
            entry = self._cache.get(key)
            if entry and not entry.is_expired:
                self._hits += 1
                logger.debug(f"Cache hit for key: {key}")
                return entry.value

            self._misses += 1
            logger.debug(f"Cache miss for key: {key}")

        # Fetch new value (outside lock to allow concurrent fetches)
        if asyncio.iscoroutinefunction(fetch_fn):
            value = await fetch_fn()
        else:
            # Run sync function in thread pool
            value = await asyncio.get_event_loop().run_in_executor(None, fetch_fn)

        # Cache the result
        async with self._lock:
            self._cache[key] = CacheEntry(
                value=value,
                expires_at=datetime.now() + self._ttl
            )

        return value

    def get_or_fetch(
        self,
        key: str,
        fetch_fn: Callable[[], T]
    ) -> T:
        """
        Get value from cache or fetch and cache it (sync version).

        Args:
            key: Cache key
            fetch_fn: Function to call if cache miss

        Returns:
            Cached or freshly fetched value
        """
        # Check cache
        entry = self._cache.get(key)
        if entry and not entry.is_expired:
            self._hits += 1
            logger.debug(f"Cache hit for key: {key}")
            return entry.value

        self._misses += 1
        logger.debug(f"Cache miss for key: {key}")

        # Fetch new value
        value = fetch_fn()

        # Cache the result
        self._cache[key] = CacheEntry(
            value=value,
            expires_at=datetime.now() + self._ttl
        )

        return value

    def get(self, key: str) -> Optional[T]:
        """
        Get value from cache without fetching.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        entry = self._cache.get(key)
        if entry and not entry.is_expired:
            return entry.value
        return None

    def set(self, key: str, value: T, ttl_seconds: Optional[int] = None) -> None:
        """
        Manually set a cache entry.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional custom TTL (uses default if not specified)
        """
        ttl = timedelta(seconds=ttl_seconds) if ttl_seconds else self._ttl
        self._cache[key] = CacheEntry(
            value=value,
            expires_at=datetime.now() + ttl
        )

    def invalidate(self, key: str) -> bool:
        """
        Remove a specific entry from cache.

        Args:
            key: Cache key

        Returns:
            True if entry was removed, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Invalidated cache key: {key}")
            return True
        return False

    def invalidate_prefix(self, prefix: str) -> int:
        """
        Remove all entries with keys starting with prefix.

        Args:
            prefix: Key prefix to match

        Returns:
            Number of entries removed
        """
        keys_to_remove = [k for k in self._cache.keys() if k.startswith(prefix)]
        for key in keys_to_remove:
            del self._cache[key]

        if keys_to_remove:
            logger.debug(f"Invalidated {len(keys_to_remove)} cache entries with prefix: {prefix}")

        return len(keys_to_remove)

    def clear(self) -> int:
        """
        Clear all cached entries.

        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        logger.debug(f"Cleared {count} cache entries")
        return count

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of expired entries removed
        """
        expired_keys = [k for k, v in self._cache.items() if v.is_expired]
        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    @property
    def size(self) -> int:
        """Get number of entries in cache."""
        return len(self._cache)

    @property
    def hits(self) -> int:
        """Get number of cache hits."""
        return self._hits

    @property
    def misses(self) -> int:
        """Get number of cache misses."""
        return self._misses

    @property
    def hit_rate(self) -> float:
        """Get cache hit rate (0.0 to 1.0)."""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": self.size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self.hit_rate:.1%}",
            "ttl_seconds": self._ttl.total_seconds(),
        }

    def reset_stats(self) -> None:
        """Reset hit/miss counters."""
        self._hits = 0
        self._misses = 0
