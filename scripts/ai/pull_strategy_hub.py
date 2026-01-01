#!/usr/bin/env python3
"""
Pull "STRATEGY ETHICS LONG TERM VISION" Page and Children
ID: 2d62bab3796d80b28086cc5f6dec683a
"""

import sys
import os
from pathlib import Path

# Add project root to path so we can import scripts
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from scripts.ai.notion_knowledge_retriever import NotionKnowledgeRetriever

def main():
    # The Notion Page ID from the URL provided
    target_page_id = "2d62bab3796d80b28086cc5f6dec683a"
    
    # Output directory
    export_dir = project_root / "knowledge" / "notion_export"
    pages_dir = export_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Initializing Notion Retriever...")
    print(f"Target Page ID: {target_page_id}")
    print(f"Export Directory: {pages_dir}")
    
    try:
        retriever = NotionKnowledgeRetriever()
    except Exception as e:
        print(f"Failed to initialize retriever: {e}")
        return

    stats = {"pages": 0, "skipped": 0}
    exported_ids = set()
    
    print(f"\nPhase 1: Fetching Root Page...")
    try:
        # Get page object
        page = retriever.client.pages.retrieve(page_id=target_page_id)
        
        # Extract title
        title = "Untitled"
        props = page.get("properties", {})
        for prop_name, prop_val in props.items():
            if prop_val.get("type") == "title":
                title_objs = prop_val.get("title", [])
                title = "".join(t.get("plain_text", "") for t in title_objs)
                break
        
        item = {
            "id": page["id"],
            "title": title,
            "url": page.get("url", ""),
            "last_edited_time": page.get("last_edited_time", ""),
            "type": "page"
        }
        
        print(f"Found Root Page: {title}")
        
        # Export root
        if retriever._export_single_page(item, pages_dir, stats, exported_ids):
            print("  > Root page exported successfully.")
        else:
            print("  > Failed to export root page.")

        print(f"\nPhase 2: Crawling Children...")
        retriever._crawl_and_export_children(
            parent_id=target_page_id,
            pages_dir=pages_dir,
            stats=stats,
            exported_ids=exported_ids,
            depth=0
        )
        
    except Exception as e:
        print(f"Error during retrieval: {e}")
        import traceback
        traceback.print_exc()

    print("\nExtraction Complete")
    print(f"Total Pages: {stats['pages']}")

if __name__ == "__main__":
    main()
