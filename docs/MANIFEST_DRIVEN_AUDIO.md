# Manifest-Driven Audio Configuration

**VERSION:** 1.0
**STATUS:** ✅ PRODUCTION READY
**LAST UPDATED:** 2025-11-30

## Overview

The workflow is **100% manifest-driven** for binaural beats and sound effects. Each session uses YOUR unique specifications from manifest.yaml - nothing is hardcoded or reused from templates.

---

## How It Works

### 1. You Specify in manifest.yaml

```yaml
sound_bed:
  binaural:
    enabled: true
    base_hz: 432  # YOUR carrier frequency
    sections:
      # YOUR unique beat frequencies for each phase
      - {start: 0, end: 150, offset_hz: 0.5}      # Pretalk
      - {start: 150, end: 540, offset_hz: 10.0}   # Alpha gateway
      - {start: 540, end: 1200, offset_hz: 6.0}   # Theta journey
      - {start: 1200, end: 1460, offset_hz: 2.8}  # Delta drift
      - {start: 1460, end: 1800, offset_hz: 8.0}  # Alpha return

fx_timeline:
  # YOUR unique sound effects
  - type: "gamma_flash"
    time: 1240        # YOUR timing
    duration_s: 3.0   # YOUR duration
    freq_hz: 40       # YOUR frequency
```

### 2. System Reads manifest.yaml

When you run:
```bash
python3 scripts/core/build_session.py \
  --session sessions/my-session \
  --ssml sessions/my-session/script.ssml \
  --auto-package
```

The system:
1. **Reads manifest.yaml** from your session directory
2. **Extracts YOUR binaural configuration**:
   - Carrier frequency (base_hz)
   - All section timings and frequencies
   - Gamma flashes and effects
3. **Passes to audio generator** as beat schedule
4. **Generates audio with YOUR exact specifications**

---

## What Gets Used From Manifest

### ✅ Always Used (Unique Per Session)

| Manifest Field | What It Controls | Example |
|----------------|------------------|---------|
| `sound_bed.binaural.base_hz` | Carrier frequency | 432 Hz (or 200, 528, etc.) |
| `sound_bed.binaural.sections[].offset_hz` | Beat frequencies | 6.0 Hz theta, 10.0 Hz alpha |
| `sound_bed.binaural.sections[].start` | Section timing | Start at 540 seconds |
| `sound_bed.binaural.sections[].end` | Section duration | End at 1200 seconds |
| `fx_timeline[].type` | Effect type | gamma_flash, ambient_layer |
| `fx_timeline[].time` | Effect timing | 1240 seconds (20:40) |
| `fx_timeline[].freq_hz` | Effect frequency | 40 Hz gamma burst |
| `fx_timeline[].duration_s` | Effect duration | 3.0 seconds |
| `session.duration` | Total length | 1819 seconds (~30 min) |
| `voice.voice_name` | TTS voice | en-US-AvaNeural |
| `voice.provider` | TTS service | edge-tts or google |

### ❌ Never Used (Command-Line Only)

Template defaults like `--beat-hz 7.83` are **IGNORED** when manifest exists.

---

## Example: Two Different Sessions

### Session 1: Deep Theta Journey

```yaml
# sessions/deep-theta/manifest.yaml
sound_bed:
  binaural:
    enabled: true
    base_hz: 200  # Lower carrier for deep work
    sections:
      - {start: 0, end: 300, offset_hz: 12.0}    # Beta alert
      - {start: 300, end: 900, offset_hz: 6.0}   # Theta deep
      - {start: 900, end: 1200, offset_hz: 4.0}  # Delta edge
      - {start: 1200, end: 1500, offset_hz: 6.0} # Theta return
      - {start: 1500, end: 1800, offset_hz: 10.0} # Alpha close

fx_timeline:
  - type: "gamma_flash"
    time: 800
    duration_s: 2.0
    freq_hz: 40
```

**Result**: Audio uses 200 Hz carrier, YOUR theta/delta frequencies, gamma flash at 800s.

### Session 2: Sacred Tuning Journey

```yaml
# sessions/sacred-432/manifest.yaml
sound_bed:
  binaural:
    enabled: true
    base_hz: 432  # Sacred tuning
    sections:
      - {start: 0, end: 200, offset_hz: 8.0}     # Alpha gentle
      - {start: 200, end: 1000, offset_hz: 7.83} # Schumann resonance
      - {start: 1000, end: 1400, offset_hz: 4.0} # Delta sacred
      - {start: 1400, end: 1800, offset_hz: 10.0} # Alpha return

fx_timeline:
  - type: "gamma_flash"
    time: 1200
    duration_s: 5.0
    freq_hz: 40
```

**Result**: Audio uses 432 Hz carrier, YOUR sacred frequencies, longer gamma flash at 1200s.

---

## Verification: How to Check It's Working

### 1. Check Build Logs

When running build_session.py, look for:

```
=== STEP 2: Generating binaural bed ===
   Detected gamma burst: 40Hz at 1240s
  Section 1/5: 0s-150s, 0.5Hz→0.5Hz (linear)
  Section 2/5: 150s-540s, 10.0Hz→10.0Hz (linear)
  Section 3/5: 540s-1200s, 6.0Hz→6.0Hz (linear)
  Section 4/5: 1200s-1460s, 2.8Hz→2.8Hz (linear)
  Section 5/5: 1460s-1800s, 8.0Hz→8.0Hz (linear)
Generating binaural beats: 30.0 min, carrier=432Hz
```

✅ **Confirms**: System read YOUR frequencies from manifest, not template defaults.

### 2. Check Audio with Spectral Analyzer

