#!/usr/bin/env python3
"""
AI Clone Pretalk Synthesis - Refactored Version

Natural conversational introduction for the AI Clone persona.
Uses BaseSynthesizer to eliminate code duplication.

Original: ~220 lines
Refactored: ~120 lines (mostly SSML content)
"""

from base_synthesizer import BaseSynthesizer
from typing import List


class AIPretalkSynthesizer(BaseSynthesizer):
    """Synthesize natural AI clone introduction (non-hypnotic)."""

    name = "AI Clone Pretalk - Natural Conversational Style"
    output_filename = "ai_pretalk_natural.mp3"
    voice_name = "en-US-Neural2-I"
    speaking_rate = 1.0
    pitch = 0.0
    volume_gain_db = 0.0
    description = "Natural, conversational, friendly with AI Clone branding"
    duration_estimate = "~3-4 minutes"

    def get_chunks(self) -> List[str]:
        """Return SSML chunks for the AI pretalk."""
        return [
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

    def get_success_message(self) -> List[str]:
        """Return custom success message."""
        return [
            "Sounds natural and conversational",
            "No hypnotic language patterns",
            "Friendly and informative",
            "Clear explanations",
            "Professional YouTube-style intro",
            "Maintains AI Clone branding"
        ]


if __name__ == "__main__":
    synthesizer = AIPretalkSynthesizer()
    synthesizer.run()
