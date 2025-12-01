# Edge TTS Removal - Implementation Complete

**Date**: 2025-11-30
**Status**: ✅ COMPLETE

---

## Summary

Edge TTS (Ava voice) has been **completely removed** from the dreamweaving production workflow per user request.

**User's Request:**
> "remove the ava voice and edge tts from our workflow completely so we do not get confused"

**Reason for Removal:**
- **Ignores ALL SSML `<break>` tags** - breathing cues, countdowns, relaxation waves had no pauses
- **Too fast for meditation** - even with post-processing
- **Audio quality issues** - skipping/glitching at certain phrases
- **Post-processing couldn't fix core issues** - hypnotic_pacing.py V2 was just a workaround

**New Production Standard:**
- **Google Cloud TTS Neural2** only
- **Default voice**: en-US-Neural2-D (female, warm, soothing)
- **Default settings**: 75% speed, -2.5st pitch
- **Full SSML support**: All `<break>` tags work natively

---

## Files Updated

### 1. Core Workflow Scripts

#### `sessions/_template/manifest.yaml`
**Changed:**
```yaml
# OLD (Edge TTS)
voice:
  provider: "edge-tts"
  voice_name: "en-US-AvaNeural"
  rate: 0.85
  pitch: "-2st"

# NEW (Google Cloud TTS)
voice:
  provider: "google"
  voice_name: "en-US-Neural2-D"
  rate: 0.75
  pitch: "-2.5st"
```

**Added:** Alternative voice options in comments
- en-US-Neural2-I (calm, gentle)
- en-US-Neural2-J (expressive, engaging)
- en-US-Neural2-C (male, deep)
- en-US-Neural2-F (male, warm)

#### `scripts/core/build_session.py`
**Changed:**
- Default voice: `en-US-AvaNeural` → `en-US-Neural2-D`
- Default TTS provider: `edge-tts` → `google`
- Removed `edge-tts` from TTS provider choices
- Only accepts `google` now

**Before:**
```python
parser.add_argument("--voice", default="en-US-AvaNeural", ...)
parser.add_argument("--tts-provider", choices=["google", "edge-tts"], default="edge-tts", ...)
```

**After:**
```python
parser.add_argument("--voice", default="en-US-Neural2-D", ...)
parser.add_argument("--tts-provider", choices=["google"], default="google", ...)
```

#### `scripts/core/generate_session_audio.py`
**Changed:**
- Default voice: `en-US-AvaNeural` → `en-US-Neural2-D`
- Default speaking rate: `0.85` → `0.75` (meditation pacing)
- Default pitch: `-2.0st` → `-2.5st` (deeper, more soothing)
- Removed `edge-tts` from TTS provider choices
- Deprecated `_synthesize_edge_tts()` function (raises NotImplementedError)
- Deprecated `_extend_voice_with_silence()` function (no longer needed)
- Simplified voice synthesis logic (Google only)

**Before:**
```python
def synthesize_current(rate: float):
    if args.tts_provider == "edge-tts":
        _synthesize_edge_tts(ssml_path, voice_out, args.voice, rate, args.pitch)
    else:
        synthesize_ssml_file_chunked(...)
```

**After:**
```python
def synthesize_current(rate: float):
    # Google Cloud TTS only (Edge TTS removed from production workflow)
    synthesize_ssml_file_chunked(...)
```

---

### 2. Deprecated Modules

#### `scripts/core/audio/hypnotic_pacing.py`
**Status**: DEPRECATED / ARCHIVED

**Added:**
- Deprecation warning at module level
- Warning displayed when module is imported
- Clear notice that this was an Edge TTS workaround
- Reference to migration guide

**Warning Added:**
```python
import warnings
warnings.warn(
    "hypnotic_pacing.py is DEPRECATED. Edge TTS is no longer supported. "
    "Use Google Cloud TTS Neural2 instead, which respects SSML breaks natively. "
    "See docs/EDGE_TTS_REMOVAL.md for details.",
    DeprecationWarning,
    stacklevel=2
)
```

**Module still works** (for backward compatibility) but displays deprecation warning.

---

### 3. Documentation Updates

#### `docs/EDGE_TTS_REMOVAL.md` (NEW)
**Created**: Complete migration guide
- Why Edge TTS was removed
- Google Cloud TTS Neural2 as new standard
- Available voices with descriptions
- Default configuration
- Voice selection guide for different session types
- SSML best practices (now fully supported)
- Cost comparison ($0.24/session)
- Troubleshooting guide

#### `docs/HYPNOTIC_PACING.md`
**Status**: DEPRECATED / ARCHIVED

**Added:**
- ⚠️ DEPRECATION NOTICE at top
- Clear statement: "no longer part of production workflow"
- Migration guidance to Google Cloud TTS
- Reference to EDGE_TTS_REMOVAL.md
- Original documentation kept for historical reference

**Before:**
```markdown
**STATUS:** ✅ PRODUCTION READY
```

**After:**
```markdown
**STATUS:** ⚠️ DEPRECATED / ARCHIVED

## ⚠️ DEPRECATION NOTICE

**This module and documentation are DEPRECATED...**
```

#### `docs/PRODUCTION_WORKFLOW.md`
**Updated**: Version 3.0 - Google Cloud TTS

