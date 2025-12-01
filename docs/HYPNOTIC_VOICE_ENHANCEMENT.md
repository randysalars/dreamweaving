# Hypnotic Voice Enhancement Workflow

This document describes the hypnotic voice enhancement techniques integrated into the Dreamweaving audio production workflow.

## Overview

The voice enhancement module (`scripts/core/audio/voice_enhancement.py`) applies professional post-processing techniques to TTS-generated voice tracks, transforming them from synthetic-sounding speech into warm, immersive hypnotic narration.

The linguistic patterns module (`scripts/core/audio/hypnotic_patterns.py`) provides Ericksonian language patterns, Milton Model phrases, and other hypnotic deepening techniques for script writing.

These techniques are integrated into the mastering pipeline (`scripts/core/audio/mastering.py`).

## Triple-Layered Hypnotic Presence

The enhanced voice creates a three-dimensional "hypnotist presence":

| Layer | Description | Frequency Range | Effect |
|-------|-------------|-----------------|--------|
| **Layer 1** | Main voice (clear, natural) | Full spectrum | Primary message delivery |
| **Layer 2** | Whisper ghost (HPF + reverb) | 900 Hz+ | Ethereal presence above |
| **Layer 3** | Subharmonic warm (LPF + delay) | Below 400 Hz | Grounding presence below |

This creates a sense of being surrounded by the voice, enhancing the feeling of safety and immersion.

---

## Enhancement Techniques

### 1. Tape Saturation Warmth

**Purpose:** Add analog character and subtle harmonic richness to digital TTS output.

**Implementation:**
- Applies soft clipping with `acompressor` for gentle saturation
- Adds tube-like warmth using `atone` low-pass filter
- Uses `rubberband` for subtle pitch warmth

**Parameters:**
- `warmth_drive`: 0.0-1.0 (default: 0.25)

**Effect:** Removes the "cold digital" quality from TTS voices, making them feel more human and comforting.

---

### 2. De-Essing (Sibilance Reduction)

**Purpose:** Soften harsh "s" and "sh" sounds that can be jarring in hypnotic content.

**Implementation:**
- High-frequency detection at 5-8 kHz
- Dynamic compression of sibilant frequencies only
- Preserves clarity while reducing harshness

**Parameters:**
- `threshold`: 0.0-1.0 (default: 0.4)
- `frequency`: Center frequency in Hz (default: 6000)

**Effect:** Creates a gentler, more soothing vocal quality without sacrificing intelligibility.

---

### 3. Whisper Overlay (Spirit-Double Effect)

**Purpose:** Create a subtle ethereal presence beneath the main voice, as if a "spirit guide" whispers along.

**Implementation:**
- Creates a pitch-shifted copy (+3 semitones)
- Applies high-pass filter (removes bass)
- Adds heavy reverb (70-80% wet)
- Mixes at very low volume (-20 to -24 dB)

**Parameters:**
- `whisper_db`: Volume in dB (default: -22)
- `reverb_wet`: Reverb mix amount (default: 0.2)

**Effect:** Adds an almost subliminal layer of presence that enhances the mystical quality of the narration.

---

### 4. Phase-Shifted Double-Voicing

**Purpose:** Create subtle depth and richness through nearly-imperceptible doubling.

**Implementation:**
- Duplicates the voice track
- Applies 6-10ms delay (Haas effect zone)
- Slight pitch detune (-2 to +2 cents)
- Mixes at -12 to -16 dB below main voice

**Parameters:**
- `double_delay_ms`: Delay in milliseconds (default: 8)
- `double_db`: Volume in dB (default: -14)

**Effect:** Creates a fuller, more authoritative vocal presence without obvious doubling artifacts.

---

### 5. Room Impulse Response

**Purpose:** Add physical presence and dimensionality to the voice.

**Implementation:**
- Uses FFmpeg's `aecho` or `reverb` filter
- Very short decay (subtle room ambience)
- Low wet mix (2-5%)

