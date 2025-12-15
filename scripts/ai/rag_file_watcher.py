#!/usr/bin/env python3
"""
RAG File Watcher - Automatically re-indexes when knowledge files change.

Watches the knowledge/ directory and triggers re-indexing when:
- New .md or .yaml files are added
- Existing files are modified
- Files are deleted (triggers full re-index)

Uses debouncing to batch rapid changes together.

Usage:
    python3 scripts/ai/rag_file_watcher.py              # Start watcher
    python3 scripts/ai/rag_file_watcher.py --daemon     # Run as daemon
    python3 scripts/ai/rag_file_watcher.py --test       # Test mode (no re-index)

Part of Phase 8: Automatic RAG Indexing System
"""
import os
import sys
import time
import logging
import signal
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Set, Optional
from threading import Timer

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog not installed. Run: pip install watchdog")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGFileWatcher(FileSystemEventHandler):
    """
    Watches knowledge directory and triggers RAG re-indexing.

    Features:
    - Debouncing: Waits for changes to settle before re-indexing
    - Filtering: Only watches .md, .yaml, .json files
    - Batching: Combines rapid changes into single re-index
    - Retry limits: Stops after consecutive failures to prevent infinite loops
    - Backoff: Exponential backoff between retries
    """

    DEBOUNCE_SECONDS = 5.0  # Wait 5 seconds after last change
    WATCHED_EXTENSIONS = {'.md', '.yaml', '.yml', '.json'}
    MAX_CONSECUTIVE_FAILURES = 3  # Stop after 3 consecutive failures
    MIN_RETRY_DELAY_SECONDS = 60  # Wait at least 1 min before retry after failure
    MAX_RETRY_DELAY_SECONDS = 3600  # Max 1 hour backoff

    def __init__(self, test_mode: bool = False):
        super().__init__()
        self.test_mode = test_mode
        self.pending_changes: Set[str] = set()
        self.debounce_timer: Optional[Timer] = None
        self.last_index_time: Optional[datetime] = None
        self.consecutive_failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.current_backoff_seconds = self.MIN_RETRY_DELAY_SECONDS
        self._syncer = None

    @property
    def syncer(self):
        """Lazy load RAGAutoSync."""
        if self._syncer is None:
            from scripts.ai.rag_auto_sync import RAGAutoSync
            self._syncer = RAGAutoSync()
        return self._syncer

    def _should_process(self, path: str) -> bool:
        """Check if file should trigger re-indexing."""
        p = Path(path)

        # Skip hidden files and directories
        if any(part.startswith('.') for part in p.parts):
            return False

        # Skip __pycache__ and similar
        if '__pycache__' in path or '.pyc' in path:
            return False

        # CRITICAL: Skip vector DB directory to prevent feedback loops
        # The watcher modifying the DB triggers more events = infinite loop
        if 'vector_db' in path or 'embeddings_cache' in path:
            return False

        # Skip other generated/temporary directories
        if any(exclude in path for exclude in ['__pycache__', '.pytest_cache', 'node_modules']):
            return False

        # Only watch specific extensions
        if p.suffix.lower() not in self.WATCHED_EXTENSIONS:
            return False

        return True

    def _schedule_reindex(self):
        """Schedule a re-index after debounce period."""
        # Cancel existing timer
        if self.debounce_timer:
            self.debounce_timer.cancel()

        # Schedule new timer
        self.debounce_timer = Timer(
            self.DEBOUNCE_SECONDS,
            self._execute_reindex
        )
        self.debounce_timer.start()

        logger.debug(f"Re-index scheduled in {self.DEBOUNCE_SECONDS}s")

    def _execute_reindex(self):
        """Execute the re-indexing operation with retry limits and backoff."""
        if not self.pending_changes:
            return

        # Check if we're in backoff period after failures
        if self.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            logger.error(
                f"Skipping re-index: {self.MAX_CONSECUTIVE_FAILURES} consecutive failures. "
                f"Manual intervention required. Restart watcher after fixing issues."
            )
            return

        # Check if we need to wait before retrying after a recent failure
        if self.last_failure_time:
            time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
            if time_since_failure < self.current_backoff_seconds:
                wait_time = self.current_backoff_seconds - time_since_failure
                logger.warning(
                    f"Backing off: waiting {wait_time:.0f}s before retry "
                    f"(attempt {self.consecutive_failures + 1}/{self.MAX_CONSECUTIVE_FAILURES})"
                )
                # Re-schedule after backoff period
                self.debounce_timer = Timer(wait_time, self._execute_reindex)
                self.debounce_timer.start()
                return

        changes = list(self.pending_changes)
        self.pending_changes.clear()

        logger.info(f"Processing {len(changes)} file change(s)...")
        for change in changes[:5]:  # Log first 5 changes
            logger.info(f"  - {change}")
        if len(changes) > 5:
            logger.info(f"  ... and {len(changes) - 5} more")

        if self.test_mode:
            logger.info("[TEST MODE] Would re-index now")
            return

        try:
            # Force re-index since we know content changed
            result = self.syncer.sync(force=True)

            if result.get("status") == "completed":
                logger.info(
                    f"Re-index complete: {result.get('vectors', 0)} vectors "
                    f"in {result.get('duration_seconds', 0):.1f}s"
                )
                self.last_index_time = datetime.now()
                # Reset failure tracking on success
                self.consecutive_failures = 0
                self.last_failure_time = None
                self.current_backoff_seconds = self.MIN_RETRY_DELAY_SECONDS
            elif result.get("status") == "skipped":
                # No changes detected - this is fine, not a failure
                logger.info(f"Re-index skipped: {result.get('reason', 'no changes')}")
                self.consecutive_failures = 0
                self.last_failure_time = None
            else:
                # Failed or unexpected status
                error_msg = result.get("error", "Unknown error")
                self._handle_reindex_failure(error_msg, changes)

        except Exception as e:
            self._handle_reindex_failure(str(e), changes)

    def _handle_reindex_failure(self, error: str, changes: list):
        """Handle re-indexing failure with backoff logic."""
        self.consecutive_failures += 1
        self.last_failure_time = datetime.now()
        
        # Exponential backoff: double the delay each time, up to max
        self.current_backoff_seconds = min(
            self.current_backoff_seconds * 2,
            self.MAX_RETRY_DELAY_SECONDS
        )

        # Detect specific error types and provide helpful messages
        if "already accessed by another instance" in error.lower():
            logger.error(
                f"Re-index failed: Vector DB is locked by another process. "
                f"Stop other Qdrant clients or use Qdrant server for concurrent access."
            )
        elif "rate limit" in error.lower():
            logger.error(
                f"Re-index failed: Notion API rate limit hit. "
                f"Will retry with backoff after {self.current_backoff_seconds:.0f}s."
            )
        else:
            logger.error(f"Re-index failed: {error}")

        logger.warning(
            f"Failure {self.consecutive_failures}/{self.MAX_CONSECUTIVE_FAILURES}. "
            f"Next retry in {self.current_backoff_seconds:.0f}s."
        )

        # Re-add changes to pending so they can be retried
        self.pending_changes.update(changes)

        if self.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            logger.error(
                "MAX FAILURES REACHED. Watcher will no longer process changes. "
                "Fix the underlying issue and restart the watcher."
            )

    def on_created(self, event: FileSystemEvent):
        """Handle file creation."""
        if event.is_directory:
            return
        if self._should_process(event.src_path):
            logger.debug(f"File created: {event.src_path}")
            self.pending_changes.add(f"created: {Path(event.src_path).name}")
            self._schedule_reindex()

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification."""
        if event.is_directory:
            return
        if self._should_process(event.src_path):
            logger.debug(f"File modified: {event.src_path}")
            self.pending_changes.add(f"modified: {Path(event.src_path).name}")
            self._schedule_reindex()

    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion."""
        if event.is_directory:
            return
        if self._should_process(event.src_path):
            logger.debug(f"File deleted: {event.src_path}")
            self.pending_changes.add(f"deleted: {Path(event.src_path).name}")
            self._schedule_reindex()

    def on_moved(self, event: FileSystemEvent):
        """Handle file move/rename."""
        if event.is_directory:
            return
        if self._should_process(event.src_path) or self._should_process(event.dest_path):
            logger.debug(f"File moved: {event.src_path} -> {event.dest_path}")
            self.pending_changes.add(f"moved: {Path(event.src_path).name}")
            self._schedule_reindex()


