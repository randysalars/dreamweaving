import sys
import os
import logging
from typing import List, Dict, Any

# Add project root to path to allow importing scripts
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
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
        Fetch articles from the database with Status='Ready to Write'.
        """
        try:
            logger.info(f"Querying Notion Database: {self.database_id}")
            response = self.client.databases.query(
                **{
                    "database_id": self.database_id,
                    "filter": {
                        "property": "Status",
                        "status": {
                            "equals": "Ready to Write"
                        }
                    }
                }
            )
            results = response.get("results", [])
            logger.info(f"Found {len(results)} pending articles.")
            return results
        except Exception as e:
            logger.error(f"Failed to fetch pending articles: {e}")
            raise

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

