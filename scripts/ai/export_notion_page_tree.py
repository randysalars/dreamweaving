#!/usr/bin/env python3
"""
Export a specific Notion page and all descendant child pages to markdown.

This is a focused helper for working with the repo's existing Notion→Markdown
export format used by the RAG pipeline (`knowledge/notion_export/pages/*.md`).

Usage:
  ./venv/bin/python3 scripts/ai/export_notion_page_tree.py --page-id <notion-page-id>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.ai.notion_knowledge_retriever import NotionKnowledgeRetriever  # noqa: E402


def _extract_page_title(page: dict) -> str:
    props = page.get("properties", {})
    for prop in props.values():
        if prop.get("type") != "title":
            continue
        title_parts = prop.get("title", [])
        title = "".join(t.get("plain_text", "") for t in title_parts).strip()
        return title or "(Untitled)"
    return "(Untitled)"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export a Notion page tree (page + descendants) to markdown."
    )
    parser.add_argument(
        "--page-id",
        required=True,
        help="Notion Page ID (hyphenated or 32-char form).",
    )
    parser.add_argument(
        "--export-dir",
        default=str(PROJECT_ROOT / "knowledge" / "notion_export"),
        help="Export directory root (default: knowledge/notion_export).",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Optional override for crawl depth.",
    )

    args = parser.parse_args()

    export_dir = Path(args.export_dir)
    pages_dir = export_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    retriever = NotionKnowledgeRetriever()
    if args.max_depth is not None:
        retriever.config.setdefault("extraction", {})
        retriever.config["extraction"]["max_depth"] = args.max_depth

    page_id = str(args.page_id).strip()
    if len(page_id) == 32 and "-" not in page_id:
        page_id = f"{page_id[0:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:32]}"

    existing_ids = retriever._scan_existing_page_ids(pages_dir)
    stats = {"pages": 0, "skipped": 0}

    print("Initializing Notion export...")
    print(f"  Page ID: {page_id}")
    print(f"  Export:  {pages_dir}")

    page = retriever.client.pages.retrieve(page_id=page_id)
    title = _extract_page_title(page)

    item = {
        "id": page["id"],
        "title": title,
        "url": page.get("url", ""),
        "last_edited_time": page.get("last_edited_time", ""),
        "type": "page",
    }

    print(f"\nExporting root page: {title}")
    exported_ids = set(existing_ids)
    retriever._export_single_page(item, pages_dir, stats, exported_ids)

    print("\nCrawling children...")
    retriever._crawl_and_export_children(
        parent_id=page["id"],
        pages_dir=pages_dir,
        stats=stats,
        exported_ids=exported_ids,
        depth=0,
    )

    print("\nDone.")
    print(f"  Exported: {stats['pages']}")
    print(f"  Skipped:  {stats['skipped']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

