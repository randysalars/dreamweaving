# Hypnotic Pacing for Edge TTS (Ava Voice)

**VERSION:** 2.0 (Enhanced Intelligence)
**STATUS:** ⚠️ DEPRECATED / ARCHIVED
**LAST UPDATED:** 2025-11-30

---

## ⚠️ DEPRECATION NOTICE

**This module and documentation are DEPRECATED and no longer part of the production workflow.**

Edge TTS has been completely removed from the dreamweaving workflow because:
- **Ignores ALL SSML `<break>` tags** - makes hypnotic pacing impossible
- **Too fast for meditation** - even with post-processing
- **Audio quality issues** - skipping and glitching

**Migration:** Use Google Cloud TTS Neural2 instead, which respects SSML breaks natively.

See **[docs/EDGE_TTS_REMOVAL.md](EDGE_TTS_REMOVAL.md)** for complete migration guide.

This file is kept for historical reference only.

---

## Original Documentation (ARCHIVED)

## Problem

Edge TTS (Microsoft Azure TTS with Ava voice) **ignores SSML `<break>` tags**, resulting in:
- Rushed delivery with no pauses
- Number countdowns that move too quickly
- No time for visualization or processing
- Unsuitable pacing for hypnotic/meditative work

## Solution

**Intelligent Post-Processing** - The `hypnotic_pacing.py` module analyzes your SSML script and automatically inserts strategic pauses into the generated audio based on content type.

---

## V2 Enhancements (What's New)

**Version 2.0 adds intelligent context-awareness** to avoid inappropriate pauses:

### What Was Fixed from V1

**Problem**: V1 paused too frequently, breaking narrative flow
- Paused after EVERY period (even in compound sentences)
- Paused after ANY "feel" or "imagine" keyword (even casual usage)
- Detected incidental numbers as countdowns
- Added pauses in drift sections that already had abundant breaks

**Solution**: V2 uses contextual analysis
- ✅ Only pauses on complete thoughts (filters out compound sentences)
- ✅ Only detects visualization cues at sentence start (not mid-thought)
- ✅ Only recognizes true countdown contexts (explicit "counting down from...")
- ✅ Skips drift zones that already have 3+ consecutive breaks
- ✅ Adds section boundary detection for major narrative transitions

### V2 Intelligence Features

1. **Countdown Context Detection**: Requires explicit "counting down from X to Y" phrasing
2. **Visualization Command Detection**: Only matches sentence-start imperative phrases
3. **Complete Thought Analysis**: Skips list items, compound sentences, mid-thought periods
4. **Drift Zone Exclusion**: Automatically skips areas with many existing breaks
5. **Section Boundary Detection**: Adds longer pauses for major narrative shifts
6. **Deduplication**: If multiple pause types at same position, uses longest duration

### Result

- **83% fewer pauses** than V1 (50 vs 293 for ATLAS session)
- **More natural flow** - pauses only where contextually appropriate
- **Preserves narrative rhythm** - doesn't break compound thoughts
- **Production ready** - suitable for actual hypnotic journey delivery

---

## How It Works

### 1. Script Analysis

The system reads your SSML script and identifies:

**Number Sequences (Countdowns)**
```
"ten... nine... eight... seven..."
"10, 9, 8, 7, 6..."
```
→ **3-second pauses** after each number

**Visualization Cues**
```
"imagine yourself..."
"picture a..."
"notice how..."
"feel the..."
```
→ **4-second pauses** for mental imagery

**Sentence Endings**
```
"...deeper and deeper."
"...completely relaxed..."
```
→ **1.5-second pauses** between sentences

### 2. Audio Insertion

The system:
1. Estimates word timing based on audio duration and word count
2. Maps text positions to audio positions
3. Inserts strategic silences at identified pause points
4. Preserves voice quality (no pitch/speed changes)

### 3. Result

A properly-paced hypnotic audio with:
- ✅ Natural breathing room between phrases
- ✅ Extended pauses during countdowns
- ✅ Time for visualization and processing
- ✅ Original voice quality maintained

---

## Usage

### Standalone (Manual)

```bash
python3 scripts/core/audio/hypnotic_pacing.py \
  sessions/my-session/working_files/voice.mp3 \
  sessions/my-session/script.ssml \
  --output sessions/my-session/working_files/voice_hypnotic.mp3
```

