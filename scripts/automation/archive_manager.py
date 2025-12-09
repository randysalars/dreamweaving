#!/usr/bin/env python3
"""
Archive Manager

Moves uploaded sessions to archive folder to save disk space.

Sessions are archived after successful YouTube upload.

Usage:
    # Archive all uploaded sessions
    python -m scripts.automation.archive_manager

    # Archive specific session
    python -m scripts.automation.archive_manager --session my-session

    # Dry run
    python -m scripts.automation.archive_manager --dry-run

    # Show sessions pending archive
    python -m scripts.automation.archive_manager --pending
"""

import argparse
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ArchiveManager:
    """Manages archiving of uploaded sessions."""

    def __init__(self, config: Dict[str, Any], db):
        """Initialize archive manager.

        Args:
            config: Configuration dictionary
            db: StateDatabase instance
        """
        self.config = config
        self.db = db

        self.archive_dir = Path(config['archive']['archive_dir'])
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        self.sessions_dir = Path(__file__).parent.parent.parent / 'sessions'

    def archive_session(
        self,
        session_name: str,
        dry_run: bool = False
    ) -> bool:
        """Archive a single session.

        Moves session folder from sessions/ to archive/.

        Args:
            session_name: Session identifier
            dry_run: If True, don't actually move files

        Returns:
            True on success
        """
        session_path = self.sessions_dir / session_name
        archive_path = self.archive_dir / session_name

        if not session_path.exists():
            logger.warning(f"Session not found: {session_path}")
            return False

        if archive_path.exists():
            logger.warning(f"Archive already exists: {archive_path}")
            # Could merge or skip - for now, skip
            return False

        logger.info(f"Archiving: {session_name}")
        logger.info(f"  From: {session_path}")
        logger.info(f"  To: {archive_path}")

        if dry_run:
            logger.info("  [DRY RUN] Would move session")
            return True

        try:
            # Move entire folder
            shutil.move(str(session_path), str(archive_path))

            # Update database
            self.db.mark_archived(session_name, str(archive_path))

            logger.info(f"  Archived successfully")
            return True

        except Exception as e:
            logger.error(f"  Failed to archive: {e}")
            return False

    def archive_all_uploaded(self, dry_run: bool = False) -> Dict[str, Any]:
        """Archive all sessions that have been uploaded to YouTube.

        Args:
            dry_run: If True, don't actually move files

        Returns:
            Summary dict with counts
        """
        sessions = self.db.get_sessions_to_archive()

        if not sessions:
            logger.info("No sessions to archive")
            return {'total': 0, 'archived': 0, 'failed': 0}

        logger.info(f"Found {len(sessions)} sessions to archive")

        archived = 0
        failed = 0

        for session in sessions:
            session_name = session['session_name']
            success = self.archive_session(session_name, dry_run)
            if success:
                archived += 1
            else:
                failed += 1

        return {
            'total': len(sessions),
            'archived': archived,
            'failed': failed,
        }

    def get_pending_archive(self) -> List[Dict[str, Any]]:
        """Get sessions pending archive.

        Returns:
            List of session dicts
        """
        return self.db.get_sessions_to_archive()

    def get_archive_stats(self) -> Dict[str, Any]:
        """Get archive statistics.

        Returns:
            Dict with archive stats
        """
        # Count archived sessions
        archived_count = len(list(self.archive_dir.iterdir())) if self.archive_dir.exists() else 0

        # Calculate archive size
        archive_size = 0
        if self.archive_dir.exists():
            for path in self.archive_dir.rglob('*'):
                if path.is_file():
                    archive_size += path.stat().st_size

        # Count active sessions
        active_count = len(list(self.sessions_dir.iterdir())) if self.sessions_dir.exists() else 0

        # Active sessions size
        active_size = 0
        if self.sessions_dir.exists():
            for path in self.sessions_dir.rglob('*'):
                if path.is_file():
                    active_size += path.stat().st_size

        return {
            'archived_sessions': archived_count,
            'archive_size_gb': round(archive_size / (1024**3), 2),
            'active_sessions': active_count,
            'active_size_gb': round(active_size / (1024**3), 2),
            'archive_dir': str(self.archive_dir),
        }

    def restore_session(
        self,
        session_name: str,
        dry_run: bool = False
    ) -> bool:
        """Restore an archived session back to active.

        Args:
            session_name: Session identifier
            dry_run: If True, don't actually move files

        Returns:
            True on success
        """
        archive_path = self.archive_dir / session_name
        session_path = self.sessions_dir / session_name

        if not archive_path.exists():
            logger.error(f"Archived session not found: {archive_path}")
            return False

        if session_path.exists():
            logger.error(f"Active session already exists: {session_path}")
            return False

        logger.info(f"Restoring: {session_name}")

        if dry_run:
            logger.info("  [DRY RUN] Would restore session")
            return True

        try:
            shutil.move(str(archive_path), str(session_path))

            # Update database
            self.db.update(
                session_name,
                archived=0,
                archived_at=None,
                archive_path=None,
                session_path=str(session_path),
            )

            logger.info(f"  Restored successfully")
            return True

        except Exception as e:
            logger.error(f"  Failed to restore: {e}")
            return False

    def cleanup_incomplete(self, dry_run: bool = False) -> int:
        """Clean up incomplete/failed sessions from active directory.

        Removes sessions with:
        - generation_status = 'failed'
        - No video file
        - Older than 7 days

        Args:
            dry_run: If True, don't delete files

        Returns:
            Number of sessions cleaned up
        """
        sessions = self.db.query("""
            SELECT session_name, session_path, created_at
            FROM sessions
            WHERE generation_status = 'failed'
              AND archived = 0
              AND created_at < datetime('now', '-7 days')
        """)

        if not sessions:
            logger.info("No incomplete sessions to clean up")
            return 0

        logger.info(f"Found {len(sessions)} incomplete sessions to clean up")

        cleaned = 0
        for session in sessions:
            session_name = session['session_name']
            session_path = Path(session['session_path']) if session['session_path'] else None

            if session_path and session_path.exists():
                logger.info(f"Cleaning up: {session_name}")

                if dry_run:
                    logger.info("  [DRY RUN] Would remove session")
                else:
                    try:
                        shutil.rmtree(session_path)
                        logger.info("  Removed")
                        cleaned += 1
                    except Exception as e:
                        logger.error(f"  Failed to remove: {e}")

        return cleaned


