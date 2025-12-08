#!/usr/bin/env python3
"""
Session Cleanup Module

Removes intermediate files while preserving final deliverables.
This is Stage 8 of the production workflow.

Files PRESERVED:
- output/youtube_package/* (final YouTube package)
- output/video/session_final.mp4 (final video)
- output/*_MASTER.mp3 (final mastered audio)
- manifest.yaml
- working_files/script*.ssml
- images/uploaded/* (source images)

Files REMOVED:
- output/*.wav (intermediate audio stems)
- output/voice.mp3 (raw TTS, enhanced version exists)
- output/video/solid_background.mp4 (generated fallback)
- output/video/video_summary.json (metadata, not needed for delivery)
- working_files/*.json (intermediate configs)

Usage:
    python3 scripts/core/cleanup_session.py sessions/{session}/
    python3 scripts/core/cleanup_session.py sessions/{session}/ --dry-run
"""

import argparse
import sys
from pathlib import Path


def format_size(bytes_size: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def cleanup_session(session_path: Path, dry_run: bool = False) -> dict:
    """
    Clean up intermediate files from a session.

    Returns dict with cleanup statistics.
    """
    if not session_path.exists():
        print(f"Session not found: {session_path}")
        return {"error": "Session not found"}

    output_path = session_path / "output"
    if not output_path.exists():
        print(f"No output directory found in {session_path}")
        return {"error": "No output directory"}

    youtube_pkg = output_path / "youtube_package"
    youtube_pkg.mkdir(parents=True, exist_ok=True)

    # Track what we're doing
    files_to_remove = []
    bytes_to_free = 0
    preserved_files = []

    # Files/patterns to remove from output/
    output_remove_patterns = [
        "*.wav",           # All WAV intermediates (including MASTER.wav if MP3 exists)
        "voice.mp3",       # Raw TTS (keep enhanced only if no MASTER)
        "voice_enhanced.mp3",  # Keep only MASTER
    ]

    # Move any YouTube package files into youtube_package/ before cleanup
    # so they are never deleted by pattern matching.
    for yt_file in output_path.glob("YOUTUBE_*.md"):
        target = youtube_pkg / yt_file.name
        if target.exists():
            # Keep existing copy; remove stray duplicate in output/
            yt_file.unlink()
        else:
            yt_file.rename(target)
        preserved_files.append(target)

    # Check if MASTER.mp3 exists (then we can remove MASTER.wav too)
    master_mp3_exists = list(output_path.glob("*_MASTER.mp3"))

    # Check output/ directory
    for pattern in output_remove_patterns:
        for file_path in output_path.glob(pattern):
            # Handle MASTER files specially
            if "_MASTER" in file_path.name:
                # Keep MASTER.mp3, remove MASTER.wav if MP3 exists
                if file_path.suffix == ".mp3":
                    preserved_files.append(file_path)
                    continue
                elif file_path.suffix == ".wav" and master_mp3_exists:
                    # Remove WAV since MP3 exists
                    files_to_remove.append(file_path)
                    bytes_to_free += file_path.stat().st_size
                    continue
                else:
                    # Keep WAV if no MP3
                    preserved_files.append(file_path)
                    continue

            # Skip voice files if no MASTER exists (fallback)
            if file_path.name in ("voice.mp3", "voice_enhanced.mp3"):
                if not master_mp3_exists:
                    preserved_files.append(file_path)
                    continue

            files_to_remove.append(file_path)
            bytes_to_free += file_path.stat().st_size

    # Check output/video/ for intermediates
    video_path = output_path / "video"
    if video_path.exists():
        video_remove_patterns = [
            "solid_background.mp4",
            "background_gradient.mp4",
            "video_summary.json",
            "*_audio.mp3",
            "*_audio.aac",
        ]
        for pattern in video_remove_patterns:
            for file_path in video_path.glob(pattern):
                files_to_remove.append(file_path)
                bytes_to_free += file_path.stat().st_size

        # Preserve session_final.mp4
        final_video = video_path / "session_final.mp4"
        if final_video.exists():
            preserved_files.append(final_video)

    # Check working_files/ for large intermediates
    working_path = session_path / "working_files"
    if working_path.exists():
        working_remove_patterns = [
            "*.wav",       # Audio intermediates
            "*.mp3",       # Audio intermediates
        ]
        for pattern in working_remove_patterns:
            for file_path in working_path.glob(pattern):
                files_to_remove.append(file_path)
                bytes_to_free += file_path.stat().st_size

    # Report
    print("=" * 60)
    print("SESSION CLEANUP - STAGE 8")
    print("=" * 60)
    print(f"\nSession: {session_path.name}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print()

    # Show what will be preserved
    print("PRESERVED (Final Deliverables):")
    if youtube_pkg.exists():
        pkg_size = sum(f.stat().st_size for f in youtube_pkg.rglob("*") if f.is_file())
        print(f"  youtube_package/ ({format_size(pkg_size)})")
        for f in sorted(youtube_pkg.iterdir()):
            print(f"    - {f.name}")

    for f in preserved_files:
        if f.is_file():
            print(f"  {f.relative_to(session_path)} ({format_size(f.stat().st_size)})")

    print()
    print("TO BE REMOVED (Intermediates):")
    if not files_to_remove:
        print("  (none - session already clean)")
    else:
        for f in files_to_remove:
            print(f"  {f.relative_to(session_path)} ({format_size(f.stat().st_size)})")

    print()
    print("-" * 60)
    print(f"Space to free: {format_size(bytes_to_free)}")
    print("-" * 60)

    # Execute removal
    if not dry_run and files_to_remove:
        print("\nRemoving files...")
        removed_count = 0
        for f in files_to_remove:
            try:
                f.unlink()
                removed_count += 1
            except Exception as e:
                print(f"  Failed to remove {f.name}: {e}")

        print(f"\nRemoved {removed_count} files, freed {format_size(bytes_to_free)}")
    elif dry_run:
        print("\n(Dry run - no files removed)")

    print()
    print("=" * 60)
    print("CLEANUP COMPLETE")
    print("=" * 60)

    # Calculate final size
    if not dry_run:
        final_size = sum(f.stat().st_size for f in session_path.rglob("*") if f.is_file())
        print(f"\nFinal session size: {format_size(final_size)}")

    return {
        "files_removed": len(files_to_remove) if not dry_run else 0,
        "bytes_freed": bytes_to_free if not dry_run else 0,
        "files_preserved": len(preserved_files),
        "dry_run": dry_run
    }


def main():
    parser = argparse.ArgumentParser(
        description="Clean up intermediate files from a session (Stage 8)"
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

    args = parser.parse_args()

    session_path = Path(args.session).resolve()
    result = cleanup_session(session_path, dry_run=args.dry_run)

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
