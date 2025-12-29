#!/usr/bin/env python3
"""
Notion Content Agent - Main Entry Point

An automated content generation pipeline that monitors Notion databases
for articles marked "Ready to Write" and generates SEO-optimized content.

Usage:
    # Standard polling mode
    python main.py

    # With custom settings
    python main.py --concurrent 5 --poll-interval 120

    # Dry run (no actual processing)
    python main.py --dry-run

    # Test mode (limited articles)
    python main.py --test

    # Batch mode (process once, no polling)
    python main.py --batch
"""

import sys
import os
import signal
import re
import logging
import argparse
import asyncio
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

from config import Config
from notion_adapter import NotionAdapter
from monetization import MonetizationEngine
from codex_client import CodexClient
from processor import ContentProcessor
from constants import Defaults, LogMessages, NotionStatus
from models import ProcessingResult
from core.orchestrator import AsyncOrchestrator, BatchOrchestrator
from ui.interactive import InteractiveUI
from utils.metrics import MetricsTracker

# Setup Logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("notion_agent")
console = Console()

# Global orchestrator reference for signal handling
_orchestrator: Optional[AsyncOrchestrator] = None


_shutdown_count = 0


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global _shutdown_count
    _shutdown_count += 1
    logger.info(LogMessages.SHUTDOWN_SIGNAL.format(signum=signum))

    if _shutdown_count >= 2:
        # Force exit on second Ctrl+C - use os._exit() to bypass input() blocking
        logger.warning("Forced shutdown requested. Exiting immediately...")
        os._exit(1)

    if _orchestrator:
        _orchestrator.request_shutdown()
    else:
        # No orchestrator, exit directly
        sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def extract_id_from_url(url: str) -> str:
    """Extract UUID from Notion URL."""
    match = re.search(r'([a-f0-9]{32})', url.replace("-", ""))
    if match:
        raw_id = match.group(1)
        return f"{raw_id[:8]}-{raw_id[8:12]}-{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:]}"
    return url


def save_database_id_to_env(db_id: str) -> bool:
    """Save database ID to .env file for future use."""
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        dotenv_path = os.path.join(project_root, ".env")

        if os.path.exists(dotenv_path):
            with open(dotenv_path, 'r') as f:
                content = f.read()

            # Replace existing or append
            if 'NOTION_DB_ID=' in content:
                content = re.sub(r'NOTION_DB_ID=.*', f'NOTION_DB_ID={db_id}', content)
                with open(dotenv_path, 'w') as f:
                    f.write(content)
            else:
                with open(dotenv_path, 'a') as f:
                    f.write(f"\n# Auto-saved from interactive prompt\nNOTION_DB_ID={db_id}\n")
        else:
            with open(dotenv_path, 'w') as f:
                f.write(f"# Auto-saved from interactive prompt\nNOTION_DB_ID={db_id}\n")

        logger.info(f"Saved database ID to {dotenv_path}")
        return True
    except Exception as e:
        logger.warning(f"Could not save database ID to .env: {e}")
        return False


def save_target_path_to_env(target_path: str) -> bool:
    """Save target path to .env file for future use."""
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        dotenv_path = os.path.join(project_root, ".env")

        if os.path.exists(dotenv_path):
            with open(dotenv_path, 'r') as f:
                content = f.read()

            # Replace existing or append
            if 'DEFAULT_TARGET_PATH=' in content:
                content = re.sub(r'DEFAULT_TARGET_PATH=.*', f'DEFAULT_TARGET_PATH={target_path}', content)
                with open(dotenv_path, 'w') as f:
                    f.write(content)
            else:
                with open(dotenv_path, 'a') as f:
                    f.write(f"\n# Auto-saved from interactive prompt\nDEFAULT_TARGET_PATH={target_path}\n")
        else:
            with open(dotenv_path, 'w') as f:
                f.write(f"# Auto-saved from interactive prompt\nDEFAULT_TARGET_PATH={target_path}\n")

        logger.info(f"Saved target path to {dotenv_path}")
        return True
    except Exception as e:
        logger.warning(f"Could not save target path to .env: {e}")
        return False


