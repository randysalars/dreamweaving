import logging
from pathlib import Path
from typing import Dict, Optional
from ..core.llm import LLMClient

logger = logging.getLogger(__name__)

class WritersRoom:
    """
    Orchestrates the multi-agent writing process.
    Replaces the single ChapterDrafter with a team of specialists.
    
    In Antigravity-native mode (prompts_only=True), writes prompts to files
    instead of generating content via an external LLM.
    """
    
    def __init__(self, templates_dir: Path, output_dir: Optional[Path] = None, prompts_only: bool = False):
        self.templates_dir = templates_dir
        self.roles = ["writers_head", "writers_story", "writers_teacher", "writers_editor"]
        self.prompts_only = prompts_only
        self.output_dir = output_dir
        
        if prompts_only and output_dir:
            from ..core.prompt_interface import PromptInterface
            self.prompt_interface = PromptInterface(output_dir)
            self.llm = None  # No LLM in prompts-only mode
            logger.info("📝 WritersRoom: Antigravity-native mode (prompts will be written to files)")
        else:
            self.llm = LLMClient()
            self.prompt_interface = None
        
    def write_chapter(self, context: Dict, feedback: list = None) -> str:
        """
        Runs the Fractal Generation logic:
        1. Architect: Break chapter into deep sections.
        2. Fractal Loop: Write each section individually (Head Writer -> Refiners).
        3. Stitch: Assemble the full chapter.
        """
        import json
        
        logger.info(f"Writer's Room Assembling for Chapter: {context.get('chapter_title')}...")
        
        # 0. Handle Feedback (If revision)
        if feedback:
            logger.info(f"⚠️ REVISION MODE. Feedback: {feedback}")
            feedback_str = "\n".join([f"- {item}" for item in feedback])
            context["feedback_instruction"] = (
                f"\n\nCRITICAL FEEDBACK FROM PREVIOUS DRAFT:\n{feedback_str}\n"
                "You MUST address these issues in this new draft."
            )
        else:
            context["feedback_instruction"] = ""

        # ─── FRACTAL STEP 1: STRUCTURE ──────────────────────────────
        logger.info("📐 Architecting Fractal Structure...")
        
        # In prompts_only mode, skip complex fractal structure and use single section
        if self.prompts_only:
            sections = [{"title": "Chapter Content", "north_star": context.get('chapter_purpose', 'Cover the topic in depth.')}]
            logger.info("✅ Using single-section structure (Antigravity-native mode)")
        else:
            structure_prompt = self._load_template("chapter_structure_architect").format(**context)
            structure_response = self.llm.generate(structure_prompt)
            
            try:
                # Extract JSON
                clean_response = structure_response.strip()
                import re
                
                # Strip markdown code blocks if present
                if "```" in clean_response:
                    clean_response = re.sub(r"^```(json)?\n", "", clean_response)
                    clean_response = re.sub(r"\n```$", "", clean_response)
                    clean_response = clean_response.strip()
                
                # Find JSON boundaries
                json_start = clean_response.find("{")
                json_end = clean_response.rfind("}") + 1
                
                if json_start != -1 and json_end > json_start:
                    sections_data = json.loads(clean_response[json_start:json_end])
                    sections = sections_data.get("sections", [])
                    logger.info(f"✅ Fractal Architect parsed {len(sections)} sections.")
                else:
                    raise ValueError("No JSON object found")

            except Exception as e:
                logger.warning(f"Failed to parse structure: {e}. Raw response: {structure_response[:100]}...")
                logger.warning("⚠️ Falling back to single-pass mode (Fractal Generation disabled).")
                sections = [{"title": "Main Content", "north_star": "Cover the chapter purpose in depth."}]

        # ─── FRACTAL STEP 2: DEEP DIVE WRITING ──────────────────────
        full_chapter_content = []
        
        for i, section in enumerate(sections):
            logger.info(f"✍️ Writing Section {i+1}/{len(sections)}: {section['title']}")
            
            # Create Section Context
            section_context = context.copy()
            section_context.update({
                "chapter_title": f"{context.get('chapter_title')}: {section['title']}",
                "chapter_purpose": f"SECTION GOAL: {section['north_star']}\n\nBROADER CHAPTER CONTEXT: {context.get('chapter_purpose')}",
                "key_takeaways": f"Section focus: {section['north_star']}" 
            })
            
            # Run the Relay for this SECTION
            section_draft = self._run_section_relay(section_context)
            full_chapter_content.append(section_draft)
        
        # ─── FRACTAL STEP 3: STITCHING ──────────────────────────────
        logger.info("🧵 Stitching Fractal components...")
        final_draft = "\n\n".join(full_chapter_content)
        
        return final_draft

    def _run_section_relay(self, context: Dict) -> str:
        """Run the standard team relay for a single section."""
        
        # 1. Head Writer (Creative Output)
        # logger.info("   [1/4] Head Writer drafting...") 
        current_draft = self._run_agent("writers_head", context)
        
        # 2. Story Producer (Refinement)
        # logger.info("   [2/4] Story Producer refining...")
        context["current_draft"] = current_draft
        current_draft = self._run_agent("writers_story", context)
        
        # 3. Teacher (Pedagogy)
        # logger.info("   [3/4] Teacher scaffolding...")
        context["current_draft"] = current_draft
        current_draft = self._run_agent("writers_teacher", context)
        
        # 4. Line Editor (Polish)
        # logger.info("   [4/4] Line Editor polishing...")
        context["current_draft"] = current_draft
        current_draft = self._run_agent("writers_editor", context)
        
        # Clean output of any markdown wrappers
        import re
        if "```" in current_draft:
            logger.info("🧹 Stripping markdown wrappers from draft...")
            current_draft = re.sub(r"^```(mdx|markdown)?\n", "", current_draft.strip())
            current_draft = re.sub(r"\n```$", "", current_draft.strip())
            
        return current_draft

    def _load_template(self, name: str) -> str:
        path = self.templates_dir / f"{name}.md"
        if path.exists():
            return path.read_text()
        return ""

    def _run_agent(self, role_name: str, context: Dict) -> str:
        """
        Runs an LLM call for a specific role.
        
        In prompts_only mode: Writes prompt to file for Antigravity to respond.
        In normal mode: Calls the LLM client.
        """
        template_path = self.templates_dir / f"{role_name}.md"
        if not template_path.exists():
            return f"# Error: Template {role_name} not found"
            
        # Load Template
        with open(template_path, 'r') as f:
            template_content = f.read()

        # Prepare Prompt
        try:
            logger.info(f"KEYS AVAILABLE for {role_name}: {list(context.keys())}")
            prompt = template_content.format(**context)
        except KeyError as e:
            logger.warning(f"Missing context key for template {role_name}: {e}")
            prompt = f"{template_content}\n\nCONTEXT:\n{context}"

        # --- ANTIGRAVITY-NATIVE MODE ---
        if self.prompts_only and self.prompt_interface:
            # Generate unique slug from context
            chapter_title = context.get('chapter_title', 'unknown').replace(' ', '_').lower()
            slug = f"{chapter_title}_{role_name}"
            
            prompt_path = self.prompt_interface.write_prompt(
                prompt=prompt,
                slug=slug,
                metadata={"role": role_name, "chapter": context.get('chapter_title')}
            )
            logger.info(f"📝 Prompt written: {prompt_path}")
            return f"[AWAITING_ANTIGRAVITY: {slug}]"
        
        # --- STANDARD LLM MODE ---
        logger.info(f"Generating content for {role_name}...")
        response = self.llm.generate(prompt)
        
        return response

