# Dreamweaving Canonical Production Workflow

**VERSION:** 1.0
**LAST UPDATED:** 2025-11-28
**STATUS:** ✅ OFFICIAL CANONICAL WORKFLOW

> ⚠️ **IMPORTANT:** This is the **ONLY** authoritative workflow document.
> All other workflow documents are deprecated or session-specific variations.
> If you find conflicting instructions elsewhere, follow THIS document.

---

## Table of Contents

1. [Quick Start (5 Minutes)](#quick-start-5-minutes)
2. [Complete Production Pipeline](#complete-production-pipeline)
3. [Standard Workflow Steps](#standard-workflow-steps)
4. [Voice Generation (OFFICIAL METHOD)](#voice-generation-official-method)
5. [Audio Mastering](#audio-mastering)
6. [Video Production](#video-production)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start (5 Minutes)

### Prerequisites Check (AUTOMATED)

**⚡ NEW: Automated Pre-Flight Check**
```bash
# Check everything automatically
./scripts/utilities/preflight_check.sh

# Check and auto-fix issues
./scripts/utilities/preflight_check.sh --fix
```

This checks:
- ✓ Python 3.8+ virtual environment
- ✓ Google Cloud authentication
- ✓ FFmpeg installation
- ✓ Required Python packages
- ✓ Disk space
- ✓ Directory structure
- ✓ File permissions

**Manual Prerequisites Check:**
```bash
# Activate environment
cd ~/Projects/dreamweaving
source venv/bin/activate

# Verify prerequisites
python3 scripts/core/check_env.py  # Comprehensive environment check
python3 scripts/core/check_env.py --fix  # Auto-fix issues
```

### Create and Generate a Session

```bash
# 1. Create new session
./scripts/utilities/create_new_session.sh "my-session"

# 2. Edit the script (use a template or write your own)
code sessions/my-session/script.ssml

# 3. Validate SSML (AUTOMATED)
python3 scripts/utilities/validate_ssml_enhanced.py sessions/my-session/script.ssml --fix

# 4. Generate audio
python3 scripts/core/generate_audio_chunked.py \
    sessions/my-session/script.ssml \
    sessions/my-session/output/audio.mp3 \
    en-US-Neural2-A

# 5. Listen and verify
vlc sessions/my-session/output/audio.mp3
```

**Done!** You now have a complete hypnotic audio session.

---

## Complete Production Pipeline

### Overview

```
1. SSML Script → 2. Voice Generation → 3. Audio Mastering → 4. Video Production
     (Manual)      (Google Cloud TTS)     (FFmpeg)            (Optional)
```

### Production Timeline

| Phase | Duration | Tool |
|-------|----------|------|
| Script writing | 2-4 hours | Text editor |
| Voice generation | 2-5 minutes | Google Cloud TTS |
| Audio mastering | 30 seconds | FFmpeg |
| Video production | 15-25 minutes | FFmpeg (optional) |

---

## Standard Workflow Steps

### Step 1: Create Session Structure

```bash
./scripts/utilities/create_new_session.sh "session-name"
```

**Creates:**
```
sessions/session-name/
├── script.ssml          # Your SSML script
├── notes.md             # Session notes
└── output/              # Generated audio files
```

### Step 2: Write SSML Script

Use the hypnotic script template structure:
1. Pre-talk (2-3 minutes)
2. Induction (5-6 minutes)
3. Main journey (12-20 minutes)
4. Awakening (2-3 minutes)
5. Post-hypnotic suggestions (optional, 2-3 minutes)

**Template location:** `templates/base/hypnosis_template.ssml`

**SSML Guidelines:**
- Use `<break time="3s"/>` for pauses
- Use `<prosody rate="0.85" pitch="-2st">` for hypnotic sections
- Use `<emphasis level="strong">` for key suggestions
- Validate before generation (see below)

### Step 3: Validate SSML (CRITICAL)

```bash
python3 scripts/utilities/validate_ssml.py sessions/session-name/script.ssml
```

**Fix any errors before proceeding!**

---

## Voice Generation (OFFICIAL METHOD)

### ✅ CANONICAL: Google Cloud Text-to-Speech

**This is the ONLY officially supported voice generation method.**

#### Command

```bash
python3 scripts/core/generate_audio_chunked.py \
    INPUT_SSML \
    OUTPUT_MP3 \
    [VOICE_NAME]
```

#### Example

```bash
python3 scripts/core/generate_audio_chunked.py \
    sessions/my-session/script.ssml \
    sessions/my-session/output/voice.mp3 \
    en-US-Neural2-D
```

#### Recommended Voices

**Female:**
- `en-US-Neural2-A` ⭐ Default - Warm, calming
- `en-US-Neural2-C` - Soft, nurturing
- `en-US-Neural2-E` - Deeper, relaxing
- `en-US-Neural2-F` - Clear, serene

**Male:**
- `en-US-Neural2-D` - Deep, resonant
- `en-US-Neural2-I` - Warm, compassionate
- `en-US-Neural2-J` - Rich, mature

#### Voice Generation Settings

**Built-in optimizations:**
- Speaking rate: 0.85 (hypnotic pace)
- Pitch: -2.0 semitones (calming)
- Sample rate: 24 kHz
- Format: MP3, optimized for headphones

#### Output

- File: As specified in OUTPUT_MP3 parameter
- Duration: Matches your script
- Quality: Production-ready

### ⚠️ Alternative Methods (NOT OFFICIALLY SUPPORTED)

**Edge TTS** is used in some session-specific scripts but is NOT part of the canonical workflow:
- `sessions/*/generate_voice_v2_ava.py` - Session-specific only
- Not maintained as core workflow
- Use for experimentation only

**Professional voice actors:** Always an option for premium productions, but outside the scope of automated workflow.

---

## Audio Mastering

### Standard Mastering Process

After voice generation, apply professional mastering for broadcast-ready audio.

#### Command

```bash
ffmpeg -i INPUT_VOICE.mp3 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11,\
       equalizer=f=250:t=h:width=200:g=1.5,\
       equalizer=f=3000:t=h:width=2000:g=1.0,\
       highshelf=f=10000:g=-0.5,\
       alimiter=limit=0.9:attack=5:release=50" \
  -c:a pcm_s24le -ar 48000 \
  OUTPUT_MASTERED.wav
```

#### Example

```bash
ffmpeg -i sessions/my-session/output/voice.mp3 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11,\
       equalizer=f=250:t=h:width=200:g=1.5,\
       equalizer=f=3000:t=h:width=2000:g=1.0,\
       highshelf=f=10000:g=-0.5,\
       alimiter=limit=0.9:attack=5:release=50" \
  -c:a pcm_s24le -ar 48000 \
  sessions/my-session/output/voice_MASTERED.wav
```

#### Mastering Specifications

- **Target loudness:** -14 LUFS (YouTube standard)
- **True peak:** < -1.5 dBTP
- **EQ:** Warmth boost (+1.5 dB @ 250 Hz), Presence (+1.0 dB @ 3 kHz)
- **Format:** 24-bit WAV, 48 kHz

#### Verification

```bash
# Check loudness
ffmpeg -i sessions/my-session/output/voice_MASTERED.wav \
  -af loudnorm=print_format=summary -f null - 2>&1 | grep "Input Integrated"
```

Should show approximately -14 LUFS.

---

## Video Production

### Overview

Video production is **optional** but recommended for YouTube distribution.

### Step 1: Generate Video Images (REQUIRED)

Before assembling video, generate all supporting imagery:

```bash
# Generate ALL video images for a session (recommended)
python3 scripts/core/generate_video_images.py sessions/session-name/ --all

# Or generate specific types
python3 scripts/core/generate_video_images.py sessions/session-name/ \
    --title-card --section-slides --outro --social-preview
```

**This generates:**
| Image Type | Dimensions | Purpose |
|------------|------------|---------|
| Title Card | 1920×1080 | Video intro screen (5-10 sec) |
| Section Slides | 1920×1080 | Chapter transitions |
| Outro | 1920×1080 | End screen with CTA zones |
| Lower Thirds | 1920×1080 | Transparent overlay bars |
| Chapter Markers | 1920×1080 | Numbered chapter cards |
| Social Preview | 1080×1080 | Instagram/social sharing |
| Scene Backgrounds | 1920×1080 | Base images for video |

**Output location:** `sessions/session-name/output/video_images/`

**Color palettes available:**
- `sacred_light` - Gold/cream on cosmic dark (default)
- `cosmic_journey` - Purple/blue on deep space
- `garden_eden` - Emerald/gold on forest shadow
- `ancient_temple` - Antique gold on temple shadow
- `neural_network` - Cyan/purple on digital void
- `volcanic_forge` - Red-gold on volcanic shadow
- `celestial_blue` - Royal blue on night sky

### Step 2: Generate Thumbnail

```bash
python3 scripts/core/generate_thumbnail.py sessions/session-name/ \
    --palette sacred_light
```

### Step 3: Prepare Scene Images

For sessions with still images:

```bash
# 1. Prepare images (1920x1080, one per section)
# Place in: sessions/session-name/images/uploaded/

# 2. Or use generated scene backgrounds
# Located in: sessions/session-name/output/video_images/backgrounds/
```

### Step 4: Assemble Video

```bash
# Use session-specific video script
# See session README for video creation commands
```

### Standard Video Specifications

- **Resolution:** 1920x1080 (Full HD)
- **Frame rate:** 30 fps
- **Video codec:** H.264 (libx264)
- **Audio codec:** AAC, 192-256 kbps
- **Duration:** Match audio exactly

### Session-Specific Video Scripts

Video workflows are **session-specific** because each session has:
- Different scene counts
- Different timings
- Different image styles
- Different visual transitions

**Location of video scripts:**
- `sessions/session-name/create_final_video*.sh`
- `sessions/session-name/composite_*.py`

**Refer to session-specific documentation:**
- `sessions/session-name/PRODUCTION_WORKFLOW.md`
- `sessions/session-name/README_VIDEO.md`

---

## Advanced: Enhanced Audio Production

### Ultimate Audio Mix (Optional)

For sessions requiring binaural beats, ambient pads, and sound effects.

**This is SESSION-SPECIFIC.** There is no universal "ultimate mix" script.

#### Available Enhanced Workflows

1. **Neural Network Navigator:**
   - Script: `sessions/neural-network-navigator/create_ultimate_audio.sh`
   - Features: 9-layer mix, dynamic binaural, gamma burst
   - Duration: 23:41

2. **Garden of Eden:**
   - Script: `sessions/garden-of-eden/create_ultimate_audio.sh`
   - Features: Voice + binaural + nature sounds
   - Duration: ~25 minutes

#### Creating Your Own Enhanced Mix

1. Generate voice (standard workflow)
2. Generate binaural beats using `scripts/core/generate_binaural.py`
3. Generate pink noise using `scripts/core/generate_pink_noise.py`
4. Mix using FFmpeg with `amix` filter
5. Refer to session-specific scripts for examples

---

## Troubleshooting

### ⚡ NEW: Automated Troubleshooting

**Complete diagnostic and auto-fix:**
```bash
# Run all checks and auto-fix issues
./scripts/utilities/preflight_check.sh --fix

# Or check individual components:
python3 scripts/core/check_env.py --fix  # Environment
python3 scripts/utilities/validate_ssml_enhanced.py FILE --fix  # SSML
```

**📚 See comprehensive guide:** [docs/TROUBLESHOOTING_AUTOMATED.md](TROUBLESHOOTING_AUTOMATED.md)

---

### Voice Generation Fails

**Error: "google-cloud-texttospeech not installed"**

```bash
# Auto-fix
python3 scripts/core/check_env.py --fix

# Or manual
pip install google-cloud-texttospeech pydub mutagen tqdm
```

**Error: "Google Cloud authentication failed"**

```bash
# Diagnostic
python3 scripts/core/check_env.py

# Fix
gcloud auth application-default login
```

**Error: "Invalid SSML"**

```bash
# Validate and auto-fix
python3 scripts/utilities/validate_ssml_enhanced.py sessions/session-name/script.ssml --fix
```

### Audio Quality Issues

**Voice sounds robotic:**
- This is expected with TTS - it's a limitation of the technology
- Use slower rate and lower pitch in SSML for more natural sound
- Consider professional voice actor for premium productions

**Audio too quiet or too loud:**
- Re-run mastering with adjusted `-14` LUFS target
- Use `-16` for quieter, `-12` for louder (YouTube standard is -14)

**Clipping or distortion:**
- Check that true peak is below -1.5 dBTP
- Reduce volume in mastering stage
- Check source audio for pre-existing distortion

### SSML Validation Errors

**Common issues:**
- Unclosed tags: Every `<tag>` needs `</tag>`
- Invalid attributes: Check Google Cloud TTS documentation for supported SSML
- Encoding issues: File must be UTF-8

**Fix:**
```bash
# Convert to UTF-8 if needed
iconv -f ISO-8859-1 -t UTF-8 script.ssml > script_utf8.ssml
```

---

## Related Documentation

### Core Documentation (Read These)
- [README.md](../README.md) - Project overview
- [QUICK_START.md](QUICK_START.md) - 5-minute quick start
- [WORKFLOW_DECISION_TREE.md](WORKFLOW_DECISION_TREE.md) - **Which workflow should I use?**
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions

### Reference Documentation
- [TERMINOLOGY_GUIDE.md](TERMINOLOGY_GUIDE.md) - Standard terminology and naming
- [WORKFLOW_MAINTENANCE_GUIDE.md](WORKFLOW_MAINTENANCE_GUIDE.md) - How to maintain workflows
- [Voice configuration](../config/voice_profiles.json) - Voice settings
- [SSML templates](../templates/base/) - Script templates
- [Hypnotic script guide](../prompts/hypnotic_dreamweaving_instructions.md) - Writing guidelines

### Session-Specific Documentation
- Neural Network Navigator: `sessions/neural-network-navigator/PRODUCTION_WORKFLOW.md`
- Garden of Eden: `sessions/garden-of-eden/AUDIO_PRODUCTION_README.md`

### Deprecated Documentation (DO NOT USE)
- ~~`docs/AUDIO_VIDEO_WORKFLOW.md`~~ - Replaced by this document
- ~~`docs/VOICE_WORKFLOW.md`~~ - Replaced by this document
- ~~`docs/SESSION_AUTOMATION_PLAN.md`~~ - Future vision, not current workflow

---

## Version History

### Version 1.0 (2025-11-28)
- ✅ Established as canonical workflow
- ✅ Unified voice generation (Google Cloud TTS only)
- ✅ Standardized mastering process
- ✅ Clarified session-specific vs. universal workflows
- ✅ Deprecated conflicting documentation

---

## Decision Log

**Why Google Cloud TTS as canonical?**
- Core script (`scripts/core/generate_audio_chunked.py`) uses Google Cloud TTS
- Well-documented and supported
- High-quality Neural2 voices
- Consistent results
- Already configured in existing setup

**Why not Edge TTS?**
- Edge TTS used only in session-specific experimental scripts
- Not part of core workflow
- Less documentation
- Mixing two TTS providers creates confusion

**Why session-specific video workflows?**
- Each session has unique:
  - Scene count and timing
  - Image styles and transitions
  - Audio duration and structure
- Universal video script would be too complex and error-prone
- Better to have clear, tested, session-specific examples

---

**Questions or Issues?**

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Verify you're using THIS document (CANONICAL_WORKFLOW.md)
3. Check session-specific docs for session-specific features

---

*This is the official canonical workflow. Last updated: 2025-11-28.*
