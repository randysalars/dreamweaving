
import sys
from scripts.ai.notion_knowledge_retriever import NotionKnowledgeRetriever

def main():
    retriever = NotionKnowledgeRetriever()
    page_id = "2d62bab3-796d-80fe-8d9c-f98e763b16b8"
    print(f"Fetching content for page ID: {page_id}")
    try:
        content = retriever.get_page_content(page_id)
        print(content)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
