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
    console.print("[bold green]Starting Notion Content Agent...[/]")
    
    # 1. Validate Config
    if not Config.validate():
        pass

    try:
        # 2. Initialize Components
        codex = CodexClient(Config.OPENAI_API_KEY, Config.OPENAI_MODEL, Config.OPENAI_BASE_URL)
        monetization = MonetizationEngine(os.path.join(os.getcwd(), "content_templates"))
        
        # Interactive Setup: If DB ID is missing or empty, ask user.
        db_id = Config.NOTION_DB_ID
        if not db_id:
            print("\n[!] Notion Database ID not found in configuration.")
            while not db_id:
                try:
                    url = input(">>> Please paste the URL of the Notion Page or Database to monitor: ").strip()
                except KeyboardInterrupt:
                    print("\nExiting.")
                    sys.exit(0)
                    
                if url:
                    extracted = extract_id_from_url(url)
                    if extracted == url and "-" not in extracted and len(extracted) != 32:
                        logger.error("Invalid URL or ID format. Could not extract UUID.")
                        continue
                    db_id = extracted
                    logger.info(f"Using extracted ID: {db_id}")
                else:
                    logger.error("No URL provided. Exiting.")
                    sys.exit(1)
                
        
        # Pass Codex so Adapter can use it for page reasoning
        notion = NotionAdapter(Config.NOTION_TOKEN, db_id, codex_client=codex)
        
        processor = ContentProcessor(notion, codex, monetization)
        
        logger.info("Agent initialized. Entering main loop...")

        # 3. Main Loop
        while True:
            try:
                # Poll Notion
                articles = notion.get_pending_articles()
                
                if not articles:
                    logger.info("No 'Ready to Write' articles found. Sleeping for 60s...")
                    # Sleep in small chunks to allow Interrupt
                    for _ in range(12): 
                       time.sleep(5)
                    continue

                processed_count = 0
                for article in articles:
                    processor.process_article(article)
                    processed_count += 1
                    
                    if Config.TEST_MODE and processed_count >= 3:
                        logger.info("[TEST MODE] Limit of 3 articles reached. Exiting.")
                        sys.exit(0)
                        
                    time.sleep(2)
                    
            except KeyboardInterrupt:
                raise # Re-raise to outer block
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(30) # Backoff on error

    except KeyboardInterrupt:
        logger.info("\nAgent stopped by user.")
        sys.exit(0)
    except Exception as ie:
        logger.critical(f"Initialization failure: {ie}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    if "--test" in sys.argv:
        print("[TEST MODE] Limiting to 3 articles with auto-generation.")
        Config.TEST_MODE = True
    else:
        Config.TEST_MODE = False
    
    main()
