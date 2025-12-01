#!/usr/bin/env python3
"""
Generate voice using Edge TTS with Ava voice
Reads SSML and converts to speech
"""

import asyncio
import re
from pathlib import Path
import edge_tts

async def generate_voice():
    """Generate voice using Edge TTS"""

    # Read SSML file
    ssml_file = Path("script.ssml")
    print(f"Reading SSML from {ssml_file}...")

    with open(ssml_file, 'r', encoding='utf-8') as f:
        ssml_content = f.read()

    # Edge TTS can handle SSML directly
    voice = "en-US-AvaNeural"
    output_file = "working_files/voice_atlas_ava.mp3"

    print(f"Generating speech with {voice}...")
    print(f"Output: {output_file}")

    # Create the communicate object
    communicate = edge_tts.Communicate(ssml_content, voice)

    # Generate and save
    await communicate.save(output_file)

    print(f"✅ Voice generation complete: {output_file}")

if __name__ == "__main__":
    asyncio.run(generate_voice())
