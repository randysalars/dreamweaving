"""
Interactive UI components for user input.

Handles all user prompts and confirmations in a centralized way.
"""

import sys
import logging
from typing import Optional, Tuple

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

logger = logging.getLogger(__name__)


class InteractiveUI:
    """
    Handles all user interaction for the agent.

    Provides a consistent interface for prompts, confirmations,
    and user input with rich console formatting.
    """

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the interactive UI.

        Args:
            console: Optional Rich Console instance
        """
        self.console = console or Console()
        self._is_interactive = self._check_interactive()

    def _check_interactive(self) -> bool:
        """Check if running in an interactive terminal."""
        try:
            return sys.stdin.isatty()
        except Exception:
            return False

    @property
    def is_interactive(self) -> bool:
        """Check if the UI can accept user input."""
        return self._is_interactive

    def prompt_for_database_url(self) -> Optional[str]:
        """
        Prompt user for Notion database URL.

        Returns:
            Database URL/ID entered by user, or None if cancelled
        """
        if not self.is_interactive:
            return None

        self.console.print(Panel(
            "[bold]Notion Database URL Required[/bold]\n\n"
            "Please paste the URL of the Notion Page or Database to monitor.\n"
            "The URL should look like: https://www.notion.so/your-page-id",
            title="Setup",
            border_style="blue"
        ))

        try:
            url = Prompt.ask(
                "[cyan]Enter Notion URL or Database ID[/cyan]",
                console=self.console
            )
            return url.strip() if url else None
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Cancelled.[/yellow]")
            return None

    def prompt_for_website_path(
        self,
        title: str,
        default_path: str = "/ai"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Prompt for target website path and section name.

        Args:
            title: Article title for context
            default_path: Default path to suggest

        Returns:
            Tuple of (target_path, section_name) or (None, None) if skipped
        """
        if not self.is_interactive:
            return None, None

        self.console.print(f"\n[bold cyan]Website Integration for:[/bold cyan] '{title}'")

        try:
            target_path = Prompt.ask(
                "Target path (e.g., '/ai' or 'ai/operations')",
                default="",
                console=self.console
            )

            if not target_path:
                return None, None

            section_name = Prompt.ask(
                "Section name (e.g., 'Daily Work')",
                default="Articles",
                console=self.console
            )

            return target_path.strip(), section_name.strip()

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Skipped.[/yellow]")
            return None, None

    def prompt_for_emoji(self, default: str = "📄") -> str:
        """
        Prompt for card emoji icon.

        Args:
            default: Default emoji to use

        Returns:
            Selected emoji
        """
        if not self.is_interactive:
            return default

        try:
            emoji = Prompt.ask(
                f"Enter emoji icon for card",
                default=default,
                console=self.console
            )
            return emoji.strip() or default
        except KeyboardInterrupt:
            return default

    def confirm_article(self, title: str) -> bool:
        """
        Confirm processing of an article.

        Args:
            title: Article title

        Returns:
            True if confirmed, False otherwise
        """
        if not self.is_interactive:
            return True  # Auto-confirm in non-interactive mode

        try:
            return Confirm.ask(
                f"Process article: '{title}'?",
                default=True,
                console=self.console
            )
        except KeyboardInterrupt:
            return False

    def confirm_batch(self, count: int) -> bool:
        """
        Confirm processing of a batch of articles.

        Args:
            count: Number of articles in batch

        Returns:
            True if confirmed, False otherwise
        """
        if not self.is_interactive:
            return True

        try:
            return Confirm.ask(
                f"Process {count} article(s)?",
                default=True,
                console=self.console
            )
        except KeyboardInterrupt:
            return False

    def show_progress(self, current: int, total: int, title: str) -> None:
        """
        Show processing progress.

        Args:
            current: Current item number
            total: Total items
            title: Current item title
        """
        self.console.print(
            f"[dim][{current}/{total}][/dim] Processing: [cyan]{title}[/cyan]"
        )

    def show_success(self, message: str) -> None:
        """Show success message."""
        self.console.print(f"[green]✓[/green] {message}")

    def show_error(self, message: str) -> None:
        """Show error message."""
        self.console.print(f"[red]✗[/red] {message}")

    def show_warning(self, message: str) -> None:
        """Show warning message."""
        self.console.print(f"[yellow]⚠[/yellow] {message}")

    def show_info(self, message: str) -> None:
        """Show info message."""
        self.console.print(f"[blue]ℹ[/blue] {message}")

    def print_card_snippet(self, snippet: str, section_path: str) -> None:
        """
        Print a card snippet for manual insertion.

        Args:
            snippet: TSX code snippet
            section_path: Target section path
        """
        self.console.print(Panel(
            snippet,
            title=f"Copy to {section_path}/page.js",
            border_style="green"
        ))

    def get_test_mode_defaults(self) -> Tuple[str, str]:
        """
        Get default values for test mode.

        Returns:
            Tuple of (target_path, section_name)
        """
        logger.info("[TEST MODE] Using default website params: /ai/operations | Daily Work")
        return "/ai/operations", "Daily Work"
