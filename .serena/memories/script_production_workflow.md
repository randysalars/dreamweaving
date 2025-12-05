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

Use `<emphasis>` tags for key hypnotic suggestions within flowing sentences:

```xml
<!-- Permission pattern -->
You can <emphasis level="moderate">allow</emphasis> this experience to deepen...<break time="2.5s"/>

<!-- Noticing pattern -->
You may begin to <emphasis level="moderate">notice</emphasis> how easily you <emphasis level="moderate">relax</emphasis>...<break time="2s"/>

<!-- Release pattern -->
Your mind naturally begins to <emphasis level="moderate">release</emphasis> what no longer serves...<break time="2.5s"/>

<!-- Deepening (strong emphasis) -->
And you go <emphasis level="strong">deeper</emphasis> now...<break time="3s"/>
```

**Minimum Requirements:**
- 10+ embedded commands per script (3-5 induction, 5-7 journey, 2-3 integration)
- 2+ fractionation loops (one in induction, one at journey peak)

### 2.4 Fractionation Loops (Required)

Circular deepening patterns that create self-reinforcing trance spirals:

```xml
<!-- Standard loop (use in induction) -->
<prosody rate="1.0" pitch="-2st">
And the deeper you go...<break time="1.5s"/>
the more natural it feels...<break time="1.5s"/>
and the more natural it feels...<break time="1.5s"/>
the deeper you <emphasis level="moderate">allow</emphasis> yourself to go...<break time="4s"/>
</prosody>

<!-- Double-bind loop (use at journey peak) -->
<prosody rate="1.0" pitch="-2st">
You can choose to go <emphasis level="strong">deeper</emphasis> now...<break time="2s"/>
or you can wait...<break time="1.5s"/>
and notice that you are already going deeper...<break time="1.5s"/>
simply by listening...<break time="4s"/>
</prosody>
```

### 2.5 Milton Model Patterns

**Yes-Sets (opening):** 3+ truisms that create agreement momentum
```xml
You're here...<break time="700ms"/>
you're listening...<break time="700ms"/>
and already beginning to settle in...<break time="1.5s"/>
```

**Presuppositions:** "As you continue to deepen..." (assumes deepening)

**Modal Operators:** Use "may", "might", "can", "could", "perhaps" to reduce resistance

**Double-Binds:** "You can relax quickly or slowly, whichever feels right..."

### 2.6 Temporal Dissociation (Required in Integration)

```xml
<prosody rate="1.0" pitch="-1st">
And in the minutes...<break time="1s"/>
hours...<break time="1s"/>
even days ahead...<break time="1.5s"/>
insights continue unfolding...<break time="3s"/>
as your mind gently reorganizes around what serves you most...<break time="4s"/>
</prosody>
```

> **Full Pattern Library:** See `knowledge/hypnotic_patterns.yaml` for complete templates and examples.

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

## Phase 2 Enhancements: Depth Stages & Families

### Depth Stages (First-Class Constructs)

Write with awareness of listener's trance depth:

| Stage | Pitch | Volume | Max Words Between Breaks | Mood |
|-------|-------|--------|--------------------------|------|
| `pre_talk` | 0st | 0dB | 80 | grounded, warm |
| `induction` | -2st | -1dB | 60 | calming, trusting |
| `deepening` | -2st | -2dB | 50 | slower, spacious |
| `journey` | -1st | -1dB | 60 | immersive, vivid |
| `helm_deep_trance` | -4st | -3dB | 40 | profound, sacred |
| `integration` | -1st | -1dB | 60 | gently rising |
| `reorientation` | 0st | 0dB | 80 | brightening |

### Journey Families

Select appropriate family for consistent theming:

| Family | Best For | Pitch Bias |
|--------|----------|------------|
| `celestial_journey` | Cosmic, stellar, expansion | -1st |
| `eden_garden` | Paradise, nature, abundance | 0st |
| `underworld_descent` | Shadow work, caves, transformation | -2st |
| `temple_initiation` | Ceremonies, mystery schools | -1st |
| `cosmic_forge` | Fire alchemy, divine smithing | -2st |
| `ocean_depths` | Water themes, cleansing | -1st |

