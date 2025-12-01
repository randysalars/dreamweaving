# Edge TTS Removal and Google Cloud TTS Migration

**Date**: 2025-11-30
**Status**: ✅ COMPLETE
**Reason**: Edge TTS ignores SSML `<break>` tags, unsuitable for hypnotic/meditative work

---

## Why Edge TTS Was Removed

### Critical Limitations

1. **❌ Ignores ALL SSML `<break>` tags**
   - Breathing cues (4/4/6) have no pause time
   - Countdowns (10...9...8...) are rushed together
   - Relaxation sequences have no spacing
   - Makes hypnotic pacing impossible

2. **❌ Too fast for meditation**
   - Even at reduced speeds, delivery is rushed
   - Post-processing pauses can't fix fundamental pacing
   - Unsuitable for hypnotic/meditative content

3. **❌ Audio quality issues**
   - Glitching/skipping at certain phrases
   - Inconsistent rendering quality

### What We Tried

- ✅ Hypnotic pacing post-processor V1: Added 293 pauses, too mechanical
- ✅ Hypnotic pacing post-processor V2: Reduced to 50 intelligent pauses, still couldn't fix core issues
- ❌ Result: Post-processing can't solve a TTS engine that ignores SSML timing

---

## New Standard: Google Cloud TTS Neural2

### Why Google Cloud TTS

1. **✅ Full SSML `<break>` support**
   - All breathing cues work as designed
   - Countdowns have proper pauses
   - Relaxation waves flow naturally

2. **✅ High quality Neural2 voices**
   - Natural, warm, expressive
   - Better suited for long-form meditation

3. **✅ Reliable rendering**
   - No glitching or skipping
   - Consistent quality across sessions

4. **✅ Professional grade**
   - Used by audiobook platforms
   - Designed for meditation/wellness content

---

## Available Voices

### Female Voices (Recommended for Dreamweaving)

| Voice | Characteristics | Best For |
|-------|----------------|----------|
| **en-US-Neural2-D** | Warm, soothing, clear | Deep journeys, meditation |
| **en-US-Neural2-I** | Calm, gentle, nurturing | Healing, relaxation |
| **en-US-Neural2-J** | Expressive, engaging | Narrative-rich sessions |

### Male Voices

| Voice | Characteristics | Best For |
|-------|----------------|----------|
| **en-US-Neural2-C** | Deep, authoritative | Power, grounding work |
| **en-US-Neural2-F** | Warm, reassuring | General meditation |
| **en-US-Neural2-H** | Calm, steady | Stability, foundation |

---

## Default Workflow Configuration

### Template Manifest Settings

**File**: `sessions/_template/manifest.yaml`

```yaml
voice:
  provider: "google"  # Default to Google Cloud TTS
  voice_name: "en-US-Neural2-D"  # Female, warm, soothing
  description: "Warm, clear voice for dreamweaving"
  rate: 0.75  # 75% speed for meditation pacing
  pitch: "-2.5st"  # Slightly deeper for soothing effect
```

### Build Session Defaults

**File**: `scripts/core/build_session.py`

```python
# Default TTS settings (Google Cloud TTS only)
DEFAULT_TTS_PROVIDER = "google"
DEFAULT_VOICE = "en-US-Neural2-D"
DEFAULT_SPEAKING_RATE = 0.75  # Slower for meditation
DEFAULT_PITCH = -2.5  # Deeper, soothing
```

---

## Voice Selection Guide

### For Different Session Types

**Deep Theta/Delta Work** (sleep, healing):
- Voice: `en-US-Neural2-D` or `en-US-Neural2-I`
- Rate: `0.70` (very slow)
- Pitch: `-3.0st` (deeper)

**Alpha Gateway** (relaxation entry):
- Voice: `en-US-Neural2-D`
- Rate: `0.75` (standard meditation)
- Pitch: `-2.5st` (warm)

**Active Visualization** (cosmic journeys):
- Voice: `en-US-Neural2-J`
- Rate: `0.80` (slightly faster for narrative)
- Pitch: `-2.0st` (engaging)

**Grounding/Power Work**:
- Voice: `en-US-Neural2-C` (male, deep)
- Rate: `0.75`
- Pitch: `-3.0st` (authoritative)

---

## SSML Best Practices (Now Fully Supported!)

### Breathing Cues

```xml
<prosody rate="x-slow" pitch="-3st">
Breathe in for 4...
<break time="4s"/>

Hold for 4...
<break time="4s"/>

Exhale for 6...
<break time="6s"/>
</prosody>
```

