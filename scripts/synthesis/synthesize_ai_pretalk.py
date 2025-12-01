#!/usr/bin/env python3
from google.cloud import texttospeech
import os
import subprocess

def create_ai_pretalk_chunks():
    """Create natural AI clone introduction (non-hypnotic)"""
    
    chunks = [
        # Chunk 1: Welcome and introduction
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="100%" pitch="medium" volume="medium">
Welcome to this special Dreamweaving and Pathworking session.<break time="500ms"/> If we haven't met, I am the Sacred Digital Dreamweaver, Randy Sailers AI Clone, and I'm really glad you're here with me today.<break time="700ms"/> I'm going to be your guide on this transformative journey into the depths of your mind and spirit.<break time="700ms"/>

In today's session, we'll be connecting with your inner self to help you find clarity, inspiration, or simply experience a moment of deep relaxation.<break time="600ms"/> Whatever your intention is, this experience has been designed with you in mind.
<break time="1000ms"/>
</prosody>

<prosody rate="98%" pitch="medium" volume="medium">
Before we begin, I want to explain what hypnosis actually is.<break time="600ms"/> It's a completely natural process—really just a state of deep relaxation and focused awareness.<break time="600ms"/> It's very similar to what you might experience when you're absorbed in a great book or lost in a daydream.<break time="700ms"/>

The important thing to understand is that you'll remain fully aware and in control the entire time.<break time="600ms"/> You can't get stuck in hypnosis, and your subconscious mind will only accept suggestions that align with your values and goals.<break time="600ms"/> You're always in charge of your experience.
<break time="1000ms"/>
</prosody>

</speak>''',
        
        # Chunk 2: Explaining techniques
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="100%" pitch="medium" volume="medium">
Now, let me tell you about Pathworking and Dreamweaving, which are at the heart of today's journey.<break time="700ms"/>

Pathworking is a powerful mental journey where we use guided imagery to walk along a symbolic path.<break time="600ms"/> Each step along this path evokes inner wisdom, healing, and insight, helping you connect deeply with your mind and spirit.<break time="600ms"/> Think of it as traveling through a dreamscape that's specifically designed to unlock your potential.<break time="800ms"/>

Dreamweaving builds on this by encouraging you to blend your imagination and intuition together.<break time="600ms"/> You'll be crafting vivid experiences that merge creativity and transformation.<break time="600ms"/> Through this process, you can weave a new vision for your future or work through challenges from the past.<break time="700ms"/> It's a really powerful combination of techniques.
<break time="1000ms"/>
</prosody>

</speak>''',
        
        # Chunk 3: Technical setup
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="100%" pitch="medium" volume="medium">
To get the most out of this session, I highly recommend using headphones.<break time="600ms"/> I've designed this experience with stereo audio, which means different sounds and suggestions will be coming through each ear to help guide your mind into a deeply relaxed state.<break time="700ms"/>

You'll also hear subtle binaural beats throughout the session.<break time="600ms"/> These are special tones created by playing slightly different frequencies in each ear.<break time="600ms"/> Your brain processes the difference between these frequencies as a kind of internal rhythm.<break time="600ms"/> You don't need to do anything special—just listen, and they'll naturally help guide your brain toward a state of deep relaxation.
<break time="1000ms"/>
</prosody>

</speak>''',
        
        # Chunk 4: Preparation instructions
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="98%" pitch="medium" volume="medium">
Here's how to prepare for this experience:<break time="600ms"/> Find a quiet, comfortable space where you won't be disturbed.<break time="600ms"/> You can sit or lie down, whatever feels most comfortable to you.<break time="700ms"/>

Once you're settled, simply close your eyes and let my voice guide you.<break time="600ms"/> Allow the experience to unfold naturally.<break time="700ms"/> Remember, you're always in control during this process.<break time="600ms"/> If you need to at any moment, you can simply open your eyes and return to full awareness.<break time="700ms"/>

There's no right or wrong way to do this—just participate in whatever way feels natural to you.<break time="700ms"/>
<break time="1000ms"/>
</prosody>

<prosody rate="100%" pitch="medium" volume="medium">
If this is your first time doing something like this, that's completely fine—just take things at your own pace.<break time="700ms"/> And here's something interesting: every time you practice this type of work, it tends to get easier and more powerful.<break time="700ms"/> The more you listen to these sessions and become familiar with my voice, the deeper you'll be able to go.<break time="600ms"/> Each session builds on the previous ones, guiding you into progressively deeper states of relaxation and self-discovery.<break time="700ms"/>
<break time="1000ms"/>
</prosody>

</speak>''',
        
        # Chunk 5: Transition and call to action
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="100%" pitch="medium" volume="medium">
Today's journey is all about walking a tranquil path to uncover the insights and inspiration that are waiting within you.<break time="600ms"/> I'll be guiding you every step of the way as we explore this inner landscape together.<break time="800ms"/>

So go ahead and take a moment to get comfortable.<break time="600ms"/> Relax your body, notice your breath, and allow yourself to become curious about what you might discover in this session.<break time="800ms"/>

When you're ready, we'll begin.
<break time="1500ms"/>
</prosody>

<prosody rate="102%" pitch="medium" volume="medium">
And lastly, if you enjoy this content, I'd really appreciate it if you'd like, share, or subscribe to my channel.<break time="600ms"/> It helps me create more of these experiences and builds a community of explorers who value personal transformation and growth.
<break time="1200ms"/>
</prosody>

<prosody rate="100%" pitch="medium" volume="medium">
Ready?<break time="700ms"/> Let's begin.
<break time="1000ms"/>
</prosody>

</speak>'''
    ]
    
    return chunks

def synthesize_chunk(client, chunk_num, ssml, output_file):
    """Synthesize with natural conversational voice"""
    
    print(f"\nChunk {chunk_num}/5:")
    print(f"  Size: {len(ssml.encode('utf-8'))} bytes")
    
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-I"
    )
    
    # NATURAL CONVERSATIONAL SETTINGS
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,           # Normal conversational pace
        pitch=0.0,                    # Natural pitch
        volume_gain_db=0.0,          # Normal volume
        sample_rate_hertz=24000,
        effects_profile_id=["headphone-class-device"]
    )
    
    try:
        print(f"  Synthesizing...")
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        with open(output_file, 'wb') as out:
            out.write(response.audio_content)
        
        print(f"  ✓ Saved {len(response.audio_content) / 1024:.1f} KB")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("="*60)
    print("AI Clone Pretalk - Natural Conversational Style")
    print("="*60)
    print("\nChanges made:")
    print("  ✓ Removed all hypnotic tag questions")
    print("  ✓ Changed to declarative statements")
    print("  ✓ Normal speaking pace (100%)")
    print("  ✓ Natural pitch (0st)")
    print("  ✓ Conversational, friendly tone")
    print("  ✓ Kept AI Clone branding")
    print("  ✓ Informative rather than suggestive")
    print("="*60)
    
    chunks = create_ai_pretalk_chunks()
    print(f"\nCreated {len(chunks)} chunks")
    
    client = texttospeech.TextToSpeechClient()
    
    chunk_files = []
    for i, chunk in enumerate(chunks, 1):
        output_file = f"ai_pretalk_{i:02d}.mp3"
        if synthesize_chunk(client, i, chunk, output_file):
            chunk_files.append(output_file)
        else:
            print(f"\n❌ Failed at chunk {i}")
            return
    
    print(f"\n{'='*60}")
    print("Combining all chunks...")
    
    with open('filelist.txt', 'w') as f:
        for cf in chunk_files:
            f.write(f"file '{cf}'\n")
    
    result = subprocess.run(
        ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'filelist.txt', '-c', 'copy', 'ai_pretalk_natural.mp3', '-y'],
        capture_output=True
    )

    if result.returncode == 0 and os.path.exists('ai_pretalk_natural.mp3'):
        print("\n" + "="*60)
        print("✓ SUCCESS!")
        print("="*60)
        
        size_mb = os.path.getsize('ai_pretalk_natural.mp3') / (1024 * 1024)
        print(f"\nCreated: ai_pretalk_natural.mp3")
        print(f"Size: {size_mb:.2f} MB")
        print(f"Duration: ~3-4 minutes")
        print(f"\nThis AI Clone pretalk:")
        print(f"  ✓ Sounds natural and conversational")
        print(f"  ✓ No hypnotic language patterns")
        print(f"  ✓ Friendly and informative")
        print(f"  ✓ Clear explanations")
        print(f"  ✓ Professional YouTube-style intro")
        print(f"  ✓ Maintains AI Clone branding")
        
        for cf in chunk_files:
            os.remove(cf)
        os.remove('filelist.txt')
        
        print("\n" + "="*60)
        print("Files available:")
        print("  • intro_natural.mp3         (generic version)")
        print("  • ai_pretalk_natural.mp3    (AI Clone version) NEW!")
        print("\nPlay: mpv ai_pretalk_natural.mp3")
        print("="*60)
        
    else:
        print("\n❌ Combination failed")
        print("Chunks saved separately:", chunk_files)

if __name__ == "__main__":
    main()
