#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Keep behavior consistent with other MCP wrappers.
if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

# Optional (recommended): keep DevTools MCP pinning/config out of `.env` (which usually contains secrets).
if [[ -f "$ROOT/config/devtools_mcp.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/config/devtools_mcp.env"
  set +a
fi

# Chrome DevTools MCP server (via npx).
# Pin with: CHROME_DEVTOOLS_MCP_VERSION=0.?.? (default: latest)
# Extra args: CHROME_DEVTOOLS_MCP_ARGS="--headless --isolated --viewport 1280x720" (example)
VERSION="${CHROME_DEVTOOLS_MCP_VERSION:-latest}"
ARGS="${CHROME_DEVTOOLS_MCP_ARGS:-}"

exec npx -y "chrome-devtools-mcp@${VERSION}" ${ARGS}
