#!/usr/bin/env python3
"""
RAG File Watcher - Automatically re-indexes when knowledge files change.

Watches the knowledge/ directory and triggers re-indexing when:
- New .md or .yaml files are added
- Existing files are modified
- Files are deleted (triggers full re-index)

Uses debouncing to batch rapid changes together.
Configuration loaded from config/notion_config.yaml (watcher section).

Usage:
    python3 scripts/ai/rag_file_watcher.py              # Start watcher
    python3 scripts/ai/rag_file_watcher.py --daemon     # Run as daemon
    python3 scripts/ai/rag_file_watcher.py --test       # Test mode (no re-index)
    python3 scripts/ai/rag_file_watcher.py --health-endpoint  # Enable health server

Part of Phase 8: Automatic RAG Indexing System
"""
import os
import sys
import time
import logging
import signal
import argparse
from pathlib import Path
from datetime import datetime
from typing import Set, Optional, Dict, Any
from threading import Timer

# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE OPTIMIZATION - Limit thread usage for background watcher
# This process should be lightweight and not compete with TTS generation
# These MUST be set BEFORE importing torch/numpy/any ML libraries
# ═══════════════════════════════════════════════════════════════════════════════
MAX_RAG_THREADS = 2  # Minimal threads for background indexing

os.environ["OMP_NUM_THREADS"] = str(MAX_RAG_THREADS)
os.environ["MKL_NUM_THREADS"] = str(MAX_RAG_THREADS)
os.environ["OPENBLAS_NUM_THREADS"] = str(MAX_RAG_THREADS)
os.environ["VECLIB_MAXIMUM_THREADS"] = str(MAX_RAG_THREADS)
os.environ["NUMEXPR_NUM_THREADS"] = str(MAX_RAG_THREADS)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Set up project path before importing project modules
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Use shared utilities
from scripts.ai.rag_utils import (
    setup_project_path,
    load_dotenv_safe,
    get_notion_config,
    normalize_path,
)

