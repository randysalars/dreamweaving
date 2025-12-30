import os
import sys
import logging
import datetime
from typing import Dict, Any, Optional

from config import Config
from notion_adapter import NotionAdapter
from monetization import MonetizationEngine
from codex_client import CodexClient
from publishers.hub import HubPageManager
from models import HubCard

logger = logging.getLogger(__name__)

class ContentProcessor:
    def __init__(self, notion: NotionAdapter, codex: CodexClient, monetization: MonetizationEngine, target_path: Optional[str] = None):
        self.notion = notion
        self.codex = codex
        self.monetization = monetization
        # Initialize hub manager if website root is configured
        if Config.WEBSITE_ROOT:
            self.hub_manager = HubPageManager(website_root=Config.WEBSITE_ROOT)
        else:
            self.hub_manager = None

        # Session-level cache for target path (pre-set from main.py or reused across articles)
        self._cached_target_path: Optional[str] = target_path

    def _humanize_path_segment(self, segment: str) -> str:
        return segment.replace("-", " ").replace("_", " ").strip().title() or "Hub"

    def _generate_hub_card(self, title: str, description: str, href: str) -> str:
        safe_title = title.replace("{", "").replace("}", "")
        safe_description = description.replace("{", "").replace("}", "")
        safe_href = href if href.startswith("/") else f"/{href.lstrip('/')}"
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

    def _ensure_parent_hub_lists_child_hub(self, web_ui_root: str, child_clean_path: str):
        """
        Ensures parent hub pages contain a card linking to this hub.
        Example: when generating `/ai/operations/...`, ensure `/ai` has a card for `/ai/operations`.
        """
        parts = [p for p in child_clean_path.split("/") if p]
        if len(parts) < 2:
            return

        parent_clean_path = "/".join(parts[:-1])
        child_segment = parts[-1]
        child_title = self._humanize_path_segment(child_segment)
        child_href = f"/{child_clean_path}"
        child_description = f"Browse {child_title} content and resources."

        parent_dir = os.path.join(web_ui_root, parent_clean_path)
        parent_page_path = os.path.join(parent_dir, "page.tsx")
        os.makedirs(parent_dir, exist_ok=True)

        if not os.path.exists(parent_page_path):
            parent_title = self._humanize_path_segment(parts[-2])
            default_parent = f"""import Link from "next/link";
import {{ Card, CardDescription, CardFooter, CardHeader, CardTitle }} from "@/components/ui/card";
import {{ Button }} from "@/components/ui/button";
import {{ ArrowRight }} from "lucide-react";

export default function HubPage() {{
  return (
    <div className="min-h-screen bg-slate-50 py-12 px-6">
      <div className="mx-auto max-w-6xl space-y-12">
        <div className="space-y-4">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900">{parent_title} Hub</h1>
          <p className="text-lg text-slate-600">Explore content hubs and generated resources.</p>
        </div>

        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">Sections</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {{/* HUB_CARDS_START */}}
{self._generate_hub_card(child_title, child_description, child_href)}
            {{/* HUB_CARDS_END */}}
          </div>
        </section>
      </div>
    </div>
  );
}}
"""
            with open(parent_page_path, "w", encoding="utf-8") as f:
                f.write(default_parent)
            logger.info(f"Created Parent Hub Page: {parent_page_path}")
            return

        with open(parent_page_path, "r", encoding="utf-8") as f:
            parent_content = f.read()

        if child_href in parent_content:
            return

        if "HUB_CARDS_START" in parent_content and "HUB_CARDS_END" in parent_content:
            end_marker = "{/* HUB_CARDS_END */}"
            if end_marker not in parent_content:
                end_marker = "{/* HUB_CARDS_END*/}"
            insert_at = parent_content.index(end_marker)
            card = self._generate_hub_card(child_title, child_description, child_href)
            updated = parent_content[:insert_at] + card + parent_content[insert_at:]
            with open(parent_page_path, "w", encoding="utf-8") as f:
                f.write(updated)
            logger.info(f"Updated Parent Hub Page with card: {parent_page_path} -> {child_href}")
            return

        snippet_path = os.path.join(parent_dir, "new_hubs.snippet.txt")
        with open(snippet_path, "a", encoding="utf-8") as f:
            f.write(self._generate_hub_card(child_title, child_description, child_href))
        logger.info(
            f"Parent hub exists but has no HUB_CARDS markers; appended snippet to: {snippet_path}"
        )
        print(
            f"[!] Parent hub page exists but has no HUB_CARDS markers. "
            f"Card snippet saved to {snippet_path} for manual insertion."
        )

    def generate_website_card_snippet(self, title: str, summary: str, slug: str, section_path: str = "/ai"):
        """
        Generates a Next.js code snippet for an AnimatedCard.
        """
        # Suggest an emoji based on title (simple heuristic or random)
        emoji = "📄"
        
        print(f"\n--- [Website Integration] ---")
        print(f"Generating card for: {title}")
        print(f"Target Section: {section_path}")
        
        # In a real agent, we might use LLM to pick a perfect emoji, but we'll ask the user or default
        try:
            # Check if interactive
            if sys.stdin.isatty():
                user_emoji = input(f"Enter an emoji icon for this card (default {emoji}): ").strip()
                if user_emoji:
                    emoji = user_emoji
        except Exception:
            pass
            
        snippet = f"""
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
"""
        print(f"\n✅ Copy/Paste this snippet into your page at {section_path}/page.js inside the Grid container:\n")
        print(snippet)
        print("-" * 30 + "\n")

    def process_article(self, article_metadata: Dict[str, Any]):
        """
        Main workflow for a single article.
        1. Parse Metadata
        2. Fetch full specs/content from Notion (Recursive)
        3. Detect Monetization opportunities
        4. Construct Prompt
        5. Generate Content
        6. Inject Monetization (if applicable)
        7. Save to file
        8. Update Notion status
        9. Generate Website Card Snippet
        """
        page_id = article_metadata["id"]
        
        # 1. Parse Metadata (Title, Topic, etc.)
        # Notion properties structure is deeply nested; robust extraction needed
        try:
            properties = article_metadata["properties"]
            title_prop = properties.get("Name") or properties.get("Title") or {}
            title = "Untitled"
            if title_prop.get("title"):
                title = title_prop["title"][0].get("plain_text", "Untitled")
            
            # Use 'Topic' or 'Category' property if available, else derive from title
            topic = title 
            
            logger.info(f"Processing candidate: '{title}' ({page_id})")

            # Interactive Confirmation - AUTO-APPROVED by user request
        # if sys.stdin.isatty():
        #     confirm = input(f"\n[?] Found candidate article: '{title}'. Generate content? [y/N] ").strip().lower()
        #     if confirm != 'y':
        #         logger.info(f"Skipping '{title}' by user request.")
        #         return
            logger.info(f"Auto-processing article: '{title}'")

            # Check for Virtual AI Task
            is_virtual = page_id.startswith("ai-task-")
            
            # Update status to In Progress (ONLY if it's a real DB item)
            is_manual = properties.get("Status", {}).get("select", {}).get("name") == "Manual Discovery"
            if not is_manual and not is_virtual:
                self.notion.update_status(page_id, "In Progress")

            # 2. Fetch Spec Content
            if is_virtual:
                # AI Task: Content is the 'Instructions' or Title
                # We cannot fetch from Notion because this page does not exist yet.
                spec_content = properties.get("Instructions", "") or title
                logger.info("Using AI Task instructions as spec content.")
            elif hasattr(self.notion, 'get_recursive_page_content'):
                spec_content = self.notion.get_recursive_page_content(page_id)
            else:
                spec_content = self.notion.get_page_content(page_id)

            if not spec_content:
                # Fallback: if it's a "Block Item" (single line task) or just empty
                if properties.get("Type") == "Block Item":
                    logger.info("Using block text as spec content.")
                    spec_content = title
                else:
                    logger.warning(f"No content found for '{title}'. Skipping.")
                    if not is_manual and not is_virtual: self.notion.update_status(page_id, "Error")
                    return

            # 3. Detect Monetization
            needs_monetization = False
            if Config.ENABLE_MONETIZATION:
                needs_monetization = self.monetization.detect_monetization_sections(spec_content)

            # 4. Construct Prompt
            prompt = self._construct_prompt(title, spec_content, needs_monetization)

            # 5. Generate Content
            logger.info(f"Generating content for '{title}'...")
            generated_content = self.codex.generate_article_content(prompt)

            # 6. Inject Monetization Elements
            if needs_monetization:
                logger.info("Injecting monetization elements...")
                elements = self.monetization.generate_monetization_elements(topic)
                
                parts = generated_content.split("\n\n")
                if len(parts) > 3:
                     # Inject ad after 3rd block
                    parts.insert(3, elements["inline_ad"])
                else:
                    parts.append(elements["inline_ad"])
                    
                parts.append(elements["landing_page"])
                
                generated_content = "\n\n".join(parts)

            # 7. Save to File
            safe_filename = "".join([c for c in title if c.isalnum() or c in (' ','-','_')]).strip().replace(' ', '_').lower() + ".md"
            output_path = os.path.join(Config.OUTPUT_DIR, safe_filename)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"---\ntitle: {title}\ndate: {datetime.date.today()}\n---\n\n")
                f.write(generated_content)
                
            logger.info(f"Saved generated article to: {output_path}")

            # 8. Update Status to Done
            if not is_manual and not is_virtual:
                self.notion.update_status(page_id, "Done")

            # 9. Interactive Website Integration
            slug = safe_filename.replace(".md", "")
            summary = "" # Placeholder

            # Check if running interactively or in batch mode
            try:
                # Batch mode: No interactive prompts, auto-accept everything
                is_batch_mode = getattr(Config, 'BATCH_MODE', False)
                is_interactive = sys.stdin.isatty() and not is_batch_mode

                if is_interactive or is_batch_mode:
                    print(f"\n[?] Website Integration for '{title}'")

                    if Config.TEST_MODE:
                        logger.info("[TEST MODE] Auto-filling website params: /ai/operations | Daily Work")
                        target_path_input = "/ai/operations"
                        section_input = "Daily Work"
                    elif is_batch_mode:
                        # BATCH MODE: No prompts, use cached or default path
                        if self._cached_target_path:
                            target_path_input = self._cached_target_path
                        else:
                            target_path_input = getattr(Config, 'DEFAULT_TARGET_PATH', '/ai')
                            self._cached_target_path = target_path_input
                        print(f"    ✓ [BATCH] Using path: {target_path_input}")

                        if target_path_input:
                            # Auto-categorize using AI (no override prompt in batch mode)
                            if self.hub_manager and getattr(Config, 'AUTO_CATEGORIZE', True):
                                print("    ⏳ Auto-categorizing article...")
                                existing_sections = self.hub_manager.get_existing_sections(target_path_input)
                                section_input = self.codex.categorize_article(
                                    title=title,
                                    content=generated_content,
                                    available_sections=existing_sections
                                )
                                print(f"    ✓ [BATCH] Category: {section_input}")
                            else:
                                # Default section in batch mode
                                section_input = "General"
                                print(f"    ✓ [BATCH] Using default section: {section_input}")
                    else:
                        # INTERACTIVE MODE: Use pre-configured path from main.py
                        target_path_input = self._cached_target_path or getattr(Config, 'DEFAULT_TARGET_PATH', '/ai')
                        print(f"    ✓ Using path: {target_path_input}")

                        if target_path_input:
                            # Auto-categorize using AI if hub manager is available
                            if self.hub_manager and getattr(Config, 'AUTO_CATEGORIZE', True):
                                print("    ⏳ Auto-categorizing article...")
                                existing_sections = self.hub_manager.get_existing_sections(target_path_input)
                                section_input = self.codex.categorize_article(
                                    title=title,
                                    content=generated_content,
                                    available_sections=existing_sections
                                )
                                print(f"    ✓ Category: {section_input}")

                                # Allow manual override in interactive mode only
                                override = input(f"    Section: '{section_input}' [Enter to accept, or type new]: ").strip()
                                if override:
                                    section_input = override
                            else:
                                # Fallback to manual input
                                section_input = input("    Section Name (e.g. 'Daily Work'): ").strip()

                    if target_path_input:
                        self.generate_website_artefacts(title, generated_content, slug, target_path_input, section_input, summary)

            except Exception as e:
                logger.warning(f"Could not run interactive card generation: {e}")

        except Exception as e:
            logger.error(f"Error processing article {page_id}: {e}", exc_info=True)
            is_virtual_err = str(page_id).startswith("ai-task-")
            if not is_manual and not is_virtual_err: 
                 self.notion.update_status(page_id, "Error")

    def generate_website_artefacts(self, title: str, content: str, slug: str, target_path_segment: str, section_name: str, summary: str = ""):
        """
        1. Creates Article Page (page.tsx)
        2. Creates/Updates Hub Page (page.tsx) with Card
        """
        try:
            # Resolve Base Path
            # Uses Config.WEBSITE_ROOT for stability across environments
            web_ui_root = Config.WEBSITE_ROOT
            logger.info(f"Targeting Website Root: {web_ui_root}")
            
            # Clean target path
            clean_path = target_path_segment.strip("/")
            target_dir = os.path.join(web_ui_root, clean_path)
            
            # --- 1. Create Article Page ---
            article_dir = os.path.join(target_dir, slug)
            os.makedirs(article_dir, exist_ok=True)
            
            article_page_path = os.path.join(article_dir, "page.tsx")
            
            # Escape content for TSX
            # Escape content for TSX template literals
            # Order matters: escape backslashes first, then special characters
            escaped_content = (
                content
                .replace('\\', '\\\\')  # Escape backslashes first
                .replace('`', '\\`')    # Escape backticks
                .replace('$', '\\$')    # Escape dollar signs
                .replace('{', '\\{')    # Escape opening braces
                .replace('}', '\\}')    # Escape closing braces
            )

            ts_content = f"""import ReactMarkdown from "react-markdown";
import {{ Card, CardContent }} from "@/components/ui/card";
import {{ Button }} from "@/components/ui/button";
import {{ ArrowLeft }} from "lucide-react";
import Link from "next/link";

const content = `{escaped_content}`;

export default function ArticlePage() {{
  return (
    <div className="min-h-screen bg-slate-50 py-12 px-6">
      <div className="max-w-4xl mx-auto space-y-8">
        <Link href="/{clean_path}">
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
"""
            with open(article_page_path, "w") as f:
                f.write(ts_content)
            logger.info(f"Created Article Page: {article_page_path}")

            # --- 2. Update/Create Hub Page using HubPageManager ---
            if self.hub_manager:
                # Ensure hub page exists
                self.hub_manager.ensure_hub_exists(clean_path)

                # Create article card
                card = HubCard(
                    title=title,
                    description=summary or "Read full article...",
                    href=f"/{clean_path}/{slug}",
                    emoji="📄"
                )

                # Add article to the appropriate section
                success = self.hub_manager.add_article_to_section(clean_path, section_name, card)

                if success:
                    logger.info(f"Added article card to hub section '{section_name}'")
                else:
                    logger.warning(f"Failed to add article card to hub - check hub page structure")

                # Ensure parent hub links to this hub path (e.g. /ai -> /ai/operations)
                self.hub_manager.ensure_parent_links_child(clean_path)
            else:
                logger.warning("No hub_manager configured - skipping hub page integration")

        except Exception as e:
            logger.error(f"Failed to generate website integration: {e}")

    def _construct_prompt(self, title: str, specs: str, monetization: bool) -> str:
        base_prompt = (
            f"Write a comprehensive, SEO-optimized article titled '{title}'.\n\n"
            f"Adhere strictly to the following content specifications and research notes:\n"
            f"{specs}\n\n"
            "Formatting Requirements:\n"
            "- Use proper H2 and H3 headers.\n"
            "- Maintain an engaging, professional tone.\n"
            "- Ensure deep coverage of the topic (AEO optimized).\n"
        )
        
        if monetization:
            base_prompt += (
                "\nCRITICAL INSTRUCTION:\n"
                "This topic is identified as High Value. "
                "Include persuasive sections that highlight the 'Speed' and 'Profit' aspects of the topic "
                "to set up for product recommendations. "
                "Focus on 'making the most cash in the least amount of time' strategies where appropriate."
            )
            
        return base_prompt