Use Audacity or similar:
1. Import the final audio
2. Analyze spectrum
3. Look for:
   - **Carrier frequency** (432 Hz in above example)
   - **Beat frequencies** changing over time (0.5, 10, 6, 2.8, 8 Hz)
   - **Gamma burst** spike at specified time (40 Hz at 1240s)

---

## Template vs. Session Manifest

### Template (sessions/_template/manifest.yaml)

```yaml
# This is EXAMPLE DATA ONLY
# It shows format, not real session values
sound_bed:
  binaural:
    base_hz: 432  # EXAMPLE
    sections:
      - {start: 0, end: 150, offset_hz: 0.5}  # EXAMPLE
```

**Purpose**: Shows you the format to copy.

### Your Session (sessions/my-session/manifest.yaml)

```yaml
# This is YOUR ACTUAL SESSION DATA
# System uses these exact values
sound_bed:
  binaural:
    base_hz: 528  # YOUR CHOICE
    sections:
      - {start: 0, end: 200, offset_hz: 12.0}  # YOUR FREQUENCIES
```

**Purpose**: Defines the actual audio for THIS specific session.

---

## Common Binaural Frequency Targets

Use these as guidance when creating YOUR unique beat schedules:

| Brainwave | Frequency Range | Common Use Cases |
|-----------|----------------|------------------|
| **Gamma** | 40-100 Hz | Insight flashes, peak awareness |
| **Beta** | 13-30 Hz | Alert, focused, active thinking |
| **Alpha** | 8-13 Hz | Relaxed awareness, meditation entry |
| **Theta** | 4-8 Hz | Deep meditation, creativity, dreamlike |
| **Delta** | 0.5-4 Hz | Deep sleep, healing, unconscious access |

### Special Frequencies

- **7.83 Hz**: Schumann resonance (Earth's frequency)
- **40 Hz**: Gamma insight burst
- **432 Hz**: Sacred tuning carrier
- **528 Hz**: "Love frequency" carrier
- **10 Hz**: Alpha-theta gateway

---

## Sound Effects Support

### Currently Supported FX

| Type | Parameters | Description |
|------|-----------|-------------|
| `gamma_flash` | time, duration_s, freq_hz | Gamma burst for insight activation |
| `ambient_layer` | path, start, gain_db, loop | Background ambient sound (planned) |

### Adding Gamma Flash

```yaml
fx_timeline:
  - type: "gamma_flash"
    time: 1240          # 20:40 into session
    duration_s: 3.0     # 3 second burst
    freq_hz: 40         # 40 Hz gamma
```

This creates an **intense 40 Hz binaural burst** for 3 seconds at the 20:40 mark, useful for:
- Peak insight moments
- Cosmic revelation scenes
- Pattern recognition activation
- Consciousness expansion points

---

## Advanced: Frequency Transitions

You can create **smooth transitions** between frequencies:

```yaml
sound_bed:
  binaural:
    sections:
      # Gradual descent from alpha to delta
      - start: 0
        end: 600
        offset_hz: 10.0      # Start: 10 Hz alpha
        # (No freq_end = holds at 10 Hz)

      - start: 600
        end: 1200
        offset_hz: 10.0      # Start: 10 Hz
        freq_end: 4.0        # End: 4 Hz delta
        transition: linear   # Smooth glide down

      - start: 1200
        end: 1800
        offset_hz: 4.0       # Hold at 4 Hz delta
```

**Transition Types**:
- `linear`: Even transition (default)
- `logarithmic`: Exponential curve (for harmonic ratios)
- `hold`: No transition (freq_end not specified)

---

## Best Practices

### 1. Match Beats to Journey Phases

```yaml
sections:
  - name: "pretalk"
    brainwave_target: "alpha"  # In sections
    # ...

sound_bed:
  binaural:
    sections:
      - {start: 0, end: 150, offset_hz: 10.0}  # 10 Hz = alpha
```

**Keep binaural frequencies aligned with narrative sections.**

### 2. Don't Overuse Gamma Flashes

Gamma flashes are powerful. Use sparingly:
- ✅ **Good**: 1-2 per 30-minute session at peak moments
- ❌ **Bad**: 5+ flashes scattered randomly

### 3. Plan Frequency Journey

Think of your session as a frequency journey:
```
Start (alert) → Deep (theta/delta) → Return (alpha)
    12 Hz    →   6 Hz → 4 Hz  →   8 Hz → 10 Hz
```

### 4. Test Different Carriers

Experiment with carriers for different effects:
- **200 Hz**: Deep, grounding, earth connection
- **432 Hz**: Sacred tuning, harmonic, balanced
- **528 Hz**: Love frequency, healing, transformation

---

## Troubleshooting

### "My beats sound the same as the template"

**Check**:
1. Manifest.yaml exists in session directory ✓
2. Manifest has sound_bed.binaural.sections defined ✓
3. Build command uses --session flag ✓
4. PyYAML installed (`pip install pyyaml`) ✓

**Verify**: Check build logs for "Detected gamma burst" and section frequency output.

### "Carrier frequency wrong"

**Solution**: Make sure `base_hz` is set in manifest:
```yaml
sound_bed:
  binaural:
    enabled: true
    base_hz: 432  # ← ADD THIS
```

### "No gamma flash audible"

**Check**:
1. fx_timeline defined in manifest ✓
2. Time is within session duration ✓
3. Using headphones (binaural requires stereo) ✓

**Verify**: Build logs should show "Detected gamma burst: 40Hz at XXXs"

---

## Summary

✅ **Every session uses YOUR unique specifications**
✅ **Nothing is reused from templates**
✅ **Binaural beats and sound effects fully customizable**
✅ **Carrier frequency, timings, and effects all from manifest**
✅ **Template is just an example format**

**Your workflow is manifest-driven and production-ready.**

---

**Created**: 2025-11-30
**Maintainer**: Randy Sailer
**Status**: Production Ready ✅
