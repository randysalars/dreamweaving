"""
Async orchestrator for concurrent article processing.

Manages the processing pipeline with support for concurrent
article processing, graceful shutdown, and metrics tracking.
"""

import asyncio
import logging
import time
from typing import List, Optional, Callable, Any

from models import Article, ProcessingResult, ProcessingMetrics
from constants import Defaults, LogMessages

logger = logging.getLogger(__name__)


class AsyncOrchestrator:
    """
    Orchestrates async article processing with concurrency control.

    Features:
    - Concurrent processing with configurable limits
    - Graceful shutdown support
    - Metrics tracking
    - Error isolation (one failure doesn't stop others)

    Usage:
        orchestrator = AsyncOrchestrator(
            process_fn=process_article,
            max_concurrent=3
        )

        # Process a batch
        results = await orchestrator.process_batch(articles)

        # Run polling loop
        await orchestrator.run_polling_loop(
            fetch_fn=get_pending_articles,
            interval=60
        )
    """

    def __init__(
        self,
        process_fn: Callable[[dict], ProcessingResult],
        max_concurrent: int = Defaults.MAX_CONCURRENT,
        dry_run: bool = False
    ):
        """
        Initialize the orchestrator.

        Args:
            process_fn: Function to process a single article
            max_concurrent: Maximum concurrent processing tasks
            dry_run: If True, simulate processing without actual work
        """
        self.process_fn = process_fn
        self.max_concurrent = max_concurrent
        self.dry_run = dry_run

        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._shutdown = asyncio.Event()
        self.metrics = ProcessingMetrics()

    async def process_batch(
        self,
        articles: List[dict],
        on_complete: Optional[Callable[[ProcessingResult], None]] = None
    ) -> List[ProcessingResult]:
        """
        Process a batch of articles concurrently.

        Args:
            articles: List of article dictionaries from Notion
            on_complete: Optional callback for each completed article

        Returns:
            List of ProcessingResult objects
        """
        if not articles:
            return []

        logger.info(f"Processing batch of {len(articles)} articles (max concurrent: {self.max_concurrent})")

        # Create tasks for all articles
        tasks = [
            self._process_with_semaphore(article, on_complete)
            for article in articles
        ]

        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to failed results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Article processing failed with exception: {result}")
                failed_result = ProcessingResult(
                    article_id=articles[i].get("id", "unknown"),
                    success=False,
                    error=str(result)
                )
                self.metrics.record_failure(str(result))
                processed_results.append(failed_result)
            else:
                processed_results.append(result)

        return processed_results

    async def _process_with_semaphore(
        self,
        article: dict,
        on_complete: Optional[Callable[[ProcessingResult], None]] = None
    ) -> ProcessingResult:
        """Process a single article with semaphore for concurrency control."""
        async with self._semaphore:
            # Check for shutdown
            if self._shutdown.is_set():
                return ProcessingResult(
                    article_id=article.get("id", "unknown"),
                    success=False,
                    error="Shutdown requested"
                )

            start_time = time.perf_counter()

            try:
                # Process the article
                if asyncio.iscoroutinefunction(self.process_fn):
                    result = await self.process_fn(article)
                else:
                    # Run sync function in thread pool
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        self.process_fn,
                        article
                    )

                # Record metrics
                processing_time = time.perf_counter() - start_time
                result.processing_time = processing_time

                if result.success:
                    self.metrics.record_success(
                        tokens=result.tokens_used,
                        processing_time=processing_time
                    )
                else:
                    self.metrics.record_failure(
                        error=result.error or "Unknown error",
                        tokens=result.tokens_used
                    )

                # Callback
                if on_complete:
                    on_complete(result)

                return result

            except Exception as e:
                processing_time = time.perf_counter() - start_time
                logger.error(f"Error processing article: {e}", exc_info=True)

                result = ProcessingResult(
                    article_id=article.get("id", "unknown"),
                    success=False,
                    error=str(e),
                    processing_time=processing_time
                )
                self.metrics.record_failure(str(e))

                if on_complete:
                    on_complete(result)

                return result

    async def run_polling_loop(
        self,
        fetch_fn: Callable[[], List[dict]],
        interval: int = Defaults.POLL_INTERVAL_SECONDS,
        on_batch_complete: Optional[Callable[[List[ProcessingResult]], None]] = None
    ) -> None:
        """
        Run the main polling loop.

        Continuously polls for new articles and processes them
        until shutdown is requested.

        Args:
            fetch_fn: Function to fetch pending articles
            interval: Polling interval in seconds
            on_batch_complete: Optional callback after each batch
        """
        logger.info(f"Starting polling loop (interval: {interval}s, max concurrent: {self.max_concurrent})")

        while not self._shutdown.is_set():
            try:
                # Fetch pending articles
                if asyncio.iscoroutinefunction(fetch_fn):
                    articles = await fetch_fn()
                else:
                    articles = await asyncio.get_event_loop().run_in_executor(
                        None, fetch_fn
                    )

                if articles:
                    logger.info(LogMessages.FOUND_ARTICLES.format(count=len(articles)))
                    results = await self.process_batch(articles)

                    if on_batch_complete:
                        on_batch_complete(results)
                else:
                    logger.info(LogMessages.NO_PENDING.format(interval=interval))

                # Wait for next poll or shutdown
                try:
                    await asyncio.wait_for(
                        self._shutdown.wait(),
                        timeout=interval
                    )
                    # If we get here, shutdown was requested
                    break
                except asyncio.TimeoutError:
                    # Normal timeout, continue polling
                    pass

            except Exception as e:
                logger.error(f"Error in polling loop: {e}", exc_info=True)
                # Backoff on error
                await asyncio.sleep(30)

        logger.info("Polling loop stopped")
        self.metrics.print_summary()

    async def process_single(self, article: dict) -> ProcessingResult:
        """
        Process a single article.

        Args:
            article: Article dictionary from Notion

        Returns:
            ProcessingResult
        """
        results = await self.process_batch([article])
        return results[0] if results else ProcessingResult(
            article_id=article.get("id", "unknown"),
            success=False,
            error="No result returned"
        )

    def request_shutdown(self) -> None:
        """Request graceful shutdown of the orchestrator."""
        logger.info(LogMessages.SHUTDOWN_REQUESTED)
        self._shutdown.set()

    @property
    def is_shutting_down(self) -> bool:
        """Check if shutdown has been requested."""
        return self._shutdown.is_set()

    def reset(self) -> None:
        """Reset the orchestrator for reuse."""
        self._shutdown.clear()
        self.metrics.reset()


