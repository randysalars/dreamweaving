# Dreamweaving Terminology Guide

**VERSION:** 1.0
**LAST UPDATED:** 2025-11-28
**PURPOSE:** Standardize terminology across all documentation

---

## Purpose

This guide ensures consistent terminology across all Dreamweaving documentation, reducing confusion and improving clarity.

---

## Standard Terms

### Audio Production

| ✅ USE THIS | ❌ NOT THIS | Definition |
|------------|------------|------------|
| **Voice generation** | Audio generation, TTS generation, speech synthesis | Creating voice audio from SSML script |
| **Mastering** | Post-processing, audio enhancement, normalization | Professional loudness and EQ treatment |
| **Ultimate mix** | Complete mix, enhanced mix, final mix | Voice + binaural + effects + ambient (session-specific) |
| **MASTERED** (filename) | mastered, Mastered, FINAL | Suffix for mastered audio files |

### File Naming Conventions

| ✅ USE THIS | ❌ NOT THIS | Example |
|------------|------------|---------|
| **session_name_MASTERED.wav** | session_name_mastered.wav, session_name_final.wav | `neural_navigator_MASTERED.wav` |
| **session_name_voice.mp3** | session_name_raw.mp3, session_name_tts.mp3 | `garden_eden_voice.mp3` |
| **session_name_ultimate.wav** | session_name_complete.wav, session_name_enhanced.wav | `neural_navigator_ultimate.wav` |

### Workflow Types

| ✅ USE THIS | ❌ NOT THIS | Definition |
|------------|------------|------------|
| **Canonical workflow** | Universal workflow, standard workflow, main workflow | The official production workflow (CANONICAL_WORKFLOW.md) |
| **Session-specific workflow** | Custom workflow, special workflow, alternative workflow | Workflows unique to a particular session |
| **Universal workflow** | Global workflow, general workflow | Workflows that apply to all sessions |

### TTS Providers

| ✅ USE THIS | ❌ NOT THIS | Notes |
|------------|------------|-------|
| **Google Cloud TTS** | Google TTS, Cloud TTS, GCP TTS | Official TTS provider |
| **Edge TTS** | Microsoft TTS, Edge Text-to-Speech | Experimental/session-specific only |

### Voice Specifications

| ✅ USE THIS | ❌ NOT THIS | Example |
|------------|------------|---------|
| **en-US-Neural2-A** | Neural2-A, en-US-A, Google-Neural2-A | Full voice ID format |
| **Speaking rate: 0.85** | Rate: 85%, Speed: 0.85x | Hypnotic pace specification |
| **Pitch: -2.0 semitones** | Pitch: -2st, Pitch: -2 | Pitch specification format |

### Session Components

| ✅ USE THIS | ❌ NOT THIS | Definition |
|------------|------------|------------|
| **Pre-talk** | Pretalk, Pre talk, Introduction | Opening section (2-3 min) |
| **Induction** | Intro, Opening, Start | Hypnotic induction (5-6 min) |
| **Main journey** | Core, Middle section, Body | Main hypnotic content (12-20 min) |
| **Awakening** | Closing, Return, Ending | Return to awareness (2-3 min) |
| **Post-hypnotic suggestions** | Anchors section, Closing suggestions | Post-hypnotic anchors (2-3 min) |

### Audio Specifications

| ✅ USE THIS | ❌ NOT THIS | Value |
|------------|------------|-------|
| **-14 LUFS** | -14dB, -14 loudness, -14 LU | YouTube standard loudness |
| **48 kHz** | 48000 Hz, 48khz, 48KHZ | Sample rate |
| **24-bit** | 24bit, 24 bit | Bit depth |
| **WAV** | wav, .wav, Wave | Uncompressed format (uppercase) |
| **MP3** | mp3, .mp3 | Compressed format (uppercase) |

### Video Specifications

| ✅ USE THIS | ❌ NOT THIS | Value |
|------------|------------|-------|
| **1920x1080** | 1080p, Full HD, 1920×1080 | Resolution format |
| **30 fps** | 30FPS, 30 frames/sec | Frame rate |
| **H.264** | h264, x264, H264 | Video codec |
| **AAC** | aac, Advanced Audio Coding | Audio codec |

### Status Labels