load_dotenv_safe()

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
    - Filtering: Only watches configured extensions
    - Batching: Combines rapid changes into single re-index
    - Retry limits: Stops after consecutive failures to prevent infinite loops
    - Backoff: Exponential backoff between retries
    - Health metrics: Optional integration with health server

    Configuration loaded from config/notion_config.yaml (watcher section).
    """

    # Default values (used if config section missing)
    DEFAULT_DEBOUNCE_SECONDS = 5.0
    DEFAULT_WATCHED_EXTENSIONS = {'.md', '.yaml', '.yml', '.json'}
    DEFAULT_MAX_FAILURES = 3
    DEFAULT_MIN_RETRY_DELAY = 60
    DEFAULT_MAX_RETRY_DELAY = 3600
    DEFAULT_IGNORE_PATHS = {'vector_db', 'embeddings_cache', '__pycache__', '.pytest_cache', 'node_modules', '.git', 'notion_export'}
    DEFAULT_IGNORE_FILES = {'.sync_state.json', 'file_manifest.json', 'index_metadata.json', '.lock'}

    def __init__(self, config: Optional[Dict[str, Any]] = None, test_mode: bool = False):
        """
        Initialize file watcher with config.

        Args:
            config: Full config dict from notion_config.yaml. If None, loads from file.
            test_mode: If True, log changes but don't trigger re-indexing.
        """
        super().__init__()
        self.test_mode = test_mode

        # Load config
        if config is None:
            config = get_notion_config()
        self.config = config

        # Extract watcher-specific config with defaults
        watcher_config = config.get("watcher", {})

        # Timing settings
        self.debounce_seconds = watcher_config.get("debounce_seconds", self.DEFAULT_DEBOUNCE_SECONDS)
        self.max_failures = watcher_config.get("max_consecutive_failures", self.DEFAULT_MAX_FAILURES)
        self.min_retry_delay = watcher_config.get("min_retry_delay_seconds", self.DEFAULT_MIN_RETRY_DELAY)
        self.max_retry_delay = watcher_config.get("max_retry_delay_seconds", self.DEFAULT_MAX_RETRY_DELAY)

        # File filtering
        extensions = watcher_config.get("watched_extensions", list(self.DEFAULT_WATCHED_EXTENSIONS))
        self.watched_extensions = set(extensions)

        # Build ignore patterns from config + vector_db path
        self._build_ignore_patterns(config, watcher_config)

        # Quiet mode for syncer (suppress embedding progress)
        self.quiet_mode = watcher_config.get("quiet_mode", True)

        # State tracking
        self.pending_changes: Set[str] = set()
        self.debounce_timer: Optional[Timer] = None
        self.last_index_time: Optional[datetime] = None
        self.consecutive_failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.current_backoff_seconds = self.min_retry_delay

        # Lazy-loaded syncer
        self._syncer = None

        # Health metrics (optional, set via set_health_metrics)
        self._health_metrics = None

    def _build_ignore_patterns(self, config: Dict[str, Any], watcher_config: Dict[str, Any]):
        """Build comprehensive ignore patterns from config."""
        # Start with default ignore paths
        self.ignore_patterns = set(self.DEFAULT_IGNORE_PATHS)

        # Add config-specified ignore paths
        config_ignores = watcher_config.get("ignore_paths", [])
        for pattern in config_ignores:
            self.ignore_patterns.add(normalize_path(pattern))

        # Add vector_db path from config (critical for preventing feedback loops)
        vector_db_config = config.get("vector_db", {})
        vector_db_path = vector_db_config.get("path", "./knowledge/vector_db")
        self.ignore_patterns.add(normalize_path(vector_db_path))

        # Ignore files (state files that change during indexing)
        self.ignore_files = set(self.DEFAULT_IGNORE_FILES)
        config_ignore_files = watcher_config.get("ignore_files", [])
        self.ignore_files.update(config_ignore_files)

        logger.debug(f"Ignore patterns: {self.ignore_patterns}")
        logger.debug(f"Ignore files: {self.ignore_files}")

    @property
    def syncer(self):
        """Lazy load RAGAutoSync with quiet mode from config."""
        if self._syncer is None:
            from scripts.ai.rag_auto_sync import RAGAutoSync
            self._syncer = RAGAutoSync(quiet=self.quiet_mode)
        return self._syncer

    def set_health_metrics(self, metrics):
        """
        Attach health metrics for reporting.

        Args:
            metrics: HealthMetrics instance from rag_health_server.
        """
        self._health_metrics = metrics

    def _should_process(self, path: str) -> bool:
        """Check if file should trigger re-indexing."""
        p = Path(path)

        # Skip hidden files and directories
        if any(part.startswith('.') for part in p.parts):
            return False

        # Skip specific state files (by name)
        if p.name in self.ignore_files:
            return False

        # Skip directories matching ignore patterns
        for pattern in self.ignore_patterns:
            if pattern in path:
                return False

        # Only watch specific extensions
        if p.suffix.lower() not in self.watched_extensions:
            return False

        return True

    def _schedule_reindex(self):
        """Schedule a re-index after debounce period."""
        # Cancel existing timer
        if self.debounce_timer:
            self.debounce_timer.cancel()

        # Schedule new timer
        self.debounce_timer = Timer(
            self.debounce_seconds,
            self._execute_reindex
        )
        self.debounce_timer.start()

        # Update health metrics
        if self._health_metrics:
            self._health_metrics.set_pending_changes(len(self.pending_changes))

        logger.debug(f"Re-index scheduled in {self.debounce_seconds}s")

    def _execute_reindex(self):
        """Execute the re-indexing operation with retry limits and backoff."""
        if not self.pending_changes:
            return

        # Check if we've hit max failures
        if self.consecutive_failures >= self.max_failures:
            logger.error(
                f"Skipping re-index: {self.max_failures} consecutive failures. "
                f"Manual intervention required. Restart watcher after fixing issues."
            )
            return

        # Check if we need to wait (backoff period)
        if self.last_failure_time:
            time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
            if time_since_failure < self.current_backoff_seconds:
                wait_time = self.current_backoff_seconds - time_since_failure
                logger.warning(
                    f"Backing off: waiting {wait_time:.0f}s before retry "
                    f"(attempt {self.consecutive_failures + 1}/{self.max_failures})"
                )
                # Re-schedule after backoff period
                self.debounce_timer = Timer(wait_time, self._execute_reindex)
                self.debounce_timer.start()
                return

        changes = list(self.pending_changes)
        self.pending_changes.clear()

        logger.info(f"Processing {len(changes)} file change(s)...")
        for change in changes[:5]:
            logger.info(f"  - {change}")
        if len(changes) > 5:
            logger.info(f"  ... and {len(changes) - 5} more")

        if self.test_mode:
            logger.info("[TEST MODE] Would re-index now")
            return

        try:
            # Update health metrics
            if self._health_metrics:
                self._health_metrics.record_sync_start()

            # Force re-index since we know content changed
            result = self.syncer.sync(force=True)

            if result.get("status") == "completed":
                vectors = result.get('vectors', 0)
                duration = result.get('duration_seconds', 0)
                logger.info(f"Re-index complete: {vectors} vectors in {duration:.1f}s")

                self.last_index_time = datetime.now()
                self.consecutive_failures = 0
                self.last_failure_time = None
                self.current_backoff_seconds = self.min_retry_delay

                # Update health metrics
                if self._health_metrics:
                    self._health_metrics.record_sync_success(vectors_count=vectors, duration_seconds=duration)

            elif result.get("status") == "skipped":
                logger.info(f"Re-index skipped: {result.get('reason', 'no changes')}")
                self.consecutive_failures = 0
                self.last_failure_time = None

                if self._health_metrics:
                    self._health_metrics.record_sync_skipped(result.get('reason', 'no changes'))

            else:
                error_msg = result.get("error", "Unknown error")
                self._handle_reindex_failure(error_msg, changes)

        except Exception as e:
            self._handle_reindex_failure(str(e), changes)

    def _handle_reindex_failure(self, error: str, changes: list):
        """Handle re-indexing failure with backoff logic."""
        self.consecutive_failures += 1
        self.last_failure_time = datetime.now()

        # Exponential backoff
        self.current_backoff_seconds = min(
            self.current_backoff_seconds * 2,
            self.max_retry_delay
        )

        # Detect specific error types
        if "already accessed by another instance" in error.lower():
            logger.error(
                "Re-index failed: Vector DB is locked by another process. "
                "Stop other Qdrant clients or use Qdrant server for concurrent access."
            )
        elif "rate limit" in error.lower():
            logger.error(
                f"Re-index failed: Notion API rate limit hit. "
                f"Will retry with backoff after {self.current_backoff_seconds:.0f}s."
            )
        else:
            logger.error(f"Re-index failed: {error}")

        logger.warning(
            f"Failure {self.consecutive_failures}/{self.max_failures}. "
            f"Next retry in {self.current_backoff_seconds:.0f}s."
        )

        # Re-add changes to pending for retry
        self.pending_changes.update(changes)

        # Update health metrics
        if self._health_metrics:
            self._health_metrics.record_sync_failure(error)

        if self.consecutive_failures >= self.max_failures:
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


def run_watcher(
    watch_paths: list,
    config: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
    enable_health_endpoint: bool = False
):
    """
    Start the file watcher.

    Args:
        watch_paths: List of directories to watch
        config: Config dict (loaded from file if None)
        test_mode: If True, don't actually re-index
        enable_health_endpoint: If True, start health server
    """
    if not WATCHDOG_AVAILABLE:
        logger.error("watchdog package not installed. Run: pip install watchdog")
        sys.exit(1)

    # Load config
    if config is None:
        config = get_notion_config()

    handler = RAGFileWatcher(config=config, test_mode=test_mode)
    observer = Observer()

    # Schedule watching for each path
    for path in watch_paths:
        if Path(path).exists():
            observer.schedule(handler, path, recursive=True)
            logger.info(f"Watching: {path}")
        else:
            logger.warning(f"Path not found, skipping: {path}")

    # Start health server if enabled
    health_thread = None
    if enable_health_endpoint:
        watcher_config = config.get("watcher", {})
        health_config = watcher_config.get("health_endpoint", {})

        if health_config.get("enabled", False) or enable_health_endpoint:
            try:
                from scripts.ai.rag_health_server import HealthMetrics, start_health_server

                metrics = HealthMetrics(max_failures=handler.max_failures)
                handler.set_health_metrics(metrics)

                host = health_config.get("host", "127.0.0.1")
                port = health_config.get("port", 8765)

                health_thread = start_health_server(metrics, host=host, port=port)
                metrics.set_watching(True, watch_paths)
            except Exception as e:
                logger.warning(f"Failed to start health server: {e}")

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
    logger.info(f"Debounce: {handler.debounce_seconds}s")
    logger.info(f"Extensions: {', '.join(sorted(handler.watched_extensions))}")
    logger.info(f"Max failures: {handler.max_failures}")
    logger.info(f"Quiet mode: {handler.quiet_mode}")
    logger.info(f"Health endpoint: {'enabled' if health_thread else 'disabled'}")
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
  python3 scripts/ai/rag_file_watcher.py --health-endpoint  # Enable health server

Configuration is loaded from config/notion_config.yaml (watcher section).

The watcher monitors:
  - knowledge/    (Local knowledge files and Notion exports)
  - prompts/      (Prompt templates)
        """
    )
    parser.add_argument("--test", action="store_true",
                        help="Test mode - log changes but don't re-index")
    parser.add_argument("--daemon", action="store_true",
                        help="Run as background daemon")
    parser.add_argument("--health-endpoint", action="store_true",
                        help="Enable health check HTTP endpoint")
    parser.add_argument("--paths", nargs="+",
                        help="Paths to watch (overrides config)")

    args = parser.parse_args()

    # Load config
    config = get_notion_config()
    watcher_config = config.get("watcher", {})

    # Determine watch paths (CLI overrides config)
    if args.paths:
        watch_paths = [str(PROJECT_ROOT / p) for p in args.paths]
    else:
        config_paths = watcher_config.get("watch_paths", ["knowledge", "prompts"])
        watch_paths = [str(PROJECT_ROOT / p) for p in config_paths]

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

        # Re-configure logging to write to the file
        # Remove existing handlers (which might be pointing to the old stdout)
        root = logging.getLogger()
        if root.handlers:
            for handler in root.handlers:
                root.removeHandler(handler)
        
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    run_watcher(
        watch_paths,
        config=config,
        test_mode=args.test,
        enable_health_endpoint=args.health_endpoint
    )


if __name__ == "__main__":
    main()
