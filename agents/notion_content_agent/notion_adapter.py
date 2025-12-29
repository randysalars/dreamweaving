import sys
import os
import logging
from typing import List, Dict, Any

# Add project root to path to allow importing scripts
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up 2 levels: agents -> dreamweaving
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from scripts.ai.notion_knowledge_retriever import NotionKnowledgeRetriever
except ImportError:
    # Fallback or error if script not found
    raise ImportError("Could not import NotionKnowledgeRetriever from scripts.ai. Ensure dreamweaving project structure is intact.")

logger = logging.getLogger(__name__)

class NotionAdapter(NotionKnowledgeRetriever):
    """
    Extends the existing NotionKnowledgeRetriever to add specific 
    functionality for the Content Agent (status tracking, identifying 'Ready to Write').
    """
    def __init__(self, api_key: str, database_id: str):
        # Initialize the parent retriever (loads config, sets up client)
        # Note: The parent __init__ loads from config/env, but we can override/ensure 
        # the client is set if we passed specific args, or just trust the shared config.
        # We passed api_key/db_id from our agent config, so we explicitly set auth 
        # if the parent didn't already pick it up from the same env source.
        
        super().__init__()
        
        # If the parent loaded a client, great. If we want to force our key:
        if api_key:
             self.client.options.auth = api_key
             
        self.database_id = database_id

    def get_pending_articles(self) -> List[Dict[str, Any]]:
        """
        Fetch articles from the database (or nested databases) with Status='Ready to Write'.
        Handles cases where self.database_id is a Page containing Databases.
        """
        all_articles = []
        
        # 1. Try treating the configured ID as a direct Database
        try:
            articles = self._query_db_for_status(self.database_id)
            all_articles.extend(articles)
            return all_articles
        except Exception as e:
            # 400 Error likely means it's a Page, not a DB.
            logger.info(f"Configured ID {self.database_id} is likely a Page, scanning for nested databases... ({e})")

        # 2. scan for nested databases
        found_dbs = self._find_nested_databases(self.database_id)
        
        if not found_dbs:
            logger.warning(f"No databases found inside page {self.database_id}.")
            return []
            
        logger.info(f"Found {len(found_dbs)} nested databases: {found_dbs}")
        
        # 3. Query each found DB
        for db_id in found_dbs:
            try:
                articles = self._query_db_for_status(db_id)
                all_articles.extend(articles)
            except Exception as e:
                logger.warning(f"Failed to query nested DB {db_id}: {e}")
                
        logger.info(f"Total pending articles found across all databases: {len(all_articles)}")
        return all_articles

    def _query_db_for_status(self, db_id: str) -> List[Dict[str, Any]]:
        """Helper to query a specific DB for Ready to Write status."""
        logger.info(f"Querying Database: {db_id}")
        # Use direct request to bypass client version issues
        response = self.client.request(
            path=f"databases/{db_id}/query",
            method="POST",
            body={
                "filter": {
                    "property": "Status",
                    "status": {
                        "equals": "Ready to Write"
                    }
                }
            }
        )
        return response.get("results", [])

    def _find_nested_databases(self, block_id: str, depth: int = 0, max_depth: int = 3) -> List[str]:
        """Recursive search for child_database blocks."""
        if depth > max_depth:
            return []
            
        found_ids = []
        cursor = None
        
        try:
            while True:
                response = self.client.blocks.children.list(block_id=block_id, start_cursor=cursor)
                
                for block in response.get("results", []):
                    btype = block.get("type")
                    
                    if btype == "child_database":
                        found_ids.append(block["id"])
                    
                    # Recurse into pages to find nested DBs
                    elif btype == "child_page":
                        # DFS recursion
                        found_ids.extend(self._find_nested_databases(block["id"], depth + 1, max_depth))
                        
                if not response.get("has_more"):
                    break
                cursor = response.get("next_cursor")
                
        except Exception as e:
            logger.debug(f"Error scanning block {block_id}: {e}")
            
        return found_ids

    def get_recursive_page_content(self, page_id: str) -> str:
        """
        Retrieves content from the page AND all its subpages.
        Used for creating comprehensive pillar pages.
        """
        # 1. Get main page content
        full_content = [f"# Main Page Content\n(Source ID: {page_id})\n"]
        main_blocks = self._get_all_blocks(page_id)
        full_content.append(self._blocks_to_markdown(main_blocks))
        
        # 2. Find and fetch child pages
        # We scan the blocks we just retrieved for child_page types
        child_pages = []
        for block in main_blocks:
            if block.get("type") == "child_page":
                child_pages.append({
                    "id": block["id"],
                    "title": block.get("child_page", {}).get("title", "Untitled Subpage")
                })
                
        # 3. Recursively fetch their content
        for child in child_pages:
            logger.info(f"Fetching subpage: {child['title']}")
            sub_blocks = self._get_all_blocks(child["id"])
            sub_markdown = self._blocks_to_markdown(sub_blocks)
            
            full_content.append(f"\n\n## Subpage: {child['title']}\n(Source ID: {child['id']})\n")
            full_content.append(sub_markdown)
            
        return "\n".join(full_content)

    def update_status(self, page_id: str, status: str):
        """
        Update the 'Status' property of a page.
        """
        try:
            self.client.pages.update(
                page_id=page_id,
                properties={"Status": {"status": {"name": status}}}
            )
            logger.info(f"Updated page {page_id} status to '{status}'")
        except Exception as e:
            logger.error(f"Failed to update status for page {page_id}: {e}")