def get_target_path(args: argparse.Namespace) -> str:
    """Get target path from args, config, or user input."""
    # Priority: CLI arg > Interactive prompt > Config default
    if hasattr(args, 'target_path') and args.target_path:
        path = args.target_path
        logger.info(f"Using target path from CLI: {path}")
        return path if path.startswith('/') else '/' + path

    # In batch/no-interactive mode, use config without prompting
    if args.no_interactive or args.batch:
        path = Config.DEFAULT_TARGET_PATH or '/ai'
        logger.info(f"Using target path from config: {path}")
        return path

    # Interactive prompt - ALWAYS ask in interactive mode
    default_path = Config.DEFAULT_TARGET_PATH or '/ai'
    print("\n[?] Website Integration Setup")
    print("    Enter the target path for articles (e.g., /ai, /operations)")
    print("    Just enter the page name with a slash (e.g., /mypage)")
    target_path = input(f"    Path [{default_path}]: ").strip()

    if not target_path:
        target_path = default_path

    # Ensure path starts with /
    if not target_path.startswith('/'):
        target_path = '/' + target_path

    logger.info(f"Using target path: {target_path}")

    # Auto-save to .env for future runs
    save_target_path_to_env(target_path)

    return target_path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Notion Content Agent - Automated content generation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     # Standard polling mode
  python main.py --concurrent 5      # Process 5 articles concurrently
  python main.py --dry-run           # Simulate without processing
  python main.py --batch             # Process once, no polling
  python main.py --test              # Test mode (max 3 articles)
        """
    )

    parser.add_argument(
        "--concurrent", "-c",
        type=int,
        default=Defaults.MAX_CONCURRENT,
        help=f"Maximum concurrent article processing (default: {Defaults.MAX_CONCURRENT})"
    )

    parser.add_argument(
        "--poll-interval", "-i",
        type=int,
        default=Defaults.POLL_INTERVAL_SECONDS,
        help=f"Polling interval in seconds (default: {Defaults.POLL_INTERVAL_SECONDS})"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate processing without making changes"
    )

    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process once and exit (no continuous polling)"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode - limit to 3 articles with auto-processing"
    )

    parser.add_argument(
        "--database-id", "-d",
        type=str,
        help="Notion database ID (overrides config)"
    )

    parser.add_argument(
        "--target-path", "-t",
        type=str,
        help="Website target path for articles (e.g., /ai/operations)"
    )

    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Disable interactive prompts (use defaults)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def get_database_id(args: argparse.Namespace, ui: InteractiveUI) -> str:
    """Get database ID from args, config, or user input."""
    # Priority: CLI arg > Interactive prompt > Config
    if args.database_id:
        db_id = extract_id_from_url(args.database_id)
        logger.info(f"Using database ID from CLI: {db_id}")
        return db_id

    # In batch/no-interactive mode, use config without prompting
    if args.no_interactive or args.batch:
        if not Config.NOTION_DB_ID:
            logger.error("No database ID configured and --batch/--no-interactive specified")
            sys.exit(1)
        logger.info("Using database ID from config")
        return Config.NOTION_DB_ID

    # Interactive prompt - ALWAYS ask, show saved value as default
    default_id = Config.NOTION_DB_ID or ""
    print("\n[?] Notion Database Setup")
    if default_id:
        print(f"    Current: {default_id}")
    url = input(f"    Enter Notion database URL or ID [{default_id or 'required'}]: ").strip()

    if not url:
        if default_id:
            logger.info("Using saved database ID from config")
            return default_id
        else:
            logger.error("No database ID provided. Exiting.")
            sys.exit(1)

    db_id = extract_id_from_url(url)
    if db_id == url and "-" not in db_id and len(db_id) != 32:
        logger.error("Invalid URL or ID format. Could not extract UUID.")
        sys.exit(1)

    logger.info(f"Using extracted ID: {db_id}")

    # Auto-save to .env for future runs (will update if changed)
    save_database_id_to_env(db_id)

    return db_id


def create_process_fn(processor: ContentProcessor, dry_run: bool = False):
    """Create the article processing function for the orchestrator."""

    def process_article(article: dict) -> ProcessingResult:
        """Process a single article."""
        page_id = article.get("id", "unknown")

        if dry_run:
            title = "Unknown"
            try:
                props = article.get("properties", {})
                title_prop = props.get("Name") or props.get("Title") or {}
                if title_prop.get("title"):
                    title = title_prop["title"][0].get("plain_text", "Unknown")
            except Exception:
                pass

            logger.info(f"[DRY-RUN] Would process: '{title}' ({page_id})")
            return ProcessingResult(
                article_id=page_id,
                success=True,
                output_path="[DRY-RUN]"
            )

        try:
            processor.process_article(article)
            return ProcessingResult(
                article_id=page_id,
                success=True
            )
        except Exception as e:
            logger.error(f"Failed to process article {page_id}: {e}")
            return ProcessingResult(
                article_id=page_id,
                success=False,
                error=str(e)
            )

    return process_article


async def run_async(args: argparse.Namespace):
    """Run the agent in async mode."""
    global _orchestrator

    console.print("[bold green]Starting Notion Content Agent...[/]")

    # Validate config
    if not Config.validate():
        logger.critical("Configuration validation failed. Exiting.")
        sys.exit(1)

    # Initialize UI
    ui = InteractiveUI(console)

    # Get database ID
    db_id = get_database_id(args, ui)

    # Get target path (will prompt if not configured and not in batch mode)
    target_path = get_target_path(args)
    Config.DEFAULT_TARGET_PATH = target_path  # Update runtime config

    try:
        # Initialize components
        codex = CodexClient(
            Config.OPENAI_API_KEY,
            Config.OPENAI_MODEL,
            Config.OPENAI_BASE_URL
        )
        monetization = MonetizationEngine(
            os.path.join(os.path.dirname(__file__), "content_templates")
        )
        notion = NotionAdapter(Config.NOTION_TOKEN, db_id, codex_client=codex)
        processor = ContentProcessor(notion, codex, monetization, target_path=target_path)

        # Create processing function
        process_fn = create_process_fn(processor, dry_run=args.dry_run)

        # Configure test mode
        article_limit = Defaults.TEST_MODE_ARTICLE_LIMIT if args.test else None

        if args.batch:
            # Batch mode - process once and exit
            logger.info("Running in batch mode (process once, no polling)")

            orchestrator = BatchOrchestrator(
                process_fn=process_fn,
                max_concurrent=args.concurrent,
                article_limit=article_limit
            )
            _orchestrator = orchestrator

            articles = notion.get_pending_articles()
            if not articles:
                logger.info("No pending articles found.")
                return

            def on_progress(current: int, total: int):
                ui.show_progress(current, total, f"Article {current}")

            results = await orchestrator.run(articles, on_progress=on_progress)

            # Print summary
            success_count = sum(1 for r in results if r.success)
            logger.info(f"Batch complete: {success_count}/{len(results)} successful")

        else:
            # Polling mode - continuous processing
            logger.info(
                f"Running in polling mode "
                f"(interval: {args.poll_interval}s, concurrent: {args.concurrent})"
            )

            orchestrator = AsyncOrchestrator(
                process_fn=process_fn,
                max_concurrent=args.concurrent,
                dry_run=args.dry_run
            )
            _orchestrator = orchestrator

            # Run polling loop
            await orchestrator.run_polling_loop(
                fetch_fn=notion.get_pending_articles,
                interval=args.poll_interval
            )

    except KeyboardInterrupt:
        logger.info(LogMessages.AGENT_STOPPED)
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point."""
    args = parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Store test mode in config for compatibility
    Config.TEST_MODE = args.test

    # Enable batch mode when --batch or --no-interactive is used
    # This disables ALL interactive prompts (path, section, confirmation)
    Config.BATCH_MODE = args.batch or args.no_interactive

    # Run async main
    try:
        asyncio.run(run_async(args))
    except KeyboardInterrupt:
        logger.info(LogMessages.AGENT_STOPPED)
        sys.exit(0)


if __name__ == "__main__":
    main()
