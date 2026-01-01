# Antigravity Notion RAG Guide

This guide explains how Antigravity (and other agents) can interact with the Notion RAG system in the `dreamweaving` project.

## Overview
The Notion RAG system allows for:
1.  **Semantic Search**: Query the knowledge base using natural language.
2.  **Page Retrieval**: Fetch full markdown content of specific Notion pages.
3.  **Synchronization**: Update the local knowledge base from Notion.

## Setup
All scripts are located in `scripts/ai/` and utilize the `venv` in the `dreamweaving` root.
**Working Directory**: `/home/rsalars/Projects/dreamweaving`
**Python Interpreter**: `./venv/bin/python3`

## Usage

### 1. Semantic Search
Search the vector database for concepts, archetypes, or general knowledge.

**Command:**
```bash
./venv/bin/python3 -m scripts.ai.notion_embeddings_pipeline --search "YOUR QUERY HERE"
```

**Example:**
```bash
./venv/bin/python3 -m scripts.ai.notion_embeddings_pipeline --search "shadow archetype"
```

### 2. Retrieve Specific Page
Get the full markdown content of a page by its exact title. This is useful when you know the page name from a search result.

**Command:**
```bash
./venv/bin/python3 -m scripts.ai.notion_knowledge_retriever --page "Exact Page Title"
```

**Example:**
```bash
./venv/bin/python3 -m scripts.ai.notion_knowledge_retriever --page "Sacred Digital Dreamweaver"
```

### 3. Search by Title
If the semantic search fails, search by title keyword using the Notion API directly.

**Command:**
```bash
./venv/bin/python3 -m scripts.ai.notion_knowledge_retriever --search "keyword"
```

### 4. Sync / Update Index
Run this if the user has added new content to Notion that needs to be reflected in the RAG.

**Command:**
```bash
./venv/bin/python3 scripts/ai/rag_auto_sync.py
```

## Troubleshooting
-   **"Module not found"**: Ensure you are running with `./venv/bin/python3`.
-   **"NOTION_TOKEN not set"**: The scripts automatically load `.env`. Verify `.env` exists in the project root.
