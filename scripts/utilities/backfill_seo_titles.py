#!/usr/bin/env python3
"""
Backfill SEO metadata for existing dreamweaving records.

This script fetches all dreamweavings from the API and generates
optimized SEO titles using the new seo_title_generator module.

Usage:
  # Dry run (preview changes without updating)
  python3 scripts/utilities/backfill_seo_titles.py --dry-run

  # Execute backfill
  python3 scripts/utilities/backfill_seo_titles.py --execute

  # Backfill specific slug only
  python3 scripts/utilities/backfill_seo_titles.py --execute --slug my-session-slug
"""

import argparse
import json
import os
import sys
import time
from typing import Optional

import requests
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.core.seo_title_generator import generate_seo_metadata

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.environ.get("SALARSU_API_URL", "https://www.salars.net")
API_TOKEN = os.environ.get("SALARSU_API_TOKEN") or os.environ.get("DREAMWEAVING_API_TOKEN")


def fetch_all_dreamweavings(limit: int = 500) -> list:
    """Fetch all dreamweavings from API."""
    url = f"{API_URL}/api/dreamweavings?limit={limit}&status=published"

    headers = {}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("dreamweavings", [])
    except requests.RequestException as e:
        print(f"Error fetching dreamweavings: {e}")
        return []


def update_seo(slug: str, seo_data: dict) -> tuple[bool, str]:
    """Update SEO data for a dreamweaving.

    Returns:
        (success, message) tuple
    """
    url = f"{API_URL}/api/dreamweavings/{slug}"

    headers = {
        "Content-Type": "application/json",
    }
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"

    payload = {"seo": seo_data}

    try:
        response = requests.patch(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            return True, "Updated"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"
    except requests.RequestException as e:
        return False, f"Request error: {e}"


def backfill_dreamweaving(dw: dict, dry_run: bool = True) -> dict:
    """Generate and optionally apply SEO metadata for a dreamweaving.

    Returns:
        Result dict with slug, old_title, new_title, success, message
    """
    slug = dw.get("slug", "unknown")
    title = dw.get("title", "")
    description = dw.get("description", "")
    category = dw.get("category", "")

    # Check if SEO already exists
    existing_seo = dw.get("seo", {})
    if existing_seo and existing_seo.get("meta_title"):
        return {
            "slug": slug,
            "old_title": title[:60],
            "new_title": existing_seo.get("meta_title"),
            "skipped": True,
            "message": "SEO already exists"
        }

    # Generate optimized SEO
    seo = generate_seo_metadata(
        full_title=title,
        topic=description,
        category=category,
        slug=slug,
    )

    result = {
        "slug": slug,
        "old_title": title[:60] + ("..." if len(title) > 60 else ""),
        "new_title": seo["meta_title"],
        "new_title_len": len(seo["meta_title"]),
        "h1_title": seo["h1_title"],
        "sku": seo["sku"],
    }

    if dry_run:
        result["dry_run"] = True
        result["message"] = "Would update"
    else:
        success, message = update_seo(slug, seo)
        result["success"] = success
        result["message"] = message

    return result


def main():
    parser = argparse.ArgumentParser(description="Backfill SEO titles for dreamweavings")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without updating database"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually update the database"
    )
    parser.add_argument(
        "--slug",
        type=str,
        help="Only update a specific slug"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Maximum number of dreamweavings to fetch"
    )

    args = parser.parse_args()

    # Require explicit --dry-run or --execute
    if not args.dry_run and not args.execute:
        print("Error: Must specify --dry-run or --execute")
        print("Use --dry-run to preview changes first")
        sys.exit(1)

    if not API_TOKEN:
        print("Warning: No API token found. Updates will likely fail.")
        print("Set SALARSU_API_TOKEN or DREAMWEAVING_API_TOKEN environment variable.")
        if args.execute:
            print("Aborting execution mode without token.")
            sys.exit(1)

    dry_run = args.dry_run

    print("=" * 70)
    print(f"SEO Title Backfill {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
    print("=" * 70)
    print(f"API URL: {API_URL}")
    print(f"Token: {'Set' if API_TOKEN else 'NOT SET'}")
    print()

    # Fetch dreamweavings
    print("Fetching dreamweavings...")
    dreamweavings = fetch_all_dreamweavings(args.limit)

    if not dreamweavings:
        print("No dreamweavings found!")
        sys.exit(1)

    print(f"Found {len(dreamweavings)} dreamweavings")
    print()

    # Filter to specific slug if requested
    if args.slug:
        dreamweavings = [dw for dw in dreamweavings if dw.get("slug") == args.slug]
        if not dreamweavings:
            print(f"No dreamweaving found with slug: {args.slug}")
            sys.exit(1)

    # Process each dreamweaving
    results = {
        "updated": 0,
        "skipped": 0,
        "failed": 0,
        "details": []
    }

    for i, dw in enumerate(dreamweavings):
        result = backfill_dreamweaving(dw, dry_run=dry_run)

        # Print progress
        status = "SKIP" if result.get("skipped") else ("OK" if result.get("success", True) else "FAIL")
        if dry_run and not result.get("skipped"):
            status = "PREVIEW"

        print(f"[{i+1}/{len(dreamweavings)}] [{status}] {result['slug']}")
        print(f"    Original: {result['old_title']}")
        if not result.get("skipped"):
            print(f"    SEO ({result.get('new_title_len', 0)} chars): {result['new_title']}")
        print(f"    {result.get('message', '')}")
        print()

        # Track results
        if result.get("skipped"):
            results["skipped"] += 1
        elif result.get("success", True) or dry_run:
            results["updated"] += 1
        else:
            results["failed"] += 1

        results["details"].append(result)

        # Rate limiting for actual updates
        if not dry_run and not result.get("skipped"):
            time.sleep(0.5)  # Avoid overwhelming the API

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total processed: {len(dreamweavings)}")
    print(f"Updated: {results['updated']}")
    print(f"Skipped (already have SEO): {results['skipped']}")
    print(f"Failed: {results['failed']}")

    if dry_run:
        print()
        print("This was a DRY RUN. No changes were made.")
        print("Run with --execute to apply changes.")

    # Exit with error if any failures
    if results["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
