# CLAUDE.md - Project Context for AI Assistants

## Project Overview
**Sacred Digital Dreamweaver** - A professional hypnotic audio generation system using Google Cloud Text-to-Speech. Creates transformational hypnotic path-working audio sessions with binaural beats and background audio.

## Key Documentation
- **Canonical Workflow**: [docs/CANONICAL_WORKFLOW.md](docs/CANONICAL_WORKFLOW.md) - Official production workflow
- **Quick Start**: [docs/QUICK_START.md](docs/QUICK_START.md)
- **Master Prompt Guide**: [prompts/hypnotic_dreamweaving_instructions.md](prompts/hypnotic_dreamweaving_instructions.md)
- **Index**: [docs/INDEX.md](docs/INDEX.md)

## Project Structure
```
dreamweaving/
├── docs/                      # All documentation
├── prompts/                   # AI prompt templates
├── scripts/
│   ├── core/                  # Core audio generation scripts
│   │   ├── generate_audio_chunked.py  # Main TTS generator
│   │   ├── generate_binaural.py       # Binaural beats
│   │   └── generate_session_audio.py  # Full session assembly
│   ├── synthesis/             # Specialized synthesis scripts
│   └── utilities/             # Helper scripts (validation, setup)
├── templates/                 # SSML templates (base, themes, components)
├── sessions/                  # Individual hypnosis session folders
│   └── {session-name}/
│       ├── manifest.yaml      # Session configuration
│       ├── working_files/     # SSML scripts, intermediate files
│       └── output/            # Final audio/video files
├── resources/background_audio/ # Background tracks, binaural bases
├── config/                    # Voice profiles and settings
└── venv/                      # Python virtual environment
```

## Common Commands

### Environment Setup
```bash
cd ~/Projects/dreamweaving && source venv/bin/activate
```

### Create New Session
```bash
./scripts/utilities/create_new_session.sh "session-name"
```

### Validate SSML
```bash
python3 scripts/utilities/validate_ssml.py sessions/{session}/working_files/script.ssml
```

### Generate Voice Audio
```bash
python3 scripts/core/generate_audio_chunked.py \
    sessions/{session}/working_files/script.ssml \
    sessions/{session}/output/voice.mp3 \
    en-US-Neural2-A
```

### Full Session Build (if manifest exists)
```bash
python3 scripts/core/build_session.py sessions/{session}
```

## Voice Options
- **Female (recommended)**: en-US-Neural2-A (warm), en-US-Neural2-C (soft), en-US-Neural2-E (deep), en-US-Neural2-F (clear)
- **Male**: en-US-Neural2-D (deep), en-US-Neural2-I (warm), en-US-Neural2-J (rich)

## SSML Guidelines
- Use `<break time="Xs"/>` for pauses (critical for hypnotic pacing)
- Use `<prosody rate="slow" pitch="-2st">` for hypnotic sections
- Use `<emphasis>` for key suggestions
- Validate all SSML before generation

## Session Workflow
1. Create session folder from template
2. Write/edit SSML script in `working_files/`
3. Validate SSML syntax
4. Generate voice audio
5. Mix with binaural beats and background audio
6. Export final audio/video

## Dependencies
- Python 3.8+ with venv
- FFmpeg (audio/video processing)
- Google Cloud SDK (authentication)
- Google Cloud TTS API enabled

## Notes for Claude
- Always validate SSML before generating audio
- Check `manifest.yaml` for session-specific settings
- Production files go in `sessions/{name}/output/`
- Working files (SSML, intermediate audio) go in `sessions/{name}/working_files/`
- Refer to CANONICAL_WORKFLOW.md for the official process
