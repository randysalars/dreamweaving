#!/usr/bin/env python3
"""
Sync Coin Buying Knowledge to Salarsu Chatbot

Exports the buyer-focused coin knowledge from Dreamweaving and adds it
to the Salarsu chatbot's knowledge base.

This includes:
- Decision guides ("Sleep-Well Coins", "Learning Coins")
- Buying psychology content
- Situational buying guides ($100/$500/$1000)
- YAML coin guides (Morgan, Peace, Junk Silver, etc.)

Usage:
    python3 scripts/sync_coin_knowledge_to_salarsu.py

    # Force overwrite existing buyer knowledge
    python3 scripts/sync_coin_knowledge_to_salarsu.py --force
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
DREAMWEAVING_ROOT = SCRIPT_DIR.parent
NOTION_EXPORT = DREAMWEAVING_ROOT / "knowledge" / "notion_export" / "pages"
YAML_GUIDES = DREAMWEAVING_ROOT / "knowledge" / "coins"

# Salarsu paths - adjust if needed
SALARSU_ROOT = Path("/home/rsalars/Projects/salarsu")
SALARSU_KNOWLEDGE = SALARSU_ROOT / "knowledge" / "coin_data"
SALARSU_KNOWLEDGE_JSON = SALARSU_KNOWLEDGE / "coin-knowledge.json"


def load_yaml_guide(filepath: Path) -> dict:
    """Load and parse a YAML coin guide."""
    import yaml
    with open(filepath) as f:
        data = yaml.safe_load(f)
    
    name = data.get("name", filepath.stem.replace("_", " ").title())
    description = data.get("description", "")
    
    # Convert YAML to readable text
    content_lines = [f"# {name}", ""]
    if description:
        content_lines.append(f"> {description.strip()}")
        content_lines.append("")
    
    def format_section(data, depth=0):
        lines = []
        for key, value in data.items():
            if key in ("entry_id", "name", "description", "version", "created", "category"):
                continue
            
            readable_key = key.replace("_", " ").title()
            
            if isinstance(value, dict):
                if depth == 0:
                    lines.append(f"\n## {readable_key}\n")
                else:
                    lines.append(f"\n### {readable_key}\n")
                lines.extend(format_section(value, depth + 1))
            elif isinstance(value, list):
                lines.append(f"\n**{readable_key}:**\n")
                for item in value:
                    if isinstance(item, dict):
                        parts = [f"{k}: {v}" for k, v in item.items() if k != "note"]
                        note = item.get("note", "")
                        if note:
                            lines.append(f"- {', '.join(parts)} — *{note}*")
                        else:
                            lines.append(f"- {', '.join(parts)}")
                    else:
                        lines.append(f"- {item}")
            else:
                lines.append(f"**{readable_key}:** {value}")
        return lines
    
    content_lines.extend(format_section(data))
    
    return {
        "id": f"buyer-guide-{filepath.stem}",
        "type": "buyer_guide",
        "title": name,
        "content": "\n".join(content_lines),
        "metadata": {
            "source": "dreamweaving_yaml",
            "category": data.get("category", "coins"),
            "synced_at": datetime.now().isoformat()
        }
    }


def load_notion_page(filepath: Path) -> dict:
    """Load a Notion export markdown page."""
    content = filepath.read_text()
    
    # Extract title from first heading
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else filepath.stem.replace("_", " ").title()
    
    # Clean title for ID
    clean_id = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    
    # Determine type based on content
    content_lower = content.lower()
    if any(kw in content_lower for kw in ["sleep-well", "learning coin", "buyer"]):
        doc_type = "buyer_psychology"
    elif any(kw in content_lower for kw in ["$100", "$500", "$1000", "budget"]):
        doc_type = "situational_guide"
    elif any(kw in content_lower for kw in ["dealer", "mistake", "regret"]):
        doc_type = "buying_advice"
    else:
        doc_type = "coin_knowledge"
    
    return {
        "id": f"notion-{clean_id[:50]}",
        "type": doc_type,
        "title": title,
        "content": content,
        "metadata": {
            "source": "dreamweaving_notion",
            "original_file": filepath.name,
            "synced_at": datetime.now().isoformat()
        }
    }


def get_coin_related_pages() -> list:
    """Find all coin-related Notion pages."""
    if not NOTION_EXPORT.exists():
        return []
    
    coin_keywords = [
        "coin", "silver", "morgan", "peace", "bullion", "junk",
        "buy", "dealer", "supplies", "rag dbase", "numismatic",
        "sleep", "learning", "confidence"
    ]
    
    pages = []
    for md_file in NOTION_EXPORT.glob("*.md"):
        name_lower = md_file.name.lower()
        if any(kw in name_lower for kw in coin_keywords):
            pages.append(md_file)
    
    return pages


def sync_knowledge(force: bool = False, verbose: bool = False):
    """Sync Dreamweaving coin knowledge to Salarsu."""
    
    # Ensure Salarsu knowledge dir exists
    SALARSU_KNOWLEDGE.mkdir(parents=True, exist_ok=True)
    
    # Load existing knowledge
    existing_docs = []
    if SALARSU_KNOWLEDGE_JSON.exists():
        try:
            existing_docs = json.loads(SALARSU_KNOWLEDGE_JSON.read_text())
            print(f"📚 Loaded {len(existing_docs)} existing documents")
        except json.JSONDecodeError:
            print("⚠️  Could not parse existing knowledge, starting fresh")
            existing_docs = []
    
    # Track existing IDs and their sources
    existing_ids = {doc["id"]: i for i, doc in enumerate(existing_docs)}
    synced_ids = set()
    new_docs = []
    updated_docs = 0
    
    # 1. Load YAML guides
    print("\n📦 Processing YAML coin guides...")
    if YAML_GUIDES.exists():
        for yaml_file in YAML_GUIDES.glob("*.yaml"):
            try:
                doc = load_yaml_guide(yaml_file)
                synced_ids.add(doc["id"])
                
                if doc["id"] in existing_ids:
                    if force:
                        existing_docs[existing_ids[doc["id"]]] = doc
                        updated_docs += 1
                        if verbose:
                            print(f"  ↻ Updated: {doc['title']}")
                else:
                    new_docs.append(doc)
                    if verbose:
                        print(f"  + Added: {doc['title']}")
            except Exception as e:
                print(f"  ✗ Error processing {yaml_file.name}: {e}")
    
    # 2. Load Notion pages
    print("\n📄 Processing Notion coin pages...")
    notion_pages = get_coin_related_pages()
    
    # Deduplicate by base name (ignore _1, _2, etc. versions)
    seen_bases = {}
    for page in notion_pages:
        # Remove trailing _N from filename
        base_name = re.sub(r'_\d+$', '', page.stem)
        if base_name not in seen_bases:
            seen_bases[base_name] = page
    
    for page in seen_bases.values():
        try:
            doc = load_notion_page(page)
            synced_ids.add(doc["id"])
            
            if doc["id"] in existing_ids:
                if force:
                    existing_docs[existing_ids[doc["id"]]] = doc
                    updated_docs += 1
                    if verbose:
                        print(f"  ↻ Updated: {doc['title'][:50]}...")
            else:
                new_docs.append(doc)
                if verbose:
                    print(f"  + Added: {doc['title'][:50]}...")
        except Exception as e:
            print(f"  ✗ Error processing {page.name}: {e}")
    
    # 3. Merge documents
    all_docs = existing_docs + new_docs
    
    # 4. Save updated knowledge
    SALARSU_KNOWLEDGE_JSON.write_text(json.dumps(all_docs, indent=2))
    
    print(f"\n✅ Sync complete!")
    print(f"   Total documents: {len(all_docs)}")
    print(f"   New documents: {len(new_docs)}")
    print(f"   Updated documents: {updated_docs}")
    print(f"   Output: {SALARSU_KNOWLEDGE_JSON}")
    
    print(f"\n📌 Next step: Re-index the knowledge base:")
    print(f"   cd {SALARSU_ROOT}")
    print(f"   .venv/bin/python3 scripts/coin-rag-pipeline.py --index --force")
    
    return {
        "total": len(all_docs),
        "new": len(new_docs),
        "updated": updated_docs
    }


def main():
    parser = argparse.ArgumentParser(
        description="Sync Dreamweaving coin knowledge to Salarsu chatbot"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force update existing documents"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synced without making changes"
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("\n🔍 DRY RUN - Showing what would be synced:\n")
        
        print("YAML Guides:")
        if YAML_GUIDES.exists():
            for f in YAML_GUIDES.glob("*.yaml"):
                print(f"  • {f.name}")
        
        print("\nNotion Pages (coin-related):")
        pages = get_coin_related_pages()
        for p in pages[:20]:
            print(f"  • {p.name}")
        if len(pages) > 20:
            print(f"  ... and {len(pages) - 20} more")
        
        print(f"\nTotal: {len(list(YAML_GUIDES.glob('*.yaml')))} YAML + {len(pages)} Notion pages")
        return
    
    sync_knowledge(force=args.force, verbose=args.verbose)


if __name__ == "__main__":
    main()
