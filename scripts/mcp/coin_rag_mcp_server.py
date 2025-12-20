#!/usr/bin/env python3
"""
Coin Database RAG MCP Server (stdio).

A specialized MCP server for querying the rare coin knowledge base, providing
semantic search specifically for coin-related content (bullion, numismatics,
key dates, pricing, grading, etc.)

This is a focused subset of the dreamweaving-rag for coin-specific queries.
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
        from dotenv import load_dotenv
    except Exception:
        return
    load_dotenv(env_path)


_try_load_dotenv()


def _log(msg: str) -> None:
    sys.stderr.write(msg.rstrip() + "\n")
    sys.stderr.flush()


def _read_message(stream) -> Optional[Dict[str, Any]]:
    """Read one newline-delimited JSON-RPC message."""
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

# Coin-related keywords for filtering results
COIN_KEYWORDS = [
    "coin", "silver", "gold", "bullion", "numismatic", "morgan", "peace",
    "dollar", "dime", "quarter", "half", "cent", "penny", "nickel",
    "mint", "mintmark", "grading", "pcgs", "ngc", "junk", "melt",
    "spot", "premium", "key date", "semi-key", "circulated", "uncirculated",
    "proof", "ms", "au", "xf", "vf", "fine", "good", "cull",
    "commemorative", "eagle", "maple", "britannia", "philharmonic",
    "mercury", "walking liberty", "franklin", "kennedy", "washington",
    "standing liberty", "barber", "seated liberty", "trade dollar",
    "round", "bar", "oz", "troy", "face value", "fv", "90%", "40%",
    "1893-s", "1916-d", "cc", "carson city", "error", "variety", "vam",
    "doubled die", "overdate", "repunched", "collecting", "stacking"
]


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        from scripts.ai.notion_embeddings_pipeline import NotionEmbeddingsPipeline
        _pipeline = NotionEmbeddingsPipeline(quiet=True)
    return _pipeline


def _is_coin_related(text: str) -> bool:
    """Check if text is related to coins/precious metals."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in COIN_KEYWORDS)


def _tool_coin_search(args: Dict[str, Any]) -> Dict[str, Any]:
    """Search for coin-related information in the knowledge base."""
    query = (args.get("query") or "").strip()
    if not query:
        raise JsonRpcError(-32602, "Missing required argument: query")

    limit = int(args.get("limit", 10))
    score_threshold = float(args.get("score_threshold", 0.4))
    
    # Search with higher limit to filter for coin content
    raw_results = _get_pipeline().search(
        query=query,
        limit=limit * 3,  # Get extra to filter
        score_threshold=score_threshold,
    )
    
    # Filter for coin-related content
    coin_results = []
    for r in raw_results:
        title = r.get("title", "").lower()
        text = r.get("text", "").lower()
        
        # Check if coin-related
        if _is_coin_related(title) or _is_coin_related(text):
            coin_results.append(r)
            if len(coin_results) >= limit:
                break
    
    return {"results": coin_results, "total_found": len(coin_results)}


def _tool_key_date_check(args: Dict[str, Any]) -> Dict[str, Any]:
    """Check if a coin date/mintmark is a key or semi-key date."""
    coin_type = (args.get("coin_type") or "").strip().lower()
    year = args.get("year")
    mintmark = (args.get("mintmark") or "").strip().upper()
    
    if not coin_type or not year:
        raise JsonRpcError(-32602, "Missing required arguments: coin_type and year")
    
    # Build search query
    query = f"{coin_type} {year} {mintmark} key date semi-key value"
    
    results = _get_pipeline().search(
        query=query,
        limit=5,
        score_threshold=0.4,
    )
    
    # Look for key date mentions
    is_key_date = False
    is_semi_key = False
    notes = []
    
    for r in results:
        text = r.get("text", "").lower()
        search_str = f"{year}"
        if mintmark:
            search_str += f"-{mintmark.lower()}"
        
        if search_str in text:
            if "key date" in text or "never junk" in text or "never bullion" in text:
                is_key_date = True
            if "semi-key" in text or "semi key" in text:
                is_semi_key = True
            # Extract relevant snippet
            notes.append(r.get("text", "")[:500])
    
    return {
        "coin_type": coin_type,
        "year": year,
        "mintmark": mintmark or "P",
        "is_key_date": is_key_date,
        "is_semi_key": is_semi_key,
        "notes": notes[:3],
    }


