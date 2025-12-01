#!/usr/bin/env python3
from google.cloud import texttospeech
import os
import subprocess

def create_hypnotic_chunks():
    """Create hypnotic opening split into chunks"""
    
    chunks = [
        # Chunk 1: Opening and initial relaxation
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="75%" pitch="-3st" volume="soft">
Begin by finding a position that feels <emphasis level="moderate">just right</emphasis> for you
<break time="1s"/>
whether sitting or lying down, in a <emphasis level="moderate">quiet, safe space</emphasis>
where you can <emphasis level="moderate">let go completely</emphasis>.
<break time="2s"/>

As you settle in, <emphasis level="moderate">gently</emphasis> close your eyes,
<break time="1s"/>
and draw in a slow, <emphasis level="moderate">deep breath</emphasis>
<break time="2s"/>
holding it for a moment
<break time="1500ms"/>
and then <emphasis level="moderate">releasing it</emphasis>,
letting it flow out like a <emphasis level="moderate">soft sigh</emphasis>.
<break time="2500ms"/>
</prosody>

<prosody rate="70%" pitch="-4st">
With each breath, notice how your mind begins to <emphasis level="moderate">quiet</emphasis>,
<break time="1500ms"/>
resting in the gentle <emphasis level="moderate">pause</emphasis>
between each inhale <break time="1s"/> and exhale,
<break time="2s"/>
as if the world around you is <emphasis level="moderate">softening</emphasis>,
<break time="1s"/>
<emphasis level="moderate">fading</emphasis> into stillness.
<break time="3s"/>
</prosody>

</speak>''',
        
        # Chunk 2: Visualization
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="72%" pitch="-3st">
Picture a <emphasis level="moderate">soothing, radiant energy</emphasis> enveloping you
<break time="1500ms"/>
a warm, <emphasis level="moderate">golden light</emphasis>
that feels as comforting as a <emphasis level="moderate">tender embrace</emphasis>
<break time="1s"/>
or a soft, <emphasis level="moderate">protective cocoon</emphasis>.
<break time="2s"/>

This light wraps around you, and as it does,
<break time="1s"/>
your body naturally begins to <emphasis level="moderate">unwind</emphasis>.
<break time="2s"/>

Feel the muscles in your forehead <emphasis level="moderate">smoothing out</emphasis>,
<break time="1s"/>
as if a gentle hand is brushing away any tightness.
<break time="1500ms"/>
Sense your jaw <emphasis level="moderate">loosening</emphasis>,
<break time="1s"/>
your shoulders <emphasis level="moderate">melting downward</emphasis>,
<break time="1500ms"/>
and every part of you <emphasis level="moderate">sinking deeper</emphasis> into ease.
<break time="3s"/>
</prosody>

</speak>''',
        
        # Chunk 3: Garden and countdown intro
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="68%" pitch="-4st">
With each breath, the outside world <emphasis level="moderate">drifts further away</emphasis>,
<break time="2s"/>
becoming distant, <emphasis level="moderate">irrelevant</emphasis>.
<break time="2s"/>

Instead, imagine stepping into a <emphasis level="moderate">tranquil, sacred space</emphasis>
<break time="1500ms"/>
a breathtaking garden at twilight,
<break time="1s"/>
where the sky glows with hues of <emphasis level="moderate">lavender and amber</emphasis>.
<break time="2500ms"/>

Every detail is alive with <emphasis level="moderate">serenity</emphasis>:
<break time="1s"/>
the soft rustle of leaves,
<break time="1s"/>
the delicate scent of <emphasis level="moderate">jasmine and sandalwood</emphasis>
<break time="1s"/>
carried on a <emphasis level="moderate">cool breeze</emphasis>.
<break time="3s"/>
</prosody>

<prosody rate="70%" pitch="-3st">
Now, as this <emphasis level="moderate">serene feeling</emphasis> wraps around you
<break time="1500ms"/>
like a warm, familiar memory,
<break time="2s"/>
allow yourself to drift even further into relaxation
<break time="1s"/>
with a <emphasis level="moderate">gentle countdown</emphasis>.
<break time="2500ms"/>

With each number I guide you through,
<break time="1s"/>
you'll find yourself <emphasis level="moderate">sinking deeper</emphasis>
<break time="1s"/>
into a state of <emphasis level="moderate">profound calm</emphasis>
and <emphasis level="moderate">inner stillness</emphasis>.
<break time="3s"/>

Let's begin this <emphasis level="moderate">journey inward</emphasis>:
<break time="2s"/>
</prosody>

</speak>''',
        
        # Chunk 4: Countdown 10-8
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="65%" pitch="-3st">
<emphasis level="strong">Ten</emphasis>
<break time="2s"/>
A wave of relaxation starts at the very top of your head,
<break time="1500ms"/>
<emphasis level="moderate">cascading down</emphasis> like warm water,
<break time="1s"/>
soothing every muscle, every thought,
<break time="1500ms"/>
<emphasis level="moderate">softening</emphasis> your scalp, your face,
<break time="1s"/>
and every tiny fiber of your being.
<break time="3s"/>
</prosody>

<prosody rate="62%" pitch="-4st">
<emphasis level="strong">Nine</emphasis>
<break time="2500ms"/>
With this number, a <emphasis level="moderate">deeper calm</emphasis>
settles behind your closed eyes.
<break time="2s"/>
Feel a <emphasis level="moderate">peaceful stillness</emphasis>
spreading from your forehead to your cheeks,
<break time="1500ms"/>
as if any lingering tension is simply <emphasis level="moderate">dissolving</emphasis>,
<break time="1s"/>
<emphasis level="moderate">melting away</emphasis> into nothingness.
<break time="3s"/>
</prosody>

<prosody rate="60%" pitch="-5st">
<emphasis level="strong">Eight</emphasis>
<break time="3s"/>
Allow your neck and shoulders to <emphasis level="moderate">release completely</emphasis>,
<break time="2s"/>
as if an invisible weight is <emphasis level="moderate">lifting off</emphasis>,
<break time="1500ms"/>
leaving you <emphasis level="moderate">lighter</emphasis>,
<emphasis level="moderate">freer</emphasis>.
<break time="2s"/>
Each exhale becomes a gentle breeze,
<break time="1500ms"/>
carrying away any strain, any burden.
<break time="3s"/>
</prosody>

</speak>''',
        
        # Chunk 5: Countdown 7-5
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="58%" pitch="-5st">
<emphasis level="strong">Seven</emphasis>
<break time="3s"/>
Notice a <emphasis level="moderate">comforting warmth</emphasis>
flowing down your arms,
<break time="2s"/>
relaxing your elbows, your wrists,
<break time="1500ms"/>
all the way to your <emphasis level="moderate">fingertips</emphasis>.
<break time="2s"/>
It's as if each nerve is bathed in a soft,
<emphasis level="moderate">healing glow</emphasis>.
<break time="3s"/>
</prosody>

<prosody rate="55%" pitch="-6st" volume="soft">
<emphasis level="strong">Six</emphasis>
<break time="3s"/>
Let this relaxation spread into your chest, your heart.
<break time="2500ms"/>
With each heartbeat, feel a wave of <emphasis level="moderate">serenity</emphasis>
filling you,
<break time="2s"/>
<emphasis level="moderate">expanding</emphasis> within you,
<break time="1500ms"/>
a quiet assurance that you are <emphasis level="moderate">safe</emphasis>,
<break time="1s"/>
<emphasis level="moderate">supported</emphasis>,
<break time="1s"/>
and at <emphasis level="moderate">peace</emphasis>.
<break time="3s"/>
</prosody>

<prosody rate="52%" pitch="-6st" volume="soft">
<emphasis level="strong">Five</emphasis>
<break time="3s"/>
Your stomach and back <emphasis level="moderate">soften</emphasis> now,
<break time="2500ms"/>
melting into a state of <emphasis level="moderate">perfect harmony</emphasis>.
<break time="3s"/>
Every muscle <emphasis level="moderate">unwinds</emphasis>,
<break time="2s"/>
and with each breath, you feel more <emphasis level="moderate">connected</emphasis>,
<break time="1500ms"/>
more at <emphasis level="moderate">ease</emphasis>.
<break time="3s"/>
</prosody>

</speak>''',
        
        # Chunk 6: Countdown 4-2
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="50%" pitch="-7st" volume="soft">
<emphasis level="strong">Four</emphasis>
<break time="3s"/>
Sense this calm traveling through your hips and thighs,
<break time="3s"/>
<emphasis level="moderate">releasing</emphasis> any hidden tension.
<break time="2500ms"/>
Imagine your legs growing <emphasis level="moderate">lighter</emphasis>,
<break time="2s"/>
almost <emphasis level="moderate">weightless</emphasis>,
<break time="2s"/>
as if they're floating on a gentle current.
<break time="3s"/>
</prosody>

<prosody rate="48%" pitch="-8st" volume="soft">
<emphasis level="strong">Three</emphasis>
<break time="3s"/>
This relaxation flows now into your knees and calves,
<break time="3s"/>
<emphasis level="moderate">deepening</emphasis> with every breath.
<break time="3s"/>
Each exhale draws you further into <emphasis level="moderate">stillness</emphasis>,
<break time="2s"/>
into a quiet <emphasis level="moderate">inner peace</emphasis>
<break time="2s"/>
that feels natural, <emphasis level="moderate">effortless</emphasis>.
<break time="3s"/>
</prosody>

<prosody rate="45%" pitch="-9st" volume="x-soft">
<emphasis level="strong">Two</emphasis>
<break time="3s"/>
Your ankles and feet are now bathed
<break time="2s"/>
in this <emphasis level="moderate">gentle tranquility</emphasis>.
<break time="3s"/>
Picture a wave of <emphasis level="moderate">deep calm</emphasis>
washing over them,
<break time="3s"/>
as if roots of peace are extending from within you,
<break time="2500ms"/>
<emphasis level="moderate">grounding you</emphasis>
into a nourishing, steady earth.
<break time="3s"/>
</prosody>

</speak>''',
        
        # Chunk 7: Number 1 and deepening
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="42%" pitch="-10st" volume="x-soft">
<emphasis level="strong">One</emphasis>
<break time="4s"/>
And at this final number,
<break time="3s"/>
<emphasis level="moderate">surrender completely</emphasis>
<break time="3s"/>
to this state of <emphasis level="moderate">profound relaxation</emphasis>.
<break time="4s"/>
Every part of your body is immersed in <emphasis level="moderate">calm</emphasis>,
<break time="3s"/>
every thought <emphasis level="moderate">quieted</emphasis>,
<break time="3s"/>
and your mind <emphasis level="moderate">open</emphasis>,
<emphasis level="moderate">clear</emphasis>,
<break time="2s"/>
and ready for the <emphasis level="moderate">transformative journey</emphasis> ahead.
<break time="4s"/>
You are at <emphasis level="moderate">peace</emphasis>,
<break time="2s"/>
<emphasis level="moderate">deeply</emphasis> at peace.
<break time="5s"/>
</prosody>

<prosody rate="45%" pitch="-9st" volume="x-soft">
As you rest in this <emphasis level="moderate">deeply relaxed state</emphasis>,
<break time="3s"/>
know that you are <emphasis level="moderate">safe</emphasis>,
<break time="2s"/>
<emphasis level="moderate">held</emphasis>,
<break time="2s"/>
and connected to a wellspring of <emphasis level="moderate">inner wisdom</emphasis>.
<break time="4s"/>

This calm is your <emphasis level="moderate">sanctuary</emphasis>
<break time="3s"/>
a sacred space where thoughts settle
<break time="2s"/>
like leaves on <emphasis level="moderate">still water</emphasis>,
<break time="3s"/>
where your spirit feels free to explore
<break time="2s"/>
the boundless landscape of your <emphasis level="moderate">inner world</emphasis>.
<break time="4s"/>

With every breath, you sink <emphasis level="moderate">deeper</emphasis>
<break time="2s"/>
into this <emphasis level="moderate">transformative awareness</emphasis>,
<break time="3s"/>
ready to uncover insights,
<break time="2s"/>
to <emphasis level="moderate">heal</emphasis>,
<break time="2s"/>
or to simply <emphasis level="moderate">be</emphasis>.
<break time="4s"/>

You are exactly where you need to be,
<break time="3s"/>
and as you breathe,
<break time="2s"/>
you prepare to step even further
<break time="2s"/>
into this <emphasis level="moderate">profound</emphasis>,
<emphasis level="moderate">enriching state of mind</emphasis>.
<break time="5s"/>
</prosody>

</speak>'''
    ]
    
    return chunks

def synthesize_chunk(client, chunk_num, ssml, output_file):
    """Synthesize with deep hypnotic voice"""
    
    print(f"\nChunk {chunk_num}/7:")
    print(f"  Size: {len(ssml.encode('utf-8'))} bytes")
    
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
    
    # DEEP HYPNOTIC MALE VOICE
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-I"
    )
    
    # HYPNOTIC SETTINGS - deep, slow, soothing
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.75,          # Slow hypnotic pace
        pitch=-3.0,                   # Lower, calming pitch
        volume_gain_db=-2.0,         # Slightly quieter
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
    print("Hypnotic Opening - Deep Relaxation Induction")
    print("="*60)
    print("\nVoice: en-US-Neural2-I (deep hypnotic male)")
    print("Style: Slow, deep, profoundly relaxing")
    print("Duration: ~10-12 minutes")
    print("="*60)
    
    chunks = create_hypnotic_chunks()
    print(f"\nCreated {len(chunks)} chunks")
    
    client = texttospeech.TextToSpeechClient()
    
    chunk_files = []
    for i, chunk in enumerate(chunks, 1):
        output_file = f"hypnotic_{i:02d}.mp3"
        if synthesize_chunk(client, i, chunk, output_file):
            chunk_files.append(output_file)
        else:
            print(f"\n❌ Failed at chunk {i}")
            return
    
    print(f"\n{'='*60}")
    print("Combining all chunks...")
    
    # Create filelist
    with open('filelist.txt', 'w') as f:
        for cf in chunk_files:
            f.write(f"file '{cf}'\n")
    
    # Combine
    result = subprocess.run(
        ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'filelist.txt', '-c', 'copy', 'hypnotic_opening.mp3', '-y'],
        capture_output=True
    )

    if result.returncode == 0 and os.path.exists('hypnotic_opening.mp3'):
        print("\n" + "="*60)
        print("✓ SUCCESS!")
        print("="*60)
        
        size_mb = os.path.getsize('hypnotic_opening.mp3') / (1024 * 1024)
        print(f"\nCreated: hypnotic_opening.mp3")
        print(f"Size: {size_mb:.2f} MB")
        print(f"Duration: ~10-12 minutes")
        print(f"Voice: Deep hypnotic male (Neural2-I)")
        
        # Cleanup
        print(f"\nCleaning up {len(chunk_files)} temporary files...")
        for cf in chunk_files:
            os.remove(cf)
        os.remove('filelist.txt')
        
        print("\n" + "="*60)
        print("Play with: mpv hypnotic_opening.mp3")
        print("\nThis is a deep relaxation induction with:")
        print("  • Progressive muscle relaxation")
        print("  • Guided visualization")
        print("  • 10-to-1 countdown deepener")
        print("  • Sanctuary establishment")
        print("="*60)
        
    else:
        print("\n❌ Combination failed. Chunks saved separately:")
        for cf in chunk_files:
            print(f"  - {cf}")

if __name__ == "__main__":
    main()
