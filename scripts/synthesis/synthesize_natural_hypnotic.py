#!/usr/bin/env python3
from google.cloud import texttospeech
import os

def create_natural_hypnotic_chunks():
    """Create naturally hypnotic opening - human but still trance-inducing"""
    
    chunks = [
        # Chunk 1: Opening - More natural pacing
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="85%" pitch="-1st" volume="soft">
Begin by finding a position<break time="800ms"/> that feels <emphasis level="moderate">just right</emphasis> for you
<break time="1200ms"/>
whether sitting or lying down,<break time="600ms"/> in a <emphasis level="moderate">quiet, safe space</emphasis>
<break time="1000ms"/>
where you can <emphasis level="moderate">let go completely</emphasis>.
<break time="1800ms"/>

As you settle in,<break time="700ms"/> <emphasis level="moderate">gently</emphasis> close your eyes,
<break time="1200ms"/>
and draw in a slow,<break time="600ms"/> <emphasis level="moderate">deep breath</emphasis>
<break time="1500ms"/>
holding it for a moment
<break time="1200ms"/>
and then <emphasis level="moderate">releasing it</emphasis>,
<break time="800ms"/>
letting it flow out<break time="600ms"/> like a <emphasis level="moderate">soft sigh</emphasis>.
<break time="2000ms"/>
</prosody>

<prosody rate="82%" pitch="-1.5st" volume="soft">
With each breath,<break time="800ms"/> notice how your mind begins to <emphasis level="moderate">quiet</emphasis>,
<break time="1200ms"/>
resting in the gentle <emphasis level="moderate">pause</emphasis>
<break time="900ms"/>
between each inhale<break time="700ms"/> and exhale,
<break time="1500ms"/>
as if the world around you<break time="700ms"/> is <emphasis level="moderate">softening</emphasis>,
<break time="1000ms"/>
<emphasis level="moderate">fading</emphasis> into stillness.
<break time="2000ms"/>
</prosody>

</speak>''',
        
        # Chunk 2: Visualization - Natural flow with varied pacing
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="83%" pitch="-1st" volume="soft">
Picture a <emphasis level="moderate">soothing, radiant energy</emphasis><break time="800ms"/> enveloping you
<break time="1200ms"/>
a warm,<break time="600ms"/> <emphasis level="moderate">golden light</emphasis>
<break time="1000ms"/>
that feels as comforting<break time="700ms"/> as a <emphasis level="moderate">tender embrace</emphasis>
<break time="1200ms"/>
or a soft,<break time="600ms"/> <emphasis level="moderate">protective cocoon</emphasis>.
<break time="1800ms"/>

This light wraps around you,<break time="800ms"/> and as it does,
<break time="1200ms"/>
your body naturally begins<break time="700ms"/> to <emphasis level="moderate">unwind</emphasis>.
<break time="1800ms"/>

Feel the muscles in your forehead<break time="800ms"/> <emphasis level="moderate">smoothing out</emphasis>,
<break time="1200ms"/>
as if a gentle hand<break time="700ms"/> is brushing away any tightness.
<break time="1500ms"/>
Sense your jaw <emphasis level="moderate">loosening</emphasis>,
<break time="900ms"/>
your shoulders <emphasis level="moderate">melting downward</emphasis>,
<break time="1200ms"/>
and every part of you<break time="800ms"/> <emphasis level="moderate">sinking deeper</emphasis> into ease.
<break time="2000ms"/>
</prosody>

</speak>''',
        
        # Chunk 3: Garden - Natural descriptive flow
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="80%" pitch="-1.5st" volume="soft">
With each breath,<break time="800ms"/> the outside world<break time="700ms"/> <emphasis level="moderate">drifts further away</emphasis>,
<break time="1500ms"/>
becoming distant,<break time="800ms"/> <emphasis level="moderate">irrelevant</emphasis>.
<break time="1800ms"/>

Instead,<break time="700ms"/> imagine stepping into<break time="800ms"/> a <emphasis level="moderate">tranquil, sacred space</emphasis>
<break time="1200ms"/>
a breathtaking garden<break time="700ms"/> at twilight,
<break time="1200ms"/>
where the sky glows<break time="700ms"/> with hues of <emphasis level="moderate">lavender and amber</emphasis>.
<break time="2000ms"/>

Every detail<break time="800ms"/> is alive with <emphasis level="moderate">serenity</emphasis>:
<break time="1200ms"/>
the soft rustle of leaves,
<break time="900ms"/>
the delicate scent<break time="700ms"/> of <emphasis level="moderate">jasmine and sandalwood</emphasis>
<break time="1200ms"/>
carried on a <emphasis level="moderate">cool breeze</emphasis>.
<break time="2500ms"/>
</prosody>

<prosody rate="82%" pitch="-1st" volume="soft">
Now,<break time="800ms"/> as this <emphasis level="moderate">serene feeling</emphasis> wraps around you
<break time="1200ms"/>
like a warm,<break time="600ms"/> familiar memory,
<break time="1500ms"/>
allow yourself to drift<break time="800ms"/> even further into relaxation
<break time="1200ms"/>
with a <emphasis level="moderate">gentle countdown</emphasis>.
<break time="2000ms"/>

With each number<break time="700ms"/> I guide you through,
<break time="1200ms"/>
you'll find yourself<break time="800ms"/> <emphasis level="moderate">sinking deeper</emphasis>
<break time="1200ms"/>
into a state of <emphasis level="moderate">profound calm</emphasis>
<break time="900ms"/>
and <emphasis level="moderate">inner stillness</emphasis>.
<break time="2000ms"/>

Let's begin<break time="800ms"/> this <emphasis level="moderate">journey inward</emphasis>:
<break time="1800ms"/>
</prosody>

</speak>''',
        
        # Chunk 4: Countdown 10-8 - Natural progression
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="78%" pitch="-1.5st" volume="soft">
<emphasis level="strong">Ten</emphasis>
<break time="1800ms"/>
A wave of relaxation<break time="800ms"/> starts at the very top<break time="700ms"/> of your head,
<break time="1200ms"/>
<emphasis level="moderate">cascading down</emphasis><break time="800ms"/> like warm water,
<break time="1200ms"/>
soothing every muscle,<break time="700ms"/> every thought,
<break time="1200ms"/>
<emphasis level="moderate">softening</emphasis> your scalp,<break time="700ms"/> your face,
<break time="1000ms"/>
and every tiny fiber<break time="700ms"/> of your being.
<break time="2200ms"/>
</prosody>

<prosody rate="76%" pitch="-2st" volume="soft">
<emphasis level="strong">Nine</emphasis>
<break time="2000ms"/>
With this number,<break time="800ms"/> a <emphasis level="moderate">deeper calm</emphasis>
<break time="1000ms"/>
settles behind your closed eyes.
<break time="1500ms"/>
Feel a <emphasis level="moderate">peaceful stillness</emphasis>
<break time="800ms"/>
spreading from your forehead<break time="700ms"/> to your cheeks,
<break time="1200ms"/>
as if any lingering tension<break time="800ms"/> is simply <emphasis level="moderate">dissolving</emphasis>,
<break time="1200ms"/>
<emphasis level="moderate">melting away</emphasis><break time="800ms"/> into nothingness.
<break time="2200ms"/>
</prosody>

<prosody rate="74%" pitch="-2st" volume="soft">
<emphasis level="strong">Eight</emphasis>
<break time="2000ms"/>
Allow your neck and shoulders<break time="800ms"/> to <emphasis level="moderate">release completely</emphasis>,
<break time="1500ms"/>
as if an invisible weight<break time="800ms"/> is <emphasis level="moderate">lifting off</emphasis>,
<break time="1200ms"/>
leaving you <emphasis level="moderate">lighter</emphasis>,
<break time="800ms"/>
<emphasis level="moderate">freer</emphasis>.
<break time="1500ms"/>
Each exhale<break time="700ms"/> becomes a gentle breeze,
<break time="1200ms"/>
carrying away<break time="800ms"/> any strain,<break time="700ms"/> any burden.
<break time="2500ms"/>
</prosody>

</speak>''',
        
        # Chunk 5: Countdown 7-5 - Deepening naturally
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="72%" pitch="-2st" volume="soft">
<emphasis level="strong">Seven</emphasis>
<break time="2000ms"/>
Notice a <emphasis level="moderate">comforting warmth</emphasis>
<break time="1000ms"/>
flowing down your arms,
<break time="1500ms"/>
relaxing your elbows,<break time="700ms"/> your wrists,
<break time="1200ms"/>
all the way<break time="700ms"/> to your <emphasis level="moderate">fingertips</emphasis>.
<break time="1500ms"/>
It's as if each nerve<break time="800ms"/> is bathed in a soft,
<break time="1000ms"/>
<emphasis level="moderate">healing glow</emphasis>.
<break time="2500ms"/>
</prosody>

<prosody rate="70%" pitch="-2.5st" volume="soft">
<emphasis level="strong">Six</emphasis>
<break time="2200ms"/>
Let this relaxation<break time="800ms"/> spread into your chest,<break time="700ms"/> your heart.
<break time="1800ms"/>
With each heartbeat,<break time="800ms"/> feel a wave of <emphasis level="moderate">serenity</emphasis>
<break time="1000ms"/>
filling you,
<break time="1500ms"/>
<emphasis level="moderate">expanding</emphasis> within you,
<break time="1200ms"/>
a quiet assurance<break time="800ms"/> that you are <emphasis level="moderate">safe</emphasis>,
<break time="1000ms"/>
<emphasis level="moderate">supported</emphasis>,
<break time="1000ms"/>
and at <emphasis level="moderate">peace</emphasis>.
<break time="2500ms"/>
</prosody>

<prosody rate="68%" pitch="-2.5st" volume="soft">
<emphasis level="strong">Five</emphasis>
<break time="2200ms"/>
Your stomach and back<break time="800ms"/> <emphasis level="moderate">soften</emphasis> now,
<break time="1500ms"/>
melting into a state<break time="800ms"/> of <emphasis level="moderate">perfect harmony</emphasis>.
<break time="2000ms"/>
Every muscle <emphasis level="moderate">unwinds</emphasis>,
<break time="1500ms"/>
and with each breath,<break time="800ms"/> you feel more <emphasis level="moderate">connected</emphasis>,
<break time="1200ms"/>
more at <emphasis level="moderate">ease</emphasis>.
<break time="2500ms"/>
</prosody>

</speak>''',
        
        # Chunk 6: Countdown 4-2 - Progressive deepening
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="66%" pitch="-3st" volume="soft">
<emphasis level="strong">Four</emphasis>
<break time="2200ms"/>
Sense this calm<break time="800ms"/> traveling through your hips<break time="700ms"/> and thighs,
<break time="2000ms"/>
<emphasis level="moderate">releasing</emphasis><break time="800ms"/> any hidden tension.
<break time="1800ms"/>
Imagine your legs<break time="800ms"/> growing <emphasis level="moderate">lighter</emphasis>,
<break time="1500ms"/>
almost <emphasis level="moderate">weightless</emphasis>,
<break time="1500ms"/>
as if they're floating<break time="800ms"/> on a gentle current.
<break time="2800ms"/>
</prosody>

<prosody rate="64%" pitch="-3st" volume="soft">
<emphasis level="strong">Three</emphasis>
<break time="2500ms"/>
This relaxation<break time="800ms"/> flows now<break time="700ms"/> into your knees and calves,
<break time="2000ms"/>
<emphasis level="moderate">deepening</emphasis><break time="800ms"/> with every breath.
<break time="2000ms"/>
Each exhale<break time="800ms"/> draws you further<break time="700ms"/> into <emphasis level="moderate">stillness</emphasis>,
<break time="1500ms"/>
into a quiet <emphasis level="moderate">inner peace</emphasis>
<break time="1500ms"/>
that feels natural,<break time="800ms"/> <emphasis level="moderate">effortless</emphasis>.
<break time="3000ms"/>
</prosody>

<prosody rate="62%" pitch="-3.5st" volume="x-soft">
<emphasis level="strong">Two</emphasis>
<break time="2500ms"/>
Your ankles and feet<break time="800ms"/> are now bathed
<break time="1500ms"/>
in this <emphasis level="moderate">gentle tranquility</emphasis>.
<break time="2000ms"/>
Picture a wave<break time="800ms"/> of <emphasis level="moderate">deep calm</emphasis>
<break time="1000ms"/>
washing over them,
<break time="2000ms"/>
as if roots of peace<break time="800ms"/> are extending from within you,
<break time="1800ms"/>
<emphasis level="moderate">grounding you</emphasis>
<break time="1000ms"/>
into a nourishing,<break time="700ms"/> steady earth.
<break time="3200ms"/>
</prosody>

</speak>''',
        
        # Chunk 7: Number 1 and deepening - Deepest but still natural
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="60%" pitch="-3.5st" volume="x-soft">
<emphasis level="strong">One</emphasis>
<break time="2800ms"/>
And at this final number,
<break time="2000ms"/>
<emphasis level="moderate">surrender completely</emphasis>
<break time="2000ms"/>
to this state<break time="800ms"/> of <emphasis level="moderate">profound relaxation</emphasis>.
<break time="2500ms"/>
Every part of your body<break time="800ms"/> is immersed in <emphasis level="moderate">calm</emphasis>,
<break time="2000ms"/>
every thought <emphasis level="moderate">quieted</emphasis>,
<break time="2000ms"/>
and your mind <emphasis level="moderate">open</emphasis>,
<break time="1000ms"/>
<emphasis level="moderate">clear</emphasis>,
<break time="1500ms"/>
and ready<break time="800ms"/> for the <emphasis level="moderate">transformative journey</emphasis> ahead.
<break time="2500ms"/>
You are at <emphasis level="moderate">peace</emphasis>,
<break time="1500ms"/>
<emphasis level="moderate">deeply</emphasis> at peace.
<break time="3500ms"/>
</prosody>

<prosody rate="65%" pitch="-3st" volume="x-soft">
As you rest<break time="800ms"/> in this <emphasis level="moderate">deeply relaxed state</emphasis>,
<break time="2000ms"/>
know that you are <emphasis level="moderate">safe</emphasis>,
<break time="1500ms"/>
<emphasis level="moderate">held</emphasis>,
<break time="1500ms"/>
and connected<break time="700ms"/> to a wellspring of <emphasis level="moderate">inner wisdom</emphasis>.
<break time="2500ms"/>

This calm<break time="800ms"/> is your <emphasis level="moderate">sanctuary</emphasis>
<break time="2000ms"/>
a sacred space<break time="800ms"/> where thoughts settle
<break time="1500ms"/>
like leaves<break time="700ms"/> on <emphasis level="moderate">still water</emphasis>,
<break time="2000ms"/>
where your spirit<break time="800ms"/> feels free to explore
<break time="1500ms"/>
the boundless landscape<break time="800ms"/> of your <emphasis level="moderate">inner world</emphasis>.
<break time="2800ms"/>

With every breath,<break time="800ms"/> you sink <emphasis level="moderate">deeper</emphasis>
<break time="1500ms"/>
into this <emphasis level="moderate">transformative awareness</emphasis>,
<break time="2000ms"/>
ready to uncover insights,
<break time="1500ms"/>
to <emphasis level="moderate">heal</emphasis>,
<break time="1500ms"/>
or to simply <emphasis level="moderate">be</emphasis>.
<break time="2500ms"/>

You are exactly<break time="800ms"/> where you need to be,
<break time="2000ms"/>
and as you breathe,
<break time="1500ms"/>
you prepare to step<break time="800ms"/> even further
<break time="1500ms"/>
into this <emphasis level="moderate">profound</emphasis>,
<break time="1000ms"/>
<emphasis level="moderate">enriching state of mind</emphasis>.
<break time="3500ms"/>
</prosody>

</speak>'''
    ]
    
    return chunks

def synthesize_chunk(client, chunk_num, ssml, output_file):
    """Synthesize with natural but hypnotic settings"""
    
    print(f"\nChunk {chunk_num}/7:")
    print(f"  Size: {len(ssml.encode('utf-8'))} bytes")
    
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-I"
    )
    
    # MORE NATURAL BUT STILL HYPNOTIC
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.85,          # Less extreme = more natural
        pitch=-1.5,                   # Subtle lowering = more human
        volume_gain_db=-1.5,         # Slightly softer but not extreme
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
    print("Natural Hypnotic Opening - Human Yet Trance-Inducing")
    print("="*60)
    print("\nImproved Settings:")
    print("  ✓ More natural speaking rate (0.85 vs 0.72)")
    print("  ✓ Less extreme pitch (-1.5st vs -3st)")
    print("  ✓ Natural volume (-1.5dB vs -3dB)")
    print("  ✓ Varied pacing throughout (60-85%)")
    print("  ✓ Shorter, more natural pauses")
    print("  ✓ Still deeply hypnotic and effective")
    print("="*60)
    
    chunks = create_natural_hypnotic_chunks()
    print(f"\nCreated {len(chunks)} chunks")
    
    client = texttospeech.TextToSpeechClient()
    
    chunk_files = []
    for i, chunk in enumerate(chunks, 1):
        output_file = f"natural_{i:02d}.mp3"
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
    
    result = os.system("ffmpeg -f concat -safe 0 -i filelist.txt -c copy hypnotic_natural.mp3 -y 2>/dev/null")
    
    if result == 0 and os.path.exists('hypnotic_natural.mp3'):
        print("\n" + "="*60)
        print("✓ SUCCESS - NATURAL & HYPNOTIC!")
        print("="*60)
        
        size_mb = os.path.getsize('hypnotic_natural.mp3') / (1024 * 1024)
        print(f"\nCreated: hypnotic_natural.mp3")
        print(f"Size: {size_mb:.2f} MB")
        print(f"Duration: ~10-12 minutes")
        print(f"\nThis version:")
        print(f"  ✓ Sounds more human and conversational")
        print(f"  ✓ Still deeply hypnotic and effective")
        print(f"  ✓ More natural vocal variety")
        print(f"  ✓ Better pacing and rhythm")
        
        for cf in chunk_files:
            os.remove(cf)
        os.remove('filelist.txt')
        
        print("\n" + "="*60)
        print("Compare versions:")
        print("  Reference:  mpv reference_voice.wav")
        print("  Ultra-slow: mpv hypnotic_opening_matched.mp3")
        print("  Natural:    mpv hypnotic_natural.mp3")
        print("="*60)
        
    else:
        print("\n❌ Combination failed")
        print("Chunks saved separately:", chunk_files)

if __name__ == "__main__":
    main()
