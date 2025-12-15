#!/usr/bin/env python3
"""
Audit Logger - Append-only event log for critical actions.

Creates an immutable audit trail of all significant events in the system.
Each session has its own audit log at sessions/{session}/.audit_log.jsonl

Usage:
    from scripts.utilities.audit_logger import log_event, get_audit_trail

    # Log an event
    log_event("audio_mixed", "garden-of-eden", {
        "voice_file": "voice_enhanced.mp3",
        "binaural_file": "binaural_dynamic.wav",
        "output_file": "session_mixed.wav"
    })

    # Get audit trail
    events = get_audit_trail("garden-of-eden")

Event Types:
    - session_created
    - manifest_generated
    - manifest_updated
    - script_generated
    - script_updated
    - audio_generated
    - audio_mixed
    - audio_mastered
    - video_assembled
    - youtube_packaged
    - validation_passed
    - validation_failed
    - error_occurred
    - cleanup_performed
    - upload_started
    - upload_completed
"""

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Thread-local storage for correlation IDs
_local = threading.local()


def get_correlation_id() -> str:
    """Get the current correlation ID, or generate a new one."""
    if not hasattr(_local, "correlation_id") or _local.correlation_id is None:
        _local.correlation_id = str(uuid.uuid4())[:8]
    return _local.correlation_id


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current thread/context."""
    _local.correlation_id = correlation_id


def clear_correlation_id() -> None:
    """Clear the correlation ID."""
    _local.correlation_id = None


def new_correlation_id() -> str:
    """Generate and set a new correlation ID, returning it."""
    new_id = str(uuid.uuid4())[:8]
    _local.correlation_id = new_id
    return new_id


def get_session_audit_path(session: str) -> Path:
    """Get the path to a session's audit log."""
    # Handle both "session-name" and "sessions/session-name" formats
    if session.startswith("sessions/"):
        session_dir = PROJECT_ROOT / session
    else:
        session_dir = PROJECT_ROOT / "sessions" / session

    return session_dir / ".audit_log.jsonl"


