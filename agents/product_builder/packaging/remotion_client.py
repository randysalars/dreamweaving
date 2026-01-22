"""
Remotion Integration
Programmatic video and audio creation using Remotion framework.
https://www.remotion.dev/docs
"""

import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MediaType(Enum):
    VIDEO = "video"
    AUDIO = "audio"


@dataclass
class RenderConfig:
    """Configuration for Remotion rendering."""
    composition_id: str
    output_path: str
    props: Dict = None
    width: int = 1920
    height: int = 1080
    fps: int = 30
    codec: str = "h264"  # h264, h265, vp8, vp9, prores
    audio_codec: str = "aac"
    quality: int = 80
    concurrency: int = None  # Auto-detect
    
    def to_cli_args(self) -> List[str]:
        """Convert to Remotion CLI arguments."""
        args = [
            self.composition_id,
            self.output_path,
            f"--width={self.width}",
            f"--height={self.height}",
            f"--codec={self.codec}",
            f"--audio-codec={self.audio_codec}",
        ]
        
        if self.props:
            args.append(f"--props={json.dumps(self.props)}")
        
        if self.concurrency:
            args.append(f"--concurrency={self.concurrency}")
            
        return args


@dataclass
class RenderResult:
    """Result of a Remotion render."""
    success: bool
    output_path: str
    duration_seconds: float = 0
    file_size_bytes: int = 0
    error: Optional[str] = None


