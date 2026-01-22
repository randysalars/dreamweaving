"""
Configuration Module
Loads settings from environment variables and .env file.
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# Try to load dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM configuration."""
    api_key: str = ""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 4096
    
    def __post_init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", self.api_key)
        self.model = os.getenv("OPENAI_MODEL", self.model)


@dataclass
class PDFConfig:
    """PDF generation configuration."""
    engine: str = "reportlab"  # weasyprint, reportlab, html
    
    def __post_init__(self):
        self.engine = os.getenv("PDF_ENGINE", self.engine)


@dataclass
class TTSConfig:
    """Text-to-speech configuration."""
    engine: str = "edge"  # edge, piper, coqui
    voice: str = "en-US-GuyNeural"
    
    def __post_init__(self):
        self.engine = os.getenv("TTS_ENGINE", self.engine)
        self.voice = os.getenv("TTS_VOICE", self.voice)


@dataclass
class VisualConfig:
    """Visual generation configuration."""
    style: str = "dreamweaving"
    generate_images: bool = False
    
    def __post_init__(self):
        self.style = os.getenv("VISUAL_STYLE", self.style)
        self.generate_images = os.getenv("GENERATE_IMAGES", "false").lower() == "true"


@dataclass
class Config:
    """Main configuration container."""
    # Paths
    output_dir: Path = field(default_factory=lambda: Path("./products"))
    temp_dir: Path = field(default_factory=lambda: Path("./tmp"))
    remotion_project_path: Path = field(default_factory=lambda: Path("./remotion_project"))
    
    # Sub-configs
    llm: LLMConfig = field(default_factory=LLMConfig)
    pdf: PDFConfig = field(default_factory=PDFConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    visual: VisualConfig = field(default_factory=VisualConfig)
    
    # Feature flags
    generate_video: bool = False
    debug: bool = False
    log_level: str = "INFO"
    
    def __post_init__(self):
        self.output_dir = Path(os.getenv("OUTPUT_DIR", str(self.output_dir)))
        self.temp_dir = Path(os.getenv("TEMP_DIR", str(self.temp_dir)))
        self.remotion_project_path = Path(os.getenv("REMOTION_PROJECT_PATH", str(self.remotion_project_path)))
        self.generate_video = os.getenv("GENERATE_VIDEO", "false").lower() == "true"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """Validate configuration."""
        errors = []
        
        if not self.llm.api_key:
            errors.append("OPENAI_API_KEY is required")
        
        if errors:
            for e in errors:
                logger.error(f"Config error: {e}")
            return False
        
        return True


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Reload configuration from environment."""
    global _config
    _config = Config()
    return _config
