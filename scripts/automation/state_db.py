#!/usr/bin/env python3
"""
State Database Manager

SQLite database for tracking:
- Generated sessions and their status
- Upload history (YouTube, website)
- Analytics cache for optimal timing
- Quality scores

Usage:
    from scripts.automation.state_db import StateDatabase

    db = StateDatabase()
    db.init_schema()

    # Create a new session
    db.create_session('my-session', 'My Topic', 'notion-id-123')

    # Update status
    db.update_status('my-session', 'generating')
    db.mark_complete('my-session', '/path/to/session', '/path/to/video.mp4', 85.5)

    # Query sessions
    next_upload = db.get_next_upload(strategy='quality')
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Default database path
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'automation_state.db'


class StateDatabase:
    """SQLite state management for the automation pipeline."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file. Defaults to data/automation_state.db
        """
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._connect()

    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ==================== Schema Management ====================

    def init_schema(self):
        """Initialize database schema (create tables if not exist)."""
        cursor = self.conn.cursor()

        # Sessions table - main tracking for generated sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT UNIQUE NOT NULL,
                topic TEXT NOT NULL,
                notion_topic_id TEXT,

                -- Generation
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                generation_status TEXT DEFAULT 'pending',
                generation_error TEXT,
                generation_duration_seconds INTEGER,

                -- Paths
                session_path TEXT,
                video_path TEXT,
                audio_path TEXT,
                thumbnail_path TEXT,

                -- Quality metrics
                quality_score REAL,
                audio_lufs REAL,
                video_duration_seconds INTEGER,
                script_word_count INTEGER,

                -- YouTube upload
                uploaded_to_youtube INTEGER DEFAULT 0,
                youtube_video_id TEXT,
                youtube_uploaded_at TIMESTAMP,
                analytics_fetched_at TIMESTAMP,

                -- Website upload
                uploaded_to_website INTEGER DEFAULT 0,
                website_url TEXT,

                -- Shorts
                shorts_created INTEGER DEFAULT 0,
                shorts_path TEXT,
                shorts_uploaded INTEGER DEFAULT 0,
                shorts_youtube_id TEXT,
                shorts_uploaded_at TIMESTAMP,

                -- Archive
                archived INTEGER DEFAULT 0,
                archived_at TIMESTAMP,
                archive_path TEXT,

                -- Priority (manual override)
                priority INTEGER DEFAULT 0
            )
        """)

        # Upload history - audit trail
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS upload_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                upload_type TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                video_id TEXT,
                url TEXT,
                success INTEGER DEFAULT 1,
                error_message TEXT,
                FOREIGN KEY (session_name) REFERENCES sessions(session_name)
            )
        """)

        # Analytics cache - store YouTube analytics for optimal timing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                optimal_long_upload_time TEXT,
                optimal_shorts_upload_time TEXT,
                best_day_of_week INTEGER,
                analytics_json TEXT
            )
        """)

        # Used topics tracking - prevent reuse of topics from text files
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS used_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_text TEXT NOT NULL,
                source_file TEXT NOT NULL,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_name TEXT,
                UNIQUE(topic_text, source_file)
            )
        """)

        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_status
            ON sessions(generation_status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_youtube
            ON sessions(uploaded_to_youtube)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_quality
            ON sessions(quality_score DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_used_topics_file
            ON used_topics(source_file, used_at DESC)
        """)

        self.conn.commit()
        logger.info(f"Database schema initialized at {self.db_path}")

    # ==================== Session Management ====================

    def create_session(
        self,
        session_name: str,
        topic: str,
        notion_topic_id: Optional[str] = None
    ) -> int:
        """Create a new session record.

        Args:
            session_name: Unique session identifier (slug)
            topic: Topic/title from Notion
            notion_topic_id: Notion page ID for reference

        Returns:
            Session ID
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (session_name, topic, notion_topic_id, generation_status)
            VALUES (?, ?, ?, 'pending')
        """, (session_name, topic, notion_topic_id))
        self.conn.commit()
        logger.info(f"Created session: {session_name}")
        return cursor.lastrowid

    def update_status(self, session_name: str, status: str, error: Optional[str] = None):
        """Update generation status.

        Args:
            session_name: Session identifier
            status: New status (pending, generating, complete, failed)
            error: Error message if failed
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE sessions
            SET generation_status = ?, generation_error = ?
            WHERE session_name = ?
        """, (status, error, session_name))
        self.conn.commit()
        logger.debug(f"Updated {session_name} status to {status}")

    def mark_complete(
        self,
        session_name: str,
        session_path: str,
        video_path: str,
        quality_score: float,
        duration_seconds: Optional[int] = None,
        audio_path: Optional[str] = None,
        thumbnail_path: Optional[str] = None,
        audio_lufs: Optional[float] = None,
        video_duration_seconds: Optional[int] = None,
        script_word_count: Optional[int] = None
    ):
        """Mark session generation as complete with all metadata.

        Args:
            session_name: Session identifier
            session_path: Full path to session directory
            video_path: Path to final video file
            quality_score: Computed quality score (0-100)
            duration_seconds: Generation time in seconds
            audio_path: Path to master audio file
            thumbnail_path: Path to thumbnail image
            audio_lufs: Audio loudness in LUFS
            video_duration_seconds: Video length in seconds
            script_word_count: Number of words in script
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE sessions
            SET generation_status = 'complete',
                session_path = ?,
                video_path = ?,
                quality_score = ?,
                generation_duration_seconds = ?,
                audio_path = ?,
                thumbnail_path = ?,
                audio_lufs = ?,
                video_duration_seconds = ?,
                script_word_count = ?
            WHERE session_name = ?
        """, (
            session_path, video_path, quality_score, duration_seconds,
            audio_path, thumbnail_path, audio_lufs, video_duration_seconds,
            script_word_count, session_name
        ))
        self.conn.commit()
        logger.info(f"Marked {session_name} as complete (score: {quality_score:.1f})")

    def mark_failed(self, session_name: str, error: str):
        """Mark session generation as failed.

        Args:
            session_name: Session identifier
            error: Error message/traceback
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE sessions
            SET generation_status = 'failed',
                generation_error = ?
            WHERE session_name = ?
        """, (error[:5000], session_name))  # Truncate error to 5000 chars
        self.conn.commit()
        logger.error(f"Marked {session_name} as failed: {error[:200]}")

    def get_session(self, session_name: str) -> Optional[Dict[str, Any]]:
        """Get session by name.

        Args:
            session_name: Session identifier

        Returns:
            Session dict or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session_name = ?", (session_name,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def session_exists(self, session_name: str) -> bool:
        """Check if session exists.

        Args:
            session_name: Session identifier

        Returns:
            True if session exists
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT 1 FROM sessions WHERE session_name = ?",
            (session_name,)
        )
        return cursor.fetchone() is not None

    # ==================== Upload Management ====================

    def get_next_upload(self, strategy: str = 'quality') -> Optional[Dict[str, Any]]:
        """Get next session to upload to YouTube.

        Args:
            strategy: Selection strategy
                - 'quality': Highest quality score first
                - 'fifo': Oldest generated first
                - 'priority': Manual priority then quality

        Returns:
            Session dict or None if queue is empty
        """
        cursor = self.conn.cursor()

        if strategy == 'priority':
            # Priority override, then quality
            cursor.execute("""
                SELECT * FROM sessions
                WHERE uploaded_to_youtube = 0
                  AND generation_status = 'complete'
                  AND video_path IS NOT NULL
                ORDER BY priority DESC, quality_score DESC, created_at ASC
                LIMIT 1
            """)
        elif strategy == 'fifo':
            # First in, first out
            cursor.execute("""
                SELECT * FROM sessions
                WHERE uploaded_to_youtube = 0
                  AND generation_status = 'complete'
                  AND video_path IS NOT NULL
                ORDER BY created_at ASC
                LIMIT 1
            """)
        else:  # quality (default)
            cursor.execute("""
                SELECT * FROM sessions
                WHERE uploaded_to_youtube = 0
                  AND generation_status = 'complete'
                  AND video_path IS NOT NULL
                ORDER BY quality_score DESC, created_at ASC
                LIMIT 1
            """)

        row = cursor.fetchone()
        return dict(row) if row else None

    def mark_youtube_uploaded(self, session_name: str, video_id: str):
        """Mark session as uploaded to YouTube.

        Args:
            session_name: Session identifier
            video_id: YouTube video ID
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE sessions
            SET uploaded_to_youtube = 1,
                youtube_video_id = ?,
                youtube_uploaded_at = ?
            WHERE session_name = ?
        """, (video_id, datetime.now().isoformat(), session_name))
        self.conn.commit()
        logger.info(f"Marked {session_name} as uploaded to YouTube: {video_id}")

    def mark_website_uploaded(self, session_name: str, website_url: str):
        """Mark session as uploaded to website.

        Args:
            session_name: Session identifier
            website_url: Full URL on salars.net
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE sessions
            SET uploaded_to_website = 1,
                website_url = ?
            WHERE session_name = ?
        """, (website_url, session_name))
        self.conn.commit()
        logger.info(f"Marked {session_name} as uploaded to website: {website_url}")

    def log_upload(
        self,
        session_name: str,
        upload_type: str,
        video_id: Optional[str] = None,
        url: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log an upload attempt to history.

        Args:
            session_name: Session identifier
            upload_type: Type of upload (youtube_long, youtube_short, website)
            video_id: Video ID if applicable
            url: URL of uploaded content
            success: Whether upload succeeded
            error_message: Error message if failed
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO upload_history
                (session_name, upload_type, video_id, url, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_name, upload_type, video_id, url, 1 if success else 0, error_message))
        self.conn.commit()

    # ==================== Shorts Management ====================

    def get_shorts_candidate(self) -> Optional[Dict[str, Any]]:
        """Get next session eligible for shorts creation.

        Criteria:
        - Uploaded to website (has content to link to)
        - NOT uploaded to YouTube (website-only content)
        - Shorts not yet created
        - Has video file

        Returns:
            Session dict or None if no candidates
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM sessions
            WHERE uploaded_to_website = 1
              AND uploaded_to_youtube = 0
              AND shorts_uploaded = 0
              AND video_path IS NOT NULL
              AND generation_status = 'complete'
            ORDER BY quality_score DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        return dict(row) if row else None

    def mark_shorts_created(self, session_name: str, shorts_path: str):
        """Mark shorts video as created.

        Args:
            session_name: Session identifier
            shorts_path: Path to shorts video file
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE sessions
            SET shorts_created = 1,
                shorts_path = ?
            WHERE session_name = ?
        """, (shorts_path, session_name))
        self.conn.commit()
        logger.info(f"Marked shorts created for {session_name}")

    def mark_shorts_uploaded(self, session_name: str, video_id: str):
        """Mark shorts as uploaded to YouTube.

        Args:
            session_name: Session identifier
            video_id: YouTube video ID for short
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE sessions
            SET shorts_uploaded = 1,
                shorts_youtube_id = ?,
                shorts_uploaded_at = ?
            WHERE session_name = ?
        """, (video_id, datetime.now().isoformat(), session_name))
        self.conn.commit()
        logger.info(f"Marked shorts uploaded for {session_name}: {video_id}")

    # ==================== Used Topics Management ====================

    def is_topic_used(self, topic_text: str, source_file: str) -> bool:
        """Check if a topic has already been used.
        
        Args:
            topic_text: The topic string
            source_file: Source file path or identifier
            
        Returns:
            True if topic was already used
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM used_topics
            WHERE topic_text = ? AND source_file = ?
        """, (topic_text, source_file))
        count = cursor.fetchone()[0]
        return count > 0

    def mark_topic_used(self, topic_text: str, source_file: str, session_name: str):
        """Mark a topic as used.
        
        Args:
            topic_text: The topic string
            source_file: Source file path or identifier  
            session_name: Associated session name
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO used_topics (topic_text, source_file, session_name)
                VALUES (?, ?, ?)
            """, (topic_text, source_file, session_name))
            self.conn.commit()
            logger.info(f"Marked topic as used: {topic_text} from {source_file}")
        except sqlite3.IntegrityError:
            # Topic already marked as used, that's fine
            logger.debug(f"Topic already marked as used: {topic_text}")

    def get_unused_topics(self, all_topics: List[str], source_file: str) -> List[str]:
        """Filter out already-used topics from a list.
        
        Args:
            all_topics: List of all available topics
            source_file: Source file identifier
            
        Returns:
            List of unused topics
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT topic_text FROM used_topics
            WHERE source_file = ?
        """, (source_file,))
        used = {row['topic_text'] for row in cursor.fetchall()}
        return [t for t in all_topics if t not in used]

    def reset_used_topics(self, source_file: Optional[str] = None):
        """Reset used topics (clear the tracking table).
        
        Args:
            source_file: If provided, only reset topics from this file.
                        If None, reset all topics.
        """
        cursor = self.conn.cursor()
        if source_file:
            cursor.execute("""
                DELETE FROM used_topics WHERE source_file = ?
            """, (source_file,))
            logger.info(f"Reset used topics for: {source_file}")
        else:
            cursor.execute("DELETE FROM used_topics")
            logger.info("Reset all used topics")
        self.conn.commit()

    def get_used_topics_count(self, source_file: str) -> int:
        """Get count of used topics from a source file.
        
        Args:
            source_file: Source file identifier
            
        Returns:
            Count of used topics
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM used_topics
            WHERE source_file = ?
        """, (source_file,))
        return cursor.fetchone()[0]

    # ==================== Archive Management ====================

    def get_sessions_to_archive(self) -> List[Dict[str, Any]]:
        """Get sessions ready for archiving.

        Criteria:
        - Uploaded to YouTube
        - Not yet archived

        Returns:
            List of session dicts
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM sessions
            WHERE uploaded_to_youtube = 1
              AND archived = 0
        """)
        return [dict(row) for row in cursor.fetchall()]

    def mark_archived(self, session_name: str, archive_path: str):
        """Mark session as archived.

        Args:
            session_name: Session identifier
            archive_path: Path in archive directory
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE sessions
            SET archived = 1,
                archived_at = ?,
                archive_path = ?
            WHERE session_name = ?
        """, (datetime.now().isoformat(), archive_path, session_name))
        self.conn.commit()
        logger.info(f"Marked {session_name} as archived: {archive_path}")

    # ==================== Analytics Cache ====================

    def save_analytics(
        self,
        optimal_long_time: str,
        optimal_shorts_time: str,
        best_day: int,
        analytics_json: str
    ):
        """Save YouTube analytics data.

        Args:
            optimal_long_time: Best time for long uploads (HH:MM MST)
            optimal_shorts_time: Best time for shorts uploads (HH:MM MST)
            best_day: Best day of week (0=Monday, 6=Sunday)
            analytics_json: Full analytics data as JSON string
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO analytics_cache
                (optimal_long_upload_time, optimal_shorts_upload_time,
                 best_day_of_week, analytics_json)
            VALUES (?, ?, ?, ?)
        """, (optimal_long_time, optimal_shorts_time, best_day, analytics_json))
        self.conn.commit()
        logger.info(f"Saved analytics: long={optimal_long_time}, shorts={optimal_shorts_time}")

    def get_latest_analytics(self) -> Optional[Dict[str, Any]]:
        """Get most recent analytics data.

        Returns:
            Analytics dict or None if no data
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM analytics_cache
            ORDER BY fetched_at DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        return dict(row) if row else None

    # ==================== Utility Methods ====================

    def update(self, session_name: str, **kwargs):
        """Generic update method for session fields.

        Args:
            session_name: Session identifier
            **kwargs: Field=value pairs to update
        """
        if not kwargs:
            return

        fields = ', '.join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [session_name]

        cursor = self.conn.cursor()
        cursor.execute(f"""
            UPDATE sessions
            SET {fields}
            WHERE session_name = ?
        """, values)
        self.conn.commit()

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute raw SQL query.

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            List of result dicts
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        """Get automation statistics.

        Returns:
            Dict with counts and metrics
        """
        cursor = self.conn.cursor()

        stats = {}

        # Session counts by status
        cursor.execute("""
            SELECT generation_status, COUNT(*) as count
            FROM sessions
            GROUP BY generation_status
        """)
        stats['by_status'] = {row['generation_status']: row['count'] for row in cursor.fetchall()}

        # Upload counts
        cursor.execute("SELECT COUNT(*) FROM sessions WHERE uploaded_to_youtube = 1")
        stats['youtube_uploads'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM sessions WHERE uploaded_to_website = 1")
        stats['website_uploads'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM sessions WHERE shorts_uploaded = 1")
        stats['shorts_uploads'] = cursor.fetchone()[0]

        # Queue size
        cursor.execute("""
            SELECT COUNT(*) FROM sessions
            WHERE uploaded_to_youtube = 0 AND generation_status = 'complete'
        """)
        stats['upload_queue_size'] = cursor.fetchone()[0]

        # Average quality score
        cursor.execute("""
            SELECT AVG(quality_score) FROM sessions
            WHERE quality_score IS NOT NULL
        """)
        avg = cursor.fetchone()[0]
        stats['avg_quality_score'] = round(avg, 1) if avg else None

        return stats


# ==================== CLI ====================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='State Database Manager')
    parser.add_argument('--init', action='store_true', help='Initialize database schema')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--db', type=str, help='Database path (default: data/automation_state.db)')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    db_path = Path(args.db) if args.db else None
    db = StateDatabase(db_path)

    if args.init:
        db.init_schema()
        print(f"Database initialized at {db.db_path}")

    if args.stats:
        stats = db.get_stats()
        print("\n=== Automation Statistics ===")
        print(f"Sessions by status: {stats['by_status']}")
        print(f"YouTube uploads: {stats['youtube_uploads']}")
        print(f"Website uploads: {stats['website_uploads']}")
        print(f"Shorts uploads: {stats['shorts_uploads']}")
        print(f"Upload queue size: {stats['upload_queue_size']}")
        print(f"Average quality score: {stats['avg_quality_score']}")

    db.close()
