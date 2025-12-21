#!/home/rsalars/Projects/dreamweaving/venv_coqui/bin/python
"""
Simple Coqui TTS Voice Generator

Strips SSML and generates audio from plain text.
Much faster than full SSML parsing but loses pause timing.

Usage:
    venv_coqui/bin/python generate_voice_coqui_simple.py <ssml_file> <output_dir>
"""

import re
import sys
from pathlib import Path

try:
    from TTS.api import TTS
    from pydub import AudioSegment
    from pydub.effects import normalize
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    sys.exit(1)


def strip_ssml(ssml_text: str) -> str:
    """Remove all SSML tags and return plain text."""
    # Remove XML declaration
    text = re.sub(r'<\?xml[^>]*\?>', '', ssml_text)
    # Remove comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # Remove all tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove DVE markers
    text = re.sub(r'\[DVE:[^\]]+\]', '', text)
    # Remove style markers
    text = re.sub(r'\[[^\]]+\]', '', text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_voice_coqui_simple.py <ssml_file> <output_dir>")
        sys.exit(1)
    
    ssml_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    if not ssml_file.exists():
        print(f"❌ SSML file not found: {ssml_file}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("   COQUI TTS VOICE GENERATOR (Simple Mode)")
    print("=" * 70)
    print()
    
    # Read and strip SSML
    print(f"📖 Reading SSML: {ssml_file}")
    with open(ssml_file, 'r', encoding='utf-8') as f:
        ssml_text = f.read()
    
    plain_text = strip_ssml(ssml_text)
    char_count = len(plain_text)
    print(f"   Character count: {char_count:,}")
    
    # Load model
    print("\n🤖 Loading Coqui TTS model (this takes ~30 seconds)...")
    model_name = "tts_models/en/ljspeech/tacotron2-DDC"
    tts = TTS(model_name=model_name, progress_bar=False, gpu=False)
    print("   ✅ Model loaded")
    
    # Generate audio
    print(f"\n🎙️  Generating audio ({char_count:,} characters)...")
    print("   This may take 2-5 minutes...")
    
    temp_file = output_dir / "voice_synth_temp.wav"
    tts.tts_to_file(text=plain_text, file_path=str(temp_file))
    
    # Normalize and convert to MP3
    print("🎚️  Normalizing and converting to MP3...")
    audio = AudioSegment.from_wav(str(temp_file))
    audio = normalize(audio)
    
    output_file = output_dir / "voice_synth.mp3"
    audio.export(str(output_file), format="mp3", bitrate="128k")
    
    # Clean up
    temp_file.unlink()
    
    duration = len(audio) / 1000
    print(f"\n✅ Complete! Duration: {duration:.1f} seconds")
    print(f"   Output: {output_file}")


if __name__ == "__main__":
    main()
