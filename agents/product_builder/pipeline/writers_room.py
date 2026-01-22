import logging
from pathlib import Path
from typing import Dict
from ..core.llm import LLMClient

logger = logging.getLogger(__name__)

class WritersRoom:
    """
    Orchestrates the multi-agent writing process.
    Replaces the single ChapterDrafter with a team of specialists.
    """
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.roles = ["writers_head", "writers_story", "writers_teacher", "writers_editor"]
        self.llm = LLMClient()
        
    def write_chapter(self, context: Dict, feedback: list = None) -> str:
        """
        Runs the full relay:
        Head Writer -> Story Producer -> Teacher -> Line Editor
        
        Optional feedback triggers a revision mindset.
        """
        logger.info(f"Writer's Room Assembling for Chapter {context.get('chapter_number')}...")
        
        current_draft = ""
        
        # 0. Handle Feedback (If revision)
        if feedback:
            logger.info(f"⚠️ REVISION MODE. Feedback: {feedback}")
            # Inject feedback into the context so the Head Writer knows to fix it
            feedback_str = "\n".join([f"- {item}" for item in feedback])
            context["feedback_instruction"] = (
                f"\n\nCRITICAL FEEDBACK FROM PREVIOUS DRAFT:\n{feedback_str}\n"
                "You MUST address these issues in this new draft."
            )
        else:
            context["feedback_instruction"] = ""
        
        # 1. Head Writer (Creative Output from scratch)
        logger.info("[1/4] Head Writer drafting...")
        current_draft = self._run_agent("writers_head", context)
        
        # 2. Story Producer (Refinement)
        logger.info("[2/4] Story Producer refining...")
        context["current_draft"] = current_draft
        current_draft = self._run_agent("writers_story", context)
        
        # 3. Teacher (Pedagogy)
        logger.info("[3/4] Teacher scaffolding...")
        context["current_draft"] = current_draft
        current_draft = self._run_agent("writers_teacher", context)
        
        # 4. Line Editor (Polish)
        logger.info("[4/4] Line Editor polishing...")
        context["current_draft"] = current_draft
        current_draft = self._run_agent("writers_editor", context)
        
        return current_draft

    def _run_agent(self, role_name: str, context: Dict) -> str:
        """
        Simulates an LLM call for a specific role.
        In prod, this would load the template and call the API.
        """
        template_path = self.templates_dir / f"{role_name}.md"
        if not template_path.exists():
            return f"# Error: Template {role_name} not found"
            
        # Load Template
        with open(template_path, 'r') as f:
            template_content = f.read()

        # Prepare Prompt
        # We assume templates use {variable} syntax for python format
        try:
            prompt = template_content.format(**context)
        except KeyError as e:
            logger.warning(f"Missing context key for template {role_name}: {e}")
            # Fallback: Just append the context as a dump if format fails
            prompt = f"{template_content}\n\nCONTEXT:\n{context}"

        logger.info(f"Generating content for {role_name}...")
        response = self.llm.generate(prompt)
        
        return response
