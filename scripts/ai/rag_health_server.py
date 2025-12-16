#!/usr/bin/env python3
"""
Minimal HTTP health server for RAG file watcher.

Uses only Python stdlib (http.server) - no external dependencies.
Binds to localhost only by default for security.

Endpoints:
    GET /health     - Basic health check (returns 200 OK or 503 UNHEALTHY)
    GET /metrics    - Detailed metrics as JSON
    GET /ready      - Readiness probe (always 200 if server running)

Usage:
    # As a module (used by rag_file_watcher.py)
    from scripts.ai.rag_health_server import HealthMetrics, start_health_server

    metrics = HealthMetrics()
    thread = start_health_server(metrics, host="127.0.0.1", port=8765)

    # Report events
    metrics.record_sync_success()
    metrics.record_sync_failure("error message")
    metrics.set_pending_changes(5)

    # Check status
    curl http://127.0.0.1:8765/health
    curl http://127.0.0.1:8765/metrics

Part of Phase 8: Automatic RAG Indexing System
"""
import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class HealthMetrics:
    """
    Thread-safe metrics storage for health reporting.

    Tracks:
        - Uptime (time since start)
        - Last sync time
        - Failure count (consecutive)
        - Total syncs
        - Pending changes count
        - Last error message
    """

    def __init__(self, max_failures: int = 3):
        """
        Initialize health metrics.

        Args:
            max_failures: Number of consecutive failures before unhealthy status.
        """
        self._lock = threading.Lock()
        self._start_time = datetime.now()
        self._last_sync_time: Optional[datetime] = None
        self._failure_count = 0
        self._max_failures = max_failures
        self._pending_changes = 0
        self._total_syncs = 0
        self._last_error: Optional[str] = None
        self._is_watching = False
        self._watched_paths: list = []

    def record_sync_start(self):
        """Record that a sync operation has started."""
        with self._lock:
            self._pending_changes = 0

    def record_sync_success(self, vectors_count: int = 0, duration_seconds: float = 0):
        """
        Record a successful sync operation.

        Args:
            vectors_count: Number of vectors indexed
            duration_seconds: Time taken for sync
        """
        with self._lock:
            self._last_sync_time = datetime.now()
            self._failure_count = 0
            self._total_syncs += 1
            self._last_error = None
            logger.debug(f"Recorded sync success: {vectors_count} vectors in {duration_seconds:.1f}s")

    def record_sync_failure(self, error: str):
        """
        Record a failed sync operation.

        Args:
            error: Error message describing the failure
        """
        with self._lock:
            self._failure_count += 1
            self._last_error = error
            logger.debug(f"Recorded sync failure ({self._failure_count}): {error}")

    def record_sync_skipped(self, reason: str):
        """Record that sync was skipped (not a failure)."""
        with self._lock:
            # Skipped syncs don't increment failure count
            logger.debug(f"Recorded sync skipped: {reason}")

    def set_pending_changes(self, count: int):
        """Set the number of pending file changes."""
        with self._lock:
            self._pending_changes = count

    def increment_pending_changes(self):
        """Increment pending changes by 1."""
        with self._lock:
            self._pending_changes += 1

    def set_watching(self, is_watching: bool, paths: Optional[list] = None):
        """Set watcher status and paths."""
        with self._lock:
            self._is_watching = is_watching
            if paths:
                self._watched_paths = paths

    def is_healthy(self) -> bool:
        """
        Check if the service is healthy.

        Returns:
            True if failure count is below threshold.
        """
        with self._lock:
            return self._failure_count < self._max_failures

    def get_failure_count(self) -> int:
        """Get current consecutive failure count."""
        with self._lock:
            return self._failure_count

    def reset_failures(self):
        """Reset failure count (e.g., after manual intervention)."""
        with self._lock:
            self._failure_count = 0
            self._last_error = None

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics as a dictionary.

        Returns:
            Dict containing all health metrics.
        """
        with self._lock:
            uptime_seconds = (datetime.now() - self._start_time).total_seconds()
            return {
                "status": "healthy" if self._failure_count < self._max_failures else "unhealthy",
                "uptime_seconds": int(uptime_seconds),
                "uptime_human": self._format_duration(uptime_seconds),
                "start_time": self._start_time.isoformat(),
                "last_sync": self._last_sync_time.isoformat() if self._last_sync_time else None,
                "failure_count": self._failure_count,
                "max_failures": self._max_failures,
                "pending_changes": self._pending_changes,
                "total_syncs": self._total_syncs,
                "last_error": self._last_error,
                "is_watching": self._is_watching,
                "watched_paths": self._watched_paths,
            }

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in human-readable form."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP request handler for health endpoints."""

    # Class-level metrics reference (set by start_health_server)
    metrics: Optional[HealthMetrics] = None

    def log_message(self, format, *args):
        """Suppress default HTTP logging to avoid noise."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/health":
            self._handle_health()
        elif self.path == "/metrics":
            self._handle_metrics()
        elif self.path == "/ready":
            self._handle_ready()
        elif self.path == "/reset":
            self._handle_reset()
        else:
            self.send_error(404, "Not Found")

    def _handle_health(self):
        """
        Basic health check endpoint.

        Returns 200 if healthy, 503 if unhealthy.
        """
        if self.metrics and self.metrics.is_healthy():
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(503)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            failure_count = self.metrics.get_failure_count() if self.metrics else 0
            self.wfile.write(f"UNHEALTHY (failures: {failure_count})".encode())

    def _handle_metrics(self):
        """
        Detailed metrics endpoint.

        Returns JSON with all health metrics.
        """
        if self.metrics:
            data = self.metrics.get_metrics()
        else:
            data = {"error": "metrics not initialized"}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _handle_ready(self):
        """
        Readiness probe endpoint.

        Always returns 200 if server is running.
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"READY")

    def _handle_reset(self):
        """
        Reset failure count endpoint (POST preferred but GET supported).

        Allows manual recovery without restarting service.
        """
        if self.metrics:
            self.metrics.reset_failures()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK - failures reset")
        else:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ERROR - metrics not initialized")


