import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path("/home/rsalars/Projects/dreamweaving")
sys.path.append(str(PROJECT_ROOT))

try:
    from scripts.ai.notion_knowledge_retriever import NotionKnowledgeRetriever
except ImportError as e:
    print(f"Error importing NotionKnowledgeRetriever: {e}")
    sys.exit(1)

def main():
    retriever = NotionKnowledgeRetriever()
    page_id = "2c92bab3-796d-802a-b5b3-f8a00dcd87fc"
    
    print(f"Checking for children of page {page_id}...")
    blocks = retriever._get_all_blocks(page_id)
    children = [b for b in blocks if b['type'] == 'child_page']
    
    if not children:
        print("No child pages found.")
    else:
        print(f"Found {len(children)} child pages:")
        for child in children:
            title = child.get('child_page', {}).get('title', 'Unknown Title')
            print(f"  - {title} (ID: {child['id']})")
            
            # Get content of child
            content = retriever.get_page_content(child['id'])
            print(f"--- Content of {title} ---")
            print(content[:500] + "..." if len(content) > 500 else content)
            print("-" * 30)

if __name__ == "__main__":
    main()
