#!/usr/bin/env python3
"""
Hypnosis Pretalk Synthesis - Refactored Version

This is the refactored version using BaseSynthesizer.
Compare with the original synthesize_pretalk.py to see
how much code duplication is eliminated.

Original: ~175 lines
Refactored: ~90 lines (mostly SSML content)
"""

from base_synthesizer import BaseSynthesizer
from typing import List


class PretalkSynthesizer(BaseSynthesizer):
    """Synthesize the hypnosis pretalk/introduction."""

    name = "Hypnosis Pretalk - Conversational Style"
    output_filename = "hypnosis_pretalk.mp3"
    voice_name = "en-US-Neural2-I"
    description = "Conversational, engaging, friendly"
    duration_estimate = "~3-4 minutes"

    def get_chunks(self) -> List[str]:
        """Return SSML chunks for the pretalk."""
        return [
            # Chunk 1: Introduction and explanation
            '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="105%" pitch="+1st" volume="medium">
Welcome to this special Dreamweaving and Pathworking session.<break time="400ms"/> My name is Randy Sayl-ers, and I'm so glad to have you here with me today.<break time="500ms"/> I'll be your guide on this transformative journey into the depths of your mind and spirit.<break time="400ms"/> You're ready to explore something meaningful today, aren't you?<break time="600ms"/>

In today's session, we'll be connecting with your inner self, helping you find clarity, inspiration, or simply a moment of deep relaxation.<break time="400ms"/> Whatever your intention, this experience is designed just for you.
</prosody>

<break time="800ms"/>

<prosody rate="102%" pitch="medium">
Before we begin, let me assure you that hypnosis is a completely natural process.<break time="400ms"/> It's simply a state of deep relaxation and focused awareness—very similar to what you might feel when you're absorbed in a great book or lost in a daydream.<break time="400ms"/> You've experienced moments like that before, haven't you?<break time="600ms"/>

You'll remain fully aware and in control the entire time.<break time="400ms"/> You can't get "stuck" in hypnosis, and your subconscious mind will only accept suggestions that align with your values and goals.<break time="400ms"/> You're always in charge.
</prosody>

<break time="800ms"/>

<prosody rate="104%" pitch="+0.5st" volume="medium">
Now, let's talk about Pathworking and Dreamweaving, the heart of today's journey.<break time="500ms"/>

Pathworking is a powerful mental journey where we use guided imagery to walk along a symbolic path.<break time="400ms"/> Each step evokes inner wisdom, healing, and insight, helping you connect deeply with your mind and spirit.<break time="400ms"/> It's like traveling through a dreamscape tailored to unlock your potential.<break time="600ms"/>

Dreamweaving builds on this by encouraging you to blend imagination and intuition—crafting vivid experiences that merge creativity and transformation.<break time="400ms"/> Through this, you'll weave a new vision for your future or resolve challenges from the past.<break time="400ms"/> That sounds like a journey worth taking, doesn't it?
</prosody>

</speak>''',

            # Chunk 2: Instructions and closing
            '''<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<prosody rate="100%" pitch="medium">
To make the most of this session, it's very important to use headphones.<break time="500ms"/> I've designed this experience with stereo audio, meaning different sounds and suggestions are fed into each ear to guide your mind into a deeply relaxed state.<break time="600ms"/>

You'll also hear subtle binaural beats throughout the session.<break time="400ms"/> These are special tones created by playing slightly different frequencies in each ear, and your brain processes the difference as a kind of "internal rhythm."<break time="500ms"/> You don't need to do anything other than listen—they will naturally guide your brain to a state of deep relaxation.<break time="400ms"/> You're ready to let that happen, right?
</prosody>

<break time="800ms"/>

<prosody rate="102%" pitch="medium" volume="medium">
To prepare for this experience, find a quiet, comfortable space where you won't be disturbed.<break time="400ms"/> Feel free to sit or lie down—whatever makes you feel most at ease.<break time="500ms"/>

Once you're settled, simply close your eyes, let my voice guide you, and allow the experience to unfold naturally.<break time="600ms"/>

Remember, you're always in control during hypnosis.<break time="400ms"/> At any moment, if needed, you can simply open your eyes and return to full awareness.<break time="400ms"/> There's no right or wrong way to experience it—just allow yourself to participate in a way that feels natural.<break time="600ms"/>

If this is your first time, take things at your own pace.<break time="400ms"/> And know that every time you practice, it gets easier and more powerful.<break time="500ms"/> In fact, the more you listen to my videos and my voice, the deeper you'll go each time.<break time="400ms"/> Each session builds on the last, guiding you into even deeper states of relaxation and discovery.<break time="400ms"/> Practice makes perfect.<break time="400ms"/> You'd like to experience that deepening effect, wouldn't you?
</prosody>

<break time="800ms"/>

<prosody rate="105%" pitch="+1st" volume="medium">
Today's journey is about walking a tranquil path to uncover the insights and inspiration waiting within you.<break time="500ms"/> I'll guide you every step of the way as we explore this inner landscape together.<break time="600ms"/>

So, take a moment to relax your body<break time="300ms"/>… notice your breath<break time="300ms"/>… and allow yourself to become curious about what you might discover in this session.<break time="600ms"/> When you're ready, we'll begin.
</prosody>

<break time="1s"/>

<prosody rate="108%" pitch="+1.5st" volume="medium">
Lastly, if you enjoy this content, feel free to like, share, or subscribe to my channel.<break time="400ms"/> It helps support future videos and builds a community of explorers like you who value transformation and growth.
</prosody>

</speak>'''
        ]


if __name__ == "__main__":
    synthesizer = PretalkSynthesizer()
    synthesizer.run()
