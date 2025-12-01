# ⚠️ FUTURE VISION: Universal Dreamweaving Session Generator - Complete Implementation Plan

> **⚠️ THIS IS A PLANNING DOCUMENT, NOT CURRENT WORKFLOW**
>
> **FOR CURRENT WORKFLOW, USE:** [docs/CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md)
>
> This document describes a future automation vision that is NOT yet implemented.
> Do not follow these instructions as they describe non-existent tooling.
>
> **Status:** Planning/Vision Document
> **Last Updated:** 2025-11-28 (Marked as future vision)

---

## Overview
Transform the Neural Network Navigator workflow into a one-command system that generates complete audio meditation sessions for any topic with advanced sound entrainment techniques.

---

## Architecture

```
scripts/core/generate_session.py --topic "Inner Child Healing" --duration 25 --style relaxation --voice en-US-Neural2-A
    ↓
1. Scaffold session directory from template
2. Generate manifest with all audio layer specifications
3. Create enhanced SSML script from topic
4. Generate voice via TTS
5. Generate all sound entrainment layers (binaural, isochronic, etc.)
6. Mix stems with intelligent ducking
7. Master to broadcast standards
8. Generate images (optional)
9. Composite video (optional)
10. Create documentation
    ↓
Complete session ready for distribution
```

---

## Sound Entrainment Technologies Integrated

Based on research showing multiple pathways to altered consciousness states:

### 1. **Binaural Beats**
- Different frequencies in each ear create perceived beat
- Promotes brainwave entrainment
- Requires headphones

### 2. **Monaural Beats**
- Both ears receive same beat frequency
- Works without headphones
- Reinforces binaural effects

### 3. **Isochronic Tones**
- Evenly spaced pulses
- No headphones required
- Effective for entrainment

### 4. **Panning Beats**
- Intensity-modulated tones simulating movement
- Engages spatial processing
- Enhances immersion

### 5. **Alternate Beeps**
- Short tones switching ears
- Influences EEG activity
- Enhances attention

### 6. **Amplitude-Modulated Tones**
- Carrier with 40-200 Hz modulation
- Evokes steady-state responses
- Perceptual changes

### 7. **Pink Noise**
- 1/f noise bed
- Supports relaxation
- Arousal shifts when combined with beats

### 8. **Natural Sounds**
- Rain, streams, forest
- Grounding and calming
- Complements entrainment

### 9. **Rhythmic Percussion**
- Drumming/repetitive patterns
- Drives rhythmic synchronization
- Reduces normal waking consciousness

### 10. **Procedural Sound Effects**
- Bells, chimes, singing bowls
- Marks transitions
- Enhances specific moments (gamma flash)

---

## File Structure

```
dreamweaving/
├── scripts/core/
│   ├── generate_session.py          # Main entrypoint
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── ssml_gen.py              # SSML script generation
│   │   ├── tts_gen.py               # Google TTS voice synthesis
│   │   ├── binaural.py              # Binaural beats generator
│   │   ├── monaural.py              # Monaural beats generator
│   │   ├── isochronic.py            # Isochronic tones generator
│   │   ├── panning_beats.py         # Panning/moving tones
│   │   ├── alternate_beeps.py       # Ear-switching beeps
│   │   ├── am_tones.py              # Amplitude-modulated tones (40-200 Hz)
│   │   ├── pink_noise.py            # Pink noise bed with ducking
│   │   ├── nature.py                # Natural soundscapes
│   │   ├── percussion.py            # Rhythmic drumming/percussion
│   │   ├── fx_gen.py                # Sound effects (bells, chimes, bowls, gamma)
│   │   ├── mixer.py                 # Stem mixing with sidechain ducking
│   │   └── mastering.py             # Final loudness normalization & limiting
│   └── video/
│       └── compositor.py            # Universal video compositor
├── templates/
│   ├── session_manifest.yaml        # Manifest template
│   ├── ENHANCED_SCRIPT_TEMPLATE.md  # LLM prompt template for scripts
│   └── sound_presets/
│       ├── relaxation.yaml
│       ├── focus.yaml
│       ├── deep_journey.yaml
│       └── learning.yaml
└── sessions/
    ├── _template/                   # Session scaffold template
    │   ├── manifest.yaml
    │   ├── working_files/
    │   ├── output/
    │   ├── images/
    │   └── final_export/
    └── <session-name>/              # Generated session directories
```

---

## Default Stem Targets (Adjustable Per Manifest)

