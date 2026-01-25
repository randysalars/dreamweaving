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
from .bonus_content_templates import get_bonus_content

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
                elif "worksheet" in format_type or "workbook" in format_type:
                    path = self._generate_worksheet_bonus(title, description)
                    generated_paths.append(path)
                elif "audio" in format_type or "mp3" in format_type:
                    path = self._generate_audio_script_bonus(title, description)
                    generated_paths.append(path)
                else:
                    logger.warning(f"   ⚠️  Skipping unknown bonus format '{format_type}'")
                    
            except Exception as e:
                logger.error(f"❌ Failed to generate bonus '{title}': {e}", exc_info=True)
                
        return generated_paths

    def _generate_worksheet_bonus(self, title: str, description: str) -> str:
        """
        Generate a PDF Workbook with exercises.
        Strategy: First try pre-defined templates, then fall back to generic exercises.
        """
        logger.info(f"   📝 Generating Worksheet Bonus: {title}")
        
        # 1. Check for pre-defined template content (ensures unique content)
        template_content = get_bonus_content(title)
        if template_content:
            logger.info(f"   ✅ Using pre-defined template for: {title}")
            full_chapters = []
            for chapter in template_content.get('chapters', []):
                full_chapters.append({
                    "title": chapter['title'],
                    "content": chapter['content'].strip(),
                    "key_takeaways": []
                })
            
            # Generate PDF from template content
            config = PDFConfig(
                title=template_content.get('title', title),
                author="Randy Salars",
                output_path=str(self.output_dir / f"{self._slugify(title)}.pdf"),
                style=PDFStyle(heading_color="#2c5282", accent_color="#4299e1")
            )
            return self.pdf_generator.generate(full_chapters, config)
        
        # 2. Fall back to generic exercises
        exercises = [
            {"title": "Self-Assessment Audit", "purpose": "Understand current state"},
            {"title": "Goal Visualization", "purpose": "Define the destination"},
            {"title": "Barrier Identification", "purpose": "Spot obstacles"},
            {"title": "Action Planning", "purpose": "Define next steps"},
            {"title": "Accountability Contract", "purpose": "Commit to the plan"}
        ]

        
        # 2. Write Content
        full_chapters = []
        for i, exercise in enumerate(exercises):
            logger.info(f"      ✍️  Exercise {i+1}: {exercise['title']}")
            
            context = {
                "title": title,
                "chapter_title": exercise['title'],
                "chapter_purpose": exercise['purpose'],
                "product_name": title,
                "length_instruction": "Create a guided worksheet exercise. Include specific questions, fill-in-the-blank statements, and reflection prompts. Use formatting like [TYPE ANSWER HERE] or [CHECKBOX] to simulate a worksheet."
            }
            
            # Use raw LLM for worksheet specific format to avoid writer's room narrative bias
            prompt = f"""
            Write a worksheet exercise titled "{exercise['title']}".
            Purpose: {exercise['purpose']}
            Context: {description}
            
            Format as a professional coaching worksheet. 
            Include an introduction, 3-5 specific questions or activities, and a closing reflection.
            Use placeholders like [______________] for user input.
            """
            content = self.llm.generate(prompt)
            
            full_chapters.append({
                "title": exercise['title'],
                "content": content,
                "key_takeaways": ["Complete the self-audit.", "Be honest with your answers.", "Review quarterly."]
            })

        # 3. Compile PDF
        config = PDFConfig(
            title=title + " (Workbook)",
            author="SalarsNet",
            output_path=str(self.output_dir / f"{self._slugify(title)}.pdf"),
            style=PDFStyle(heading_color="#2c5282", accent_color="#4299e1") 
        )
        return self.pdf_generator.generate(full_chapters, config)

    def _generate_audio_script_bonus(self, title: str, description: str) -> str:
        """
        Generate a PDF Script for Audio.
        Strategy: 5 Tracks/Modules script.
        """
        logger.info(f"   🎙️  Generating Audio Script Bonus: {title}")
        
        tracks = [
            {"title": "Track 1: Introduction & Intent", "purpose": "Set the stage"},
            {"title": "Track 2: The Core Shift", "purpose": "Change perspective"},
            {"title": "Track 3: Guided Visualization", "purpose": "Mental rehearsal"},
            {"title": "Track 4: Affirmations", "purpose": "Reprogramming"},
            {"title": "Track 5: Daily Ritual", "purpose": "Integration"}
        ]
        
        full_chapters = []
        for i, track in enumerate(tracks):
            logger.info(f"      ✍️  Scripting {track['title']}")
            
            prompt = f"""
            Write a spoken-word script for audio recording.
            Title: {track['title']}
            Purpose: {track['purpose']}
            Context: {description}
            
            Tone: Soothing, authoritative, hypnotic, empowering.
            Include [PAUSE] markers and [EMPHASIZE] directives.
            Write in a spoken conversational rhythm.
            """
            content = self.llm.generate(prompt)
            
            full_chapters.append({
                "title": track['title'],
                "content": content,
                "key_takeaways": ["Listen daily.", "Internalize the shift.", "Practice the ritual."]
            })

        # 3. Compile PDF
        config = PDFConfig(
            title=title + " (Audio Transcript)",
            author="SalarsNet",
            output_path=str(self.output_dir / f"{self._slugify(title)}.pdf"),
            style=PDFStyle(heading_color="#276749", accent_color="#48bb78") 
        )
        return self.pdf_generator.generate(full_chapters, config)

    def _generate_pdf_bonus(self, title: str, description: str) -> str:
        """
        Generate a massive PDF bonus (>50 pages).
        Strategy: First try pre-defined templates for known bonus types,
                  then fall back to LLM-generated content.
        """
        logger.info(f"   📄 Expanding PDF Bonus: {title}")
        
        # 1. Check for pre-defined template content (ensures unique content per bonus type)
        template_content = get_bonus_content(title)
        if template_content:
            logger.info(f"   ✅ Using pre-defined template for: {title}")
            full_chapters = []
            for chapter in template_content.get('chapters', []):
                full_chapters.append({
                    "title": chapter['title'],
                    "content": chapter['content'].strip(),
                    "key_takeaways": []
                })
            
            # Generate PDF from template content
            config = PDFConfig(
                title=template_content.get('title', title),
                author="Randy Salars",
                output_path=str(self.output_dir / f"{self._slugify(title)}.pdf"),
                style=PDFStyle(heading_color="#1e3a5f", accent_color="#2ecc71")
            )
            return self.pdf_generator.generate(full_chapters, config)
        
        # 2. Fall back to LLM-generated outline (original behavior)
        logger.info("   🎯 Goal: 50+ pages (approx 10-12 deep chapters)")
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
                "key_takeaways": "Master the key ideas of this section.", # Dummy takeaways for structure gen
                "audience_state": "Eager to learn", # Generic for bonus
                "tone_voice": "Authoritative, extremely detailed, actionable, expansive",
                # Add missing keys for templates
                "product_promise": f"Master {title}",
                "product_name": title,
                "audience_pain_points": "Lack of in-depth knowledge, need for actionable steps",
                "transformation_from": "Novice",
                "transformation_to": "Expert",
                "length_instruction": "WRITE AN EXTREMELY LONG, COMPREHENSIVE NARRATIVE CHAPTER. Aim for 2000+ words. Go deep into theory, then practice, then examples. Leave no stone unturned.\n\nCRITICAL CONSTRAINTS:\n1. NO CODE BLOCKS.\n2. NO PYTHON SCRIPTS.\n3. WRITE IN PLAIN ENGLISH ONLY."
            }
            
            # Use Writer's Room to generate deep content
            content = self.writers_room.write_chapter(context)
            
            full_chapters.append({
                "title": chapter_meta['title'],
                "content": content,
                "key_takeaways": self._extract_takeaways(content, chapter_meta['title'])
            })
            
            # 2.5 Generate Visuals for Bonus Chapters
            visuals = {}
            # Lazy load visuals generator
            from .code_visuals import CodeVisualsGenerator
            visuals_dir = self.output_dir / "visuals"
            visuals_dir.mkdir(exist_ok=True)
            cv_gen = CodeVisualsGenerator(visuals_dir)
            
            logger.info(f"   📊 Generating Charts/Diagrams for Bonus...")
            slug = self._slugify(title)

            for i, ch in enumerate(full_chapters):
                # Ask LLM for a specific process flow for this chapter
                try:
                    visual_prompt = f"""
                    Based on the following chapter content, define a simple process flow (3-5 steps).
                    Format: "Step 1 -> Step 2 -> Step 3"
                    Content: {ch['content'][:1500]}...
                    """
                    visual_desc = self.llm.generate(visual_prompt).strip()
                    # Fallback if too verbose
                    if len(visual_desc) > 100 or "->" not in visual_desc:
                         visual_desc = f"Start -> {ch['title']} -> Success"
                    
                    section_id = f"{slug}_ch{i+1}_visual"
                    
                    # Generate deterministically
                    # Inject Title for Context-Aware Visual Mocking
                    context_desc = f"Topic: {title} - {ch['title']}. Process: {visual_desc}"
                    path = cv_gen.generate(section_id, context_desc, "diagram")
                    
                    # Map to opener ID for PDF generator
                    opener_id = f"ch{i+1}_opener"
                    visuals[opener_id] = str(path)
                    
                except Exception as e:
                    logger.warning(f"Failed to generate bonus visual {i}: {e}")

        # 3. Compile PDF
        logger.info(f"   🖨️  Compiling Bonus PDF...")
        config = PDFConfig(
            title=title,
            author="SalarsNet",
            output_path=str(self.output_dir / f"{self._slugify(title)}.pdf"),
            style=PDFStyle(heading_color="#1a202c", accent_color="#3182ce") 
        )
        
        return self.pdf_generator.generate(full_chapters, config, visuals)

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
        
        # Retry loop for outline generation
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.llm.generate(prompt)
                
                # Clean and parse JSON
                clean = response.strip()
                import re
                if "```" in clean:
                    clean = re.sub(r"^```(json)?\n", "", clean)
                    clean = re.sub(r"\n```$", "", clean)
                
                import json
                data = json.loads(clean)
                chapters = data.get("chapters", [])
                
                # Validation
                if len(chapters) >= 5:
                    return chapters
                
                logger.warning(f"   ⚠️  Outline attempt {attempt+1} too short ({len(chapters)} chapters). Retrying...")
                
            except Exception as e:
                logger.warning(f"   ⚠️  Outline attempt {attempt+1} failed: {e}")
        
        logger.error("❌ All outline attempts failed. Using fallback.")
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

    def _extract_takeaways(self, content: str, chapter_title: str) -> List[str]:
        """Extract 3 actionable takeaways from the content."""
        prompt = f"""
        Context: Chapter "{chapter_title}"
        
        Extract 3 short, actionable takeaways (1 sentence each) specifically from the text below.
        Do NOT give generic advice. Use the actual content provided.
        
        Format:
        - Takeaway 1
        - Takeaway 2
        - Takeaway 3
        
        Text:
        {content[:3000]}...
        """
        response = self.llm.generate(prompt)
        takeaways = [
            line.strip("- *").strip() 
            for line in response.split("\n") 
            if line.strip().startswith("-") or line.strip().startswith("*")
        ]
        return takeaways[:3] if takeaways else ["Master the core concepts.", "Apply the strategy.", "Review your progress."]

    def _slugify(self, text: str) -> str:
        return "".join(c if c.isalnum() or c == " " else "" for c in text).replace(" ", "_").lower()
