#!/usr/bin/env python3
"""
Holistic Wellness Protocol - High-Fidelity Audio Session Generator

Generates 4 guided meditation/breathing sessions (15-20 minutes each):
1. Box Breathing Foundation (16 min) - Stress relief, nervous system balance
2. 4-7-8 Sleep Induction (18 min) - Deep relaxation for sleep
3. Body Scan Meditation (20 min) - Full body awareness and release
4. Energizing Breath Work (15 min) - Morning energy boost

Uses Edge TTS for high-quality, natural voice synthesis.
"""

import asyncio
import os
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent / "output" / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Use a calm, measured male voice for meditation content
VOICE = "en-US-GuyNeural"  # Natural male voice, good for meditation

# Session scripts with therapeutic pacing (... indicates natural pauses)
SESSIONS = {
    "01_box_breathing_foundation": {
        "title": "Box Breathing Foundation",
        "duration_estimate": "16 minutes",
        "script": """
Welcome to the Box Breathing Foundation session. This ancient technique, used by Navy SEALs and high-performance athletes, will help you find calm, focus, and balance in your nervous system.

Find a comfortable position. You can sit in a chair with your feet flat on the floor, or sit cross-legged on a cushion. Allow your spine to be straight but not rigid. Rest your hands gently on your thighs.

Close your eyes if that feels comfortable. If not, soften your gaze toward the floor about six feet in front of you.

Take a moment to arrive fully in this space. Notice the weight of your body being supported. Feel the surface beneath you. You are safe. You are present. There is nothing you need to do right now except breathe.

Let's begin with three natural breaths to settle in. Breathe in through your nose... and exhale fully through your mouth. Again, breathe in... and let it go. One more time, a deep breath in... and release completely.

Now I will guide you through the box breathing pattern. We breathe in for four counts, hold for four counts, exhale for four counts, and hold the exhale for four counts. This creates a box, or square, of breath.

Let's begin our first cycle together.

Breathe in slowly. One. Two. Three. Four.

Hold gently. One. Two. Three. Four.

Exhale softly. One. Two. Three. Four.

Hold empty. One. Two. Three. Four.

Beautiful. Let's continue.

Breathe in. One. Two. Three. Four.

Hold. One. Two. Three. Four.

Exhale. One. Two. Three. Four.

Hold. One. Two. Three. Four.

Notice how each breath becomes more natural. Your body remembers this rhythm. We are moving from the sympathetic nervous system, the fight or flight response, into the parasympathetic state, where healing and restoration happen.

Breathe in. One. Two. Three. Four.

Hold. One. Two. Three. Four.

Exhale. One. Two. Three. Four.

Hold. One. Two. Three. Four.

Continue at your own pace now. I will guide you with gentle prompts.

Inhale...

Hold...

Exhale...

Hold...

Inhale...

Hold...

Exhale...

Hold...

You're doing wonderfully. Notice how your shoulders may have dropped away from your ears. Your jaw may have relaxed. Each cycle deepens your calm.

Inhale...

Hold...

Exhale...

Hold...

Now let's deepen the practice. We'll extend to five-count cycles. The longer duration amplifies the calming effect.

Breathe in. One. Two. Three. Four. Five.

Hold gently. One. Two. Three. Four. Five.

Exhale slowly. One. Two. Three. Four. Five.

Hold empty. One. Two. Three. Four. Five.

Beautiful.

Breathe in. One. Two. Three. Four. Five.

Hold. One. Two. Three. Four. Five.

Exhale. One. Two. Three. Four. Five.

Hold. One. Two. Three. Four. Five.

Continue with five-count cycles.

Inhale...

Hold...

Exhale...

Hold...

Inhale...

Hold...

Exhale...

Hold...

Inhale...

Hold...

Exhale...

Hold...

Inhale...

Hold...

Exhale...

Hold...

Inhale...

Hold...

Exhale...

Hold...

Now for our final sequence, if you feel ready, let's try six-count cycles. This is the gold standard for deep nervous system regulation.

Breathe in slowly. One. Two. Three. Four. Five. Six.

Hold with ease. One. Two. Three. Four. Five. Six.

Exhale completely. One. Two. Three. Four. Five. Six.

Hold peacefully. One. Two. Three. Four. Five. Six.

One more cycle at six counts.

Breathe in. One. Two. Three. Four. Five. Six.

Hold. One. Two. Three. Four. Five. Six.

Exhale. One. Two. Three. Four. Five. Six.

Hold. One. Two. Three. Four. Five. Six.

Now let your breathing return to its natural rhythm. There's nothing to control. Simply observe. Feel the subtle rise and fall of your chest. Notice the gentle expansion and contraction of your belly.

You have activated your parasympathetic nervous system. You have told your body that you are safe. Stress hormones are lowering. Your heart rate has settled. Your blood pressure has normalized.

This is your natural state. Calm. Clear. Present.

Take a moment to appreciate what you've done for yourself. This investment in your wellbeing ripples out to everyone you interact with today.

When you're ready, gently wiggle your fingers and toes. Roll your shoulders back. Take one more deep breath in through your nose... and exhale fully through your mouth.

Slowly open your eyes, returning to the room with clarity and calm.

Thank you for practicing with me today. You can return to box breathing anytime you need to reset. Just four breaths can shift your state. You now have this tool for life.

Carry this peace with you.
        """
    },
    
    "02_478_sleep_induction": {
        "title": "4-7-8 Sleep Induction",
        "duration_estimate": "18 minutes",
        "script": """
Welcome to the 4-7-8 Sleep Induction session. This breathing technique, developed by Dr. Andrew Weil and rooted in ancient yogic practice, is sometimes called the natural tranquilizer for the nervous system. It will guide you gently toward deep, restorative sleep.

Find a comfortable position in your bed. You may lie on your back with a pillow supporting your head, or on your side if that feels more natural. Allow your body to sink into the mattress. Feel yourself being held by the surface beneath you.

Close your eyes. Let the darkness behind your eyelids become a welcoming space. This is your time. This is your rest. There is nothing left to do today. Everything that needed attention can wait until morning.

Let's begin with a body release. Starting at the top of your head, allow any tension to simply melt away. Feel your scalp soften. Your forehead releases. The tiny muscles around your eyes relax. Your jaw unclenches, creating a small space between your teeth. Your tongue releases from the roof of your mouth.

Release your neck. Your shoulders drop toward the mattress. Your arms grow heavy. Your hands open. Your chest expands. Your belly softens. Your lower back releases. Your hips sink deeper. Your legs grow heavy. Your feet relax completely.

You are safe. You are supported. You can let go.

Now I will teach you the 4-7-8 breath pattern. Place the tip of your tongue against the ridge of tissue behind your upper front teeth. Keep it there through the entire practice.

We will breathe in quietly through the nose for 4 counts, hold the breath for 7 counts, and exhale completely through the mouth, making a soft whoosh sound, for 8 counts. The exhalation is key. It activates your relaxation response.

Let's begin together.

Breathe in through your nose. One. Two. Three. Four.

Hold your breath gently. One. Two. Three. Four. Five. Six. Seven.

Exhale slowly through your mouth with a soft whoosh. One. Two. Three. Four. Five. Six. Seven. Eight.

Beautiful. That's one complete breath. Let's do three more.

Breathe in. One. Two. Three. Four.

Hold. One. Two. Three. Four. Five. Six. Seven.

Exhale with the whoosh. One. Two. Three. Four. Five. Six. Seven. Eight.

Breathe in. One. Two. Three. Four.

Hold. One. Two. Three. Four. Five. Six. Seven.

Exhale completely. One. Two. Three. Four. Five. Six. Seven. Eight.

One more in this first set.

Breathe in. One. Two. Three. Four.

Hold peacefully. One. Two. Three. Four. Five. Six. Seven.

Exhale fully. One. Two. Three. Four. Five. Six. Seven. Eight.

Feel the relaxation spreading through your body. Each exhale carries you deeper toward sleep. Your limbs may feel heavy. Your thoughts may begin to drift. This is perfect. Let it happen.

Let's continue with another set of four breaths.

Breathe in. One. Two. Three. Four.

Hold. One. Two. Three. Four. Five. Six. Seven.

Exhale. One. Two. Three. Four. Five. Six. Seven. Eight.

Breathe in. One. Two. Three. Four.

Hold. One. Two. Three. Four. Five. Six. Seven.

Exhale. One. Two. Three. Four. Five. Six. Seven. Eight.

If your mind wanders to thoughts from the day, that's perfectly normal. Simply notice the thought, like watching a cloud drift across the sky, and gently return your attention to your breath.

Breathe in. One. Two. Three. Four.

Hold. One. Two. Three. Four. Five. Six. Seven.

Exhale. One. Two. Three. Four. Five. Six. Seven. Eight.

Breathe in. One. Two. Three. Four.

Hold. One. Two. Three. Four. Five. Six. Seven.

Exhale. One. Two. Three. Four. Five. Six. Seven. Eight.

You may be feeling quite drowsy now. This is the natural effect of the 4-7-8 breath. Your heart rate has slowed. Your blood pressure has lowered. Your brain is releasing sleep-promoting chemicals.

Let's do one final set, and then I'll leave you to drift into sleep.

Breathe in. One. Two. Three. Four.

Hold. One. Two. Three. Four. Five. Six. Seven.

Exhale. One. Two. Three. Four. Five. Six. Seven. Eight.

Breathe in. One. Two. Three. Four.

Hold. One. Two. Three. Four. Five. Six. Seven.

Exhale. One. Two. Three. Four. Five. Six. Seven. Eight.

Breathe in. One. Two. Three. Four.

Hold. One. Two. Three. Four. Five. Six. Seven.

Exhale. One. Two. Three. Four. Five. Six. Seven. Eight.

Breathe in. One. Two. Three. Four.

Hold. One. Two. Three. Four. Five. Six. Seven.

Exhale. One. Two. Three. Four. Five. Six. Seven. Eight.

Now let your breathing return to its natural rhythm. No need to control it anymore. Your body knows how to breathe. Your body knows how to sleep.

Let your thoughts become lighter. Softer. Like feathers floating on still water.

You are drifting now. Safe and warm. Held by the night.

Tomorrow will take care of itself. Right now, there is only rest.

Sleep well. Sweet dreams.
        """
    },
    
    "03_body_scan_meditation": {
        "title": "Body Scan Meditation",
        "duration_estimate": "20 minutes",
        "script": """
Welcome to the Body Scan Meditation. This practice will guide your awareness through every part of your body, releasing tension, increasing circulation, and deepening your connection to your physical self.

Find a comfortable position. You may lie down on your back with your arms slightly away from your body, palms facing up. Or you may sit in a chair with your feet flat on the floor. Choose whatever position allows you to be fully relaxed and fully aware.

Close your eyes gently. Take three deep breaths to arrive in this moment.

Breathe in deeply... and exhale fully.

Breathe in... and release.

One more time, breathe in... and let everything go.

We will now travel through your body, from the crown of your head to the tips of your toes, bringing conscious awareness to each area. There's nothing to fix or change. Simply notice, observe, and allow.

Begin at the top of your head. Bring your attention to your scalp. Notice any sensations there. Perhaps a subtle tingling. Perhaps warmth. Perhaps nothing at all. All observations are valid. Simply notice.

Move your awareness to your forehead. Feel the space between your eyebrows. Allow this area to soften completely. Let go of any furrowing or concentration. Smooth. Relaxed. Open.

Bring attention to your eyes. Even closed, they may hold tension. Let them rest deeply in their sockets. The muscles around your eyes release. Your eyelids become soft and heavy.

Notice your cheeks. Your nose. The sensation of air flowing through your nostrils with each breath. Cool on the inhale. Warm on the exhale.

Bring awareness to your mouth. Your lips. Allow them to part slightly. Feel your jaw release. Create a small space between your upper and lower teeth. Your tongue relaxes, falling away from the roof of your mouth. This is where we hold so much tension. Let it all go.

Move to your ears. Notice any sounds around you without judging them. They are simply sounds. Part of this moment.

Bring attention to your neck. This bridge between your head and body. Feel the muscles on each side. The back of your neck. Any tension here begins to melt. Softening. Releasing.

Expand your awareness to your shoulders. These carry so much for us. Worries. Responsibilities. Let them drop away from your ears. Feel them sink toward the floor or the chair. Heavy. Relaxed. Free.

Travel down your right arm. Your upper arm. Your elbow. Your forearm. Notice any sensations. Warmth. Tingling. Weight. Continue to your wrist. Your palm. Each finger, from thumb to pinky. Feel the energy in your fingertips.

Now your left arm. Upper arm. Elbow. Forearm. Wrist. Palm. Each finger, one by one. Thumb. Index. Middle. Ring. Pinky. Both arms now completely relaxed. Heavy and warm.

Bring your attention to your upper back. The muscles between your shoulder blades. Let them soften and spread. Feel your ribcage expand with each breath.

Move to your chest. Notice your heartbeat. That steady rhythm that has been with you since before you were born. Thank your heart for its tireless work.

Expand awareness to your belly. Let it be soft. No need to hold it in. Allow it to rise and fall freely with your breath. Feel the organs within, performing their miraculous functions without any conscious effort from you.

Bring attention to your lower back. This area supports you in everything you do. Acknowledge any sensations here. Send it gratitude. Let tension dissolve.

Move to your hips. Your pelvis. This bowl that holds your core. Allow it to be heavy and settled.

Travel down your right leg. Your thigh. Strong muscles that carry you through the world. Your knee. Your calf. Your ankle. The top of your foot. The sole of your foot. Each toe, from big toe to little toe.

Now your left leg. Thigh. Knee. Calf. Ankle. Top of foot. Sole. Each toe. Big toe to little toe.

Your entire body has been acknowledged. Every part of you has received attention and care.

Now expand your awareness to your body as a whole. Feel it as one unified field of sensation. Notice the boundary where your body meets the air. Feel the Life Force that animates every cell. This is you. Present. Alive. Whole.

Rest in this awareness for a few breaths. There is nothing to do. Nowhere to go. Simply be.

When you're ready to return, begin by deepening your breath. Feel the expansion in your chest and belly. Gently wiggle your fingers and toes. Roll your wrists and ankles.

Take a stretch if your body wants one. Arms overhead. A gentle twist.

Slowly open your eyes, seeing the world with fresh clarity.

You are grounded. You are present. You are connected to your body.

Carry this awareness with you. Notice how your body feels as you move through your day. It is always communicating with you. Now you know how to listen.

Thank you for practicing with me today.
        """
    },
    
    "04_energizing_breath_work": {
        "title": "Energizing Breath Work",
        "duration_estimate": "15 minutes",
        "script": """
Welcome to the Energizing Breath Work session. This practice is designed to invigorate your body, sharpen your mind, and fill you with vital energy for the day ahead. It's perfect for morning routines or anytime you need a natural energy boost without caffeine.

Stand or sit with your spine straight. If standing, feet hip-width apart, knees slightly soft. If sitting, feet flat on the floor, sitting bones grounded. Roll your shoulders back. Lift through the crown of your head.

Take a moment to check in with your energy level right now. Notice it without judgment. By the end of this practice, you will feel remarkably different.

Let's begin with three cleansing breaths to clear stale energy.

Breathe in deeply through your nose... and exhale forcefully through your mouth with a sigh. 

Again, inhale fully... and exhale with release. 

One more, deep breath in... and let it all go.

Good. Now we'll warm up with energizing inhales. These are quick, sharp breaths through the nose that pump energy into your system.

Take ten quick, sharp inhales through your nose, letting the exhales happen naturally. I'll count you through.

Begin. One. Two. Three. Four. Five. Six. Seven. Eight. Nine. Ten.

Pause. Take one deep, slow breath. In through the nose... and out through the mouth.

Feel the tingling in your fingertips. The alertness behind your eyes. This is oxygen flooding your cells.

Let's do another round of ten.

Ready? One. Two. Three. Four. Five. Six. Seven. Eight. Nine. Ten.

Deep breath in... hold briefly... and release.

Notice how you feel. More present. More awake. Now we'll move to Breath of Fire, a powerful technique from kundalini yoga.

Breath of Fire uses rapid, rhythmic breaths in and out through the nose. The emphasis is on the exhale, which is a sharp, quick expulsion of air. The inhale happens naturally. The movement comes from the belly.

Let's practice slowly first. Sharp exhale through the nose while pulling your belly in. The inhale naturally follows as your belly relaxes.

Exhale sharp. Inhale relaxed. Exhale. Inhale. Exhale. Inhale.

Now we'll speed it up. We'll do thirty seconds of Breath of Fire. Start slow and find your rhythm.

Begin... keep going... maintain the rhythm... powerful exhales... belly pumping... keep going... ten more seconds... five seconds... and rest.

Take three deep recovery breaths.

Inhale... exhale.

Inhale... exhale.

Inhale... exhale.

Notice the energy surging through your body. Your eyes are brighter. Your mind is clearer. This is your vital force awakening.

Now we'll practice energizing breath holds after an inhale. These build energy and heat in the body.

Breathe in deeply through your nose, filling your lungs completely. Hold at the top while gently engaging your core.

Inhale fully... and hold. Feel the energy building. Three. Two. One. Exhale slowly.

Again. Deep breath in... and hold. Energy building. Three. Two. One. Release.

One more time. Breathe in completely... hold with presence... three... two... one... and release fully.

Excellent. Feel the warmth spreading through your body.

Now let's combine everything into an energizing sequence. We'll do quick inhales, a breath hold, and a powerful release.

Quick inhales. One. Two. Three. Four. Five. Now hold... building energy... and release with power through the mouth. 

Again. Quick breaths. One. Two. Three. Four. Five. Hold at the top... energy building... and release.

One more time. One. Two. Three. Four. Five. Hold... feel the power... and release completely.

Your cells are saturated with oxygen. Your nervous system is activated in the optimal way for energy and focus. Your metabolism is firing.

Let's close with three intention breaths. As you inhale, think of what you want to create today. As you exhale, release what no longer serves you.

Inhale your intention... exhale what you're letting go.

Inhale purpose... exhale limitation.

Inhale energy... exhale fatigue.

Take a moment to feel the transformation in your body. You started this practice at one energy level. Notice where you are now.

Roll your shoulders back. Shake out your hands. Stamp your feet if you're standing. Claim this energy as your own.

You are awake. You are alive. You are ready.

Carry this vitality with you. When you feel it fading, you can return to these techniques. Just thirty seconds of breath of fire can reset your energy. Just three quick inhales can shift your state.

Thank you for practicing with me today. Go create something amazing.
        """
    }
}


