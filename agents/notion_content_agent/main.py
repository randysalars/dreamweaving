import sys
import time
import signal
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

def main():
    # Signal handlers for Ctrl+C / SIGTERM
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    console.print("[bold green]Starting Notion Content Agent...[/]")
    
    # 1. Validate Config
    if not Config.validate():
        sys.exit(1)

    try:
        # 2. Initialize Components
        notion = NotionAdapter(Config.NOTION_TOKEN, Config.NOTION_DB_ID)
        monetization = MonetizationEngine(os.path.join(os.getcwd(), "content_templates"))
        codex = CodexClient(Config.OPENAI_API_KEY, Config.OPENAI_MODEL, Config.OPENAI_BASE_URL)
        
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
