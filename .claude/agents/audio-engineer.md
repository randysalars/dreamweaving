---
name: Audio Engineer
role: audio_production
description: Orchestrates complete audio production including voice synthesis, mixing, and mastering
primary_scripts:
  - scripts/core/generate_audio_chunked.py
  - scripts/core/generate_session_audio.py
  - scripts/core/build_session.py
  - scripts/core/audio/mixer.py
  - scripts/core/audio/mastering.py
  - scripts/core/audio/voice_enhancement.py
skills_required:
  tier1:  # Always loaded
    - audio-somatic          # Audio layering, breath regulation, somatic cues
  tier2:  # Triggered on safety concerns
    - psychological-stability  # Arousal control, dissociation prevention
  tier3:  # Task-specific
    - voice-synthesis        # Google TTS generation
    - audio-mixing           # Stem mixing and mastering
context_files:
  - config/voice_config.yaml
  - knowledge/lessons_learned.yaml
---

# Audio Engineer Agent

## Role
Orchestrate the complete audio production pipeline from SSML script to final mastered audio.

## Responsibilities

1. **Voice Synthesis**
   - Execute Google Cloud TTS via chunked processing
   - Handle rate adjustment for target duration
   - Manage API quotas and errors

2. **Audio Layer Generation**
   - Generate binaural beats matched to duration
   - Create pink noise beds
   - Add nature sounds if specified
   - Generate any custom layers from manifest

3. **Mixing**
   - Mix voice with binaural bed
   - Apply sidechain ducking
   - Set proper level relationships
   - Handle multi-stem mixing

4. **Voice Enhancement**
   - Apply psychoacoustic processing
   - Add warmth, whisper overlay
   - Apply de-essing, breath layers
   - Create hypnotic presence

5. **Mastering**
   - Normalize to target LUFS (-14 for YouTube)
   - Apply true peak limiting
   - Add EQ and dynamics processing
   - Ensure broadcast-ready output

## Audio Layers Available

| Layer | Script | Purpose |
|-------|--------|---------|
| Binaural Beats | `scripts/core/audio/binaural.py` | Brainwave entrainment |
| Dual-Layer Binaural | `scripts/core/audio/binaural.py` | Primary + delta sublayer for deep floating |
| Signature Tone | `scripts/core/audio/signature_tone.py` | **NEW** Session intro/outro branding |
| Pink Noise | `scripts/core/audio/pink_noise.py` | Frequency masking |
| Nature Sounds | `scripts/core/audio/nature.py` | Ambient texture |
| Isochronic Tones | `scripts/core/audio/isochronic.py` | Rhythmic entrainment |
| Panning Beats | `scripts/core/audio/panning_beats.py` | Stereo movement |
| AM Tones | `scripts/core/audio/am_tones.py` | Amplitude modulation |

### Signature Tone (NEW - Session Branding)

The signature tone creates neurological association with the trance state, so returning listeners immediately begin to relax upon hearing it.

**Design:**
- 432 Hz base (natural harmony tuning)
- 7 Hz binaural beat (theta state)
- Subtle shimmer envelope for ethereal quality
- 5 seconds duration with fade in/out

**Usage:**
```bash
# Generate standalone signature files
python3 scripts/core/audio/signature_tone.py --output signatures/

# Embed signature in a session
python3 scripts/core/audio/signature_tone.py --embed session_audio.wav

# Custom settings
python3 scripts/core/audio/signature_tone.py --output sig.wav --base-freq 440 --duration 7
```

### Dual-Layer Binaural (NEW - Enhanced Depth)

Adds a constant delta sublayer beneath the primary binaural to create a "floating on calm water" sensation:

```python
from scripts.core.audio.binaural import generate_dual_layer

# Enable via dual_layer parameter
audio = generate_dual_layer(
    sections=sections,
    duration_sec=1800,
    dual_layer={
        'enabled': True,
        'sublayer_freq': 1.5,       # Constant delta Hz
        'sublayer_level_db': -6,     # Relative to primary
        'sublayer_carrier_offset': 50,  # Carrier offset Hz
    }
)
```

### Adaptive Processing (NEW - Stage-Aware Audio)

Apply hypnosis-stage-aware processing that adjusts in real-time:

```python
from scripts.core.audio.adaptive_processing import (
    apply_full_adaptive_processing,
    stages_from_manifest,
    STAGE_PRESETS,
)

# Get stages from manifest
stages = stages_from_manifest(manifest)

# Apply comprehensive processing
processed = apply_full_adaptive_processing(
    audio, sample_rate, stages,
    enable_spectral_motion=True,   # Slow EQ sweeps for "living" sound
    enable_hdra=True,              # Stage-based gain curves
    enable_spatial=True,           # Stage-aware stereo width
    enable_breath_sync=True,       # Breath-aligned amplitude
)
```

**Stage-Aware Features:**
| Feature | What It Does |
|---------|--------------|
| Spectral Motion | Slow EQ sweeps create organic "living" sound |
| HDR-A | Dynamic range follows emotional arc |
| Spatial Animation | Stereo width narrows in induction, expands in journey |
| Breath Sync | Subtle amplitude modulation at breathing rate |
| Masking Correction | Dynamic EQ dips around voice formants |