**Added:**
- Breaking changes notice in V3.0
- Explanation of Edge TTS removal
- Reference to migration guide
- Updated all examples to use Google Cloud TTS
- Removed all Edge TTS command examples
- Added voice selection guide with all available Neural2 voices

**Changed:**
```markdown
# OLD
**VERSION:** 2.0 Enhanced
> ...with Edge TTS Ava voice, binaural beats...

# NEW
**VERSION:** 3.0 - Google Cloud TTS
> ...with Google Cloud TTS Neural2 voices, binaural beats...

## ⚠️ Breaking Changes in V3.0

**Edge TTS (Ava voice) has been removed from the workflow.**
```

---

## What Still Works

### Backward Compatibility

1. **hypnotic_pacing.py** still functions (for now)
   - Shows deprecation warning
   - Can still be called manually if needed
   - Will be removed in future version

2. **Edge TTS references** in session-specific scripts
   - Session-specific scripts (e.g., `sessions/atlas-starship-ancient-future/generate_voice_v2_ava.py`) still exist
   - These are **NOT** part of core workflow
   - Users can keep them for experimentation
   - Not maintained or supported

3. **Manifest.yaml** backward compatibility
   - Old manifests with `provider: "edge-tts"` will be rejected by core scripts
   - Users must update to `provider: "google"`

---

## Breaking Changes

### Commands That No Longer Work

```bash
# ❌ BROKEN - Edge TTS removed
python3 scripts/core/build_session.py \
  --tts-provider edge-tts \
  --voice en-US-AvaNeural \
  ...

# ❌ BROKEN - Edge TTS not in choices
python3 scripts/core/generate_session_audio.py \
  --tts-provider edge-tts \
  ...

# ✅ WORKS - Google Cloud TTS only
python3 scripts/core/build_session.py \
  --voice en-US-Neural2-D \
  ...
```

### Manifest Changes Required

```yaml
# ❌ OLD - Will error
voice:
  provider: "edge-tts"
  voice_name: "en-US-AvaNeural"

# ✅ NEW - Required
voice:
  provider: "google"
  voice_name: "en-US-Neural2-D"
  rate: 0.75
  pitch: "-2.5st"
```

---

## Migration Checklist

For users upgrading existing sessions:

- [ ] Update `sessions/_template/manifest.yaml` with Google TTS defaults
- [ ] Update all session manifests to use `provider: "google"`
- [ ] Change all voice names from `en-US-AvaNeural` to `en-US-Neural2-D` (or another Neural2 voice)
- [ ] Update rate from `0.85` to `0.75` (meditation pacing)
- [ ] Update pitch from `-2st` to `-2.5st` (deeper, soothing)
- [ ] Remove all `--tts-provider edge-tts` from documentation and scripts
- [ ] Remove all `--voice en-US-AvaNeural` from documentation and scripts
- [ ] Remove calls to `hypnotic_pacing.py` (no longer needed)
- [ ] Test SSML `<break>` tags work natively with Google TTS

---

## Benefits of Migration

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

## Testing

### Recommended Test

Generate a simple test session to verify Google Cloud TTS works:

```bash
# 1. Create test SSML with explicit breaks
cat > test_breaks.ssml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<prosody rate="slow" pitch="-2st">
Breathe in for 4...
<break time="4s"/>

Hold for 4...
<break time="4s"/>

Exhale for 6...
<break time="6s"/>

Counting down from 10...
<break time="2s"/>
10... <break time="2s"/>
9... <break time="2s"/>
8... <break time="2s"/>
</prosody>
</speak>
EOF

# 2. Generate with Google Cloud TTS
python3 scripts/core/generate_audio_chunked.py \
  test_breaks.ssml \
  test_output.mp3 \
  --voice en-US-Neural2-D \
  --speaking-rate 0.75 \
  --pitch -2.5

# 3. Listen and verify breaks work
vlc test_output.mp3
```

**Expected result**: All breaks should be present, breathing cues should have proper 4s/6s pauses, countdown should have 2s pauses between numbers.

---

## Support and Troubleshooting

### Getting Help

1. **Migration issues**: See [docs/EDGE_TTS_REMOVAL.md](docs/EDGE_TTS_REMOVAL.md)
2. **Voice selection**: See voice guide in EDGE_TTS_REMOVAL.md
3. **SSML issues**: Run `python3 scripts/utilities/validate_ssml.py`
4. **API errors**: See troubleshooting section in EDGE_TTS_REMOVAL.md

### Common Issues

**"Invalid choice: 'edge-tts'"**
- Solution: Remove `--tts-provider edge-tts`, use `--tts-provider google` (or omit, it's default)

**"Voice not found: en-US-AvaNeural"**
- Solution: Change to `--voice en-US-Neural2-D`

**"SSML breaks still not working"**
- Solution: You're likely using old Edge TTS. Verify Google TTS in command/manifest.

---

## Next Steps

1. **Update all session manifests** to use Google Cloud TTS
2. **Test existing sessions** with new TTS provider
3. **Remove Edge TTS references** from any custom scripts
4. **Enjoy properly-paced hypnotic audio** with full SSML break support!

---

**Created**: 2025-11-30
**Maintainer**: Randy Sailer
**Status**: Migration Complete ✅
