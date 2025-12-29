"""
Website publisher for Next.js article pages.

Generates TSX article pages and integrates with hub pages.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple

from models import WebsiteArtifact
from .hub import HubPageManager

logger = logging.getLogger(__name__)


class WebsitePublisher:
    """
    Publishes generated content to Next.js website.

    Creates article pages (page.tsx) and integrates them with
    hub pages for navigation.
    """

    def __init__(self, website_root: str):
        """
        Initialize the website publisher.

        Args:
            website_root: Path to the Next.js app directory
        """
        self.website_root = Path(website_root)
        self.hub_manager = HubPageManager(website_root)

    def escape_for_tsx(self, content: str) -> str:
        """
        Properly escape content for TSX template literals.

        Order matters: escape backslashes first, then special characters.

        Args:
            content: Raw content to escape

        Returns:
            Escaped content safe for TSX template literals
        """
        return (
            content
            .replace('\\', '\\\\')  # Escape backslashes first
            .replace('`', '\\`')    # Escape backticks
            .replace('$', '\\$')    # Escape dollar signs
            .replace('{', '\\{')    # Escape opening braces
            .replace('}', '\\}')    # Escape closing braces
        )

    def publish_article(
        self,
        title: str,
        content: str,
        slug: str,
        target_path: str,
        section_name: str,
        summary: str = ""
    ) -> WebsiteArtifact:
        """
        Create article page and update hub.

        Args:
            title: Article title
            content: Article content (markdown)
            slug: URL slug for the article
            target_path: Target path (e.g., "/ai/operations")
            section_name: Section name for back link
            summary: Article summary for hub card

        Returns:
            WebsiteArtifact with paths to created files
        """
        clean_path = target_path.strip("/")
        target_dir = self.website_root / clean_path

        # 1. Create article page
        article_path = self._create_article_page(
            title=title,
            content=content,
            slug=slug,
            target_dir=target_dir,
            clean_path=clean_path,
            section_name=section_name
        )

        # 2. Ensure parent hub links to this path
        self.hub_manager.ensure_parent_links_child(clean_path)

        # 3. Update or create hub page with article card
        hub_path, snippet_path = self._update_hub_page(
            title=title,
            slug=slug,
            summary=summary,
            target_dir=target_dir,
            section_name=section_name
        )

        return WebsiteArtifact(
            article_path=str(article_path),
            hub_path=str(hub_path) if hub_path else None,
            snippet_path=str(snippet_path) if snippet_path else None
        )

    def _create_article_page(
        self,
        title: str,
        content: str,
        slug: str,
        target_dir: Path,
        clean_path: str,
        section_name: str
    ) -> Path:
        """Create the article page.tsx file."""
        article_dir = target_dir / slug
        article_dir.mkdir(parents=True, exist_ok=True)

        article_page_path = article_dir / "page.tsx"
        escaped_content = self.escape_for_tsx(content)

        tsx_content = self._generate_article_tsx(
            title=title,
            content=escaped_content,
            back_path=clean_path,
            section_name=section_name
        )

        with open(article_page_path, "w", encoding="utf-8") as f:
            f.write(tsx_content)

        logger.info(f"Created article page: {article_page_path}")
        return article_page_path

    def _generate_article_tsx(
        self,
        title: str,
        content: str,
        back_path: str,
        section_name: str
    ) -> str:
        """Generate the article page TSX content."""
        return f'''import React from "react";
import ReactMarkdown from "react-markdown";
import {{ Card, CardContent }} from "@/components/ui/card";
import {{ Button }} from "@/components/ui/button";
import {{ ArrowLeft }} from "lucide-react";
import Link from "next/link";

const content = `{content}`;

export default function ArticlePage() {{
  return (
    <div className="min-h-screen bg-slate-50 py-12 px-6">
      <div className="max-w-4xl mx-auto space-y-8">
        <Link href="/{back_path}">
            <Button variant="ghost" className="gap-2 pl-0">
                <ArrowLeft className="h-4 w-4" />
                Back to {section_name}
            </Button>
        </Link>

        <article className="prose prose-slate lg:prose-lg bg-white p-8 rounded-2xl shadow-sm ring-1 ring-slate-200">
            <ReactMarkdown>{{content}}</ReactMarkdown>
        </article>
      </div>
    </div>
  );
}}
'''

    def _update_hub_page(
        self,
        title: str,
        slug: str,
        summary: str,
        target_dir: Path,
        section_name: str
    ) -> Tuple[Optional[Path], Optional[Path]]:
        """Update or create hub page with article card."""
        hub_page_path = target_dir / "page.tsx"
        snippet_path = None

        if not hub_page_path.exists():
            # Create new hub page with this article
            target_dir.mkdir(parents=True, exist_ok=True)
            hub_content = self._generate_hub_with_article(
                section_name=section_name,
                title=title,
                slug=slug,
                summary=summary,
                clean_path=target_dir.relative_to(self.website_root)
            )

            with open(hub_page_path, "w", encoding="utf-8") as f:
                f.write(hub_content)

            logger.info(f"Created new hub page: {hub_page_path}")
            return hub_page_path, None

        # Hub exists - try to append card
        with open(hub_page_path, "r", encoding="utf-8") as f:
            hub_content = f.read()

        # Check if article already in hub
        if slug in hub_content:
            logger.info(f"Article already in hub: {slug}")
            return hub_page_path, None

        # Append to snippet file for manual insertion
        snippet_path = target_dir / "new_cards.snippet.txt"
        card_snippet = self.hub_manager.generate_section_snippet(
            section=section_name,
            title=title,
            slug=slug,
            summary=summary
        )

        with open(snippet_path, "a", encoding="utf-8") as f:
            f.write(card_snippet)

        logger.info(f"Hub page exists. Card snippet saved to: {snippet_path}")
        return hub_page_path, snippet_path

    def _generate_hub_with_article(
        self,
        section_name: str,
        title: str,
        slug: str,
        summary: str,
        clean_path: Path
    ) -> str:
        """Generate a hub page that includes the first article."""
        path_title = str(clean_path).split('/')[-1].replace('-', ' ').replace('_', ' ').title()

        return f'''import React from "react";
import Link from "next/link";
import {{ Card, CardHeader, CardTitle, CardDescription, CardFooter }} from "@/components/ui/card";
import {{ Button }} from "@/components/ui/button";
import {{ ArrowRight }} from "lucide-react";

export default function HubPage() {{
  return (
    <div className="min-h-screen bg-slate-50 py-12 px-6">
      <div className="max-w-6xl mx-auto space-y-12">
        <div className="space-y-4">
            <h1 className="text-4xl font-bold tracking-tight text-slate-900">{path_title} Hub</h1>
            <p className="text-lg text-slate-600">Generated content and resources.</p>
        </div>

        <section className="space-y-6">
            <h2 className="text-2xl font-semibold">{section_name}</h2>
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
      </div>
    </div>
  );
}}
'''

    def generate_card_snippet(
        self,
        title: str,
        summary: str,
        slug: str,
        section_path: str = "/ai",
        emoji: str = "📄"
    ) -> str:
        """
        Generate an AnimatedCard snippet for manual insertion.

        Args:
            title: Article title
            summary: Article summary
            slug: URL slug
            section_path: Section path for link
            emoji: Emoji icon for card

        Returns:
            TSX code snippet for AnimatedCard
        """
        return f'''
          <Link href='{section_path}/{slug}'>
            <AnimatedCard
              className='h-full group cursor-pointer text-center p-8'
              hoverEffect='lift'
              gradient
            >
              <div className='text-6xl mb-4 group-hover:scale-110 transition-transform duration-300'>
                {emoji}
              </div>
              <h3 className='text-2xl font-bold text-foreground mb-3'>
                {title}
              </h3>
              <p className='text-muted-foreground mb-4'>
                {summary or "Click to read more about " + title}
              </p>
              <div className='flex items-center justify-center text-primary group-hover:text-primary/80 transition-colors'>
                <span className='font-medium'>Learn More</span>
                <svg
                  className='w-4 h-4 ml-2 transition-transform group-hover:translate-x-1'
                  fill='none'
                  viewBox='0 0 24 24'
                  stroke='currentColor'
                >
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    strokeWidth={{2}}
                    d='M9 5l7 7-7 7'
                  />
                </svg>
              </div>
            </AnimatedCard>
          </Link>
'''
