"""
Constants and default values for the Notion Content Agent.

Centralizes all magic strings and configuration defaults.
"""

from enum import Enum


class NotionStatus(str, Enum):
    """Status values used in Notion database."""
    READY = "Ready to Write"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    ERROR = "Error"
    MANUAL_DISCOVERY = "Manual Discovery"
    AI_DISCOVERY = "AI Discovery"


class ArticleType(str, Enum):
    """Types of article sources."""
    PAGE = "Page"
    BLOCK_ITEM = "Block Item"
    AI_TASK = "AI Task"


class Defaults:
    """Default configuration values."""
    # Polling
    POLL_INTERVAL_SECONDS = 60
    POLL_CHUNK_SIZE = 5  # Sleep in chunks for interrupt handling
    POLL_CHUNKS = 12  # Total chunks = 60s

    # Processing
    BATCH_SIZE = 10
    MAX_CONCURRENT = 3

    # Retry
    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 1.0  # seconds
    RETRY_MAX_DELAY = 60.0  # seconds
    RETRY_EXPONENTIAL_BASE = 2.0

    # Cache
    CACHE_TTL_SECONDS = 300  # 5 minutes

    # API
    OPENAI_MODEL = "gpt-4"
    OPENAI_TEMPERATURE = 0.7

    # Test mode
    TEST_MODE_ARTICLE_LIMIT = 3


class Timeouts:
    """Timeout values in seconds."""
    API_CALL = 120
    ERROR_BACKOFF = 30


class LogMessages:
    """Standardized log message templates."""
    AGENT_STARTED = "Starting Notion Content Agent..."
    AGENT_STOPPED = "Agent stopped by user."
    NO_PENDING = "No 'Ready to Write' articles found. Sleeping for {interval}s..."
    FOUND_ARTICLES = "Found {count} pending articles"
    PROCESSING = "Processing candidate: '{title}' ({page_id})"
    AUTO_PROCESSING = "Auto-processing article: '{title}'"
    SHUTDOWN_REQUESTED = "Shutdown requested"
    SHUTDOWN_SIGNAL = "Received signal {signum}, initiating graceful shutdown..."