def start_health_server(
    metrics: HealthMetrics,
    host: str = "127.0.0.1",
    port: int = 8765
) -> Optional[threading.Thread]:
    """
    Start health server in a background daemon thread.

    Args:
        metrics: HealthMetrics instance to report
        host: Host to bind (default: localhost only for security)
        port: Port to listen on

    Returns:
        Thread running the server, or None if failed to start.
    """
    try:
        # Set class-level metrics reference
        HealthHandler.metrics = metrics

        server = HTTPServer((host, port), HealthHandler)
        server.timeout = 1.0  # Allow periodic checks for shutdown

        thread = threading.Thread(
            target=server.serve_forever,
            name="HealthServer",
            daemon=True  # Thread dies when main thread exits
        )
        thread.start()

        logger.info(f"Health server started on http://{host}:{port}")
        logger.info(f"  GET /health  - Health check (200 OK or 503)")
        logger.info(f"  GET /metrics - Detailed JSON metrics")
        logger.info(f"  GET /ready   - Readiness probe")
        logger.info(f"  GET /reset   - Reset failure count")

        return thread

    except OSError as e:
        if e.errno == 98:  # Address already in use
            logger.error(f"Health server port {port} already in use. Is another instance running?")
        else:
            logger.error(f"Failed to start health server: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to start health server: {e}")
        return None


def stop_health_server(server: HTTPServer):
    """Stop the health server gracefully."""
    if server:
        server.shutdown()
        logger.info("Health server stopped")


if __name__ == "__main__":
    # Simple test mode
    import time

    logging.basicConfig(level=logging.INFO)

    print("Starting health server test...")
    metrics = HealthMetrics()
    thread = start_health_server(metrics, port=8765)

    if thread:
        print("\nEndpoints:")
        print("  curl http://127.0.0.1:8765/health")
        print("  curl http://127.0.0.1:8765/metrics")
        print("  curl http://127.0.0.1:8765/ready")
        print("\nSimulating events...")

        # Simulate some events
        metrics.set_watching(True, ["knowledge", "prompts"])
        time.sleep(1)

        metrics.set_pending_changes(3)
        time.sleep(1)

        metrics.record_sync_success(vectors_count=100, duration_seconds=5.5)
        time.sleep(1)

        print("\nPress Ctrl+C to stop...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
    else:
        print("Failed to start health server")
