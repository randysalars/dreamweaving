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
    def __init__(self, api_key: str, database_id: str, codex_client=None):
        super().__init__()
        if api_key:
             self.client.options.auth = api_key
        self.database_id = database_id
        self.codex_client = codex_client

    def get_pending_articles(self) -> List[Dict[str, Any]]:
        """
        Fetch articles.
        1. Try Database Query (Status='Ready to Write').
        2. If that fails or finds nothing, and we have an LLM attached:
           READ THE FULL PAGE CONTENT and use LLM to identifying tasks.
        3. Fallback: Recursive scan of subpages.
        """
        all_articles = []
        
        # 1. Try treating the configured ID as a direct Database
        try:
            articles = self._query_db_for_status(self.database_id)
            if articles:
                logger.info(f"Found {len(articles)} articles via Database Query.")
                all_articles.extend(articles)
                return all_articles
        except Exception as e:
            logger.debug(f"Direct DB query failed: {e}")

        # 2. AI Reasoning / Page Reading
        if self.codex_client:
            logger.info(f"Reading full content of page {self.database_id} for AI analysis...")
            try:
                # We reuse the recursive fetcher to get all text
                full_text = self.get_recursive_page_content(self.database_id)
                if not full_text:
                    logger.warning("Page content is empty.")
                else:
                    logger.info("Content fetched. Analyzing with AI...")
                    ai_tasks = self.codex_client.extract_tasks_from_page(full_text)
                    logger.info(f"AI identified {len(ai_tasks)} potential articles.")
                    
                    # Convert AI tasks to "Article" objects
                    for task in ai_tasks:
                        # Create a mock ID using hash of title to ensure uniqueness?
                        # Or just use the Page ID but with metadata?
                        # We use the Page ID as the ID, but we set a custom "property" 
                        # so that processor knows to use the AI context.
                        # Wait, we need distinct IDs for distinct tasks.
                        # We can't really "update status" on them if they don't have real Notion Block IDs.
                        # BUT, maybe the AI can return Block IDs? 
                        # Not robustly.
                        # For now, we return virtual objects. Update Status will fail, but Processor handles that.
                        import hashlib
                        fake_id = hashlib.md5(task['title'].encode()).hexdigest()
                        
                        all_articles.append({
                            "id": f"ai-task-{fake_id}", 
                            "properties": {
                                "Name": {"title": [{"text": {"content": task['title']}}]},
                                "Status": {"select": {"name": "AI Discovery"}},
                                "Type": "AI Task",
                                "Instructions": task.get('instructions', '')
                            },
                            "url": f"https://notion.so/{self.database_id}"
                        })
                    
                    if all_articles:
                        return all_articles
            except Exception as e:
                logger.error(f"AI Analysis failed: {e}")

        # 3. Fallback: Recursively find all subpages/blocks (Mechanistic)
        logger.info(f"Fallback: Scanning page {self.database_id} recursively for subpages...")
        subpages = self._scan_page_tree_for_articles(self.database_id)
        
        # Deduplicate
        unique_pages = {p['id']: p for p in subpages}.values()
        return list(unique_pages)

    def _query_db_for_status(self, db_id: str) -> List[Dict[str, Any]]:
        """Helper to query a specific DB for Ready to Write status."""
        # ... (same as before) ...
        # But suppress errors to allow fallback
        try:
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
        except:
            return []

    def _scan_page_tree_for_articles(self, block_id: str, depth: int = 0, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Recursively find ANY child_page OR text list item and treat it as an article candidate.
        """
        if depth > max_depth:
            return []
            
        articles = []
        cursor = None
        
        try:
            while True:
                response = self.client.blocks.children.list(block_id=block_id, start_cursor=cursor)
                
                for block in response.get("results", []):
                    btype = block.get("type")
                    
                    # 1. Child Pages (existing logic)
                    if btype == "child_page":
                        page_title = block.get("child_page", {}).get("title", "Untitled")
                        articles.append(self._create_candidate(block["id"], page_title, "Page"))
                        # Recurse
                        articles.extend(self._scan_page_tree_for_articles(block["id"], depth + 1, max_depth))
                        
                    # 2. List Items / Checkboxes (New Logic: Treat lines as tasks/articles)
                    elif btype in ["to_do", "bulleted_list_item", "numbered_list_item"]:
                        content = block.get(btype, {})
                        text_objs = content.get("rich_text", [])
                        plain_text = "".join([t.get("plain_text", "") for t in text_objs]).strip()
                        
                        # Only consider if substantial text (avoid empty lines)
                        # Also check if checked? Maybe ignore checked items?
                        is_checked = content.get("checked", False)
                        
                        if plain_text and not is_checked:
                             # Use the text as the title/spec
                             articles.append(self._create_candidate(block["id"], plain_text, "Block Item"))
                             
                        # Recurse (items can have nested sub-items)
                        if block.get("has_children"):
                             articles.extend(self._scan_page_tree_for_articles(block["id"], depth + 1, max_depth))

                    # 3. Layout Blocks (recurse transparently)
                    elif btype in ["column_list", "column"]:
                        articles.extend(self._scan_page_tree_for_articles(block["id"], depth, max_depth)) 
                        
                if not response.get("has_more"):
                    break
                cursor = response.get("next_cursor")
                
        except Exception as e:
            logger.debug(f"Error scanning block {block_id}: {e}")
            
        return articles

    def _create_candidate(self, cid: str, title: str, source_type: str) -> Dict[str, Any]:
        """Helper to format a candidate article object."""
        return {
            "id": cid,
            "properties": {
                "Name": {"title": [{"type": "text", "text": {"content": title}, "plain_text": title}]},
                "Status": {"select": {"name": "Manual Discovery"}},
                "Type": source_type
            },
            "url": f"https://notion.so/{cid.replace('-', '')}"
        }

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