See `knowledge/hypnotic_patterns.yaml` for entry/exit templates per family.

### Safety Clause (REQUIRED - HARD FAIL)

**Must include safety language in first 500 words:**
- "You remain fully in control throughout..."
- "At any time, you can choose to return to waking awareness..."
- "Completely safe..."

The validator will **HARD FAIL** scripts without safety clauses.

### Rhythm Requirements

**Sentence variety for hypnotic flow:**
- Target average: 12-28 words per sentence
- 20%+ short sentences (<10 words) for emphasis
- No run-on sentences (>45 words)
- Think in breath-sized chunks (2-3 clauses then break)

---

## Phase 3 Enhancements: Deep Hypnotic Patterns

### Vagal Tone Activation (2+ per script)

Use 2-3 vagal activation patterns in induction/deepening stages. These create genuine physiological relaxation by triggering the parasympathetic nervous system.

**Available patterns in `hypnotic_patterns.yaml`:**
- `jaw_release` - Releases masseter tension
- `tongue_relaxation` - Opens throat, vagal trigger
- `belly_softening` - Activates diaphragmatic breathing
- `swallow_deepener` - Links swallow reflex to deepening (use once max)
- `eye_softening` - Reduces sympathetic activation
- `shoulder_drop` - Classic tension release cascade

**Optimal sequence:** eye_softening → jaw_release → tongue_relaxation → shoulder_drop → belly_softening → swallow_deepener (use 2-3, not all)

### Emotional Calibration (1-2 per script)

IFS-inspired questions that create space for personalized emotional processing. Place at journey entry or integration beginning.

**Available patterns:**
- `feeling_inquiry` - "What feeling is ready to soften today..."
- `part_acknowledgment` - "Perhaps there's a part of you..."
- `readiness_check` - "If something is ready to release..."
- `burden_inquiry` - "Something you've been carrying..."
- `protector_acknowledgment` - IFS-style protector appreciation

**Always follow with grounding** - never leave listener in unresolved emotional state.

### Symbolic Objects of Power (1 per script)

Include an archetypal gift/object received during journey peak. Match to session theme.

| Theme | Recommended Objects |
|-------|---------------------|
| Healing | `glowing_stone`, `crystal_vial` |
| Transformation | `flame_of_will`, `seed_of_becoming` |
| Self-knowledge | `mirror_of_truth`, `glowing_stone` |
| Release | `luminous_feather`, `crystal_vial` |
| Power | `flame_of_will`, `golden_key` |

Each object has complete SSML template with visual/tactile/energetic sensory details.

### Real-World Integration Actions (1-2 per script)

Small actions in final 2 minutes that anchor experience into daily life.

**Available patterns:**
- `hydration_anchor` - Drink water to integrate
- `beauty_noticing` - Notice one beautiful thing today
- `breath_trigger` - Three deep breaths recalls calm (universal)
- `threshold_anchor` - Doorways trigger remembering
- `morning_connection` - Tomorrow morning awareness
- `hand_heart_anchor` - Physical gesture anchor

### Signature Closing Phrase (REQUIRED)

Every session MUST end with the signature phrase:

```xml
<prosody rate="1.0" pitch="0st">
Until we journey again...<break time="2.5s"/>
rest well...<break time="1.5s"/>
dream deep...<break time="5s"/>
</prosody>
```

This creates a neurological anchor that deepens with repeated listening.

---

## Phase 6: Outcome Engineering (NEW)

### 6.1 Overview

Outcome Engineering ensures scripts contain the specific hypnotic patterns required to reliably deliver their stated transformation. Every session should specify a `desired_outcome` in the manifest.

**Reference:** `knowledge/outcome_registry.yaml`

### 6.2 Outcome Categories

