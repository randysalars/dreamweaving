"""
Markdown file publisher for local output.

Saves generated articles as markdown files with frontmatter.
"""

import os
import logging
from datetime import date
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class MarkdownPublisher:
    """
    Publishes generated content as markdown files.

    Handles local file output with proper frontmatter formatting.
    """

    def __init__(self, output_dir: str):
        """
        Initialize the markdown publisher.

        Args:
            output_dir: Directory to save markdown files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def publish(
        self,
        title: str,
        content: str,
        slug: Optional[str] = None,
        tags: Optional[list] = None,
        category: Optional[str] = None
    ) -> Path:
        """
        Save content as a markdown file.

        Args:
            title: Article title
            content: Article content
            slug: Optional custom filename slug
            tags: Optional list of tags
            category: Optional category

        Returns:
            Path to the created file
        """
        # Generate filename from slug or title
        if slug:
            filename = f"{slug}.md"
        else:
            filename = self._generate_filename(title)

        filepath = self.output_dir / filename

        # Generate frontmatter
        frontmatter = self._generate_frontmatter(
            title=title,
            tags=tags,
            category=category
        )

        # Write file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(frontmatter)
            f.write(content)

        logger.info(f"Saved markdown: {filepath}")
        return filepath

    def _generate_filename(self, title: str) -> str:
        """Generate safe filename from title."""
        # Remove unsafe characters, convert to lowercase
        safe_name = "".join(
            c for c in title
            if c.isalnum() or c in (' ', '-', '_')
        )
        safe_name = safe_name.strip().replace(' ', '_').lower()

        # Ensure non-empty and add extension
        if not safe_name:
            safe_name = "untitled"

        return f"{safe_name}.md"

    def _generate_frontmatter(
        self,
        title: str,
        tags: Optional[list] = None,
        category: Optional[str] = None
    ) -> str:
        """Generate YAML frontmatter for the markdown file."""
        lines = [
            "---",
            f"title: {title}",
            f"date: {date.today()}",
        ]

        if category:
            lines.append(f"category: {category}")

        if tags:
            lines.append("tags:")
            for tag in tags:
                lines.append(f"  - {tag}")

        lines.append("---")
        lines.append("")
        lines.append("")

        return "\n".join(lines)

    def exists(self, slug: str) -> bool:
        """Check if an article with this slug already exists."""
        filepath = self.output_dir / f"{slug}.md"
        return filepath.exists()

    def list_articles(self) -> list:
        """List all markdown files in output directory."""
        return sorted(self.output_dir.glob("*.md"))
