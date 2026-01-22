import logging
from pathlib import Path
from ..core.context import ProductContext
from .components import SkepticAgent
# from .components import ChapterDrafter # Deprecated
from .writers_room import WritersRoom
from .reader_sim import ReaderSimulator
from .rubric_guard import RubricGuard
from ..packaging.audio import AudioScriptAgent
from ..packaging.video import VideoOrchestrator
import json

logger = logging.getLogger(__name__)

class SessionOrchestrator:
    """
    The Conductor.
    Runs the build loop:
    1. Identify next chapter
    2. Writer's Room (Multi-Agent Draft)
    3. Reader Simulation (Focus Group)
    4. Critique (Skeptic)
    5. Audio Scripting
    6. Video Planning
    7. Rubric Quality Gate
    8. Save & Update State
    """
    
    def __init__(self, context: ProductContext):
        self.context = context
        # Assuming templates are nearby, relative to this file
        self.templates_dir = Path(__file__).parent.parent / "templates"
        
        # Upgraded Pipeline Components
        self.writers_room = WritersRoom(self.templates_dir)
        self.skeptic = SkepticAgent(self.templates_dir)
        self.simulator = ReaderSimulator(self.templates_dir)
        self.rubric_guard = RubricGuard()
        self.audio_agent = AudioScriptAgent()
        self.video_agent = VideoOrchestrator()

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
        
        # 2. Production Loop (Draft -> Critique -> Verify -> Revise)
        attempts = 0
        max_attempts = 2
        feedback = []
        
        draft_content = ""
        
        while attempts <= max_attempts:
            # A. Draft (Writer's Room)
            if attempts > 0:
                logger.info(f"🔄 Redrafting Chapter {chapter_id} (Attempt {attempts + 1}/{max_attempts + 1})...")
            
            draft_content = self.writers_room.write_chapter(draft_context, feedback=feedback)
            
            # B. Reader Simulation
            focus_group_report = self.simulator.run_focus_group(draft_content, self.context.blueprint.promise.headline)
            logger.info(f"Focus Group Result: {focus_group_report['summary']}")
            
            # C. Rubric Quality Gate
            rubric_assessment = self.rubric_guard.evaluate(draft_content)
            
            if rubric_assessment.overall_verdict == "SHIP":
                logger.info("✅ Rubric Check PASSED (SHIP).")
                break # Exit loop, we have a winner
            else:
                logger.warning(f"❌ Rubric Check FAILED: {rubric_assessment.critical_issues}")
                feedback = rubric_assessment.critical_issues
                attempts += 1
                
                if attempts > max_attempts:
                    logger.warning("Max retries reached. Shipping best effort (or failing).")
                    # In strict mode we might raise Error, but for now we ship best effort
                    break

        # 4. Post-Production (Audio/Video) - Only run on the final draft
        critique = self.skeptic.review(draft_content, draft_context) # Keeping skeptic for logs, but not blocking
        
        # 8. Save
        self.context.update_chapter(
            chapter_id=chapter_id,
            content=draft_content,
            summary=f"Completed {chapter_spec.title}. Addressed {chapter_spec.purpose}."
        )
        
        # Save Multimedia Artifacts
        audio_path = self.context.staging_path / "chapters" / f"{chapter_id}_audio.xml"
        with open(audio_path, 'w') as f:
            f.write(audio_script)
            
        video_path = self.context.staging_path / "chapters" / f"{chapter_id}_video_plan.json"
        with open(video_path, 'w') as f:
             f.write(video_plan.model_dump_json(indent=2))
        
        logger.info(f"Chapter {chapter_id} saved (Text + Audio + Video).")
