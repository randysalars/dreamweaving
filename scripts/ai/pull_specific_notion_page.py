#!/usr/bin/env python3
"""
One-off script to pull a specific Notion page and its children
into the shared knowledge/notion_export directory.
Target: "AI AS THE BUSINESS OPERATING SYSTEM"
ID: 2d62bab3796d80468a5ff781e6b68b12
"""

import sys
import os
from pathlib import Path

# Add project root to path so we can import scripts
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from scripts.ai.notion_knowledge_retriever import NotionKnowledgeRetriever

def main():
    # The Notion Page ID provided by the user
    target_page_id = "2d62bab3796d80fc989bccde20994923"
    
    # Output directory (consistent with existing RAG)
    export_dir = project_root / "knowledge" / "notion_export"
    pages_dir = export_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Initializing Notion Retriever...")
    print(f"Target Page ID: {target_page_id}")
    print(f"Export Directory: {pages_dir}")
    
    try:
        retriever = NotionKnowledgeRetriever()
    except Exception as e:
        print(f"Failed to initialize retriever (check .env and config): {e}")
        return

    stats = {"pages": 0, "skipped": 0}
    exported_ids = set()
    
    # Optional: Scan existing to avoid duplicates in this run?
    # For this specific task, we probably want to ensure we get this tree.
    # But let's respect the retriever's logic if we want.
    # Actually, let's just use a fresh set for this run to ensure we track what we pulled.
    
    print(f"\nPhase 1: Fetching Root Page...")
    try:
        # We need to get the page object to create the metadata 'item'
        page = retriever.client.pages.retrieve(page_id=target_page_id)
        
        # Extract title safely
        title = "Untitled"
        props = page.get("properties", {})
        # Title property name varies; usually "title" or "Name"
        # We look for the property that has type "title"
        for prop_name, prop_val in props.items():
            if prop_val.get("type") == "title":
                title_objs = prop_val.get("title", [])
                title = "".join(t.get("plain_text", "") for t in title_objs)
                break
        
        # Fallback if title not found in properties (unlikely for a page)
        if title == "Untitled" and "icon" in page:
             # Sometimes pages rely on icon + untitled? No, just keep Untitled.
             pass

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
            exported_ids=exported_ids, # Pass the set that now includes the root
            depth=0
        )
        
    except Exception as e:
        print(f"Error during retrieval: {e}")
        import traceback
        traceback.print_exc()

    print("\n------------------------------------------------")
    print("Execution Complete")
    print(f"Total Pages Exported: {stats['pages']}")
    print(f"Skipped: {stats['skipped']}")
    print("------------------------------------------------")

if __name__ == "__main__":
    main()
