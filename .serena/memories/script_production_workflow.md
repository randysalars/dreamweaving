# Script Production Workflow

## Overview

This document defines the complete workflow for creating production-ready hypnotic scripts with sound effect cues, proper SSML formatting, and voice generation.

---

## Phase 1: Script Creation

### 1.1 Start with Session Topic/Theme

Begin with a clear session concept including:
- Session name (kebab-case)
- Theme/archetype
- Target duration (typically 25-30 minutes)
- Key transformation goals

### 1.2 Script Structure (5 Mandatory Sections)

Every script MUST contain these sections with XML comments:

```xml
<!-- SECTION 1: PRE-TALK -->
<!-- Duration: 2-3 minutes -->
<!-- Purpose: Welcome, safety, preparation -->

<!-- SECTION 2: INDUCTION -->
<!-- Duration: 4-5 minutes -->
<!-- Purpose: Progressive relaxation, trance induction -->

<!-- SECTION 3: MAIN JOURNEY -->
<!-- Duration: 14-16 minutes -->
<!-- Purpose: Core transformation experience -->

<!-- SECTION 4: INTEGRATION AND RETURN -->
<!-- Duration: 2-3 minutes -->
<!-- Purpose: Process insights, return to awareness -->

<!-- SECTION 5: POST-HYPNOTIC ANCHORS AND CLOSING -->
<!-- Duration: 2-3 minutes -->
<!-- Purpose: Install anchors, closing message -->
```

### 1.3 Word Count Target

- **Target: ~3,750 words** for 25-minute session at normal speaking rate
- With generous pauses, actual duration will be 28-32 minutes
- This provides comfortable pacing without feeling rushed

---

## Phase 2: SSML Formatting

### 2.1 Prosody Settings (CRITICAL)

**ALWAYS use `rate="1.0"` (normal speed) for ALL sections.**

Slow speaking rates (0.85, 0.88, 0.90) sound unnatural with Google Cloud TTS Neural2 voices.

```xml
<!-- Pre-Talk: Normal, grounded -->
<prosody rate="1.0" pitch="0st">

<!-- Induction: Normal rate, deeper pitch for calming -->
<prosody rate="1.0" pitch="-2st">

<!-- Journey: Normal rate, slightly deeper for immersion -->
<prosody rate="1.0" pitch="-1st">

<!-- Integration: Normal rate, maintaining depth -->
<prosody rate="1.0" pitch="-1st">

<!-- Closing: Normal rate, neutral pitch, grounded -->
<prosody rate="1.0" pitch="0st">
```

### 2.2 Hypnotic Pacing Through Breaks

Achieve hypnotic pacing through strategic `<break>` tags, NOT slower speech rate.

**Break Duration Guidelines:**

| Context | Duration | Example |
|---------|----------|---------|
| Between phrases | 700ms-1.0s | `word, <break time="700ms"/> next word` |
| After sentences | 1.0s-1.7s | `sentence. <break time="1.3s"/>` |
| Breathing cues | 2.0s-3.0s | `Breathe in... <break time="3.0s"/>` |
| Visualization moments | 3.0s-4.0s | `See it clearly. <break time="3.5s"/>` |
| Major transitions | 4.0s-5.5s | `You have arrived. <break time="5.5s"/>` |
| After emphasis words | 1.0s-1.3s | `<emphasis>Discipline.</emphasis> <break time="1.0s"/>` |

### 2.3 Emphasis for Embedded Commands

Use `<emphasis>` tags for key suggestions and virtue words:

```xml
<emphasis level="moderate">Discipline.</emphasis> <break time="1.0s"/>
<emphasis level="strong">"Now we forge,"</emphasis> <break time="1.0s"/>
```

---

## Phase 3: Sound Effect Cues

### 3.1 SFX Marker Format

Place SFX cues on their own lines using square brackets:

```
[SFX: Description of sound, duration/timing notes]
```

### 3.2 SFX Categories

1. **Ambient/Continuous** - Background soundscapes
   - `[SFX: Volcanic cavern ambience - bubbling magma, distant fire, low rumbling - continues throughout journey section at low volume]`

2. **Bells/Gongs** - Transitions and emphasis
   - `[SFX: Deep ceremonial bell tone, resonant, 4 seconds with natural decay]`

3. **Rhythmic** - Drums, heartbeats
   - `[SFX: Slow heartbeat rhythm begins, 60 BPM, very subtle underneath, continues through induction]`

4. **Footsteps** - Movement and descent/ascent
   - `[SFX: Footstep on stone, single, with reverb, 1 second]`

5. **Fire/Heat** - Transformation moments
   - `[SFX: Fire whooshing, internal, 3 seconds]`
   - `[SFX: Flame burst, quick, 1 second]`

6. **Metal/Forge** - Theme-specific
   - `[SFX: MASSIVE hammer strike on metal - deep, resonant, reverberant, 3 seconds]`

7. **Mystical/Ethereal** - Magic moments
   - `[SFX: Rising tone, magical, transformative, 4 seconds]`

