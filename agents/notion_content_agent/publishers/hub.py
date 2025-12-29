"""
Hub page management for Next.js website.

Handles creation and updating of hub pages that link to articles.
"""

import os
import logging
from pathlib import Path
from typing import Optional

from models import HubCard

logger = logging.getLogger(__name__)


class HubPageManager:
    """
    Manages hub pages and their card grids.

    Hub pages are section landing pages that contain cards linking to
    individual articles. This class handles creating new hubs and adding
    cards to existing hubs.
    """

    # Markers used to find insertion points in hub pages
    HUB_CARDS_START = "{/* HUB_CARDS_START */}"
    HUB_CARDS_END = "{/* HUB_CARDS_END */}"

    def __init__(self, website_root: str):
        """
        Initialize the hub page manager.

        Args:
            website_root: Path to the Next.js app directory (e.g., salarsu/src/app)
        """
        self.website_root = Path(website_root)

    def _humanize_path_segment(self, segment: str) -> str:
        """Convert path segment to human-readable title."""
        return segment.replace("-", " ").replace("_", " ").strip().title() or "Hub"

    def generate_hub_card(self, card: HubCard) -> str:
        """
        Generate TSX code for a hub card component.

        Args:
            card: HubCard with title, description, and href

        Returns:
            TSX code string for the card
        """
        # Sanitize inputs for TSX
        safe_title = card.title.replace("{", "").replace("}", "")
        safe_description = card.description.replace("{", "").replace("}", "")
        safe_href = card.href if card.href.startswith("/") else f"/{card.href.lstrip('/')}"

        return f"""
            <Card className="border-slate-200 bg-white transition-shadow hover:shadow-md">
              <CardHeader>
                <CardTitle className="text-lg">{safe_title}</CardTitle>
                <CardDescription className="line-clamp-3">{safe_description}</CardDescription>
              </CardHeader>
              <CardFooter>
                <Link href="{safe_href}" className="w-full">
                  <Button variant="ghost" className="w-full justify-between gap-2">
                    Open Hub <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </CardFooter>
            </Card>
"""

    def ensure_hub_exists(self, path: str, title: Optional[str] = None) -> Path:
        """
        Create a hub page if it doesn't exist.

        Args:
            path: Relative path for the hub (e.g., "ai/operations")
            title: Optional title override (derived from path if not provided)

        Returns:
            Path to the hub page.tsx file
        """
        clean_path = path.strip("/")
        hub_dir = self.website_root / clean_path
        hub_page_path = hub_dir / "page.tsx"

        if hub_page_path.exists():
            return hub_page_path

        # Create directory
        hub_dir.mkdir(parents=True, exist_ok=True)

        # Derive title from path if not provided
        if not title:
            segments = clean_path.split("/")
            title = self._humanize_path_segment(segments[-1]) if segments else "Hub"

        # Generate default hub page
        hub_content = self._generate_default_hub_page(title, clean_path)

        with open(hub_page_path, "w", encoding="utf-8") as f:
            f.write(hub_content)

        logger.info(f"Created new hub page: {hub_page_path}")
        return hub_page_path

    def _generate_default_hub_page(self, title: str, clean_path: str) -> str:
        """Generate default hub page TSX content."""
        return f'''import React from "react";
import Link from "next/link";
import {{ Card, CardDescription, CardFooter, CardHeader, CardTitle }} from "@/components/ui/card";
import {{ Button }} from "@/components/ui/button";
import {{ ArrowRight }} from "lucide-react";

export default function HubPage() {{
  return (
    <div className="min-h-screen bg-slate-50 py-12 px-6">
      <div className="mx-auto max-w-6xl space-y-12">
        <div className="space-y-4">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900">{title} Hub</h1>
          <p className="text-lg text-slate-600">Explore content hubs and generated resources.</p>
        </div>

        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">Sections</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {{/* HUB_CARDS_START */}}
            {{/* HUB_CARDS_END */}}
          </div>
        </section>
      </div>
    </div>
  );
}}
'''

    def add_card_to_hub(self, hub_path: str, card: HubCard) -> bool:
        """
        Add a card to an existing hub page.

        Args:
            hub_path: Relative path to the hub (e.g., "ai/operations")
            card: HubCard to add

        Returns:
            True if card was added successfully, False otherwise
        """
        clean_path = hub_path.strip("/")
        hub_page_path = self.website_root / clean_path / "page.tsx"

        if not hub_page_path.exists():
            logger.warning(f"Hub page does not exist: {hub_page_path}")
            return False

        with open(hub_page_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if card already exists
        if card.href in content:
            logger.info(f"Card already exists in hub for: {card.href}")
            return True

        # Try to insert at HUB_CARDS_END marker
        if self.HUB_CARDS_END in content:
            card_tsx = self.generate_hub_card(card)
            content = content.replace(
                self.HUB_CARDS_END,
                f"{card_tsx}            {self.HUB_CARDS_END}"
            )

            with open(hub_page_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Added card to hub: {hub_page_path} -> {card.href}")
            return True

        # No markers found - save as snippet for manual insertion
        snippet_path = self.website_root / clean_path / "new_cards.snippet.txt"
        with open(snippet_path, "a", encoding="utf-8") as f:
            f.write(self.generate_hub_card(card))

        logger.warning(
            f"Hub page exists but has no HUB_CARDS markers. "
            f"Card snippet saved to: {snippet_path}"
        )
        return False

    def ensure_parent_links_child(self, child_path: str) -> None:
        """
        Ensure parent hub page contains a link to the child hub.

        For example, when creating /ai/operations, ensure /ai hub
        has a card linking to /ai/operations.

        Args:
            child_path: Path of the child hub (e.g., "ai/operations")
        """
        parts = [p for p in child_path.strip("/").split("/") if p]

        if len(parts) < 2:
            return  # No parent to update

        parent_path = "/".join(parts[:-1])
        child_segment = parts[-1]
        child_title = self._humanize_path_segment(child_segment)
        child_href = f"/{child_path.strip('/')}"
        child_description = f"Browse {child_title} content and resources."

        # Ensure parent hub exists
        parent_hub = self.ensure_hub_exists(parent_path)

        # Add card for child hub
        card = HubCard(
            title=child_title,
            description=child_description,
            href=child_href
        )

        self.add_card_to_hub(parent_path, card)

    def generate_section_snippet(
        self,
        section: str,
        title: str,
        slug: str,
        summary: str = ""
    ) -> str:
        """
        Generate a section with article card for hub pages.

        Args:
            section: Section heading
            title: Article title
            slug: Article URL slug
            summary: Article summary

        Returns:
            TSX code for the section
        """
        return f'''
        <section className="space-y-6">
            <h2 className="text-2xl font-semibold">{section}</h2>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                 <Card className="bg-white border-slate-200 hover:shadow-md transition-shadow">
                    <CardHeader>
                        <CardTitle className="text-lg line-clamp-2">{title}</CardTitle>
                        <CardDescription className="line-clamp-3">{summary or "Read full article..."}</CardDescription>
                    </CardHeader>
                    <CardFooter>
                        <Link href="{slug}" className="w-full">
                            <Button variant="ghost" className="w-full justify-between gap-2">
                                Read Article <ArrowRight className="h-4 w-4" />
                            </Button>
                        </Link>
                    </CardFooter>
                 </Card>
            </div>
        </section>
        '''
