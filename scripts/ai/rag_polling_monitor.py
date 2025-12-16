#!/usr/bin/env python3
"""
Lightweight polling monitor for Notion RAG changes.

Instead of a high-frequency filesystem watcher, this script runs the
Notion export + incremental re-index on a fixed interval. It is
intended to be CPU-friendly (sleeping between runs) while still keeping
the local vector index up to date.

Examples:
    python3 scripts/ai/rag_polling_monitor.py --once
    python3 scripts/ai/rag_polling_monitor.py --interval 900
    python3 scripts/ai/rag_polling_monitor.py --interval 1800 --full
"""
import argparse
import logging
import signal
import time
from typing import Optional

# Use shared utilities for project setup
from scripts.ai.rag_utils import setup_project_path, load_dotenv_safe, get_notion_config

setup_project_path()
load_dotenv_safe()

from scripts.ai.rag_auto_sync import RAGAutoSync  # noqa: E402

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Polling-based Notion RAG change monitor (low CPU alternative to file watcher)."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=900,
        help="Seconds between sync attempts (default: 900 / 15 minutes).",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run a full re-index instead of incremental mode.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-index even if no changes are detected by the pipeline.",
    )
    parser.add_argument(
        "--export-dir",
        default="knowledge/notion_export",
        help="Notion export directory (default: knowledge/notion_export).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single sync pass and exit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only check for changes and log the result; do not index.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output from embeddings pipeline.",
    )
    return parser.parse_args()


def perform_iteration(
    syncer: RAGAutoSync, full_reindex: bool, force: bool, dry_run: bool
) -> Optional[dict]:
    """
    Run a single poll iteration. In dry-run mode, only checks for changes.
    """
    if dry_run:
        has_changes = syncer.check_for_changes()
        if has_changes:
            logger.info("Changes detected (dry-run). Run without --dry-run to index.")
            return {"status": "changes_detected", "timestamp": time.time()}
        logger.info("No changes detected (dry-run).")
        return {"status": "no_changes", "timestamp": time.time()}

    return syncer.sync(force=force, full_reindex=full_reindex)


def main():
    args = parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Load quiet mode from config if not explicitly set
    config = get_notion_config()
    quiet_mode = args.quiet or config.get("watcher", {}).get("quiet_mode", False)

    syncer = RAGAutoSync(export_dir=args.export_dir, quiet=quiet_mode)
    stop_requested = False

    def handle_signal(signum, frame):
        nonlocal stop_requested
        stop_requested = True
        logger.info("Received signal %s, will stop after current iteration.", signum)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    iteration = 0
    while True:
        iteration += 1
        logger.info(
            "Polling iteration %s (interval=%ss, mode=%s, force=%s, dry_run=%s)",
            iteration,
            args.interval,
            "full" if args.full else "incremental",
            args.force,
            args.dry_run,
        )

        try:
            result = perform_iteration(
                syncer,
                full_reindex=args.full,
                force=args.force,
                dry_run=args.dry_run,
            )
            if result:
                logger.debug("Iteration result: %s", result)
        except Exception as exc:  # pragma: no cover - safety net
            logger.exception("Sync iteration failed: %s", exc)

        if args.once or stop_requested:
            break

        # Sleep until next interval, exit early if signal received
        slept = 0
        while slept < args.interval and not stop_requested:
            time.sleep(1)
            slept += 1

    logger.info("Polling monitor stopped.")


if __name__ == "__main__":
    main()
