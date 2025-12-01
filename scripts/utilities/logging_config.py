#!/usr/bin/env python3
"""
Centralized logging configuration for the Dreamweaving project.

This module provides a consistent logging setup across all scripts,
replacing scattered print() statements with proper logging.

Usage:
    from scripts.utilities.logging_config import get_logger

    logger = get_logger(__name__)
    logger.info("Processing audio...")
    logger.warning("File not found, using default")
    logger.error("Failed to generate audio")

Environment variables:
    DREAMWEAVING_LOG_LEVEL: Set log level (DEBUG, INFO, WARNING, ERROR)
    DREAMWEAVING_LOG_FILE: Optional file path for log output
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional


# Default configuration
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
SIMPLE_FORMAT = '%(levelname)s: %(message)s'

# Module-level logger cache
_loggers: dict = {}


def setup_logging(
    name: str = 'dreamweaving',
    level: Optional[int] = None,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Set up and return a configured logger.

    Args:
        name: Logger name (typically __name__ of the calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to write logs to file
        format_string: Custom format string for log messages
        console_output: Whether to output to console (default True)

    Returns:
        Configured logger instance
    """
    # Check environment variables for overrides
    env_level = os.environ.get('DREAMWEAVING_LOG_LEVEL', '').upper()
    env_file = os.environ.get('DREAMWEAVING_LOG_FILE')

    if env_level and hasattr(logging, env_level):
        level = getattr(logging, env_level)
    elif level is None:
        level = DEFAULT_LOG_LEVEL

    if env_file:
        log_file = env_file

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Choose format
    if format_string is None:
        format_string = DEFAULT_FORMAT if log_file else SIMPLE_FORMAT

    formatter = logging.Formatter(format_string)

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = 'dreamweaving') -> logging.Logger:
    """
    Get or create a logger with the given name.

    This is the primary function to use in other modules.
    It caches loggers to avoid duplicate setup.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Configured logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("Starting audio generation")
    """
    if name not in _loggers:
        _loggers[name] = setup_logging(name)
    return _loggers[name]


def set_global_level(level: int) -> None:
    """
    Set logging level for all cached loggers.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
    """
    for logger in _loggers.values():
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)


# Convenience functions for quick logging without setup
def debug(msg: str, *args, **kwargs) -> None:
    """Log a debug message to the default logger."""
    get_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """Log an info message to the default logger."""
    get_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """Log a warning message to the default logger."""
    get_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """Log an error message to the default logger."""
    get_logger().error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs) -> None:
    """Log a critical message to the default logger."""
    get_logger().critical(msg, *args, **kwargs)


if __name__ == '__main__':
    # Demo/test the logging configuration
    logger = get_logger('demo')

    print("Testing logging configuration...")
    print("=" * 50)

    logger.debug("This is a debug message (hidden by default)")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    print("\nSetting level to DEBUG...")
    set_global_level(logging.DEBUG)
    logger.debug("Now debug messages are visible")

    print("\nLogging configuration test complete.")