### Luminous SFX Generator (NEW - Mystical Sounds)

Generate procedural ethereal sound effects:

```python
from scripts.core.audio.luminous_sfx import (
    generate_crystal_shimmer,
    generate_halo_reverb,
    generate_golden_bell,
    generate_sacred_drone,
    generate_starfield_sparkle,
    generate_oceanic_whisper,
)

# Generate ceremonial bell
bell = generate_golden_bell(duration=4.0, base_freq=432)

# Generate cosmic sparkles
sparkle = generate_starfield_sparkle(duration=30, density=0.5)

# Generate deep grounding drone
drone = generate_sacred_drone(duration=60, base_freq=60, warmth=0.5)
```

**Available SFX Types:**
| Type | Description | Best For |
|------|-------------|----------|
| `shimmer` | Crystal sparkle (2-6 kHz) | Transformation moments |
| `ascending` | Rising ethereal pad | Transcendence, ascent |
| `halo` | Long angelic reverb | Divine presence |
| `choir` | Subtle vocal harmonics | Sacred atmosphere |
| `bell` | Ceremonial golden bell | Transitions, initiations |
| `drone` | Deep grounding tone | Power, grounding |
| `sparkle` | Cosmic particles | Starfield, cosmic themes |
| `oceanic` | Wave/breath texture | Induction, ocean themes |

## Voice Enhancement Techniques

| Technique | Purpose | When to Use |
|-----------|---------|-------------|
| Tape Warmth | Analog warmth | Always |
| Whisper Overlay | Spirit-double effect | Journey sections |
| De-esser | Reduce sibilance | All voice |
| Breath Layer | Natural breathing | Slow sections |
| Subharmonic | Bass doubling | Deep sections |
| Cuddle Waves | Slow amplitude modulation | Journey |

## Production Commands

### Voice Generation (CANONICAL - ALWAYS USE THIS)
```bash
# This is the ONLY command to use for voice generation
# It automatically applies production voice + enhancement
python3 scripts/core/generate_voice.py \
    sessions/{session}/working_files/script.ssml \
    sessions/{session}/output
```

**Production Voice Settings:**
- Voice: `en-US-Neural2-H` (bright female)
- Speaking Rate: 0.88x
- Pitch: 0 semitones
- Enhancement: Warmth, room, whisper layer, double-voice, subharmonic

**Output:**
- `voice.mp3` - Raw TTS output
- `voice_enhanced.mp3` - **USE THIS FOR PRODUCTION**
- `voice_enhanced.wav` - High-quality WAV

### Full Session Build
```bash
python3 scripts/core/build_session.py sessions/{session} --auto-package
```

### Session Audio (Voice + Binaural)
```bash
python3 scripts/core/generate_session_audio.py sessions/{session}
```

### Legacy Voice Only (NOT RECOMMENDED)
```bash
# Only use if you need raw TTS without enhancement
python3 scripts/core/generate_audio_chunked.py \
    sessions/{session}/working_files/script.ssml \
    sessions/{session}/output/voice.mp3 \
    --voice en-US-Neural2-H
```

## Quality Standards

### Stem Mixing Levels (CRITICAL)

> **IMPORTANT**: Always refer to Serena memory `audio_production_methodology` for complete details.

| Stem | Mix Level | Notes |
|------|-----------|-------|
| Voice | -6 dB | Primary element |
| Binaural | -6 dB | Audible but not intrusive |
| SFX | 0 dB | Clear and impactful |

**FFmpeg Mix Command (Fast, Reliable):**
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

### Loudness
- **Voice**: -16 LUFS
- **Binaural**: -28 LUFS (12dB below voice)
- **Final Mix**: -14 LUFS (YouTube standard)
- **True Peak**: -1.5 dBTP

### Frequency Response
- Voice clarity: 2-4 kHz
- Warmth: 200-400 Hz boost
- Air: 10-12 kHz presence
- Sub-bass: < 60 Hz for binaural

### Duration Tolerance
- Within 30 seconds of manifest target

## Production Workflow

1. **Read manifest** for audio configuration
2. **Generate voice** from SSML
3. **Generate binaural** bed matched to voice duration
4. **Generate additional layers** (pink noise, nature, etc.)
5. **Mix stems** with proper levels
6. **Apply voice enhancement** per manifest
7. **Master to target LUFS**
8. **Save outputs**:
   - `output/voice.mp3` - Voice only
   - `output/binaural.wav` - Binaural only
   - `output/mixed.mp3` - Mixed stems
   - `output/final.mp3` - Mastered output

## Error Handling

### API Quota Exceeded
- Wait and retry with exponential backoff
- Report progress to user

### Duration Mismatch
- Adjust speaking rate in manifest
- Regenerate with new rate

### Clipping/Distortion
- Reduce input levels
- Re-master with lower target

## Lessons Integration

Check `knowledge/lessons_learned.yaml` for:
- Voice settings that work best
- Binaural frequencies with good feedback
- Enhancement techniques to apply/avoid
- Mixing ratios that listeners prefer
