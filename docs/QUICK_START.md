# 🚀 Quick Start Guide - 5 Minutes to Your First Session

Get your first hypnotic audio session generated in 5 minutes flat.

> **📖 For complete workflow details:** See [CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md)

---

## Prerequisites Check (30 seconds)

Make sure you have:
- ✅ Python 3.8+ installed
- ✅ FFmpeg installed (`sudo apt install ffmpeg`)
- ✅ Google Cloud authentication configured
- ✅ Virtual environment activated

**Quick verify:**
```bash
python3 --version
ffmpeg -version
gcloud auth application-default print-access-token
which python3  # Should show venv path
```

---

## Step 1: Navigate and Activate (15 seconds)

```bash
cd ~/Projects/dreamweaving
source venv/bin/activate
# You should see (venv) in your prompt
```

**Shortcut:** Use the activation script:
```bash
cd ~/Projects/dreamweaving
./activate.sh
```

---

## Step 2: Create Your Session (30 seconds)

```bash
./scripts/utilities/create_new_session.sh "my-first-session"
```

This creates:
```
sessions/my-first-session/
├── script.ssml
├── notes.md
└── output/
```

---

## Step 3: Write Your Script (2 minutes)

**Option A: Use a Template (Fastest)**

```bash
# Copy a pre-made theme template
cp templates/themes/confidence_building.ssml \
   sessions/my-first-session/script.ssml
```

**Option B: Edit the Default Template**

```bash
# Open the auto-generated template
code sessions/my-first-session/script.ssml
```

**Option C: Start from Scratch**

1. Review the master prompt:
   ```bash
   cat prompts/hypnotic_dreamweaving_instructions.md
   ```

2. Use the base template as a guide:
   ```bash
   cat templates/base/hypnosis_template.ssml
   ```

**Quick Tip:** For your first session, just copy a theme template from `templates/themes/` - you can customize it later!

---

## Step 4: Generate Audio (2 minutes)

```bash
python3 scripts/core/generate_audio_chunked.py \
    sessions/my-first-session/script.ssml \
    sessions/my-first-session/output/audio.mp3 \
    en-US-Neural2-A
```

**What happens:**
- Script splits into chunks (under 5000 bytes each)
- Each chunk synthesized via Google TTS
- Chunks automatically merged into single MP3
- Progress bar shows generation status
- Output saved to `sessions/my-first-session/output/audio.mp3`

**Expected output:**
```
====================================================================
   Dreamweaving Audio Generator - Chunked Processing
====================================================================
✓ Loaded SSML (12,450 bytes)
✓ Split into 3 chunks
✓ Generated chunk 1/3 (4,200 bytes)
✓ Generated chunk 2/3 (4,100 bytes)
✓ Generated chunk 3/3 (4,150 bytes)
✓ Merged audio segments
✓ Output: sessions/my-first-session/output/audio.mp3 (27:34)
====================================================================
```

---

## Step 5: Listen and Refine (30 seconds)

```bash
# Play the audio (Linux)
vlc sessions/my-first-session/output/audio.mp3

# Or open in file manager
xdg-open sessions/my-first-session/output/
```

**Listen for:**
- Pacing and timing (too fast/slow?)
- Pronunciation issues
- Pause lengths (too long/short?)
- Overall flow and coherence

**Need adjustments?**
1. Edit `sessions/my-first-session/script.ssml`
2. Regenerate: `python3 scripts/core/generate_audio_chunked.py ...`
3. Listen again

---

## 🔍 Component Validation (Ava + Binaural + SFX)

Before long renders, run the short smoke test to ensure the core stack is healthy:
```bash
./tests/audio_component_smoke.sh
```
Outputs appear in `test_output/`:
- `voice_smoke.mp3` (Ava voice, 6 Hz bed, SFX at 2s)
- `binaural_smoke.wav` (10s, 6 Hz beat)
- `output/audio_summary.json` (confirms `tts_provider: edge-tts` and SFX metadata)

Success criteria: files render without errors; Ava voice is audible, a 6 Hz pulse is present, and the SFX is audible near 2 seconds.

---

## 🎯 You Did It!

You now have:
- ✅ A complete hypnosis session structure
- ✅ Professional audio generated via Google TTS
- ✅ A reusable workflow for future sessions

---

## Next Steps

### Customize Your Voice

Try different voices:
```bash
# Deep male voice
python3 scripts/core/generate_audio_chunked.py \
    sessions/my-first-session/script.ssml \
    sessions/my-first-session/output/audio_male.mp3 \
    en-US-Neural2-D

# Soft female voice
python3 scripts/core/generate_audio_chunked.py \
    sessions/my-first-session/script.ssml \
    sessions/my-first-session/output/audio_soft.mp3 \
    en-US-Neural2-C
```

See all voices: `config/voice_profiles.json`

### Create More Sessions

```bash
# Healing session
./scripts/utilities/create_new_session.sh "inner-child-healing"
cp templates/themes/healing_journey.ssml \
   sessions/inner-child-healing/script.ssml

# Abundance session
./scripts/utilities/create_new_session.sh "wealth-activation"
cp templates/themes/abundance_activation.ssml \
   sessions/wealth-activation/script.ssml
```

### Learn Advanced Techniques

- **SSML Formatting:** [docs/SSML_REFERENCE.md](SSML_REFERENCE.md)
- **Complete Workflow:** [docs/CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md)
- **Master Prompt:** `prompts/hypnotic_dreamweaving_instructions.md`

---

## Common Quick Fixes

### Audio Too Fast
Edit SSML, change rate:
```xml
<prosody rate="x-slow" pitch="-3st">
```

### Pauses Too Short
Add longer breaks:
```xml
<break time="3s"/>
```

### Word Mispronounced
Use phoneme tag:
```xml
<phoneme alphabet="ipa" ph="pæθ ˈwɝkɪŋ">path-working</phoneme>
```

### Chunk Too Large Error
Add more `<break>` tags throughout your script to create natural split points.

---

## ⚡ Super Quick Reference

**Activate environment:**
```bash
cd ~/Projects/dreamweaving && source venv/bin/activate
```

**Create session:**
```bash
./scripts/utilities/create_new_session.sh "session-name"
```

**Generate audio:**
```bash
python3 scripts/core/generate_audio_chunked.py INPUT.ssml OUTPUT.mp3 VOICE_NAME
```

**Example voices:**
- `en-US-Neural2-A` (default warm female)
- `en-US-Neural2-D` (deep male)
- `en-US-Neural2-C` (soft female)

**Find templates:**
```bash
ls templates/themes/
ls templates/components/
```

---

## Getting Help

**Problems?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Questions?** Check [INDEX.md](INDEX.md) for complete navigation

**Want details?** Read [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)

---

*Ready to create transformational audio? You've got this!* 🌿

[← Back to Index](INDEX.md) | [Full Workflow Guide →](WORKFLOW_GUIDE.md)
