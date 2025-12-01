# CLAUDE.md - AI Creative Operating System

## System Overview

**Sacred Digital Dreamweaver** is an AI-powered creative operating system for producing hypnotic journey videos. This system combines professional audio generation (Google Cloud TTS), multi-layer audio mixing, video assembly, and a self-learning feedback loop.

**Mode**: Fully automated with final review only
**Execution**: Supports headless/scheduled operation
**Learning**: Continuously improves from YouTube analytics and feedback

---

## AI Agents

The system uses 8 specialized AI agents that work together:

| Agent | File | Role |
|-------|------|------|
| **Dreamweaver** | `.claude/agents/dreamweaver.md` | Master orchestrator - parses intent, coordinates agents |
| **Script Writer** | `.claude/agents/script-writer.md` | Generates SSML hypnotic scripts |
| **Manifest Architect** | `.claude/agents/manifest-architect.md` | Creates manifest.yaml from high-level description |
| **Audio Engineer** | `.claude/agents/audio-engineer.md` | Voice synthesis, mixing, mastering |
| **Visual Artist** | `.claude/agents/visual-artist.md` | Generates Midjourney prompts for images |
| **Video Producer** | `.claude/agents/video-producer.md` | Video assembly, VTT subtitles, YouTube package |
| **Quality Control** | `.claude/agents/quality-control.md` | Validates all outputs |
| **Learning Agent** | `.claude/agents/learning-agent.md` | Analyzes feedback, improves system |

---

## Slash Commands

### Session Creation & Building
| Command | Description |
|---------|-------------|
| `/new-session <name>` | Create new session with AI-generated manifest stub |
| `/generate-manifest <session>` | Generate manifest from topic description |
| `/generate-script <topic>` | Generate SSML script for session |
| `/build-audio <session>` | Build audio only |
| `/build-video <session>` | Build video (requires audio) |
| `/full-build <session>` | Complete pipeline: manifest → script → prompts → audio → video |
| `/validate <session>` | Validate SSML and manifest |

### Learning & Improvement
| Command | Description |
|---------|-------------|
| `/learn-analytics <session>` | Process YouTube analytics data |
| `/learn-comments <session>` | Analyze viewer comments |
| `/review-code` | Review and improve codebase |
| `/show-lessons` | Display accumulated learnings |

---

## Skills (SOPs)

Skills are located in `.claude/skills/` and provide standard operating procedures:

### Session Creation
- `create-session.md` - Basic session scaffolding
- `manifest-generation.md` - AI manifest creation
- `full-pipeline.md` - End-to-end automation

### Audio Production
- `voice-synthesis.md` - TTS workflow
- `binaural-generation.md` - Binaural beats
- `mixing-mastering.md` - Audio mixing
- `voice-enhancement.md` - Psychoacoustic processing

### Script Writing
- `ssml-basics.md` - SSML fundamentals
- `hypnotic-patterns.md` - NLP techniques
- `ai-script-generation.md` - Claude-powered generation

### Video Production
- `midjourney-prompts.md` - Image prompt generation
- `video-assembly.md` - FFmpeg assembly
- `vtt-generation.md` - Subtitle timing
- `youtube-packaging.md` - Final package

### Learning
- `analyze-analytics.md` - YouTube stats processing
- `analyze-comments.md` - Feedback extraction
- `code-review.md` - Code improvement
- `apply-lessons.md` - Learning integration

---

## Knowledge Base

The system maintains a self-improving knowledge base in `knowledge/`:

| File | Purpose |
|------|---------|
| `lessons_learned.yaml` | Accumulated insights with timestamps |
| `best_practices.md` | Evolving best practices |
| `analytics_history/` | Historical YouTube performance |
| `code_improvements/` | Code quality tracking |

---

## Production Pipeline

### Automated Flow
```
Topic Description
    ↓
Manifest Generation (AI)
    ↓
SSML Script Generation (AI)
    ↓
Midjourney Prompts (AI) → [User creates images on Midjourney]
    ↓
Audio Generation (Google Cloud TTS)
    ↓
Audio Mixing & Mastering
    ↓
VTT Subtitle Generation
    ↓
Video Assembly
    ↓
YouTube Package (video, thumbnail, description, VTT)
    ↓
[User uploads to YouTube]
    ↓
Analytics & Comments → Learning Agent → Knowledge Base → Next Session
```

### Key Files
| Purpose | Location |
|---------|----------|
| Session manifests | `sessions/{name}/manifest.yaml` |
| SSML scripts | `sessions/{name}/working_files/script.ssml` |
| Midjourney prompts | `sessions/{name}/midjourney-prompts.md` |
| Output files | `sessions/{name}/output/` |
| YouTube package | `sessions/{name}/output/youtube_package/` |

---

## Project Structure

