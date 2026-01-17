---
description: Use the Dreamweaving Notion RAG to search, retrieve, and sync knowledge.
---
# Use Notion RAG

This workflow allows you to interact with the Notion RAG system.

### Prerequisites
-   You must process these commands in the `/home/rsalars/Projects/dreamweaving` directory.
-   Use `./venv/bin/python3` to execute Python scripts.

---

## 🪙 COIN KNOWLEDGE CHAT (Recommended)

### Interactive Chat Mode
Start a conversation with the coin knowledge base:
```bash
cd /home/rsalars/Projects/dreamweaving
./venv/bin/python3 -m scripts.ai.coin_chat
```

### Single Question Mode
Ask a quick question:
```bash
./venv/bin/python3 -m scripts.ai.coin_chat --ask "What's a good first Morgan dollar to buy?"
```

### Show Available Topics
```bash
./venv/bin/python3 -m scripts.ai.coin_chat --topics
```

---

## 📚 Index Coin YAML Guides

Index the structured YAML coin guides (Morgan, Peace, Junk Silver, etc.) into the searchable database:

```bash
cd /home/rsalars/Projects/dreamweaving
./venv/bin/python3 -m scripts.ai.index_coin_knowledge --verbose
```

List available coin knowledge files:
```bash
./venv/bin/python3 -m scripts.ai.index_coin_knowledge --list
```

---

## 🔍 Search Knowledge Base
Use this to find relevant information, concepts, or page titles.

```bash
cd /home/rsalars/Projects/dreamweaving
./venv/bin/python3 -m scripts.ai.notion_embeddings_pipeline --search "<YOUR_QUERY>"
```

## 📄 Get Page Content
Use this to read the full content of a page found in search results.

```bash
cd /home/rsalars/Projects/dreamweaving
./venv/bin/python3 -m scripts.ai.notion_knowledge_retriever --page "<EXACT_PAGE_TITLE>"
```

## 🔄 Sync Knowledge Base
Use this to update the local index with recent changes from Notion.

```bash
cd /home/rsalars/Projects/dreamweaving
./venv/bin/python3 scripts/ai/rag_auto_sync.py
```