| ✅ USE THIS | ❌ NOT THIS | Meaning |
|------------|------------|---------|
| **✅ Current and Valid** | Active, Up to date, Current | Document is current |
| **⚠️ DEPRECATED** | Old, Outdated, Archived | Do not use |
| **🔮 Future Vision** | Planned, Roadmap, Todo | Not yet implemented |
| **✅ Production Ready** | Ready, Complete, Finished | Ready for use |

### Directory Names

| ✅ USE THIS | ❌ NOT THIS | Purpose |
|------------|------------|---------|
| **working_files/** | work/, tmp/, temp/ | Session working directory |
| **output/** | out/, exports/, renders/ | Generated output files |
| **images/** | imgs/, pictures/, visuals/ | Session images |
| **final_export/** | final/, export/, deliverables/ | Final production files |

---

## Capitalization Rules

### Document Titles

**Use Title Case for main headings:**
- ✅ "Neural Network Navigator: Production Manual"
- ❌ "neural network navigator: production manual"

### File Extensions

**Always uppercase in documentation:**
- ✅ MP3, WAV, SSML, JSON
- ❌ mp3, wav, ssml, json

### Command Examples

**Keep commands as-is (case-sensitive):**
```bash
# Correct - preserve exact case
python3 scripts/core/generate_audio_chunked.py

# Don't change to:
Python3 Scripts/Core/Generate_Audio_Chunked.py
```

### Status Messages

**Use emoji + uppercase for emphasis:**
- ✅ "✅ COMPLETE"
- ✅ "⚠️ DEPRECATED"
- ✅ "🔮 FUTURE VISION"

---

## Measurement Units

### Time Specifications

| ✅ USE THIS | ❌ NOT THIS | Example |
|------------|------------|---------|
| **23:41 (1421 seconds)** | 23m 41s, 23.68 minutes | Always show both formats |
| **2-3 minutes** | 2-3 min, 120-180 sec | Range format for estimates |

### File Sizes

| ✅ USE THIS | ❌ NOT THIS | Example |
|------------|------------|---------|
| **26 MB** | 26MB, 26 mb, 26M | Space between number and unit |
| **~500-800 MB** | 500-800MB, ~500MB-800MB | Range with tilde for estimates |

### Frequency Specifications

| ✅ USE THIS | ❌ NOT THIS | Example |
|------------|------------|---------|
| **10 Hz** | 10hz, 10HZ, 10 hertz | Space between number and unit |
| **Alpha (8-13 Hz)** | Alpha 8-13Hz, Alpha: 8-13 Hz | Format for brainwave states |

---

## Phrase Standardization

### Common Phrases

| ✅ USE THIS | ❌ AVOID |
|------------|---------|
| "Follow the canonical workflow" | "Use the standard process" |
| "Session-specific enhancements" | "Custom features" |
| "Google Cloud TTS" | "Google voice API" |
| "Generate voice audio" | "Create the voice" |
| "Apply mastering" | "Master the audio" |
| "Ultimate mix" (session-specific) | "Final mix" (ambiguous) |

### Action Verbs

| Task | ✅ USE THIS | ❌ NOT THIS |
|------|------------|------------|
| Creating voice | "Generate voice" | "Create voice", "Make audio" |
| Audio processing | "Apply mastering" | "Process audio", "Enhance" |
| Video creation | "Render video" | "Make video", "Build video" |
| File verification | "Validate SSML" | "Check SSML", "Verify script" |

---

## Documentation Structure

### Version Headers

**Standard format for all session-specific docs:**
```markdown
# Document Title

**VERSION:** X.Y (Session-Specific)
**LAST UPDATED:** YYYY-MM-DD
**SESSION DURATION:** XX minutes (XXXX seconds)
**STATUS:** ✅ Current and Valid

> **📖 For universal workflow:** See [../../docs/CANONICAL_WORKFLOW.md](...)
> This document covers **session-specific** [description].

---
```

### Deprecation Notices

**Standard format:**
```markdown
# ⚠️ DEPRECATED: Document Title

> **⚠️ THIS DOCUMENT IS DEPRECATED**
>
> **USE INSTEAD:** [docs/CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md)
>
> [Reason for deprecation]
>
> **Last Updated:** YYYY-MM-DD (Marked as deprecated)

---
```

---

## Command Format Standards

### Python Commands

**Always use python3 explicitly:**
```bash
# ✅ Correct
python3 scripts/core/generate_audio_chunked.py input.ssml output.mp3 en-US-Neural2-A

# ❌ Avoid
python scripts/core/generate_audio_chunked.py input.ssml output.mp3
```

### FFmpeg Commands

**Use long-form flags for clarity:**
```bash
# ✅ Correct (readable)
ffmpeg -i input.mp3 -af loudnorm=I=-14:TP=-1.5 output.wav

# ❌ Avoid (obscure)
ffmpeg -i input.mp3 -af loudnorm=I=-14:TP=-1.5 output.wav  # Actually this is fine
```

### File Paths

**Use relative paths from project root:**
```bash
# ✅ Correct
sessions/my-session/output/audio.mp3

# ❌ Avoid
/home/user/Projects/dreamweaving/sessions/my-session/output/audio.mp3
```

---

## Acronyms and Abbreviations

### Standard Acronyms

| Acronym | Full Form | Usage |
|---------|-----------|-------|
| **TTS** | Text-to-Speech | Google Cloud TTS, Edge TTS |
| **SSML** | Speech Synthesis Markup Language | SSML script, SSML validation |
| **LUFS** | Loudness Units relative to Full Scale | -14 LUFS target |
| **FFmpeg** | Fast Forward Moving Picture Experts Group | FFmpeg command |
| **WAV** | Waveform Audio File Format | WAV file, 24-bit WAV |
| **MP3** | MPEG Audio Layer 3 | MP3 output, 320 kbps MP3 |

### When to Spell Out

**First use in document:**
- ✅ "Text-to-Speech (TTS) provider"
- ✅ "Speech Synthesis Markup Language (SSML)"

**Subsequent uses:**
- ✅ "TTS generation"
- ✅ "SSML validation"

---

## Voice and Tone

### Documentation Voice

**Use second person ("you") for instructions:**
- ✅ "Run the command to generate voice audio"
- ❌ "The user should run the command"

**Use active voice:**
- ✅ "Generate voice using Google Cloud TTS"
- ❌ "Voice is generated using Google Cloud TTS"

**Be direct and concise:**
- ✅ "Follow the canonical workflow"
- ❌ "It is recommended that you consider following the canonical workflow"

### Command Descriptions

**Use imperative mood:**
```bash
# ✅ Correct
# Generate voice from SSML
python3 generate_audio_chunked.py ...

# ❌ Avoid
# This will generate voice from SSML
# You can generate voice from SSML
```

---

## Examples and Templates

### Command Block Format

```bash
# [Brief description of what this does]
command --flag value \
    --another-flag value \
    output-file

# What it produces:
# - output-file.ext (size, duration)
```

### Version History Format

```markdown
### Version X.Y (YYYY-MM-DD)
- ✅ Added: [feature]
- 🔧 Changed: [change]
- 🐛 Fixed: [fix]
- ⚠️ Deprecated: [item]
```

---

## Migration from Old Terms

| Old Term | New Standard Term | Migration Note |
|----------|------------------|----------------|
| "Audio generation" | "Voice generation" | When referring to TTS from SSML |
| "Complete mix" | "Ultimate mix" | Session-specific only |
| "Final audio" | "[session]_MASTERED.wav" | Use specific filename format |
| "Standard workflow" | "Canonical workflow" | Emphasizes authority |
| "Custom workflow" | "Session-specific workflow" | Clarifies scope |

---

## Enforcement

### Documentation Reviews

When reviewing documentation:
1. Check terminology against this guide
2. Verify file naming conventions
3. Ensure consistent capitalization
4. Validate command formats
5. Confirm version headers present

### Automated Checks (Future)

Potential automation:
- Terminology linter
- File naming validator
- Command format checker
- Version header validator

---

## Updates to This Guide

**When to update:**
- New terms emerge in practice
- Inconsistencies discovered
- Community feedback received
- New workflows added

**How to update:**
1. Propose change in WORKFLOW_MAINTENANCE_GUIDE.md
2. Verify change doesn't conflict
3. Update this guide
4. Update affected documentation
5. Increment version number

---

**Last Updated:** 2025-11-28
**Version:** 1.0
**Next Review:** 2026-11-28

---

*Consistent terminology reduces confusion and improves workflow reliability.*
