#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Provide env vars (NOTION_TOKEN, etc.) to both Python and any subprocesses.
if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

exec "$ROOT/venv/bin/python3" "$ROOT/scripts/mcp/coin_rag_mcp_server.py"
