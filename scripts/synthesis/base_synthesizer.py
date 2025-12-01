#!/usr/bin/env python3
"""
Base synthesizer class for text-to-speech synthesis.

This module provides a reusable base class that consolidates common
synthesis patterns used across all synthesis scripts, reducing code
duplication from ~1000+ lines to a single shared implementation.

Usage:
    from base_synthesizer import BaseSynthesizer

    class MySynthesizer(BaseSynthesizer):
        name = "My Synthesis"
        output_filename = "my_output.mp3"

        def get_chunks(self):
            return [chunk1_ssml, chunk2_ssml, ...]

    if __name__ == "__main__":
        synthesizer = MySynthesizer()
        synthesizer.run()
"""

import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any

from google.cloud import texttospeech

# Import our centralized config and logging
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from scripts.config.defaults import AUDIO, TTS, VOICES, DEFAULT_VOICE
    from scripts.utilities.logging_config import get_logger
except ImportError:
    # Fallback defaults if imports fail
    AUDIO = {'sample_rate_hz': 24000}
    TTS = {'speaking_rate': 1.0, 'pitch_semitones': 0.0, 'volume_gain_db': 0.0,
           'effects_profile': ['headphone-class-device'], 'default_language': 'en-US'}
    DEFAULT_VOICE = 'en-US-Neural2-I'

    import logging
    def get_logger(name):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)


class BaseSynthesizer(ABC):
    """
    Base class for text-to-speech synthesis with chunked SSML.

    Subclasses must implement:
        - get_chunks(): Return list of SSML chunks to synthesize
        - name: Human-readable name for the synthesis
        - output_filename: Final output filename

    Optional overrides:
        - voice_name: TTS voice to use (default: en-US-Neural2-I)
        - speaking_rate: Speech rate multiplier (default: 1.0)
        - pitch: Pitch adjustment in semitones (default: 0.0)
        - description: Additional description text
        - duration_estimate: Estimated duration string
    """

    # Required - subclasses must set these
    name: str = "Base Synthesis"
    output_filename: str = "output.mp3"

    # Optional - subclasses can override
    voice_name: str = DEFAULT_VOICE
    speaking_rate: float = 1.0
    pitch: float = 0.0
    volume_gain_db: float = 0.0
    description: str = ""
    duration_estimate: str = "unknown"

    def __init__(
        self,
        voice_name: Optional[str] = None,
        speaking_rate: Optional[float] = None,
        pitch: Optional[float] = None,
        output_dir: Optional[str] = None
    ):
        """
        Initialize the synthesizer.

        Args:
            voice_name: Override the default voice
            speaking_rate: Override the default speaking rate
            pitch: Override the default pitch
            output_dir: Directory for output files (default: current directory)
        """
        if voice_name:
            self.voice_name = voice_name
        if speaking_rate is not None:
            self.speaking_rate = speaking_rate
        if pitch is not None:
            self.pitch = pitch

        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.logger = get_logger(self.__class__.__name__)
        self._client: Optional[texttospeech.TextToSpeechClient] = None

    @property
    def client(self) -> texttospeech.TextToSpeechClient:
        """Lazy-load the TTS client."""
        if self._client is None:
            self._client = texttospeech.TextToSpeechClient()
        return self._client

    @abstractmethod
    def get_chunks(self) -> List[str]:
        """
        Return list of SSML chunks to synthesize.

        Each chunk should be valid SSML under 5000 bytes.

        Returns:
            List of SSML strings
        """
        pass

    def get_success_message(self) -> List[str]:
        """
        Return additional success message lines.

        Override to add custom success info.

        Returns:
            List of message lines to display on success
        """
        return []

    def synthesize_chunk(
        self,
        ssml: str,
        output_file: Path,
        chunk_num: int
    ) -> bool:
        """
        Synthesize a single SSML chunk to an audio file.

        Args:
            ssml: SSML content to synthesize
            output_file: Path to save the audio
            chunk_num: Chunk number for logging

        Returns:
            True if synthesis succeeded, False otherwise
        """
        chunk_size = len(ssml.encode('utf-8'))
        self.logger.info(f"Chunk {chunk_num}: {chunk_size} bytes")

        if chunk_size > 5000:
            self.logger.warning(f"Chunk {chunk_num} exceeds 5000 byte limit!")

        synthesis_input = texttospeech.SynthesisInput(ssml=ssml)

        voice = texttospeech.VoiceSelectionParams(
            language_code=TTS.get('default_language', 'en-US'),
            name=self.voice_name
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=self.speaking_rate,
            pitch=self.pitch,
            volume_gain_db=self.volume_gain_db,
            sample_rate_hertz=AUDIO.get('sample_rate_hz', 24000),
            effects_profile_id=TTS.get('effects_profile', ['headphone-class-device'])
        )

        try:
            self.logger.info(f"  Synthesizing chunk {chunk_num}...")
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            with open(output_file, 'wb') as out:
                out.write(response.audio_content)

            size_kb = len(response.audio_content) / 1024
            self.logger.info(f"  ✓ Saved {size_kb:.1f} KB")
            return True

        except Exception as e:
            self.logger.error(f"  ❌ Error synthesizing chunk {chunk_num}: {e}")
            return False

    def concatenate_chunks(
        self,
        chunk_files: List[Path],
        output_file: Path
    ) -> bool:
        """
        Concatenate audio chunks into a single file using ffmpeg.

        Args:
            chunk_files: List of chunk file paths
            output_file: Path for the concatenated output

        Returns:
            True if concatenation succeeded, False otherwise
        """
        if not chunk_files:
            self.logger.error("No chunk files to concatenate")
            return False

        # Use a temporary directory for the filelist
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for cf in chunk_files:
                f.write(f"file '{cf}'\n")
            filelist_path = f.name

        try:
            result = subprocess.run(
                ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', filelist_path,
                 '-c', 'copy', str(output_file), '-y'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                self.logger.error(f"ffmpeg error: {result.stderr}")
                return False

            return output_file.exists()

        finally:
            # Clean up filelist
            if os.path.exists(filelist_path):
                os.remove(filelist_path)

    def cleanup_chunks(self, chunk_files: List[Path]) -> None:
        """Remove temporary chunk files."""
        for cf in chunk_files:
            if cf.exists():
                cf.unlink()

    def print_header(self) -> None:
        """Print synthesis header information."""
        print("=" * 60)
        print(self.name)
        print("=" * 60)
        print(f"\nVoice: {self.voice_name}")
        if self.description:
            print(f"Style: {self.description}")
        print("=" * 60)

    def print_success(self, output_file: Path) -> None:
        """Print success message with file info."""
        print("\n" + "=" * 60)
        print("✓ SUCCESS!")
        print("=" * 60)

        size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"\nCreated: {output_file.name}")
        print(f"Size: {size_mb:.2f} MB")
        print(f"Duration: {self.duration_estimate}")

        # Print any custom success messages
        for line in self.get_success_message():
            print(f"  ✓ {line}")

        print("\n" + "=" * 60)
        print(f"Play with: mpv {output_file.name}")
        print("=" * 60)

    def run(self) -> bool:
        """
        Execute the full synthesis pipeline.

        Returns:
            True if synthesis completed successfully, False otherwise
        """
        self.print_header()

        # Get chunks
        chunks = self.get_chunks()
        if not chunks:
            self.logger.error("No chunks returned from get_chunks()")
            return False

        print(f"\nSplit into {len(chunks)} chunks")

        # Use temporary directory for chunk files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            chunk_files: List[Path] = []

            # Synthesize each chunk
            for i, chunk in enumerate(chunks, 1):
                chunk_file = tmpdir_path / f"chunk_{i:02d}.mp3"
                if self.synthesize_chunk(chunk, chunk_file, i):
                    chunk_files.append(chunk_file)
                else:
                    self.logger.error(f"Failed at chunk {i}, aborting")
                    return False

            # Concatenate chunks
            print(f"\n{'=' * 60}")
            print("Combining chunks...")

            output_file = self.output_dir / self.output_filename
            if not self.concatenate_chunks(chunk_files, output_file):
                self.logger.error("Failed to concatenate chunks")
                # Keep chunk files for debugging
                print(f"Chunk files preserved in: {tmpdir}")
                return False

        # Success
        self.print_success(output_file)
        return True


