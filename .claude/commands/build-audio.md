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

2. **Generate voice audio (CANONICAL METHOD)**
   ```bash
   # ALWAYS use generate_voice.py - it applies production voice + enhancement
   python3 scripts/core/generate_voice.py \
       sessions/{session}/working_files/script.ssml \
       sessions/{session}/output
   ```

   **This automatically:**
   - Uses production voice: `en-US-Neural2-H` (bright female)
   - Speaking rate: 0.88x, Pitch: 0 semitones
   - Applies voice enhancement (warmth, room, whisper, double-voice, subharmonic)
   - Outputs: `voice.mp3`, `voice_enhanced.mp3`, `voice_enhanced.wav`

   **USE `voice_enhanced.mp3` FOR ALL SUBSEQUENT STEPS!**

3. **Generate binaural bed**
   - Match duration to voice_enhanced.mp3
   - Apply section-specific frequencies
   - Generate additional layers (pink noise, etc.)

4. **Generate SFX track** (if markers present)
   ```bash
   python3 scripts/core/sfx_sync.py \
       sessions/{session}/working_files/script_production.ssml \
       sessions/{session}/output/voice_enhanced.wav \
       sessions/{session}/output/sfx_track.wav
   ```

5. **Mix audio** (CRITICAL - Use correct levels!)

   > See Serena memory `audio_production_methodology` for complete details.

   **Standard Mix Levels:**
   | Stem | Level |
   |------|-------|
   | Voice | -6 dB |
   | Binaural | -6 dB |
   | SFX | 0 dB |

   ```bash
   ffmpeg -y \
     -i sessions/{session}/output/voice_enhanced.wav \
     -i sessions/{session}/output/binaural_dynamic.wav \
     -i sessions/{session}/output/sfx_track.wav \
     -filter_complex "
       [0:a]volume=-6dB[voice];
       [1:a]volume=-6dB[bin];
       [2:a]volume=0dB[sfx];
       [voice][bin][sfx]amix=inputs=3:duration=longest:normalize=0[mixed]
     " \
     -map "[mixed]" \
     -acodec pcm_s16le \
     sessions/{session}/output/session_mixed.wav
   ```

6. **Master audio**
   - Normalize to -14 LUFS
   - Apply true peak limiting
   - Final EQ and dynamics

7. **Save outputs**
   - `output/voice.mp3` - Raw TTS (backup)
   - `output/voice_enhanced.mp3` - Enhanced voice (USE THIS)
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
