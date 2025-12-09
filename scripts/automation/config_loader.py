#!/usr/bin/env python3
"""
Configuration Loader

Loads automation settings from config/automation_config.yaml with defaults.

Usage:
    from scripts.automation.config_loader import load_config

    config = load_config()
    print(config['generation']['mode'])  # 'standard'
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Default config path
DEFAULT_CONFIG_PATH = PROJECT_ROOT / 'config' / 'automation_config.yaml'

# Default configuration values
DEFAULT_CONFIG: Dict[str, Any] = {
    'generation': {
        'target_sessions_per_night': 5,
        'mode': 'standard',  # budget | standard | premium
        'image_method': 'sd',  # sd | midjourney | stock
    },
    'upload': {
        'selection_strategy': 'quality',  # quality | fifo | priority
        'use_analytics_timing': True,
        'fallback_long_upload_time': '12:00',  # MST
        'fallback_shorts_upload_time': '08:00',  # MST
        'category_id': '22',  # People & Blogs
    },
    'shorts': {
        'duration_seconds': 40,
        'cta_duration_seconds': 8,
        'source': 'website_only',
    },
    'youtube': {
        'channel_name': 'Randy Salars',
        'channel_url': 'https://www.youtube.com/@RandySalars',
        'credentials_dir': 'config/youtube_credentials',
    },
    'notion': {
        'topic_database_id': '2c22bab3-796d-81fb-bdf8-efd2aab0159e',
        'root_page_id': '1ee2bab3796d80738af6c96bd5077acf',
    },
    'database': {
        'path': 'data/automation_state.db',
    },
    'archive': {
        'enabled': True,
        'archive_dir': 'archive',
        'archive_after_youtube_upload': True,
    },
    'logging': {
        'log_dir': 'data/logs/automation',
        'log_level': 'INFO',
    },
    'cron': {
        'enabled': False,  # Disabled until tested
        'nightly_generation': '0 4 * * *',  # 9pm MST = 4am UTC
        'daily_upload': None,
        'daily_shorts': None,
    },
}


def deep_merge(base: Dict, override: Dict) -> Dict:
    """Deep merge two dictionaries, with override taking precedence.

    Args:
        base: Base dictionary with defaults
        override: Override dictionary

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_path: Path = None) -> Dict[str, Any]:
    """Load configuration from YAML file with defaults.

    Args:
        config_path: Path to config file. Defaults to config/automation_config.yaml

    Returns:
        Configuration dictionary
    """
    config_path = config_path or DEFAULT_CONFIG_PATH

    # Start with defaults
    config = DEFAULT_CONFIG.copy()

    # Load from file if exists
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f) or {}
            config = deep_merge(config, file_config)
            logger.debug(f"Loaded config from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            logger.warning("Using default configuration")
    else:
        logger.info(f"Config file not found at {config_path}, using defaults")

    # Override with environment variables
    config = apply_env_overrides(config)

    # Resolve relative paths to absolute
    config = resolve_paths(config)

    return config


def apply_env_overrides(config: Dict) -> Dict:
    """Apply environment variable overrides.

    Environment variables:
        DREAMWEAVING_GENERATION_MODE: budget | standard | premium
        DREAMWEAVING_IMAGE_METHOD: sd | midjourney | stock
        DREAMWEAVING_UPLOAD_STRATEGY: quality | fifo | priority
        DREAMWEAVING_SESSIONS_PER_NIGHT: Number of sessions to generate

    Args:
        config: Current configuration

    Returns:
        Configuration with overrides applied
    """
    env_mappings = {
        'DREAMWEAVING_GENERATION_MODE': ('generation', 'mode'),
        'DREAMWEAVING_IMAGE_METHOD': ('generation', 'image_method'),
        'DREAMWEAVING_UPLOAD_STRATEGY': ('upload', 'selection_strategy'),
        'DREAMWEAVING_SESSIONS_PER_NIGHT': ('generation', 'target_sessions_per_night'),
        'DREAMWEAVING_LOG_LEVEL': ('logging', 'log_level'),
    }

    for env_var, (section, key) in env_mappings.items():
        value = os.environ.get(env_var)
        if value:
            # Type conversion for integers
            if key == 'target_sessions_per_night':
                value = int(value)
            config[section][key] = value
            logger.debug(f"Override from env: {env_var} = {value}")

    return config


def resolve_paths(config: Dict) -> Dict:
    """Resolve relative paths to absolute paths.

    Args:
        config: Configuration dictionary

    Returns:
        Configuration with resolved paths
    """
    # Database path
    db_path = config['database']['path']
    if not Path(db_path).is_absolute():
        config['database']['path'] = str(PROJECT_ROOT / db_path)

    # YouTube credentials directory
    creds_dir = config['youtube']['credentials_dir']
    if not Path(creds_dir).is_absolute():
        config['youtube']['credentials_dir'] = str(PROJECT_ROOT / creds_dir)

    # Archive directory
    archive_dir = config['archive']['archive_dir']
    if not Path(archive_dir).is_absolute():
        config['archive']['archive_dir'] = str(PROJECT_ROOT / archive_dir)

    # Log directory
    log_dir = config['logging']['log_dir']
    if not Path(log_dir).is_absolute():
        config['logging']['log_dir'] = str(PROJECT_ROOT / log_dir)

    return config


def get_project_root() -> Path:
    """Get project root directory.

    Returns:
        Path to project root
    """
    return PROJECT_ROOT


def setup_logging(config: Dict = None):
    """Set up logging based on configuration.

    Args:
        config: Configuration dictionary. Loads default if None.
    """
    if config is None:
        config = load_config()

    log_dir = Path(config['logging']['log_dir'])
    log_dir.mkdir(parents=True, exist_ok=True)

    log_level = getattr(logging, config['logging']['log_level'].upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / 'automation.log'),
        ]
    )

    logger.info(f"Logging configured: level={config['logging']['log_level']}, dir={log_dir}")


# ==================== CLI ====================

if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Configuration Loader')
    parser.add_argument('--show', action='store_true', help='Show current configuration')
    parser.add_argument('--create', action='store_true', help='Create default config file')
    parser.add_argument('--path', type=str, help='Config file path')

    args = parser.parse_args()

    config_path = Path(args.path) if args.path else DEFAULT_CONFIG_PATH

    if args.create:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
        print(f"Created config file at {config_path}")

    if args.show:
        config = load_config(config_path)
        print("\n=== Current Configuration ===")
        print(yaml.dump(config, default_flow_style=False, sort_keys=False))
