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
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# =============================================================================
# PRICING CONFIG LOADER
# =============================================================================

def _load_pricing_config() -> Dict[str, Any]:
    """Load pricing configuration from YAML file."""
    config_path = PROJECT_ROOT / 'config' / 'coin_pricing.yaml'
    if config_path.exists():
        try:
            return yaml.safe_load(config_path.read_text())
        except Exception as e:
            _log(f"Warning: Failed to load pricing config: {e}")
    # Return defaults if config doesn't exist
    return {
        'defaults': {
            'junk_silver_multiplier': 20,
            'morgan_premium_usd': 8.00,
            'peace_premium_usd': 7.00,
        },
        'market_conditions': {
            'multiplier_floor': 18,
            'multiplier_ceiling': 24,
        }
    }


def _save_pricing_config(config: Dict[str, Any]) -> bool:
    """Save pricing configuration to YAML file."""
    config_path = PROJECT_ROOT / 'config' / 'coin_pricing.yaml'
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))
        return True
    except Exception as e:
        _log(f"Error saving pricing config: {e}")
        return False


# Global config - loaded at startup, can be modified at runtime
PRICING_CONFIG = _load_pricing_config()


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
    "doubled die", "overdate", "repunched", "collecting", "stacking",
    # Extended keywords for supplies and stamps
    "stamp", "philatelic", "tongs", "mounts", "hinges", "album",
    "capsule", "flip", "tube", "magnifier", "scale", "starter kit",
    "supplies", "storage", "libertad", "peso", "mexican", "prepper",
    "preparedness", "bundle", "stack", "velocity", "catalog"
]

# =============================================================================
# HARDCODED KEY DATE KNOWLEDGE (for instant classification)
# =============================================================================
MORGAN_KEY_DATES = {
    "absolute_key": [
        "1893-S", "1895", "1895-O", "1895-S"
    ],
    "semi_key": [
        "1878-CC", "1879-CC", "1880-CC", "1881-CC", "1885-CC", "1889-CC",
        "1890-CC", "1891-CC", "1892-CC", "1893-CC", "1892-S", "1893-O",
        "1894", "1896-S", "1897-S", "1898-S", "1899-S", "1901-S",
        "1902-S", "1903-S"
    ],
    "safe_bullion_p": [
        "1879", "1880", "1881", "1882", "1883", "1884", "1885", "1886",
        "1887", "1888", "1889", "1890", "1891", "1896", "1897", "1898",
        "1899", "1900", "1901", "1902", "1903", "1904"
    ],
    "safe_bullion_o": [
        "1879-O", "1880-O", "1881-O", "1882-O", "1883-O", "1884-O",
        "1885-O", "1886-O", "1887-O", "1888-O", "1889-O", "1890-O",
        "1891-O", "1896-O", "1897-O", "1898-O"
    ],
    "safe_bullion_s": [
        "1881-S", "1882-S", "1883-S", "1884-S"  # Only if heavily circulated
    ]
}

PEACE_KEY_DATES = {
    "absolute_key": [
        "1921", "1927-D", "1928", "1934-S", "1935-S"
    ],
    "semi_key": [
        "1924-S", "1925-S", "1926-S", "1927-S"
    ],
    "safe_bullion": [
        "1922", "1922-D", "1922-S", "1923", "1923-D", "1923-S",
        "1924", "1925", "1926", "1926-D", "1927"
    ]
}

# Junk silver face value to silver oz conversion
JUNK_SILVER_MATH = {
    "oz_per_dollar_fv": 0.715,
    "dime_oz": 0.0715,
    "quarter_oz": 0.17875,
    "half_oz": 0.3575,
}

# Product bundles for recommendations
BUNDLES = {
    "starter_silver_stack": {
        "name": "Starter Silver Stack",
        "contents": ["1 Morgan Dollar", "$5 FV 90% Silver"],
        "target": "first-time buyers"
    },
    "preparedness_stack": {
        "name": "Preparedness Stack",
        "contents": ["2 Peace Dollars", "$10 FV 90% Silver"],
        "target": "preppers"
    },
    "sound_money_bundle": {
        "name": "Sound Money Bundle",
        "contents": ["1 Morgan Dollar", "1 Peace Dollar", "1 Mexican Silver"],
        "target": "long-term thinkers"
    },
    "junk_silver_roll_pack": {
        "name": "Junk Silver Roll Pack",
        "contents": ["$20 FV Mixed 90% Silver"],
        "target": "serious stackers"
    }
}


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


