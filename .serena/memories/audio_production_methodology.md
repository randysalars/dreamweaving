# Audio Production Methodology for Dreamweaving Sessions

## Overview
This document defines the standardized audio production methodology for hypnotic session creation. It ensures consistent quality and reproducibility across all sessions while allowing creative variation in content.

---

## 1. Binaural Beat Generation

### Carrier Frequency Selection
| Session Theme | Carrier Frequency | Rationale |
|---------------|-------------------|-----------|
| Grounding/Power | 150 Hz | Lower carrier for warrior/earth energy |
| Standard | 200 Hz | Neutral baseline |
| Ethereal/Cosmic | 250-300 Hz | Higher carrier for lighter themes |

### Beat Frequency Progression (Dynamic Arc)
Standard hypnotic arc pattern:
```
Pre-Talk (0-3 min):     12 Hz → 10 Hz (alpha, alert but receptive)
Induction (3-8 min):    10 Hz → 6 Hz (alpha to theta, deepening)
Journey (8-22 min):     6 Hz → 1.5 Hz (theta to delta, deep trance)
  - Optional: Gamma burst (40 Hz, 3s) at peak transformation moment
  - Optional: Micro-modulation (±0.3 Hz @ 0.05 Hz rate) for enhanced entrainment
Return (22-27 min):     1.5 Hz → 8 Hz (ascending back)
Closing (27-30 min):    8 Hz → 12 Hz (return to alert)
```

### Transition Types
- `hold`: Maintain frequency (no transition)
- `linear`: Smooth linear interpolation
- `logarithmic`: Gradual curve (better for descending)
- `burst`: Short spike with fade in/out (for gamma flashes)

### Volume Levels
- Binaural base volume: 0.30 (manifest setting)
- Mix level: -6 dB to -12 dB relative to voice
- Never louder than voice

---

## 2. Sound Effect Generation

### Procedural Generators (sfx_sync.py)
| Effect Type | Generator | Key Parameters |
|-------------|-----------|----------------|
| Bells/Gongs | `_generate_bell()` | freq: 120-440 Hz, decay: 2-5s |
| Impacts | `_generate_impact()` | low_freq: 60 Hz, resonance envelope |
| Fire/Crackle | `_generate_fire()` | crackle_rate: 20 Hz, rumble: 30 Hz |
| Ambient | `_generate_ambient()` | drone: 50/75/100 Hz layers |
| Footsteps | `_generate_footstep()` | attack: 20ms, reverb tail |
| Mystical | `_generate_mystical()` | freq sweep: 200-800 Hz |
| Heartbeat | `_generate_heartbeat()` | bpm: 60 (default) |
| Resonance | `_generate_resonance()` | singing bowl harmonics |

### SFX Gain Levels (Default: 0 dB)
- Soft/Gentle effects: -18 dB
- Standard effects: 0 dB (unity)
- Loud/Massive effects: -8 dB
- These are relative gains within the SFX track

### SFX Library Location
`assets/sfx/library.yaml` - Registry with tags, keywords, and cached files

---

## 3. Mixing Methodology

### Stem Levels (Relative to 0 dB FS)
| Stem | Level | Notes |
|------|-------|-------|
| Voice | -6 dB | Primary element |
| Binaural | -12 dB | Subtle background, always present |
| SFX | -6 dB | Moderate, punctuating moments |

### Sidechain Ducking Configuration
```python
sidechain_enabled = True
sidechain_targets = ['binaural', 'sfx']  # Duck these when voice present
sidechain_threshold = -30 dB  # Trigger level
sidechain_ratio = 0.3  # 30% reduction (gentle)
```

### FFmpeg Mix Command (Fast Alternative)
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
  output.wav
```

---

## 4. Critical Bug Fixes (Mixer Normalization)

### The Problem (mixer.py:82-84)
Audio files saved as 16-bit PCM must be normalized when loaded:

**WRONG (Bug):**
```python
audio = audio.astype(np.float32)
if audio.dtype == np.int16:  # Never true after conversion!
    audio = audio / 32768.0
```

**CORRECT (Fixed):**
```python
original_dtype = audio.dtype
if original_dtype == np.int16:
    audio = audio.astype(np.float32) / 32768.0
elif original_dtype == np.int32:
    audio = audio.astype(np.float32) / 2147483648.0
else:
    audio = audio.astype(np.float32)
