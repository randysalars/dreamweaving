import os
import sys
import logging
import datetime
from typing import Dict, Any

from config import Config
from notion_adapter import NotionAdapter
from monetization import MonetizationEngine
from codex_client import CodexClient

logger = logging.getLogger(__name__)

class ContentProcessor:
    def __init__(self, notion: NotionAdapter, codex: CodexClient, monetization: MonetizationEngine):
        self.notion = notion
        self.codex = codex
        self.monetization = monetization

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

            # Check if running interactively
            try:
                if sys.stdin.isatty():
                    # 9a. Prompt for Target Path if not already set (conceptually, we might want to do this once per batch in main.py, 
                    # but doing it here allows per-article flexibility or we can use a class-level cache)
                    
                    # For this implementation, we'll ask locally if not provided in env, 
                    # OR we keeps it simple: Ask every time or use a default? 
                    # The user request implies a sequential flow: Source -> Target Path -> Section.
                    # Let's prompt.
                    
                    print(f"\n[?] Website Integration for '{title}'")
                    
                    if Config.TEST_MODE:
                        logger.info("[TEST MODE] Auto-filling website params: /ai/operations | Daily Work")
                        target_path_input = "/ai/operations"
                        section_input = "Daily Work"
                    else:
                        print("    Target Path (e.g. '/ai') or local path relative to web-ui/src/app")
                        target_path_input = input("    Path [Skip]: ").strip()
                        if target_path_input:
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
            # Assuming agent is in agents/notion_content_agent/
            # and web-ui is in projects/dreamweaving/web-ui/
            
            # We are at: /home/rsalars/Projects/dreamweaving/agents/notion_content_agent/processor.py
            # Config.OUTPUT_DIR is likely somewhere? 
            # Let's resolve relative to current working directory (usually agent dir)
            
            # Better to find project root.
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            web_ui_root = os.path.join(project_root, "web-ui", "src", "app")
            
            # Clean target path
            clean_path = target_path_segment.strip("/")
            target_dir = os.path.join(web_ui_root, clean_path)
            
            # --- 1. Create Article Page ---
            article_dir = os.path.join(target_dir, slug)
            os.makedirs(article_dir, exist_ok=True)
            
            article_page_path = os.path.join(article_dir, "page.tsx")
            
            # Escape content for TSX
            # Simple escape for backticks and braces which might confuse React
            # For a robust solution, we might pass raw content to a component, but here we inline it.
            # actually, using a component is safer.
            
            ts_content = f"""import React from "react";
import ReactMarkdown from "react-markdown";
import {{ Card, CardContent }} from "@/components/ui/card";
import {{ Button }} from "@/components/ui/button";
import {{ ArrowLeft }} from "lucide-react";
import Link from "next/link";

const content = `{content.replace('`', '\`').replace('$', '\$')}`;

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


            # --- 2. Update/Create Hub Page ---
            hub_page_path = os.path.join(target_dir, "page.tsx")
            
            if not os.path.exists(hub_page_path):
                # Create Default Hub Page
                os.makedirs(target_dir, exist_ok=True)
                default_hub = f"""import React from "react";
import Link from "next/link";
import {{ Card, CardHeader, CardTitle, CardDescription, CardFooter }} from "@/components/ui/card";
import {{ Button }} from "@/components/ui/button";
import {{ ArrowRight }} from "lucide-react";

export default function HubPage() {{
  return (
    <div className="min-h-screen bg-slate-50 py-12 px-6">
      <div className="max-w-6xl mx-auto space-y-12">
        <div className="space-y-4">
            <h1 className="text-4xl font-bold tracking-tight text-slate-900">{clean_path.split('/')[-1].title()} Hub</h1>
            <p className="text-lg text-slate-600">Generated content and resources.</p>
        </div>
        
        {self._generate_section_snippet(section_name, title, slug, summary)}
      </div>
    </div>
  );
}}
"""
                with open(hub_page_path, "w") as f:
                    f.write(default_hub)
                logger.info(f"Created New Hub Page: {hub_page_path}")
                
            else:
                # Append to existing
                # For naive implementation: Read, check if section exists, inject card.
                # Parsing standard TSX is hard with regex. 
                # We will append a simplistic placeholder comment or just verify manual entry needed
                # BUT the user asked for automation.
                # Let's try to append AFTER the last </section> or inside the last </div> if we can parse it?
                # Simpler: Append to a known list?
                # Safest for now: Append to END of file inside invalid comment? No that breaks build.
                
                # Let's read file, look for our Section Heading.
                with open(hub_page_path, "r") as f:
                    hub_content = f.read()
                
                card_snippet = f"""
        {self._generate_section_snippet(section_name, title, slug, summary)}
"""
                # Naive injection: Insert before last </div> </div> (closing main tags)
                # This is risky.
                
                # Safer Strategy: Warn user?
                # Or simplistic regex replacement ?
                
                # Let's just log instructions for now to avoid breaking existing complex pages.
                # actually, lets append it to a "autogen.log" in the dir so they can copy paste
                
                snippet_path = os.path.join(target_dir, "new_cards.snippet.tsx")
                with open(snippet_path, "a") as f:
                    f.write(card_snippet)
                
                logger.info(f"Hub Page exists. Appended card snippet to: {snippet_path}")
                print(f"[!] Hub page exists. Code snippet saved to {snippet_path} for manual insertion.")

        except Exception as e:
            logger.error(f"Failed to generate website integration: {e}")

    def _generate_section_snippet(self, section, title, slug, summary=""):
        return f"""
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
        """

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
