#!/usr/bin/env python3
"""
Populate the Dreamweaving Topic Index Notion database with all child pages
under the configured root page. If the index grows beyond the configured
threshold, a new database is created and the remaining topics are added there.

Env vars:
  NOTION_TOKEN                (required) Notion integration token
  NOTION_ROOT_PAGE_ID         (default: 1ee2bab3796d80738af6c96bd5077acf)
  NOTION_TOPIC_DATABASE_ID    (optional) Existing database to use as primary
  NOTION_DB_PAGE_SIZE_LIMIT   (optional) Threshold before creating overflow DB (default 900)
"""

import os
import sys
import random
import time
import requests
from typing import Dict, List, Tuple, Deque
from collections import deque

NOTION_VERSION = "2022-06-28"
ROOT_PAGE_ID = os.getenv("NOTION_ROOT_PAGE_ID", "1ee2bab3796d80738af6c96bd5077acf")
PRIMARY_DB_ID = os.getenv("NOTION_TOPIC_DATABASE_ID")  # optional override
DB_PAGE_SIZE_LIMIT = int(os.getenv("NOTION_DB_PAGE_SIZE_LIMIT", "900"))
REQUEST_TIMEOUT = int(os.getenv("NOTION_REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("NOTION_REQUEST_RETRIES", "5"))


def headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def list_children(token: str, block_id: str) -> List[Dict]:
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    cursor = None
    results: List[Dict] = []
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        attempt = 0
        while True:
            try:
                resp = requests.get(
                    url,
                    headers=headers(token),
                    params=params,
                    timeout=REQUEST_TIMEOUT,
                )
                resp.raise_for_status()
                data = resp.json()
                # gentle pacing to avoid rate limits
                time.sleep(0.01)
                break
            except requests.exceptions.Timeout:
                attempt += 1
                if attempt >= MAX_RETRIES:
                    raise
                continue
            except requests.exceptions.RequestException:
                attempt += 1
                if attempt >= MAX_RETRIES:
                    raise
                continue
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return results


def collect_child_pages(token: str, root_id: str) -> List[Dict]:
    """Iterative BFS collection with progress logging."""
    collected: List[Dict] = []
    queue: Deque[Tuple[str, List[str]]] = deque()
    queue.append((root_id, []))
    seen = set()
    while queue:
        block_id, path = queue.popleft()
        if block_id in seen:
            continue
        seen.add(block_id)
        try:
            children = list_children(token, block_id)
        except Exception as exc:
            print(f"  ⚠️  Failed to fetch children for {block_id}: {exc}")
            continue
        for block in children:
            if block.get("type") != "child_page":
                continue
            title = (block["child_page"].get("title") or "").strip()
            child_path = path + [title or "Untitled"]
            collected.append({"id": block["id"], "title": title, "path": child_path})
            if block.get("has_children"):
                queue.append((block["id"], child_path))
            if len(collected) % 10 == 0:
                print(f"  ... collected {len(collected)} pages so far", flush=True)
    return collected


def notion_url(page_id: str) -> str:
    return f"https://www.notion.so/{page_id.replace('-', '')}"


def fetch_existing_paths(token: str, database_id: str) -> Tuple[int, set]:
    """Return total row count and a set of existing Path strings."""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    cursor = None
    total = 0
    paths = set()
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        resp = requests.post(url, headers=headers(token), json=body, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for row in data.get("results", []):
            total += 1
            props = row.get("properties", {})
            path_prop = props.get("Path", {})
            rich = path_prop.get("rich_text", [])
            if rich and isinstance(rich, list):
                text = "".join(rt.get("plain_text", "") for rt in rich)
                if text:
                    paths.add(text.strip())
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return total, paths


def create_database(token: str, parent_page: str, suffix: int = 0) -> str:
    name = "Dreamweaving Topic Index" if suffix == 0 else f"Dreamweaving Topic Index ({suffix})"
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page},
        "title": [{"type": "text", "text": {"content": name}}],
        "properties": {
            "Name": {"title": {}},
            "Status": {"select": {"options": [
                {"name": "New", "color": "blue"},
                {"name": "In Progress", "color": "yellow"},
                {"name": "Used", "color": "green"},
                {"name": "Blocked", "color": "red"},
            ]}},
            "Used": {"checkbox": {}},
            "Used At": {"date": {}},
            "Path": {"rich_text": {}},
            "Source Page": {"url": {}},
            "Notes": {"rich_text": {}},
        },
    }
    resp = requests.post("https://api.notion.com/v1/databases",
                         headers=headers(token), json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    print(f"Created database '{name}' -> {data.get('url')}")
    return data["id"]


def insert_rows(token: str, database_id: str, rows: List[Dict]):
    url = "https://api.notion.com/v1/pages"
    for row in rows:
        payload = {
            "parent": {"database_id": database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": row["title"] or "Untitled"}}]},
                "Path": {"rich_text": [{"text": {"content": row["path_str"]}}]},
                "Source Page": {"url": row["url"]},
                "Status": {"select": {"name": "New"}},
                "Used": {"checkbox": False},
            },
        }
        resp = requests.post(url, headers=headers(token), json=payload, timeout=15)
        if resp.status_code != 200:
            print(f"  ✗ Failed to insert {row['title']}: {resp.text[:180]}")
        else:
            print(f"  ✓ Added {row['title']}")


def main():
    token = os.getenv("NOTION_TOKEN")
    if not token:
        print("NOTION_TOKEN is required")
        sys.exit(1)

    print(f"Scanning child pages under root {ROOT_PAGE_ID} ...")
    topics = collect_child_pages(token, ROOT_PAGE_ID)
    if not topics:
        print("No child pages found; nothing to do.")
        sys.exit(0)
    print(f"Found {len(topics)} topic pages.")

    primary_db = PRIMARY_DB_ID or create_database(token, ROOT_PAGE_ID, suffix=0)

    existing_count, existing_paths = fetch_existing_paths(token, primary_db)
    print(f"Primary DB has {existing_count} rows; {len(existing_paths)} paths recorded.")

    to_add = []
    for t in topics:
        path_str = " / ".join(t["path"])
        if path_str in existing_paths:
            continue
        to_add.append(
            {
                "title": t["title"] or "Untitled",
                "path_str": path_str,
                "url": notion_url(t["id"]),
            }
        )

    if not to_add:
        print("No new topics to add.")
        sys.exit(0)

    random.shuffle(to_add)

    db_index = 0
    current_db = primary_db
    current_count = existing_count

    remaining = to_add
    while remaining:
        available = max(DB_PAGE_SIZE_LIMIT - current_count, 0)
        batch = remaining[:available] if available > 0 else []
        if batch:
            print(f"Adding {len(batch)} rows to DB {current_db} ...")
            insert_rows(token, current_db, batch)
            current_count += len(batch)
            remaining = remaining[len(batch):]
        else:
            # create overflow database
            db_index += 1
            current_db = create_database(token, ROOT_PAGE_ID, suffix=db_index)
            current_count = 0

    print("Done.")


if __name__ == "__main__":
    main()
