#!/usr/bin/env python3
"""
Seed dreamweaving categories into the database.

This script reads the master category configuration from config/categories.yaml
and inserts or updates categories in the Neon PostgreSQL database.

Usage:
    python3 scripts/utilities/seed_categories.py
    python3 scripts/utilities/seed_categories.py --dry-run
    python3 scripts/utilities/seed_categories.py --sql-only > categories.sql

Options:
    --dry-run       Show what would be done without making changes
    --sql-only      Output SQL statements instead of executing them
    --api           Use API endpoint instead of direct database access

Environment Variables:
    DATABASE_URL    PostgreSQL connection string (for direct DB access)
    SALARSU_API_TOKEN   API token (for API mode)
"""

import argparse
import json
import os
import sys
import yaml
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def load_categories_config() -> dict:
    """Load category configuration from YAML file."""
    config_path = PROJECT_ROOT / "config" / "categories.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Categories config not found: {config_path}")

    with open(config_path) as f:
        return yaml.safe_load(f)


def generate_category_id(slug: str) -> str:
    """Generate a CUID-like ID for a category."""
    import hashlib
    import time

    # Create a deterministic but unique-looking ID
    timestamp = "cm4f"  # CUID prefix
    hash_input = f"{slug}-{int(time.time())}"
    hash_suffix = hashlib.sha256(hash_input.encode()).hexdigest()[:20]
    return f"{timestamp}{hash_suffix}"


def flatten_keywords(keywords: dict) -> list:
    """Flatten primary and secondary keywords into a single list."""
    flat = []
    if isinstance(keywords, dict):
        flat.extend(keywords.get("primary", []))
        flat.extend(keywords.get("secondary", []))
    elif isinstance(keywords, list):
        flat = keywords
    return flat


def category_to_sql(category: dict, parent_id: str = None) -> str:
    """Convert a category dict to an SQL INSERT/UPDATE statement."""
    cat_id = category.get("id", generate_category_id(category["slug"]))
    name = category["name"].replace("'", "''")
    slug = category["slug"]
    description = (category.get("description", "") or "").replace("'", "''")
    color = category.get("color", "#8B5CF6")
    icon = category.get("icon", "")
    priority = category.get("priority", 100)
    page_source = category.get("page_source", "")
    keywords = flatten_keywords(category.get("keywords", {}))
    keywords_array = "ARRAY[" + ", ".join(f"'{k}'" for k in keywords) + "]::TEXT[]" if keywords else "'{}'::TEXT[]"
    parent_sql = f"'{parent_id}'" if parent_id else "NULL"

    return f"""
INSERT INTO dreamweaving_categories (id, name, slug, description, color, icon, priority, page_source, keywords, parent_id, display_order, created_at, updated_at)
VALUES ('{cat_id}', '{name}', '{slug}', '{description}', '{color}', '{icon}', {priority}, '{page_source}', {keywords_array}, {parent_sql}, {priority}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    color = EXCLUDED.color,
    icon = EXCLUDED.icon,
    priority = EXCLUDED.priority,
    page_source = EXCLUDED.page_source,
    keywords = EXCLUDED.keywords,
    parent_id = EXCLUDED.parent_id,
    display_order = EXCLUDED.display_order,
    updated_at = CURRENT_TIMESTAMP;
"""


def generate_all_sql(config: dict) -> str:
    """Generate all SQL statements for seeding categories."""
    statements = []
    statements.append("-- Category Seeding Script")
    statements.append("-- Generated from config/categories.yaml")
    statements.append("")

    # Core categories
    statements.append("-- Core Categories (from /dreamweavings/types)")
    for cat in config.get("core_categories", []):
        statements.append(category_to_sql(cat))

    # Extended categories
    statements.append("\n-- Extended Categories (from /dreamweavings/more)")
    for cat in config.get("extended_categories", []):
        statements.append(category_to_sql(cat))

    # Theme categories
    statements.append("\n-- Theme-based Categories")
    for cat in config.get("theme_categories", []):
        statements.append(category_to_sql(cat))

    # Growth categories
    statements.append("\n-- Growth Experience Categories")
    for cat in config.get("growth_categories", []):
        statements.append(category_to_sql(cat))

    # Verification
    statements.append("\n-- Verify")
    statements.append("SELECT slug, name, priority, page_source, array_length(keywords, 1) as keyword_count FROM dreamweaving_categories ORDER BY priority;")

    return "\n".join(statements)


