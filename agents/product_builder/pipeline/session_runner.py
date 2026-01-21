import logging
from pathlib import Path
from ..core.context import ProductContext
from .components import ChapterDrafter, SkepticAgent

logger = logging.getLogger(__name__)

class SessionOrchestrator:
    """
    The Conductor.
    Runs the build loop:
    1. Identify next chapter
    2. Draft
    3. Critique
    4. Refine (optional loop)
    5. Save & Update State
    """
    
    def __init__(self, context: ProductContext):
        self.context = context
        # Assuming templates are nearby, relative to this file
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.drafter = ChapterDrafter(self.templates_dir)
        self.skeptic = SkepticAgent(self.templates_dir)

    def run_next_chapter(self):
        """
        Finds the next unfinished chapter and builds it.
        """
        if not self.context.blueprint:
            logger.error("No blueprint loaded in context.")
            return

        # Simple sequential check
        blueprint_chapters = self.context.blueprint.chapter_map
        completed = self.context.state.completed_chapters
        
        target_idx = len(completed)
        if target_idx >= len(blueprint_chapters):
            logger.info("All chapters completed!")
            return

        chapter_spec = blueprint_chapters[target_idx]
        chapter_id = f"chapter_{target_idx + 1:02d}"
        
        logger.info(f"Starting session for: {chapter_id} - {chapter_spec.title}")
        
        # 1. Prepare Context
        draft_context = {
            "chapter_number": target_idx + 1,
            "chapter_title": chapter_spec.title,
            "product_promise": self.context.blueprint.promise.headline,
            "audience_persona": self.context.blueprint.audience.current_state,
            "voice_rules": "\n".join(self.context.blueprint.voice_rules),
            "chapter_purpose": chapter_spec.purpose,
            "key_takeaways": "\n".join(chapter_spec.key_takeaways),
            "required_diagrams": ", ".join(chapter_spec.required_diagrams),
            "reference_material": "Reference excerpts would allow here..." 
        }
        
        # 2. Draft
        draft_content = self.drafter.draft(draft_context)
        
        # 3. Critique
        critique = self.skeptic.review(draft_content, draft_context)
        
        if critique["status"] == "FAIL":
            logger.info("Critique failed. Redrafting... (Simulated)")
            # In real system: feed critique back to drafter
            pass
            
        # 4. Save
        self.context.update_chapter(
            chapter_id=chapter_id,
            content=draft_content,
            summary=f"Completed {chapter_spec.title}. Addressed {chapter_spec.purpose}."
        )
        
        logger.info(f"Chapter {chapter_id} saved.")
