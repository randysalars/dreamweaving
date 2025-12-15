#!/usr/bin/env python3
"""
Session Cleanup Module

Removes ALL files except the YouTube package for maximum space savings.
This is Stage 8 of the production workflow.

Files PRESERVED:
- output/youtube_package/* (final YouTube package with video, audio, thumbnail, VTT)
- manifest.yaml (session configuration)

Files REMOVED (everything else):
- output/*.wav, *.mp3 (all intermediate and master audio)
- output/video/* (intermediate video files)
- working_files/* (all working files - scripts, configs, prompts)
- images/* (all images - they're embedded in video or in youtube_package)
- All other intermediate files

Usage:
    python3 scripts/core/cleanup_session.py sessions/{session}/
    python3 scripts/core/cleanup_session.py sessions/{session}/ --dry-run
    python3 scripts/core/cleanup_session.py sessions/{session}/ --keep-scripts  # Also preserve SSML scripts
"""

import argparse
import shutil
import sys
from pathlib import Path


def format_size(bytes_size: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def get_dir_size(path: Path) -> int:
    """Get total size of a directory."""
    if not path.exists():
        return 0
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def cleanup_session(session_path: Path, dry_run: bool = False, keep_scripts: bool = False, aggressive: bool = False) -> dict:
    """
    Aggressively clean up a session, keeping only youtube_package and manifest.

    Args:
        session_path: Path to session directory
        dry_run: If True, show what would be removed without removing
        keep_scripts: If True, also preserve SSML scripts in working_files
        aggressive: If True, remove EVERYTHING including youtube_package and manifest (nightly mode)

    Returns:
        dict with cleanup statistics
    """
    if not session_path.exists():
        print(f"Session not found: {session_path}")
        return {"error": "Session not found"}

    output_path = session_path / "output"
    youtube_pkg = output_path / "youtube_package"

    # In aggressive mode, we don't require youtube_package
    if not aggressive and not youtube_pkg.exists():
        print(f"WARNING: No youtube_package found in {session_path}")
        print("This session may not be ready for cleanup.")
        return {"error": "No youtube_package found"}

    # Calculate initial size
    initial_size = get_dir_size(session_path)

    # Track what we're doing
    items_to_remove = []  # (path, size, type)
    bytes_to_free = 0
    preserved_items = []

    # In aggressive mode, remove EVERYTHING - no preserves
    if aggressive:
        # Remove entire output directory
        if output_path.exists():
            size = get_dir_size(output_path)
            items_to_remove.append((output_path, size, "dir"))
            bytes_to_free += size

        # Remove manifest.yaml
        manifest_file = session_path / "manifest.yaml"
        if manifest_file.exists():
            size = manifest_file.stat().st_size
            items_to_remove.append((manifest_file, size, "file"))
            bytes_to_free += size

        # Remove working_files entirely
        working_path = session_path / "working_files"
        if working_path.exists():
            size = get_dir_size(working_path)
            items_to_remove.append((working_path, size, "dir"))
            bytes_to_free += size

        # Remove images entirely
        images_path = session_path / "images"
        if images_path.exists():
            size = get_dir_size(images_path)
            items_to_remove.append((images_path, size, "dir"))
            bytes_to_free += size

        # Remove any other files/dirs in session root
        for item in session_path.iterdir():
            if item in [p for p, _, _ in items_to_remove]:
                continue  # Already added
            if item.name.startswith("."):
                continue  # Skip hidden files
            if item.is_file():
                size = item.stat().st_size
                items_to_remove.append((item, size, "file"))
                bytes_to_free += size
            elif item.is_dir():
                size = get_dir_size(item)
                items_to_remove.append((item, size, "dir"))
                bytes_to_free += size
    else:
        # Standard mode: preserve youtube_package and manifest
        if youtube_pkg.exists():
            preserved_items.append(("output/youtube_package/", get_dir_size(youtube_pkg)))
        if (session_path / "manifest.yaml").exists():
            preserved_items.append(("manifest.yaml", (session_path / "manifest.yaml").stat().st_size))

        # Optionally preserve scripts
        if keep_scripts:
            working_path = session_path / "working_files"
            if working_path.exists():
                for ssml_file in working_path.glob("*.ssml"):
                    preserved_items.append((f"working_files/{ssml_file.name}", ssml_file.stat().st_size))

        # Remove everything in output/ EXCEPT youtube_package
        if output_path.exists():
            for item in output_path.iterdir():
                if item.name == "youtube_package":
                    continue  # Preserve

                if item.is_file():
                    size = item.stat().st_size
                    items_to_remove.append((item, size, "file"))
                    bytes_to_free += size
                elif item.is_dir():
                    size = get_dir_size(item)
                    items_to_remove.append((item, size, "dir"))
                    bytes_to_free += size

        # Remove working_files/ (except scripts if --keep-scripts)
        working_path = session_path / "working_files"
        if working_path.exists():
            if keep_scripts:
                # Remove everything except *.ssml
                for item in working_path.iterdir():
                    if item.is_file() and item.suffix == ".ssml":
                        continue  # Preserve
                    if item.is_file():
                        size = item.stat().st_size
                        items_to_remove.append((item, size, "file"))
                        bytes_to_free += size
                    elif item.is_dir():
                        size = get_dir_size(item)
                        items_to_remove.append((item, size, "dir"))
                        bytes_to_free += size
            else:
                # Remove entire directory
                size = get_dir_size(working_path)
                items_to_remove.append((working_path, size, "dir"))
                bytes_to_free += size

        # Remove images/
        images_path = session_path / "images"
        if images_path.exists():
            size = get_dir_size(images_path)
            items_to_remove.append((images_path, size, "dir"))
            bytes_to_free += size

        # Remove any stray large files in session root
        for item in session_path.iterdir():
            if item.name in ("manifest.yaml", "output", "working_files", "images"):
                continue  # Already handled
            if item.name.startswith("."):
                continue  # Skip hidden files

            if item.is_file():
                # Remove large files (> 1MB), keep small ones like notes
                if item.stat().st_size > 1_000_000:
                    size = item.stat().st_size
                    items_to_remove.append((item, size, "file"))
                    bytes_to_free += size
                else:
                    preserved_items.append((item.name, item.stat().st_size))
            elif item.is_dir():
                # Remove any other directories
                size = get_dir_size(item)
                items_to_remove.append((item, size, "dir"))
                bytes_to_free += size

    # Report
    print("=" * 60)
    mode_label = "NIGHTLY/AGGRESSIVE" if aggressive else "STANDARD"
    print(f"SESSION CLEANUP - {mode_label} MODE")
    print("=" * 60)
    print(f"\nSession: {session_path.name}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Initial size: {format_size(initial_size)}")
    print()

    # Show what will be preserved
    print("PRESERVED:")
    for name, size in preserved_items:
        print(f"  {name} ({format_size(size)})")

    print()
    print("TO BE REMOVED:")
    if not items_to_remove:
        print("  (none - session already clean)")
    else:
        # Group by type for cleaner output
        dirs_to_remove = [(p, s) for p, s, t in items_to_remove if t == "dir"]
        files_to_remove = [(p, s) for p, s, t in items_to_remove if t == "file"]

        if dirs_to_remove:
            print("  Directories:")
            for path, size in dirs_to_remove:
                rel_path = path.relative_to(session_path)
                print(f"    {rel_path}/ ({format_size(size)})")

        if files_to_remove:
            print("  Files:")
            # Show first 10, summarize rest
            for path, size in files_to_remove[:10]:
                rel_path = path.relative_to(session_path)
                print(f"    {rel_path} ({format_size(size)})")
            if len(files_to_remove) > 10:
                remaining = len(files_to_remove) - 10
                remaining_size = sum(s for _, s in files_to_remove[10:])
                print(f"    ... and {remaining} more files ({format_size(remaining_size)})")

    print()
    print("-" * 60)
    print(f"Space to free: {format_size(bytes_to_free)}")
    expected_final = initial_size - bytes_to_free
    print(f"Expected final size: {format_size(expected_final)}")
    savings_pct = (bytes_to_free / initial_size * 100) if initial_size > 0 else 0
    print(f"Space savings: {savings_pct:.1f}%")
    print("-" * 60)

    # Execute removal
    if not dry_run and items_to_remove:
        print("\nRemoving files...")
        removed_count = 0
        errors = []

        for path, size, item_type in items_to_remove:
            try:
                if item_type == "dir":
                    shutil.rmtree(path)
                else:
                    path.unlink()
                removed_count += 1
            except Exception as e:
                errors.append(f"{path.name}: {e}")

        if errors:
            print("\nErrors:")
            for err in errors:
                print(f"  {err}")

        print(f"\nRemoved {removed_count} items, freed {format_size(bytes_to_free)}")
    elif dry_run:
        print("\n(Dry run - no files removed)")

    print()
    print("=" * 60)
    print("CLEANUP COMPLETE")
    print("=" * 60)

    # Calculate final size
    if not dry_run:
        final_size = get_dir_size(session_path)
        actual_freed = initial_size - final_size
        print(f"\nFinal session size: {format_size(final_size)}")
        print(f"Actual space freed: {format_size(actual_freed)}")

    return {
        "items_removed": len(items_to_remove) if not dry_run else 0,
        "bytes_freed": bytes_to_free if not dry_run else 0,
        "items_preserved": len(preserved_items),
        "dry_run": dry_run,
        "initial_size": initial_size,
        "expected_final_size": initial_size - bytes_to_free
    }


def main():
    parser = argparse.ArgumentParser(
        description="Aggressively clean up session, keeping only youtube_package (Stage 8)"
    )
    parser.add_argument(
        "session",
        help="Path to session directory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing"
    )
    parser.add_argument(
        "--keep-scripts",
        action="store_true",
        help="Also preserve SSML scripts in working_files/"
    )
    parser.add_argument(
        "--aggressive",
        action="store_true",
        help="Remove EVERYTHING including youtube_package and manifest (for nightly builds)"
    )

    args = parser.parse_args()

    session_path = Path(args.session).resolve()
    result = cleanup_session(session_path, dry_run=args.dry_run, keep_scripts=args.keep_scripts, aggressive=args.aggressive)

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