def seed_via_api(config: dict, dry_run: bool = False) -> None:
    """Seed categories via the API endpoint."""
    import requests

    api_url = os.environ.get("SALARSU_API_URL", "https://www.salars.net")
    api_token = os.environ.get("SALARSU_API_TOKEN") or os.environ.get("DREAMWEAVING_API_TOKEN")

    if not api_token:
        raise ValueError("Missing API token (set SALARSU_API_TOKEN)")

    all_categories = []
    all_categories.extend(config.get("core_categories", []))
    all_categories.extend(config.get("extended_categories", []))
    all_categories.extend(config.get("theme_categories", []))
    all_categories.extend(config.get("growth_categories", []))

    print(f"Seeding {len(all_categories)} categories via API...")

    for cat in all_categories:
        payload = {
            "id": cat.get("id"),
            "name": cat["name"],
            "slug": cat["slug"],
            "description": cat.get("description", ""),
            "color": cat.get("color", "#8B5CF6"),
            "icon": cat.get("icon", ""),
            "priority": cat.get("priority", 100),
            "page_source": cat.get("page_source", ""),
            "keywords": flatten_keywords(cat.get("keywords", {})),
        }

        if dry_run:
            print(f"  [DRY RUN] Would upsert: {cat['slug']}")
            continue

        response = requests.post(
            f"{api_url}/api/dreamweavings/categories",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        if response.status_code in [200, 201]:
            print(f"  OK: {cat['slug']}")
        else:
            print(f"  ERROR: {cat['slug']} - {response.status_code}: {response.text}")


def seed_via_database(config: dict, dry_run: bool = False) -> None:
    """Seed categories directly to database."""
    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 not installed. Use --sql-only or --api mode instead.")
        print("  Install with: pip install psycopg2-binary")
        sys.exit(1)

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("Missing DATABASE_URL environment variable")

    sql = generate_all_sql(config)

    if dry_run:
        print("[DRY RUN] Would execute SQL:")
        print(sql)
        return

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    try:
        cur.execute(sql)
        conn.commit()
        print("Categories seeded successfully!")

        # Show results
        cur.execute("""
            SELECT slug, name, priority, page_source, array_length(keywords, 1) as keyword_count
            FROM dreamweaving_categories
            ORDER BY priority
        """)
        rows = cur.fetchall()

        print(f"\nSeeded {len(rows)} categories:")
        for row in rows:
            print(f"  {row[0]}: {row[1]} (priority={row[2]}, source={row[3]}, keywords={row[4]})")

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Seed dreamweaving categories to database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 seed_categories.py --sql-only > categories.sql
  python3 seed_categories.py --dry-run
  python3 seed_categories.py --api
        """
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--sql-only", action="store_true", help="Output SQL only")
    parser.add_argument("--api", action="store_true", help="Use API instead of direct DB")

    args = parser.parse_args()

    # Load configuration
    config = load_categories_config()

    total = (
        len(config.get("core_categories", [])) +
        len(config.get("extended_categories", [])) +
        len(config.get("theme_categories", [])) +
        len(config.get("growth_categories", []))
    )

    print(f"Loaded {total} categories from config/categories.yaml")

    if args.sql_only:
        print(generate_all_sql(config))
        return

    if args.api:
        seed_via_api(config, dry_run=args.dry_run)
    else:
        seed_via_database(config, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