**Parameters:**
- `room_amount`: Wet mix 0.0-1.0 (default: 0.03)

**Effect:** Makes the voice feel like it exists in a real space rather than floating in a vacuum.

---

### 6. Stereo Micro-Panning (ASMR Effect)

**Purpose:** Create subtle ear-to-ear movement for immersive experience.

**Implementation:**
- Very slow LFO modulation of stereo position
- Subtle width (2-5% movement)
- Phase-coherent to maintain focus

**Parameters:**
- `micropan_amount`: 0.0-1.0 (default: 0.03)

**Effect:** Creates gentle, hypnotic stereo movement. Use sparingly for hypnosis (can be distracting).

---

### 7. Breath Layer Generation

**Purpose:** Add natural breathing sounds to create rhythm and pacing cues.

**Implementation:**
- Generates soft pink noise bursts
- Shapes with envelope to mimic breath
- Places at natural pause points

**Parameters:**
- `duration_seconds`: Length of breath layer to generate
- `sample_rate`: Audio sample rate (default: 48000)

**Note:** Currently experimental. Best used with manual placement.

---

### 8. Subharmonic Warm Layer

**Purpose:** Create grounding bass presence beneath the voice (Layer 3 of triple-layer presence).

**Implementation:**
- Duplicates voice track
- Applies low-pass filter at 400 Hz (bass only)
- Adds 8ms delay for warmth
- Low-shelf boost at 200 Hz for body resonance

**Parameters:**
- `subharmonic_db`: Volume in dB (default: -12)

**Effect:** Creates a warm, body-resonance foundation that grounds the listener. The bass frequencies are felt more than heard, creating a sense of physical presence.

---

### 9. Amplitude Modulation "Cuddle Waves"

**Purpose:** Create subtle slow-volume undulations that simulate being gently rocked or held.

**Implementation:**
- Very slow tremolo effect (0.04-0.07 Hz)
- Small amplitude variation (±1.5 dB)
- Sine wave modulation for smoothness

**Parameters:**
- `cuddle_frequency`: LFO frequency in Hz (default: 0.05 = one cycle per 20 seconds)
- `cuddle_depth_db`: Volume variation depth (default: 1.5 dB)

**Effect:** Creates a metaphorical "rocking" sensation in the listener's nervous system. The slow, gentle volume undulations bypass conscious awareness and trigger parasympathetic relaxation.

---

## SSML-Level Techniques

These techniques are applied at the script level before TTS generation:

### Micro-Inflection Drift

Small pitch variations within sentences create natural speech patterns:

```xml
<prosody pitch="+2%">Ten.</prosody> <prosody pitch="-3%">Drifting deeper.</prosody>
```

### Temporal Jitter

Randomized pause lengths prevent robotic pacing:

```xml
<break time="280ms"/>  <!-- Not always exactly 300ms -->
<break time="220ms"/>  <!-- Varies naturally -->
```

### Falling Cadence

Descending pitch on sentence endings creates hypnotic effect:

```xml
<prosody pitch="-0.5st">...and release.</prosody>
```

### Variable Rate Pacing

Different sections use different speaking rates:

| Section | Rate | Purpose |
|---------|------|---------|
| Pre-talk | 1.0 | Normal, conversational |
| Induction | 0.94 → 0.92 | Gradual slowing |
| Deep Journey | 0.90 → 0.88 | Deep trance pacing |
| Return | 0.94 → 1.0 | Gradual speeding |

---

## Manifest Configuration

Add this block to your session's `manifest.yaml`:

```yaml
voice_enhancement:
  enabled: true
  warmth_drive: 0.25
  deessing: true
  whisper_overlay: true
  whisper_db: -22
  double_voice: true
  double_db: -14
  double_delay_ms: 8
  room_tone: true
  room_amount: 0.03
  stereo_micropan: false
  micropan_amount: 0.03
```

---

## CLI Usage

### Basic mastering (no enhancement):

```bash
python3 scripts/core/audio/mastering.py voice.wav
```

### Mastering with voice enhancement:

```bash
python3 scripts/core/audio/mastering.py voice.wav --enhance
```

### Selective enhancement:

```bash
python3 scripts/core/audio/mastering.py voice.wav --enhance --no-whisper --no-double
```

### Direct voice enhancement (without mastering):

```bash
python3 scripts/core/audio/voice_enhancement.py voice.wav -o voice_enhanced.wav
```

---

## Processing Order

The full enhancement chain applies in this order:

1. **De-essing** - Remove harsh sibilants first
2. **Tape warmth** - Add analog character
3. **Whisper layer** - Generate and mix spirit-double
4. **Double voice** - Add phase-shifted copy
5. **Room tone** - Add spatial presence
6. **Stereo micropan** - Add subtle movement (if enabled)
7. **LUFS normalization** - Match target loudness
8. **EQ** - Warmth and presence boost
9. **Stereo enhancement** - Subtle widening
10. **Peak limiting** - Prevent clipping

---

## Best Practices

1. **Less is more** - Subtle enhancement sounds natural; heavy processing sounds artificial
2. **Test on headphones** - Most listeners use headphones for hypnosis
3. **Preserve intelligibility** - The voice must remain clear and easy to understand
4. **Match the journey** - Deep trance sections can use more enhancement than conversational pre-talk
5. **A/B compare** - Always compare enhanced vs. original to ensure improvement

---

## Linguistic Enhancement Patterns

The `hypnotic_patterns.py` module provides ready-to-use language patterns for script writing.

### Ericksonian Nested Loops

Use loops within loops to bypass conscious filters:

```python
from scripts.core.audio.hypnotic_patterns import get_nested_loop

loop = get_nested_loop()
# Returns: ["and as you notice yourself listening",
#           "you may also notice yourself noticing",
#           "how listening becomes a feeling",
#           "and that feeling becomes something drifting inward"]
```

### Milton Model Ambiguities

Phrases that bypass logical analysis:

| Pattern Type | Example |
|-------------|---------|
| Mind reading | "You may already be noticing..." |
| Lost performative | "It's good to relax deeply..." |
| Cause-effect | "The more you listen, the deeper you go..." |
| Presupposition | "When you notice the relaxation..." |
| Double bind | "You can relax quickly or slowly, whichever feels right..." |
| Embedded command | "You can allow yourself to sink deeper..." |

### Sensory-Synesthetic Blending

Cross-modal sensory phrases that open deeper associations:

- "Feel the color of the light..."
- "Hear the warmth spreading..."
- "See the sound of your breath softening..."

### Somatic Anchors

Physical sensation references for embodiment:

- "That subtle heaviness behind the eyes..."
- "The warmth spreading through your palms..."
- "That warm hum at the base of your spine..."

### Limbic Language

Emotional activation phrases:

- Safety: "safe warmth", "held securely", "cocooned in comfort"
- Softness: "soft openness", "gentle surrender", "tender release"
- Depth: "deeper stillness", "profound quiet", "infinite rest"

### Time Distortion

Phrases that make time feel fluid:

- "Moments stretching softly..."
- "Between one breath and the next, entire worlds open..."
- "Time unwinding like a ribbon..."

### Trance Ratifications

Phrases that confirm the listener's experience:

- "That subtle heaviness in your jaw..."
- "The way your breath naturally slows..."
- "That dreamy quality to your awareness now..."

### Soothing Refrains

Repeat every 70-90 seconds for rhythmic entrainment:

- "...and deeper still..."
- "...softly drifting..."
- "...a slow dissolving..."
- "...beautifully relaxing..."

### Somatic Return Sequence

Walk the listener back through their body:

1. Hands warming
2. Feet grounding
3. Breath deepening
4. Spine lengthening
5. Eyes clearing

---

## Technical Notes

- All processing uses FFmpeg for maximum compatibility
- Intermediate files are created in system temp directory and cleaned up automatically
- Sample rate is preserved throughout the chain
- Bit depth is maintained at 24-bit until final export
