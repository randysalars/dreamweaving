import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

class WritersRoom:
    """
    Orchestrates the multi-agent writing process.
    Replaces the single ChapterDrafter with a team of specialists.
    """
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.roles = ["writers_head", "writers_story", "writers_teacher", "writers_editor"]
        
    def write_chapter(self, context: Dict) -> str:
        """
        Runs the full relay:
        Head Writer -> Story Producer -> Teacher -> Line Editor
        """
        logger.info(f"Writer's Room Assembling for Chapter {context.get('chapter_number')}...")
        
        current_draft = ""
        
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
            
        # Simulate transformation based on role
        # Ideally, we call the LLM here.
        
        role_label = role_name.replace("writers_", "").title()
        
        # Base Draft Simulation (If first pass)
        if role_name == "writers_head":
             return f"""# {context.get('chapter_title')}

## The Core Concept
The Head Writer says: This chapter is about {context.get('chapter_purpose')}.

## Implementation
1. Step one
2. Step two
"""

        # Refinement Simulation
        previous_content = context.get("current_draft", "")
        addition = f"\n> ({role_label} Pass: Enhanced content with specific focus.)"
        
        return previous_content + addition
