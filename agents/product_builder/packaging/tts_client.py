"""
TTS Client - Text-to-Speech Integration
Supports free/open-source TTS engines for audio narration.

Best Free/Open-Source TTS Options:
1. Piper TTS - Fast, lightweight, many voices, runs locally
2. Coqui TTS (XTTS) - High quality, cross-lingual, open source
3. Bark (Suno) - Natural speech with emotion, open source
4. Edge TTS - Microsoft Edge's TTS, free to use
"""

import logging
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TTSEngine(Enum):
    PIPER = "piper"        # Fastest, lightweight
    COQUI = "coqui"        # Highest quality
    EDGE = "edge"          # Free cloud TTS
    BARK = "bark"          # Most natural


@dataclass
class TTSConfig:
    """Configuration for TTS generation."""
    engine: TTSEngine = TTSEngine.PIPER
    voice: str = "en_US-lessac-medium"  # Piper default
    speed: float = 1.0
    pitch: float = 1.0
    output_format: str = "wav"


@dataclass
class TTSResult:
    """Result of TTS generation."""
    success: bool
    audio_path: str
    duration_seconds: float = 0
    error: Optional[str] = None


class TTSClient:
    """
    Multi-engine TTS client supporting free/open-source options.
    
    Recommended Setup Order:
    1. Edge TTS - No setup, works immediately (uses Microsoft's free API)
    2. Piper - pip install piper-tts, download voice model
    3. Coqui - pip install TTS, higher quality but slower
    """
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("./generated_audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check available engines
        self.available_engines = self._detect_engines()
        logger.info(f"Available TTS engines: {self.available_engines}")
    
    def _detect_engines(self) -> List[TTSEngine]:
        """Detect which TTS engines are installed."""
        available = []
        
        # Edge TTS (always available via pip install edge-tts)
        try:
            import edge_tts
            available.append(TTSEngine.EDGE)
        except ImportError:
            pass
        
        # Piper
        try:
            result = subprocess.run(["piper", "--version"], capture_output=True)
            if result.returncode == 0:
                available.append(TTSEngine.PIPER)
        except FileNotFoundError:
            pass
        
        # Coqui TTS
        try:
            from TTS.api import TTS
            available.append(TTSEngine.COQUI)
        except ImportError:
            pass
        
        return available
    
    def synthesize(
        self, 
        text: str, 
        output_name: str,
        config: TTSConfig = None
    ) -> TTSResult:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to convert to speech
            output_name: Name for output file (without extension)
            config: TTS configuration
            
        Returns:
            TTSResult with audio path or error
        """
        config = config or TTSConfig()
        
        # Select best available engine
        if config.engine not in self.available_engines:
            if TTSEngine.EDGE in self.available_engines:
                config.engine = TTSEngine.EDGE
            elif self.available_engines:
                config.engine = self.available_engines[0]
            else:
                return TTSResult(
                    success=False,
                    audio_path="",
                    error="No TTS engine available. Install: pip install edge-tts"
                )
        
        output_path = self.output_dir / f"{output_name}.{config.output_format}"
        
        if config.engine == TTSEngine.EDGE:
            return self._synthesize_edge(text, str(output_path), config)
        elif config.engine == TTSEngine.PIPER:
            return self._synthesize_piper(text, str(output_path), config)
        elif config.engine == TTSEngine.COQUI:
            return self._synthesize_coqui(text, str(output_path), config)
        else:
            return TTSResult(
                success=False,
                audio_path="",
                error=f"Engine {config.engine} not implemented"
            )
    
    def _synthesize_edge(self, text: str, output_path: str, config: TTSConfig) -> TTSResult:
        """
        Synthesize using Edge TTS (Microsoft's free cloud TTS).
        
        Best voices:
        - en-US-GuyNeural (male, natural)
        - en-US-JennyNeural (female, natural)
        - en-US-AriaNeural (female, expressive)
        - en-GB-RyanNeural (British male)
        """
        import asyncio
        
        async def _generate():
            import edge_tts
            
            voice = config.voice or "en-US-GuyNeural"
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
        
        try:
            asyncio.run(_generate())
            
            logger.info(f"✅ Edge TTS generated: {output_path}")
            return TTSResult(
                success=True,
                audio_path=output_path
            )
        except Exception as e:
            logger.error(f"Edge TTS failed: {e}")
            return TTSResult(
                success=False,
                audio_path="",
                error=str(e)
            )
    
    def _synthesize_piper(self, text: str, output_path: str, config: TTSConfig) -> TTSResult:
        """
        Synthesize using Piper TTS (fast, local).
        
        Install: pip install piper-tts
        Download voices from: https://github.com/rhasspy/piper/releases
        
        Good voices:
        - en_US-lessac-medium (balanced)
        - en_US-amy-medium (female)
        - en_GB-alan-medium (British)
        """
        try:
            # Write text to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text)
                text_file = f.name
            
            result = subprocess.run([
                "piper",
                "--model", config.voice,
                "--output_file", output_path
            ], stdin=open(text_file), capture_output=True, timeout=120)
            
            os.unlink(text_file)
            
            if result.returncode == 0:
                logger.info(f"✅ Piper TTS generated: {output_path}")
                return TTSResult(success=True, audio_path=output_path)
            else:
                return TTSResult(
                    success=False,
                    audio_path="",
                    error=result.stderr.decode()
                )
                
        except Exception as e:
            logger.error(f"Piper TTS failed: {e}")
            return TTSResult(success=False, audio_path="", error=str(e))
    
    def _synthesize_coqui(self, text: str, output_path: str, config: TTSConfig) -> TTSResult:
        """
        Synthesize using Coqui TTS (highest quality).
        
        Install: pip install TTS
        
        Good models:
        - tts_models/en/ljspeech/tacotron2-DDC (fast)
        - tts_models/en/vctk/vits (multi-speaker)
        - tts_models/multilingual/multi-dataset/xtts_v2 (best quality, slow)
        """
        try:
            from TTS.api import TTS
            
            model = config.voice or "tts_models/en/ljspeech/tacotron2-DDC"
            tts = TTS(model_name=model)
            tts.tts_to_file(text=text, file_path=output_path)
            
            logger.info(f"✅ Coqui TTS generated: {output_path}")
            return TTSResult(success=True, audio_path=output_path)
            
        except Exception as e:
            logger.error(f"Coqui TTS failed: {e}")
            return TTSResult(success=False, audio_path="", error=str(e))
    
    def list_edge_voices(self) -> List[str]:
        """List available Edge TTS voices."""
        import asyncio
        
        async def _list():
            import edge_tts
            voices = await edge_tts.list_voices()
            return [v["ShortName"] for v in voices if "en-" in v["Locale"]]
        
        try:
            return asyncio.run(_list())
        except:
            return []


# Convenience function for quick TTS
def text_to_speech(
    text: str, 
    output_path: str, 
    voice: str = "en-US-GuyNeural"
) -> TTSResult:
    """
    Quick TTS function using best available engine.
    
    Args:
        text: Text to convert
        output_path: Where to save audio
        voice: Voice ID (defaults to Edge TTS Guy)
        
    Returns:
        TTSResult
    """
    client = TTSClient()
    name = Path(output_path).stem
    
    config = TTSConfig(voice=voice)
    return client.synthesize(text, name, config)
