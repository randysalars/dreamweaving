---
description: Use the Dreamweaving Notion RAG to search, retrieve, and sync knowledge.
---
# Use Notion RAG

This workflow allows you to interact with the Notion RAG system.

### Prerequisites
-   You must process these commands in the `/home/rsalars/Projects/dreamweaving` directory.
-   Use `./venv/bin/python3` to execute Python scripts.

## 1. Search Knowledge Base
Use this to find relevant information, concepts, or page titles.

```bash
cd /home/rsalars/Projects/dreamweaving
./venv/bin/python3 -m scripts.ai.notion_embeddings_pipeline --search "<YOUR_QUERY>"
```

## 2. Get Page Content
Use this to read the full content of a page found in search results.

```bash
cd /home/rsalars/Projects/dreamweaving
./venv/bin/python3 -m scripts.ai.notion_knowledge_retriever --page "<EXACT_PAGE_TITLE>"
```

## 3. Sync Knowledge Base
Use this to update the local index with recent changes from Notion.

```bash
cd /home/rsalars/Projects/dreamweaving
./venv/bin/python3 scripts/ai/rag_auto_sync.py
```