def run_watcher(watch_paths: list, test_mode: bool = False, daemon: bool = False):
    """
    Start the file watcher.

    Args:
        watch_paths: List of directories to watch
        test_mode: If True, don't actually re-index
        daemon: If True, run in background mode
    """
    if not WATCHDOG_AVAILABLE:
        logger.error("watchdog package not installed. Run: pip install watchdog")
        sys.exit(1)

    handler = RAGFileWatcher(test_mode=test_mode)
    observer = Observer()

    for path in watch_paths:
        if Path(path).exists():
            observer.schedule(handler, path, recursive=True)
            logger.info(f"Watching: {path}")
        else:
            logger.warning(f"Path not found, skipping: {path}")

    # Handle graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Shutting down watcher...")
        observer.stop()
        if handler.debounce_timer:
            handler.debounce_timer.cancel()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    observer.start()

    logger.info("=" * 60)
    logger.info("RAG FILE WATCHER STARTED")
    logger.info(f"Test mode: {test_mode}")
    logger.info(f"Debounce: {handler.DEBOUNCE_SECONDS}s")
    logger.info(f"Extensions: {', '.join(handler.WATCHED_EXTENSIONS)}")
    logger.info("=" * 60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


def main():
    parser = argparse.ArgumentParser(
        description="Watch knowledge files and auto-reindex RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/ai/rag_file_watcher.py              # Start watcher
  python3 scripts/ai/rag_file_watcher.py --test       # Test mode (no re-index)
  python3 scripts/ai/rag_file_watcher.py --daemon     # Run as daemon

The watcher monitors:
  - knowledge/notion_export/    (Notion content)
  - knowledge/                  (Local knowledge files)
  - prompts/                    (Prompt templates)
        """
    )
    parser.add_argument("--test", action="store_true",
                        help="Test mode - log changes but don't re-index")
    parser.add_argument("--daemon", action="store_true",
                        help="Run as background daemon")
    parser.add_argument("--paths", nargs="+",
                        default=["knowledge", "prompts"],
                        help="Paths to watch (default: knowledge prompts)")

    args = parser.parse_args()

    # Convert relative paths to absolute
    watch_paths = [str(PROJECT_ROOT / p) for p in args.paths]

    if args.daemon:
        # Fork to background
        try:
            pid = os.fork()
            if pid > 0:
                print(f"Watcher started in background (PID: {pid})")
                sys.exit(0)
        except OSError as e:
            logger.error(f"Fork failed: {e}")
            sys.exit(1)

        # Detach from terminal
        os.setsid()
        os.umask(0)

        # Redirect stdout/stderr to log
        log_file = PROJECT_ROOT / "logs" / "rag_watcher.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        sys.stdout = open(log_file, 'a')
        sys.stderr = sys.stdout

    run_watcher(watch_paths, test_mode=args.test, daemon=args.daemon)


if __name__ == "__main__":
    main()
