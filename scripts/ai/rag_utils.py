#!/usr/bin/env python3
"""
Shared utilities for RAG file watcher infrastructure.

Consolidates common patterns across RAG-related scripts:
- Project root detection
- Environment loading
- Configuration loading with env var resolution
- State file I/O (JSON)
- File hashing

Part of Phase 8: Automatic RAG Indexing System
"""
import os
import sys
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Set
from datetime import datetime

# Single source of truth for project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

logger = logging.getLogger(__name__)


def setup_project_path() -> None:
    """Add project root to sys.path if not already present."""
    project_str = str(PROJECT_ROOT)
    if project_str not in sys.path:
        sys.path.insert(0, project_str)


def load_dotenv_safe() -> bool:
    """
    Load .env file if python-dotenv is available.

    Returns:
        True if .env was loaded, False if dotenv not available or .env missing.
    """
    try:
        from dotenv import load_dotenv
        env_path = PROJECT_ROOT / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            return True
        return False
    except ImportError:
        return False


def _resolve_env_vars(obj: Any) -> Any:
    """
    Recursively resolve ${VAR} patterns in config values.

    Supports:
        - ${VAR} -> os.environ.get("VAR", "${VAR}")
        - Nested dicts and lists
    """
    if isinstance(obj, str):
        if obj.startswith("${") and obj.endswith("}"):
            var_name = obj[2:-1]
            return os.environ.get(var_name, obj)
        return obj
    elif isinstance(obj, dict):
        return {k: _resolve_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_env_vars(item) for item in obj]
    return obj


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """
    Load YAML config with environment variable resolution.

    Args:
        config_path: Path to YAML config file

    Returns:
        Parsed config dict with ${VAR} patterns resolved from environment.
        Returns empty dict if file doesn't exist.
    """
    if not config_path.exists():
        return {}

    try:
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
        return _resolve_env_vars(config)
    except ImportError:
        logger.warning("PyYAML not installed, config loading unavailable")
        return {}
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        return {}


def get_notion_config() -> Dict[str, Any]:
    """Load the main notion_config.yaml configuration."""
    config_path = PROJECT_ROOT / "config" / "notion_config.yaml"
    return load_yaml_config(config_path)


def load_state_file(state_path: Path) -> Dict[str, Any]:
    """
    Load JSON state file with error handling.

    Args:
        state_path: Path to JSON state file

    Returns:
        Parsed state dict, or empty dict if file doesn't exist or is invalid.
    """
    if state_path.exists():
        try:
            return json.loads(state_path.read_text())
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse state file {state_path}: {e}")
        except Exception as e:
            logger.error(f"Failed to read state file {state_path}: {e}")
    return {}


def save_state_file(state_path: Path, state: Dict[str, Any]) -> bool:
    """
    Save state dict to JSON file with timestamp.

    Args:
        state_path: Path to JSON state file
        state: State dict to save

    Returns:
        True if saved successfully, False otherwise.
    """
    try:
        state["updated_at"] = datetime.now().isoformat()
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2))
        return True
    except Exception as e:
        logger.error(f"Failed to save state file {state_path}: {e}")
        return False


def get_file_hash(filepath: Path) -> str:
    """
    Calculate MD5 hash of a single file.

    Args:
        filepath: Path to file

    Returns:
        MD5 hex digest of file contents.
    """
    return hashlib.md5(filepath.read_bytes()).hexdigest()


def get_content_hash(
    directory: Path,
    extensions: Optional[Set[str]] = None
) -> str:
    """
    Calculate combined hash of all files with given extensions in directory.

    Args:
        directory: Directory to scan
        extensions: Set of file extensions to include (default: {'.md'})

    Returns:
        MD5 hex digest of combined file contents.
    """
    if extensions is None:
        extensions = {'.md'}

    hasher = hashlib.md5()

    for ext in sorted(extensions):
        # Ensure extension has leading dot
        if not ext.startswith('.'):
            ext = f'.{ext}'

        for filepath in sorted(directory.glob(f"**/*{ext}")):
            try:
                hasher.update(filepath.read_bytes())
            except Exception as e:
                logger.debug(f"Skipped hashing {filepath}: {e}")

    return hasher.hexdigest()


def normalize_path(path: str) -> str:
    """
    Normalize a path string for comparison.

    Removes leading ./ and trailing /

    Args:
        path: Path string to normalize

    Returns:
        Normalized path string.
    """
    if path.startswith("./"):
        path = path[2:]
    if path.endswith("/"):
        path = path[:-1]
    return path


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable form.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string like "2m 30s" or "45s"
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"


def format_size(bytes_count: int) -> str:
    """
    Format byte count in human-readable form.

    Args:
        bytes_count: Size in bytes

    Returns:
        Formatted string like "1.5 MB" or "256 KB"
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f} TB"
