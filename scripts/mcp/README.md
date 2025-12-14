# MCP Servers (Dreamweaving)

This directory contains MCP servers/wrappers intended for IDE agents (including Codex).

- `dreamweaving_rag_mcp_server.py`: MCP server exposing local semantic search + sync.
- `run_dreamweaving_rag_mcp_server.sh`: wrapper that loads `./.env` and runs the server with `./venv/bin/python3`.
- `run_notion_mcp_server.sh`: wrapper that loads `./.env` and starts the official Notion MCP server via `npx`.
- `run_chrome_devtools_mcp_server.sh`: wrapper that loads `./.env` and starts the Chrome DevTools MCP server via `npx`.

Workspace config:
- `mcp.json` (repo root)