```
dreamweaving/
├── .claude/                      # AI OS configuration
│   ├── agents/                   # AI agent definitions
│   ├── commands/                 # Slash command definitions
│   ├── skills/                   # SOPs and procedures
│   └── hooks/                    # Event automation
│
├── scripts/
│   ├── core/                     # Core production scripts
│   │   ├── generate_audio_chunked.py
│   │   ├── generate_session_audio.py
│   │   ├── assemble_session_video.py
│   │   ├── package_youtube.py
│   │   └── audio/                # Audio processing modules
│   ├── synthesis/                # Specialized synthesis
│   ├── utilities/                # Helpers and validation
│   └── ai/                       # AI integration
│       ├── script_generator.py
│       ├── manifest_generator.py
│       ├── prompt_generator.py
│       ├── vtt_generator.py
│       └── learning/             # Self-learning system
│
├── knowledge/                    # Self-improving knowledge base
│   ├── lessons_learned.yaml
│   ├── best_practices.md
│   └── analytics_history/
│
├── sessions/                     # Individual sessions
│   └── {session-name}/
│       ├── manifest.yaml
│       ├── working_files/
│       ├── images/uploaded/
│       ├── midjourney-prompts.md
│       └── output/
│
├── config/                       # Configuration
│   ├── voice_config.yaml
│   └── manifest.schema.json
│
├── prompts/                      # AI prompt templates
│   └── hypnotic_dreamweaving_instructions.md
│
├── docs/                         # Documentation
└── templates/                    # SSML templates
```

---

## Key Documentation

| Document | Purpose |
|----------|---------|
| [docs/CANONICAL_WORKFLOW.md](docs/CANONICAL_WORKFLOW.md) | Official production workflow |
| [docs/QUICK_START.md](docs/QUICK_START.md) | 5-minute quick start |
| [prompts/hypnotic_dreamweaving_instructions.md](prompts/hypnotic_dreamweaving_instructions.md) | Master script prompt |
| [docs/INDEX.md](docs/INDEX.md) | Complete documentation index |

---

## Voice Options

### Female (recommended for hypnosis)
- `en-US-Neural2-A` - Warm, calming (default)
- `en-US-Neural2-C` - Soft, gentle
- `en-US-Neural2-E` - Deep, resonant
- `en-US-Neural2-F` - Clear, articulate

### Male
- `en-US-Neural2-D` - Deep, authoritative
- `en-US-Neural2-I` - Warm, compassionate
- `en-US-Neural2-J` - Rich, mature

---

## SSML Guidelines

```xml
<!-- Pauses (critical for hypnotic pacing) -->
<break time="2s"/>

<!-- Slow, hypnotic delivery -->
<prosody rate="0.85" pitch="-2st">
  Allow yourself to relax...
</prosody>

<!-- Emphasis for suggestions -->
<emphasis level="moderate">deeply relaxed</emphasis>
```

**Mandatory Sections:**
1. Pre-talk (2-3 min) - Introduction and safety
2. Induction (3-5 min) - Guide into trance
3. Journey (10-20 min) - Main hypnotic experience
4. Integration (2-3 min) - Process and integrate
5. Awakening (1-2 min) - Return to awareness

---

## Quick Commands

### Environment
```bash
cd ~/Projects/dreamweaving && source venv/bin/activate
```

### Manual Workflow
```bash
# Create session
./scripts/utilities/create_new_session.sh "session-name"

# Validate SSML
python3 scripts/utilities/validate_ssml.py sessions/{session}/working_files/script.ssml

# Build complete session
python3 scripts/core/build_session.py sessions/{session}
```

---

## Dependencies

- Python 3.8+ with venv
- FFmpeg (audio/video processing)
- Google Cloud SDK (authentication)
- Google Cloud TTS API enabled
- Serena MCP Server (http://127.0.0.1:24283)

---

## Automation Hooks

| Hook | Trigger | Action |
|------|---------|--------|
| `on-ssml-change` | Save `.ssml` file | Auto-validate SSML |
| `on-manifest-change` | Save `manifest.yaml` | Auto-validate manifest |
| `pre-build` | Before build | Run preflight checks |

---

## Learning System

The system continuously improves through:

1. **YouTube Analytics** - Track views, retention, engagement
2. **Comment Analysis** - Extract sentiment and feedback
3. **Code Review** - Improve code quality over time
4. **Performance Correlation** - Map session attributes to metrics

### Feedback Loop
```
Session Published → Analytics Collected → Lessons Extracted → Applied to Next Session
```

### Learning Categories
- Content performance (topics, themes)
- Audio quality (voice settings, frequencies)
- Pacing (section durations)
- Visual style (image engagement)
- Code quality (track improvements)

---

## Notes for Claude

1. **Always use agents** for complex tasks - they have specialized context
2. **Check lessons_learned.yaml** before generating new sessions
3. **Validate early** - run validation before any generation
4. **Use manifest.yaml** for session-specific settings
5. **Track progress** with TODO list for multi-step tasks
6. **Learn from mistakes** - update knowledge base when things go wrong
7. **Production files** go in `sessions/{name}/output/`
8. **Working files** go in `sessions/{name}/working_files/`
9. **Refer to skills** for detailed procedures