class RemotionClient:
    """
    Client for rendering video and audio using Remotion.
    
    Remotion is a React-based framework for programmatic video creation.
    This client wraps the CLI and provides a Python interface.
    """
    
    def __init__(self, project_path: Path = None):
        """
        Initialize Remotion client.
        
        Args:
            project_path: Path to Remotion project (with package.json and src/)
        """
        self.project_path = project_path or Path(__file__).parent.parent / "remotion_project"
        self._check_installation()
    
    def _check_installation(self):
        """Check if Remotion is available."""
        try:
            result = subprocess.run(
                ["npx", "remotion", "--version"],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"Remotion available: {result.stdout.decode().strip()}")
            else:
                logger.warning("Remotion not found. Run: npm install @remotion/cli")
        except FileNotFoundError:
            logger.warning("npx not found. Node.js required for Remotion.")
        except Exception as e:
            logger.warning(f"Could not check Remotion: {e}")
    
    def render_video(self, config: RenderConfig) -> RenderResult:
        """
        Render a video using Remotion.
        
        Args:
            config: Render configuration
            
        Returns:
            RenderResult with output path or error
        """
        logger.info(f"🎬 Rendering video: {config.composition_id}")
        
        cmd = ["npx", "remotion", "render"] + config.to_cli_args()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_path),
                capture_output=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                output = Path(config.output_path)
                size = output.stat().st_size if output.exists() else 0
                
                logger.info(f"✅ Video rendered: {config.output_path}")
                return RenderResult(
                    success=True,
                    output_path=config.output_path,
                    file_size_bytes=size
                )
            else:
                error = result.stderr.decode()
                logger.error(f"Render failed: {error}")
                return RenderResult(
                    success=False,
                    output_path="",
                    error=error
                )
                
        except subprocess.TimeoutExpired:
            return RenderResult(
                success=False,
                output_path="",
                error="Render timed out after 10 minutes"
            )
        except Exception as e:
            return RenderResult(
                success=False,
                output_path="",
                error=str(e)
            )
    
    def render_audio(self, config: RenderConfig) -> RenderResult:
        """
        Render audio-only using Remotion.
        
        Args:
            config: Render configuration (output should be .mp3 or .wav)
            
        Returns:
            RenderResult
        """
        logger.info(f"🎧 Rendering audio: {config.composition_id}")
        
        # Modify config for audio-only
        audio_config = RenderConfig(
            composition_id=config.composition_id,
            output_path=config.output_path,
            props=config.props,
            width=1,
            height=1,
            codec="mp3",  # Audio codec
            audio_codec="mp3",
            quality=config.quality
        )
        
        return self.render_video(audio_config)
    
    def get_compositions(self) -> List[str]:
        """Get list of available compositions in the project."""
        try:
            result = subprocess.run(
                ["npx", "remotion", "compositions"],
                cwd=str(self.project_path),
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse output to get composition IDs
                output = result.stdout.decode()
                # This is a simplified parse - actual output may vary
                compositions = [line.strip() for line in output.split('\n') if line.strip()]
                return compositions
            return []
            
        except Exception as e:
            logger.warning(f"Could not list compositions: {e}")
            return []
    
    def create_composition_props(
        self,
        title: str,
        content: str,
        style: Dict = None,
        audio_script: str = None,
        slides: List[Dict] = None
    ) -> Dict:
        """
        Create props for a Remotion composition.
        
        These props are passed to React components in the Remotion project.
        """
        return {
            "title": title,
            "content": content,
            "style": style or {},
            "audioScript": audio_script,
            "slides": slides or [],
            "theme": {
                "primaryColor": "#9F7AEA",
                "backgroundColor": "#FAF5FF",
                "textColor": "#2D3748",
                "fontFamily": "Inter, system-ui, sans-serif"
            }
        }


class MediaProducer:
    """
    Orchestrates media production for products.
    Decides when to create audio/video and manages the Remotion pipeline.
    """
    
    def __init__(self, remotion_project_path: Path = None):
        self.client = RemotionClient(remotion_project_path)
        self.output_dir = Path("./generated_media")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def should_create_video(self, chapter_context: Dict) -> bool:
        """
        Decide if video is appropriate for this content.
        
        Video is best for:
        - Procedural demonstrations
        - Visual frameworks (maps, diagrams)
        - Walkthroughs
        """
        purpose = chapter_context.get("purpose", "").lower()
        
        video_triggers = [
            "walkthrough", "demonstration", "step-by-step",
            "visual", "diagram", "framework", "process",
            "tutorial", "how-to", "guide"
        ]
        
        return any(trigger in purpose for trigger in video_triggers)
    
    def should_create_audio(self, chapter_context: Dict) -> bool:
        """
        Decide if audio is appropriate for this content.
        
        Audio is best for:
        - Reflective, meditative content
        - Guided practice
        - Emotional integration
        """
        purpose = chapter_context.get("purpose", "").lower()
        emotional_arc = chapter_context.get("emotional_arc", [])
        
        audio_triggers = [
            "reflect", "meditation", "guided", "practice",
            "mindset", "belief", "emotional", "integration",
            "visualization", "breathing", "calm"
        ]
        
        # Also check emotional arc for introspective emotions
        introspective_emotions = ["peace", "calm", "hope", "clarity", "acceptance"]
        has_introspective = any(e in introspective_emotions for e in emotional_arc)
        
        return any(trigger in purpose for trigger in audio_triggers) or has_introspective
    
    def produce_video(
        self,
        chapter_id: str,
        title: str,
        content: str,
        slides: List[Dict] = None
    ) -> RenderResult:
        """
        Produce a video for a chapter.
        """
        output_path = str(self.output_dir / f"{chapter_id}_video.mp4")
        
        props = self.client.create_composition_props(
            title=title,
            content=content,
            slides=slides
        )
        
        config = RenderConfig(
            composition_id="ChapterVideo",  # Assumes this composition exists
            output_path=output_path,
            props=props,
            width=1920,
            height=1080,
            fps=30,
            codec="h264"
        )
        
        return self.client.render_video(config)
    
    def produce_audio(
        self,
        chapter_id: str,
        title: str,
        script: str
    ) -> RenderResult:
        """
        Produce audio for a chapter.
        """
        output_path = str(self.output_dir / f"{chapter_id}_audio.mp3")
        
        props = self.client.create_composition_props(
            title=title,
            content="",
            audio_script=script
        )
        
        config = RenderConfig(
            composition_id="AudioNarration",  # Assumes this composition exists
            output_path=output_path,
            props=props,
            codec="mp3"
        )
        
        return self.client.render_audio(config)
    
    def produce_media_for_chapter(
        self,
        chapter_id: str,
        chapter_context: Dict,
        content: str,
        audio_script: str = None
    ) -> Dict[str, RenderResult]:
        """
        Produce all appropriate media for a chapter.
        
        Returns dict with 'video' and/or 'audio' results.
        """
        results = {}
        
        if self.should_create_video(chapter_context):
            logger.info(f"Creating video for {chapter_id}")
            results["video"] = self.produce_video(
                chapter_id=chapter_id,
                title=chapter_context.get("title", ""),
                content=content
            )
        
        if self.should_create_audio(chapter_context):
            logger.info(f"Creating audio for {chapter_id}")
            script = audio_script or content
            results["audio"] = self.produce_audio(
                chapter_id=chapter_id,
                title=chapter_context.get("title", ""),
                script=script
            )
        
        if not results:
            logger.info(f"No media needed for {chapter_id}")
        
        return results
