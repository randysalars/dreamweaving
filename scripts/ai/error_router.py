#!/usr/bin/env python3
"""
Error Router - Routes errors to appropriate agents and suggests fixes.

Uses the error catalog (.claude/error_catalog.yaml) to match symptoms
to known errors and provide actionable guidance.

Usage:
    python3 scripts/ai/error_router.py "error message or symptom"
    python3 scripts/ai/error_router.py --list                    # List all known errors
    python3 scripts/ai/error_router.py --category audio          # List errors by category
    python3 scripts/ai/error_router.py --agent audio-engineer    # List errors by agent
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
ERROR_CATALOG_PATH = PROJECT_ROOT / ".claude" / "error_catalog.yaml"


def load_error_catalog() -> Dict[str, Any]:
    """Load the error catalog from YAML."""
    if not ERROR_CATALOG_PATH.exists():
        print(f"Error: Catalog not found at {ERROR_CATALOG_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(ERROR_CATALOG_PATH, "r") as f:
        return yaml.safe_load(f)


def tokenize(text: Any) -> set:
    """Convert text to lowercase tokens for matching."""
    # Handle non-string types
    if not isinstance(text, str):
        text = str(text)
    # Remove special characters, split on whitespace
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    return set(text.split())


def calculate_match_score(error_text: str, error_def: Dict[str, Any]) -> float:
    """
    Calculate a match score between error text and an error definition.

    Score is based on:
    - Keyword matches (highest weight)
    - Symptom matches (medium weight)
    - Partial matches (low weight)
    """
    error_tokens = tokenize(error_text)
    if not error_tokens:
        return 0.0

    score = 0.0

    # Keyword matches (weight: 3.0 each)
    keywords = error_def.get("keywords", [])
    for keyword in keywords:
        keyword_tokens = tokenize(keyword)
        if keyword_tokens & error_tokens:
            score += 3.0
        # Partial match bonus
        for token in keyword_tokens:
            if any(token in et or et in token for et in error_tokens):
                score += 0.5

    # Symptom matches (weight: 2.0 each)
    symptoms = error_def.get("symptoms", [])
    for symptom in symptoms:
        symptom_tokens = tokenize(symptom)
        overlap = symptom_tokens & error_tokens
        if overlap:
            # Score based on overlap percentage
            overlap_ratio = len(overlap) / max(len(symptom_tokens), 1)
            score += 2.0 * overlap_ratio

    # Normalize by number of error tokens
    normalized_score = score / max(len(error_tokens), 1)

    return min(normalized_score, 1.0)  # Cap at 1.0


def route_error(
    error_text: str,
    catalog: Optional[Dict[str, Any]] = None,
    min_confidence: float = 0.1
) -> Dict[str, Any]:
    """
    Route an error message to the appropriate handler.

    Args:
        error_text: The error message or symptom description
        catalog: Optional pre-loaded catalog
        min_confidence: Minimum confidence threshold (0.0-1.0)

    Returns:
        Dict with matched_error, confidence, agent, checks, fix_pattern, etc.
    """
    if catalog is None:
        catalog = load_error_catalog()

    errors = catalog.get("errors", {})

    matches: List[Tuple[str, float, Dict]] = []

    for error_id, error_def in errors.items():
        score = calculate_match_score(error_text, error_def)
        if score >= min_confidence:
            matches.append((error_id, score, error_def))

    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)

    if not matches:
        return {
            "matched_error": None,
            "confidence": 0.0,
            "message": "No matching error found in catalog",
            "suggestion": "Check .ai/DEBUGGING.md or create a new memory card"
        }

    best_match = matches[0]
    error_id, confidence, error_def = best_match

    result = {
        "matched_error": error_id,
        "confidence": round(confidence, 3),
        "severity": error_def.get("severity", "unknown"),
        "agent": error_def.get("agent", "quality-control"),
        "symptoms": error_def.get("symptoms", []),
        "checks": error_def.get("checks", []),
        "root_causes": error_def.get("root_causes", []),
        "fix_pattern": error_def.get("fix_pattern", ""),
        "prevention": error_def.get("prevention", []),
        "memory_refs": error_def.get("memory_refs", []),
        "playbook_ref": error_def.get("playbook_ref", ""),
        "related_errors": [m[0] for m in matches[1:4]]  # Top 3 alternatives
    }

    return result


def format_result(result: Dict[str, Any], verbose: bool = True) -> str:
    """Format routing result for human-readable output."""
    lines = []

    if result.get("matched_error") is None:
        lines.append("No matching error found in catalog.")
        lines.append(f"Suggestion: {result.get('suggestion', '')}")
        return "\n".join(lines)

    # Header
    lines.append("=" * 60)
    lines.append(f"MATCHED ERROR: {result['matched_error']}")
    lines.append(f"Confidence: {result['confidence']:.1%}")
    lines.append(f"Severity: {result['severity'].upper()}")
    lines.append(f"Recommended Agent: {result['agent']}")
    lines.append("=" * 60)

    if verbose:
        # Symptoms
        if result.get("symptoms"):
            lines.append("\nSymptoms:")
            for symptom in result["symptoms"]:
                lines.append(f"  - {symptom}")

        # Checks to run
        if result.get("checks"):
            lines.append("\nDiagnostic Checks:")
            for i, check in enumerate(result["checks"], 1):
                lines.append(f"  {i}. {check}")

        # Root causes
        if result.get("root_causes"):
            lines.append("\nPossible Root Causes:")
            for cause in result["root_causes"]:
                lines.append(f"  - {cause}")

        # Fix pattern
        if result.get("fix_pattern"):
            lines.append("\nFix Pattern:")
            for line in result["fix_pattern"].strip().split("\n"):
                lines.append(f"  {line}")

        # Prevention
        if result.get("prevention"):
            lines.append("\nPrevention:")
            for item in result["prevention"]:
                lines.append(f"  - {item}")

        # References
        if result.get("memory_refs"):
            lines.append("\nSerena Memories to Read:")
            for ref in result["memory_refs"]:
                lines.append(f"  - {ref}")

        if result.get("playbook_ref"):
            lines.append(f"\nPlaybook: {result['playbook_ref']}")

        # Related errors
        if result.get("related_errors"):
            lines.append("\nRelated Errors:")
            for related in result["related_errors"]:
                lines.append(f"  - {related}")

    return "\n".join(lines)


def list_errors(
    catalog: Dict[str, Any],
    category: Optional[str] = None,
    agent: Optional[str] = None
) -> str:
    """List all errors, optionally filtered by category or agent."""
    errors = catalog.get("errors", {})

    lines = ["Known Errors:", "=" * 40]

    # Group by category (first part of error_id)
    categories: Dict[str, List[Tuple[str, Dict]]] = {}
    for error_id, error_def in errors.items():
        cat = error_id.split(".")[0]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((error_id, error_def))

    for cat, cat_errors in sorted(categories.items()):
        # Apply filters
        if category and cat != category:
            continue

        lines.append(f"\n{cat.upper()}:")
        for error_id, error_def in cat_errors:
            error_agent = error_def.get("agent", "")
            if agent and error_agent != agent:
                continue

            severity = error_def.get("severity", "?")
            error_agent = error_def.get("agent", "?")
            symptoms = error_def.get("symptoms", ["?"])

            lines.append(f"  {error_id}")
            lines.append(f"    Severity: {severity}, Agent: {error_agent}")
            lines.append(f"    Symptom: {symptoms[0][:50]}...")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Route errors to appropriate agents and suggest fixes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/ai/error_router.py "audio output is silent"
  python3 scripts/ai/error_router.py "TTS reads SFX markers aloud"
  python3 scripts/ai/error_router.py --list
  python3 scripts/ai/error_router.py --category audio
  python3 scripts/ai/error_router.py --agent script-writer
        """
    )

    parser.add_argument(
        "error_text",
        nargs="?",
        help="Error message or symptom to route"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all known errors"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Filter errors by category (audio, ssml, env, video, etc.)"
    )
    parser.add_argument(
        "--agent",
        type=str,
        help="Filter errors by agent (audio-engineer, script-writer, etc.)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--brief",
        action="store_true",
        help="Brief output (no verbose details)"
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.1,
        help="Minimum confidence threshold (0.0-1.0, default: 0.1)"
    )

    args = parser.parse_args()

    # Load catalog
    catalog = load_error_catalog()

    # List mode
    if args.list or args.category or (args.agent and not args.error_text):
        print(list_errors(catalog, category=args.category, agent=args.agent))
        return

    # Route mode requires error text
    if not args.error_text:
        parser.print_help()
        sys.exit(1)

    # Route the error
    result = route_error(
        args.error_text,
        catalog=catalog,
        min_confidence=args.min_confidence
    )

    # Output
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print(format_result(result, verbose=not args.brief))


if __name__ == "__main__":
    main()
