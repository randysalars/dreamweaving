#!/usr/bin/env python3
"""
Smoke-test an MCP stdio server by performing:
  initialize -> tools/list

This uses newline-delimited JSON-RPC, matching common MCP server implementations.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from typing import Any, Dict, Optional, Tuple


def _recv(proc: subprocess.Popen, timeout_s: float) -> Optional[Dict[str, Any]]:
    if proc.stdout is None:
        return None
    end = time.time() + timeout_s
    while time.time() < end:
        line = proc.stdout.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line.decode("utf-8"))
        except Exception:
            # ignore non-json lines
            continue
    return None


def _send(proc: subprocess.Popen, msg: Dict[str, Any]) -> None:
    line = (json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8")
    proc.stdin.write(line)  # type: ignore[union-attr]
    proc.stdin.flush()  # type: ignore[union-attr]


def _run(command: str, timeout_s: float) -> Tuple[bool, str]:
    # SECURITY NOTE: shell=True used here for testing utility.
    # Command comes from hardcoded config, not user input.
    # Safe in this context but do not use for production code.
    proc = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        _send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "dreamweaving-smoke", "version": "0"},
                },
            },
        )
        init = _recv(proc, timeout_s)
        if not init or "result" not in init:
            return False, "initialize: no response (server may not be stdio MCP, or is still starting)"

        _send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

        _send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools = _recv(proc, timeout_s)
        if not tools or "result" not in tools or "tools" not in tools["result"]:
            return False, "tools/list: no response"

        tool_names = [t.get("name") for t in tools["result"]["tools"] if isinstance(t, dict)]
        return True, f"ok: {len(tool_names)} tools: {', '.join([n for n in tool_names if n])}"
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test an MCP stdio server")
    parser.add_argument(
        "server",
        choices=["dreamweaving-rag", "chrome-devtools", "notion"],
        help="Which repo-configured MCP server to smoke-test",
    )
    parser.add_argument("--timeout", type=float, default=20.0, help="Per-step timeout seconds")
    args = parser.parse_args()

    if args.server == "dreamweaving-rag":
        cmd = "bash scripts/mcp/run_dreamweaving_rag_mcp_server.sh"
    elif args.server == "chrome-devtools":
        cmd = "bash scripts/mcp/run_chrome_devtools_mcp_server.sh"
    else:
        cmd = "bash scripts/mcp/run_notion_mcp_server.sh"

    ok, msg = _run(cmd, timeout_s=args.timeout)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
