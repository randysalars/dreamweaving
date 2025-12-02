#!/usr/bin/env python3
"""
Garden of Eden Path-Working: Audio Generator
Uses Google Cloud Text-to-Speech to create hypnotic audio from SSML

Requirements:
    pip install google-cloud-texttospeech

Usage:
    python3 generate_audio.py garden_of_eden_hypnosis.ssml output.mp3

Author: The Sacred Digital Dreamweaver - Randy Sailer's Autonomous AI Clone
"""

from google.cloud import texttospeech
import sys
import os

def print_header():
    """Print a nice header"""
    print("=" * 70)
    print("   Garden of Eden Path-Working: Audio Generator")
    print("   Hypnotic SSML → Professional Audio")
    print("=" * 70)
    print()

def synthesize_ssml_file(ssml_filepath, output_filepath, voice_name="en-US-Neural2-A"):
    """
    Synthesizes speech from SSML file using Google Cloud TTS.
    
    Args:
        ssml_filepath: Path to input SSML file
        output_filepath: Path for output MP3 file
        voice_name: Google TTS voice to use (default: Neural2-A for hypnosis)
    """
    
    # Validate input file exists
    if not os.path.exists(ssml_filepath):
        print(f"❌ Error: Input file not found: {ssml_filepath}")
        sys.exit(1)
    
    # Initialize the Text-to-Speech client
    try:
        client = texttospeech.TextToSpeechClient()
    except Exception as e:
        print(f"❌ Error: Could not initialize Google Cloud TTS client.")
        print(f"   Make sure you've run: gcloud auth application-default login")
        print(f"   Error details: {e}")
        sys.exit(1)

    # Read SSML content from file
    print(f"📖 Reading SSML from: {ssml_filepath}")
    with open(ssml_filepath, 'r', encoding='utf-8') as f:
        ssml_content = f.read()
    
    # Calculate approximate character count
    char_count = len(ssml_content)
    print(f"   Character count: {char_count:,}")
    
    # Prepare synthesis input
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_content)

    # Configure voice parameters (optimized for hypnosis)
    # Correct gender mapping for Neural2 voices:
    # Female: C, E, F, G, H
    # Male: A, D, I, J
    voice_letter = voice_name.split('-')[-1] if '-' in voice_name else voice_name[-1]
    female_voices = {'C', 'E', 'F', 'G', 'H'}
    is_female = voice_letter in female_voices

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE if is_female else texttospeech.SsmlVoiceGender.MALE
    )

    # Configure audio output (optimized for hypnotic delivery)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.85,  # Slightly slower for hypnotic effect
        pitch=-2.0,          # Lower pitch for calming effect
        effects_profile_id=["headphone-class-device"],  # Optimized for headphones
        sample_rate_hertz=24000  # High quality
    )

    # Synthesize speech
    print(f"🎙️  Generating audio with voice: {voice_name}")
    print(f"   Speaking rate: 0.85x (hypnotic pace)")
    print(f"   Pitch: -2.0 semitones (calming)")
    print()
    print("⏳ Synthesizing... (this may take 30-60 seconds)")
    
    try:
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
    except Exception as e:
        print(f"❌ Error during synthesis: {e}")
        sys.exit(1)

    # Save the audio to a file
    print(f"💾 Saving audio to: {output_filepath}")
    with open(output_filepath, 'wb') as out:
        out.write(response.audio_content)
    
    # Calculate file size
    file_size_mb = os.path.getsize(output_filepath) / (1024 * 1024)
    
    print()
    print("=" * 70)
    print("✅ SUCCESS! Audio generated successfully!")
    print("=" * 70)
    print(f"📁 Output file: {output_filepath}")
    print(f"📊 File size: {file_size_mb:.2f} MB")
    print(f"⏱️  Estimated duration: ~25-30 minutes")
    print(f"🎧 Optimized for: Headphone listening")
    print()
    print("💡 Tips:")
    print("   • Listen with headphones in a quiet space")
    print("   • Test pronunciation of 'path-working' (should be two words)")
    print("   • If too slow, regenerate with speakingRate=0.90")
    print("   • If too fast, regenerate with speakingRate=0.80")
    print()

def main():
    """Main execution function"""
    print_header()
    
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("❌ Error: Missing required arguments")
        print()
        print("Usage:")
        print("   python3 generate_audio.py <input.ssml> <output.mp3> [voice_name]")
        print()
        print("Example:")
        print("   python3 generate_audio.py garden_of_eden_hypnosis.ssml output.mp3")
        print()
        print("Optional voice_name (default: en-US-Neural2-A):")
        print("   Female voices: en-US-Neural2-A, en-US-Neural2-C, en-US-Neural2-E, en-US-Neural2-F")
        print("   Male voices: en-US-Neural2-D, en-US-Neural2-I, en-US-Neural2-J")
        print()
        sys.exit(1)
    
    ssml_file = sys.argv[1]
    output_file = sys.argv[2]
    voice_name = sys.argv[3] if len(sys.argv) > 3 else "en-US-Neural2-A"
    
    # Generate the audio
    synthesize_ssml_file(ssml_file, output_file, voice_name)

if __name__ == "__main__":
    main()
