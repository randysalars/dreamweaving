#!/usr/bin/env python3
"""
Stock Image License Validation Utility

Validates that all images in a session's images/uploaded/ directory have
corresponding license records in license_manifest.yaml.

Features:
- Checks all PNGs/JPGs have license entries
- Validates no CC BY-NC (non-commercial) images
- Warns about images with people or logos
- Checks attribution block exists for CC BY images
- Generates compliance report

Usage:
    python scripts/utilities/validate_image_licenses.py sessions/{session}/
    python scripts/utilities/validate_image_licenses.py sessions/{session}/ --strict
    python scripts/utilities/validate_image_licenses.py --all  # Check all sessions

Exit codes:
    0 = All checks passed
    1 = Warnings found (non-strict mode)
    2 = Errors found (missing licenses, prohibited content)
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)


# ANSI color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def color(text: str, color_code: str) -> str:
    """Apply color to text if stdout is a terminal."""
    if sys.stdout.isatty():
        return f"{color_code}{text}{Colors.END}"
    return text


def load_manifest(manifest_path: Path) -> Optional[dict]:
    """Load and parse the license manifest YAML."""
    if not manifest_path.exists():
        return None

    try:
        with open(manifest_path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(color(f"ERROR: Invalid YAML in {manifest_path}: {e}", Colors.RED))
        return None


def get_image_files(uploaded_dir: Path) -> set:
    """Get all image files in the uploaded directory."""
    extensions = {'.png', '.jpg', '.jpeg', '.webp'}
    if not uploaded_dir.exists():
        return set()

    return {
        f.name for f in uploaded_dir.iterdir()
        if f.is_file() and f.suffix.lower() in extensions
    }


def validate_session(session_dir: Path, strict: bool = False) -> tuple[list, list]:
    """
    Validate image licenses for a session.

    Returns:
        (errors: list[str], warnings: list[str])
    """
    errors = []
    warnings = []

    manifest_path = session_dir / "images" / "license_manifest.yaml"
    uploaded_dir = session_dir / "images" / "uploaded"

    # Check manifest exists
    if not manifest_path.exists():
        # Only error if there are actual images
        image_files = get_image_files(uploaded_dir)
        if image_files:
            errors.append(f"No license_manifest.yaml found but {len(image_files)} images exist")
            errors.append(f"  Create manifest at: {manifest_path}")
        return errors, warnings

    # Load manifest
    manifest = load_manifest(manifest_path)
    if manifest is None:
        errors.append("Failed to parse license_manifest.yaml")
        return errors, warnings

    # Get tracked and actual images
    images_list = manifest.get('images', []) or []
    tracked = {img.get('filename') for img in images_list if img.get('filename')}
    actual = get_image_files(uploaded_dir)

    # Check for untracked images
    untracked = actual - tracked
    if untracked:
        for img in sorted(untracked):
            errors.append(f"UNTRACKED: {img} has no license record")

    # Check for orphaned records (tracked but file missing)
    orphaned = tracked - actual
    if orphaned:
        for img in sorted(orphaned):
            warnings.append(f"ORPHANED: License record exists for missing file: {img}")

    # Validate each tracked image
    cc_by_images = []

    for img in images_list:
        if not img:
            continue

        filename = img.get('filename', 'UNKNOWN')
        license_info = img.get('license', {})
        content = img.get('content', {})
        source = img.get('source', {})

        # Check for prohibited license types
        license_type = license_info.get('type', '').lower()
        if 'nc' in license_type or license_type == 'cc_by_nc':
            errors.append(f"PROHIBITED: {filename} uses non-commercial license ({license_type})")

        # Check for commercial use flag
        if license_info.get('commercial_use') is False:
            errors.append(f"PROHIBITED: {filename} is marked as non-commercial")

        # Track CC BY images that need attribution
        if license_info.get('attribution_required'):
            cc_by_images.append(filename)

        # Warn about people in images
        if content.get('has_people'):
            if strict:
                errors.append(f"PEOPLE: {filename} contains people (model release risk)")
            else:
                warnings.append(f"PEOPLE: {filename} contains people (verify model release)")

        # Warn about logos in images
        if content.get('has_logos'):
            if strict:
                errors.append(f"LOGOS: {filename} contains logos/brands (trademark risk)")
            else:
                warnings.append(f"LOGOS: {filename} contains logos/brands (verify usage rights)")

        # Check for missing source URL
        if not source.get('url'):
            warnings.append(f"MISSING URL: {filename} has no source URL recorded")

        # Check for missing retrieval date
        if not license_info.get('retrieved_date'):
            warnings.append(f"MISSING DATE: {filename} has no retrieval date")

    # Check attribution credits exist if CC BY images used
    if cc_by_images:
        attribution = manifest.get('attribution_credits', '')
        if not attribution or attribution.strip().startswith('#'):
            errors.append(f"ATTRIBUTION REQUIRED: {len(cc_by_images)} CC BY images need credits block")
            for img in cc_by_images:
                errors.append(f"  - {img}")

    return errors, warnings


def print_report(session_name: str, errors: list, warnings: list) -> None:
    """Print validation report for a session."""
    print(f"\n{color('=' * 60, Colors.BLUE)}")
    print(color(f"Session: {session_name}", Colors.BOLD))
    print(color('=' * 60, Colors.BLUE))

    if not errors and not warnings:
        print(color("✓ All license checks passed", Colors.GREEN))
        return

    if errors:
        print(color(f"\n✗ ERRORS ({len(errors)}):", Colors.RED))
        for err in errors:
            print(color(f"  • {err}", Colors.RED))

    if warnings:
        print(color(f"\n⚠ WARNINGS ({len(warnings)}):", Colors.YELLOW))
        for warn in warnings:
            print(color(f"  • {warn}", Colors.YELLOW))


def main():
    parser = argparse.ArgumentParser(
        description="Validate stock image licenses for dreamweaving sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s sessions/eden-garden/
    %(prog)s sessions/eden-garden/ --strict
    %(prog)s --all
    %(prog)s --all --strict
        """
    )
    parser.add_argument(
        'session_dir',
        nargs='?',
        type=Path,
        help='Path to session directory'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate all sessions in sessions/ directory'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors (fail on people/logos)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Only output errors, not warnings'
    )

    args = parser.parse_args()

    # Determine sessions to check
    sessions_to_check = []

    if args.all:
        # Find all sessions
        sessions_root = Path('sessions')
        if not sessions_root.exists():
            sessions_root = Path(__file__).parent.parent.parent / 'sessions'

        if sessions_root.exists():
            for session_dir in sorted(sessions_root.iterdir()):
                if session_dir.is_dir() and not session_dir.name.startswith('_'):
                    sessions_to_check.append(session_dir)
        else:
            print(color("ERROR: Could not find sessions/ directory", Colors.RED))
            sys.exit(2)
    elif args.session_dir:
        session_dir = args.session_dir
        if not session_dir.exists():
            print(color(f"ERROR: Session directory not found: {session_dir}", Colors.RED))
            sys.exit(2)
        sessions_to_check.append(session_dir)
    else:
        parser.print_help()
        sys.exit(1)

    # Validate sessions
    total_errors = 0
    total_warnings = 0

    for session_dir in sessions_to_check:
        errors, warnings = validate_session(session_dir, strict=args.strict)

        if not args.quiet or errors:
            print_report(session_dir.name, errors, warnings if not args.quiet else [])

        total_errors += len(errors)
        total_warnings += len(warnings)

    # Summary
    print(f"\n{color('=' * 60, Colors.BLUE)}")
    print(color("SUMMARY", Colors.BOLD))
    print(color('=' * 60, Colors.BLUE))
    print(f"Sessions checked: {len(sessions_to_check)}")

    if total_errors:
        print(color(f"Total errors: {total_errors}", Colors.RED))
    else:
        print(color("Total errors: 0", Colors.GREEN))

    if total_warnings:
        print(color(f"Total warnings: {total_warnings}", Colors.YELLOW))

    # Exit code
    if total_errors:
        sys.exit(2)
    elif total_warnings and args.strict:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
