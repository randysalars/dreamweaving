# Dreamweaving Project Context

> **Purpose:** Single-page repo map for AI assistants (Claude, Codex). Keep under 200 lines.

---

## What This Project Is

**Sacred Digital Dreamweaver** - An AI-powered system for producing hypnotic audio/video journeys.

**Core Flow:**
```
Topic → Manifest → SSML Script → Voice (TTS) → Audio Mix → Video → YouTube Package
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.8+ |
| Voice | Google Cloud TTS (Neural2-H default) |
| Audio | FFmpeg, scipy, numpy |
| Video | FFmpeg (H.264 + AAC) |
| Config | YAML manifests, JSON schemas |
| Scripts | SSML format |
| Images | Stable Diffusion (local), Midjourney (manual) |
| Knowledge | YAML files, Serena memories |

---

## Key Directories

```
dreamweaving/
├── .ai/                    # AI context docs (YOU ARE HERE)
│   ├── CONTEXT.md          # This file - repo map
│   ├── CONVENTIONS.md      # Coding standards
│   ├── DEBUGGING.md        # Failure playbooks
│   ├── RUBRIC.md           # Review checklist
│   └── memory/             # Incident memories
│
├── .claude/                # AI agent definitions
│   ├── agents/             # 8 specialized agents
│   ├── commands/           # Slash commands
│   ├── skills/             # SOPs and procedures
│   └── hooks/              # Automation triggers
│
├── scripts/
│   ├── core/               # Main production scripts
│   │   ├── audio/          # Mixing, binaural, enhancement
│   │   ├── generate_voice.py
│   │   ├── build_session.py
│   │   └── assemble_session_video.py
│   ├── ai/                 # AI integration
│   │   ├── learning/       # Self-learning system
│   │   └── error_router.py # Error classification
│   └── utilities/          # Helpers, validation, doctor
│
├── sessions/               # Individual session content
│   └── {session-name}/
│       ├── manifest.yaml   # Session config
│       ├── working_files/  # Scripts, intermediates
│       ├── images/         # Scene images
│       └── output/         # Final deliverables
│
├── knowledge/              # Self-improving knowledge base
│   ├── lessons_learned.yaml
│   ├── outcome_registry.yaml
│   ├── archetypes/
│   ├── symbols/
│   └── indexes/
│
├── docs/                   # Human documentation
├── prompts/                # AI prompt templates
└── config/                 # Configuration files
```

---

## Critical Files

| File | Purpose | When to Read |
|------|---------|--------------|
| `CLAUDE.md` | Master AI instructions | Always |
| `manifest.yaml` | Session configuration | Before any session work |
| `script_production.ssml` | Full script with SFX | Script editing |
| `script_voice_clean.ssml` | Voice-only for TTS | Before TTS generation |
| `voice_enhanced.mp3` | Production voice | Audio mixing |
| `{session}_MASTER.mp3` | Final mastered audio | Video assembly |

---

## External Dependencies

| Service | Purpose | Auth |
|---------|---------|------|
| Google Cloud TTS | Voice synthesis | `GOOGLE_APPLICATION_CREDENTIALS` |
| FFmpeg | Audio/video processing | System install |
| Stable Diffusion | Scene images (optional) | Local API |

---

## Production Stages

| Stage | Output | Checkpoint |
|-------|--------|------------|
| 1. Design | `script_production.ssml` | - |
| 2. Voice Script | `script_voice_clean.ssml` | User review |
| 3. Audio Gen | voice, binaural, SFX | User review |
| 4. Mix | `session_mixed.wav` | User review |
| 5. Master | `{name}_MASTER.mp3` | User review |
| 6. Video | `final_video.mp4` | User review |
| 7. Package | `youtube_package/` | User review |

---

## Key Conventions (Quick Reference)

- **Voice rate:** Always `rate="1.0"` in SSML
- **Pacing:** Use `<break>` tags, not slow rates
- **Audio levels:** Voice -6dB, Binaural -6dB, SFX 0dB
- **Validation:** Run before any generation
- **Enhanced voice:** Always use `voice_enhanced.mp3`

---

## Serena Memories to Check

| Memory | When |
|--------|------|
| `audio_production_methodology` | Audio mixing/mastering |
| `script_production_workflow` | SSML writing |
| `voice_pacing_guidelines` | Voice prosody |
| `production_workflow_stages` | Full pipeline |
| `website_upload_deployment` | Deployment |

---

## Common Commands

```bash
# Environment
source venv/bin/activate

# Validation
python3 scripts/utilities/validate_ssml.py sessions/{session}/working_files/script.ssml
python3 scripts/utilities/doctor.py

# Voice generation
python3 scripts/core/generate_voice.py sessions/{session}/working_files/script_voice_clean.ssml sessions/{session}/output

# Full build
python3 scripts/core/build_session.py sessions/{session}

# Post-processing (MANDATORY)
python3 scripts/core/hypnotic_post_process.py --session sessions/{session}/
```

---

## What Makes This Project Different

1. **Self-learning:** System improves from YouTube analytics and feedback
2. **Agent-based:** 8 specialized AI agents with clear responsibilities
3. **Knowledge-rich:** 60+ YAML files of hypnotic patterns, archetypes, symbols
4. **Quality-gated:** Validation at every stage
5. **Audit-ready:** Lessons learned and memory system

---

## Quick Decision Tree

```
Need to...
├── Create new session → /new-session or /full-build
├── Fix audio issue → Read Serena: audio_production_methodology
├── Fix script/SSML → Read Serena: script_production_workflow
├── Debug anything → Run: python3 scripts/utilities/doctor.py
└── Improve system → /learn-analytics or /review-code
```
