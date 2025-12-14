#!/usr/bin/env python3
"""
Dreamweaving RAG MCP server (stdio).

Exposes the local Notion-export + Qdrant vector index as MCP tools, so IDE agents
(e.g., Codex VS Code extension) can do semantic retrieval and trigger re-syncs.
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _try_load_dotenv() -> None:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        return
    load_dotenv(env_path)


_try_load_dotenv()


def _log(msg: str) -> None:
    sys.stderr.write(msg.rstrip() + "\n")
    sys.stderr.flush()

def _read_message(stream) -> Optional[Dict[str, Any]]:
    """
    Read one newline-delimited JSON-RPC message (the stdio transport used by
    common MCP servers like notion-mcp-server and chrome-devtools-mcp).
    """
    line = stream.readline()
    if not line:
        return None
    line = line.strip()
    if not line:
        return None
    return json.loads(line.decode("utf-8"))


def _write_message(payload: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


@dataclass
class JsonRpcError(Exception):
    code: int
    message: str
    data: Optional[Any] = None


def _rpc_error(err: JsonRpcError) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"code": err.code, "message": err.message}
    if err.data is not None:
        payload["data"] = err.data
    return payload


_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        # Lazy import to keep MCP server startup fast.
        from scripts.ai.notion_embeddings_pipeline import NotionEmbeddingsPipeline

        _pipeline = NotionEmbeddingsPipeline()
    return _pipeline


def _tool_rag_search(args: Dict[str, Any]) -> Dict[str, Any]:
    query = (args.get("query") or "").strip()
    if not query:
        raise JsonRpcError(-32602, "Missing required argument: query")

    limit = int(args.get("limit", 5))
    content_type = args.get("content_type")
    score_threshold = float(args.get("score_threshold", 0.0))

    results = _get_pipeline().search(
        query=query,
        limit=limit,
        content_type=content_type,
        score_threshold=score_threshold,
    )
    return {"results": results}


def _tool_rag_stats(_args: Dict[str, Any]) -> Dict[str, Any]:
    return _get_pipeline().get_stats()


def _tool_rag_sync(args: Dict[str, Any]) -> Dict[str, Any]:
    force = bool(args.get("force", False))
    full_reindex = bool(args.get("full_reindex", False))

    # Lazy import: this loads Notion client + may do network calls.
    from scripts.ai.rag_auto_sync import RAGAutoSync

    syncer = RAGAutoSync()
    return syncer.sync(force=force, full_reindex=full_reindex)


TOOLS: Dict[str, Tuple[str, Any]] = {
    "dreamweaving_rag_search": (
        "Semantic search over the local Dreamweaving Notion RAG index (Qdrant).",
        _tool_rag_search,
    ),
    "dreamweaving_rag_stats": (
        "Get stats for the local Dreamweaving Notion RAG index (Qdrant).",
        _tool_rag_stats,
    ),
    "dreamweaving_rag_sync": (
        "Export Notion → update local RAG index (incremental by default).",
        _tool_rag_sync,
    ),
}


def _tools_list() -> Dict[str, Any]:
    return {
        "tools": [
            {
                "name": "dreamweaving_rag_search",
                "description": TOOLS["dreamweaving_rag_search"][0],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 5},
                        "content_type": {
                            "type": ["string", "null"],
                            "description": "Optional filter, e.g. 'page' or 'database_entry'.",
                        },
                        "score_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.0},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "dreamweaving_rag_stats",
                "description": TOOLS["dreamweaving_rag_stats"][0],
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "dreamweaving_rag_sync",
                "description": TOOLS["dreamweaving_rag_sync"][0],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "force": {"type": "boolean", "default": False},
                        "full_reindex": {"type": "boolean", "default": False},
                    },
                },
            },
        ]
    }


def _tools_call(params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get("name")
    arguments = params.get("arguments") or {}
    if name not in TOOLS:
        raise JsonRpcError(-32601, f"Unknown tool: {name}")

    try:
        result = TOOLS[name][1](arguments)
    except JsonRpcError:
        raise
    except Exception as e:
        raise JsonRpcError(
            -32000,
            f"Tool '{name}' failed: {e}",
            data={"traceback": traceback.format_exc()},
        )

    # MCP tool call result: return content blocks. Most clients accept text blocks.
    return {
        "content": [
            {"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}
        ]
    }


def _handle_request(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = req.get("method")
    rpc_id = req.get("id")
    params = req.get("params") or {}

    # Notifications (no id) should not get a response.
    is_notification = rpc_id is None

    if method == "initialize":
        result = {
            "protocolVersion": params.get("protocolVersion", "2024-11-05"),
            "serverInfo": {"name": "dreamweaving-rag", "version": "0.1.0"},
            "capabilities": {"tools": {"list": True, "call": True}},
        }
        return None if is_notification else {"jsonrpc": "2.0", "id": rpc_id, "result": result}

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return None if is_notification else {"jsonrpc": "2.0", "id": rpc_id, "result": _tools_list()}

    if method == "tools/call":
        return None if is_notification else {"jsonrpc": "2.0", "id": rpc_id, "result": _tools_call(params)}

    if is_notification:
        return None

    raise JsonRpcError(-32601, f"Method not found: {method}")


def main() -> int:
    # Ensure relative imports work even when launched from outside repo root.
    os.chdir(PROJECT_ROOT)
    sys.path.insert(0, str(PROJECT_ROOT))

    stdin = sys.stdin.buffer

    while True:
        try:
            req = _read_message(stdin)
            if req is None:
                return 0

            try:
                resp = _handle_request(req)
            except JsonRpcError as e:
                if req.get("id") is None:
                    resp = None
                else:
                    resp = {"jsonrpc": "2.0", "id": req.get("id"), "error": _rpc_error(e)}

            if resp is not None:
                _write_message(resp)
        except KeyboardInterrupt:
            return 0
        except Exception as e:
            _log(f"Fatal MCP server error: {e}\n{traceback.format_exc()}")
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
