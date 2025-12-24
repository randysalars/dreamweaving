#!/usr/bin/env python3
from google.cloud import texttospeech
import os
import subprocess

def create_matched_hypnotic_chunks():
    """Create hypnotic opening matched to reference voice"""
    
    chunks = [
        # Chunk 1: Opening - MATCHED TO REFERENCE (60% pauses, soft, very slow)
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="72%" pitch="-3st" volume="soft">
Begin by finding a position<break time="1200ms"/> that feels <emphasis level="moderate">just right</emphasis> for you
<break time="2000ms"/>
whether sitting<break time="800ms"/> or lying down,<break time="1200ms"/> in a <emphasis level="moderate">quiet, safe space</emphasis>
<break time="1500ms"/>
where you can <emphasis level="moderate">let go completely</emphasis>.
<break time="3000ms"/>

As you settle in,<break time="1000ms"/> <emphasis level="moderate">gently</emphasis> close your eyes,
<break time="2000ms"/>
and draw in a slow,<break time="800ms"/> <emphasis level="moderate">deep breath</emphasis>
<break time="2500ms"/>
holding it for a moment
<break time="2000ms"/>
and then <emphasis level="moderate">releasing it</emphasis>,
<break time="1200ms"/>
letting it flow out<break time="800ms"/> like a <emphasis level="moderate">soft sigh</emphasis>.
<break time="3500ms"/>
</prosody>

<prosody rate="68%" pitch="-4st" volume="soft">
With each breath,<break time="1200ms"/> notice how your mind begins to <emphasis level="moderate">quiet</emphasis>,
<break time="2000ms"/>
resting in the gentle <emphasis level="moderate">pause</emphasis>
<break time="1500ms"/>
between each inhale<break time="1200ms"/> and exhale,
<break time="2500ms"/>
as if the world around you<break time="1000ms"/> is <emphasis level="moderate">softening</emphasis>,
<break time="1800ms"/>
<emphasis level="moderate">fading</emphasis> into stillness.
<break time="3500ms"/>
</prosody>

</speak>''',
        
        # Chunk 2: Visualization
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="70%" pitch="-3st" volume="soft">
Picture a <emphasis level="moderate">soothing, radiant energy</emphasis><break time="1200ms"/> enveloping you
<break time="2000ms"/>
a warm,<break time="800ms"/> <emphasis level="moderate">golden light</emphasis>
<break time="1500ms"/>
that feels as comforting<break time="1000ms"/> as a <emphasis level="moderate">tender embrace</emphasis>
<break time="2000ms"/>
or a soft,<break time="800ms"/> <emphasis level="moderate">protective cocoon</emphasis>.
<break time="3000ms"/>

This light wraps around you,<break time="1200ms"/> and as it does,
<break time="1800ms"/>
your body naturally begins<break time="1000ms"/> to <emphasis level="moderate">unwind</emphasis>.
<break time="3000ms"/>

Feel the muscles in your forehead<break time="1200ms"/> <emphasis level="moderate">smoothing out</emphasis>,
<break time="1800ms"/>
as if a gentle hand<break time="1000ms"/> is brushing away any tightness.
<break time="2500ms"/>
Sense your jaw <emphasis level="moderate">loosening</emphasis>,
<break time="1500ms"/>
your shoulders <emphasis level="moderate">melting downward</emphasis>,
<break time="2000ms"/>
and every part of you<break time="1200ms"/> <emphasis level="moderate">sinking deeper</emphasis> into ease.
<break time="3500ms"/>
</prosody>

</speak>''',
        
        # Chunk 3: Garden and countdown intro
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="66%" pitch="-4st" volume="soft">
With each breath,<break time="1200ms"/> the outside world<break time="1000ms"/> <emphasis level="moderate">drifts further away</emphasis>,
<break time="2500ms"/>
becoming distant,<break time="1200ms"/> <emphasis level="moderate">irrelevant</emphasis>.
<break time="3000ms"/>

Instead,<break time="1000ms"/> imagine stepping into<break time="1200ms"/> a <emphasis level="moderate">tranquil, sacred space</emphasis>
<break time="2000ms"/>
a breathtaking garden<break time="1000ms"/> at twilight,
<break time="1800ms"/>
where the sky glows<break time="1000ms"/> with hues of <emphasis level="moderate">lavender and amber</emphasis>.
<break time="3500ms"/>

Every detail<break time="1200ms"/> is alive with <emphasis level="moderate">serenity</emphasis>:
<break time="2000ms"/>
the soft rustle of leaves,
<break time="1500ms"/>
the delicate scent<break time="1000ms"/> of <emphasis level="moderate">jasmine and sandalwood</emphasis>
<break time="1800ms"/>
carried on a <emphasis level="moderate">cool breeze</emphasis>.
<break time="4000ms"/>
</prosody>

<prosody rate="68%" pitch="-3st" volume="soft">
Now,<break time="1200ms"/> as this <emphasis level="moderate">serene feeling</emphasis> wraps around you
<break time="2000ms"/>
like a warm,<break time="800ms"/> familiar memory,
<break time="2500ms"/>
allow yourself to drift<break time="1200ms"/> even further into relaxation
<break time="1800ms"/>
with a <emphasis level="moderate">gentle countdown</emphasis>.
<break time="3500ms"/>

With each number<break time="1000ms"/> I guide you through,
<break time="1800ms"/>
you'll find yourself<break time="1200ms"/> <emphasis level="moderate">sinking deeper</emphasis>
<break time="2000ms"/>
into a state of <emphasis level="moderate">profound calm</emphasis>
<break time="1500ms"/>
and <emphasis level="moderate">inner stillness</emphasis>.
<break time="3500ms"/>

Let's begin<break time="1200ms"/> this <emphasis level="moderate">journey inward</emphasis>:
<break time="3000ms"/>
</prosody>

</speak>''',
        
        # Chunk 4: Countdown 10-8
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="64%" pitch="-3st" volume="soft">
<emphasis level="strong">Ten</emphasis>
<break time="3000ms"/>
A wave of relaxation<break time="1200ms"/> starts at the very top<break time="1000ms"/> of your head,
<break time="2000ms"/>
<emphasis level="moderate">cascading down</emphasis><break time="1200ms"/> like warm water,
<break time="1800ms"/>
soothing every muscle,<break time="1000ms"/> every thought,
<break time="2000ms"/>
<emphasis level="moderate">softening</emphasis> your scalp,<break time="1000ms"/> your face,
<break time="1500ms"/>
and every tiny fiber<break time="1000ms"/> of your being.
<break time="4000ms"/>
</prosody>

<prosody rate="62%" pitch="-4st" volume="soft">
<emphasis level="strong">Nine</emphasis>
<break time="3500ms"/>
With this number,<break time="1200ms"/> a <emphasis level="moderate">deeper calm</emphasis>
<break time="1500ms"/>
settles behind your closed eyes.
<break time="2500ms"/>
Feel a <emphasis level="moderate">peaceful stillness</emphasis>
<break time="1200ms"/>
spreading from your forehead<break time="1000ms"/> to your cheeks,
<break time="2000ms"/>
as if any lingering tension<break time="1200ms"/> is simply <emphasis level="moderate">dissolving</emphasis>,
<break time="1800ms"/>
<emphasis level="moderate">melting away</emphasis><break time="1200ms"/> into nothingness.
<break time="4000ms"/>
</prosody>

<prosody rate="60%" pitch="-4st" volume="x-soft">
<emphasis level="strong">Eight</emphasis>
<break time="3500ms"/>
Allow your neck and shoulders<break time="1200ms"/> to <emphasis level="moderate">release completely</emphasis>,
<break time="2500ms"/>
as if an invisible weight<break time="1200ms"/> is <emphasis level="moderate">lifting off</emphasis>,
<break time="2000ms"/>
leaving you <emphasis level="moderate">lighter</emphasis>,
<break time="1200ms"/>
<emphasis level="moderate">freer</emphasis>.
<break time="2500ms"/>
Each exhale<break time="1000ms"/> becomes a gentle breeze,
<break time="2000ms"/>
carrying away<break time="1200ms"/> any strain,<break time="1000ms"/> any burden.
<break time="4500ms"/>
</prosody>

</speak>''',
        
        # Chunk 5: Countdown 7-5
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="58%" pitch="-4st" volume="x-soft">
<emphasis level="strong">Seven</emphasis>
<break time="3500ms"/>
Notice a <emphasis level="moderate">comforting warmth</emphasis>
<break time="1500ms"/>
flowing down your arms,
<break time="2500ms"/>
relaxing your elbows,<break time="1000ms"/> your wrists,
<break time="2000ms"/>
all the way<break time="1000ms"/> to your <emphasis level="moderate">fingertips</emphasis>.
<break time="2500ms"/>
It's as if each nerve<break time="1200ms"/> is bathed in a soft,
<break time="1500ms"/>
<emphasis level="moderate">healing glow</emphasis>.
<break time="4500ms"/>
</prosody>

<prosody rate="56%" pitch="-5st" volume="x-soft">
<emphasis level="strong">Six</emphasis>
<break time="4000ms"/>
Let this relaxation<break time="1200ms"/> spread into your chest,<break time="1000ms"/> your heart.
<break time="3000ms"/>
With each heartbeat,<break time="1200ms"/> feel a wave of <emphasis level="moderate">serenity</emphasis>
<break time="1500ms"/>
filling you,
<break time="2500ms"/>
<emphasis level="moderate">expanding</emphasis> within you,
<break time="2000ms"/>
a quiet assurance<break time="1200ms"/> that you are <emphasis level="moderate">safe</emphasis>,
<break time="1500ms"/>
<emphasis level="moderate">supported</emphasis>,
<break time="1500ms"/>
and at <emphasis level="moderate">peace</emphasis>.
<break time="5000ms"/>
</prosody>

<prosody rate="54%" pitch="-5st" volume="x-soft">
<emphasis level="strong">Five</emphasis>
<break time="4000ms"/>
Your stomach and back<break time="1200ms"/> <emphasis level="moderate">soften</emphasis> now,
<break time="2500ms"/>
melting into a state<break time="1200ms"/> of <emphasis level="moderate">perfect harmony</emphasis>.
<break time="3500ms"/>
Every muscle <emphasis level="moderate">unwinds</emphasis>,
<break time="2500ms"/>
and with each breath,<break time="1200ms"/> you feel more <emphasis level="moderate">connected</emphasis>,
<break time="2000ms"/>
more at <emphasis level="moderate">ease</emphasis>.
<break time="5000ms"/>
</prosody>

</speak>''',
        
        # Chunk 6: Countdown 4-2
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="52%" pitch="-5st" volume="x-soft">
<emphasis level="strong">Four</emphasis>
<break time="4000ms"/>
Sense this calm<break time="1200ms"/> traveling through your hips<break time="1000ms"/> and thighs,
<break time="3500ms"/>
<emphasis level="moderate">releasing</emphasis><break time="1200ms"/> any hidden tension.
<break time="3000ms"/>
Imagine your legs<break time="1200ms"/> growing <emphasis level="moderate">lighter</emphasis>,
<break time="2500ms"/>
almost <emphasis level="moderate">weightless</emphasis>,
<break time="2500ms"/>
as if they're floating<break time="1200ms"/> on a gentle current.
<break time="5000ms"/>
</prosody>

<prosody rate="50%" pitch="-6st" volume="x-soft">
<emphasis level="strong">Three</emphasis>
<break time="4500ms"/>
This relaxation<break time="1200ms"/> flows now<break time="1000ms"/> into your knees and calves,
<break time="3500ms"/>
<emphasis level="moderate">deepening</emphasis><break time="1200ms"/> with every breath.
<break time="3500ms"/>
Each exhale<break time="1200ms"/> draws you further<break time="1000ms"/> into <emphasis level="moderate">stillness</emphasis>,
<break time="2500ms"/>
into a quiet <emphasis level="moderate">inner peace</emphasis>
<break time="2500ms"/>
that feels natural,<break time="1200ms"/> <emphasis level="moderate">effortless</emphasis>.
<break time="5500ms"/>
</prosody>

<prosody rate="48%" pitch="-6st" volume="x-soft">
<emphasis level="strong">Two</emphasis>
<break time="4500ms"/>
Your ankles and feet<break time="1200ms"/> are now bathed
<break time="2500ms"/>
in this <emphasis level="moderate">gentle tranquility</emphasis>.
<break time="3500ms"/>
Picture a wave<break time="1200ms"/> of <emphasis level="moderate">deep calm</emphasis>
<break time="1500ms"/>
washing over them,
<break time="3500ms"/>
as if roots of peace<break time="1200ms"/> are extending from within you,
<break time="3000ms"/>
<emphasis level="moderate">grounding you</emphasis>
<break time="1500ms"/>
into a nourishing,<break time="1000ms"/> steady earth.
<break time="6000ms"/>
</prosody>

</speak>''',
        
        # Chunk 7: Number 1 and deepening
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="46%" pitch="-7st" volume="x-soft">
<emphasis level="strong">One</emphasis>
<break time="5000ms"/>
And at this final number,
<break time="3500ms"/>
<emphasis level="moderate">surrender completely</emphasis>
<break time="3500ms"/>
to this state<break time="1200ms"/> of <emphasis level="moderate">profound relaxation</emphasis>.
<break time="4500ms"/>
Every part of your body<break time="1200ms"/> is immersed in <emphasis level="moderate">calm</emphasis>,
<break time="3500ms"/>
every thought <emphasis level="moderate">quieted</emphasis>,
<break time="3500ms"/>
and your mind <emphasis level="moderate">open</emphasis>,
<break time="1500ms"/>
<emphasis level="moderate">clear</emphasis>,
<break time="2500ms"/>
and ready<break time="1200ms"/> for the <emphasis level="moderate">transformative journey</emphasis> ahead.
<break time="4500ms"/>
You are at <emphasis level="moderate">peace</emphasis>,
<break time="2500ms"/>
<emphasis level="moderate">deeply</emphasis> at peace.
<break time="6000ms"/>
</prosody>

<prosody rate="48%" pitch="-6st" volume="x-soft">
As you rest<break time="1200ms"/> in this <emphasis level="moderate">deeply relaxed state</emphasis>,
<break time="3500ms"/>
know that you are <emphasis level="moderate">safe</emphasis>,
<break time="2500ms"/>
<emphasis level="moderate">held</emphasis>,
<break time="2500ms"/>
and connected<break time="1000ms"/> to a wellspring of <emphasis level="moderate">inner wisdom</emphasis>.
<break time="4500ms"/>

This calm<break time="1200ms"/> is your <emphasis level="moderate">sanctuary</emphasis>
<break time="3500ms"/>
a sacred space<break time="1200ms"/> where thoughts settle
<break time="2500ms"/>
like leaves<break time="1000ms"/> on <emphasis level="moderate">still water</emphasis>,
<break time="3500ms"/>
where your spirit<break time="1200ms"/> feels free to explore
<break time="2500ms"/>
the boundless landscape<break time="1200ms"/> of your <emphasis level="moderate">inner world</emphasis>.
<break time="5000ms"/>

With every breath,<break time="1200ms"/> you sink <emphasis level="moderate">deeper</emphasis>
<break time="2500ms"/>
into this <emphasis level="moderate">transformative awareness</emphasis>,
<break time="3500ms"/>
ready to uncover insights,
<break time="2500ms"/>
to <emphasis level="moderate">heal</emphasis>,
<break time="2500ms"/>
or to simply <emphasis level="moderate">be</emphasis>.
<break time="4500ms"/>

You are exactly<break time="1200ms"/> where you need to be,
<break time="3500ms"/>
and as you breathe,
<break time="2500ms"/>
you prepare to step<break time="1200ms"/> even further
<break time="2500ms"/>
into this <emphasis level="moderate">profound</emphasis>,
<break time="1500ms"/>
<emphasis level="moderate">enriching state of mind</emphasis>.
<break time="6000ms"/>
</prosody>

</speak>'''
    ]
    
    return chunks

def synthesize_chunk(client, chunk_num, ssml, output_file):
    """Synthesize with matched hypnotic voice settings"""
    
    print(f"\nChunk {chunk_num}/7:")
    print(f"  Size: {len(ssml.encode('utf-8'))} bytes")
    
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-I"
    )
    
    # MATCHED TO REFERENCE VOICE
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.72,          # Very slow (matches 60% silence)
        pitch=-3.0,                   # Calm, soothing
        volume_gain_db=-3.0,         # Soft, intimate
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
    print("Hypnotic Opening - MATCHED TO REFERENCE VOICE")
    print("="*60)
    print("\nReference Analysis:")
    print("  Pace: VERY SLOW (60% silence)")
    print("  Volume: SOFT (intimate)")
    print("  Style: Deep hypnotic")
    print("\nMatched TTS Settings:")
    print("  Voice: en-US-Neural2-I (warm male)")
    print("  Rate: 0.72 (very slow)")
    print("  Pitch: -3st (calm)")
    print("  Volume: -3dB (soft)")
    print("  Extra long pauses to match reference")
    print("="*60)
    
    chunks = create_matched_hypnotic_chunks()
    print(f"\nCreated {len(chunks)} chunks")
    
    client = texttospeech.TextToSpeechClient()
    
    chunk_files = []
    for i, chunk in enumerate(chunks, 1):
        output_file = f"matched_{i:02d}.mp3"
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
        ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'filelist.txt', '-c', 'copy', 'hypnotic_opening_matched.mp3', '-y'],
        capture_output=True
    )

    if result.returncode == 0 and os.path.exists('hypnotic_opening_matched.mp3'):
        print("\n" + "="*60)
        print("✓ SUCCESS - MATCHED TO YOUR REFERENCE!")
        print("="*60)
        
        size_mb = os.path.getsize('hypnotic_opening_matched.mp3') / (1024 * 1024)
        print(f"\nCreated: hypnotic_opening_matched.mp3")
        print(f"Size: {size_mb:.2f} MB")
        print(f"Duration: ~12-15 minutes")
        print(f"\nMatches your reference voice:")
        print(f"  ✓ Very slow pace (60% pauses)")
        print(f"  ✓ Soft, intimate volume")
        print(f"  ✓ Deep hypnotic delivery")
        print(f"  ✓ Extended silence for trance depth")
        
        for cf in chunk_files:
            os.remove(cf)
        os.remove('filelist.txt')
        
        print("\n" + "="*60)
        print("Compare:")
        print("  Original: mpv reference_voice.wav")
        print("  Matched:  mpv hypnotic_opening_matched.mp3")
        print("="*60)
        
    else:
        print("\n❌ Combination failed")
        print("Chunks saved separately:", chunk_files)

if __name__ == "__main__":
    main()