def main():
    """Main entry point."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from scripts.automation.config_loader import load_config, setup_logging
    from scripts.automation.state_db import StateDatabase

    parser = argparse.ArgumentParser(description='Archive Manager')
    parser.add_argument('--session', type=str, help='Archive specific session')
    parser.add_argument('--dry-run', action='store_true', help='Dry run')
    parser.add_argument('--pending', action='store_true', help='Show pending archives')
    parser.add_argument('--stats', action='store_true', help='Show archive stats')
    parser.add_argument('--restore', type=str, help='Restore archived session')
    parser.add_argument('--cleanup', action='store_true', help='Clean up failed sessions')
    parser.add_argument('--config', type=str, help='Config file path')

    args = parser.parse_args()

    config = load_config(Path(args.config) if args.config else None)
    setup_logging(config)

    db = StateDatabase(Path(config['database']['path']))
    db.init_schema()

    manager = ArchiveManager(config, db)

    if args.stats:
        print("\n=== Archive Statistics ===")
        stats = manager.get_archive_stats()
        print(f"Archive directory: {stats['archive_dir']}")
        print(f"Archived sessions: {stats['archived_sessions']}")
        print(f"Archive size: {stats['archive_size_gb']} GB")
        print(f"Active sessions: {stats['active_sessions']}")
        print(f"Active size: {stats['active_size_gb']} GB")

    elif args.pending:
        print("\n=== Sessions Pending Archive ===")
        pending = manager.get_pending_archive()
        if not pending:
            print("No sessions pending archive")
        else:
            for session in pending:
                print(f"  - {session['session_name']}")
            print(f"\nTotal: {len(pending)}")

    elif args.restore:
        success = manager.restore_session(args.restore, args.dry_run)
        if success:
            print(f"Restored: {args.restore}")
        else:
            print(f"Failed to restore: {args.restore}")

    elif args.cleanup:
        cleaned = manager.cleanup_incomplete(args.dry_run)
        print(f"Cleaned up {cleaned} incomplete sessions")

    elif args.session:
        success = manager.archive_session(args.session, args.dry_run)
        if success:
            print(f"Archived: {args.session}")
        else:
            print(f"Failed to archive: {args.session}")

    else:
        # Archive all uploaded
        result = manager.archive_all_uploaded(args.dry_run)
        print(f"\n=== Archive Results ===")
        print(f"Total: {result['total']}")
        print(f"Archived: {result['archived']}")
        print(f"Failed: {result['failed']}")

    db.close()


if __name__ == '__main__':
    main()