| Outcome | Key Patterns Required | Focus |
|---------|----------------------|-------|
| `healing` | vagal_activation (2+), emotional_calibration (1+) | Safety, somatic release |
| `transformation` | fractionation_loops (2+), temporal_dissociation (1+) | Deep trance, identity shift |
| `empowerment` | embedded_commands (10+), fractionation_loops (2+) | Power words, receptivity |
| `self_knowledge` | emotional_calibration (2+), temporal_dissociation (1+) | Inquiry, insight |
| `release` | vagal_activation (2+), temporal_dissociation (1+) | Letting go, extends over time |
| `spiritual_growth` | temporal_dissociation (1+), sensory_stacking (3+) | Timelessness, immersion |
| `creativity` | sensory_stacking (4+), breath_pacing (2+) | Rich sensory, creative rhythm |
| `relaxation` | vagal_activation (3+), breath_pacing (3+) | Maximum parasympathetic |
| `focus` | breath_pacing (2+), embedded_commands (8+) | Regulated breathing, focus |
| `confidence` | embedded_commands (12+), fractionation_loops (2+) | Worth affirmations |

### 6.3 Before Writing

1. Check manifest for `desired_outcome` field
2. Look up outcome in `knowledge/outcome_registry.yaml`
3. Extract:
   - Required patterns with minimum counts
   - Suggested archetypes
   - Suggested journey family
   - Recommended symbolic objects
   - Integration actions

### 6.4 During Writing

- Include ALL required patterns at minimum counts
- Place patterns in specified sections (see registry)
- Select archetypes from suggested list
- Match symbolic object to outcome theme
- Include at least 1 integration action

### 6.5 After Writing

Run outcome validation:

```bash
# Full validation (includes outcome check)
python scripts/utilities/validate_ssml.py sessions/{session}/working_files/script.ssml

# Detailed outcome validation
python scripts/utilities/validate_outcome.py sessions/{session}/ -v
```

### 6.6 Additional Pattern Templates

**Identity Shift Patterns** (for transformation/empowerment/confidence):
- Future self encounter (journey peak)
- Identity step-in (integration)
- Identity merge (journey)

**Nondual Pointers** (for spiritual_growth/self_knowledge):
- Witness consciousness
- Stillness beneath
- Self-inquiry
- Awareness of awareness

**Extended Sensory Channels** (for creativity/spiritual_growth):
- Gustatory (taste)
- Olfactory (smell)
- Temporal-spatial synesthesia

See `knowledge/hypnotic_patterns.yaml` Sections 19-21 for complete templates.

---

## Quick Reference Checklist

### Before Writing Script
- [ ] Session topic/theme defined
- [ ] **Journey family selected** (celestial, garden, underworld, etc.)
- [ ] Target duration set (~25 min spoken + pauses = ~30 min total)
- [ ] Key transformation goals identified

### During Script Writing
- [ ] **Safety clause in first 500 words** (REQUIRED)
- [ ] All 7 depth stages addressed
- [ ] `rate="1.0"` used for ALL prosody tags
- [ ] Punctuation before ALL break tags (L016)
- [ ] 10+ embedded commands (distributed, not clumped)
- [ ] 2+ fractionation loops (one ~20%, one ~60%)
- [ ] Yes-set in opening (3+ truisms)
- [ ] At least one double-bind
- [ ] VAK sensory rotation in visualizations
- [ ] Temporal dissociation in integration
- [ ] **Sentence variety** (mix short/medium, avg 12-28 words)
- [ ] **Max words between breaks** per stage limits
- [ ] SFX cues placed on separate lines
- [ ] 3-5 post-hypnotic anchors included
- [ ] Word count ~3,750 words

### Phase 3 Requirements
- [ ] **2+ vagal activation patterns** (induction/deepening)
- [ ] **1-2 emotional calibration questions** (journey/integration)
- [ ] **1 symbolic object of power** (journey peak, theme-matched)
- [ ] **1-2 real-world integration actions** (reorientation)
- [ ] **Signature closing phrase** "rest well, dream deep" (REQUIRED)

### Outcome Engineering Requirements (if `desired_outcome` set)
- [ ] **All required patterns** for outcome at minimum counts
- [ ] **Patterns placed** in specified sections per registry
- [ ] **At least 1 integration action** included
- [ ] **Outcome validation passed** (`validate_outcome.py`)

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
