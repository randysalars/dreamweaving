"""
Product Assembler
The final stage that assembles all product components into deliverable formats.
Coordinates PDF generation, media production, and package assembly.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .pdf_generator import PDFGenerator, PDFConfig, PDFStyle
from .remotion_client import MediaProducer, RemotionClient
from .tts_client import TTSClient, TTSConfig
from ..pipeline.visual_director import VisualDirector
from ..pipeline.visual_qa import VisualQA
from .image_generator import ImageGenerator
from ..schemas.visual_style import VisualStyle, DREAMWEAVING_STYLE

logger = logging.getLogger(__name__)


@dataclass
class AssemblyConfig:
    """Configuration for assembling a product."""
    title: str
    author: str = "SalarsNet"
    output_dir: Path = None
    
    # Output formats
    generate_pdf: bool = True
    generate_audio: bool = True
    generate_video: bool = False
    generate_visuals: bool = True
    
    # Style
    visual_style: VisualStyle = None
    pdf_style: PDFStyle = None
    
    # TTS
    tts_voice: str = "en-US-GuyNeural"
    
    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = Path(f"./products/{self._slugify(self.title)}")
        if self.visual_style is None:
            self.visual_style = DREAMWEAVING_STYLE
        if self.pdf_style is None:
            self.pdf_style = PDFStyle()
    
    def _slugify(self, text: str) -> str:
        return "".join(c if c.isalnum() or c == " " else "" for c in text).replace(" ", "_").lower()


@dataclass
class AssemblyResult:
    """Result of assembling a product."""
    success: bool
    title: str
    output_dir: str
    
    # Generated files
    pdf_path: Optional[str] = None
    audio_files: List[str] = field(default_factory=list)
    video_files: List[str] = field(default_factory=list)
    visual_files: List[str] = field(default_factory=list)
    
    # Metadata
    total_chapters: int = 0
    total_words: int = 0
    generation_time_seconds: float = 0
    
    errors: List[str] = field(default_factory=list)
    
    def to_manifest(self) -> Dict:
        """Generate a manifest file for the product."""
        return {
            "title": self.title,
            "generated_at": datetime.now().isoformat(),
            "files": {
                "pdf": self.pdf_path,
                "audio": self.audio_files,
                "video": self.video_files,
                "visuals": self.visual_files
            },
            "stats": {
                "chapters": self.total_chapters,
                "words": self.total_words,
                "generation_time_seconds": self.generation_time_seconds
            },
            "success": self.success,
            "errors": self.errors
        }


class ProductAssembler:
    """
    The final assembly stage for products.
    
    Takes completed chapters and generates:
    - Professional PDF
    - Audio narration (per chapter or full)
    - Video components (intro, cards, key insights)
    - Visual assets
    """
    
    def __init__(self, templates_dir: Path = None):
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "templates"
        
        # Component generators
        self.pdf_generator = PDFGenerator()
        self.media_producer = MediaProducer()
        self.tts_client = TTSClient()
        self.visual_director = VisualDirector(self.templates_dir)
        self.visual_qa = VisualQA()
        self.image_generator = ImageGenerator()
    
    def assemble(
        self, 
        chapters: List[Dict],
        config: AssemblyConfig,
        audio_scripts: Dict[str, str] = None
    ) -> AssemblyResult:
        """
        Assemble a complete product.
        
        Args:
            chapters: List of chapter dicts with title, content, key_takeaways
            config: Assembly configuration
            audio_scripts: Optional custom audio scripts per chapter
            
        Returns:
            AssemblyResult with all generated file paths
        """
        start_time = datetime.now()
        logger.info(f"📦 Assembling: {config.title}")
        
        # Create output directory
        config.output_dir.mkdir(parents=True, exist_ok=True)
        
        result = AssemblyResult(
            success=True,
            title=config.title,
            output_dir=str(config.output_dir),
            total_chapters=len(chapters),
            total_words=sum(len(ch.get("content", "").split()) for ch in chapters)
        )
        
        visuals = {}
        
        # 1. Generate Visuals
        if config.generate_visuals:
            logger.info("🎨 Generating visuals...")
            try:
                visuals = self._generate_visuals(chapters, config)
                result.visual_files = list(visuals.values())
            except Exception as e:
                logger.error(f"Visual generation failed: {e}")
                result.errors.append(f"Visuals: {str(e)}")
        
        # 2. Generate PDF
        if config.generate_pdf:
            logger.info("📄 Generating PDF...")
            try:
                pdf_path = self._generate_pdf(chapters, config, visuals)
                result.pdf_path = pdf_path
            except Exception as e:
                logger.error(f"PDF generation failed: {e}")
                result.errors.append(f"PDF: {str(e)}")
        
        # 3. Generate Audio
        if config.generate_audio:
            logger.info("🎙️ Generating audio...")
            try:
                audio_files = self._generate_audio(chapters, config, audio_scripts)
                result.audio_files = audio_files
            except Exception as e:
                logger.error(f"Audio generation failed: {e}")
                result.errors.append(f"Audio: {str(e)}")
        
        # 4. Generate Video
        if config.generate_video:
            logger.info("🎬 Generating video...")
            try:
                video_files = self._generate_video(chapters, config)
                result.video_files = video_files
            except Exception as e:
                logger.error(f"Video generation failed: {e}")
                result.errors.append(f"Video: {str(e)}")
        
        # Calculate timing
        end_time = datetime.now()
        result.generation_time_seconds = (end_time - start_time).total_seconds()
        
        # Write manifest
        manifest_path = config.output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(result.to_manifest(), indent=2))
        
        # Determine success
        result.success = len(result.errors) == 0
        
        logger.info(f"{'✅' if result.success else '⚠️'} Assembly complete: {config.title}")
        logger.info(f"   Output: {config.output_dir}")
        logger.info(f"   Time: {result.generation_time_seconds:.1f}s")
        
        if result.errors:
            logger.warning(f"   Errors: {len(result.errors)}")
        
        return result
    
    def _generate_visuals(
        self, 
        chapters: List[Dict], 
        config: AssemblyConfig
    ) -> Dict[str, str]:
        """Generate visual assets for the product."""
        from ..schemas.blueprint import ChapterSpec
        
        # Convert chapters to ChapterSpec for VisualDirector
        chapter_specs = [
            ChapterSpec(
                title=ch.get("title", f"Chapter {i+1}"),
                purpose=ch.get("purpose", ""),
                key_takeaways=ch.get("key_takeaways", []),
                target_word_count=len(ch.get("content", "").split())
            )
            for i, ch in enumerate(chapters)
        ]
        
        # Plan visuals
        visual_map = self.visual_director.plan_visuals(
            config.title,
            chapter_specs,
            config.visual_style
        )
        
        # Generate prompts
        prompts = self.visual_director.generate_image_prompts(
            visual_map,
            config.visual_style
        )
        
        # Set output directory
        self.image_generator.output_dir = config.output_dir / "visuals"
        self.image_generator.output_dir.mkdir(exist_ok=True)
        
        # Generate images
        results = self.image_generator.generate_batch(prompts, config.visual_style)
        
        # Return map of section_id -> path
        return {r.section_id: r.path for r in results if r.success}
    
    def _generate_pdf(
        self, 
        chapters: List[Dict], 
        config: AssemblyConfig,
        visuals: Dict[str, str]
    ) -> str:
        """Generate the PDF document."""
        pdf_config = PDFConfig(
            title=config.title,
            author=config.author,
            style=config.pdf_style,
            output_path=str(config.output_dir / f"{config.title.replace(' ', '_')}.pdf")
        )
        
        return self.pdf_generator.generate(chapters, pdf_config, visuals)
    
    def _generate_audio(
        self, 
        chapters: List[Dict], 
        config: AssemblyConfig,
        audio_scripts: Dict[str, str] = None
    ) -> List[str]:
        """Generate audio narration for chapters."""
        self.tts_client.output_dir = config.output_dir / "audio"
        self.tts_client.output_dir.mkdir(exist_ok=True)
        
        audio_files = []
        tts_config = TTSConfig(voice=config.tts_voice)
        
        for i, chapter in enumerate(chapters):
            chapter_id = f"chapter_{i+1}"
            
            # Use custom script or chapter content
            script = audio_scripts.get(chapter_id) if audio_scripts else None
            if not script:
                script = chapter.get("content", "")
            
            if not script:
                continue
            
            result = self.tts_client.synthesize(
                script,
                chapter_id,
                tts_config
            )
            
            if result.success:
                audio_files.append(result.audio_path)
        
        return audio_files
    
    def _generate_video(
        self, 
        chapters: List[Dict], 
        config: AssemblyConfig
    ) -> List[str]:
        """Generate video components."""
        video_files = []
        
        # Create video directory
        video_dir = config.output_dir / "video"
        video_dir.mkdir(exist_ok=True)
        
        # Course intro would be generated here
        # For now, return empty list as Remotion needs to be set up
        logger.info("Video generation requires Remotion project setup")
        
        return video_files


# Convenience function for quick assembly
def assemble_product(
    title: str,
    chapters: List[Dict],
    output_dir: str = None,
    **kwargs
) -> AssemblyResult:
    """
    Quick assemble a product.
    
    Args:
        title: Product title
        chapters: List of chapter dicts
        output_dir: Where to save outputs
        **kwargs: Additional AssemblyConfig options
        
    Returns:
        AssemblyResult
    """
    config = AssemblyConfig(
        title=title,
        output_dir=Path(output_dir) if output_dir else None,
        **kwargs
    )
    
    assembler = ProductAssembler()
    return assembler.assemble(chapters, config)
