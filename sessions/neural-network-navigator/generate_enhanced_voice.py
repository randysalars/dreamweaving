#!/usr/bin/env python3
"""
Generate enhanced voice track with improved pacing and transitions
Removes metadata from spoken content and adds strategic pauses
"""

from google.cloud import texttospeech
import sys
import os

def generate_enhanced_voice():
    """Generate enhanced voice track using Google Cloud TTS"""

    print("=" * 70)
    print("   Neural Network Navigator: Enhanced Voice Generation")
    print("   Improved pacing, extended content, strategic pauses")
    print("=" * 70)
    print()

    # Initialize the TTS client
    try:
        client = texttospeech.TextToSpeechClient()
        print("✓ Connected to Google Cloud TTS")
    except Exception as e:
        print(f"❌ Error: Could not initialize Google Cloud TTS client.")
        print(f"   Make sure you've run: gcloud auth application-default login")
        print(f"   Error details: {e}")
        sys.exit(1)

    # Read the enhanced SSML script
    ssml_file = "working_files/voice_script_enhanced.ssml"
    print(f"📖 Reading enhanced SSML from: {ssml_file}")

    if not os.path.exists(ssml_file):
        print(f"❌ Error: Script file not found: {ssml_file}")
        sys.exit(1)

    with open(ssml_file, 'r', encoding='utf-8') as f:
        ssml_content = f.read()

    # Calculate size
    char_count = len(ssml_content)
    byte_count = len(ssml_content.encode('utf-8'))
    print(f"   Character count: {char_count:,}")
    print(f"   Byte count: {byte_count:,}")

    if byte_count > 5000:
        print(f"❌ Error: Script exceeds 5000 byte limit ({byte_count} bytes)")
        print(f"   Please use generate_audio_chunked.py for large files")
        sys.exit(1)

    # Configure voice
    voice_name = "en-US-Neural2-A"  # Natural female voice
    print(f"\n🎙️  Generating audio with voice: {voice_name}")
    print(f"   Speaking rate: 0.85x (hypnotic pace)")
    print(f"   Pitch: -2.0 semitones (calming)")
    print(f"   Profile: Headphone-optimized")

    # Set up synthesis
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_content)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.85,
        pitch=-2.0,
        effects_profile_id=["headphone-class-device"],
        sample_rate_hertz=24000
    )

    # Generate audio
    print("\n⏳ Synthesizing speech... (this may take 1-2 minutes)")

    try:
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        print("✓ Speech synthesis complete")
    except Exception as e:
        print(f"\n❌ Error during synthesis: {e}")
        sys.exit(1)

    # Save output
    output_file = "working_files/voice_neural_navigator_enhanced.mp3"
    print(f"\n💾 Saving audio to: {output_file}")

    with open(output_file, 'wb') as out:
        out.write(response.audio_content)

    # Calculate file size
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

    print()
    print("=" * 70)
    print("✅ SUCCESS! Enhanced voice track generated!")
    print("=" * 70)
    print(f"📁 Output file: {output_file}")
    print(f"📊 File size: {file_size_mb:.2f} MB")
    print(f"🎧 Optimized for: Headphone listening")
    print()
    print("💡 Next steps:")
    print("   1. Listen to verify pacing and content")
    print("   2. Generate enhanced binaural track with sound effects")
    print("   3. Mix voice + binaural + effects")
    print()
    print("✨ Improvements:")
    print("   • Removed script metadata from spoken content")
    print("   • Extended pauses on 'down...down...down' transitions")
    print("   • Extended pauses on 'up...up...up' transitions")
    print("   • Added additional journey content for full duration")
    print("   • Maintained natural, human voice quality")
    print()

if __name__ == "__main__":
    generate_enhanced_voice()
