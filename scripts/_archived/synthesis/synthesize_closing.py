#!/usr/bin/env python3
from google.cloud import texttospeech
import os
import subprocess

def create_closing_chunks():
    """Create hypnotic closing/emergence - gradual return to awareness"""
    
    chunks = [
        # Chunk 1: Integration and heart light
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="78%" pitch="-2st" volume="soft">
As your journey gently draws to a close,<break time="800ms"/> pause for a moment to collect every fragment of wisdom,<break time="600ms"/> every insight,<break time="500ms"/> and every pulse of transformative energy you've encountered.<break time="1200ms"/> Feel these profound revelations<break time="600ms"/> weaving seamlessly into the very fabric of your being,<break time="800ms"/> merging with every cell,<break time="500ms"/> every thought,<break time="500ms"/> every breath,<break time="800ms"/> as they become an unshakable part<break time="600ms"/> of your ever-expanding consciousness.
<break time="2000ms"/>
</prosody>

<prosody rate="76%" pitch="-2st" volume="soft">
Picture now a radiant,<break time="500ms"/> golden light<break time="600ms"/> blooming softly from the center of your heart—<break time="1000ms"/>a warm,<break time="500ms"/> pulsating glow<break time="600ms"/> that embodies every discovery,<break time="700ms"/> every moment of awareness you've embraced.<break time="1200ms"/> With each slow,<break time="500ms"/> deliberate breath,<break time="800ms"/> this light intensifies,<break time="600ms"/> rippling outward,<break time="700ms"/> flooding through your entire body,<break time="800ms"/> illuminating even the deepest recesses of your soul<break time="700ms"/> with a crystalline understanding<break time="600ms"/> that feels both ancient<break time="500ms"/> and new.
<break time="2000ms"/>
</prosody>

</speak>''',
        
        # Chunk 2: Grounding and integration
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="78%" pitch="-1.5st" volume="soft">
Sense the unyielding weight of the earth beneath you,<break time="800ms"/> a steadfast anchor<break time="600ms"/> grounding your energy.<break time="1000ms"/> As you root into this solid foundation,<break time="700ms"/> trust that every insight,<break time="500ms"/> every transformative shift,<break time="700ms"/> is being etched into your cellular memory<break time="600ms"/> with unbreakable permanence.<break time="1200ms"/> These truths are now woven<break time="600ms"/> into the essence of who you are,<break time="800ms"/> a wellspring of strength and clarity<break time="600ms"/> you can draw upon<break time="500ms"/> in any moment.
<break time="2000ms"/>
</prosody>

<prosody rate="76%" pitch="-2st" volume="soft">
Take a deep,<break time="500ms"/> intentional breath now,<break time="1000ms"/> and as you release it,<break time="700ms"/> notice the alchemy within—<break time="800ms"/>your body feels transformed,<break time="600ms"/> lighter yet deeply anchored,<break time="700ms"/> vibrant with energy<break time="600ms"/> yet wrapped in a profound peace.<break time="1200ms"/> Your mind shines<break time="600ms"/> with a quiet clarity,<break time="700ms"/> your spirit resonating<break time="600ms"/> in perfect harmony<break time="500ms"/> with your truest purpose.
<break time="2000ms"/>
</prosody>

</speak>''',
        
        # Chunk 3: Beginning reawakening
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="80%" pitch="-1.5st" volume="soft">
Begin to gently reawaken<break time="600ms"/> awareness of your physical presence:<break time="1000ms"/>
Feel a subtle,<break time="500ms"/> electric tingle<break time="600ms"/> dancing through your fingers and toes,<break time="800ms"/> a sign of life returning.<break time="1000ms"/>
Notice the steady,<break time="500ms"/> powerful rhythm of your heartbeat,<break time="800ms"/> a drumbeat of resilience and vitality.<break time="1000ms"/>
Sense the gentle rise and fall of your chest,<break time="700ms"/> each breath a bridge<break time="500ms"/> between worlds.<break time="1000ms"/>
Feel the whisper of air around you,<break time="700ms"/> the subtle caress of temperature<break time="600ms"/> on your skin.<break time="1000ms"/>
Tune into the soft symphony<break time="600ms"/> of ambient sounds in your space,<break time="800ms"/> grounding you in the now.
<break time="2000ms"/>
</prosody>

<prosody rate="82%" pitch="-1st" volume="medium-soft">
As you ease back<break time="600ms"/> into full waking consciousness,<break time="800ms"/> know that you carry a sacred treasure within—<break time="1000ms"/>the gift of profound self-knowledge<break time="700ms"/> and unshakable purpose.<break time="1000ms"/> These insights are now enduring stepping stones,<break time="700ms"/> guiding your path of growth and transformation<break time="600ms"/> with every step.
<break time="2000ms"/>
</prosody>

</speak>''',
        
        # Chunk 4: Symbolic treasures and anchoring
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="78%" pitch="-2st" volume="soft">
Hold close the symbolic riches<break time="600ms"/> from your journey:<break time="1200ms"/>
The timeless wisdom<break time="600ms"/> whispered by your future self,<break time="700ms"/> a beacon of possibility.<break time="1000ms"/>
The unshakable strength<break time="600ms"/> that surged through you<break time="600ms"/> in moments of pure revelation.<break time="1000ms"/>
The piercing clarity<break time="600ms"/> unearthed in the stillness of reflection.<break time="1000ms"/>
The boundless power<break time="600ms"/> of your own inner knowing,<break time="700ms"/> a compass that never falters.
<break time="2000ms"/>
</prosody>

<prosody rate="80%" pitch="-1.5st" volume="soft">
Let these memories root deeply within you,<break time="700ms"/> like ancient seeds sown in rich,<break time="600ms"/> fertile soil,<break time="700ms"/> poised to blossom at the perfect moment.<break time="1200ms"/> Each insight will unfurl further,<break time="700ms"/> revealing hidden layers of meaning<break time="600ms"/> as days and weeks<break time="500ms"/> weave into the future.
<break time="2000ms"/>
</prosody>

<prosody rate="78%" pitch="-2st" volume="soft">
Take a quiet moment now<break time="600ms"/> to forge a mental anchor—<break time="1000ms"/>a simple,<break time="500ms"/> personal gesture or touch<break time="700ms"/> to summon this state of connection and awareness<break time="700ms"/> instantly.<break time="1000ms"/> Perhaps a gentle press to your heart center,<break time="800ms"/> or the meeting of thumb and forefinger<break time="700ms"/> in a circle of intent.<break time="1000ms"/> As you craft this anchor,<break time="700ms"/> feel the full,<break time="500ms"/> radiant power of your journey<break time="600ms"/> pouring into it,<break time="700ms"/> a reservoir of strength<break time="600ms"/> at your fingertips.
<break time="2000ms"/>
</prosody>

</speak>''',
        
        # Chunk 5: Physical reawakening
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="85%" pitch="-1st" volume="medium-soft">
Begin to stir life back into your body—<break time="700ms"/>wiggle your fingers and toes,<break time="700ms"/> inviting vitality to flow freely.<break time="1000ms"/> Roll your shoulders with gentle care,<break time="700ms"/> and if it feels right,<break time="600ms"/> reach your arms upward<break time="600ms"/> in a slow,<break time="500ms"/> luxurious stretch.<break time="1000ms"/> Draw in a deep,<break time="500ms"/> life-giving breath,<break time="700ms"/> filling every corner of your lungs<break time="600ms"/> with renewed energy.
<break time="1800ms"/>
</prosody>

<prosody rate="88%" pitch="medium-low" volume="medium">
When you're ready,<break time="600ms"/> allow your eyes to flutter open,<break time="800ms"/> letting them soften<break time="600ms"/> as they adjust to the light.<break time="1000ms"/> Notice how the world appears<break time="600ms"/> through your reborn awareness—<break time="800ms"/>colors pulse with vivid intensity,<break time="700ms"/> shapes carry a sharper edge,<break time="700ms"/> textures seem to hum<break time="600ms"/> with intricate detail.
<break time="1800ms"/>
</prosody>

</speak>''',
        
        # Chunk 6: Post-hypnotic suggestions
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="88%" pitch="medium-low" volume="medium">
As you fully return to your waking state,<break time="700ms"/> carry these unshakable truths in your core:<break time="1200ms"/>
You are infinitely more powerful<break time="600ms"/> than you once believed,<break time="700ms"/> a force of boundless potential.<break time="1000ms"/>
Your purpose shines with crystalline clarity,<break time="700ms"/> a destination within reach.<break time="1000ms"/>
Your path glows<break time="500ms"/> with the light of inner wisdom,<break time="700ms"/> guiding each step.<break time="1000ms"/>
You are cradled by forces<break time="600ms"/> both seen and unseen,<break time="700ms"/> a network of support<break time="600ms"/> beyond imagining.<break time="1000ms"/>
Every forward movement<break time="600ms"/> is a sacred stride<break time="600ms"/> toward your highest good.
<break time="1800ms"/>
</prosody>

<prosody rate="80%" pitch="-1.5st" volume="soft">
Understand that this journey<break time="600ms"/> is not an ending,<break time="700ms"/> but a magnificent beginning.<break time="1000ms"/> Each dawn brings fresh chances<break time="700ms"/> to embody the wisdom you've claimed.<break time="1000ms"/> Your consciousness has stretched<break time="600ms"/> beyond its former boundaries,<break time="700ms"/> and this expansion is eternal,<break time="700ms"/> unyielding,<break time="600ms"/> a permanent awakening.
<break time="2000ms"/>
</prosody>

</speak>''',
        
        # Chunk 7: Final integration and return
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="85%" pitch="-1st" volume="medium-soft">
Take one final,<break time="500ms"/> grounding breath,<break time="1000ms"/> and as you exhale,<break time="700ms"/> let a gentle smile curve your lips,<break time="800ms"/> knowing you are irrevocably changed<break time="700ms"/> by this sacred experience.<break time="1000ms"/> You have touched the deepest layers of your being,<break time="800ms"/> igniting dormant potential<break time="600ms"/> that now burns brightly within.
<break time="1800ms"/>
</prosody>

<prosody rate="80%" pitch="-1.5st" volume="soft">
The portal to this wisdom<break time="600ms"/> remains ever-open,<break time="800ms"/> a sanctuary you can revisit at will.<break time="1000ms"/> Trust that your unconscious mind<break time="600ms"/> continues its silent work,<break time="700ms"/> weaving these experiences into your life,<break time="800ms"/> delivering fresh insights and revelations<break time="700ms"/> precisely when you need them most.
<break time="2000ms"/>
</prosody>

<prosody rate="90%" pitch="medium-low" volume="medium">
As you step back into your day,<break time="700ms"/> feel the subtle shift within—<break time="800ms"/>more centered,<break time="500ms"/> more attuned,<break time="500ms"/> more aligned<break time="600ms"/> with the essence of your purpose.<break time="1000ms"/> This journey of transformation<break time="600ms"/> unfurls with every breath,<break time="600ms"/> every step,<break time="500ms"/> every fleeting moment.
<break time="1800ms"/>
</prosody>

<prosody rate="82%" pitch="-1st" volume="soft">
Know that you can return<break time="600ms"/> to this expansive state<break time="600ms"/> whenever you desire,<break time="800ms"/> peeling back new layers of wisdom and understanding<break time="700ms"/> with each visit.<break time="1000ms"/> Your path is bathed in light,<break time="700ms"/> your purpose unwavering,<break time="700ms"/> your potential an endless horizon.
<break time="2000ms"/>
</prosody>

</speak>''',
        
        # Chunk 8: Full return and call to action
        '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="92%" pitch="medium" volume="medium">
Now,<break time="500ms"/> fully present,<break time="500ms"/> vibrantly aware,<break time="700ms"/> you stand ready to engage with the world<break time="700ms"/> from this elevated state of being.<break time="1000ms"/> Carry this radiant light within you<break time="700ms"/> as you move forward,<break time="700ms"/> sharing the quiet power of your transformed energy<break time="600ms"/> with everyone you meet.
<break time="1800ms"/>
</prosody>

<prosody rate="95%" pitch="medium" volume="medium">
Welcome back<break time="600ms"/> to full waking consciousness,<break time="800ms"/> bearing the seeds of transformation<break time="700ms"/> that will continue to sprout,<break time="600ms"/> grow,<break time="500ms"/> and flourish<break time="600ms"/> in the days ahead.
<break time="2000ms"/>
</prosody>

<prosody rate="100%" pitch="medium" volume="medium">
If this script has resonated with you,<break time="600ms"/> I invite you to like and subscribe to my channel.<break time="800ms"/> For even more immersive dreamweaving adventures<break time="700ms"/> that I can't share on this platform,<break time="700ms"/> be sure to visit the link in the video description.
<break time="1500ms"/>
</prosody>

</speak>'''
    ]
    
    return chunks

