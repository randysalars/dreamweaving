# Dreamweaving Production Specification

**VERSION:** 2.0.0
**STATUS:** AUTHORITATIVE SPECIFICATION
**LAST UPDATED:** 2025-12-02

> This document defines the comprehensive production workflow ensuring consistency
> in voice selection, NLP/hypnotic technique adherence, sound effect synchronization,
> and audio quality across all binaural hypnosis sessions.

---

## Table of Contents

1. [Voice Consistency System](#1-voice-consistency-system)
2. [NLP/Hypnotic Guidelines Enforcement](#2-nlphypnotic-guidelines-enforcement)
3. [Sound Effect Synchronization](#3-sound-effect-synchronization)
4. [Production Pipeline](#4-production-pipeline)
5. [Quality Assurance Checklist](#5-quality-assurance-checklist)

---

## 1. Voice Consistency System

### 1.1 Canonical Voice Selection

**PRODUCTION STANDARD:** All sessions use the **deep_female** voice profile.

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Voice ID | `en-US-Neural2-E` | Deep, resonant female - ideal for hypnosis |
| Gender | Female | Consistent brand identity |
| Speaking Rate | 0.88-0.92 | Hypnotic pacing |
| Pitch | -1st to -2st | Warm, calming tone |
| Sample Rate | 48000 Hz | Production quality |

### 1.2 Voice Gender Mapping (CORRECTED)

The following table shows correct gender classification:

| Voice ID | Gender | Best For |
|----------|--------|----------|
| en-US-Neural2-C | **Female** | Soft, nurturing |
| en-US-Neural2-E | **Female** | Deep trance (DEFAULT) |
| en-US-Neural2-F | **Female** | Clear, articulate |
| en-US-Neural2-G | **Female** | Warm, approachable |
| en-US-Neural2-H | **Female** | Bright, clear |
| en-US-Neural2-A | **Male** | Calm, neutral |
| en-US-Neural2-D | **Male** | Deep, resonant |
| en-US-Neural2-I | **Male** | Warm, compassionate |
| en-US-Neural2-J | **Male** | Rich, mature |

### 1.3 Manifest Voice Configuration

Every session manifest MUST include:

```yaml
voice:
  profile: deep_female                    # Profile from voice_config.yaml
  id: en-US-Neural2-E                     # Google Cloud TTS voice ID
  gender: female                          # Explicit gender declaration
  speaking_rate: 0.90                     # Hypnotic pace
  pitch: -1st                             # Semitones adjustment
  effects_profile: headphone-class-device # Audio optimization

  # Voice consistency enforcement
  consistency:
    locked: true                          # Prevent override
    signature: "deep_female_v1"           # Version tracking
```

### 1.4 Voice Parameters Per Section

Different script sections require different voice parameters:

```yaml
voice_by_section:
  pretalk:
    speaking_rate: 1.0       # Normal pace for information delivery
    pitch: 0st               # Neutral tone

  induction:
    speaking_rate: 0.85      # Slower for relaxation
    pitch: -2st              # Deeper for calming effect

  journey:
    speaking_rate: 0.90      # Immersive pace
    pitch: -1st              # Warm and engaging

  deepening:
    speaking_rate: 0.82      # Very slow for deep trance
    pitch: -2st              # Maximum calm

  awakening:
    speaking_rate: 0.95      # Gradually faster
    pitch: -1st              # Bright but warm

  closing:
    speaking_rate: 1.0       # Return to normal
    pitch: 0st               # Neutral, grounded
```

---

## 2. NLP/Hypnotic Guidelines Enforcement

### 2.1 Script Validation Requirements

Every SSML script MUST be validated against these criteria:

#### Structural Requirements
- [ ] PRE-TALK section (2-3 minutes)
- [ ] INDUCTION section (3-5 minutes)
- [ ] JOURNEY section (10-20 minutes)
- [ ] INTEGRATION section (2-3 minutes)
- [ ] AWAKENING section (1-2 minutes)

#### NLP Pattern Requirements
- [ ] Minimum 5 embedded commands per script
- [ ] Presuppositions in induction
- [ ] Future pacing in integration
- [ ] 3-5 post-hypnotic anchors
- [ ] Sensory-specific language (all 5 senses)

#### Language Quality
- [ ] No negative imagery or fear-based language
- [ ] Positive, empowering suggestions only
- [ ] Present tense for suggestions
- [ ] Rhythmic, flowing sentence structure
- [ ] Strategic repetition patterns

### 2.2 NLP Pattern Reference

Include these patterns in every script:

```xml
<!-- Embedded Commands (emphasize key words) -->
<prosody rate="0.85" pitch="-1st">
  And you can <emphasis level="moderate">relax deeply</emphasis> now,
  allowing yourself to <emphasis level="moderate">let go completely</emphasis>.
</prosody>

<!-- Presuppositions (assume the desired state) -->
<prosody rate="0.85" pitch="-1st">
  As you continue to deepen... noticing how easily you drift...
</prosody>

<!-- Future Pacing (connect present to future) -->
<prosody rate="0.90" pitch="-1st">
  And in the days ahead, you'll notice yourself naturally feeling
  more confident... more at peace...
</prosody>

<!-- Truisms (undeniable facts that build agreement) -->
<prosody rate="0.90" pitch="-1st">
  Everyone knows how to breathe naturally...
  and with each breath, something can change...
</prosody>

<!-- Sensory Stacking (engage multiple senses) -->
<prosody rate="0.85" pitch="-1st">
  Notice the soft golden light... feel its gentle warmth...
  hear the distant crystalline tones... breathing in the
  sweet fragrance of possibilities...
</prosody>
```

### 2.3 Mandatory Script Markers

Every SSML file MUST contain these section markers:

```xml
<!-- SECTION 1: PRE-TALK -->
<!-- Duration: 2-3 minutes -->
<!-- Purpose: Welcome, safety, preparation -->

<!-- SECTION 2: INDUCTION -->
<!-- Duration: 3-5 minutes -->
<!-- Purpose: Progressive relaxation, trance induction -->

<!-- SECTION 3: JOURNEY -->
<!-- Duration: 10-20 minutes -->
<!-- Purpose: Main therapeutic content -->

<!-- SECTION 4: INTEGRATION -->
<!-- Duration: 2-3 minutes -->
<!-- Purpose: Process insights, post-hypnotic suggestions -->

<!-- SECTION 5: AWAKENING -->
<!-- Duration: 1-2 minutes -->
<!-- Purpose: Return to full awareness, grounding -->
```

---

## 3. Sound Effect Synchronization

### 3.1 SFX Marker System

Use inline markers in SSML to trigger synchronized sound effects:

```xml
<!-- SFX marker format: [[SFX:effect_name:parameters]] -->

<prosody rate="0.90" pitch="-1st">
  You hear a gentle chime in the distance...
  [[SFX:bell_chime:freq=528,duration=3s,fade_in=0.5s]]
  <break time="3s"/>
  Its resonance washing through you...
</prosody>

<prosody rate="0.85" pitch="-1st">
  A door slowly opens before you...
  [[SFX:door_creak:style=ancient,duration=2s]]
  <break time="2s"/>
  Revealing a passage of golden light...
</prosody>
```

### 3.2 SFX Timeline in Manifest

Define sound effects with precise timing:

```yaml
sfx_timeline:
  - id: opening_chime
    type: bell
    trigger_text: "gentle chime"           # Text that triggers this SFX
    time_offset: 0                         # Seconds relative to trigger
    duration_s: 3.0
    freq_hz: 528                           # Solfeggio frequency
    gain_db: -12
    fade_in_s: 0.5
    fade_out_s: 1.0

  - id: door_open
    type: foley
    trigger_text: "door slowly opens"
    time_offset: 0.3                       # Slight delay after voice
    file: assets/sfx/ancient_door.wav
    gain_db: -15

  - id: water_flow
    type: ambient
    trigger_text: "flowing waters"
    time_offset: -0.5                      # Start slightly before voice
    duration_s: 15.0
    file: assets/sfx/gentle_stream.wav
    gain_db: -20
    loop: false

  - id: heartbeat
    type: rhythm
    trigger_text: "heartbeat"
    time_offset: 0
    bpm: 60
    duration_s: 10.0
    gain_db: -18
    fade_in_s: 2.0
```

### 3.3 SFX Categories

| Category | Use Case | Example Triggers |
|----------|----------|------------------|
| bell | Transitions, awakenings | "chime", "bell", "gong" |
| foley | Physical actions | "door opens", "footsteps", "wind" |
| ambient | Environmental | "ocean", "forest", "rain" |
| rhythm | Pacing, heartbeats | "heartbeat", "drum", "pulse" |
| tonal | Frequencies | "tone", "vibration", "hum" |
| nature | Natural sounds | "birds", "stream", "thunder" |

### 3.4 SFX Synchronization Rules

1. **Pre-voice SFX**: Start 0.3-0.5s before the trigger text
2. **Post-voice SFX**: Start immediately after trigger text completes
3. **Ambient SFX**: Loop continuously during relevant section
4. **Transition SFX**: Crossfade 2-3s between sections
5. **Never overlap** competing SFX (use ducking or sequencing)

---

## 3.5 Audio Mixing Methodology

> **AUTHORITATIVE SOURCE**: See Serena memory `audio_production_methodology` for complete technical details.

### 3.5.1 Standard Stem Levels (CRITICAL)

These levels ensure all audio elements are audible and balanced:

| Stem | Mix Level | Notes |
|------|-----------|-------|
| Voice | -6 dB | Primary element, always prominent |
| Binaural | -6 dB | Audible low hum, never intrusive |
| SFX | 0 dB | Clear and impactful |

### 3.5.2 Recommended Mix Command (FFmpeg)

```bash
ffmpeg -y \
  -i voice_enhanced.wav \
  -i binaural_dynamic.wav \
  -i sfx_track.wav \
  -filter_complex "
    [0:a]volume=-6dB[voice];
    [1:a]volume=-6dB[bin];
    [2:a]volume=0dB[sfx];
    [voice][bin][sfx]amix=inputs=3:duration=longest:normalize=0[mixed]
  " \
  -map "[mixed]" \
  -acodec pcm_s16le \
  session_mixed.wav
```

### 3.5.3 Critical Implementation Notes

1. **16-bit PCM Normalization**: When loading WAV files, normalize BEFORE type conversion:
   ```python
   original_dtype = audio.dtype
   if original_dtype == np.int16:
       audio = audio.astype(np.float32) / 32768.0
   ```

2. **Sample Rate**: All stems must be 48000 Hz

3. **Peak Validation**: Final mix should have:
   - Peak: -1 to -3 dB (no clipping)
   - RMS: -15 to -20 dB

### 3.5.4 Binaural Beat Progression

Standard hypnotic arc for beat frequencies:

| Phase | Time Range | Frequency | Purpose |
|-------|------------|-----------|---------|
| Pre-Talk | 0-3 min | 12 Hz → 10 Hz | Alert alpha |
| Induction | 3-8 min | 10 Hz → 6 Hz | Descent to theta |
| Journey | 8-22 min | 6 Hz → 1.5 Hz | Deep delta trance |
| Peak | ~22 min | 40 Hz burst (3s) | Gamma insight |
| Return | 22-27 min | 1.5 Hz → 8 Hz | Ascending |
| Closing | 27-30 min | 8 Hz → 12 Hz | Alert return |

---

## 4. Production Pipeline

### 4.1 Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DREAMWEAVING PRODUCTION PIPELINE                  │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ 1. MANIFEST  │  Define session: voice, sections, SFX, audio
    │    CREATION  │  → validate against schema
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ 2. SCRIPT    │  Write SSML with NLP patterns
    │    WRITING   │  → validate hypnotic structure
    └──────┬───────┘  → embed SFX markers
           │
           ▼
    ┌──────────────┐
    │ 3. VOICE     │  Generate TTS with locked voice profile
    │    SYNTHESIS │  → en-US-Neural2-E (female)
    └──────┬───────┘  → verify gender consistency
           │
           ▼
    ┌──────────────┐
    │ 4. SFX       │  Parse markers, align to voice timing
    │    ALIGNMENT │  → render positioned SFX track
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ 5. AUDIO     │  Generate binaural, pink noise, nature
    │    LAYERS    │  → match voice duration
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ 6. MIXING    │  Combine all stems with sidechain
    │              │  → voice enhancement processing
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ 7. MASTERING │  Normalize to -14 LUFS
    │              │  → EQ, limiting, final polish
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ 8. QUALITY   │  Verify all checkpoints
    │    CONTROL   │  → approve for release
    └──────────────┘
```

### 4.2 Pipeline Commands

```bash
# 1. Create session from manifest
./scripts/utilities/create_new_session.sh "my-session"

# 2. Generate/validate SSML script
python3 scripts/utilities/validate_ssml_enhanced.py \
    sessions/my-session/working_files/script.ssml \
    --check-nlp --check-structure --fix

# 3. Synthesize voice (with locked profile)
python3 scripts/core/synthesize_voice.py \
    sessions/my-session/working_files/script.ssml \
    sessions/my-session/output/voice.wav \
    --profile deep_female \
    --verify-gender

# 4. Align and render SFX
python3 scripts/core/align_sfx.py \
    sessions/my-session/working_files/script.ssml \
    sessions/my-session/manifest.yaml \
    sessions/my-session/output/sfx_aligned.wav

# 5. Generate audio layers
python3 scripts/core/generate_session_audio.py \
    sessions/my-session/manifest.yaml

# 6. Mix all stems
python3 scripts/core/mix_session.py \
    sessions/my-session/manifest.yaml \
    --sidechain-voice

# 7. Master final audio
python3 scripts/core/master_audio.py \
    sessions/my-session/output/mixed.wav \
    sessions/my-session/output/mastered.wav \
    --target-lufs -14

# 8. Run quality control
python3 scripts/core/quality_check.py \
    sessions/my-session/
```

### 4.3 One-Command Build

```bash
# Full automated pipeline
python3 scripts/core/build_session.py sessions/my-session/ --full

# Options:
#   --validate-only    Run validations without building
#   --skip-mastering   Stop before mastering
#   --preview          Generate 30-second preview
#   --verbose          Show detailed progress
```

---

## 5. Quality Assurance Checklist

### 5.1 Pre-Production Checklist

- [ ] Manifest validated against schema
- [ ] Voice profile set to `deep_female`
- [ ] All 5 script sections present
- [ ] NLP patterns verified (min 5 embedded commands)
- [ ] SFX markers placed at trigger points
- [ ] Audio layer configuration complete

### 5.2 Voice Verification Checklist

- [ ] Voice ID is `en-US-Neural2-E`
- [ ] Gender confirmed as FEMALE in TTS response
- [ ] Speaking rate in hypnotic range (0.82-1.0)
- [ ] Pitch adjustment applied (-1st to -2st)
- [ ] No voice clipping or distortion
- [ ] Consistent tone across all sections

### 5.3 Audio Quality Checklist

- [ ] Voice audible and clear throughout
- [ ] Binaural beats present but not intrusive
- [ ] SFX properly synchronized with narration
- [ ] No audio artifacts, pops, or clicks
- [ ] Sidechain ducking effective (music ducks for voice)
- [ ] Final level normalized to -14 LUFS
- [ ] True peak below -1.5 dBTP

### 5.4 NLP/Hypnotic Checklist

- [ ] Safety disclaimer in pre-talk
- [ ] Progressive relaxation in induction
- [ ] All 5 senses engaged in journey
- [ ] Embedded commands present throughout
- [ ] 3-5 post-hypnotic anchors installed
- [ ] Positive, empowering language only
- [ ] Proper count-up awakening

### 5.5 Final Approval

```bash
# Generate quality report
python3 scripts/core/quality_check.py sessions/my-session/ --report

# Output: sessions/my-session/output/quality_report.json
```

```json
{
  "session": "my-session",
  "timestamp": "2025-12-02T10:30:00Z",
  "checks": {
    "voice_consistency": "PASS",
    "nlp_patterns": "PASS",
    "sfx_alignment": "PASS",
    "audio_quality": "PASS",
    "loudness": "PASS"
  },
  "approved": true,
  "notes": []
}
```

---

## Appendix A: Voice Profile Lock Implementation

To prevent accidental voice changes, the system uses a profile lock:

```python
# In scripts/config/voice_config.py

LOCKED_PRODUCTION_PROFILE = {
    'name': 'en-US-Neural2-E',
    'gender': 'female',
    'speaking_rate': 0.90,
    'pitch': -1.0,
    'locked': True,
    'version': 'deep_female_v1'
}

def get_production_voice():
    """Returns the locked production voice profile."""
    return LOCKED_PRODUCTION_PROFILE.copy()

def verify_voice_gender(voice_name: str) -> str:
    """Correctly determines gender for any Neural2 voice."""
    female_voices = {'C', 'E', 'F', 'G', 'H'}
    male_voices = {'A', 'D', 'I', 'J'}

    # Extract the letter from voice name (e.g., 'E' from 'en-US-Neural2-E')
    voice_letter = voice_name.split('-')[-1]

    if voice_letter in female_voices:
        return 'female'
    elif voice_letter in male_voices:
        return 'male'
    else:
        raise ValueError(f"Unknown voice: {voice_name}")
```

---

## Appendix B: SFX Synchronization Implementation

```python
# In scripts/core/sfx_sync.py

import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SFXMarker:
    effect_name: str
    parameters: dict
    text_position: int      # Character position in script
    audio_time: float       # Calculated time in audio (seconds)

def parse_sfx_markers(ssml_content: str) -> List[SFXMarker]:
    """Extract SFX markers from SSML script."""
    pattern = r'\[\[SFX:(\w+):([^\]]+)\]\]'
    markers = []

    for match in re.finditer(pattern, ssml_content):
        effect_name = match.group(1)
        params = parse_params(match.group(2))
        markers.append(SFXMarker(
            effect_name=effect_name,
            parameters=params,
            text_position=match.start(),
            audio_time=0.0  # Calculated after voice synthesis
        ))

    return markers

def align_sfx_to_voice(
    markers: List[SFXMarker],
    voice_audio: np.ndarray,
    ssml_content: str,
    sample_rate: int
) -> np.ndarray:
    """Render SFX track aligned to voice timing."""
    duration = len(voice_audio) / sample_rate
    sfx_track = np.zeros_like(voice_audio)

    for marker in markers:
        # Calculate timing based on text position
        marker.audio_time = estimate_time_from_text_position(
            marker.text_position, ssml_content, duration
        )

        # Render and place the effect
        effect_audio = render_effect(
            marker.effect_name,
            marker.parameters,
            sample_rate
        )

        # Mix into SFX track at calculated position
        start_sample = int(marker.audio_time * sample_rate)
        sfx_track = mix_at_position(sfx_track, effect_audio, start_sample)

    return sfx_track
```

---

## Appendix C: NLP Validation Implementation

```python
# In scripts/utilities/validate_nlp.py

NLP_REQUIREMENTS = {
    'embedded_commands': {
        'min_count': 5,
        'pattern': r'<emphasis[^>]*>(.*?)</emphasis>',
        'description': 'Emphasized commands that slip past conscious awareness'
    },
    'presuppositions': {
        'min_count': 3,
        'patterns': [
            r'as you continue',
            r'while you',
            r'when you notice',
            r'the more you.*the more'
        ],
        'description': 'Assumptions of desired state'
    },
    'future_pacing': {
        'min_count': 2,
        'patterns': [
            r'in the days ahead',
            r'you\'ll find yourself',
            r'you\'ll notice'
        ],
        'description': 'Connecting present experience to future behavior'
    },
    'sensory_language': {
        'required_senses': ['visual', 'auditory', 'kinesthetic', 'olfactory'],
        'patterns': {
            'visual': [r'see', r'notice', r'light', r'color', r'imagine'],
            'auditory': [r'hear', r'sound', r'voice', r'tone', r'silence'],
            'kinesthetic': [r'feel', r'touch', r'warm', r'heavy', r'relax'],
            'olfactory': [r'smell', r'scent', r'fragrance', r'aroma']
        }
    },
    'anchors': {
        'min_count': 3,
        'types': ['physical', 'symbolic', 'sensory'],
        'description': 'Triggers for reinstating hypnotic states'
    }
}

def validate_nlp_content(ssml_content: str) -> dict:
    """Validate script contains required NLP patterns."""
    results = {'passed': True, 'checks': {}, 'suggestions': []}

    for check_name, requirements in NLP_REQUIREMENTS.items():
        passed, count, details = run_check(ssml_content, requirements)
        results['checks'][check_name] = {
            'passed': passed,
            'count': count,
            'required': requirements.get('min_count', 1),
            'details': details
        }
        if not passed:
            results['passed'] = False
            results['suggestions'].append(
                f"Add more {check_name}: found {count}, need {requirements.get('min_count', 1)}"
            )

    return results
```

---

*This specification ensures consistent, professional-quality binaural hypnosis sessions
with proper voice selection, NLP technique adherence, and synchronized sound design.*