```

---

## 5. Hypnotic Post-Processing (MANDATORY)

After mixing, apply the unified hypnotic post-processing script. This is a **required step** for all sessions.

### Command
```bash
python3 scripts/core/hypnotic_post_process.py --session sessions/{session}/
```

### Triple-Layer Hypnotic Presence
| Layer | Purpose | Default Level |
|-------|---------|---------------|
| Layer 1: Main Voice | Warmth + de-essing | Base |
| Layer 2: Whisper Overlay | Ethereal presence | -22 dB |
| Layer 3: Subharmonic | Grounding presence | -12 dB |

### Enhancement Chain
| Enhancement | Description | Default |
|-------------|-------------|---------|
| **Tape Warmth** | Analog saturation for richness | 25% drive |
| **De-essing** | Sibilance reduction (4-8 kHz) | Always on |
| **Whisper Overlay** | Ethereal HPF + reverb layer | -22 dB |
| **Subharmonic** | LPF + delay for grounding | -12 dB, 15ms |
| **Double-Voice** | Subliminal presence | -14 dB, 8ms delay |
| **Room Tone** | Gentle reverb for space | 4% wet |
| **Cuddle Waves** | Amplitude modulation | 0.05 Hz, ±1.5 dB |
| **Echo** | Subtle depth enhancement | 180ms, 25% decay |

### Custom Settings (Optional)
```bash
# Adjust warmth and echo
python3 scripts/core/hypnotic_post_process.py --session sessions/{session}/ \
    --warmth 0.3 --echo-delay 200

# Disable specific effects
python3 scripts/core/hypnotic_post_process.py --session sessions/{session}/ \
    --no-echo --no-cuddle
```

### Output Files
- `{session}_MASTER.wav` - 24-bit WAV (lossless)
- `{session}_MASTER.mp3` - 320 kbps MP3 (distribution)

---

## 7. File Formats and Specifications

### Audio Specifications
- Sample Rate: 48000 Hz (all stems)
- Bit Depth: 16-bit PCM for WAV files
- Channels: Stereo (2 channels)
- Final Output: WAV + MP3 (320 kbps)

### Mastering Targets
- Target LUFS: -14 LUFS
- True Peak: -1.5 dBTP
- Use FFmpeg loudnorm filter for final master

---

## 8. Testing and Validation

### Level Analysis Script
```python
import numpy as np
from scipy.io import wavfile

sr, audio = wavfile.read('file.wav')
audio = audio.astype(np.float32) / 32768.0
peak = np.max(np.abs(audio))
rms = np.sqrt(np.mean(audio**2))
print(f"Peak: {peak:.4f} ({20*np.log10(peak):.1f} dB)")
print(f"RMS: {rms:.4f} ({20*np.log10(rms):.1f} dB)")
```

### Key Timestamps for Testing
When verifying a mix, check these specific moments:
- 0:03-0:10: Binaural should be audible as low hum
- First SFX marker: Should hear clear effect
- Loudest SFX: Peak should approach -3 dB
- During voice: Binaural/SFX should duck but remain present

---

## 9. Workflow Checklist

### Pre-Mix Validation
- [ ] All stems at 48000 Hz sample rate
- [ ] Voice file is properly normalized (peak < 1.0)
- [ ] Binaural track is full session duration
- [ ] SFX track has markers at correct timestamps

### Post-Mix Validation
- [ ] Peak level: -1 to -3 dB (not clipping)
- [ ] RMS level: -15 to -20 dB
- [ ] Binaural audible in quiet sections
- [ ] SFX clearly audible at marker points
- [ ] Voice remains primary element throughout

---

---

## 10. Advanced Binaural Techniques

### Dual-Layer Binaural (NEW)

The dual-layer binaural technique creates a "floating on calm water" sensation by adding a constant delta sublayer beneath the dynamic primary layer.

**How it works:**
- Primary layer: Dynamic theta-to-delta progression as usual
- Sublayer: Constant delta (1.5 Hz default) at reduced level (-6 dB)
- Sublayer uses slightly offset carrier frequency (+50 Hz) to prevent interference

**Configuration:**
```python
from scripts.core.audio.binaural import generate_dual_layer

audio = generate_dual_layer(
    sections=sections,
    duration_sec=1800,
    dual_layer={
        'enabled': True,
        'sublayer_freq': 1.5,       # Constant delta Hz
        'sublayer_level_db': -6,     # Relative to primary (-6 to -12)
        'sublayer_carrier_offset': 50,  # Carrier offset Hz
        'crossfade_sec': 2.0,        # Layer crossfade duration
    }
)
```

**Best for:**
- Long journeys (20+ minutes)
- Deep trance work
- Sessions emphasizing "floating" or "weightless" experiences
- Cosmic/astral themes

---

## 11. Signature Tone (Session Branding)

The signature tone creates neurological association with the trance state, so returning listeners immediately begin to relax upon hearing it.

**Design Specifications:**
| Parameter | Value | Purpose |
|-----------|-------|---------|
| Base frequency | 432 Hz | Natural harmony tuning |
| Binaural beat | 7 Hz | Theta state |
| Duration | 5 seconds | Short enough to not delay content |
| Fade in | 1.5 seconds | Gentle introduction |
| Fade out | 2.0 seconds | Smooth exit |
| Shimmer rate | 0.5 Hz | Ethereal quality |

**Usage:**
```bash
# Generate standalone signature files
python3 scripts/core/audio/signature_tone.py --output signatures/

