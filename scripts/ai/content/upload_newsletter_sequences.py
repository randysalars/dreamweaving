#!/usr/bin/env python3
"""
Upload Newsletter Sequences to Admin API

Reads generated JSON sequence files and uploads them to the salars.net admin API.

Usage:
    python3 scripts/ai/content/upload_newsletter_sequences.py --all
    python3 scripts/ai/content/upload_newsletter_sequences.py --category dreamweavings
    python3 scripts/ai/content/upload_newsletter_sequences.py --dry-run
"""

import argparse
import json
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
NEWSLETTERS_DIR = PROJECT_ROOT / "output" / "newsletters"

# API Configuration
DEFAULT_API_BASE = os.getenv("SALARSU_API_BASE", "https://www.salars.net")


def load_sequence_file(filepath: Path) -> dict:
    """Load a newsletter sequence JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def upload_email(email: dict, api_base: str, api_token: str, dry_run: bool = False) -> bool:
    """Upload a single email to the API"""
    url = f"{api_base}/api/admin/newsletters/content"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }

    payload = {
        "category_slug": email["category_slug"],
        "subject": email["subject"],
        "preview_text": email["preview_text"],
        "body_html": email["body_html"],
        "body_text": email["body_text"],
        "sequence_order": email["sequence_order"],
        "delay_days": email["delay_days"],
        "status": email.get("status", "draft")
    }

    if dry_run:
        print(f"    [DRY RUN] Would upload: {email['subject'][:50]}...")
        return True

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            return True
        else:
            print(f"    API Error {response.status_code}: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"    Upload error: {e}")
        return False


def upload_sequence(filepath: Path, api_base: str, api_token: str, dry_run: bool = False) -> tuple[int, int]:
    """Upload all emails from a sequence file"""
    data = load_sequence_file(filepath)
    category = data.get("category_slug", "unknown")
    emails = data.get("emails", [])

    print(f"\nUploading {category} ({len(emails)} emails)...")

    success = 0
    failed = 0

    for email in emails:
        if upload_email(email, api_base, api_token, dry_run):
            success += 1
            print(f"  [{email['sequence_order']}/10] {email['subject'][:40]}... OK")
        else:
            failed += 1
            print(f"  [{email['sequence_order']}/10] {email['subject'][:40]}... FAILED")

    return success, failed


def get_sequence_files(newsletters_dir: Path, category: str = None) -> list[Path]:
    """Get list of sequence files to upload"""
    if category:
        filepath = newsletters_dir / f"{category}_sequence.json"
        if filepath.exists():
            return [filepath]
        else:
            print(f"File not found: {filepath}")
            return []
    else:
        return sorted(newsletters_dir.glob("*_sequence.json"))


def main():
    parser = argparse.ArgumentParser(
        description="Upload newsletter sequences to admin API"
    )
    parser.add_argument(
        "--category", "-c",
        help="Upload a specific category (e.g., dreamweavings, health)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Upload all categories"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be uploaded without actually uploading"
    )
    parser.add_argument(
        "--api-base",
        default=DEFAULT_API_BASE,
        help="API base URL"
    )
    parser.add_argument(
        "--newsletters-dir",
        default=str(NEWSLETTERS_DIR),
        help="Directory containing newsletter JSON files"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available sequence files"
    )

    args = parser.parse_args()

    newsletters_dir = Path(args.newsletters_dir)

    # List mode
    if args.list:
        print("\nAvailable newsletter sequence files:")
        for f in sorted(newsletters_dir.glob("*_sequence.json")):
            data = load_sequence_file(f)
            print(f"  {f.stem}: {data.get('category_name', 'Unknown')} ({data.get('generated_count', 0)} emails)")
        return

    # Validate args
    if not args.category and not args.all:
        parser.print_help()
        print("\nError: Specify --category <slug> or --all")
        return

    # Get API token
    api_token = os.getenv("SALARSU_API_TOKEN")
    if not api_token and not args.dry_run:
        print("Error: SALARSU_API_TOKEN environment variable not set")
        print("Set it with: export SALARSU_API_TOKEN=your-token-here")
        return

    # Get files to upload
    files = get_sequence_files(newsletters_dir, args.category if args.category else None)

    if not files:
        print("No sequence files found to upload")
        return

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Uploading to: {args.api_base}")
    print(f"Files to process: {len(files)}")

    # Upload
    total_success = 0
    total_failed = 0

    for filepath in files:
        success, failed = upload_sequence(
            filepath,
            args.api_base,
            api_token,
            args.dry_run
        )
        total_success += success
        total_failed += failed

    # Summary
    print("\n" + "=" * 50)
    print("UPLOAD COMPLETE" if not args.dry_run else "DRY RUN COMPLETE")
    print("=" * 50)
    print(f"Categories processed: {len(files)}")
    print(f"Emails {'would be ' if args.dry_run else ''}uploaded: {total_success}")
    if total_failed > 0:
        print(f"Failures: {total_failed}")


if __name__ == "__main__":
    main()