def _tool_coin_pricing_guide(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get pricing guidance for a type of coin or silver."""
    item_type = (args.get("item_type") or "").strip()
    
    if not item_type:
        raise JsonRpcError(-32602, "Missing required argument: item_type")
    
    query = f"{item_type} pricing strategy premium spot multiplier value"
    
    results = _get_pipeline().search(
        query=query,
        limit=5,
        score_threshold=0.4,
    )
    
    return {
        "item_type": item_type,
        "pricing_info": [
            {"title": r.get("title", ""), "text": r.get("text", "")[:800], "score": r.get("score", 0)}
            for r in results
        ]
    }


def _tool_coin_stats(_args: Dict[str, Any]) -> Dict[str, Any]:
    """Get statistics about the coin knowledge base."""
    stats = _get_pipeline().get_stats()
    stats["specialized_for"] = "Coin & Precious Metals Knowledge"
    stats["keywords_tracked"] = len(COIN_KEYWORDS)
    return stats


TOOLS: Dict[str, Tuple[str, Any]] = {
    "coin_search": (
        "Semantic search over the rare coin knowledge base (Morgan/Peace dollars, junk silver, bullion, key dates, pricing, grading).",
        _tool_coin_search,
    ),
    "coin_key_date_check": (
        "Check if a specific coin date/mintmark is a key date or semi-key (e.g., 1893-S Morgan, 1916-D Mercury).",
        _tool_key_date_check,
    ),
    "coin_pricing_guide": (
        "Get pricing guidance for coins or silver (junk silver multipliers, bullion premiums, etc.).",
        _tool_coin_pricing_guide,
    ),
    "coin_rag_stats": (
        "Get statistics about the coin knowledge base index.",
        _tool_coin_stats,
    ),
}


def _tools_list() -> Dict[str, Any]:
    return {
        "tools": [
            {
                "name": "coin_search",
                "description": TOOLS["coin_search"][0],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query about coins, silver, pricing, etc."
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 20,
                            "default": 10,
                            "description": "Maximum results to return"
                        },
                        "score_threshold": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "default": 0.4,
                            "description": "Minimum relevance score (0-1)"
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "coin_key_date_check",
                "description": TOOLS["coin_key_date_check"][0],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "coin_type": {
                            "type": "string",
                            "description": "Type of coin (e.g., 'morgan dollar', 'mercury dime', 'washington quarter')"
                        },
                        "year": {
                            "type": "integer",
                            "description": "Year of the coin"
                        },
                        "mintmark": {
                            "type": "string",
                            "description": "Mintmark (S, D, O, CC, or empty for Philadelphia)"
                        },
                    },
                    "required": ["coin_type", "year"],
                },
            },
            {
                "name": "coin_pricing_guide",
                "description": TOOLS["coin_pricing_guide"][0],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "item_type": {
                            "type": "string",
                            "description": "Type of item (e.g., 'junk silver', 'bullion dollar', 'silver rounds', '90% dimes')"
                        },
                    },
                    "required": ["item_type"],
                },
            },
            {
                "name": "coin_rag_stats",
                "description": TOOLS["coin_rag_stats"][0],
                "inputSchema": {"type": "object", "properties": {}},
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

    return {
        "content": [
            {"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}
        ]
    }


def _handle_request(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = req.get("method")
    rpc_id = req.get("id")
    params = req.get("params") or {}

    is_notification = rpc_id is None

    if method == "initialize":
        result = {
            "protocolVersion": params.get("protocolVersion", "2024-11-05"),
            "serverInfo": {"name": "coin-rag", "version": "1.0.0"},
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