def log_event(
    event_type: str,
    session: str,
    data: Optional[Dict[str, Any]] = None,
    actor: str = "system",
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Log an audit event.

    Args:
        event_type: Type of event (see module docstring for list)
        session: Session name or path
        data: Additional event data (will be sanitized)
        actor: Who/what triggered the event (user, system, agent name)
        correlation_id: Optional correlation ID (uses thread-local if not provided)

    Returns:
        The logged event dict
    """
    if data is None:
        data = {}

    # Sanitize data - remove sensitive values
    sanitized_data = _sanitize_data(data)

    # Build event
    event = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "session": _extract_session_name(session),
        "actor": actor,
        "correlation_id": correlation_id or get_correlation_id(),
        "data": sanitized_data
    }

    # Append to audit log
    audit_path = get_session_audit_path(session)

    # Ensure directory exists
    audit_path.parent.mkdir(parents=True, exist_ok=True)

    # Append event (atomic write)
    with open(audit_path, "a") as f:
        f.write(json.dumps(event) + "\n")

    return event


def log_error(
    session: str,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    actor: str = "system"
) -> Dict[str, Any]:
    """
    Log an error event.

    Args:
        session: Session name or path
        error: The exception that occurred
        context: Additional context about what was happening
        actor: Who/what triggered the error

    Returns:
        The logged event dict
    """
    data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {}
    }

    return log_event("error_occurred", session, data, actor)


def get_audit_trail(
    session: str,
    event_types: Optional[List[str]] = None,
    since: Optional[datetime] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get audit trail for a session.

    Args:
        session: Session name or path
        event_types: Filter to specific event types
        since: Only return events after this time
        limit: Maximum number of events to return (most recent)

    Returns:
        List of event dicts, ordered by timestamp
    """
    audit_path = get_session_audit_path(session)

    if not audit_path.exists():
        return []

    events = []

    with open(audit_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                events.append(event)
            except json.JSONDecodeError:
                continue

    # Filter by event type
    if event_types:
        events = [e for e in events if e.get("event_type") in event_types]

    # Filter by time
    if since:
        since_iso = since.isoformat() if since.tzinfo else since.replace(tzinfo=timezone.utc).isoformat()
        events = [e for e in events if e.get("timestamp", "") >= since_iso]

    # Sort by timestamp
    events.sort(key=lambda e: e.get("timestamp", ""))

    # Apply limit (most recent)
    if limit and len(events) > limit:
        events = events[-limit:]

    return events


def get_last_event(session: str, event_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get the most recent event for a session."""
    event_types = [event_type] if event_type else None
    events = get_audit_trail(session, event_types=event_types, limit=1)
    return events[0] if events else None


def get_session_timeline(session: str) -> List[Dict[str, str]]:
    """
    Get a simplified timeline of events for a session.

    Returns list of {timestamp, event_type, summary} dicts.
    """
    events = get_audit_trail(session)

    timeline = []
    for event in events:
        summary = _summarize_event(event)
        timeline.append({
            "timestamp": event.get("timestamp", ""),
            "event_type": event.get("event_type", ""),
            "summary": summary
        })

    return timeline


def _extract_session_name(session: str) -> str:
    """Extract session name from path or return as-is."""
    if "/" in session:
        # Handle "sessions/name" or "sessions/name/"
        parts = session.rstrip("/").split("/")
        if parts[0] == "sessions" and len(parts) > 1:
            return parts[1]
        return parts[-1]
    return session


def _sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive values from data dict."""
    sensitive_keys = {
        "password", "secret", "token", "key", "credential",
        "api_key", "auth", "authorization"
    }

    sanitized = {}
    for key, value in data.items():
        key_lower = key.lower()

        # Check if key contains sensitive terms
        if any(s in key_lower for s in sensitive_keys):
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_data(value)
        elif isinstance(value, list):
            sanitized[key] = [
                _sanitize_data(v) if isinstance(v, dict) else v
                for v in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def _summarize_event(event: Dict[str, Any]) -> str:
    """Generate a human-readable summary of an event."""
    event_type = event.get("event_type", "unknown")
    data = event.get("data", {})

    summaries = {
        "session_created": "Session created",
        "manifest_generated": "Manifest generated",
        "manifest_updated": "Manifest updated",
        "script_generated": "Script generated",
        "script_updated": "Script updated",
        "audio_generated": f"Audio generated: {data.get('output_file', 'unknown')}",
        "audio_mixed": f"Audio mixed: {data.get('output_file', 'unknown')}",
        "audio_mastered": f"Audio mastered: {data.get('output_file', 'unknown')}",
        "video_assembled": f"Video assembled: {data.get('output_file', 'unknown')}",
        "youtube_packaged": "YouTube package created",
        "validation_passed": f"Validation passed: {data.get('validator', 'unknown')}",
        "validation_failed": f"Validation failed: {data.get('errors', 'see details')}",
        "error_occurred": f"Error: {data.get('error_type', 'unknown')} - {data.get('error_message', '')[:50]}",
        "cleanup_performed": "Cleanup performed",
        "upload_started": f"Upload started to {data.get('destination', 'unknown')}",
        "upload_completed": f"Upload completed: {data.get('url', 'unknown')}"
    }

    return summaries.get(event_type, f"{event_type}: {str(data)[:50]}")


# =============================================================================
# Context Manager for Correlation IDs
# =============================================================================

class AuditContext:
    """
    Context manager for setting correlation ID for a block of operations.

    Usage:
        with AuditContext("my-operation") as ctx:
            log_event("step_1", session, {...})
            log_event("step_2", session, {...})
            # All events will have the same correlation_id
    """

    def __init__(self, prefix: str = ""):
        self.prefix = prefix
        self.correlation_id = None
        self.previous_id = None

    def __enter__(self):
        self.previous_id = getattr(_local, "correlation_id", None)
        self.correlation_id = f"{self.prefix}-{uuid.uuid4().hex[:6]}" if self.prefix else str(uuid.uuid4())[:8]
        set_correlation_id(self.correlation_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.previous_id:
            set_correlation_id(self.previous_id)
        else:
            clear_correlation_id()
        return False


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """CLI interface for viewing audit logs."""
    import argparse

    parser = argparse.ArgumentParser(description="View audit logs for a session")
    parser.add_argument("session", help="Session name")
    parser.add_argument("--type", "-t", dest="event_type", help="Filter by event type")
    parser.add_argument("--limit", "-n", type=int, help="Limit number of events")
    parser.add_argument("--timeline", action="store_true", help="Show simplified timeline")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.timeline:
        timeline = get_session_timeline(args.session)
        if args.json:
            print(json.dumps(timeline, indent=2))
        else:
            for entry in timeline:
                print(f"[{entry['timestamp'][:19]}] {entry['event_type']}: {entry['summary']}")
    else:
        event_types = [args.event_type] if args.event_type else None
        events = get_audit_trail(args.session, event_types=event_types, limit=args.limit)

        if args.json:
            print(json.dumps(events, indent=2))
        else:
            for event in events:
                print(f"\n[{event['timestamp'][:19]}] {event['event_type']}")
                print(f"  ID: {event['id'][:8]}... | Correlation: {event['correlation_id']}")
                print(f"  Actor: {event['actor']}")
                if event.get('data'):
                    print(f"  Data: {json.dumps(event['data'], indent=4)[:200]}...")


if __name__ == "__main__":
    main()
