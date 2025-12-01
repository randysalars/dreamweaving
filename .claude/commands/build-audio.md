---
name: build-audio
description: Build audio only for a session
arguments:
  - name: session
    required: true
    description: Session name or path
agent: audio-engineer
---

# /build-audio Command

Build complete audio for a session (voice + binaural + mastering).

## Usage
```
/build-audio <session>
```

## Example
```
/build-audio inner-child-healing
```

## Process

1. **Pre-flight checks**
   - Validate SSML exists and is valid
   - Validate manifest exists
   - Check Google Cloud credentials
   - Verify FFmpeg available

2. **Generate voice audio**
   ```bash
   python3 scripts/core/generate_audio_chunked.py \
       sessions/{session}/working_files/script.ssml \
       sessions/{session}/output/voice.mp3 \
       {voice_from_manifest}
   ```

3. **Generate binaural bed**
   - Match duration to voice
   - Apply section-specific frequencies
   - Generate additional layers (pink noise, etc.)

4. **Mix audio**
   - Combine voice + binaural
   - Apply sidechain ducking
   - Set proper levels

5. **Apply voice enhancement**
   - Warmth, whisper overlay
   - De-essing, breath layers
   - Per manifest settings

6. **Master audio**
   - Normalize to -14 LUFS
   - Apply true peak limiting
   - Final EQ and dynamics

7. **Save outputs**
   - `output/voice.mp3` - Voice only
   - `output/binaural.wav` - Binaural only
   - `output/mixed.mp3` - Mixed stems
   - `output/final.mp3` - Mastered output

## Prerequisites

- `manifest.yaml` must exist
- `working_files/script.ssml` must exist and be valid
- Google Cloud credentials configured
- Virtual environment activated

## Quality Verification

After build:
- Loudness: -14 LUFS (±1)
- True Peak: < -1.5 dBTP
- Duration: Within 30s of target

## Build Time Estimate

| Duration | Voice Gen | Mix/Master | Total |
|----------|-----------|------------|-------|
| 15 min | ~5 min | ~2 min | ~7 min |
| 30 min | ~10 min | ~3 min | ~13 min |
| 45 min | ~15 min | ~4 min | ~19 min |

## Troubleshooting

### API Quota Exceeded
- Wait and retry
- Check billing

### Duration Mismatch
- Adjust speaking rate in manifest
- Regenerate

### Clipping
- Reduce voice LUFS
- Re-master
