#!/usr/bin/env python3
"""
TTS Provider Abstraction Layer

Provides a unified interface for different TTS providers:
- CoquiTTSProvider (default) - Free, local, uses XTTS v2
- GoogleTTSProvider - Paid, cloud-based, uses Neural2 voices

Usage:
    from scripts.core.tts_provider import get_tts_provider

    provider = get_tts_provider("coqui")  # or "google"
    provider.synthesize(ssml_path, output_path)
"""

import os
import re
import sys
import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    def synthesize(
        self,
        ssml_path: Path,
        output_path: Path,
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        **kwargs
    ) -> Path:
        """
        Synthesize speech from SSML file.

        Args:
            ssml_path: Path to SSML file
            output_path: Path for output audio file (MP3)
            speaking_rate: Speech rate multiplier (0.5-2.0)
            pitch: Pitch adjustment in semitones
            **kwargs: Provider-specific options

        Returns:
            Path to generated audio file
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return provider name."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available/configured."""
        pass


class CoquiTTSProvider(TTSProvider):
    """
    Coqui TTS Provider using XTTS v2.

    Free, local, high-quality voice synthesis with optimized parameters
    for natural, human-sounding hypnotic content.
    """

    # Quality presets for different use cases
    QUALITY_PRESETS = {
        'hypnotic': {
            'temperature': 0.45,        # Low for consistent, stable voice
            'repetition_penalty': 3.0,  # Reduce phrase repetition
            'top_p': 0.75,              # Focused token selection
            'top_k': 50,                # Limit vocabulary per step
            'speed': 0.92,              # Slightly slower for trance
        },
        'natural': {
            'temperature': 0.55,        # Balanced naturalness
            'repetition_penalty': 2.5,
            'top_p': 0.80,
            'top_k': 50,
            'speed': 0.95,
        },
        'expressive': {
            'temperature': 0.70,        # More variation
            'repetition_penalty': 2.0,
            'top_p': 0.85,
            'top_k': 50,
            'speed': 1.0,
        },
    }

    def __init__(self, quality_preset: str = 'hypnotic'):
        self.venv_python = PROJECT_ROOT / "venv_coqui" / "bin" / "python"
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        self._tts = None
        self._model = None
        self.quality_preset = quality_preset
        self.params = self.QUALITY_PRESETS.get(quality_preset, self.QUALITY_PRESETS['hypnotic'])

    def get_name(self) -> str:
        return "coqui"

    def is_available(self) -> bool:
        """Check if Coqui TTS is installed."""
        return self.venv_python.exists()

    def _load_tts(self):
        """Lazy-load TTS model with direct access for advanced parameters."""
        if self._tts is None:
            try:
                from TTS.api import TTS
                import torch

                use_gpu = torch.cuda.is_available()
                device = "cuda" if use_gpu else "cpu"
                print(f"Loading XTTS v2 model ({'GPU' if use_gpu else 'CPU'})...")
                print(f"Quality preset: {self.quality_preset}")

                self._tts = TTS(model_name=self.model_name, progress_bar=True, gpu=use_gpu)

                # Get direct model access for advanced synthesis
                if hasattr(self._tts, 'synthesizer') and self._tts.synthesizer is not None:
                    self._model = self._tts.synthesizer.tts_model
                    self._model.to(device)

                print("Model loaded successfully")
            except ImportError:
                raise RuntimeError(
                    "Coqui TTS not installed. Run:\n"
                    "  python3.11 -m venv venv_coqui\n"
                    "  venv_coqui/bin/pip install TTS pydub torch"
                )
        return self._tts

    def _strip_ssml(self, ssml_text: str) -> str:
        """Convert SSML to plain text with natural pauses and breath markers."""
        # Remove XML declaration
        text = re.sub(r'<\?xml[^>]*\?>', '', ssml_text)
        # Remove comments
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

        # Convert break tags to natural pause markers
        def break_to_pause(match):
            time_str = match.group(1)
            if 'ms' in time_str:
                ms = int(time_str.replace('ms', ''))
            else:
                ms = int(float(time_str.replace('s', '')) * 1000)

            # Use natural pause indicators that XTTS handles well
            if ms >= 3000:
                return '.\n\n'        # Paragraph break for long pauses
            elif ms >= 2000:
                return '...\n'        # Line break with ellipsis
            elif ms >= 1000:
                return '... '         # Ellipsis for medium pause
            elif ms >= 500:
                return ', '           # Comma for short pause
            else:
                return ' '            # Space for very short pause

        text = re.sub(r'<break\s+time=["\']([^"\']+)["\']\s*/>', break_to_pause, text)

        # Remove all remaining tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove DVE markers
        text = re.sub(r'\[DVE:[^\]]+\]', '', text)
        # Remove SFX markers
        text = re.sub(r'\[SFX:[^\]]+\]', '', text)
        # Remove style markers
        text = re.sub(r'\[[^\]]+\]', '', text)
        # Clean whitespace but preserve paragraph structure
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def _smart_chunk_text(self, text: str, max_chars: int = 150) -> list:
        """
        Smart text chunking optimized for XTTS v2.

        Splits at natural boundaries (sentences, clauses) with smaller chunks
        for better prosody and more natural speech.
        """
        chunks = []

        # First split by paragraphs (preserve structure)
        paragraphs = text.split('\n\n')

        for para in paragraphs:
            if not para.strip():
                continue

            # Split paragraph into sentences
            sentences = re.split(r'(?<=[.!?])\s+', para)

            current_chunk = ""
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                # If sentence itself is too long, split at clause boundaries
                if len(sentence) > max_chars:
                    # Split at commas, semicolons, colons, or em-dashes
                    clauses = re.split(r'(?<=[,;:\-])\s+', sentence)
                    for clause in clauses:
                        clause = clause.strip()
                        if not clause:
                            continue
                        if len(current_chunk) + len(clause) + 1 < max_chars:
                            current_chunk += " " + clause if current_chunk else clause
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = clause
                elif len(current_chunk) + len(sentence) + 1 < max_chars:
                    current_chunk += " " + sentence if current_chunk else sentence
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence

            if current_chunk:
                chunks.append(current_chunk.strip())

        return chunks

    def _synthesize_chunk_advanced(self, text: str, tmp_path: str, tts) -> bool:
        """
        Synthesize a single chunk using advanced XTTS parameters.
        Returns True on success.
        """
        try:
            # Try advanced synthesis with quality parameters
            if self._model is not None and hasattr(self._model, 'inference'):
                import torch

                # Compute speaker latents (conditioning)
                gpt_cond_latent, speaker_embedding = self._model.get_conditioning_latents(
                    audio_path=None,  # Use default voice
                    gpt_cond_len=6,   # Longer conditioning for consistency
                    max_ref_length=30,
                    sound_norm_refs=True,  # Normalize for consistency
                )

                # Advanced inference with quality parameters
                out = self._model.inference(
                    text=text,
                    language="en",
                    gpt_cond_latent=gpt_cond_latent,
                    speaker_embedding=speaker_embedding,
                    temperature=self.params['temperature'],
                    repetition_penalty=self.params['repetition_penalty'],
                    top_p=self.params['top_p'],
                    top_k=self.params['top_k'],
                    enable_text_splitting=True,  # Let XTTS handle sub-sentence splits
                )

                # Save audio
                import torchaudio
                wav = torch.tensor(out["wav"]).unsqueeze(0)
                torchaudio.save(tmp_path, wav, 24000)
                return True

            else:
                # Fallback to standard API
                tts.tts_to_file(
                    text=text,
                    file_path=tmp_path,
                    language="en"
                )
                return True

        except Exception as e:
            print(f"    Advanced synthesis failed ({e}), using standard...")
            # Fallback to basic synthesis
            try:
                tts.tts_to_file(
                    text=text,
                    file_path=tmp_path,
                    language="en"
                )
                return True
            except Exception as e2:
                print(f"    Chunk synthesis failed: {e2}")
                return False

    def synthesize(
        self,
        ssml_path: Path,
        output_path: Path,
        speaking_rate: float = 0.95,
        pitch: float = 0.0,
        **kwargs
    ) -> Path:
        """
        Synthesize speech using Coqui XTTS v2 via subprocess.

        Uses venv_coqui/bin/python to run the TTS script since TTS
        is installed in a separate virtualenv.

        Args:
            ssml_path: Path to SSML file
            output_path: Path for output MP3
            speaking_rate: Speed adjustment (applied post-synthesis)
            pitch: Ignored for Coqui (XTTS doesn't support pitch adjustment)
            quality_preset: Override preset ('hypnotic', 'natural', 'expressive')
        """
        # Allow runtime preset override
        if 'quality_preset' in kwargs:
            preset = kwargs['quality_preset']
            if preset in self.QUALITY_PRESETS:
                self.params = self.QUALITY_PRESETS[preset]
                self.quality_preset = preset

        ssml_path = Path(ssml_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Use the dedicated Coqui TTS script via subprocess
        # This runs in venv_coqui which has TTS installed
        coqui_script = PROJECT_ROOT / "scripts" / "core" / "generate_voice_coqui_simple.py"

        if not self.venv_python.exists():
            raise RuntimeError(
                "Coqui TTS not installed. Run:\n"
                "  python3.11 -m venv venv_coqui\n"
                "  venv_coqui/bin/pip install TTS pydub torch"
            )

        if not coqui_script.exists():
            raise RuntimeError(f"Coqui TTS script not found: {coqui_script}")

        # Build command - output to parent dir, script outputs voice.mp3
        output_dir = output_path.parent
        cmd = [
            str(self.venv_python),
            str(coqui_script),
            str(ssml_path),
            str(output_dir),
            "--speed", str(speaking_rate),
        ]

        print("Running Coqui TTS via subprocess...")
        print(f"Quality preset: {self.quality_preset}")
        print(f"Command: {' '.join(cmd[:3])}...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout for long scripts
                cwd=str(PROJECT_ROOT)
            )

            # Print output
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        print(f"  {line}")

            if result.returncode != 0:
                print(f"Coqui TTS failed with return code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr[-500:]}")
                raise RuntimeError(f"Coqui TTS synthesis failed: {result.stderr[-200:]}")

            # The script outputs voice.mp3 in output_dir
            generated_file = output_dir / "voice.mp3"
            if not generated_file.exists():
                raise RuntimeError(f"Expected output file not found: {generated_file}")

            # If the requested output path is different, rename
            if output_path != generated_file:
                import shutil
                shutil.move(str(generated_file), str(output_path))

            print(f"Voice generated: {output_path}")
            return output_path

        except subprocess.TimeoutExpired:
            raise RuntimeError("Coqui TTS synthesis timed out after 1 hour")


class GoogleTTSProvider(TTSProvider):
    """
    Google Cloud TTS Provider using Neural2 voices.

    Requires Google Cloud credentials and billing enabled.
    Uses the existing generate_audio_chunked implementation.
    """

    def __init__(self, voice_name: str = "en-US-Neural2-H"):
        self.voice_name = voice_name
        self.sample_rate_hz = 24000
        self.effects_profile = ['headphone-class-device']

    def get_name(self) -> str:
        return "google"

    def is_available(self) -> bool:
        """Check if Google Cloud TTS is configured."""
        try:
            from google.cloud import texttospeech
            # Try to create a client - will fail if no credentials
            texttospeech.TextToSpeechClient()
            return True
        except Exception:
            return False

    def synthesize(
        self,
        ssml_path: Path,
        output_path: Path,
        speaking_rate: float = 0.88,
        pitch: float = 0.0,
        **kwargs
    ) -> Path:
        """
        Synthesize speech using Google Cloud TTS.

        Uses the existing chunked synthesis implementation.
        """
        from scripts.core.generate_audio_chunked import synthesize_ssml_file_chunked

        ssml_path = Path(ssml_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        voice_name = kwargs.get('voice_name', self.voice_name)
        sample_rate_hz = kwargs.get('sample_rate_hz', self.sample_rate_hz)

        synthesize_ssml_file_chunked(
            ssml_filepath=str(ssml_path),
            output_filepath=str(output_path),
            voice_name=voice_name,
            speaking_rate=speaking_rate,
            pitch=pitch,
            sample_rate_hz=sample_rate_hz,
            effects_profile_id=self.effects_profile
        )

        return output_path


# Provider registry
_PROVIDERS = {
    'coqui': CoquiTTSProvider,
    'google': GoogleTTSProvider,
}

# Default provider
DEFAULT_PROVIDER = 'coqui'


def get_tts_provider(provider_name: str = None) -> TTSProvider:
    """
    Get a TTS provider instance.

    Args:
        provider_name: Provider name ('coqui' or 'google').
                      Defaults to 'coqui'.

    Returns:
        TTSProvider instance

    Raises:
        ValueError: If provider not found
        RuntimeError: If provider not available
    """
    provider_name = provider_name or DEFAULT_PROVIDER

    if provider_name not in _PROVIDERS:
        raise ValueError(f"Unknown TTS provider: {provider_name}. "
                        f"Available: {list(_PROVIDERS.keys())}")

    provider = _PROVIDERS[provider_name]()

    if not provider.is_available():
        if provider_name == 'coqui':
            raise RuntimeError(
                "Coqui TTS not available. Install with:\n"
                "  python3.11 -m venv venv_coqui\n"
                "  venv_coqui/bin/pip install TTS pydub torch"
            )
        elif provider_name == 'google':
            raise RuntimeError(
                "Google Cloud TTS not available. Ensure:\n"
                "  1. GOOGLE_APPLICATION_CREDENTIALS is set\n"
                "  2. Billing is enabled on the project\n"
                "  3. Cloud Text-to-Speech API is enabled"
            )

    return provider


def list_providers() -> Dict[str, bool]:
    """
    List all providers and their availability.

    Returns:
        Dict mapping provider name to availability status
    """
    result = {}
    for name, cls in _PROVIDERS.items():
        try:
            provider = cls()
            result[name] = provider.is_available()
        except Exception:
            result[name] = False
    return result


if __name__ == "__main__":
    # Quick test
    print("TTS Provider Status:")
    print("-" * 40)
    for name, available in list_providers().items():
        status = "Available" if available else "Not Available"
        default = " (default)" if name == DEFAULT_PROVIDER else ""
        print(f"  {name}: {status}{default}")
