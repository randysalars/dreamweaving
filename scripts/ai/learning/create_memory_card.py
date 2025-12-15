#!/usr/bin/env python3
"""
Create Memory Card - Auto-generate memory cards for incident tracking.

Creates structured memory cards in .ai/memory/ when incidents are resolved
or significant lessons are learned.

Usage:
    python3 scripts/ai/learning/create_memory_card.py \
        --title "Silent Audio After Mix" \
        --category audio \
        --keywords "mix,silent,stems,levels" \
        --symptom "Output audio was silent after mixing" \
        --root-cause "Stems not normalized before mixing" \
        --fix "Check dtype before conversion in mixer.py:82" \
        --session garden-of-eden

Categories:
    audio, ssml, video, api, deployment, theme, validation, build, code, content
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
MEMORY_DIR = PROJECT_ROOT / ".ai" / "memory"
INDEX_FILE = MEMORY_DIR / "INDEX.md"
TEMPLATE_FILE = MEMORY_DIR / "TEMPLATE.md"

# Valid categories
VALID_CATEGORIES = [
    "audio", "ssml", "video", "api", "deployment",
    "theme", "validation", "build", "code", "content"
]


def slugify(title: str) -> str:
    """Convert title to slug for filename."""
    # Convert to lowercase
    slug = title.lower()
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    # Limit length
    return slug[:50]


def generate_filename(category: str, title: str) -> str:
    """Generate memory card filename: YYYY-MM-DD__category-title.md"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    title_slug = slugify(title)
    return f"{date_str}__{category}-{title_slug}.md"


def generate_memory_card(
    title: str,
    category: str,
    keywords: List[str],
    symptom: str,
    root_cause: str,
    fix: str,
    session: Optional[str] = None,
    verification: Optional[str] = None,
    prevention: Optional[str] = None,
    files_changed: Optional[List[str]] = None,
    related_memories: Optional[List[str]] = None,
    notes: Optional[str] = None
) -> str:
    """Generate memory card content from parameters."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    keywords_str = ", ".join(keywords)

    # Build verification section
    verification_content = verification or "```bash\n# Run relevant tests or validation\n```\n\nVerify the issue no longer occurs."

    # Build prevention section
    prevention_items = []
    if prevention:
        prevention_items.append(f"- [x] {prevention}")
    else:
        prevention_items.append("- [ ] Test added: (if applicable)")
        prevention_items.append("- [ ] Validation added: (if applicable)")
        prevention_items.append("- [ ] Documentation updated: (if applicable)")
    prevention_content = "\n".join(prevention_items)

    # Build links section
    links = []
    if session:
        links.append(f"- **Session:** `sessions/{session}/`")
    if files_changed:
        for file_path in files_changed:
            links.append(f"- **File:** `{file_path}`")
    if related_memories:
        for memory in related_memories:
            links.append(f"- **Related memory:** `.ai/memory/{memory}`")
    links_content = "\n".join(links) if links else "- (Add relevant links)"

    # Build notes section
    notes_content = notes or "(Additional context if needed)"

    content = f"""# {title}

**Date:** {date_str}
**Category:** {category}
**Keywords:** {keywords_str}

---

## Symptom

{symptom}

---

## Root Cause

{root_cause}

---

## Fix Pattern

{fix}

---

## Verification

{verification_content}

---

## Prevention

{prevention_content}

---

## Links

{links_content}

---

## Notes