**✅ This now works perfectly!**

### Countdowns

```xml
<prosody rate="x-slow" pitch="-3st">
Counting down from ten to one...
<break time="2s"/>

10... <break time="2s"/>
9... <break time="2s"/>
8... <break time="2s"/>
7... <break time="2s"/>
</prosody>
```

**✅ Each number will have proper pauses!**

### Relaxation Waves

```xml
<prosody rate="slow" pitch="-2st">
A slow wave of relaxation travels from the crown...
<break time="2s"/>

To the brow...
<break time="2s"/>

To the throat...
<break time="2s"/>

To the heart...
<break time="3s"/>
</prosody>
```

**✅ Natural, flowing pacing!**

---

## Migration Checklist

### Files Updated

- [x] `sessions/_template/manifest.yaml` - Default to Google TTS
- [x] `scripts/core/build_session.py` - Remove Edge TTS option
- [x] `scripts/core/generate_session_audio.py` - Google TTS as primary
- [x] `docs/HYPNOTIC_PACING.md` - Archived (no longer needed)
- [x] `docs/EDGE_TTS_REMOVAL.md` - This document

### Files Deprecated

- `scripts/core/audio/hypnotic_pacing.py` - **ARCHIVED** (Edge TTS workaround, no longer needed)
- `docs/HYPNOTIC_PACING.md` - **ARCHIVED** (documented the workaround)

These files remain in the repository for reference but are no longer part of the active workflow.

---

## Updated Workflow

### Single Command (Now Simpler!)

```bash
python3 scripts/core/build_session.py \
  --session sessions/my-session \
  --ssml sessions/my-session/script.ssml \
  --auto-package
```

**No more**:
- ❌ `--tts-provider edge-tts`
- ❌ Post-processing with hypnotic_pacing.py
- ❌ Worrying about ignored SSML breaks

**Just works**:
- ✅ Reads manifest voice settings (defaults to Google Neural2-D)
- ✅ Respects ALL SSML `<break>` tags
- ✅ Generates properly-paced hypnotic audio
- ✅ Creates complete YouTube package

---

## Cost Comparison

### Google Cloud TTS Pricing

**Neural2 Voices**: $16 per 1 million characters

**Typical 30-minute session**:
- Script length: ~15,000 characters
- Cost: **$0.24 per session**

**Cost for 100 sessions**: $24

**Verdict**: Extremely affordable for professional-quality meditation content.

---

## Troubleshooting

### "500 Internal Error" from Google

**Cause**: Temporary API issue or SSML validation problem

**Solutions**:
1. Wait 5-10 minutes and retry
2. Check SSML is valid (`python3 scripts/utilities/validate_ssml.py`)
3. Reduce chunk size if script is very long

### "Invalid SSML" Error

**Solution**: Use the SSML validator:
```bash
python3 scripts/utilities/validate_ssml.py sessions/my-session/script.ssml
```

### Voice Sounds Too Fast

**Solution**: Adjust speaking rate in manifest:
```yaml
voice:
  provider: "google"
  voice_name: "en-US-Neural2-D"
  rate: 0.65  # Even slower (was 0.75)
```

### Voice Sounds Too High-Pitched

**Solution**: Adjust pitch in manifest:
```yaml
voice:
  provider: "google"
  voice_name: "en-US-Neural2-D"
  pitch: "-4.0st"  # Deeper (was -2.5st)
```

---

## Benefits Summary

| Aspect | Edge TTS (Old) | Google Neural2 (New) |
|--------|---------------|---------------------|
| **SSML `<break>` support** | ❌ Ignored | ✅ Fully supported |
| **Hypnotic pacing** | ❌ Rushed | ✅ Natural |
| **Audio quality** | ⚠️ Glitching | ✅ Consistent |
| **Meditation suitability** | ❌ Too fast | ✅ Perfect |
| **Post-processing needed** | ✅ Required | ❌ Not needed |
| **Workflow complexity** | ⚠️ Complex | ✅ Simple |
| **Cost** | Free | $0.24/session |

---

## Recommendation

**Use Google Cloud TTS Neural2 for ALL dreamweaving sessions.**

Edge TTS is no longer part of the workflow and should not be used for hypnotic/meditative content.

---

**Created**: 2025-11-30
**Maintainer**: Randy Sailer
**Status**: Production Standard ✅
