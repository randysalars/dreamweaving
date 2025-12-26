#!/usr/bin/env python3
"""
Upload Newsletter Sequences via Cron Endpoint

Uses the /api/cron/seed-newsletters endpoint which accepts cron token auth.

Usage:
    python3 scripts/ai/content/upload_via_cron.py --all
    python3 scripts/ai/content/upload_via_cron.py --category dreamweavings
"""

import argparse
import json
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
NEWSLETTERS_DIR = PROJECT_ROOT / "output" / "newsletters"

API_BASE = os.getenv("SALARSU_API_URL", "https://www.salars.net")
API_TOKEN = os.getenv("SALARSU_API_TOKEN")


def load_sequence_file(filepath: Path) -> dict:
    with open(filepath, 'r') as f:
        return json.load(f)


def upload_category(filepath: Path, dry_run: bool = False) -> tuple[int, int, int]:
    data = load_sequence_file(filepath)
    category_slug = data.get("category_slug")
    emails = data.get("emails", [])

    print(f"\nUploading {category_slug} ({len(emails)} emails)...")

    if dry_run:
        print(f"  [DRY RUN] Would upload {len(emails)} emails")
        return len(emails), 0, 0

    url = f"{API_BASE}/api/cron/seed-newsletters?token={API_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "category_slug": category_slug,
        "emails": emails
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=120)

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                created = result.get("created", 0)
                updated = result.get("updated", 0)
                errors = result.get("errors", [])
                print(f"  Created: {created}, Updated: {updated}")
                if errors:
                    print(f"  Errors: {len(errors)}")
                    for e in errors:
                        print(f"    - Seq {e['sequence_order']}: {e['error']}")
                return created, updated, len(errors)
            else:
                print(f"  API Error: {result.get('error', 'Unknown')}")
                return 0, 0, len(emails)
        elif response.status_code == 401:
            print(f"  Auth failed: Invalid token")
            return 0, 0, len(emails)
        else:
            print(f"  HTTP {response.status_code}: {response.text[:200]}")
            return 0, 0, len(emails)

    except Exception as e:
        print(f"  Request error: {e}")
        return 0, 0, len(emails)


def get_sequence_files(category: str = None) -> list[Path]:
    if category:
        filepath = NEWSLETTERS_DIR / f"{category}_sequence.json"
        return [filepath] if filepath.exists() else []
    return sorted(NEWSLETTERS_DIR.glob("*_sequence.json"))


def main():
    parser = argparse.ArgumentParser(description="Upload newsletters via cron endpoint")
    parser.add_argument("--category", "-c", help="Specific category to upload")
    parser.add_argument("--all", "-a", action="store_true", help="Upload all categories")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show without uploading")
    args = parser.parse_args()

    if not args.category and not args.all:
        parser.print_help()
        print("\nError: Specify --category <slug> or --all")
        return

    if not API_TOKEN and not args.dry_run:
        print("Error: SALARSU_API_TOKEN not set")
        return

    files = get_sequence_files(args.category if args.category else None)
    if not files:
        print("No sequence files found")
        return

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Uploading to: {API_BASE}")
    print(f"Files: {len(files)}")

    total_created = 0
    total_updated = 0
    total_errors = 0

    for filepath in files:
        created, updated, errors = upload_category(filepath, args.dry_run)
        total_created += created
        total_updated += updated
        total_errors += errors

    print("\n" + "=" * 50)
    print("UPLOAD COMPLETE" if not args.dry_run else "DRY RUN COMPLETE")
    print("=" * 50)
    print(f"Categories: {len(files)}")
    print(f"Created: {total_created}")
    print(f"Updated: {total_updated}")
    if total_errors:
        print(f"Errors: {total_errors}")


if __name__ == "__main__":
    main()
