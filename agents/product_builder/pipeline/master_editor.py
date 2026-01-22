"""
MasterEditor Agent
Two-pass writing: transforms technically accurate content into beautiful content.
"""

import logging
from pathlib import Path
from typing import Dict, Optional

from ..core.llm import LLMClient

logger = logging.getLogger(__name__)


class MasterEditor:
    """
    Pass 2 of the writing process.
    Takes accurate content and adds rhythm, metaphor, and human soul.
    """
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.llm = LLMClient()
        self.template_path = templates_dir / "master_editor.md"
        
    def polish(self, draft: str, context: Dict) -> str:
        """
        Apply the human excellence pass to a draft.
        
        Args:
            draft: The technically accurate draft from WritersRoom
            context: Chapter context (purpose, emotion, insight)
            
        Returns:
            str: The polished, beautiful content
        """
        logger.info("✨ MasterEditor applying human excellence pass...")
        
        # Load template
        template = self._load_template()
        
        # Build context
        edit_context = {
            "current_draft": draft,
            "chapter_purpose": context.get("chapter_purpose", "Inform and inspire"),
            "target_emotion": context.get("target_emotion", "clarity"),
            "reader_energy": context.get("reader_energy", "neutral"),
            "core_insight": context.get("core_insight", "Understanding this changes everything"),
        }
        
        # Render prompt
        prompt = template.format(**edit_context)
        
        # Call LLM with slightly higher temperature for creativity
        polished = self.llm.generate(prompt, max_tokens=4000)
        
        # Validate output
        if not self._is_valid_output(polished, draft):
            logger.warning("MasterEditor output validation failed. Returning original draft.")
            return draft
        
        # Check for AI tells (basic heuristic)
        ai_tell_count = self._count_ai_tells(polished)
        if ai_tell_count > 3:
            logger.warning(f"⚠️ Output still has {ai_tell_count} AI tells. Consider additional pass.")
        
        logger.info("✅ MasterEditor pass complete.")
        return polished
    
    def _load_template(self) -> str:
        """Load the MasterEditor prompt template."""
        if self.template_path.exists():
            return self.template_path.read_text()
        else:
            logger.warning(f"Template not found at {self.template_path}")
            return self._fallback_template()
    
    def _is_valid_output(self, polished: str, original: str) -> bool:
        """
        Validate that the output is reasonable.
        - Not empty
        - Not drastically shorter
        - Contains actual content (not just meta-commentary)
        """
        if not polished or len(polished.strip()) < 100:
            return False
        
        # Should be at least 50% of original length
        if len(polished) < len(original) * 0.5:
            return False
        
        # Should not start with meta-commentary
        meta_starts = ["Here is", "I've edited", "The following", "Below is"]
        for start in meta_starts:
            if polished.strip().startswith(start):
                return False
        
        return True
    
    def _count_ai_tells(self, text: str) -> int:
        """Count common AI writing patterns."""
        ai_tells = [
            "it's important to note",
            "in today's fast-paced",
            "by leveraging",
            "it's worth mentioning",
            "in conclusion",
            "to summarize",
            "as we've discussed",
            "needless to say",
            "at the end of the day",
            "going forward",
        ]
        
        text_lower = text.lower()
        count = sum(1 for tell in ai_tells if tell in text_lower)
        return count
    
    def _fallback_template(self) -> str:
        """Minimal fallback template."""
        return """
Edit this draft to be more human and engaging:

{current_draft}

Make it flow beautifully. Remove robotic language. Add rhythm.
Return only the edited content.
"""