def _tool_bullion_sort(args: Dict[str, Any]) -> Dict[str, Any]:
    """Classify a coin as bullion-grade or numismatic based on date/mint/condition."""
    coin_type = (args.get("coin_type") or "").strip().lower()
    year = args.get("year")
    mintmark = (args.get("mintmark") or "").strip().upper()
    condition = (args.get("condition") or "").strip().lower()

    if not coin_type or not year:
        raise JsonRpcError(-32602, "Missing required arguments: coin_type and year")

    # Build date string for lookup
    date_str = str(year)
    if mintmark and mintmark != "P":
        date_str = f"{year}-{mintmark}"

    result = {
        "coin_type": coin_type,
        "year": year,
        "mintmark": mintmark or "P",
        "date_string": date_str,
        "classification": "unknown",
        "reason": "",
        "action": "",
        "warnings": []
    }

    # Check Morgan dollars
    if "morgan" in coin_type:
        if date_str in MORGAN_KEY_DATES["absolute_key"] or str(year) in MORGAN_KEY_DATES["absolute_key"]:
            result["classification"] = "absolute_key"
            result["reason"] = "This is an absolute key date - never sell as bullion"
            result["action"] = "STOP - set aside for numismatic evaluation"
        elif date_str in MORGAN_KEY_DATES["semi_key"]:
            result["classification"] = "semi_key"
            result["reason"] = "This is a semi-key date with collector premium"
            result["action"] = "STOP - evaluate for numismatic value"
        elif "cc" in mintmark.lower() or "carson" in mintmark.lower():
            result["classification"] = "semi_key"
            result["reason"] = "All Carson City (CC) Morgans carry premiums"
            result["action"] = "STOP - CC coins are never bullion"
        elif str(year) in MORGAN_KEY_DATES["safe_bullion_p"] and (not mintmark or mintmark == "P"):
            result["classification"] = "bullion_grade"
            result["reason"] = "Common Philadelphia date, safe for bullion sale when circulated"
            result["action"] = "Safe to sell as bullion if circulated (VF or lower)"
        elif date_str in MORGAN_KEY_DATES["safe_bullion_o"]:
            result["classification"] = "bullion_grade"
            result["reason"] = "Common New Orleans date, safe for bullion when worn"
            result["action"] = "Safe to sell as bullion if circulated"
        elif date_str in MORGAN_KEY_DATES["safe_bullion_s"]:
            result["classification"] = "bullion_grade"
            result["reason"] = "S-mint safe only if HEAVILY circulated"
            result["action"] = "Check condition carefully - if lustrous, pull for evaluation"
            result["warnings"].append("S-mint Morgans often carry premiums in higher grades")
        else:
            result["classification"] = "needs_evaluation"
            result["reason"] = "Date/mint combination not in known safe list"
            result["action"] = "Research this specific date before selling"

    # Check Peace dollars
    elif "peace" in coin_type:
        if date_str in PEACE_KEY_DATES["absolute_key"] or str(year) in PEACE_KEY_DATES["absolute_key"]:
            result["classification"] = "absolute_key"
            result["reason"] = "This is a key date Peace dollar - never sell as bullion"
            result["action"] = "STOP - set aside for numismatic evaluation"
        elif date_str in PEACE_KEY_DATES["semi_key"]:
            result["classification"] = "semi_key"
            result["reason"] = "This is a semi-key Peace dollar"
            result["action"] = "STOP - evaluate for collector value"
        elif date_str in PEACE_KEY_DATES["safe_bullion"] or str(year) in ["1922", "1923", "1924", "1925", "1926"]:
            result["classification"] = "bullion_grade"
            result["reason"] = "Common date Peace dollar, safe for bullion sale"
            result["action"] = "Safe to sell as bullion if circulated"
        else:
            result["classification"] = "needs_evaluation"
            result["reason"] = "Date not in known safe list"
            result["action"] = "Research before selling"

    # Generic bullion items
    elif any(x in coin_type for x in ["round", "bar", "eagle", "maple", "libertad"]):
        result["classification"] = "bullion"
        result["reason"] = "Modern bullion product"
        result["action"] = "Sell as bullion - price by silver content + small premium"

    # Junk silver
    elif any(x in coin_type for x in ["junk", "90%", "dime", "quarter", "half"]):
        result["classification"] = "junk_silver"
        result["reason"] = "U.S. 90% silver - valued by face value"
        result["action"] = "Sell by face value using multiplier"

    # Condition warnings
    if condition:
        if any(x in condition for x in ["bu", "unc", "ms", "proof", "au", "lustrous", "nice"]):
            result["warnings"].append("High grade/lustrous coins may have numismatic value even for common dates")
        if "cleaned" in condition:
            result["warnings"].append("Cleaning destroys numismatic value - may be bullion only now")

    return result


