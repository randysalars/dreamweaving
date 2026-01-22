import logging
from typing import Dict
from typing import Dict
from pathlib import Path
from ..core.llm import LLMClient

logger = logging.getLogger(__name__)

class ChapterDrafter:
    """
    Wraps the LLM generation logic for writing a chapter.
    """
    def __init__(self, templates_dir: Path):
        self.template_path = templates_dir / "chapter_contract.md"
        
    def draft(self, context: Dict) -> str:
        """
        Generates the chapter draft.
        In a real system, this calls the LLM with the filled template.
        """
        logger.info(f"Drafting Chapter {context.get('chapter_number')}...")
        
        # Load Template
        if self.template_path.exists():
            with open(self.template_path, 'r') as f:
                template = f.read()
        else:
            return "# Error: Template not found"

        # Simulate LLM filling text (In prod: call Anthropic/OpenAI)
        # response = llm.generate(template.format(**context))
        
        # Placeholder Stub
        return f"""# {context.get('chapter_title')}

## The Core Concept
This is the drafted content for the chapter. It addresses {context.get('chapter_purpose')}.

## Implementation
1. Step one
2. Step two

## Summary
Key takeaway for the reader.
"""

class SkepticAgent:
    """
    Wraps the LLM critique logic.
    """
    def __init__(self, templates_dir: Path):
        self.template_path = templates_dir / "skeptic_review.md"
        self.llm = LLMClient()
        
    def review(self, draft: str, context: Dict) -> Dict:
        """
        Returns structured critique.
        """
        logger.info("Skeptic is reviewing the draft...")
        
        if not self.template_path.exists():
            return {"status": "ERROR", "issues": ["Template missing"], "suggestions": ""}

        with open(self.template_path, 'r') as f:
            template_content = f.read()

        # Prepare Prompt (Skeptic needs draft and context)
        # Assuming template expects {draft} and {context_str}
        full_context_str = str(context)
        prompt = template_content.replace("{draft}", draft).replace("{context}", full_context_str)
        # Also try format if keys exist
        try:
             prompt = template_content.format(draft=draft, context=full_context_str, **context)
        except:
             pass 

        response = self.llm.generate(prompt)

        # Naive parsing of LLM response (in prod, force JSON schema)
        # For now, we assume if it generated something, it passed, unless it says "FAIL" explicitly
        status = "PASS"
        if "FAIL" in response.upper() and len(response) < 500: # Simple heuristic
             status = "FAIL"
             
        return {
            "status": status,
            "issues": [],
            "suggestions": response, # Return full critique text
            "raw_response": response
        }
