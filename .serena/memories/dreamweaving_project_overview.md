# Dreamweaving Project - Comprehensive Overview

## Project Purpose
Sacred Digital Dreamweaver - Professional hypnotic audio generation system using Google Cloud Text-to-Speech. Creates transformational hypnotic path-working audio sessions with binaural beats and background audio, including complete video production and YouTube packaging.

## Current Status
- **Version:** 2.0 (Reorganized November 2025)
- **Core Provider:** Google Cloud Text-to-Speech (Neural2 voices)
- **Deprecated:** Edge TTS (removed, was ignoring SSML breaks)
- **Status:** Production-ready with comprehensive documentation

## Tech Stack
- **Language:** Python 3.8+, Bash, YAML
- **Core Dependencies:**
  - google-cloud-texttospeech==2.16.3
  - pydub==0.25.1
  - mutagen==1.47.0
  - tqdm==4.66.1
  - scipy, numpy (for audio processing)
  - FFmpeg (system-level, for audio/video)

## Key Architecture Components

### 1. Scripts Organization (scripts/)
- **core/**: Core audio/video generation
  - `generate_audio_chunked.py` - Large SSML to audio (chunks under provider limits)
  - `generate_session_audio.py` - Universal session audio generator with binaural beds
  - `build_session.py` - One-command builder (audio + video)
  - `assemble_session_video.py` - Cross-session video assembly
  - `package_youtube.py` - YouTube packaging automation
  - `audio/` - Audio processing modules:
    - `binaural.py` - Binaural beat generation
    - `voice_enhancement.py` - Hypnotic voice post-processing (warmth, whisper overlay, subharmonic, etc.)
    - `mastering.py` - LUFS normalization, EQ, limiting
    - `mixer.py` - Universal audio stem mixing with sidechain ducking
    - `pink_noise.py`, `isochronic.py`, `am_tones.py`, `panning_beats.py`, `nature.py`, `percussion.py` - Specialized audio layers

- **synthesis/**: Specialized synthesis (pre-talk, opening, closing, natural voice variants - v1 and v2)

- **utilities/**: Helper scripts
  - `create_new_session.sh` - Session scaffolding
  - `validate_ssml.py`, `validate_ssml_enhanced.py` - SSML validation
  - `validate_manifest.py` - Manifest validation
  - `validation.py` - Input validation utilities
  - `preflight_check.sh` - Environment verification with auto-fix
  - `setup_git_hooks.sh` - Git hook setup

- **config/**: Configuration management
  - `voice_config.py` - Voice profile loading
  - `defaults.py` - Default settings

### 2. Session Structure (sessions/)
Each session directory contains:
```
sessions/{session-name}/
├── manifest.yaml           # Session configuration (JSON schema validated)
├── script.ssml             # SSML script (markup for TTS)
├── working_files/          # Intermediate processing
│   └── stems/
├── output/                 # Generated audio/video
│   └── video/
├── images/
│   ├── uploaded/           # User-provided PNGs
│   └── example/
└── variants/               # Alternative versions
```

Existing sessions:
- garden-of-eden - Comprehensive example with extensive documentation
- atlas-starship-ancient-future - Extended session
- neural-network-navigator - Complex session
- _template - Scaffold template

### 3. Documentation Structure (docs/)
- `INDEX.md` - Master navigation
- `CANONICAL_WORKFLOW.md` - Official production workflow (VERSION 1.0)
- `QUICK_START.md` - 5-minute quick start
- `PRODUCTION_WORKFLOW.md` - Complete pipeline (VERSION 3.0)
- `MANIFEST_DRIVEN_AUDIO.md` - Manifest-based generation
- `HYPNOTIC_VOICE_ENHANCEMENT.md` - Voice processing techniques
- `HYPNOTIC_PACING.md` - Timing and pacing techniques
- `WORKFLOW_DECISION_TREE.md` - Workflow selection guide
- `TROUBLESHOOTING.md` - Common issues and solutions
- `AUDIO_VIDEO_WORKFLOW.md` - Audio + video production
- Specialized guides for Edge TTS removal, workflow validation, maintenance

### 4. Configuration & Schemas (config/)
- `voice_config.yaml` - Voice profiles with prosody defaults, audio settings, provider config
  - 7 voice profiles (4 female, 3 male)
  - Session type recommendations
  - Mastering settings (LUFS -14, true peak -1.5dBTP)
- `manifest.schema.json` - JSON Schema for manifest validation
  - Comprehensive validation for all manifest sections
  - Support for multiple audio layers and effects

### 5. Prompts & Guidelines (prompts/)
- `hypnotic_dreamweaving_instructions.md` - Master prompt for script creation
  - 5 mandatory sections: Pre-talk, Induction, Journey, Integration, Post-hypnotic
  - Writing style mandates
  - SSML formatting guidelines
- `nlp_dreamweaving_techniques.md` - NLP techniques
- `session_themes/` - Theme-specific guides

### 6. Templates (templates/)
- `base/` - Base templates (standard, short, extended sessions)
- `themes/` - Theme-specific templates
- `components/` - Reusable SSML components
- Enhancement guides and example scripts

### 7. Testing & Validation (tests/)
- Unit tests
- Integration tests
- Fixtures for test data
- Smoke tests for audio components
- pytest.ini configuration

### 8. Automation & Hooks (.githooks/)
- Pre-commit hook in place
- Git hook setup utility available

## Current Workflow Capabilities

### Audio Generation Pipeline
1. **SSML Input** → Script validation
2. **Voice Synthesis** → Chunked TTS (Google Cloud)
3. **Audio Layers** → Binaural, pink noise, nature, special effects
4. **Voice Enhancement** → Optional post-processing (warmth, whisper, subharmonic)
5. **Mastering** → LUFS normalization, EQ, limiting
6. **Mixing** → Stem mixing with sidechain ducking
7. **Output** → MP3/WAV with metadata

### Video Production
1. **Background Selection** → Auto-detect or provided
2. **Image Timing** → Manifest-driven or even distribution
3. **Overlays** → Fade transitions between images
4. **Title/Subtitle** → Optional text overlays
5. **Audio Sync** → Final audio muxed to video

### Packaging
1. **YouTube Metadata** → Title, description, tags
2. **Thumbnail Generation** → From session images
3. **Package Creation** → Complete YouTube-ready deliverable
4. **Cleanup** → Intermediate files removal

## Key Features Already Implemented

### Manifest-Driven Generation
- Session configuration in YAML
- Automatically applied voice, duration, binaural settings
- Section timing for image placement
- FX timeline for effects scheduling (gamma flashes, ambient layers, bells)
- Archetype definitions with appearance times
- Brainwave state mapping for sections

### Audio Layers Available
1. Binaural beats (adjustable base frequency, per-section offset)
2. Pink noise (with gain control)
3. Nature sounds
4. Isochronic tones
5. Panning beats (stereo panning)
6. Alternate beeps
7. AM (Amplitude Modulation) tones
8. Percussion
9. Custom layers: Delta drift, Xenolinguistic, Harmonic drone, Sub-bass, Hyperspace wind, Ship memory

### Voice Processing
- Tape warmth/saturation
- Whisper overlay (spirit-double effect)
- Phase-shifted double-voicing
- Room impulse response
- De-esser (sibilance softening)
- Breath layers
- Stereo micro-panning
- Low-pass warmth filter
- Subharmonic warm layer
- Amplitude modulation "cuddle waves"
- Triple-layered hypnotic presence

### Validation & Error Handling
- SSML validation with auto-fix
- Manifest schema validation
- Input parameter validation
- Environment checking with auto-fix
- Comprehensive error messages

## Production Capabilities

### One-Command Production
```bash
python3 scripts/core/build_session.py \
  --session sessions/my-session \
  --ssml sessions/my-session/script.ssml \
  --auto-package
```

Produces:
- Voice audio with Google Cloud TTS
- Binaural beats matched to duration
- Mixed audio with proper levels
- Video with images and titles
- YouTube thumbnail
- YouTube description and upload guide
- Cleaned-up working files

### Manifest-Based Configuration
Complete control via manifest.yaml:
- Voice selection and prosody
- Target duration with speaking rate adjustment
- Per-section binaural beat frequencies
- FX timeline with gamma flashes and effects
- Sidechain ducking configuration
- Mastering targets (LUFS, true peak)
- Voice enhancement settings
- YouTube metadata

## Documentation Quality
- Clear, comprehensive docs
- Multiple workflow guides for different scenarios
- Decision trees for choosing correct workflow
- Troubleshooting guides
- Code examples throughout
- Master prompt guide for content creation
- Best practices documented

## Testing Infrastructure
- pytest configured
- Unit and integration tests in place
- Fixtures for test data
- Audio component smoke tests
- Test discovery configured

## Current Gaps (For AI Creative Operating System)

1. **MCP Server Integration** - No existing MCP server configuration
2. **Web Interface** - No web UI for session creation/editing
3. **Real-Time Generation** - Not designed for streaming/real-time
4. **AI Content Generation** - SSML scripts written manually, no AI script generation
5. **Advanced Scheduling** - No workflow scheduling/queuing
6. **Performance Optimization** - Limited parallelization
7. **Advanced Analytics** - No session performance tracking
8. **CI/CD Integration** - No automated testing on commits
9. **Distributed Processing** - Single-machine architecture
10. **Advanced Version Control** - Basic git only, no workflow versioning system
