# Codex ↔ Notion RAG (Dreamweaving)

This repo already has a Notion→local RAG pipeline (export → embeddings → Qdrant). This guide wires that into the VS Code Codex extension via MCP so you can:

- **Pull**: semantically search your canonical Notion knowledge (fast, local Qdrant)
- **Push**: read/write Notion pages/databases (official Notion MCP server)
- **Sync**: re-export + incrementally update the local index after edits

---

## What’s Already Set Up

### 1) Notion export (markdown)
- Script: `scripts/ai/notion_knowledge_retriever.py`
- Output: `knowledge/notion_export/` (markdown files + `manifest.json`)

### 2) Embeddings + vector search (Qdrant local)
- Script: `scripts/ai/notion_embeddings_pipeline.py`
- Vector DB: `knowledge/vector_db/` (Qdrant local storage)
- Current index (example): `./venv/bin/python3 -m scripts.ai.notion_embeddings_pipeline --stats`

By default it prefers **local embeddings** (`sentence-transformers`, `all-MiniLM-L6-v2`, 384 dims). OpenAI embeddings are a fallback if local isn’t available.

### 3) Auto-sync job (optional)
- Script: `scripts/ai/rag_auto_sync.py`
- Service unit: `scripts/scheduling/rag-sync.service`

---

## MCP: Make It Available to Codex (VS Code)

This repo includes an MCP config file you can point Codex at:
- `mcp.json`

It starts two MCP servers:
- `notion` (official Notion MCP server) for **read/write**
- `dreamweaving-rag` (this repo) for **semantic search + sync**

Both wrappers load `./.env` automatically so your `NOTION_TOKEN` is available.

### Prereqs
- Node.js available (for Notion MCP via `npx`)
- Python deps installed in `./venv/` (see `requirements.txt`)
- `.env` contains `NOTION_TOKEN=...`
- The Notion integration is connected to the **Sacred Digital Dreamweaver** root page (subpages inherit access).

### VS Code setup
In the Codex VS Code extension, add an MCP configuration file and point it at:
- `mcp.json`

Then reload VS Code (or restart the extension) so it starts the servers.

### Quick verification (outside VS Code)
- RAG index reachable: `./venv/bin/python3 -m scripts.ai.notion_embeddings_pipeline --stats`
- Notion token reachable: `./venv/bin/python3 -m scripts.ai.notion_knowledge_retriever --search "Dreamweaver"`
- MCP servers reachable: `./scripts/utilities/smoke_mcp_server.py dreamweaving-rag` and `./scripts/utilities/smoke_mcp_server.py notion`

---

## How to Use in Codex Chat

### Semantic search (local index)
- “Use `dreamweaving_rag_search` for: *shadow healing journey*”
- “Search for *Navigator archetype* and summarize the top 5 results.”

### Sync after you edit Notion
- “Run `dreamweaving_rag_sync` to refresh the local index.”

### Push updates to Notion
Use the Notion MCP tools (from the `notion` server) to create/update pages or blocks, then run:
- `dreamweaving_rag_sync`

---

## Troubleshooting

### `dreamweaving_rag_sync` fails with “NOTION_TOKEN not set”
- Confirm `NOTION_TOKEN=...` exists in `./.env`.
- Re-run: `./venv/bin/python3 scripts/ai/rag_auto_sync.py --json` (it now auto-loads `./.env`).

### MCP servers don’t appear in Codex
- Ensure the Codex extension is actually using `mcp.json` from this workspace.
- Confirm `bash`, `npx`, and `./venv/bin/python3` exist on your PATH / filesystem.

---

## CLI (Optional) Quick Checks

- Vector index stats: `./venv/bin/python3 -m scripts.ai.notion_embeddings_pipeline --stats`
- Semantic search: `./venv/bin/python3 -m scripts.ai.notion_embeddings_pipeline --search "your query"`
- Sync export + incremental index: `./venv/bin/python3 scripts/ai/rag_auto_sync.py --json`