class BatchOrchestrator(AsyncOrchestrator):
    """
    Orchestrator variant for batch processing without polling.

    Use this for one-shot processing of a known set of articles.
    """

    def __init__(
        self,
        process_fn: Callable[[dict], ProcessingResult],
        max_concurrent: int = Defaults.MAX_CONCURRENT,
        article_limit: Optional[int] = None
    ):
        """
        Initialize the batch orchestrator.

        Args:
            process_fn: Function to process a single article
            max_concurrent: Maximum concurrent processing tasks
            article_limit: Optional limit on articles to process
        """
        super().__init__(process_fn, max_concurrent)
        self.article_limit = article_limit

    async def run(
        self,
        articles: List[dict],
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> List[ProcessingResult]:
        """
        Run batch processing on a list of articles.

        Args:
            articles: List of articles to process
            on_progress: Optional progress callback (current, total)

        Returns:
            List of ProcessingResult objects
        """
        # Apply limit if set
        if self.article_limit:
            articles = articles[:self.article_limit]

        total = len(articles)
        processed = 0
        all_results = []

        def track_progress(result: ProcessingResult):
            nonlocal processed
            processed += 1
            if on_progress:
                on_progress(processed, total)

        results = await self.process_batch(articles, on_complete=track_progress)
        all_results.extend(results)

        return all_results