# Embed in session audio
python3 scripts/core/audio/signature_tone.py --embed session_audio.wav

# Custom settings
python3 scripts/core/audio/signature_tone.py --output sig.wav \
    --base-freq 440 --duration 7 --amplitude 0.25
```

**Placement:**
- **Intro**: Plays before pre-talk (variant: 'intro' with longer fade-in)
- **Outro**: Plays after closing (variant: 'outro' with longer fade-out)
- Consistent placement creates Pavlovian conditioning for trance state

---

---

## 12. Adaptive Processing Pipeline (Long-Term Enhancement)

The adaptive processing module provides hypnosis-stage-aware audio transformations:

**File:** `scripts/core/audio/adaptive_processing.py`

### Key Features

| Feature | Description |
|---------|-------------|
| **Spectral Motion Generator** | Slow EQ sweeps (0.008 Hz) for organic "living" sound |
| **Psychoacoustic Masking** | Dynamic EQ dips around voice formants |
| **HDR-A** | Hypnotic Dynamic Range Architecture - stage-based gain curves |
| **Spatial Animator** | Stage-aware stereo width (narrows in induction, expands in journey) |
| **Breath Sync** | Amplitude modulation aligned with relaxed breathing (0.15 Hz) |

### Stage Presets

| Stage | Gain | Low Shelf | Reverb | Stereo Width |
|-------|------|-----------|--------|--------------|
| `pretalk` | 0 dB | 0 dB | 3.0s, 8% | 90% |
| `induction` | -1 dB | +0.5 dB | 5.0s, 10% | 70% |
| `deepening` | -2.5 dB | +1.0 dB | 8.0s, 12% | 85% |
| `journey` | -2 dB | +0.5 dB | 10s, 14% | 100% |
| `luminous_core` | +1 dB | 0 dB | 12s, 16% | 100% |
| `integration` | -1 dB | +0.5 dB | 6.0s, 10% | 75% |
| `awakening` | 0 dB | 0 dB | 4.0s, 8% | 60% |

### Usage

```python
from scripts.core.audio.adaptive_processing import (
    apply_full_adaptive_processing,
    stages_from_manifest,
)

stages = stages_from_manifest(manifest)
processed = apply_full_adaptive_processing(
    audio, sample_rate, stages,
    voice_track=voice  # Optional: for masking correction
)
```

---

## 13. Luminous SFX Generator (Long-Term Enhancement)

Procedural generation of mystical sound effects:

**File:** `scripts/core/audio/luminous_sfx.py`

### Available Effects

| Effect | Function | Best For |
|--------|----------|----------|
| Crystal Shimmer | `generate_crystal_shimmer()` | Transformation, light |
| Ascending Pad | `generate_ascending_pad()` | Transcendence, rising |
| Halo Reverb | `generate_halo_reverb()` | Divine presence, 528 Hz |
| Choir Texture | `generate_choir_texture()` | Sacred atmosphere |
| Golden Bell | `generate_golden_bell()` | Transitions, 432 Hz |
| Sacred Drone | `generate_sacred_drone()` | Grounding, power |
| Starfield Sparkle | `generate_starfield_sparkle()` | Cosmic, particles |
| Oceanic Whisper | `generate_oceanic_whisper()` | Induction, waves |

### Composite Track Generation

```python
from scripts.core.audio.luminous_sfx import generate_luminous_sfx_track

events = [
    {'type': 'bell', 'time': 0, 'duration': 4, 'base_freq': 432},
    {'type': 'shimmer', 'time': 300, 'duration': 10, 'amplitude': 0.2},
    {'type': 'halo', 'time': 900, 'duration': 15, 'center_freq': 528},
]

track = generate_luminous_sfx_track(duration=1800, events=events)
```

---

## Version History
- v1.2 (2025-12-04): Added adaptive processing and luminous SFX documentation
- v1.1 (2025-12-04): Added dual-layer binaural and signature tone documentation
- v1.0 (2025-12-02): Initial documentation based on Iron Soul Forge session fixes
