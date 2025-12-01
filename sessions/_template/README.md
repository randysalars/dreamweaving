# Session Template

**VERSION:** 1.0 (Template)
**LAST UPDATED:** 2025-11-28
**STATUS:** ✅ Template - Do Not Modify Directly

> **📖 For universal workflow:** See [../../docs/CANONICAL_WORKFLOW.md](../../docs/CANONICAL_WORKFLOW.md)

---

This directory serves as the template for all generated Dreamweaving sessions.

## Structure

```
_template/
├── manifest.yaml           # Session configuration (copied and populated)
├── working_files/          # Intermediate files
│   ├── stems/             # Individual audio layers
│   ├── voice.wav          # Generated TTS voice
│   └── *.ssml             # SSML scripts
├── output/                 # Final audio outputs
│   ├── *_master.wav       # Mastered 24-bit WAV
│   └── *_master.mp3       # Distribution MP3
├── images/                 # Generated visuals
│   └── *.png              # Scene images
└── final_export/           # Complete deliverables
    ├── *.mp4              # Final video
    └── *.srt              # Subtitles
```

## Usage

This template is automatically copied by `generate_session.py` when creating a new session.

**Do not modify this directory directly.** It serves as the scaffold for new sessions.