### Automatic (In Workflow)

The hypnotic pacing will be automatically applied when:
1. Using Edge TTS (`--tts-provider edge-tts`)
2. Ava voice specified (`--voice en-US-AvaNeural`)
3. Manifest has `hypnotic_pacing: true` (planned feature)

---

## Pause Durations

| Content Type | Pause Duration | Use Case |
|--------------|----------------|----------|
| Number countdown | 3.0 seconds | Allow relaxation between numbers |
| Visualization cue | 4.0 seconds | Time to form mental imagery |
| Sentence ending | 1.5 seconds | Natural breathing pause |
| Scene transition | 5.0 seconds | Major shift in narrative (planned) |

---

## Examples

### Before (No Pauses)

```
Audio: "Ten nine eight seven six five four three two one deeper and deeper"
Duration: 8 seconds (too fast!)
```

### After (With Hypnotic Pacing)

```
Audio: "Ten... (3s) nine... (3s) eight... (3s) seven... (3s) six... (3s)
        five... (3s) four... (3s) three... (3s) two... (3s) one... (3s)
        deeper and deeper... (1.5s)"
Duration: 38 seconds (properly paced)
```

---

## Detection Patterns (V2 Enhanced Intelligence)

### Countdown Sequences (Context-Aware)

**Only detects TRUE countdown contexts**, not incidental numbers:
- ✅ `"Counting down from ten to one... 10... 9... 8..."`
- ✅ `"With each number you drift deeper... ten... nine... eight..."`
- ❌ `"The 10 principles..."` (not a countdown)
- ❌ `"Section 5... 4... 3..."` (section headers, not induction)

### Visualization Cues (Command-Style Only)

**Only at sentence start** (not casual usage mid-thought):
- ✅ `"Imagine yourself floating..."` (sentence start)
- ✅ `"Picture a beautiful garden..."` (sentence start)
- ❌ `"...and you imagine the stars"` (mid-sentence, casual)
- ❌ `"feel the ship moving"` (not a command)

### Complete Thoughts (Smart Sentence Detection)

**Filters out compound sentences and mid-thought breaks**:
- ✅ `"You are safe. You are held."` (two complete thoughts)
- ❌ `"...part spacecraft, part cathedral, part mind."` (list, not separate thoughts)
- ❌ `"Breathing deeply. Relaxing completely. Drifting down."` (rhythmic sequence)

### Section Boundaries (Major Transitions)

**Detects narrative section shifts**:
- SECTION markers in comments
- Named sections: Pretalk, Induction, Journey, Integration, Awakening
- Major paragraph breaks

### Drift Zones (Exclusion Areas)

**Skips areas that already have many breaks**:
- Extended rest/integration sections with 3+ consecutive breaks
- These already have plenty of silence - no additional pauses needed

---

## Comparison: Strategies

### Intelligent Strategy (Recommended)

```python
strategy='intelligent'
```

**How it works**:
- Analyzes script content
- Identifies specific pause-worthy moments
- Variable pause durations based on context
- Most natural and hypnotic result

**Best for**: Scripted hypnotic journeys with varied content

### Uniform Strategy

```python
strategy='uniform'
```

**How it works**:
- Adds pause every N seconds uniformly
- Fixed 2-second pauses
- No content analysis

**Best for**: Quick testing or simple ambient narration

---

## Integration with Workflow

### Current Status

**Manual Application**:
```bash
# Generate voice without pacing
python3 scripts/core/generate_session_audio.py ...

# Apply pacing separately
python3 scripts/core/audio/hypnotic_pacing.py voice.mp3 script.ssml
```

### Planned Auto-Integration

```yaml
# manifest.yaml
voice:
  provider: "edge-tts"
  voice_name: "en-US-AvaNeural"
  hypnotic_pacing:
    enabled: true
    strategy: "intelligent"
    countdown_pause_s: 3.0
    visualization_pause_s: 4.0
    sentence_pause_s: 1.5
```

Then:
```bash
python3 scripts/core/build_session.py \
  --session sessions/my-session \
  --ssml sessions/my-session/script.ssml \
  --auto-package
```

Will automatically apply hypnotic pacing during audio generation.

---

## Script Writing Tips

### For Best Results

