"""
Retry decorator with exponential backoff for API calls.

Provides both sync and async retry functionality with configurable
retry behavior for different types of failures.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from functools import wraps
from typing import Callable, TypeVar, Tuple, Type, Any, Optional

from constants import Defaults

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = Defaults.MAX_RETRIES
    base_delay: float = Defaults.RETRY_BASE_DELAY
    max_delay: float = Defaults.RETRY_MAX_DELAY
    exponential_base: float = Defaults.RETRY_EXPONENTIAL_BASE
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number (1-indexed)."""
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        return min(delay, self.max_delay)


def with_retry(
    max_attempts: int = Defaults.MAX_RETRIES,
    base_delay: float = Defaults.RETRY_BASE_DELAY,
    max_delay: float = Defaults.RETRY_MAX_DELAY,
    exponential_base: float = Defaults.RETRY_EXPONENTIAL_BASE,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
) -> Callable:
    """
    Decorator for retry with exponential backoff.

    Works with both sync and async functions.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
        exponential_base: Base for exponential backoff calculation
        retryable_exceptions: Tuple of exception types to retry on
        on_retry: Optional callback called on each retry with (exception, attempt)

    Usage:
        @with_retry(max_attempts=3, retryable_exceptions=(APIError,))
        async def call_api():
            return await api.request()
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        retryable_exceptions=retryable_exceptions
    )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        if asyncio.iscoroutinefunction(func):
            return _async_wrapper(func, config, on_retry)
        else:
            return _sync_wrapper(func, config, on_retry)

    return decorator


def _async_wrapper(
    func: Callable[..., T],
    config: RetryConfig,
    on_retry: Optional[Callable[[Exception, int], None]]
) -> Callable[..., T]:
    """Wrapper for async functions."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        last_exception: Optional[Exception] = None

        for attempt in range(1, config.max_attempts + 1):
            try:
                return await func(*args, **kwargs)
            except config.retryable_exceptions as e:
                last_exception = e

                if attempt == config.max_attempts:
                    logger.error(
                        f"All {config.max_attempts} attempts failed for {func.__name__}: {e}"
                    )
                    raise

                delay = config.calculate_delay(attempt)
                logger.warning(
                    f"Attempt {attempt}/{config.max_attempts} failed for {func.__name__}: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )

                if on_retry:
                    on_retry(e, attempt)

                await asyncio.sleep(delay)

        # Should never reach here, but satisfy type checker
        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected retry state")

    return wrapper


def _sync_wrapper(
    func: Callable[..., T],
    config: RetryConfig,
    on_retry: Optional[Callable[[Exception, int], None]]
) -> Callable[..., T]:
    """Wrapper for sync functions."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        last_exception: Optional[Exception] = None

        for attempt in range(1, config.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except config.retryable_exceptions as e:
                last_exception = e

                if attempt == config.max_attempts:
                    logger.error(
                        f"All {config.max_attempts} attempts failed for {func.__name__}: {e}"
                    )
                    raise

                delay = config.calculate_delay(attempt)
                logger.warning(
                    f"Attempt {attempt}/{config.max_attempts} failed for {func.__name__}: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )

                if on_retry:
                    on_retry(e, attempt)

                time.sleep(delay)

        # Should never reach here, but satisfy type checker
        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected retry state")

    return wrapper


class RetryableError(Exception):
    """Base exception for errors that should be retried."""
    pass


class RateLimitError(RetryableError):
    """Raised when an API rate limit is hit."""
    pass


class TransientError(RetryableError):
    """Raised for transient failures that may succeed on retry."""
    pass
