"""
Centralized logging configuration for the Notion Content Agent.

Provides rich console output with structured logging support.
"""

import logging
import sys
from typing import Optional, Tuple

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme


# Custom theme for agent logging
AGENT_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "processing": "magenta",
    "metric": "blue",
})

# Module-level console instance
_console: Optional[Console] = None
_logger: Optional[logging.Logger] = None


def setup_logging(
    level: str = "INFO",
    name: str = "notion_agent",
    show_path: bool = False
) -> Tuple[logging.Logger, Console]:
    """
    Configure rich logging for the agent.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        name: Logger name
        show_path: Whether to show file paths in log output

    Returns:
        Tuple of (logger, console)
    """
    global _console, _logger

    # Create console with custom theme
    _console = Console(theme=AGENT_THEME)

    # Configure logging with rich handler
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=_console,
                rich_tracebacks=True,
                show_path=show_path,
                markup=True
            )
        ],
        force=True  # Override any existing configuration
    )

    _logger = logging.getLogger(name)
    _logger.setLevel(level)

    return _logger, _console


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name. If None, returns the main agent logger.

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(name)

    if _logger is None:
        setup_logging()

    return _logger or logging.getLogger("notion_agent")


def get_console() -> Console:
    """
    Get the shared console instance.

    Returns:
        Rich Console instance
    """
    global _console

    if _console is None:
        _console = Console(theme=AGENT_THEME)

    return _console


def log_processing(title: str, page_id: str) -> None:
    """Log that an article is being processed."""
    logger = get_logger()
    logger.info(f"[processing]Processing:[/processing] '{title}' ({page_id})")


def log_success(title: str, output_path: str) -> None:
    """Log successful article generation."""
    logger = get_logger()
    logger.info(f"[success]Saved:[/success] {output_path}")


def log_error(message: str, exc_info: bool = False) -> None:
    """Log an error."""
    logger = get_logger()
    logger.error(f"[error]{message}[/error]", exc_info=exc_info)


def log_warning(message: str) -> None:
    """Log a warning."""
    logger = get_logger()
    logger.warning(f"[warning]{message}[/warning]")


def log_metric(name: str, value: any) -> None:
    """Log a metric value."""
    logger = get_logger()
    logger.info(f"[metric]{name}:[/metric] {value}")
