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
            
            logger.info(f"Processing article: '{title}' ({page_id})")
            
            # Update status to In Progress
            self.notion.update_status(page_id, "In Progress")

            # 2. Fetch Spec Content (Recursive!)
            # We use recursive fetch to ensure subpages are included as context
            if hasattr(self.notion, 'get_recursive_page_content'):
                spec_content = self.notion.get_recursive_page_content(page_id)
            else:
                spec_content = self.notion.get_page_content(page_id)

            if not spec_content:
                logger.warning(f"No content found for '{title}'. Skipping.")
                self.notion.update_status(page_id, "Error") 
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
            self.notion.update_status(page_id, "Done")

            # 9. Interactive Website Integration
            slug = safe_filename.replace(".md", "")
            summary = "" # Placeholder, could extract from content

            # Check if running interactively
            try:
                import sys
                if sys.stdin.isatty():
                    print(f"\n[?] Where should the card for '{title}' be located? (e.g. /ai)")
                    print("    (Press Enter to skip card generation)")
                    location = input("    Location: ").strip()
                    
                    if location:
                        self.generate_website_card_snippet(title, summary, slug, location)
            except Exception as e:
                logger.warning(f"Could not run interactive card generation: {e}")

        except Exception as e:
            logger.error(f"Error processing article {page_id}: {e}", exc_info=True)
            self.notion.update_status(page_id, "Error")

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
