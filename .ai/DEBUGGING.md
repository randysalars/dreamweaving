# Dreamweaving Debugging Playbooks

> **Purpose:** Decision trees for the top 10 most common failures. Follow step-by-step.

---

## How to Use This Document

1. **Identify symptom** from the list below
2. **Run checks** in order
3. **Apply fix** for the root cause found
4. **Verify** the fix worked
5. **Prevent** by adding test/gate if needed
6. **Record** in `.ai/memory/` if novel issue

---

## Issue #1: Silent or Inaudible Audio Output

### Symptoms
- Output audio file plays but is silent
- Mixed audio has no waveform
- "Audio plays but I can't hear anything"

### Checks (run in order)
```bash
# 1. Check if input files have audio
ffprobe -v error -show_format sessions/{session}/output/voice_enhanced.mp3
ffprobe -v error -show_format sessions/{session}/output/binaural_dynamic.wav

# 2. Check peak levels
ffmpeg -i sessions/{session}/output/session_mixed.wav \
  -af "volumedetect" -f null /dev/null 2>&1 | grep max_volume

# 3. Verify mixer command used correct levels
# Look for: volume=-6dB for voice/binaural, normalize=0
```

### Root Causes & Fixes

| If You Find | Root Cause | Fix |
|-------------|------------|-----|
| Input files are silent | TTS failed silently | Re-run voice generation |
| max_volume = -inf dB | Wrong file paths in mix | Check paths exist |
| max_volume very low | Levels too low | Use -6dB not -12dB |
| No normalize=0 | amix auto-normalized | Add normalize=0 to filter |

### Prevention
- Always validate audio levels post-mix
- Use the standard mix command from CONVENTIONS.md

---

## Issue #2: TTS Reads "[SFX:..." Aloud

### Symptoms
- Voice says "SFX colon" or reads sound effect descriptions
- Markers appear in audio as spoken text

### Checks
```bash
# Check if SFX markers were stripped
grep -n "\[SFX:" sessions/{session}/working_files/script_voice_clean.ssml

# Should return nothing. If it returns lines, markers weren't stripped.
```

### Root Cause
`script_voice_clean.ssml` still contains `[SFX:...]` markers that should only be in `script_production.ssml`.

### Fix
```bash
# Strip SFX markers from voice script
sed -i 's/\[SFX:[^]]*\]//g' sessions/{session}/working_files/script_voice_clean.ssml

# Or regenerate voice script properly
```

### Prevention
- Always create separate `script_production.ssml` and `script_voice_clean.ssml`
- Add validation check for markers in clean script

---

## Issue #3: Voice Sounds Robotic/Unnatural

### Symptoms
- TTS output sounds mechanical
- Pacing feels unnatural or too slow
- Words are stretched oddly

### Checks
```bash
# Check SSML for slow rates
grep -n 'rate="0\.' sessions/{session}/working_files/script_voice_clean.ssml
```

### Root Cause
Using `rate` values below 1.0 (like 0.85, 0.88) sounds robotic with Neural2 voices.

### Fix
1. Change all `rate="0.XX"` to `rate="1.0"`
2. Add `<break>` tags for pacing instead
3. Re-generate voice

### Prevention
- SSML validation should flag rate < 1.0
- Use breaks, not rate, for hypnotic pacing

---

## Issue #4: Audio Clips/Distorts

### Symptoms
- Crackling or popping in audio
- Waveform shows flat tops (clipping)
- Harsh distortion on loud passages

### Checks
```bash
# Check for clipping (max_volume should be < 0 dB)
ffmpeg -i sessions/{session}/output/session_mixed.wav \
  -af "volumedetect" -f null /dev/null 2>&1 | grep max_volume

# Check true peak
ffmpeg -i sessions/{session}/output/session_mixed.wav \
  -af "loudnorm=print_format=json" -f null /dev/null 2>&1
```

### Root Cause
Stems mixed at 0dB or positive levels, causing peaks above 0dB.

### Fix
1. Re-mix with correct levels: voice -6dB, binaural -6dB
2. Add limiter if needed: `-af "alimiter=limit=0.9"`

### Prevention
- Always use standard stem levels
- Post-mix level validation

---

## Issue #5: SSML Validation Fails

### Symptoms
- `validate_ssml.py` reports errors
- TTS API rejects script
- XML parsing errors

### Checks
```bash
# Run full validation
python3 scripts/utilities/validate_ssml.py sessions/{session}/working_files/script.ssml -v
```