def synthesize_chunk(client, chunk_num, ssml, output_file):
    """Synthesize with gradual awakening settings"""
    
    print(f"\nChunk {chunk_num}/8:")
    print(f"  Size: {len(ssml.encode('utf-8'))} bytes")
    
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-I"
    )
    
    # GRADUAL EMERGENCE - starts slow/soft, ends normal
    # Base settings (will be modified by SSML prosody)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.88,          # Natural base rate
        pitch=-1.0,                   # Subtle lowering
        volume_gain_db=-1.0,         # Slightly soft
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
    print("Hypnotic Closing - Gradual Emergence")
    print("="*60)
    print("\nProgressive awakening:")
    print("  ✓ Starts slow & soft (integration)")
    print("  ✓ Gradually speeds up (reawakening)")
    print("  ✓ Ends at normal pace (full return)")
    print("  ✓ Natural vocal progression")
    print("  ✓ Post-hypnotic suggestions embedded")
    print("="*60)
    
    chunks = create_closing_chunks()
    print(f"\nCreated {len(chunks)} chunks")
    
    client = texttospeech.TextToSpeechClient()
    
    chunk_files = []
    for i, chunk in enumerate(chunks, 1):
        output_file = f"closing_{i:02d}.mp3"
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
        ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'filelist.txt', '-c', 'copy', 'hypnotic_closing.mp3', '-y'],
        capture_output=True
    )

    if result.returncode == 0 and os.path.exists('hypnotic_closing.mp3'):
        print("\n" + "="*60)
        print("✓ SUCCESS!")
        print("="*60)
        
        size_mb = os.path.getsize('hypnotic_closing.mp3') / (1024 * 1024)
        print(f"\nCreated: hypnotic_closing.mp3")
        print(f"Size: {size_mb:.2f} MB")
        print(f"Duration: ~8-10 minutes")
        print(f"\nThis closing:")
        print(f"  ✓ Integrates insights and wisdom")
        print(f"  ✓ Creates mental anchor for future use")
        print(f"  ✓ Gradually returns to full awareness")
        print(f"  ✓ Installs post-hypnotic suggestions")
        print(f"  ✓ Ends with clear, energized state")
        print(f"  ✓ Includes channel call-to-action")
        
        for cf in chunk_files:
            os.remove(cf)
        os.remove('filelist.txt')
        
        print("\n" + "="*60)
        print("Complete session structure:")
        print("  1. hypnosis_pretalk.mp3      (~3-4 min)")
        print("  2. hypnotic_natural.mp3       (~10-12 min)")
        print("  3. [Your main content here]")
        print("  4. hypnotic_closing.mp3       (~8-10 min)")
        print("\nPlay: mpv hypnotic_closing.mp3")
        print("="*60)
        
    else:
        print("\n❌ Combination failed")
        print("Chunks saved separately:", chunk_files)

if __name__ == "__main__":
    main()