def _tool_junk_silver_calculator(args: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate silver content and pricing for junk silver by face value.

    Now auto-fetches spot price if not provided and uses config multiplier.
    """
    face_value = args.get("face_value")
    spot_price = args.get("spot_price")
    multiplier = args.get("multiplier")

    if face_value is None:
        raise JsonRpcError(-32602, "Missing required argument: face_value")

    fv = float(face_value)
    silver_oz = fv * JUNK_SILVER_MATH["oz_per_dollar_fv"]

    result = {
        "face_value": fv,
        "silver_content_oz": round(silver_oz, 3),
        "silver_math": f"${fv} FV × 0.715 oz/$ = {round(silver_oz, 3)} oz"
    }

    # Auto-fetch spot price if not provided
    spot_source = None
    spot_cached = False
    spot_age_minutes = None

    if spot_price is None:
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from scripts.utilities.spot_price_fetcher import get_spot_prices
            prices = get_spot_prices()
            if prices.get('silver'):
                spot_price = prices['silver']
                spot_source = prices.get('source', 'fetched')
                spot_cached = prices.get('cached', False)
                spot_age_minutes = prices.get('cache_age_minutes')
        except Exception as e:
            _log(f"Warning: Could not auto-fetch spot price: {e}")

    # Use config multiplier if not provided
    if multiplier is None:
        multiplier = PRICING_CONFIG.get('defaults', {}).get('junk_silver_multiplier', 20)

    if spot_price:
        spot = float(spot_price)
        melt_value = silver_oz * spot
        result["spot_price"] = spot
        result["melt_value"] = round(melt_value, 2)

        # Include spot source info if auto-fetched
        if spot_source:
            result["spot_source"] = spot_source
            result["spot_cached"] = spot_cached
            if spot_age_minutes is not None:
                result["spot_age_minutes"] = spot_age_minutes

        mult = float(multiplier)
        result["multiplier"] = mult
        result["suggested_price"] = round(fv * mult, 2)
        result["premium_over_melt"] = round((fv * mult) - melt_value, 2)
    else:
        result["note"] = "Spot price not available. Provide spot_price for full calculation."

    return result


def _tool_listing_generator(args: Dict[str, Any]) -> Dict[str, Any]:
    """Generate product listing copy for coins/silver."""
    product_type = (args.get("product_type") or "").strip().lower()

    if not product_type:
        raise JsonRpcError(-32602, "Missing required argument: product_type")

    listings = {
        "morgan_bullion": {
            "title": "Circulated Morgan Silver Dollar — Bullion Grade",
            "description": "A genuine U.S. Morgan silver dollar in circulated condition. Dates and mint marks vary. These are bullion-grade coins, valued for silver content and recognizability—not collector hype.",
            "why_buy": ["Instantly recognizable", "Tangible, historic silver", "Easy to understand and trade"],
            "notes": "Circulated condition. No cherry-picking. Priced transparently relative to silver content.",
            "never_say": ["AU", "XF", "BU", "Choice", "Rare"]
        },
        "peace_bullion": {
            "title": "Circulated Peace Silver Dollar — Honest, Heavy Silver",
            "description": "Original U.S. Peace silver dollar, circulated condition. These coins represent real, substantial silver from the last era of circulating U.S. silver dollars.",
            "why_buy": ["Slightly higher silver content feel than junk", "Less hype, more substance", "Excellent bridge between bullion and junk silver"],
            "notes": "Sold as bullion-grade. Dates vary. Calm pricing. No drama."
        },
        "junk_dimes": {
            "title": "90% U.S. Silver Dimes — $5 Face Value",
            "description": "Five dollars face value of genuine U.S. 90% silver dimes (Mercury and/or Roosevelt). Circulated condition.",
            "why_buy": ["Most practical fractional silver", "Easy to count, store, and trade", "Prepper-preferred denomination"],
            "notes": "Sold strictly by face value. No cherry-picking. Honest mix."
        },
        "junk_quarters": {
            "title": "90% U.S. Silver Quarters — $10 Face Value",
            "description": "Ten dollars face value of U.S. 90% silver quarters (Washington and/or Standing Liberty). Circulated condition.",
            "why_buy": ["Fewer coins than dimes", "Still divisible", "Familiar to nearly everyone"],
            "notes": "Priced by face value × market multiplier. Straightforward and transparent."
        },
        "starter_stack": {
            "title": "Starter Silver Stack — Simple, Real, Understandable",
            "description": "A balanced entry into physical silver: one large, recognizable silver dollar plus fractional 90% U.S. silver.",
            "contents": ["1 Morgan Dollar", "$5 FV 90% Silver"],
            "why_buy": ["Big silver + small silver", "Easy to grasp", "Gift-friendly", "No overthinking required"],
            "notes": "Ideal for first-time buyers or anyone starting a tangible silver position."
        },
        "preparedness_stack": {
            "title": "Preparedness Silver Stack — Flexibility Over Flash",
            "description": "Designed for people who think in scenarios, not speculation.",
            "contents": ["2 Peace Dollars", "$10 FV 90% Silver"],
            "why_buy": ["Substantial silver weight", "Fractional usability", "Recognizability across experience levels"],
            "notes": "A calm, practical way to hold silver without overexposure."
        }
    }

    # Find matching listing
    for key, listing in listings.items():
        if key in product_type or product_type in key:
            return {"product_type": product_type, "listing": listing}

    # Default template
    return {
        "product_type": product_type,
        "listing": {
            "title": "[Product Type] — Clear, Honest Description",
            "description": "Write a clear, no-hype description focused on what the buyer gets.",
            "template_rules": [
                "No hype language",
                "Clear condition statement",
                "Priced transparently",
                "Photos of exact item"
            ],
            "trust_signals": [
                "All silver verified by weight & dimensions",
                "Photos show the exact item",
                "Authenticity guaranteed or full refund",
                "Ships within 24-48 hours"
            ]
        }
    }


def _tool_bundle_recommendation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Recommend bundles based on available inventory."""
    inventory = args.get("inventory", {})

    # Parse inventory
    has_morgan = inventory.get("morgan_dollars", 0) > 0
    has_peace = inventory.get("peace_dollars", 0) > 0
    has_mexican = inventory.get("mexican_silver", 0) > 0
    junk_fv = inventory.get("junk_silver_fv", 0)

    recommendations = []

    # Starter Stack: 1 Morgan + $5 FV
    if has_morgan and junk_fv >= 5:
        recommendations.append({
            "bundle": "starter_silver_stack",
            "name": "Starter Silver Stack",
            "can_make": min(inventory.get("morgan_dollars", 0), int(junk_fv / 5)),
            "target_buyer": "First-time buyers, gift market"
        })

    # Preparedness Stack: 2 Peace + $10 FV
    if inventory.get("peace_dollars", 0) >= 2 and junk_fv >= 10:
        recommendations.append({
            "bundle": "preparedness_stack",
            "name": "Preparedness Stack",
            "can_make": min(inventory.get("peace_dollars", 0) // 2, int(junk_fv / 10)),
            "target_buyer": "Preppers, scenario thinkers"
        })

    # Sound Money Bundle: 1 Morgan + 1 Peace + Mexican
    if has_morgan and has_peace and has_mexican:
        recommendations.append({
            "bundle": "sound_money_bundle",
            "name": "Sound Money Bundle",
            "can_make": min(
                inventory.get("morgan_dollars", 0),
                inventory.get("peace_dollars", 0),
                inventory.get("mexican_silver", 0)
            ),
            "target_buyer": "Long-term holders, diversification"
        })

    # Junk Silver Roll Pack: $20 FV
    if junk_fv >= 20:
        recommendations.append({
            "bundle": "junk_silver_roll_pack",
            "name": "Junk Silver Roll Pack",
            "can_make": int(junk_fv / 20),
            "target_buyer": "Serious stackers, repeat buyers"
        })

    return {
        "inventory_received": inventory,
        "recommendations": recommendations,
        "total_bundle_types": len(recommendations)
    }


def _tool_get_spot_price(args: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch current silver and gold spot prices."""
    force_refresh = args.get("force_refresh", False)

    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.utilities.spot_price_fetcher import get_spot_prices
        return get_spot_prices(force_refresh=force_refresh)
    except ImportError as e:
        raise JsonRpcError(-32000, f"Spot price fetcher not available: {e}")
    except Exception as e:
        raise JsonRpcError(-32000, f"Failed to fetch spot prices: {e}")


def _tool_update_multiplier(args: Dict[str, Any]) -> Dict[str, Any]:
    """Update the junk silver multiplier (persisted to config and database)."""
    global PRICING_CONFIG

    new_multiplier = args.get("multiplier")
    reason = args.get("reason", "Manual adjustment")

    if new_multiplier is None:
        raise JsonRpcError(-32602, "Missing required argument: multiplier")

    new_multiplier = float(new_multiplier)

    # Validate bounds
    floor = PRICING_CONFIG.get('market_conditions', {}).get('multiplier_floor', 18)
    ceiling = PRICING_CONFIG.get('market_conditions', {}).get('multiplier_ceiling', 24)

    if not (floor <= new_multiplier <= ceiling):
        raise JsonRpcError(
            -32602,
            f"Multiplier must be between {floor} and {ceiling}. Got: {new_multiplier}"
        )

    old_multiplier = PRICING_CONFIG.get('defaults', {}).get('junk_silver_multiplier', 20)

    # Update in-memory config
    if 'defaults' not in PRICING_CONFIG:
        PRICING_CONFIG['defaults'] = {}
    PRICING_CONFIG['defaults']['junk_silver_multiplier'] = new_multiplier

    # Save to config file
    if not _save_pricing_config(PRICING_CONFIG):
        raise JsonRpcError(-32000, "Failed to save config file")

    # Log to database
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.automation.state_db import StateDatabase
        db = StateDatabase()
        db.init_schema()  # Ensure tables exist
        db.save_multiplier(new_multiplier, reason)
        db.close()
    except Exception as e:
        _log(f"Warning: Could not log multiplier to database: {e}")

    return {
        "success": True,
        "old_multiplier": old_multiplier,
        "new_multiplier": new_multiplier,
        "reason": reason,
        "config_saved": True
    }


def _tool_get_pricing_config(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get current pricing configuration."""
    # Reload config to ensure we have latest
    config = _load_pricing_config()

    # Also get current multiplier from database if available
    db_multiplier = None
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.automation.state_db import StateDatabase
        db = StateDatabase()
        db_multiplier = db.get_current_multiplier()
        db.close()
    except Exception:
        pass

    result = {
        "config": config,
        "current_multiplier": config.get('defaults', {}).get('junk_silver_multiplier', 20),
    }

    if db_multiplier is not None:
        result["db_multiplier"] = db_multiplier

    return result


def _tool_get_multiplier_history(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get history of multiplier changes."""
    limit = int(args.get("limit", 20))

    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.automation.state_db import StateDatabase
        db = StateDatabase()
        db.init_schema()
        history = db.get_multiplier_history(limit=limit)
        db.close()
        return {"history": history, "count": len(history)}
    except Exception as e:
        raise JsonRpcError(-32000, f"Failed to get multiplier history: {e}")


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
    "coin_bullion_sort": (
        "Classify a coin as bullion-grade or numismatic based on date, mintmark, and condition. Returns classification, reason, and action.",
        _tool_bullion_sort,
    ),
    "coin_junk_silver_calc": (
        "Calculate silver content and pricing for junk silver by face value. Auto-fetches spot price if not provided. Uses config multiplier by default.",
        _tool_junk_silver_calculator,
    ),
    "coin_listing_generator": (
        "Generate product listing copy for coins/silver products (titles, descriptions, trust signals).",
        _tool_listing_generator,
    ),
    "coin_bundle_recommendation": (
        "Recommend product bundles based on available inventory (Morgan/Peace dollars, junk silver, Mexican silver).",
        _tool_bundle_recommendation,
    ),
    "coin_get_spot_price": (
        "Fetch current silver and gold spot prices from web sources (APMEX, JM Bullion, Kitco). Cached for 15 minutes.",
        _tool_get_spot_price,
    ),
    "coin_update_multiplier": (
        "Update the junk silver multiplier used for pricing. Persists to config file and logs to database.",
        _tool_update_multiplier,
    ),
    "coin_get_pricing_config": (
        "Get current pricing configuration including multiplier, premiums, and market condition bounds.",
        _tool_get_pricing_config,
    ),
    "coin_get_multiplier_history": (
        "Get history of multiplier changes with timestamps and reasons.",
        _tool_get_multiplier_history,
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
            {
                "name": "coin_bullion_sort",
                "description": TOOLS["coin_bullion_sort"][0],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "coin_type": {
                            "type": "string",
                            "description": "Type of coin (e.g., 'morgan dollar', 'peace dollar', 'silver eagle')"
                        },
                        "year": {
                            "type": "integer",
                            "description": "Year of the coin"
                        },
                        "mintmark": {
                            "type": "string",
                            "description": "Mintmark (S, D, O, CC, or empty for Philadelphia)"
                        },
                        "condition": {
                            "type": "string",
                            "description": "Condition notes (e.g., 'circulated', 'lustrous', 'AU', 'cleaned')"
                        },
                    },
                    "required": ["coin_type", "year"],
                },
            },
            {
                "name": "coin_junk_silver_calc",
                "description": TOOLS["coin_junk_silver_calc"][0],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "face_value": {
                            "type": "number",
                            "description": "Face value in dollars (e.g., 10 for $10 FV)"
                        },
                        "spot_price": {
                            "type": "number",
                            "description": "Silver spot price per oz (optional - auto-fetched if not provided)"
                        },
                        "multiplier": {
                            "type": "number",
                            "description": "Market multiplier for pricing (optional - uses config value if not provided)"
                        },
                    },
                    "required": ["face_value"],
                },
            },
            {
                "name": "coin_listing_generator",
                "description": TOOLS["coin_listing_generator"][0],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "product_type": {
                            "type": "string",
                            "description": "Product type (e.g., 'morgan_bullion', 'junk_dimes', 'starter_stack')"
                        },
                    },
                    "required": ["product_type"],
                },
            },
            {
                "name": "coin_bundle_recommendation",
                "description": TOOLS["coin_bundle_recommendation"][0],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "inventory": {
                            "type": "object",
                            "description": "Inventory counts: {morgan_dollars, peace_dollars, junk_silver_fv, mexican_silver}",
                            "properties": {
                                "morgan_dollars": {"type": "integer"},
                                "peace_dollars": {"type": "integer"},
                                "junk_silver_fv": {"type": "number"},
                                "mexican_silver": {"type": "integer"},
                            }
                        },
                    },
                    "required": ["inventory"],
                },
            },
            {
                "name": "coin_get_spot_price",
                "description": TOOLS["coin_get_spot_price"][0],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "force_refresh": {
                            "type": "boolean",
                            "default": False,
                            "description": "Force fresh fetch, bypassing cache"
                        },
                    },
                },
            },
            {
                "name": "coin_update_multiplier",
                "description": TOOLS["coin_update_multiplier"][0],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "multiplier": {
                            "type": "number",
                            "description": "New multiplier value (must be between floor and ceiling from config)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for the change (for audit trail)"
                        },
                    },
                    "required": ["multiplier"],
                },
            },
            {
                "name": "coin_get_pricing_config",
                "description": TOOLS["coin_get_pricing_config"][0],
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "coin_get_multiplier_history",
                "description": TOOLS["coin_get_multiplier_history"][0],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "default": 20,
                            "description": "Maximum number of records to return"
                        },
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