### Common Root Causes

| Error | Cause | Fix |
|-------|-------|-----|
| "unclosed tag" | Missing `</prosody>` or `</speak>` | Close all tags |
| "invalid attribute" | Typo in attribute name | Check spelling |
| "break too long" | `<break time="15s"/>` | Max 10 seconds |
| "unescaped &" | `&` instead of `&amp;` | Escape special chars |

### Prevention
- Run validation before any TTS generation
- Use SSML-aware editor

---

## Issue #6: "Works Locally, Fails on Build"

### Symptoms
- Scripts work in dev, fail in production
- "Module not found" errors
- Different behavior between environments

### Checks
```bash
# Verify venv is activated
which python3  # Should be in venv path

# Check Python version
python3 --version  # Should be 3.8+

# Verify all dependencies
pip list | grep -E "numpy|scipy|pydub|google-cloud"

# Run environment check
python3 scripts/core/check_env.py
```

### Root Causes & Fixes

| If You Find | Root Cause | Fix |
|-------------|------------|-----|
| Wrong python path | venv not activated | `source venv/bin/activate` |
| Missing packages | Dependencies not installed | `pip install -r requirements.txt` |
| Version mismatch | Different Python versions | Use pyenv or venv |

---

## Issue #7: Google Cloud TTS Auth Fails

### Symptoms
- "Could not automatically determine credentials"
- "Permission denied" from TTS API
- 401/403 errors

### Checks
```bash
# Check env var is set
echo $GOOGLE_APPLICATION_CREDENTIALS

# Verify file exists
ls -la $GOOGLE_APPLICATION_CREDENTIALS

# Test auth
gcloud auth application-default print-access-token
```

### Fix
```bash
# Set credentials path
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

# Or authenticate interactively
gcloud auth application-default login
```

### Prevention
- Add to shell profile or .env
- Preflight check validates auth

---

## Issue #8: FFmpeg Not Found or Fails

### Symptoms
- "ffmpeg: command not found"
- "Unknown encoder" errors
- "Invalid option" errors

### Checks
```bash
# Check FFmpeg is installed
which ffmpeg
ffmpeg -version

# Check specific codec
ffmpeg -encoders | grep libx264
ffmpeg -encoders | grep aac
```

### Fix
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# If codecs missing, reinstall with full codecs
sudo apt install ffmpeg libavcodec-extra
```

---

## Issue #9: Session Build Hangs or Times Out

### Symptoms
- Build process stops responding
- No output for >5 minutes
- Partial files created

### Checks
```bash
# Check disk space
df -h /home

# Check for zombie processes
ps aux | grep -E "ffmpeg|python" | grep -v grep

# Check system resources
top -bn1 | head -20
```

### Root Causes

| If You Find | Root Cause | Fix |
|-------------|------------|-----|
| Disk full | No space for temp files | Free space or use different disk |
| FFmpeg stuck | Complex filter graph | Simplify or add timeout |
| API timeout | Network issues | Retry with backoff |

---

## Issue #10: Video/Audio Sync Issues

### Symptoms
- Voice doesn't match video timing
- VTT subtitles are offset
- Audio ends before/after video

### Checks
```bash
# Check audio duration
ffprobe -v error -show_entries format=duration \
  sessions/{session}/output/{session}_MASTER.mp3

# Check video duration
ffprobe -v error -show_entries format=duration \
  sessions/{session}/output/youtube_package/final_video.mp4

# Compare (should be within 0.5s)
```

### Fix
1. If audio shorter: Pad audio or trim video
2. If video shorter: Extend video or trim audio
3. Regenerate VTT from correct audio

---

## Quick Reference: Check Commands

```bash
# Full system diagnostic
python3 scripts/utilities/doctor.py

# Session validation
python3 scripts/utilities/validate_session_structure.py sessions/{session}/

# SSML check
python3 scripts/utilities/validate_ssml.py sessions/{session}/working_files/script.ssml

# Audio levels
ffmpeg -i file.wav -af "volumedetect" -f null /dev/null 2>&1 | grep max_volume

# Environment
python3 scripts/core/check_env.py
```

---

## When to Create a Memory Card

Create `.ai/memory/YYYY-MM-DD__issue-title.md` when:
- Root cause was not in this playbook
- Fix took >30 minutes to discover
- Same issue has occurred twice
- Fix required code changes

See `.ai/memory/TEMPLATE.md` for format.