```yaml
# Voice: -16 LUFS target (post-TTS), no duck
# Binaural: -28 LUFS bed, gentle fade in/out
# Monaural: -30 LUFS, very low to avoid phase mud
# Isochronic: -30 LUFS, short release to keep pulses distinct
# Panning beats: -32 LUFS, slow pan (6–12s cycle), depth 35–50%
# Alternate beeps: -32 LUFS, 1–3s interval, brief (100–200 ms)
# AM tones: -30 LUFS, mod depth 30–40%
# Pink noise: -26 LUFS, sidechain duck -6 dB to voice
# Nature: -28 LUFS, optional; high-pass at 150 Hz
# Percussion: -30 LUFS, low-pass 400 Hz, light reverb; keep minimal
# Master bus: brickwall limiter to -1 dBTP; final render 48 kHz WAV + 192 kbps MP3
```

---

## Quick Parameter Presets

### Relaxation
```yaml
binaural: {base: 100, offset: 4}
isochronic: 4–6 Hz
am_tones: 40 Hz light
pink_noise: on
percussion: off
```

### Focus
```yaml
binaural: {base: 220, offset: 14}
isochronic: 14 Hz
am_tones: 40–80 Hz
panning_beats: light
percussion: very low
nature: off
```

### Deep Journey
```yaml
binaural: {base: 120, offset: 6}
monaural: 6 Hz
isochronic: 5 Hz
am_tones: 40 Hz
pink_noise: low
nature: on
percussion: off
```

---

## Implementation Phases

### Phase 1: Core Audio (Week 1)
- [x] Create `generate_session.py` entrypoint
- [x] Implement manifest schema
- [ ] Port NN Navigator binaural generator
- [ ] Implement monaural, isochronic, panning_beats
- [ ] Implement alternate_beeps, am_tones
- [ ] Implement pink_noise, percussion
- [ ] Create mixer with sidechain ducking
- [ ] Create mastering chain
- [ ] Test with 3 different presets

### Phase 2: Integration (Week 2)
- [ ] Port SSML generation
- [ ] Integrate Google TTS with chunking
- [ ] Add FX timeline support
- [ ] Create validation suite
- [ ] Write comprehensive tests
- [ ] Document all parameters

### Phase 3: Visual (Week 3)
- [ ] Integrate image generation
- [ ] Create universal compositor
- [ ] Add video rendering
- [ ] Generate documentation automatically

### Phase 4: Polish (Week 4)
- [ ] Add queue system for batch generation
- [ ] Create web dashboard (optional)
- [ ] Add retry logic
- [ ] Performance optimization
- [ ] User guide & examples

---

## Usage Examples

### Basic Session
```bash
# Generate 25-minute relaxation session
python3 scripts/core/generate_session.py \
    --topic "Deep Relaxation" \
    --duration 25 \
    --style relaxation \
    --voice en-US-Neural2-A
```

### Custom Duration & Style
```bash
# Generate 40-minute deep journey
python3 scripts/core/generate_session.py \
    --topic "Shadow Integration" \
    --duration 40 \
    --style deep_journey \
    --voice en-US-Wavenet-C
```

### Dry Run (Preview)
```bash
# See what would be generated without creating files
python3 scripts/core/generate_session.py \
    --topic "Focus Enhancement" \
    --duration 20 \
    --style focus \
    --dry-run
```

---

## Validation & Quality Control

### Smoke Test
```bash
# Generate 2-minute test session
python3 scripts/core/generate_session.py \
    --topic "Test Session" \
    --duration 2 \
    --style relaxation

# Verify outputs
ffprobe sessions/test-session/output/test-session_master.wav
ffmpeg -i sessions/test-session/output/test-session_master.wav \
       -af loudnorm=print_format=summary -f null -
```

### Quality Checks
- LUFS target: -14 LUFS ±1
- True peak: < -1.5 dBTP
- Duration match: ±1 second
- Stem presence: All enabled stems exist
- Voice clarity: SNR > 20 dB
- Gamma sync: FX timing accurate

---

## Success Metrics

✅ **Single command** generates complete session  
✅ **All 10 sound types** integrated and validated  
✅ **Reproducible** via manifest + seeds  
✅ **Broadcast quality** audio (-14 LUFS, <-1.5 dBTP)  
✅ **Documented** with auto-generated guides  
✅ **Tested** on 5+ different topics/styles  

---

## Next Immediate Steps

1. ✅ Copy this plan to `docs/SESSION_AUTOMATION_PLAN.md`
2. [ ] Create template structure at `sessions/_template/`
3. [ ] Implement `binaural.py` (port from NN Navigator)
4. [ ] Implement `monaural.py` (simplest new sound type)
5. [ ] Test basic mixing of voice + binaural + monaural
6. [ ] Expand to remaining sound types once core works

---

**Status:** Phase 1 - Foundation  
**Date:** 2025-11-27  
**Ready for:** Core audio module implementation