{notes_content}
"""
    return content


def update_index(filename: str, title: str, category: str, keywords: List[str]) -> None:
    """Add entry to INDEX.md."""
    if not INDEX_FILE.exists():
        print(f"Warning: INDEX.md not found at {INDEX_FILE}")
        return

    # Read current index
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Create new entry
    date_str = datetime.now().strftime("%Y-%m-%d")
    keywords_str = ", ".join(keywords)
    new_entry = f"| [{title}]({filename}) | {category} | {keywords_str} | {date_str} |"

    # Find the table and insert entry
    # Look for the table header pattern
    table_pattern = r"(\| Memory \| Category \| Keywords \| Date \|\n\|[-| ]+\|)"

    if re.search(table_pattern, content):
        # Insert after table header
        content = re.sub(
            table_pattern,
            r"\1\n" + new_entry,
            content
        )
    else:
        # Append to end if table not found
        content += f"\n\n## Recent Entries\n\n| Memory | Category | Keywords | Date |\n|--------|----------|----------|------|\n{new_entry}\n"

    # Write updated index
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Updated INDEX.md with new entry")


def update_trigger_maps(keywords: List[str], filename: str) -> None:
    """Update TRIGGER_MAPS.md with new keywords."""
    trigger_maps_path = PROJECT_ROOT / ".ai" / "TRIGGER_MAPS.md"

    if not trigger_maps_path.exists():
        print(f"Note: TRIGGER_MAPS.md not found, skipping keyword update")
        return

    # Read current trigger maps
    with open(trigger_maps_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if keywords are already present
    missing_keywords = [kw for kw in keywords if kw.lower() not in content.lower()]

    if missing_keywords:
        # Add note about new keywords at the end
        note = f"\n\n<!-- New keywords from {filename}: {', '.join(missing_keywords)} -->\n"
        with open(trigger_maps_path, "a", encoding="utf-8") as f:
            f.write(note)
        print(f"Added keyword note to TRIGGER_MAPS.md")


def main():
    parser = argparse.ArgumentParser(
        description="Create a memory card for incident tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--title", "-t",
        required=True,
        help="Short descriptive title for the memory card"
    )
    parser.add_argument(
        "--category", "-c",
        required=True,
        choices=VALID_CATEGORIES,
        help="Category for the memory card"
    )
    parser.add_argument(
        "--keywords", "-k",
        required=True,
        help="Comma-separated keywords for searching"
    )
    parser.add_argument(
        "--symptom", "-s",
        required=True,
        help="What was observed (error message, behavior)"
    )
    parser.add_argument(
        "--root-cause", "-r",
        required=True,
        help="The underlying reason for the issue"
    )
    parser.add_argument(
        "--fix", "-f",
        required=True,
        help="The exact solution applied"
    )
    parser.add_argument(
        "--session",
        help="Related session name (optional)"
    )
    parser.add_argument(
        "--verification",
        help="How to confirm the fix worked (optional)"
    )
    parser.add_argument(
        "--prevention",
        help="What was added to prevent recurrence (optional)"
    )
    parser.add_argument(
        "--files",
        help="Comma-separated list of files changed (optional)"
    )
    parser.add_argument(
        "--related",
        help="Comma-separated list of related memory filenames (optional)"
    )
    parser.add_argument(
        "--notes",
        help="Additional context or notes (optional)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print card content without saving"
    )
    parser.add_argument(
        "--no-index",
        action="store_true",
        help="Don't update INDEX.md"
    )

    args = parser.parse_args()

    # Parse keywords
    keywords = [k.strip() for k in args.keywords.split(",")]

    # Parse optional lists
    files_changed = [f.strip() for f in args.files.split(",")] if args.files else None
    related_memories = [m.strip() for m in args.related.split(",")] if args.related else None

    # Generate filename
    filename = generate_filename(args.category, args.title)
    filepath = MEMORY_DIR / filename

    # Generate content
    content = generate_memory_card(
        title=args.title,
        category=args.category,
        keywords=keywords,
        symptom=args.symptom,
        root_cause=args.root_cause,
        fix=args.fix,
        session=args.session,
        verification=args.verification,
        prevention=args.prevention,
        files_changed=files_changed,
        related_memories=related_memories,
        notes=args.notes
    )

    if args.dry_run:
        print(f"Would create: {filepath}")
        print("-" * 60)
        print(content)
        print("-" * 60)
        return

    # Ensure memory directory exists
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    # Check for existing file
    if filepath.exists():
        print(f"Warning: File already exists: {filepath}")
        response = input("Overwrite? [y/N]: ")
        if response.lower() != "y":
            print("Aborted")
            sys.exit(1)

    # Write memory card
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Created memory card: {filepath}")

    # Update index
    if not args.no_index:
        update_index(filename, args.title, args.category, keywords)
        update_trigger_maps(keywords, filename)

    print("\nMemory card created successfully!")
    print(f"  File: {filepath}")
    print(f"  Category: {args.category}")
    print(f"  Keywords: {', '.join(keywords)}")


if __name__ == "__main__":
    main()
