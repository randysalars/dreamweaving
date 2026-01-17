#!/usr/bin/env python3
"""
Export Coin YAML Guides to Markdown

Converts the structured YAML coin knowledge files to markdown format
and places them in the Notion export directory where the RAG file watcher
will automatically index them.

This approach works seamlessly with the running RAG watcher.

Usage:
    python3 -m scripts.ai.export_coin_knowledge
"""

import os
import sys
import argparse
import yaml
from pathlib import Path
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
COINS_DIR = PROJECT_ROOT / "knowledge" / "coins"
EXPORT_DIR = PROJECT_ROOT / "knowledge" / "notion_export" / "pages"


def yaml_to_markdown(data: dict, depth: int = 0) -> str:
    """Convert YAML data to readable markdown."""
    lines = []
    
    for key, value in data.items():
        # Skip metadata fields
        if key in ("entry_id", "version", "created"):
            continue
        
        # Convert key to readable header
        readable_key = key.replace("_", " ").title()
        
        if isinstance(value, dict):
            if depth == 0:
                lines.append(f"\n## {readable_key}\n")
            else:
                lines.append(f"\n### {readable_key}\n")
            lines.append(yaml_to_markdown(value, depth + 1))
            
        elif isinstance(value, list):
            lines.append(f"\n**{readable_key}:**\n")
            for item in value:
                if isinstance(item, dict):
                    # Format dict items
                    item_parts = []
                    for k, v in item.items():
                        if k != "note":
                            item_parts.append(f"{k}: {v}")
                    item_text = ", ".join(item_parts)
                    note = item.get("note", "")
                    if note:
                        lines.append(f"- {item_text} — *{note}*")
                    else:
                        lines.append(f"- {item_text}")
                else:
                    lines.append(f"- {item}")
            lines.append("")
            
        elif isinstance(value, str) and len(value) > 100:
            # Long text - as paragraph
            lines.append(f"\n**{readable_key}:**\n")
            lines.append(f"{value}\n")
            
        else:
            lines.append(f"**{readable_key}:** {value}\n")
    
    return "\n".join(lines)


def export_coin_yaml(filepath: Path) -> str:
    """Convert a coin YAML file to markdown."""
    with open(filepath) as f:
        data = yaml.safe_load(f)
    
    if not data:
        return ""
    
    name = data.get("name", filepath.stem.replace("_", " ").title())
    category = data.get("category", "coins")
    description = data.get("description", "")
    
    # Build markdown document
    md_lines = [
        f"# {name}",
        "",
        f"Source: file://{filepath}",
        f"Last edited: {datetime.now().isoformat()}",
        f"Category: {category}",
        "",
        "---",
        "",
    ]
    
    if description:
        md_lines.append(f"> {description.strip()}")
        md_lines.append("")
    
    md_lines.append(yaml_to_markdown(data))
    
    return "\n".join(md_lines)


def export_all_coin_knowledge(verbose: bool = False) -> dict:
    """Export all coin YAML files to markdown."""
    if not COINS_DIR.exists():
        print(f"Error: Coins directory not found: {COINS_DIR}")
        return {"error": "Directory not found"}
    
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    yaml_files = list(COINS_DIR.glob("*.yaml")) + list(COINS_DIR.glob("*.yml"))
    
    if not yaml_files:
        print("No YAML files found")
        return {"files": 0}
    
    print(f"Found {len(yaml_files)} coin knowledge files")
    
    stats = {"files": 0, "exported": []}
    
    for filepath in yaml_files:
        try:
            markdown = export_coin_yaml(filepath)
            
            # Write to export directory with "Coin Guide - " prefix
            output_name = f"Coin Guide - {filepath.stem.replace('_', ' ').title()}.md"
            output_path = EXPORT_DIR / output_name
            
            output_path.write_text(markdown)
            
            stats["files"] += 1
            stats["exported"].append(output_name)
            
            if verbose:
                print(f"  ✓ {filepath.name} → {output_name}")
                
        except Exception as e:
            print(f"  ✗ Error exporting {filepath.name}: {e}")
    
    print(f"\n✅ Exported {stats['files']} files to {EXPORT_DIR}")
    print("The RAG file watcher will automatically index these files.")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Export coin YAML knowledge to markdown for RAG indexing"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress"
    )
    
    args = parser.parse_args()
    export_all_coin_knowledge(verbose=args.verbose)


if __name__ == "__main__":
    main()
