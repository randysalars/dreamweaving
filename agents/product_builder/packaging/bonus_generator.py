"""
Bonus Generator
Generates actual content for bonuses, ensuring high value and volume (50+ pages for PDFs).
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..core.llm import LLMClient
from ..schemas.bonus_plan import Bonus
from ..pipeline.writers_room import WritersRoom
from .pdf_generator import PDFGenerator, PDFConfig, PDFStyle

logger = logging.getLogger(__name__)

class BonusGenerator:
    """
    Generates content for standard bonuses.
    CRITICAL REQUIREMENT: PDF bonuses must be substantial (50+ pages).
    """
    
    def __init__(self, templates_dir: Path, output_dir: Path):
        self.templates_dir = templates_dir
        self.output_dir = output_dir
        self.llm = LLMClient()
        self.writers_room = WritersRoom(templates_dir)
        self.pdf_generator = PDFGenerator(output_dir)
        
    def generate(self, bonuses: List[Dict[str, Any]]) -> List[str]:
        """
        Generate content for a list of bonuses.
        
        Args:
            bonuses: List of bonus dictionaries (usually from landing page JSON)
            
        Returns:
            List of paths to generated bonus files
        """
        generated_paths = []
        
        logger.info(f"🎁 Generating {len(bonuses)} bonuses...")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        for bonus_data in bonuses:
            try:
                # Normalize bonus data
                title = bonus_data.get("title", "Untitled Bonus")
                format_type = bonus_data.get("format", "pdf").lower()
                description = bonus_data.get("description", "")
                
                logger.info(f"   Generating Bonus: {title} ({format_type})")
                
                if "pdf" in format_type or "ebook" in format_type or "guide" in format_type:
                    path = self._generate_pdf_bonus(title, description)
                    generated_paths.append(path)
                else:
                    logger.warning(f"   ⚠️  Skipping non-PDF bonus format '{format_type}' (Not yet implemented)")
                    
            except Exception as e:
                logger.error(f"❌ Failed to generate bonus '{title}': {e}", exc_info=True)
                
        return generated_paths

    def _generate_pdf_bonus(self, title: str, description: str) -> str:
        """
        Generate a massive PDF bonus (>50 pages).
        Strategy: Treat it as a mini-course with 10-12 chapters.
        """
        logger.info(f"   📄 Expanding PDF Bonus: {title}")
        logger.info("   🎯 Goal: 50+ pages (approx 10-12 deep chapters)")
        
        # 1. Outline the "Mini-Course"
        chapters_outline = self._outline_bonus_chapters(title, description)
        logger.info(f"   📝 Outlined {len(chapters_outline)} chapters for bonus.")
        
        # 2. Write Content (Fractal Generation Reuse)
        full_chapters = []
        for i, chapter_meta in enumerate(chapters_outline):
            logger.info(f"      ✍️  Bonus Chapter {i+1}/{len(chapters_outline)}: {chapter_meta['title']}")
            
            # Construct context for Writer's Room
            context = {
                "title": title, # Product title (Bonus title)
                "chapter_title": chapter_meta['title'],
                "chapter_number": i + 1,
                "chapter_purpose": chapter_meta['purpose'],
                "key_takeaways": "Master the core concepts of this section.", # Dummy takeaways for structure gen
                "audience_state": "Eager to learn", # Generic for bonus
                "tone_voice": "Authoritative, extremely detailed, actionable, expansive",
                # Add missing keys for templates
                "product_promise": f"Master {title}",
                "product_name": title,
                "audience_pain_points": "Lack of in-depth knowledge, need for actionable steps",
                "transformation_from": "Novice",
                "transformation_to": "Expert",
                "length_instruction": "WRITE AN EXTREMELY LONG, COMPREHENSIVE CHAPTER. Aim for 2000+ words per chapter. Go deep into theory, then practice, then examples. Leave no stone unturned."
            }
            
            # Use Writer's Room to generate deep content
            content = self.writers_room.write_chapter(context)
            
            full_chapters.append({
                "title": chapter_meta['title'],
                "content": content,
                "key_takeaways": self._extract_takeaways(content)
            })
            
        # 3. Compile PDF
        logger.info(f"   🖨️  Compiling Bonus PDF...")
        config = PDFConfig(
            title=title,
            author="SalarsNet",
            output_path=str(self.output_dir / f"{self._slugify(title)}.pdf"),
            style=PDFStyle(heading_color="#1a202c", accent_color="#3182ce") # Different style for bonuses?
        )
        
        return self.pdf_generator.generate(full_chapters, config)

    def _outline_bonus_chapters(self, title: str, description: str) -> List[Dict[str, str]]:
        """
        Use LLM to break the bonus topic into 12-15 substantial chapters.
        """
        prompt = f"""
        You are an expert instructional designer.
        
        We need to create a "Deep Dive" bonus guide titled: "{title}"
        Description: {description}
        
        CRITICAL GOAL: This must be a MASSIVE manual (50+ pages).
        Design an outline with **12 to 15 distinct, meaty chapters**.
        Each chapter must be substantial.
        
        Return JSON format:
        {{
            "chapters": [
                {{ "title": "Chapter 1 Title", "purpose": "Detailed description..." }},
                ...
            ]
        }}
        """
        
        response = self.llm.generate(prompt)
        
        import json
        import re
        
        try:
            # Clean and parse JSON
            clean = response.strip()
            if "```" in clean:
                clean = re.sub(r"^```(json)?\n", "", clean)
                clean = re.sub(r"\n```$", "", clean)
            
            data = json.loads(clean)
            chapters = data.get("chapters", [])
            
            # Fallback if too few chapters
            if len(chapters) < 5:
                # If LLM failed to give enough, we duplicate/expand logic or just accept (for now, let's accept but warn)
                logger.warning(f"   ⚠️  Outline only has {len(chapters)} chapters. Might not reach 50 pages.")
                
            return chapters
            
        except Exception as e:
            logger.error(f"Failed to outline bonus: {e}")
            # Fallback outline
            return [
                {"title": "Introduction", "purpose": "Overview of the strategy"},
                {"title": "Core Concepts", "purpose": "Deep dive into fundamentals"},
                {"title": "Strategy Part 1", "purpose": "First phase of execution"},
                {"title": "Strategy Part 2", "purpose": "Second phase of execution"},
                {"title": "Strategy Part 3", "purpose": "Final phase of execution"},
                {"title": "Advanced Tactics", "purpose": "Leveling up"},
                {"title": "Common Mistakes", "purpose": "What to avoid"},
                {"title": "Case Studies", "purpose": "Real world examples"},
                {"title": "Tools and Resources", "purpose": "What you need"},
                {"title": "Action Plan", "purpose": "30 day roadmap"}
            ]

    def _extract_takeaways(self, content: str) -> List[str]:
        """Simple helper to extract takeaways or generate dummy ones."""
        # Ideally we'd use LLM, but for speed let's just grab headers or return generic
        return ["Actionable Insight 1", "Actionable Insight 2", "Actionable Insight 3"]

    def _slugify(self, text: str) -> str:
        return "".join(c if c.isalnum() or c == " " else "" for c in text).replace(" ", "_").lower()