### 3.3 SFX Placement Rules

- Place SFX cue on the line BEFORE the text it accompanies
- For continuous ambience, note when it starts and when it fades
- Include duration estimates for timing
- Be descriptive enough for a sound designer to create the effect

---

## Phase 4: Voice Generation

### 4.1 File Structure

Create two script versions:

1. **`script_production.ssml`** - Full script with SFX markers (for reference/mixing)
2. **`script_voice_clean.ssml`** - Script with SFX markers removed (for TTS)

### 4.2 Creating Clean Voice Script

Run this process to create the voice-only version:

```python
import re

with open('script_production.ssml', 'r') as f:
    content = f.read()

# Remove SFX markers
content = re.sub(r'\[SFX:[^\]]*\]', '', content)

# Remove production notes at end (after </speak>), keep section markers
content = re.sub(r'(</speak>)\s*<!--[\s\S]*', r'\1\n', content)

# Remove multiple consecutive blank lines
content = re.sub(r'\n{3,}', '\n\n', content)

with open('script_voice_clean.ssml', 'w') as f:
    f.write(content)
```

**Important:** Keep the `<!-- SECTION -->` comments in the clean script - they're needed for proper chunking!

### 4.3 Voice Generation Command

```bash
source venv/bin/activate
python3 scripts/core/generate_voice.py \
    sessions/{session}/working_files/script_voice_clean.ssml \
    sessions/{session}/output
```

This automatically:
- Uses **en-US-Neural2-H** (bright female voice)
- Speaking rate: 0.88x
- Applies voice enhancement (warmth, room, layers)
- Outputs both `voice.mp3` and `voice_enhanced.mp3`

### 4.4 Output Files

| File | Purpose |
|------|---------|
| `voice.mp3` | Raw TTS output |
| `voice_enhanced.mp3` | Production-ready with enhancements |
| `voice_enhanced.wav` | High-quality WAV for mixing |

**Always use `voice_enhanced.mp3` or `.wav` for production!**

---

## Phase 5: Production Notes

### 5.1 Include at End of Production Script

Add production notes as XML comments after `</speak>`:

```xml
</speak>

<!-- ============================================================== -->
<!-- PRODUCTION NOTES                                                -->
<!-- ============================================================== -->
<!--
ESTIMATED WORD COUNT: ~3,780 words
ESTIMATED DURATION: 28-32 minutes (normal speaking rate with strategic pauses)

SECTION BREAKDOWN:
- Pre-Talk: ~480 words (2-3 min)
- Induction: ~620 words (4-5 min)
- Main Journey: ~1,950 words (14-16 min)
- Integration: ~350 words (2-3 min)
- Anchors/Closing: ~380 words (2-3 min)

VOCAL DELIVERY NOTES:
** ALL SECTIONS USE rate="1.0" (normal speed) **
** Hypnotic pacing achieved through <break> tags, NOT slow speech rate **

BINAURAL BEAT RECOMMENDATIONS:
- Frequency: 2.5 Hz delta for deep trance
- Carrier: 150 Hz for grounding
- Volume: 0.30 (30%) to allow voice prominence
-->

<!-- ============================================================== -->
<!-- SOUND EFFECTS PRODUCTION LIST                                   -->
<!-- ============================================================== -->
<!--
[List all unique SFX needed, organized by category]

MIXING NOTES:
- All SFX should duck for voice clarity
- Continuous ambience at -20 to -25 dB
- Accent SFX (bells, gongs) at -12 to -15 dB
- Final master to -14 LUFS with -1.5 dBTP true peak
-->
```

---

## Quick Reference Checklist

### Before Writing Script
- [ ] Session topic/theme defined
- [ ] Target duration set (~25 min spoken + pauses = ~30 min total)
- [ ] Key transformation goals identified

### During Script Writing
- [ ] All 5 section markers included
- [ ] `rate="1.0"` used for ALL prosody tags
- [ ] Generous breaks for hypnotic pacing (not slow rate)
- [ ] SFX cues placed on separate lines
- [ ] 3-5 post-hypnotic anchors included
- [ ] Word count ~3,750 words

### Before Voice Generation
- [ ] SSML validated with `validate_ssml.py`
- [ ] Clean voice script created (SFX removed, section markers kept)
- [ ] No square bracket markers remaining in clean script

### After Voice Generation
- [ ] Duration verified (~28-32 minutes)
- [ ] Enhanced voice file created
- [ ] Production script saved for mixing reference

---

## Example Session Files

```
sessions/{session-name}/
├── manifest.yaml
├── working_files/
│   ├── script_production.ssml    # Full script with SFX cues
│   └── script_voice_clean.ssml   # Clean script for TTS
├── output/
│   ├── voice.mp3                 # Raw TTS
│   ├── voice_enhanced.mp3        # Enhanced (use this!)
│   └── voice_enhanced.wav        # High-quality for mixing
└── midjourney-prompts.md
```
