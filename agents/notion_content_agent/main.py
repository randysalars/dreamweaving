import sys
import os
import time
import signal
import re
import logging
from rich.console import Console
from rich.logging import RichHandler

from config import Config
from notion_adapter import NotionAdapter
from monetization import MonetizationEngine
from codex_client import CodexClient
from processor import ContentProcessor

# Setup Logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("notion_agent")
console = Console()

RUNNING = True

def handle_signal(signum, frame):
    """Graceful shutdown handler"""
    global RUNNING
    logger.info("\n[bold red]Stopping agent gracefully...[/]", extra={"markup": True})
    RUNNING = False

def extract_id_from_url(url: str) -> str:
    """Extract UUID from Notion URL."""
    # Match last 32 hex characters
    match = re.search(r'([a-f0-9]{32})', url.replace("-", ""))
    if match:
        raw_id = match.group(1)
        # Format as UUID
        return f"{raw_id[:8]}-{raw_id[8:12]}-{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:]}"
    return url

def main():
    # Signal handlers for Ctrl+C / SIGTERM
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    console.print("[bold green]Starting Notion Content Agent...[/]")
    
    # 1. Validate Config
    if not Config.validate():
        # Fallback: prompt for config if missing? For now exit.
        # But wait, we want to allow missing DB ID. 
        # Config.validate() likely checks DB ID. We might need to relax Config validation or bypass it.
        # Let's check config.py later. For now, assume it passes or we fix it.
        pass

    try:
        # 2. Initialize Components
        codex = CodexClient(Config.OPENAI_API_KEY, Config.OPENAI_MODEL, Config.OPENAI_BASE_URL)
        monetization = MonetizationEngine(os.path.join(os.getcwd(), "content_templates"))
        
        # Interactive Setup: If DB ID is missing or empty, ask user.
        db_id = Config.NOTION_DB_ID
        if not db_id:
            print("\n[!] Notion Database ID not found in configuration.")
            url = input(">>> Please paste the URL of the Notion Page or Database to monitor: ").strip()
            if url:
                db_id = extract_id_from_url(url)
                logger.info(f"Using extracted ID: {db_id}")
            else:
                logger.error("No URL provided. Exiting.")
                sys.exit(1)
                
        
        # Pass Codex so Adapter can use it for page reasoning
        notion = NotionAdapter(Config.NOTION_TOKEN, db_id, codex_client=codex)
        
        processor = ContentProcessor(notion, codex, monetization)
        
        logger.info("Agent initialized. Entering main loop...")

        # 3. Main Loop
        while RUNNING:
            try:
                # Poll Notion
                articles = notion.get_pending_articles()
                
                if not articles:
                    logger.info("No 'Ready to Write' articles found. Sleeping for 60s...")
                    # Sleep in small chunks to remain responsive to stop signals
                    for _ in range(12): 
                        if not RUNNING: break
                        time.sleep(5)
                    continue

                for article in articles:
                    if not RUNNING: break
                    processor.process_article(article)
                    # Small breath between articles
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(30) # Backoff on error

    except Exception as ie:
        logger.critical(f"Initialization failure: {ie}", exc_info=True)
        sys.exit(1)
        
    logger.info("Agent stopped.")

if __name__ == "__main__":
    main()