# Example usage and testing
if __name__ == "__main__":
    # Demo synthesizer for testing
    class DemoSynthesizer(BaseSynthesizer):
        name = "Demo Synthesis Test"
        output_filename = "demo_test.mp3"
        description = "Test of the base synthesizer"
        duration_estimate = "~10 seconds"

        def get_chunks(self) -> List[str]:
            return [
                '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<prosody rate="100%" pitch="medium">
This is a test of the base synthesizer class.
<break time="500ms"/>
If you hear this message, the synthesis pipeline is working correctly.
</prosody>
</speak>'''
            ]

        def get_success_message(self) -> List[str]:
            return [
                "Base synthesizer is working",
                "Ready for production use"
            ]

    print("Base Synthesizer Module")
    print("=" * 60)
    print("\nThis module provides the BaseSynthesizer class.")
    print("Import and subclass it to create new synthesis scripts.")
    print("\nExample:")
    print("  from base_synthesizer import BaseSynthesizer")
    print("")
    print("  class MySynthesizer(BaseSynthesizer):")
    print("      name = 'My Synthesis'")
    print("      output_filename = 'output.mp3'")
    print("")
    print("      def get_chunks(self):")
    print("          return [ssml_chunk1, ssml_chunk2]")
    print("")
    print("To run a demo synthesis, uncomment the test code below.")
    print("=" * 60)

    # Uncomment to test:
    # demo = DemoSynthesizer()
    # demo.run()
