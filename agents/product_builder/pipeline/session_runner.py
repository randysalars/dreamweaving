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
        
        # 2. Draft (Writer's Room Upgrade)
        draft_content = self.writers_room.write_chapter(draft_context)
        
        # 3. Reader Simulation (The Upgrade)
        focus_group_report = self.simulator.run_focus_group(draft_content, self.context.blueprint.promise.headline)
        logger.info(f"Focus Group Result: {focus_group_report['summary']}")
        
        # 4. Critique
        critique = self.skeptic.review(draft_content, draft_context)
        
        if critique["status"] == "FAIL":
            logger.info("Critique failed. Redrafting... (Simulated)")
            # In real system: feed critique back to drafter
            pass
            
        # 5. Audio Scripting (The Upgrade)
        audio_script = self.audio_agent.generate_script(chapter_spec.title, draft_content)
        
        # 6. Video Planning (The Upgrade v2)
        video_plan = self.video_agent.generate_plan(chapter_spec.title, draft_content, audio_script)
            
        # 7. Rubric Quality Gate (The Upgrade v3)
        rubric_assessment = self.rubric_guard.evaluate(draft_content)
        if rubric_assessment.overall_verdict == "REVISE":
             logger.warning(f"Rubric Check FAILED: {rubric_assessment.critical_issues}")
             # In prod, we would loop back to WritersRoom here.
        else:
             logger.info("✅ Rubric Check PASSED (SHIP).")
        
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
