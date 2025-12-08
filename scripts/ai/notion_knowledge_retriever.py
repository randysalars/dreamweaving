#!/usr/bin/env python3
"""
Notion Knowledge Retriever for Dreamweaving

Bridge between Serena MCP (code) and Notion MCP (knowledge).
Provides functions to query the Sacred Digital Dreamweaver workspace
for canonical definitions, lore, and frameworks.

Usage:
    # Search for archetypes
    python3 -m scripts.ai.notion_knowledge_retriever --search "Navigator archetype"

    # Get specific page content
    python3 -m scripts.ai.notion_knowledge_retriever --page "Mythic Cosmology"

    # Query database by name
    python3 -m scripts.ai.notion_knowledge_retriever --db archetypes --filter "Guardian"

    # Export all content to markdown
    python3 -m scripts.ai.notion_knowledge_retriever --export ./knowledge/notion_export/
"""

import os
import sys
import json
import argparse
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    from notion_client import Client
    HAS_NOTION = True
except ImportError:
    HAS_NOTION = False
    print("Warning: notion-client not installed. Run: pip install notion-client")


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "notion_config.yaml"


def load_config() -> Dict[str, Any]:
    """Load Notion configuration from YAML."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")

    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    # Resolve environment variables
    def resolve_env(obj):
        if isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            var_name = obj[2:-1]
            return os.environ.get(var_name, obj)
        elif isinstance(obj, dict):
            return {k: resolve_env(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [resolve_env(item) for item in obj]
        return obj

    return resolve_env(config)


def get_notion_client() -> Client:
    """Initialize Notion client with token from config."""
    if not HAS_NOTION:
        raise ImportError("notion-client not installed")

    config = load_config()
    token = config["notion"]["integration_token"]

    if not token or token.startswith("${"):
        raise ValueError(
            "NOTION_TOKEN not set. Create an integration at "
            "https://www.notion.so/profile/integrations and set the token."
        )

    return Client(auth=token)


class NotionKnowledgeRetriever:
    """
    Retrieves knowledge from the Sacred Digital Dreamweaver Notion workspace.

    Capabilities:
    - Search workspace by title
    - Query structured databases (Archetypes, Realms, Frequencies, etc.)
    - Retrieve full page content as markdown
    - Export content for embeddings pipeline
    """

    def __init__(self):
        self.client = get_notion_client()
        self.config = load_config()
        self.workspace_root = self.config["notion"]["workspace_root"]

    def search_workspace(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search entire workspace by title.

        Note: Notion API search is title-based only, not full-text.
        For semantic search, use the embeddings pipeline.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching pages/databases with metadata
        """
        response = self.client.search(
            query=query,
            page_size=limit
        )

        results = []
        for item in response.get("results", []):
            result = {
                "id": item["id"],
                "type": item["object"],  # "page" or "database"
                "url": item.get("url", ""),
                "created_time": item.get("created_time"),
                "last_edited_time": item.get("last_edited_time"),
            }

            # Extract title based on type
            if item["object"] == "page":
                props = item.get("properties", {})
                title_prop = props.get("title", props.get("Name", {}))
                if "title" in title_prop:
                    result["title"] = "".join(
                        t.get("plain_text", "") for t in title_prop["title"]
                    )
                else:
                    result["title"] = "(Untitled)"
            elif item["object"] == "database":
                title_list = item.get("title", [])
                result["title"] = "".join(
                    t.get("plain_text", "") for t in title_list
                )

            results.append(result)

        return results

    def query_database(
        self,
        database_key: str,
        filter_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query a Notion database by key from config.

        Args:
            database_key: Key from config (archetypes, realms, frequencies, etc.)
            filter_name: Optional filter by Name property (contains)
            limit: Maximum results

        Returns:
            List of database entries with all properties
        """
        db_config = self.config["databases"].get(database_key)
        if not db_config:
            raise ValueError(f"Unknown database: {database_key}")

        db_id = db_config.get("id")
        if not db_id:
            raise ValueError(
                f"Database ID not configured for '{database_key}'. "
                "Update config/notion_config.yaml with the database ID."
            )

        # Build filter
        filter_obj = None
        if filter_name:
            filter_obj = {
                "property": "Name",
                "title": {"contains": filter_name}
            }

        response = self.client.databases.query(
            database_id=db_id,
            filter=filter_obj,
            page_size=limit
        )

        return [self._parse_entry(entry) for entry in response.get("results", [])]

    def get_page_content(self, page_id: str, as_markdown: bool = True) -> str:
        """
        Retrieve full page content.

        Args:
            page_id: Notion page ID
            as_markdown: Convert blocks to markdown (default True)

        Returns:
            Page content as markdown or raw blocks
        """
        blocks = self._get_all_blocks(page_id)

        if as_markdown:
            return self._blocks_to_markdown(blocks)
        else:
            return json.dumps(blocks, indent=2, default=str)

    def get_page_by_title(self, title: str) -> Optional[Dict]:
        """
        Find and return a page by exact title match.

        Args:
            title: Page title to search for

        Returns:
            Page content and metadata, or None if not found
        """
        results = self.search_workspace(title, limit=10)

        for result in results:
            if result["title"].lower() == title.lower():
                content = self.get_page_content(result["id"])
                return {
                    **result,
                    "content": content
                }

        return None

    def export_all_content(self, output_dir: Path, include_recursive: bool = True) -> Dict[str, int]:
        """
        Export all accessible content to markdown files.

        Uses BOTH search API AND recursive child page crawling to ensure
        complete coverage of all subpages at any depth.

        Args:
            output_dir: Directory to save exports
            include_recursive: Also crawl child pages from workspace root (default True)

        Returns:
            Statistics about exported content
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        stats = {"pages": 0, "databases": 0, "entries": 0, "skipped": 0}
        exported_ids = set()  # Track to avoid duplicates

        # Export pages
        pages_dir = output_dir / "pages"
        pages_dir.mkdir(exist_ok=True)

        # Method 1: Search API (finds most accessible pages)
        print("Phase 1: Searching workspace via API...")
        search_results = self.search_workspace("", limit=100)

        for item in search_results:
            if item["type"] == "page" and item["id"] not in exported_ids:
                self._export_single_page(item, pages_dir, stats, exported_ids)

        # Method 2: Recursive child page crawl from workspace root
        if include_recursive and self.workspace_root:
            print(f"\nPhase 2: Crawling child pages from root {self.workspace_root}...")
            self._crawl_and_export_children(
                self.workspace_root,
                pages_dir,
                stats,
                exported_ids,
                depth=0
            )

        # Export databases
        for db_key, db_config in self.config["databases"].items():
            if not db_config.get("id"):
                continue

            db_dir = output_dir / "databases" / db_key
            db_dir.mkdir(parents=True, exist_ok=True)

            try:
                entries = self.query_database(db_key)
                stats["databases"] += 1

                for entry in entries:
                    safe_name = self._sanitize_filename(entry.get("Name", "untitled"))
                    filepath = db_dir / f"{safe_name}.md"

                    with open(filepath, "w") as f:
                        f.write(f"# {entry.get('Name', 'Untitled')}\n\n")
                        f.write(f"Database: {db_key}\n")
                        f.write(f"ID: {entry['id']}\n\n")
                        f.write("---\n\n")

                        for prop, value in entry.items():
                            if prop not in ["id", "url", "created_time", "last_edited_time"]:
                                f.write(f"## {prop}\n\n{value}\n\n")

                    stats["entries"] += 1

            except Exception as e:
                print(f"Error exporting database '{db_key}': {e}")

        # Write manifest
        manifest = {
            "exported_at": datetime.utcnow().isoformat(),
            "stats": stats,
            "databases": list(self.config["databases"].keys()),
        }
        with open(output_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        return stats

    def _get_all_blocks(self, block_id: str, depth: int = 0) -> List[Dict]:
        """Recursively fetch all blocks from a page."""
        max_depth = self.config.get("extraction", {}).get("max_depth", 10)
        if depth > max_depth:
            return []

        blocks = []
        cursor = None

        while True:
            response = self.client.blocks.children.list(
                block_id=block_id,
                start_cursor=cursor,
                page_size=100
            )

            for block in response.get("results", []):
                blocks.append(block)

                # Recursively fetch children
                if block.get("has_children"):
                    children = self._get_all_blocks(block["id"], depth + 1)
                    block["children"] = children

            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        return blocks

    def _blocks_to_markdown(self, blocks: List[Dict], indent: int = 0) -> str:
        """Convert Notion blocks to markdown."""
        lines = []
        prefix = "  " * indent

        for block in blocks:
            block_type = block.get("type", "")
            content = block.get(block_type, {})

            if block_type == "paragraph":
                text = self._rich_text_to_str(content.get("rich_text", []))
                lines.append(f"{prefix}{text}")

            elif block_type.startswith("heading_"):
                level = int(block_type[-1])
                text = self._rich_text_to_str(content.get("rich_text", []))
                lines.append(f"{prefix}{'#' * level} {text}")

            elif block_type == "bulleted_list_item":
                text = self._rich_text_to_str(content.get("rich_text", []))
                lines.append(f"{prefix}- {text}")

            elif block_type == "numbered_list_item":
                text = self._rich_text_to_str(content.get("rich_text", []))
                lines.append(f"{prefix}1. {text}")

            elif block_type == "to_do":
                text = self._rich_text_to_str(content.get("rich_text", []))
                checked = "x" if content.get("checked") else " "
                lines.append(f"{prefix}- [{checked}] {text}")

            elif block_type == "toggle":
                text = self._rich_text_to_str(content.get("rich_text", []))
                lines.append(f"{prefix}<details><summary>{text}</summary>")

            elif block_type == "code":
                text = self._rich_text_to_str(content.get("rich_text", []))
                lang = content.get("language", "")
                lines.append(f"{prefix}```{lang}")
                lines.append(f"{prefix}{text}")
                lines.append(f"{prefix}```")

            elif block_type == "quote":
                text = self._rich_text_to_str(content.get("rich_text", []))
                lines.append(f"{prefix}> {text}")

            elif block_type == "callout":
                icon = content.get("icon", {}).get("emoji", "")
                text = self._rich_text_to_str(content.get("rich_text", []))
                lines.append(f"{prefix}> {icon} {text}")

            elif block_type == "divider":
                lines.append(f"{prefix}---")

            elif block_type == "table":
                lines.append(f"{prefix}(table)")  # Simplified table handling

            elif block_type == "image":
                url = content.get("file", content.get("external", {})).get("url", "")
                caption = self._rich_text_to_str(content.get("caption", []))
                lines.append(f"{prefix}![{caption}]({url})")

            # Handle children
            if block.get("children"):
                child_md = self._blocks_to_markdown(block["children"], indent + 1)
                lines.append(child_md)

            # Add spacing
            if block_type not in ["bulleted_list_item", "numbered_list_item"]:
                lines.append("")

        return "\n".join(lines)

    def _rich_text_to_str(self, rich_text: List[Dict]) -> str:
        """Convert rich text array to plain string."""
        return "".join(
            item.get("plain_text", "")
            for item in rich_text
        )

    def _parse_entry(self, entry: Dict) -> Dict:
        """Parse a database entry into a flat dictionary."""
        result = {
            "id": entry["id"],
            "url": entry.get("url", ""),
            "created_time": entry.get("created_time"),
            "last_edited_time": entry.get("last_edited_time"),
        }

        for prop_name, prop_value in entry.get("properties", {}).items():
            prop_type = prop_value.get("type")

            if prop_type == "title":
                result[prop_name] = self._rich_text_to_str(prop_value.get("title", []))

            elif prop_type == "rich_text":
                result[prop_name] = self._rich_text_to_str(prop_value.get("rich_text", []))

            elif prop_type == "number":
                result[prop_name] = prop_value.get("number")

            elif prop_type == "select":
                select = prop_value.get("select")
                result[prop_name] = select.get("name") if select else None

            elif prop_type == "multi_select":
                result[prop_name] = [
                    item.get("name") for item in prop_value.get("multi_select", [])
                ]

            elif prop_type == "relation":
                result[prop_name] = [
                    rel.get("id") for rel in prop_value.get("relation", [])
                ]

            elif prop_type == "checkbox":
                result[prop_name] = prop_value.get("checkbox", False)

            elif prop_type == "date":
                date_obj = prop_value.get("date")
                result[prop_name] = date_obj.get("start") if date_obj else None

            elif prop_type == "url":
                result[prop_name] = prop_value.get("url")

            else:
                # Store raw for unsupported types
                result[prop_name] = prop_value

        return result

    def _sanitize_filename(self, name: str) -> str:
        """Create safe filename from title."""
        # Replace unsafe characters
        safe = name.replace("/", "-").replace("\\", "-").replace(":", "-")
        safe = "".join(c for c in safe if c.isalnum() or c in " -_")
        return safe[:50].strip() or "untitled"

    def _export_single_page(
        self,
        item: Dict,
        pages_dir: Path,
        stats: Dict,
        exported_ids: set
    ) -> bool:
        """Export a single page to markdown file."""
        try:
            page_id = item["id"]
            title = item.get("title", "(Untitled)")
            url = item.get("url", "")
            last_edited = item.get("last_edited_time", "")

            content = self.get_page_content(page_id)
            safe_title = self._sanitize_filename(title)
            filepath = pages_dir / f"{safe_title}.md"

            # Handle duplicate filenames
            counter = 1
            while filepath.exists() and page_id not in exported_ids:
                filepath = pages_dir / f"{safe_title}_{counter}.md"
                counter += 1

            with open(filepath, "w") as f:
                f.write(f"# {title}\n\n")
                f.write(f"Source: {url}\n")
                f.write(f"Last edited: {last_edited}\n")
                f.write(f"Page ID: {page_id}\n\n")
                f.write("---\n\n")
                f.write(content)

            exported_ids.add(page_id)
            stats["pages"] += 1
            print(f"  Exported: {title}")
            return True

        except Exception as e:
            print(f"  Error exporting '{item.get('title', 'unknown')}': {e}")
            stats["skipped"] += 1
            return False

    def _crawl_and_export_children(
        self,
        parent_id: str,
        pages_dir: Path,
        stats: Dict,
        exported_ids: set,
        depth: int = 0
    ):
        """
        Recursively crawl child pages from a parent page/block.

        This ensures we get ALL subpages at any depth, not just
        what the search API returns.
        """
        max_depth = self.config.get("extraction", {}).get("max_depth", 10)
        if depth > max_depth:
            print(f"  Max depth {max_depth} reached, stopping recursion")
            return

        try:
            cursor = None
            while True:
                response = self.client.blocks.children.list(
                    block_id=parent_id,
                    start_cursor=cursor,
                    page_size=100
                )

                for block in response.get("results", []):
                    block_type = block.get("type", "")

                    # Found a child page!
                    if block_type == "child_page":
                        child_id = block["id"]
                        child_title = block.get("child_page", {}).get("title", "(Untitled)")

                        if child_id not in exported_ids:
                            # Build item dict for export
                            item = {
                                "id": child_id,
                                "title": child_title,
                                "url": f"https://notion.so/{child_id.replace('-', '')}",
                                "last_edited_time": block.get("last_edited_time", ""),
                                "type": "page"
                            }
                            self._export_single_page(item, pages_dir, stats, exported_ids)

                            # Recurse into this child page
                            self._crawl_and_export_children(
                                child_id,
                                pages_dir,
                                stats,
                                exported_ids,
                                depth + 1
                            )

                    # Found a child database
                    elif block_type == "child_database":
                        db_title = block.get("child_database", {}).get("title", "")
                        print(f"  Found database: {db_title} (ID: {block['id']})")
                        # Note: Database entries are exported separately

                    # Some blocks can have child pages nested inside
                    elif block.get("has_children"):
                        self._crawl_and_export_children(
                            block["id"],
                            pages_dir,
                            stats,
                            exported_ids,
                            depth + 1
                        )

                if not response.get("has_more"):
                    break
                cursor = response.get("next_cursor")

        except Exception as e:
            print(f"  Error crawling children of {parent_id}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Query Dreamweaving canonical knowledge from Notion"
    )
    parser.add_argument(
        "--search", "-s",
        help="Search workspace by title"
    )
    parser.add_argument(
        "--page", "-p",
        help="Get page content by title"
    )
    parser.add_argument(
        "--db",
        help="Query database (archetypes, realms, frequencies, rituals, lore, scripts)"
    )
    parser.add_argument(
        "--filter", "-f",
        help="Filter database by name"
    )
    parser.add_argument(
        "--export", "-e",
        help="Export all content to directory"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    if not HAS_NOTION:
        print("Error: notion-client not installed")
        print("Run: pip install notion-client")
        sys.exit(1)

    try:
        retriever = NotionKnowledgeRetriever()
    except Exception as e:
        print(f"Error initializing: {e}")
        sys.exit(1)

    try:
        if args.search:
            results = retriever.search_workspace(args.search)
            if args.json:
                print(json.dumps(results, indent=2, default=str))
            else:
                print(f"\nFound {len(results)} results for '{args.search}':\n")
                for r in results:
                    print(f"  [{r['type']}] {r['title']}")
                    print(f"         {r['url']}")

        elif args.page:
            result = retriever.get_page_by_title(args.page)
            if result:
                if args.json:
                    print(json.dumps(result, indent=2, default=str))
                else:
                    print(f"\n# {result['title']}\n")
                    print(f"URL: {result['url']}")
                    print(f"\n{result['content']}")
            else:
                print(f"Page not found: {args.page}")

        elif args.db:
            results = retriever.query_database(args.db, args.filter)
            if args.json:
                print(json.dumps(results, indent=2, default=str))
            else:
                print(f"\nFound {len(results)} entries in '{args.db}':\n")
                for entry in results:
                    print(f"  - {entry.get('Name', '(unnamed)')}")
                    for key, value in entry.items():
                        if key not in ["id", "url", "Name", "created_time", "last_edited_time"]:
                            if isinstance(value, str) and len(value) > 100:
                                value = value[:100] + "..."
                            print(f"      {key}: {value}")
                    print()

        elif args.export:
            stats = retriever.export_all_content(Path(args.export))
            print(f"\nExport complete:")
            print(f"  Pages: {stats['pages']}")
            print(f"  Databases: {stats['databases']}")
            print(f"  Entries: {stats['entries']}")
            print(f"\nSaved to: {args.export}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
