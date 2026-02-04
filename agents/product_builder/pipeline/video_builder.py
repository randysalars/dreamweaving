"""
Video Builder Pipeline for SalarsNet Educational Videos

Orchestrates the complete video build process:
1. Generate lesson JSON from content
2. Generate audio segments via Coqui TTS
3. Resolve image/icon assets
4. Generate SRT captions
5. Render via Remotion
"""

import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from .lesson_generator import LessonGenerator, LessonBlueprint

logger = logging.getLogger(__name__)


@dataclass
class VideoAssets:
    """Resolved assets for a lesson video."""
    audio_paths: Dict[str, Path]  # scene_id -> audio file
    image_paths: Dict[str, Path]  # asset_key -> image file
    caption_paths: Dict[str, Path]  # scene_id -> srt file


@dataclass
class VideoBuildResult:
    """Result of a video build."""
    success: bool
    video_path: Optional[Path] = None
    blueprint_path: Optional[Path] = None
    assets: Optional[VideoAssets] = None
    error: Optional[str] = None


class VideoBuilder:
    """
    Orchestrates the complete video build pipeline.
    
    Connects the lesson generator, asset generators (TTS, images),
    and Remotion renderer into a unified build system.
    """
    
    def __init__(
        self,
        output_dir: Path = None,
        remotion_project_path: Path = None,
        coqui_enabled: bool = True,
        coqui_model: str = "tts_models/en/ljspeech/tacotron2-DDC"
    ):
        self.output_dir = output_dir or Path("./generated_videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.remotion_project_path = remotion_project_path or (
            Path(__file__).parent.parent / "remotion_project"
        )
        
        self.lesson_generator = LessonGenerator()
        self.coqui_enabled = coqui_enabled
        self.coqui_model = coqui_model
    
    def build_from_content(
        self,
        chapter_id: str,
        title: str,
        goal: str,
        content: str,
        keywords: List[str] = None,
        check_question: str = None,
        check_answer: str = None,
        next_preview: str = None,
        level: str = "beginner",
        skip_audio: bool = False,
        skip_render: bool = False
    ) -> VideoBuildResult:
        """
        Build a complete lesson video from content.
        
        This is the main entry point for the video build pipeline.
        
        Args:
            chapter_id: Unique lesson identifier
            title: Lesson title
            goal: Single-sentence learning goal
            content: Main explanation content
            keywords: Key terms to highlight
            check_question: Comprehension check question
            check_answer: Answer to check
            next_preview: Preview of next lesson
            level: Difficulty level
            skip_audio: Skip audio generation (for testing)
            skip_render: Skip Remotion render (for testing)
            
        Returns:
            VideoBuildResult with paths and status
        """
        logger.info(f"🎬 Starting video build: {chapter_id}")
        
        # Step 1: Generate lesson blueprint
        logger.info("📝 Generating lesson blueprint...")
        blueprint = self.lesson_generator.generate_from_chapter(
            chapter_id=chapter_id,
            title=title,
            goal=goal,
            content=content,
            keywords=keywords,
            check_question=check_question,
            check_answer=check_answer,
            next_preview=next_preview,
            level=level
        )
        
        # Create output directory for this lesson
        lesson_dir = self.output_dir / chapter_id
        lesson_dir.mkdir(parents=True, exist_ok=True)
        
        # Save blueprint JSON
        blueprint_path = lesson_dir / "lesson.json"
        blueprint.to_json(blueprint_path)
        logger.info(f"   Blueprint saved: {blueprint_path}")
        
        # Step 2: Generate audio segments
        audio_paths = {}
        if not skip_audio and self.coqui_enabled:
            logger.info("🎙️ Generating audio segments...")
            audio_paths = self._generate_audio_segments(blueprint, lesson_dir)
            
            # Update blueprint with audio paths
            self._update_blueprint_audio_paths(blueprint, audio_paths)
            blueprint.to_json(blueprint_path)
        
        # Step 3: Generate captions
        logger.info("📝 Generating captions...")
        caption_paths = self._generate_captions(blueprint, lesson_dir)
        
        # Step 4: Render video
        video_path = None
        if not skip_render:
            logger.info("🎬 Rendering video with Remotion...")
            video_path = self._render_video(blueprint, lesson_dir)
        
        assets = VideoAssets(
            audio_paths=audio_paths,
            image_paths={},  # TODO: Implement image asset resolution
            caption_paths=caption_paths
        )
        
        return VideoBuildResult(
            success=True,
            video_path=video_path,
            blueprint_path=blueprint_path,
            assets=assets
        )
    
    def _generate_audio_segments(
        self, blueprint: LessonBlueprint, output_dir: Path
    ) -> Dict[str, Path]:
        """Generate audio files for each scene with narration."""
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        
        audio_paths = {}
        
        for scene in blueprint.scenes:
            if scene.narration and scene.narration.voice_text:
                script_text = scene.narration.voice_text
                output_path = audio_dir / f"{scene.id}.wav"
                
                # Generate using Coqui TTS
                success = self._run_coqui_tts(script_text, output_path)
                if success:
                    audio_paths[scene.id] = output_path
                    logger.info(f"   ✅ Audio generated: {scene.id}")
                else:
                    logger.warning(f"   ⚠️ Audio failed: {scene.id}")
        
        return audio_paths
    
    def _run_coqui_tts(self, text: str, output_path: Path) -> bool:
        """Run Coqui TTS to generate audio."""
        try:
            # Use the dedicated Coqui venv
            coqui_python = Path.home() / "Projects/dreamweaving/venv_coqui/bin/python"
            
            if not coqui_python.exists():
                logger.warning("Coqui venv not found, skipping audio generation")
                return False
            
            # Simple TTS command
            cmd = [
                str(coqui_python), "-c",
                f"""
from TTS.api import TTS
tts = TTS(model_name='{self.coqui_model}', progress_bar=False)
tts.tts_to_file(text='''{text}''', file_path='{output_path}')
"""
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Coqui TTS error: {e}")
            return False
    
    def _update_blueprint_audio_paths(
        self, blueprint: LessonBlueprint, audio_paths: Dict[str, Path]
    ):
        """Update blueprint scenes with resolved audio paths."""
        for scene in blueprint.scenes:
            if scene.id in audio_paths:
                if scene.narration:
                    scene.narration.audio_path = str(audio_paths[scene.id])
    
    def _generate_captions(
        self, blueprint: LessonBlueprint, output_dir: Path
    ) -> Dict[str, Path]:
        """Generate SRT captions for each scene."""
        caption_dir = output_dir / "captions"
        caption_dir.mkdir(exist_ok=True)
        
        caption_paths = {}
        
        for scene in blueprint.scenes:
            if scene.narration and scene.narration.text and scene.captions_enabled:
                srt_path = caption_dir / f"{scene.id}.srt"
                srt_content = self._text_to_srt(scene.narration.text, scene.duration_sec)
                srt_path.write_text(srt_content)
                caption_paths[scene.id] = srt_path
        
        return caption_paths
    
    def _text_to_srt(self, text: str, duration_sec: float) -> str:
        """Convert text to simple SRT format."""
        # Simple single-block SRT for now
        # TODO: Split into sentence-level blocks with timing
        end_time = self._seconds_to_srt_time(duration_sec)
        return f"""1
00:00:00,000 --> {end_time}
{text}
"""
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _render_video(
        self, blueprint: LessonBlueprint, output_dir: Path
    ) -> Optional[Path]:
        """Render video using Remotion CLI."""
        output_path = output_dir / f"{blueprint.id}.mp4"
        
        # Prepare props for Remotion
        props = blueprint.to_dict()
        
        cmd = [
            "npx", "remotion", "render",
            "LessonVideo",
            str(output_path),
            "--props", json.dumps(props),
            "--width", "1920",
            "--height", "1080",
            "--codec", "h264"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.remotion_project_path),
                capture_output=True,
                timeout=600
            )
            
            if result.returncode == 0 and output_path.exists():
                logger.info(f"✅ Video rendered: {output_path}")
                return output_path
            else:
                logger.error(f"Render failed: {result.stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Remotion render error: {e}")
            return None
    
    def validate_blueprint(self, blueprint_path: Path) -> Dict:
        """Validate a lesson blueprint JSON."""
        try:
            with open(blueprint_path) as f:
                data = json.load(f)
            
            errors = []
            warnings = []
            
            # Check required fields
            if "video" not in data:
                errors.append("Missing 'video' section")
            if "scenes" not in data:
                errors.append("Missing 'scenes' section")
            elif len(data["scenes"]) == 0:
                errors.append("No scenes defined")
            
            # Learning quality checks
            scenes = data.get("scenes", [])
            total_duration = sum(s.get("duration_sec", 0) for s in scenes)
            
            if total_duration > 420:  # 7 minutes
                warnings.append(f"Video exceeds 7 minute limit ({total_duration}s)")
            
            if total_duration < 60:
                warnings.append(f"Video under 1 minute ({total_duration}s)")
            
            # Check for required scene types
            roles = [s.get("learning_role") for s in scenes]
            if "goal_statement" not in roles:
                warnings.append("Missing goal_statement scene")
            if "check_understanding" not in roles:
                warnings.append("Missing check_understanding scene")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "stats": {
                    "scene_count": len(scenes),
                    "total_duration_sec": total_duration
                }
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "stats": {}
            }


def build_sample_video() -> VideoBuildResult:
    """Build a sample video for testing."""
    builder = VideoBuilder()
    
    return builder.build_from_content(
        chapter_id="ell-restaurant-lesson-01",
        title="Ordering Food: 3 Key Words",
        goal="In this lesson, you will learn three words for ordering food.",
        content="""
        Word one: Menu. A menu shows the food you can order. 
        When you arrive at a restaurant, you can ask: Can I see the menu?
        
        Word two: Order. To order means to ask for food or drinks.
        You can say: I would like to order, please.
        
        Word three: Pay. Pay means to give money for your food.
        At the end, you can ask: Can I pay now?
        """,
        keywords=["menu", "order", "pay"],
        check_question="Which word means the list of food?",
        check_answer="menu",
        next_preview="Next, you will practice a restaurant conversation.",
        level="A1",
        skip_audio=True,  # Skip for quick test
        skip_render=True  # Skip for quick test
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = build_sample_video()
    print(f"\nBuild result: {result}")
    if result.blueprint_path:
        print(f"Blueprint: {result.blueprint_path}")