async def generate_audio_session(session_id: str, session_data: dict):
    """Generate a single audio session using Edge TTS."""
    import edge_tts
    
    output_file = OUTPUT_DIR / f"{session_id}.mp3"
    
    print(f"\n🎙️  Generating: {session_data['title']}")
    print(f"   Estimated duration: {session_data['duration_estimate']}")
    print(f"   Output: {output_file}")
    
    # Clean up the script text
    script = session_data["script"].strip()
    
    # Use Edge TTS with a calm voice
    communicate = edge_tts.Communicate(
        text=script,
        voice=VOICE,
        rate="-5%",  # Slightly slower for meditation
        pitch="-2Hz"  # Slightly lower pitch for calm
    )
    
    await communicate.save(str(output_file))
    
    # Get file size
    size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"   ✅ Generated: {size_mb:.1f} MB")
    
    return output_file


async def main():
    """Generate all audio sessions."""
    print("=" * 60)
    print("🧘 Holistic Wellness Protocol - Audio Session Generator")
    print("=" * 60)
    print(f"\nVoice: {VOICE}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Sessions to generate: {len(SESSIONS)}")
    
    generated = []
    
    for session_id, session_data in SESSIONS.items():
        try:
            output_file = await generate_audio_session(session_id, session_data)
            generated.append((session_id, session_data["title"], output_file))
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("📦 Generation Complete!")
    print("=" * 60)
    print(f"\nGenerated {len(generated)} audio sessions:\n")
    
    for session_id, title, output_file in generated:
        size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"  • {title}: {size_mb:.1f} MB")
    
    print(f"\nAll files saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