**1. Use Clear Countdown Markers**
```
Good: "ten... nine... eight..."
Good: "10, 9, 8, 7, 6..."
Bad:  "counting from ten to one" (no actual numbers)
```

**2. Include Visualization Cues**
```
Good: "Imagine yourself standing..."
Good: "Picture a beautiful garden..."
Bad:  "You are in a garden" (no visualization trigger)
```

**3. Proper Sentence Structure**
```
Good: "Breathing deeply. Relaxing completely. Drifting down."
Bad:  "Breathing deeply relaxing completely drifting down" (run-on)
```

### SSML Still Useful

Even though `<break>` tags are ignored by Edge TTS, keep them in your SSML:
- Documentation of intended pauses
- Works with other TTS providers (Google Cloud TTS)
- Shows hypnotic_pacing.py where you want extra emphasis

---

## Technical Details

### Word Timing Calculation

```python
ms_per_word = total_audio_duration / total_word_count
audio_position = (text_position / text_length) * word_count * ms_per_word
```

This estimates where in the audio each text position occurs.

### Pause Insertion

```python
# Extract segment before pause point
segment = audio[last_pos:pause_position]

# Add segment to result
result += segment

# Insert silence
silence = AudioSegment.silent(duration=pause_ms)
result += silence
```

Pauses are added as actual silence (not time-stretching).

---

## Limitations

1. **Timing Estimation**: Word timing is approximate based on average speaking rate
2. **No Phrase Detection**: Cannot detect complex multi-word phrases perfectly
3. **No Prosody Analysis**: Doesn't analyze actual speech prosody
4. **Fixed Durations**: Pause lengths are predetermined, not adaptive

### Future Enhancements

- **Speech-to-text alignment**: Use Whisper to get exact word timestamps
- **Adaptive pausing**: Adjust pause length based on sentence complexity
- **Emotional context**: Longer pauses during emotional/profound moments
- **User preferences**: Allow per-session pause customization in manifest

---

## Performance

**Processing Time**: ~5-10 seconds for 30-minute audio
**Memory**: Minimal (audio loaded once)
**Output Quality**: Identical to input (no re-encoding artifacts)

---

## Troubleshooting

### "Pauses are too long"

Adjust durations in the code:
```python
pause_points.append({
    'duration_ms': 2000,  # Reduce from 3000 to 2000
    'reason': 'countdown'
})
```

### "Not detecting my countdowns"

Check format - must be:
- `10, 9, 8` or
- `ten, nine, eight` or
- `10... 9... 8...`

Not: `counting down from ten`

### "Pauses in wrong places"

Try `uniform` strategy for testing:
```bash
python3 scripts/core/audio/hypnotic_pacing.py \
  voice.mp3 script.ssml \
  --strategy uniform
```

---

## Best Practices

1. **Test first**: Apply pacing to a short test script before full session
2. **Listen critically**: Verify pauses feel natural, not mechanical
3. **Adjust as needed**: Modify pause durations for your style
4. **Keep originals**: Save both paced and unpaced versions
5. **Document intent**: Note in manifest which version is final

---

## Example Session: ATLAS (V2 Enhanced)

**Input**:
- Voice: 31.5 minutes of Edge TTS delivery (1887s)
- Script: Cosmic journey with countdowns, visualizations, and drift sections

**Processing**:
```bash
python3 scripts/core/audio/hypnotic_pacing.py \
  working_files/voice_atlas_ava_full.mp3 \
  script.ssml \
  --output working_files/voice_atlas_ava_hypnotic_v2.mp3 \
  --strategy intelligent
```

**Result (V2 Enhanced)**:
- Duration: 31.5 min → 33.4 min (+6.1% with targeted pauses)
- Detected: 50 pause points (intelligently filtered)
  - 10 countdown pauses (true induction countdowns only)
  - 10 section boundary pauses (major narrative transitions)
  - 30 sentence pauses (complete thoughts only, not compound sentences)
- Skipped: All drift zones with existing breaks (no redundant pauses)
- Quality: Original Ava voice preserved perfectly

**Comparison with V1**:
- V1: 293 pause points, +28.5% duration (too many, pausing inappropriately)
- V2: 50 pause points, +6.1% duration (contextually appropriate)
- **83% fewer pauses, much more natural hypnotic flow**

---

**Created**: 2025-11-30
**Maintainer**: Randy Sailer
**Status**: Ready for Testing ✅
