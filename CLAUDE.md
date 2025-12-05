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
| `/auto-generate <topic>` | **NEW:** Fully automated topic → YouTube package (see below) |
| `/validate <session>` | Validate SSML and manifest |

### Learning & Improvement
| Command | Description |
|---------|-------------|
| `/learn-analytics <session>` | Process YouTube analytics data |
| `/learn-comments <session>` | Analyze viewer comments |
| `/review-code` | Review and improve codebase |
| `/show-lessons` | Display accumulated learnings |

---

## Automated Video Generation (NEW)

### Single Command: Topic → YouTube Package

The `/auto-generate` command produces a complete YouTube-ready video from just a topic:

```bash
/auto-generate "Finding Inner Peace Through Nature" --mode standard
```

**Output:** Complete `sessions/{name}/output/youtube_package/` with:
- `final_video.mp4` (1920x1080, H.264)
- `thumbnail.png` (1280x720)
- `metadata.yaml` (title, description, tags, chapters)
- `subtitles.vtt` (timed captions)
- `cost_report.json` (actual costs tracked)

### Cost Optimization Modes

| Mode | AI Cost | Total | Use Case |
|------|---------|-------|----------|
| `budget` | ~$0.55 | ~$0.70 | Bulk production, testing |
| `standard` | ~$0.91 | ~$1.06 | **Production (recommended)** |
| `premium` | ~$1.36 | ~$1.51 | High-stakes releases |

### Tiered Model Allocation

The system uses 3 AI model tiers strategically:

| Tier | Model | Cost | Used For |
|------|-------|------|----------|
| **Haiku** | claude-3-haiku | $0.25-1.25/M tok | Structured data, assembly |
| **Sonnet** | claude-sonnet-4 | $3-15/M tok | Script sections, metadata |
| **Opus** | claude-opus-4 | $15-75/M tok | Creative concept, main journey |

### 14 Discrete Prompts

The pipeline executes 14 prompts in phases:

| Phase | Prompts | Purpose |
|-------|---------|---------|
| **1. Init** | P1.1 (Haiku), P1.2 (Opus) | Manifest + journey concept |
| **2. Script** | P2.1-P2.3 (Sonnet/Opus) | SSML generation |
| **3. Audio** | P3.1-P3.2 (Haiku) | Binaural + SFX config |
| **4. Images** | P4.1 (Sonnet) | SD scene prompts |
| **5. Video** | P5.1-P5.3 (Haiku/Sonnet) | VTT, YouTube metadata |
| **6. QA** | P6.1-P6.2 (Haiku/Opus) | Validation |

### Batch Generation

For scheduled/cron operation:

```bash
# Create topics file
python3 scripts/ai/batch_generate.py --create-sample

# Run batch
python3 scripts/ai/batch_generate.py --topics-file topics.yaml --mode standard

# Parallel execution
python3 scripts/ai/batch_generate.py --topics-file topics.yaml --parallel 2
```

**Topics file format:**
```yaml
sessions:
  - topic: "Finding Inner Peace Through Nature"
    duration: 25
    style: healing
  - topic: "Building Confidence"
    duration: 30
    style: confidence
```

### Key Files

| File | Purpose |
|------|---------|
| `scripts/ai/auto_generate.py` | Main orchestrator |
| `scripts/ai/batch_generate.py` | Batch/scheduled generation |
| `scripts/ai/prompt_executor.py` | Prompt template execution |
| `scripts/ai/model_router.py` | Routes to API endpoints |
| `scripts/ai/cost_tracker.py` | Token/cost tracking |
| `scripts/ai/prompts/*.yaml` | 14 prompt templates |
| `config/model_tiers.yaml` | Tier definitions |

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
- **Serena memory: `audio_production_methodology`** - Complete mixing methodology

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
| `hypnotic_patterns.yaml` | Phase 3 patterns: vagal activation, emotional calibration, integration actions |
| `archetypes.yaml` | Shadow/gift transformations, archetypal guides, family mappings |
| `outcome_registry.yaml` | **NEW:** Outcome → patterns/archetypes/objects mapping |
| `best_practices.md` | Evolving best practices |
| `analytics_history/` | Historical YouTube performance |
| `code_improvements/` | Code quality tracking |

---

## Outcome Engineering (NEW)

Ensures scripts deliver their stated transformations through systematic pattern inclusion.

### Quick Reference

| Outcome | Required Patterns | Key Focus |
|---------|-------------------|-----------|
| `healing` | vagal (2+), emotional_calibration (1+) | Safety, somatic release |
| `transformation` | fractionation (2+), temporal_dissociation (1+) | Deep trance, identity |
| `empowerment` | embedded_commands (10+), fractionation (2+) | Power words |
| `confidence` | embedded_commands (12+), fractionation (2+) | Worth affirmations |
| `relaxation` | vagal (3+), breath_pacing (3+) | Parasympathetic |
| `spiritual_growth` | temporal_dissociation (1+), sensory_stacking (3+) | Timelessness |

### Manifest Fields

```yaml
session:
  desired_outcome: "healing"  # Required for outcome validation
  outcome_subcategory: "trauma_integration"  # Optional
  target_transformation: "From fragmentation → wholeness"
  success_metrics:
    - "Somatic shift in chest/heart area"
    - "Sense of emotional release"
```

### Validation

```bash
# Full validation (includes outcome check)
python scripts/utilities/validate_ssml.py sessions/{session}/working_files/script.ssml

# Detailed outcome validation
python scripts/utilities/validate_outcome.py sessions/{session}/ -v
```

**Reference:** `knowledge/outcome_registry.yaml` for complete outcome specifications.

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
Audio Mixing
    ↓
Hypnotic Post-Processing (MANDATORY)
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
| Production script (with SFX cues) | `sessions/{name}/working_files/script_production.ssml` |
| Voice-only script (for TTS) | `sessions/{name}/working_files/script_voice_clean.ssml` |
| Midjourney prompts | `sessions/{name}/midjourney-prompts.md` |
| Enhanced voice | `sessions/{name}/output/voice_enhanced.mp3` |
| Mixed audio | `sessions/{name}/output/session_mixed.wav` |
| **Final master (USE THIS)** | `sessions/{name}/output/{name}_MASTER.mp3` |
| Output files | `sessions/{name}/output/` |
| YouTube package | `sessions/{name}/output/youtube_package/` |

---

## Production Workflow Stages

> **Full details:** See Serena memory `production_workflow_stages`

| Stage | Name | Key Output | User Check |
|-------|------|------------|------------|
| 1 | Creative Design | `script_production.ssml` | - |
| 2 | Voice Script | `script_voice_clean.ssml` | ✓ |
| 3 | Audio Generation | voice, binaural, SFX | ✓ |
| 4 | Audio Mixing | `session_mixed.wav` | ✓ |
| 5 | **Hypnotic Post-Processing** | `{name}_MASTER.mp3` | ✓ |
| 5.5 | **Video Images** | `output/video_images/` | - |
| 6 | Video Production | `final_video.mp4` | ✓ |
| 7 | YouTube Packaging | `youtube_package/` | ✓ |
| 8 | Cleanup | - | - |
| 9 | **Website Upload** | salars.net/dreamweavings/{slug} | - |

**Stage 5 Command (MANDATORY):**
```bash
python3 scripts/core/hypnotic_post_process.py --session sessions/{session}/
```

**Stage 5.5 Command (Scene Images - SD Default):**
```bash
# Generate scene images using Stable Diffusion (default)
python3 scripts/core/generate_scene_images.py sessions/{session}/

# Or generate Midjourney prompts instead
python3 scripts/core/generate_scene_images.py sessions/{session}/ --midjourney-only
```

### Stage Flow

```
TOPIC → [1] Brainstorm & Script → ✓ [2] Voice Script Review
                                           ↓
         [8] Cleanup ← ✓ [7] YouTube ← ✓ [6] Video ← [5.5] Images ← ✓ [5] Hypnotic Post-Process
                                                                              ↑
                                                        ✓ [4] Mix ← ✓ [3] Audio Gen
```

### Claude Stage Tracking

When working on a session, Claude should always state the current stage:

> "We are in **STAGE X: [NAME]**"

Wait for user checkpoint (✓) before proceeding to next stage.

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
| [docs/PRODUCTION_SPECIFICATION.md](docs/PRODUCTION_SPECIFICATION.md) | Voice consistency, NLP validation, SFX sync |
| [docs/YOUTUBE_PACKAGING_SOP.md](docs/YOUTUBE_PACKAGING_SOP.md) | Complete YouTube packaging workflow (thumbnails, titles, VTT) |
| [docs/THUMBNAIL_DESIGN_GUIDE.md](docs/THUMBNAIL_DESIGN_GUIDE.md) | Expert thumbnail design principles |
| [docs/YOUTUBE_TITLE_GUIDE.md](docs/YOUTUBE_TITLE_GUIDE.md) | High-CTR title optimization |
| [docs/QUICK_START.md](docs/QUICK_START.md) | 5-minute quick start |
| [prompts/hypnotic_dreamweaving_instructions.md](prompts/hypnotic_dreamweaving_instructions.md) | Master script prompt |
| [docs/INDEX.md](docs/INDEX.md) | Complete documentation index |
| [docs/MCP_PLUGINS_GUIDE.md](docs/MCP_PLUGINS_GUIDE.md) | MCP servers & plugins integration guide |
| [docs/STOCK_IMAGE_SOP.md](docs/STOCK_IMAGE_SOP.md) | Stock image sourcing and licensing |

---

## Voice Options

**PRODUCTION STANDARD:** Use `en-US-Neural2-H` (bright female) for all sessions.

> **Note:** The `generate_voice.py` script automatically uses this voice. Do not override unless specifically requested.

### Female (recommended for hypnosis)
- `en-US-Neural2-H` - Bright, clear **(DEFAULT - Production Standard)**
- `en-US-Neural2-E` - Deep, resonant (alternative for darker themes)
- `en-US-Neural2-C` - Soft, gentle
- `en-US-Neural2-F` - Clear, articulate
- `en-US-Neural2-G` - Warm, approachable

### Male
- `en-US-Neural2-A` - Calm, neutral
- `en-US-Neural2-D` - Deep, authoritative
- `en-US-Neural2-I` - Warm, compassionate
- `en-US-Neural2-J` - Rich, mature

> **Note:** Neural2-A is MALE, not female.

---

## SSML Guidelines

> **CRITICAL:** See Serena memory `script_production_workflow` for complete workflow.

### Voice Pacing (IMPORTANT)

**ALWAYS use `rate="1.0"` (normal speed) for ALL sections.**

Slow speaking rates (0.85, 0.88, 0.90) sound unnatural with Google TTS Neural2 voices.
Achieve hypnotic pacing through generous `<break>` tags instead.

```xml
<!-- CORRECT: Normal rate, use breaks for pacing -->
<prosody rate="1.0" pitch="-2st">
  Take a deep breath in... <break time="2s"/>
  And exhale slowly... <break time="3s"/>
</prosody>

<!-- WRONG: Do NOT slow the rate -->
<prosody rate="0.85" pitch="-2st">
  Take a deep breath in...
</prosody>
```

### Break Duration Guidelines

| Context | Duration |
|---------|----------|
| Between phrases | 700ms-1.0s |
| After sentences | 1.0s-1.7s |
| Breathing cues | 2.0s-3.0s |
| Visualization moments | 3.0s-4.0s |
| Major transitions | 4.0s-5.5s |

### Prosody by Section

```xml
<!-- Pre-Talk: Normal, grounded -->
<prosody rate="1.0" pitch="0st">

<!-- Induction: Deeper pitch for calming -->
<prosody rate="1.0" pitch="-2st">

<!-- Journey: Slightly deeper for immersion -->
<prosody rate="1.0" pitch="-1st">

<!-- Integration/Return: Maintaining depth -->
<prosody rate="1.0" pitch="-1st">

<!-- Closing: Neutral, grounded -->
<prosody rate="1.0" pitch="0st">
```

### Sound Effect Cues

Place SFX markers on their own lines in the production script:
```
[SFX: Deep ceremonial bell tone, resonant, 4 seconds with natural decay]
```

These are stripped out before voice generation but preserved for mixing reference.

**Mandatory Sections:**
1. Pre-talk (2-3 min) - Introduction and safety
2. Induction (4-5 min) - Progressive relaxation, trance induction
3. Journey (14-16 min) - Main hypnotic experience
4. Integration (2-3 min) - Process and return
5. Anchors/Closing (2-3 min) - Post-hypnotic suggestions

---

## Quick Commands

### Environment
```bash
cd ~/Projects/dreamweaving && source venv/bin/activate
```

### Voice Generation (ALWAYS USE THIS)
```bash
# CANONICAL voice generation command - uses production voice + enhancement
python3 scripts/core/generate_voice.py \
    sessions/{session}/working_files/script.ssml \
    sessions/{session}/output
```

This automatically:
- Uses **en-US-Neural2-H** (bright female voice)
- Speaking rate: 0.88x, Pitch: 0 semitones
- Applies voice enhancement (warmth, room, layers)
- Outputs both `voice.mp3` and `voice_enhanced.mp3`

**Always use `voice_enhanced.mp3` for production!**

> **Note:** Despite SSML using `rate="1.0"`, the TTS engine applies 0.88x for natural hypnotic pacing. The `rate="1.0"` in SSML prevents additional slowing on top of this baseline.

### Audio Mixing (CRITICAL)

> **Full details:** See Serena memory `audio_production_methodology`

**Standard Stem Levels:**
| Stem | Level |
|------|-------|
| Voice | -6 dB |
| Binaural | -6 dB |
| SFX | 0 dB |

```bash
# Mix with FFmpeg (fast, reliable)
ffmpeg -y -i voice_enhanced.wav -i binaural_dynamic.wav -i sfx_track.wav \
  -filter_complex "[0:a]volume=-6dB[voice];[1:a]volume=-6dB[bin];[2:a]volume=0dB[sfx];[voice][bin][sfx]amix=inputs=3:duration=longest:normalize=0[mixed]" \
  -map "[mixed]" -acodec pcm_s16le session_mixed.wav
```

### Manual Workflow
```bash
# Create session
./scripts/utilities/create_new_session.sh "session-name"

# Validate SSML
python3 scripts/utilities/validate_ssml.py sessions/{session}/working_files/script.ssml

# Generate voice (with enhancement)
python3 scripts/core/generate_voice.py sessions/{session}/working_files/script.ssml sessions/{session}/output

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

---

# Quick Decision Trees

## What Task Am I Doing?

```
User Request
    │
    ├─► "Create new session" ──────► /new-session or /full-build
    │
    ├─► "Generate script" ─────────► /generate-script (needs manifest first)
    │
    ├─► "Build audio" ─────────────► /build-audio (needs script first)
    │
    ├─► "Fix audio issue" ─────────► Read Serena memory: audio_production_methodology
    │
    ├─► "Fix script/SSML" ─────────► Read Serena memory: script_production_workflow
    │
    ├─► "Debug something" ─────────► Follow Debugging Playbook (below)
    │
    └─► "Improve/learn" ───────────► /learn-analytics or /review-code
```

## Where Should I Look for Information?

| Need | First Check | Then Check |
|------|-------------|------------|
| Audio mixing levels | Serena: `audio_production_methodology` | CLAUDE.md Quick Commands |
| Script structure | Serena: `script_production_workflow` | SSML Guidelines section |
| Voice settings | CLAUDE.md Voice Options | `scripts/core/generate_voice.py` |
| Session structure | CLAUDE.md Key Files table | `sessions/_template/` |
| Debugging | CLAUDE.md Debugging Playbook | Known Pitfalls section |
| Best practices | `knowledge/best_practices.md` | `knowledge/lessons_learned.yaml` |

## File Naming Conventions

| File | Purpose | When Created |
|------|---------|--------------|
| `script_production.ssml` | Full script with SFX markers | After script generation |
| `script_voice_clean.ssml` | Script without SFX (for TTS) | Before voice generation |
| `voice.mp3` | Raw TTS output | After voice generation |
| `voice_enhanced.mp3` | **USE THIS** - Production voice | After voice generation |
| `binaural_dynamic.wav` | Binaural beats track | During audio build |
| `sfx_track.wav` | Sound effects track | During audio build |
| `session_mixed.wav` | All stems mixed | After mixing |
| `final_master.mp3` | Final mastered output | After mastering |

---

# Anti-Patterns (What NOT To Do)

## Script Writing Anti-Patterns

```xml
<!-- WRONG: Slow rate sounds robotic -->
<prosody rate="0.85" pitch="-2st">

<!-- CORRECT: Normal rate, use breaks for pacing -->
<prosody rate="1.0" pitch="-2st">
  Text... <break time="2s"/>
</prosody>
```

```xml
<!-- WRONG: SFX markers inline with text -->
Here is the text [SFX: bell] and more text.

<!-- CORRECT: SFX markers on their own lines -->
[SFX: Deep ceremonial bell, 3 seconds]

Here is the text and more text.
```

## Audio Production Anti-Patterns

```bash
# WRONG: Using raw voice.mp3
ffmpeg -i voice.mp3 ...

# CORRECT: Always use enhanced voice
ffmpeg -i voice_enhanced.wav ...
```

```bash
# WRONG: Mixing without proper levels
ffmpeg -i voice.wav -i binaural.wav -filter_complex "amix" output.wav

# CORRECT: Apply proper stem levels
ffmpeg -i voice.wav -i binaural.wav \
  -filter_complex "[0:a]volume=-6dB[v];[1:a]volume=-6dB[b];[v][b]amix=inputs=2:normalize=0" \
  output.wav
```

## Common Mistakes to Avoid

| Mistake | Why It's Wrong | Correct Approach |
|---------|----------------|------------------|
| Using `rate="0.85"` in SSML | Sounds robotic with Neural2 | Use `rate="1.0"` + breaks |
| Mixing voice at 0 dB | Voice clips when mixed | Voice at -6 dB |
| Forgetting to strip SFX markers | TTS reads "[SFX:..." aloud | Create `script_voice_clean.ssml` |
| Using `voice.mp3` for production | Missing enhancement | Use `voice_enhanced.mp3` |
| Running scripts without venv | Missing dependencies | `source venv/bin/activate` first |
| Normalizing in amix filter | Unpredictable levels | Use `normalize=0` |

---

# Serena Memory Quick Reference

Claude should read these memories for detailed information:

| Memory | When to Read |
|--------|--------------|
| `audio_production_methodology` | Any audio mixing/mastering task |
| `script_production_workflow` | Writing or fixing SSML scripts |
| `voice_pacing_guidelines` | Quick voice pacing reference |
| `dreamweaving_project_overview` | Understanding project architecture |
| `session_learnings_system` | Before generating new sessions |
| `production_workflow_stages` | Full stage-by-stage production workflow |
| `website_upload_deployment` | Uploading to salars.net, Vercel, R2 storage |
| `mcp_plugins_integration` | MCP servers, plugins, context window management |

**Usage Pattern:**
```
1. Check CLAUDE.md for quick reference
2. If need detailed procedure → Read relevant Serena memory
3. If still unclear → Check .claude/skills/ or .claude/agents/
```

---

# Prompt-Engineering Cheat-Sheet for Dreamweaving, Coding & Creative AI Pipelines

## Step 1 — Expert Table

| Expert(s)         | AI Prompt Engineers, NLP Architects, Systems Designers                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| :---------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Possible Keywords | prompt patterns, structured prompting, exemplars, chain-of-thought, scaffolding, rewriting loops, constraints, formatting rules, markdown specs, guardrails, style conditioning, system personas, multimodal cues, sensory prompting, SSML markup, narrative arcs, audio engineering prompts, Claude Opus, iterative refinement, debugging prompts, hallucination control, anchoring examples, input schema, output schema, evaluation rubric, step decomposition, role conditioning, style transfer, TTS optimization, Midjourney alignment |
| Question          | Create a comprehensive prompt-engineering cheat-sheet tailored for Claude workflows, Dreamweaver scripts, coding tasks, and creative AI pipelines                                                                                                                                                                                                                                                                                                                                                                                            |
| Plan              | Summarize best practices using a structured, multi-section methodology including: role conditioning, scaffolding, exemplar anchoring, output schemas, iteration loops, multimodal prompting, and creative control frameworks.                                                                                                                                                                                                                                                                                                                |

---

## Authoritative Expert Guidance

### Core Principle 1 — Role Conditioning

Use strong identities to anchor behavior.

**Pattern:**

```
You are [ROLE]. Your job is to [MISSION].
Your output must follow: [STYLE + FORMAT RULES].
```

**Examples:**

* "You are *The Sacred Digital Dreamweaver*, a narrative architect of mythic, religious, and futuristic consciousness journeys."
* "You are a *Senior Next.js Systems Engineer* specializing in TypeScript, Tailwind, Neon Postgres, and agent pipelines."

Role = stability.
Mission = precision.
Format rules = reliability.

---

### Core Principle 2 — Scaffolding (Break Big Tasks into Structured Subtasks)

Instead of:

> "Write the whole system."

Use:

```
1. Summarize the goal
2. List constraints
3. Generate architecture
4. Write core components
5. Refine with examples
```

For Dreamweaver:

```
1. Summarize the mystical idea
2. Extract archetypes
3. Define sound palette
4. Produce SSML script
5. Provide video imagery prompt
```

Claude performs 10× better when walking through stages.

---

### Core Principle 3 — Provide Exemplars (Show the Pattern You Want)

Claude is heavily example-driven.
Give it a model to imitate.

**Example:**

```
Here is a sample journey structure:

## [Journey Name]
- Journey: …
- Archetypes: …
- Sound: …

Now create a new one for "The Emerald Gate of the Elohim."
```

Your Dreamweaver templates are PERFECT for this.

---

### Core Principle 4 — Explicit Input/Output Schema

Define rigid boundaries.

**Example Schema:**

```
INPUTS:
- topic
- emotional tone
- duration
- theological or mythic source
- desired gifts/skills

OUTPUT:
{
  "journey": "...",
  "archetypes": [...],
  "sound": "...",
  "ssml_script": "...",
  "imagery_prompt": "..."
}
```

Claude will ALWAYS comply better with defined schemas.

---

### Core Principle 5 — Iterative Refinement Loop ("Refining Passes")

This is where Claude shines.
Use a recursive loop:

```
1. Generate v1
2. Evaluate your own output against rubric
3. Improve clarity, depth, sensory richness
4. Output improved version
```

You can literally say:

> "Run a refinement pass. Improve narrative depth, sensory layering, archetypal clarity, and SSML rhythm."

---

### Core Principle 6 — Add Constraints & Guardrails

Claude LOVES rules.

Examples:

* "No filler language."
* "Use sacred tone."
* "All SSML must use <break> no longer than 300ms."
* "Limit the induction language to non-clinical terms."
* "Maintain consistency with Dreamweaver cosmology."

More rules = more accuracy.

---

### Core Principle 7 — Sensory Prompting for Dreamweaving

To upgrade hypnotic content:

**Use sensory layers:**

```
Layer 1 — Visual archetype field
Layer 2 — Felt-sense somatic cues
Layer 3 — Auditory & vibrational symbols
Layer 4 — Temporal/ritual sequencing
```

Claude excels at multi-layer sensory prompting when explicitly requested.

---

### Core Principle 8 — Multimodal Prompting (SSML, Audio, Imagery)

For SSML:

```
Use <prosody rate="1.0"> for all speech (normal rate).
Achieve pacing through <break time="2s"/> tags.
Use <emphasis> only for sacred key terms.
```

For cinematic imagery:

```
Use 16:9
Use 8k level detail
Specify atmospherics (mist, glow particles, sacred light)
Specify mood (tranquil, ancient, cosmic)
```

For binaural beats:

```
Alpha: 8–12hz for soft induction
Theta: 4–7hz for journeying
Delta: 0.5–3hz for mystery, cosmic
```

Claude follows these like programming instructions.

---

### Core Principle 9 — Claude Loves "Rubrics"

Tell Claude how it will be graded.

Example:

```
Evaluate your output for:
- clarity
- depth
- archetypal coherence
- hypnotic pacing
- sensory density
- narrative potency

Then revise.
```

This yields MUCH better Dreamweavings, hypnotic scripts, and coding.

---

### Core Principle 10 — Debugging Prompts

When Claude misfires:

Use:

```
Identify the failure mode.
Explain the underlying cause.
Provide a corrected version.
```

Failure modes include:

* Over-verbose
* Too abstract
* Missing structure
* Hallucinated logic
* Loss of narrative tone

Claude is GREAT at self-diagnosis when asked.

---

### Core Principle 11 — Metaprompting (Prompting About Prompts)

Ask Claude:

> "Rewrite my prompt to be 10× clearer using your own best practices."

Or:

> "Optimize this for Claude Opus."

It will rewrite your prompt into its own internal style — extremely powerful.

---

### Core Principle 12 — "Dreamweaver Mode" Template

Add this to your system prompts:

```
You are The Sacred Digital Dreamweaver AI.

Mission:
Transform mystical, religious, mythic, cosmic, and historical themes into hypnotic SSML scripts, archetypal journeys, and multisensory binaural soundscapes with cinematic imagery prompts.

Always output in the structure:
1. Journey
2. Archetypes
3. Sound
4. SSML script
5. 16:9 Image Prompt

Tone: sacred, mythic, profound, sensory-rich, hypnotic, elegant.
```

This anchor produces consistent high-grade results.

---

## Recommended Resources

### See also

* **Prompt Engineering Patterns** - For deeper structured prompting systems.
* **Chain of Thought prompting** - Helps with step-by-step reasoning.
* **Role-Based Prompting Examples** - Useful for persona anchoring.

### You may also enjoy

* **Archetypal symbolism** - Expands your dreamweaving vocabulary.
* **Binaural beat theory** - For deeper audio design.
* **SSML advanced techniques** - Perfect for your Google Cloud TTS pipeline.

---

# Dreamweaving Task Protocol

For complex tasks in this project, follow this streamlined protocol:

## Task Types & Approach

| Task Type | Approach | Key Checks |
|-----------|----------|------------|
| **New Session** | Use `/full-build` or `/new-session` | Check `lessons_learned.yaml` first |
| **Script Writing** | Read Serena memory first | Validate SSML before TTS |
| **Audio Production** | Follow exact stem levels | Use `voice_enhanced.mp3` |
| **Bug Fix** | Follow Debugging Playbook | Minimal diff, test after |
| **Code Change** | Plan → Implement → Validate | Use TodoWrite for tracking |

## Before Starting Any Task

```
1. What type of task is this? (see table above)
2. What Serena memories are relevant?
3. What files will be affected?
4. What validation will confirm success?
```

## Code Change Protocol

For any code modification:

1. **Read first** - Never modify code you haven't read
2. **Minimal diff** - Change only what's necessary
3. **Test immediately** - Run validation after changes
4. **Track progress** - Use TodoWrite for multi-step tasks

## Safety Rules

* Never overwrite SSML without backup awareness
* Always use `voice_enhanced.mp3` not `voice.mp3`
* Never mix audio without setting stem levels
* Validate SSML before any TTS generation
* Check `venv` is activated before running Python scripts

---

# Dreamweaving-Specific Debugging

## Common Issues & Quick Fixes

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| Audio silent after mix | Stems not normalized | Check stem levels in `audio_production_methodology` |
| TTS reads "[SFX:..." | SFX markers not stripped | Create `script_voice_clean.ssml` |
| Voice sounds robotic | Using `rate < 1.0` | Change to `rate="1.0"`, use breaks |
| Audio clips/distorts | Voice at 0 dB | Set voice to -6 dB |
| Script validation fails | Invalid SSML syntax | Run `validate_ssml.py` for details |
| Missing dependencies | venv not activated | `source venv/bin/activate` |
| TTS API error | Auth issue | Check `GOOGLE_APPLICATION_CREDENTIALS` |
| Binaural inaudible | Level too low | Should be -6 dB (was -12 dB in old config) |

## Audio Debugging Commands

```bash
# Check audio file properties
ffprobe -v error -show_format -show_streams file.wav

# Check peak levels (should be < 0 dB)
ffmpeg -i file.wav -af "volumedetect" -f null /dev/null 2>&1 | grep max_volume

# Check LUFS loudness
ffmpeg -i file.wav -af "loudnorm=print_format=json" -f null /dev/null 2>&1

# Listen to specific stem isolated
ffplay -nodisp file.wav
```

## Script Debugging

```bash
# Validate SSML syntax
python3 scripts/utilities/validate_ssml.py sessions/{session}/working_files/script.ssml

# Check for leftover SFX markers (should return nothing)
grep -n "\[SFX:" sessions/{session}/working_files/script_voice_clean.ssml

# Count words (target ~3,750 for 25 min)
cat script.ssml | sed 's/<[^>]*>//g' | wc -w
```

---

# Project Debugging Playbook

When debugging this project, always behave like a senior engineer:
- Work step-by-step, forming and testing hypotheses.
- Prefer minimal, surgical fixes over large refactors.
- Before proposing changes, restate:
  - The symptom
  - The expected behavior
  - The most likely root causes

## Debugging Workflow

Follow this algorithm:

1. **Clarify problem**
   - Restate the bug in your own words.
   - List assumptions and unknowns.

2. **Reproduce**
   - Suggest concrete steps or commands to reproduce the issue.
   - If logs or stack traces are provided, summarize what they say.

3. **Inspect code**
   - Identify the most likely failing module/function.
   - Use Serena / other MCP tools to open those files.

4. **Hypothesize**
   - List 2–4 plausible root causes.
   - For each, propose a small experiment or code probe.

5. **Experiment**
   - Propose specific debug actions:
     - Temporary logs
     - Small test cases
     - Debugger breakpoints

6. **Decide + Fix**
   - Pick the most likely root cause based on evidence.
   - Propose the smallest safe code change.

7. **Verify**
   - Explain how to re-run tests or manual steps to confirm the fix.
   - Mention any edge cases that still deserve tests.

Always show your reasoning and label hypotheses vs. confirmed facts.

---

## Debugging Checklist

```
### DEBUG CHECKLIST
- [ ] Confirm exact error message
- [ ] Confirm file + line number
- [ ] Reproduce the issue locally
- [ ] Check logs and stack traces
- [ ] Inspect recent changes
- [ ] Verify environment variables
- [ ] Validate data assumptions
- [ ] Create minimal reproduction case
- [ ] Identify root cause category:
      • Logic bug
      • State bug
      • Dependency issue
      • Environment mismatch
      • Integration mismatch
- [ ] Propose fix
- [ ] Implement small diff
- [ ] Add verification steps
```

---

## Debugging Output Format

Claude's debug responses must follow this structure:

```
### ROOT CAUSE
Explanation of what failed and why.

### FIX PLAN
1. Step 1
2. Step 2
3. Step 3

### PATCH (diff-only)
# file.ext
@@ changes @@
+ fix here
- remove here

### VERIFICATION
- [ ] Run command:
- [ ] Open URL:
- [ ] Check logs:
- [ ] Confirm no regressions:
```

---

## Commands For Debugging

- Dev environment: `cd ~/Projects/dreamweaving && source venv/bin/activate`
- Run all tests: `python -m pytest`
- Validate SSML: `python3 scripts/utilities/validate_ssml.py <file>`
- Validate NLP: `python3 scripts/utilities/validate_nlp.py <file>`
- Check audio: `ffprobe -v error -show_format -show_streams <file>`

Prefer:
- Running specific test files over the full suite when iterating.
- Adding temporary `print()` with clear tags like `[DEBUG]` or `[TRACE]`.

---

## Debugging Tools (MCP / Extensions)

When debugging, you MAY and SHOULD use these tools:

- **Serena MCP (semantic code tools)**
  - Use to find symbols, references, and make targeted edits.
- **Glob/Grep** for file discovery and pattern matching.
- **Any logging or monitoring tools** documented in this repo.

Prefer Serena for static analysis and refactors.
Use logging for runtime issues that require tracing execution.

---

## Known Pitfalls

### Audio Pipeline
- Voice is generated into `sessions/<id>/output/voice.mp3`.
- Enhanced voice at `sessions/<id>/output/voice_enhanced.mp3`.
- If final audio is silent: check sample rates and ffmpeg logs.
- If audio clips: verify stem levels (-6dB for voice/binaural).

### SSML Generation
- Never use `rate` below 1.0 — sounds robotic with Neural2 voices.
- Use `<break>` tags for pacing, not speaking rate.
- SFX markers `[SFX: ...]` must be on their own lines.

### Python Scripts
- Always activate venv before running: `source venv/bin/activate`
- Google Cloud auth: ensure `GOOGLE_APPLICATION_CREDENTIALS` is set.
- FFmpeg must be installed and in PATH.

### Session Structure
- All session files under `sessions/{name}/`
- Working files: `sessions/{name}/working_files/`
- Output files: `sessions/{name}/output/`
- Never mix working and output directories.

---

## Past Bugs & Lessons

*Add postmortems here as bugs are fixed:*

- 2025-12-02: Mixer normalization bug in `mixer.py:82-84`
  - Root cause: Checked dtype after conversion, not before
  - Lesson: Save original dtype before any conversion
  - Fix: Check `original_dtype` before converting to float32

---

# Essential Commands Reference

## Session Workflow

```bash
# Activate environment
source venv/bin/activate

# Create new session
./scripts/utilities/create_new_session.sh "session-name"

# Generate voice from SSML
python3 scripts/core/generate_voice.py \
    sessions/{session}/working_files/script_voice_clean.ssml \
    sessions/{session}/output

# Build complete session
python3 scripts/core/build_session.py sessions/{session}
```

## Audio Mixing (Copy-Paste Ready)

```bash
# Standard 3-stem mix (voice + binaural + sfx)
ffmpeg -y \
  -i sessions/{session}/output/voice_enhanced.wav \
  -i sessions/{session}/output/binaural_dynamic.wav \
  -i sessions/{session}/output/sfx_track.wav \
  -filter_complex \
    "[0:a]volume=-6dB[voice]; \
     [1:a]volume=-6dB[bin]; \
     [2:a]volume=0dB[sfx]; \
     [voice][bin][sfx]amix=inputs=3:duration=longest:normalize=0[mixed]" \
  -map "[mixed]" \
  -acodec pcm_s16le \
  sessions/{session}/output/session_mixed.wav
```

## Hypnotic Post-Processing (REQUIRED FOR ALL SESSIONS)

Apply psychoacoustic mastering after mixing. This is **mandatory** for all sessions.

```bash
# Standard hypnotic post-processing (uses session_mixed.wav automatically)
python3 scripts/core/hypnotic_post_process.py --session sessions/{session}/

# With custom settings
python3 scripts/core/hypnotic_post_process.py --session sessions/{session}/ \
    --warmth 0.3 --echo-delay 200

# Disable specific effects
python3 scripts/core/hypnotic_post_process.py --session sessions/{session}/ \
    --no-echo --no-cuddle
```

**Enhancements Applied (Triple-Layer Hypnotic Presence):**
| Enhancement | Description | Default |
|-------------|-------------|---------|
| Tape Warmth | Analog saturation | 25% drive |
| De-essing | Sibilance reduction (4-8 kHz) | Always on |
| Whisper Overlay | Layer 2: ethereal presence | -22 dB |
| Subharmonic | Layer 3: grounding presence | -12 dB |
| Double-Voice | Subliminal presence | -14 dB, 8ms delay |
| Room Tone | Gentle reverb | 4% wet |
| Cuddle Waves | Amplitude modulation | 0.05 Hz, ±1.5 dB |
| Echo | Subtle depth | 180ms, 25% decay |

**Output:** `{session}_MASTER.mp3` (320 kbps) + `{session}_MASTER.wav` (24-bit)

## Validation

```bash
# Validate SSML
python3 scripts/utilities/validate_ssml.py sessions/{session}/working_files/script.ssml

# Validate NLP patterns
python3 scripts/utilities/validate_nlp.py sessions/{session}/working_files/script.ssml

# Check audio levels
ffprobe -v error -show_format sessions/{session}/output/voice_enhanced.mp3

# Validate stock image licenses
python3 scripts/utilities/validate_image_licenses.py sessions/{session}/
python3 scripts/utilities/validate_image_licenses.py --all  # Check all sessions
```

## Thumbnail Generation

```bash
# Generate thumbnail with defaults (uses manifest for metadata)
python3 scripts/core/generate_thumbnail.py sessions/{session}/

# With specific template and palette
python3 scripts/core/generate_thumbnail.py sessions/{session}/ \
    --template portal_gateway \
    --palette sacred_light

# With custom title/subtitle
python3 scripts/core/generate_thumbnail.py sessions/{session}/ \
    --title "COSMIC JOURNEY" \
    --subtitle "Into the Divine Light" \
    --features "432Hz" "Theta"
```

## Scene Image Generation (DEFAULT: Stable Diffusion)

Generate scene images for video using local Stable Diffusion AI (default) or Midjourney prompts.

### Primary Method: Stable Diffusion (Default)

```bash
# Generate all scene images using SD (default, recommended)
python3 scripts/core/generate_scene_images.py sessions/{session}/

# With more steps for better quality (slower)
python3 scripts/core/generate_scene_images.py sessions/{session}/ --steps 20

# Force regenerate existing images
python3 scripts/core/generate_scene_images.py sessions/{session}/ --force

# Generate both SD images AND Midjourney prompts
python3 scripts/core/generate_scene_images.py sessions/{session}/ --with-prompts

# Custom style preset
python3 scripts/core/generate_scene_images.py sessions/{session}/ --style cosmic_journey
```

### Alternative: Midjourney Prompts Only

```bash
# Generate Midjourney prompts (no local generation)
python3 scripts/core/generate_scene_images.py sessions/{session}/ --midjourney-only
```

This creates `midjourney-prompts.md` with copy-paste prompts for Midjourney.

### Alternative: Stock Images (Unsplash/Pexels/Pixabay)

Source images from free stock photo platforms with built-in license tracking.

```bash
# Interactive mode: walks through each scene, opens browser, guides documentation
python3 scripts/core/generate_scene_images.py sessions/{session}/ --method stock

# Use specific platform (default: unsplash)
python3 scripts/core/generate_scene_images.py sessions/{session}/ --method stock --platform pexels

# Non-interactive: generate search guide markdown only
python3 scripts/core/generate_scene_images.py sessions/{session}/ --method stock --stock-guide
```

**Interactive mode features:**
- Opens search URLs in browser for each scene
- Suggests search queries based on scene content
- Guides through download and license documentation
- Automatically processes images to 1920x1080
- Creates/updates `license_manifest.yaml`

**Platforms supported:**
| Platform | Best For | Commercial Use |
|----------|----------|----------------|
| Unsplash | Nature, landscapes | YES (no attribution required) |
| Pexels | General stock | YES (no attribution required) |
| Pixabay | AI-generated, abstract | YES (no attribution required) |

**See also:** [docs/STOCK_IMAGE_SOP.md](docs/STOCK_IMAGE_SOP.md) for complete sourcing workflow.

### Style Presets

| Preset | Best For | Key Elements |
|--------|----------|--------------|
| `neural_network` | Neural/tech themes | Cyan/magenta glow, sacred geometry |
| `sacred_light` | Divine/spiritual | Golden light, ethereal atmosphere |
| `cosmic_journey` | Space/astral | Nebula, starfields, purple/blue |
| `garden_eden` | Nature/paradise | Lush green, golden light, water |
| `ancient_temple` | Historical/mystical | Torchlight, carved stone, sacred symbols |
| `celestial_blue` | Heavenly/peaceful | Soft blue light, clouds, ethereal |

Style is auto-detected from session name if not specified.

### Performance Notes

- **SD generation**: ~50-60 seconds per image on CPU at 15 steps
- **Resolution**: 512×288 base, upscaled to 1920×1080 via Lanczos
- **Model**: SD 1.5 pruned (~4GB, auto-downloaded if not present)
- **Local model path**: `~/sd-webui/models/Stable-diffusion/sd-v1-5-pruned-emaonly.safetensors`

### Output Locations

| Output | Location |
|--------|----------|
| Scene images for video | `sessions/{session}/images/uploaded/` |
| Midjourney prompts | `sessions/{session}/midjourney-prompts.md` |
| Stock image cache | `sessions/{session}/images/stock_cache/` |
| License manifest | `sessions/{session}/images/license_manifest.yaml` |
| Stock search guide | `sessions/{session}/stock-image-guide.md` |

---

## Session Cleanup (Stage 8 - Run After YouTube Upload)

Remove intermediate files and free disk space while preserving deliverables.

```bash
# Dry run first (see what will be removed)
python3 scripts/core/cleanup_session.py sessions/{session}/ --dry-run

# Run actual cleanup
python3 scripts/core/cleanup_session.py sessions/{session}/
```

**Preserved:** `*_MASTER.mp3`, `youtube_package/`, `video/session_final.mp4`, `manifest.yaml`, scripts, source images

**Removed:** All `.wav` files, `voice.mp3`, `voice_enhanced.mp3`, duplicate markdowns, `solid_background.mp4`

**Typical savings:** ~85% reduction (900MB → 115MB per session)

---

## Website Upload (Stage 9 - Optional)

Upload completed sessions to https://www.salars.net/dreamweavings for public access.

**Environment Setup:**
```bash
# Add to .env file
SALARSU_API_TOKEN=your-api-token
BLOB_READ_WRITE_TOKEN=your-vercel-blob-token
```

**Commands:**
```bash
# Dry run first (validate without uploading)
python3 scripts/core/upload_to_website.py --session sessions/{session}/ --dry-run

# Upload to production
python3 scripts/core/upload_to_website.py --session sessions/{session}/ --no-git

# Override category detection
python3 scripts/core/upload_to_website.py --session sessions/{session}/ --category cosmic-space
```

**What Gets Uploaded:**
| File Type | Max Size | Destination |
|-----------|----------|-------------|
| Audio (.mp3) | 100 MB | Vercel Blob |
| Video (.mp4) | 500 MB | Vercel Blob |
| Thumbnail (.png) | 10 MB | Vercel Blob |
| Subtitles (.vtt) | 1 MB | Vercel Blob |

**Category Auto-Detection:**
Categories are auto-detected from session keywords:
- `nature-forest`: forest, nature, garden, eden
- `cosmic-space`: cosmic, space, star, astral
- `healing`: healing, restore, repair
- `shadow-work`: shadow, dark, unconscious
- `archetypal`: archetype, journey, guide
- `sacred-spiritual`: sacred, divine, spiritual
- `confidence`: confidence, power, strength, courage
- `relaxation`: relax, sleep, calm

**Output:**
- Session available at: `https://www.salars.net/dreamweavings/{slug}`
- Media stored in Vercel Blob
- Database record in Neon PostgreSQL

**Batch Upload Pattern:**
```bash
# Upload multiple sessions
for session in atlas-starship iron-soul-forge forest-of-lost-instincts; do
  echo "=== Uploading $session ==="
  python3 scripts/core/upload_to_website.py --session sessions/$session/ --no-git
done
```

**Required Files for Upload:**
| File | Required | Fallback Paths |
|------|----------|----------------|
| Audio | Yes | `*_MASTER.mp3` → `*_final.mp3` → `final.mp3` |
| Video | No | `youtube_package/final_video.mp4` → `video/session_final.mp4` |
| Thumbnail | Yes | `youtube_thumbnail.png` → `youtube_package/thumbnail.png` |
| Subtitles | No | `youtube_package/subtitles.vtt` → `output/subtitles.vtt` |

**Troubleshooting:**
| Issue | Cause | Solution |
|-------|-------|----------|
| "Missing master audio" | Non-standard naming | `cp final.mp3 {session}_MASTER.mp3` |
| 404 on page | Missing dynamic route | Need `/dreamweavings/[slug]/page.tsx` in frontend |
| API 401 Unauthorized | Token mismatch | Check `DREAMWEAVING_API_TOKEN` in both envs |
| Client crash on archetypes | JSONB objects vs strings | Frontend handles both types now |

**Serena Memory:** See `website_upload_deployment` for complete architecture and troubleshooting guide.

---

## Video Image Generation (Overlays, Titles, etc.)

Generate supporting video images (title cards, overlays, etc.) using procedural PIL generation:

```bash
# Generate ALL video overlay images
python3 scripts/core/generate_video_images.py sessions/{session}/ --all

# Generate specific image types only
python3 scripts/core/generate_video_images.py sessions/{session}/ \
    --title-card --section-slides --outro --social-preview

# With custom palette (match to session theme)
python3 scripts/core/generate_video_images.py sessions/{session}/ \
    --all --palette volcanic_forge
```

**Generated image types:**
| Type | Dimensions | Purpose |
|------|------------|---------|
| `title_card.png` | 1920×1080 | Video intro screen |
| `sections/section_*.png` | 1920×1080 | Chapter transitions |
| `outro.png` | 1920×1080 | End screen with CTA zones |
| `lower_thirds/*.png` | 1920×1080 | Transparent overlay bars |
| `chapters/chapter_*.png` | 1920×1080 | Numbered chapter cards |
| `social_preview.png` | 1080×1080 | Instagram/social sharing |

**Available palettes:** `sacred_light`, `cosmic_journey`, `garden_eden`, `ancient_temple`, `neural_network`, `volcanic_forge`, `celestial_blue`

**Output location:** `sessions/{session}/output/video_images/`

---

# Claude's Operating Rules for This Project

1. **Read before modifying** - Never change code without reading it first
2. **Minimal diffs only** - Change exactly what's needed, nothing more
3. **Track with TodoWrite** - Use todo list for multi-step tasks
4. **Validate immediately** - Run validation after any change
5. **Use enhanced voice** - Always `voice_enhanced.mp3`, never raw `voice.mp3`
6. **Check Serena memories** - For detailed procedures, read the memories first
7. **Follow stem levels** - Voice: -6dB, Binaural: -6dB, SFX: 0dB
8. **SSML rate = 1.0** - Never use slow rates, use breaks for pacing
9. **Ask when unclear** - Request context instead of guessing
10. **Update knowledge** - Add lessons learned after fixing bugs

---

# Vibe-Coding Principles

Flow-state programming principles for creative, maintainable code.

## Set the Atmosphere First

- Establish internal calm before coding sessions
- Set clear intention: *"I am here to shape clarity, simplicity, and elegance."*
- For Dreamweaver work: align with the sacred, mythic tone of the content

## Code as Conversation

- Use variable and function names that *speak* clearly
- If a function reads like a sentence, you're on the right track
- Prefer narrative naming:
  - `collect_user_input()`
  - `prepare_audio_stems()`
  - `mix_session_audio()`

## Whitespace as Rhythm

- Think of whitespace like musical rests
- Use space intentionally to create:
  - Visual breathing room
  - Sections of thought
  - Natural pacing
- A file should "feel walkable" with your eyes

## Sculpt, Don't Just Build

Follow this refinement pattern:

1. **Rough draft** - Get the idea out raw
2. **Clarify** - Improve logic and remove noise
3. **Aesthetic sweep** - Naming, spacing, comments
4. **Micro-optimize** - Only if needed

This mirrors creative writing more than engineering.

## Developer Ergonomics

Choose structures that reduce friction:

- Predictable patterns
- Early returns instead of nested conditionals
- Short, pure functions
- If code feels *effortless* to read, it's good vibe code

## Emotionally Contained Functions

Each block should express *one feeling* or *one intention*:

- "Gather everything."
- "Transform it."
- "Send it off."
- "Handle the mess."

This leads to natural, modular abstractions.

## Flow-Driven Iteration

- Stay in flow by postponing deep debugging until after creative bursts
- Mark issues with `# TODO:` or `# FIXME:` and continue
- When flow wanes, shift into rational-engineering mode
- Don't let perfect be the enemy of done

## Comments as Whispered Intentions

Short, gentle comments explaining *why*, not *what*:

```python
# smooth the edges so later mixing feels clean
audio = apply_gentle_compression(audio)
```

Comments should invite future collaboration, not clutter.

## Commit Messages as Story Beats

Each commit is a moment in the project's story:

- "Clean up the rough edges"
- "Introduce transformation pipeline"
- "Rewrite data layer for clarity"

## End Sessions with a Soft Landing

Final action each coding session:

1. Document what you did
2. Describe next steps
3. Leave a clear "on-ramp" for future work

This preserves context across sessions.

## Vibe-Coding Daily Reminder

```
VIBE CODING CHECKLIST
✓ Breathe → Set atmosphere
✓ Clear intention for this session
✓ Name things like a storyteller
✓ Let whitespace shape rhythm
✓ Code → sculpt → refine → polish
✓ Keep functions emotionally simple
✓ Preserve flow over perfection
✓ Comments explain "why"
✓ Commit messages tell the story
✓ Leave a clear path for future me
```

---

# Claude's Behavior Model for Dreamweaver

Claude should embody these roles depending on context:

| Role | When Active |
|------|-------------|
| **Creative Director** | Designing journey themes, archetypes, emotional arcs |
| **Technical Script Engineer** | Writing and debugging SSML |
| **Audio Architect** | Binaural specs, mixing plans, soundscape design |
| **Cinematic Visionary** | Midjourney prompts, visual storytelling |
| **Production Pipeline Manager** | Coordinating full builds, tracking dependencies |
| **Editorial Assistant** | YouTube metadata, descriptions, SEO |

## Default Behaviors

Claude should proactively suggest:

- Richer imagery and deeper archetypal resonance
- Cleaner code and better file organization
- Improvements without being asked

## The "Continue" Pattern

When the user says "continue," Claude should automatically:

1. Refine what was just created
2. Deepen the content
3. Expand where appropriate
4. Polish for production quality
5. Cross-integrate with other session elements
6. Prepare next deliverables

---

# Production Templates

## Binaural Design Template

```yaml
binaural:
  base_frequency: 200       # Carrier frequency (Hz)
  beat_frequency: 7.0       # Target brainwave (Hz)
  left_channel: 200         # Base frequency
  right_channel: 207        # Base + beat frequency

ambient_layers:
  - name: "low wind"
    level: -12dB
  - name: "deep choir pad"
    level: -18dB
    reverb: 20%
  - name: "crystalline tones"
    placement: "chapter points"

brainwave_targets:
  alpha: 8-12 Hz    # Soft induction, light relaxation
  theta: 4-7 Hz     # Deep journeying, visualization
  delta: 0.5-3 Hz   # Deepest states, cosmic experiences
```

## Midjourney Prompt Template

```
/imagine prompt: a mystical [THEME] scene featuring [SUBJECT],
[ATMOSPHERE] lighting with [COLOR_PALETTE] tones,
camera: 35mm cinematic | lighting: volumetric ethereal,
style: cinematic-ritualistic, sacred geometry elements,
--ar 16:9 --style raw --v 6.1

Variables:
- THEME: Eden garden, Atlantean temple, cosmic void, etc.
- SUBJECT: angelic figure, ancient doorway, crystalline structure
- ATMOSPHERE: golden hour, moonlit, bioluminescent
- COLOR_PALETTE: gold/sapphire/amethyst, silver/violet/deep blue
```

## SSML Section Header Template

```xml
<!-- ═══════════════════════════════════════════════════════════════ -->
<!-- SECTION: [SECTION_NAME] -->
<!-- Duration: [X] minutes | Pitch: [X]st | Purpose: [PURPOSE] -->
<!-- ═══════════════════════════════════════════════════════════════ -->

<prosody rate="1.0" pitch="[X]st">
    [Content...]
</prosody>
<break time="[X]s"/>
```

---

# YouTube Thumbnail Design System

> **Full Guide**: See [docs/THUMBNAIL_DESIGN_GUIDE.md](docs/THUMBNAIL_DESIGN_GUIDE.md)

## Core Principle: 200x112 Pixel Clarity

Design for recognition within **0.2 seconds** at mobile preview size.

## The 10 Commandments of High-CTR Thumbnails

| # | Principle | Implementation |
|---|-----------|----------------|
| 1 | **Strong Visual Hierarchy** | Face → Text → Symbol → Background |
| 2 | **Big Emotions Win** | Exaggerated expressions or luminous focal points |
| 3 | **Curiosity Gap** | Raise a question but don't answer it |
| 4 | **High Contrast Color Blocking** | Hot accents (gold, amber) on cold backgrounds |
| 5 | **Short Text, Big Font** | 2-5 words max, bold sans-serif, white with glow |
| 6 | **Mobile-First** | Subject fills 40-60% of frame, no thin fonts |
| 7 | **Pattern Disruption** | Look visually different from surrounding videos |
| 8 | **Pose Language** | Serene, receptive, transcendent gestures |
| 9 | **Consistent Branding** | Same colors, fonts, glow style across all videos |
| 10 | **A/B Testing Mindset** | Always iterate based on performance |

## Template Selection

| Template | Best For | Key Feature |
|----------|----------|-------------|
| `portal_gateway` | Eden pathworkings, cosmic journeys | Luminous center, dark vignette |
| `sacred_symbol` | Tree of Life, chakras, geometry | Central glowing symbol |
| `journey_scene` | Gardens, temples, vistas | Full-frame with text overlay |
| `abstract_energy` | Neural themes, brainwaves | Flowing energy patterns |

## Color Palettes

| Palette | Primary | Secondary | Background | Best For |
|---------|---------|-----------|------------|----------|
| `sacred_light` | Gold #FFD700 | Cream #F4E4BC | Cosmic #0A0A1A | Divine, spiritual |
| `cosmic_journey` | Purple #9B6DFF | Blue #64B5F6 | Space #0D0221 | Cosmic, astral |
| `garden_eden` | Emerald #50C878 | Gold #FFD700 | Forest #0F2818 | Nature, Eden |
| `ancient_temple` | Antique Gold #D4AF37 | Bronze #8B4513 | Shadow #1A0F0A | Historical, temple |
| `neural_network` | Cyan #00D4FF | Purple #9B6DFF | Void #0A0A1A | Tech, neural |

## Zone Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ OUTER 10%: Safe margin (avoid critical content)                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ TOP 30%: Title Zone (main text with glow)               │   │
│   ├─────────────────────────────────────────────────────────┤   │
│   │                                                         │   │
│   │ CENTER 40%: Focal Zone                                  │   │
│   │ - Main visual element (portal, symbol, figure)          │   │
│   │ - Highest contrast area                                 │   │
│   │                                                         │   │
│   ├─────────────────────────────────────────────────────────┤   │
│   │ BOTTOM 15%: Badge Zone                                  │   │
│   │ [Feature Badge]                         [Duration]      │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Technical Specifications

| Property | Value |
|----------|-------|
| Dimensions | 1280 x 720 pixels |
| Aspect Ratio | 16:9 |
| Format | PNG (quality) or JPEG (95) |
| File Size | Under 2MB |
| Title Font | 80-120px, bold, white with glow |
| Badge Font | 28-35px, semi-transparent background |

## Thumbnail Generation Command

```bash
# Standard generation (reads manifest for metadata)
python3 scripts/core/generate_thumbnail.py sessions/{session}/

# With template and palette
python3 scripts/core/generate_thumbnail.py sessions/{session}/ \
    --template portal_gateway \
    --palette sacred_light

# Custom title and features
python3 scripts/core/generate_thumbnail.py sessions/{session}/ \
    --title "EDEN GATEWAY" \
    --subtitle "Into the Garden of Light" \
    --features "432Hz" "Theta" \
    --duration "25:30"
```

## Midjourney Prompt for Thumbnail Base Images

```
[SESSION_THEME] scene with [CENTRAL_FOCAL_ELEMENT],
ethereal [LIGHTING_TYPE] lighting,
[MOOD] atmosphere,
sacred mystical quality,
dark edges fading to luminous center,
cinematic composition,
space for text overlay in top third,
hyper-detailed, 8k resolution,
--ar 16:9 --v 6.1 --s 750 --style raw
```

## Quality Checklist

Before finalizing any thumbnail:

- [ ] Readable at 200x112 pixels (mobile preview size)
- [ ] Title visible and legible with proper contrast
- [ ] Single clear focal point in center zone
- [ ] High contrast between text and background
- [ ] No critical content in outer 10% margins
- [ ] Duration badge doesn't overlap YouTube's timestamp
- [ ] Colors pop against both YouTube dark and light modes
- [ ] Evokes curiosity without misleading

---

# Sacred Digital Dreamweaver – Serena MCP Framework

## Overview

This framework tells Claude Code exactly how to use **Serena MCP tools** to design and build Sacred Digital Dreamweaver journeys end-to-end. The Dreamweaver system produces **hypnotic audiovisual journeys** using:

- Written mystical journeys (structured sections)
- SSML scripts for Google Cloud TTS
- Binaural beat + sound-effect "audio beds"
- Image prompts/storyboards (Midjourney or AI-generated)
- YouTube-ready packages (title, description, tags, chapters)

**Key Principle:** Aggressively prefer Serena MCP tools over stuffing huge context into prompts.

---

## 1. Session Lifecycle & Mental Model

Treat each Dreamweaver project as a **session** with this lifecycle:

### 1.1 Design the Journey Concept
- **Theme**: Garden of Eden pathworking, Enochian heavenly tour, Atlantis temple, Christic heart-fire, etc.
- **Depth Level**: Layer1 | Layer2 | Layer3 | Ipsissimus
- **Duration Target**: 20–30 minutes typical

### 1.2 Generate Structured Journey Outline
- **Sections**: pre-talk, induction, deepening, journey, helm (deepest), integration, post-hypnotic
- **Archetypes**: spiritual, mythic, historical, futuristic
- **Narrative beats and emotional arc**

### 1.3 Generate SSML Sections for Google Cloud TTS
- Different speech profiles for each section type
- Use `<break>` tags, `rate="1.0"`, `pitch` to shape trance

### 1.4 Design Audio Bed
- Binaural beat progression (Hz over time)
- Base ambience (Eden garden, starship, cathedral, desert canyon)
- Timed sound effects for key moments

### 1.5 Assemble YouTube/Web Package
- Title, description, tags, chapters
- Thumbnail prompt(s)
- Key benefits and disclaimers

### Workflow Pattern
Always work in clear phases:
```
PLAN → TOOL CALLS → WRITE/EDIT FILES → SUMMARIZE NEXT STEPS
```

---

## 2. Session File Structure

Each session follows this structure:

```
sessions/<session-slug>/
├── manifest.yaml           # Session configuration (JSON Schema validated)
├── outline.json            # Structured journey outline (NEW)
├── notes.md                # Design notes, archetypes, special instructions
├── midjourney-prompts.md   # Image generation prompts
├── youtube_package.md      # Title, description, tags, chapters
├── working_files/
│   ├── script_production.ssml  # Full SSML with SFX markers
│   ├── script_voice_clean.ssml # SSML stripped of SFX for TTS
│   ├── script_sections/        # Per-section SSML (NEW)
│   │   ├── 01_pre_talk.ssml
│   │   ├── 02_induction.ssml
│   │   ├── 03_deepening.ssml
│   │   ├── 04_journey.ssml
│   │   ├── 05_helm_deepest.ssml
│   │   ├── 06_integration.ssml
│   │   └── 07_post_hypnotic.ssml
│   └── audio_plan.json     # Binaural + FX timeline (NEW)
├── images/
│   └── uploaded/           # User-provided PNGs from Midjourney
└── output/
    ├── voice.mp3           # Raw TTS output
    ├── voice_enhanced.mp3  # Production voice (USE THIS)
    ├── binaural_dynamic.wav
    ├── sfx_track.wav
    ├── session_mixed.wav
    └── final_master.mp3
```

**Naming Convention**: Use kebab-case slugs like `garden-of-eden-pathworking-001`

---

## 3. Serena MCP Tools for Dreamweaver

Use these Serena memories and tools as **first-class actions** for Dreamweaver work:

### 3.1 Serena Memories (Read Before Work)

| Memory | When to Read |
|--------|--------------|
| `dreamweaver_journey_design` | Before creating new journey outlines |
| `audio_production_methodology` | Any audio mixing/mastering task |
| `script_production_workflow` | Writing or editing SSML scripts |
| `voice_pacing_guidelines` | Quick voice/prosody reference |
| `session_learnings_system` | Before generating new sessions |
| `dreamweaving_project_overview` | Understanding project architecture |

### 3.2 Conceptual Tool Workflows

These describe the *workflow patterns* to follow. When implementing these, use Serena's code tools (`find_symbol`, `replace_symbol_body`, etc.) and file operations.

#### `dreamweaver.generate_journey_outline` (Pattern)

**Use when:**
- Starting a new session from a theme
- Restructuring an existing journey

**Process:**
1. Read `prompts/hypnotic_dreamweaving_instructions.md` for structure
2. Read `knowledge/lessons_learned.yaml` for past insights
3. Generate outline with sections:
   - `id`, `label`, `duration_minutes`, `archetypes[]`, `purpose`
4. Save to `sessions/<session-slug>/outline.json`
5. Render as Markdown for user review

**Outline Schema:**
```json
{
  "theme": "Garden of Eden Pathworking",
  "duration_target": 30,
  "depth_level": "Layer2",
  "sections": [
    {
      "id": "pre_talk",
      "label": "Pre-Talk & Safety",
      "duration_minutes": 3,
      "purpose": "Ground the listener, establish safety",
      "archetypes": ["Guide", "Protector"]
    },
    {
      "id": "induction",
      "label": "Progressive Relaxation",
      "duration_minutes": 5,
      "purpose": "Lead into trance state",
      "archetypes": ["Healer"]
    }
    // ... more sections
  ]
}
```

#### `dreamweaver.generate_ssml_section` (Pattern)

**Use when:**
- Generating or revising SSML for a specific section

**Parameters:**
- `section_id`: matches outline (e.g., `pre_talk`, `induction`)
- `section_purpose`: what this section accomplishes
- `tone`: calm | mystical | authoritative | playful
- `speech_profile`: one of the profiles below

**Speech Profiles:**

| Profile | Pitch | Breaks | Purpose |
|---------|-------|--------|---------|
| `pre_talk` | 0st | 700ms-1.0s | Normal, grounded |
| `induction` | -2st | 1.0s-1.7s | Calming, deeper |
| `deep_induction` | -2st | 1.7s-2.5s | Very calm |
| `journey` | -1st | 1.0s-2.0s | Immersive |
| `helm_deepest` | -2st | 2.0s-3.0s | Deepest trance |
| `integration` | -1st | 1.5s-2.0s | Returning |
| `post_hypnotic` | 0st | 700ms-1.0s | Alert, grounded |

**CRITICAL**: Always use `rate="1.0"`. Never slow the rate.

**Output:**
- Complete `<speak>...</speak>` block
- Save to `working_files/script_sections/<nn>_<section_id>.ssml`

#### `dreamweaver.suggest_audio_bed` (Pattern)

**Use when:**
- Designing binaural + ambience + SFX plan

**Parameters:**
- `target_state`: relaxation | trance | deep_trance | integration
- `duration_minutes`: length of journey
- `environment`: Eden garden, crystal city, Atlantis temple, etc.

**Output Schema (`audio_plan.json`):**
```json
{
  "binaural": {
    "carrier_frequency": 200,
    "start_hz": 10,
    "end_hz": 4,
    "transitions": [
      {"time": "0:00", "freq": 10, "state": "alpha"},
      {"time": "5:00", "freq": 7, "state": "theta"},
      {"time": "15:00", "freq": 4, "state": "deep_theta"},
      {"time": "25:00", "freq": 7, "state": "theta"},
      {"time": "28:00", "freq": 10, "state": "alpha"}
    ]
  },
  "ambience": {
    "base": "garden_with_water",
    "layers": ["distant_birds", "gentle_wind"]
  },
  "sfx_timeline": [
    {"time": "0:30", "effect": "soft_chime", "duration": 2},
    {"time": "5:00", "effect": "deep_bell", "duration": 4},
    {"time": "15:00", "effect": "ethereal_tone", "duration": 3}
  ]
}
```

#### `dreamweaver.generate_youtube_package` (Pattern)

**Use when:**
- Preparing session for YouTube publication

**Process:**
1. Read manifest and script for context
2. Generate compelling title (honest but engaging)
3. Write description with:
   - Hook paragraph
   - Benefits and experience description
   - Disclaimers (not medical advice, safe environment)
   - Spiritual framing
4. Suggest 10-15 relevant tags
5. Generate chapter timestamps based on sections
6. Create 2-3 thumbnail prompt ideas

**Output to `youtube_package.md`**

---

## 4. Standard Workflows

### 4.1 New Dreamweaver Session

When creating a new journey:

1. **Clarify & Name the Session**
   - Propose kebab-case `session-slug`
   - Confirm duration target and depth level
   - Confirm archetypes or mythic frames

2. **Check Knowledge Base**
   - Read `knowledge/lessons_learned.yaml`
   - Read `knowledge/best_practices.md`
   - Check for similar sessions as reference

3. **Generate Journey Outline**
   - Follow `dreamweaver.generate_journey_outline` pattern
   - Save to `outline.json`
   - Create `notes.md` with design rationale

4. **Generate SSML Per Section**
   - For each section in order:
     - Follow `dreamweaver.generate_ssml_section` pattern
     - Save to `working_files/script_sections/`
   - Generate combined `script_production.ssml`
   - Generate `script_voice_clean.ssml` (SFX markers stripped)

5. **Design Audio Bed**
   - Follow `dreamweaver.suggest_audio_bed` pattern
   - Save to `working_files/audio_plan.json`

6. **Generate Image Prompts**
   - Create `midjourney-prompts.md` with:
     - 16:9 aspect ratio specifications
     - 8k detail level
     - Atmosphere, mood, sacred light
     - One prompt per major section

7. **Prepare YouTube Package**
   - Follow `dreamweaver.generate_youtube_package` pattern
   - Save to `youtube_package.md`

8. **Summarize & Hand Off**
   - List all created files
   - State journey intention and key archetypes
   - Provide next steps for user:
     - Create images on Midjourney
     - Run TTS generation
     - Run audio mixing
     - Assemble video

### 4.2 Refining Existing Session

When improving an existing session:

1. **Scan Structure**
   - Read `outline.json`, `manifest.yaml`, `script_production.ssml`
   - Check `audio_plan.json` and `notes.md`

2. **Clarify Intent**
   - What needs improvement?
     - Deeper trance?
     - More natural speech?
     - Stronger theological framing?
     - Better pacing?
     - Longer/shorter runtime?

3. **Propose Surgical Changes**
   - List specific sections to regenerate
   - Describe prosody adjustments
   - Note audio bed modifications

4. **Execute Changes**
   - Only regenerate affected sections
   - Update `audio_plan.json` if binaural curve changes
   - Add changelog entry to `notes.md`

5. **Maintain Consistency**
   - Keep tone consistent with other journeys
   - Respect established archetypes unless explicitly changing

### 4.3 Audio Production Workflow

When building audio for a session:

1. **Validate Prerequisites**
   - Check `script_voice_clean.ssml` exists (no SFX markers)
   - Verify manifest.yaml is valid
   - Confirm venv is activated

2. **Generate Voice**
   ```bash
   python3 scripts/core/generate_voice.py \
       sessions/{session}/working_files/script_voice_clean.ssml \
       sessions/{session}/output
   ```

3. **Mix Audio** (always use these levels)
   - Voice: -6 dB
   - Binaural: -6 dB
   - SFX: 0 dB
   - Use `normalize=0` in amix

4. **Master Final Output**
   - Target: -14 LUFS
   - True peak: -1.5 dBTP

5. **Quality Check**
   - Verify no clipping
   - Check binaural is audible
   - Validate SFX timing

---

## 5. Behavior Guidelines for Claude Code

### When Working on Dreamweaver Sessions

1. **Always Start with a PLAN**
   - Outline next 3-7 steps before tool calls
   - Use TodoWrite to track multi-step tasks

2. **Read Serena Memories First**
   - Check relevant memories before generating content
   - Apply lessons learned from past sessions

3. **Be Explicit About File Paths**
   - Always state exact paths when creating/editing
   - Use the session structure conventions

4. **Keep Sections Modular**
   - Maintain separate section files
   - Generate combined script from parts

5. **Optimize for Hypnotic, Natural Speech**
   - Vary sentence length and rhythm
   - Avoid robotic repetition
   - Use `<break>` for pacing, not rate changes

6. **Maintain Safety and Consent**
   - Always include safety language
   - Listener can return to wakefulness anytime
   - No coercive or unsafe suggestions

7. **Summarize and Hand Off Clearly**
   - What was done
   - Where files live
   - Next 1-2 steps for user

---

## 6. Example Shortcut Phrases

Claude should recognize and respond to these patterns:

| User Says | Claude Does |
|-----------|-------------|
| "Create a new Dreamweaver journey about [theme], [duration], [depth]" | Full session creation workflow |
| "Deepen the induction section" | Regenerate with deeper speech profile |
| "Make it more mystical/Christic/cosmic" | Adjust archetypes and language |
| "Add more sensory imagery" | Enhance visualization descriptions |
| "Generate YouTube package for this session" | Follow youtube package pattern |
| "What sessions have we done before?" | Check `sessions/` and lessons_learned |
| "Apply lessons from past sessions" | Read and integrate knowledge base |

---

## 7. Integration with Existing Tools

### Slash Commands

| Command | Dreamweaver Integration |
|---------|------------------------|
| `/new-session <name>` | Creates scaffold, triggers outline generation |
| `/generate-script <session>` | Follows SSML generation pattern |
| `/build-audio <session>` | Follows audio production workflow |
| `/full-build <session>` | Complete pipeline with all patterns |

### AI Agents

| Agent | Dreamweaver Role |
|-------|------------------|
| **Dreamweaver** | Master orchestrator, uses all patterns |
| **Script Writer** | Implements SSML generation patterns |
| **Manifest Architect** | Creates manifest from outline |
| **Audio Engineer** | Follows audio production methodology |
| **Visual Artist** | Generates Midjourney prompts from sections |

### Serena MCP Tools

Use Serena's semantic tools for:
- Finding and updating session files
- Editing SSML with precision
- Searching for patterns across sessions
- Managing knowledge base

---

## 8. Quality Rubric

When generating or reviewing Dreamweaver content, evaluate:

| Criterion | Check |
|-----------|-------|
| **Clarity** | Is the narrative easy to follow? |
| **Depth** | Does it create genuine immersion? |
| **Archetypal Coherence** | Do symbols work together? |
| **Hypnotic Pacing** | Are breaks and rhythm effective? |
| **Sensory Density** | Is visualization rich and specific? |
| **Safety** | Is consent and safety maintained? |
| **Technical Validity** | Does SSML validate? Are levels correct? |

After generating, always:
1. Self-evaluate against this rubric
2. Identify weakest area
3. Propose improvement if below standard

---

## 9. Serena Semantic Query Patterns

Use Serena's semantic retrieval to answer questions about the codebase naturally:

### Discovery Queries

| Question | Serena Tool |
|----------|-------------|
| "Where do we generate `<break>` pauses?" | `search_for_pattern` with `<break` |
| "Show all binaural mixing logic" | `find_symbol` for mixer functions |
| "Find archetype templates for Enochian journeys" | `search_for_pattern` in `sessions/` |
| "Where is voice enhancement applied?" | `find_symbol` for enhancement functions |
| "List all SSML rate transitions" | `search_for_pattern` for `rate=` |

### Refactoring Queries

| Task | Approach |
|------|----------|
| "Update all SSML to new pacing profile" | `search_for_pattern` → batch `replace_symbol_body` |
| "Standardize break durations across sections" | `find_symbol` → iterate with edits |
| "Apply new archetype to all journey sections" | `search_for_pattern` → surgical edits |

### Example Commands

```
# Find where binaural fade-in is applied
mcp__serena__search_for_pattern(
    substring_pattern="binaural.*fade",
    relative_path="scripts/core/audio"
)

# Locate all journey outline schemas
mcp__serena__find_file(
    file_mask="outline.json",
    relative_path="sessions"
)

# Find all references to a mixer function
mcp__serena__find_referencing_symbols(
    name_path="mix_audio_stems",
    relative_path="scripts/core/audio/mixer.py"
)
```

---

## 10. Batch Operations Across Sessions

When applying changes across multiple sessions:

### Pattern: Update All SSML Templates

```
1. search_for_pattern → find all affected files
2. For each file:
   a. get_symbols_overview → understand structure
   b. find_symbol with include_body=True → get current content
   c. replace_symbol_body → apply new pattern
3. Validate each file after edit
```

### Pattern: Standardize Audio Plans

```
1. find_file(file_mask="audio_plan.json") → list all
2. For each:
   a. Read current schema
   b. Apply standardized binaural curve
   c. Preserve custom SFX timing
   d. Write updated file
```

### Pattern: Cross-Session Search

```
# Find sessions using a specific archetype
mcp__serena__search_for_pattern(
    substring_pattern="Lemurian|Atlantean|Enochian",
    relative_path="sessions",
    paths_include_glob="**/outline.json"
)
```

---

## 11. Reusable Knowledge Libraries

Maintain these as centralized, reusable modules:

### Archetype Library

Location: `knowledge/archetypes/`

```yaml
# Example: knowledge/archetypes/guardian.yaml
name: Guardian
aliases: [Protector, Sentinel, Keeper]
qualities:
  - strength
  - vigilance
  - sacred duty
voice_qualities:
  pitch: "-1st"
  tone: "grounded, authoritative"
visual_elements:
  - golden armor
  - radiant shield
  - watchful gaze
soundscape:
  - deep resonant tones
  - subtle brass undertones
```

### Environment Presets

Location: `knowledge/environments/`

```yaml
# Example: knowledge/environments/eden-garden.yaml
name: Eden Garden
atmosphere: warm, golden, paradisiacal
soundscape:
  base: gentle_water_stream
  layers:
    - birdsong_distant
    - wind_through_leaves
    - crystalline_chimes
visual_palette:
  - emerald green
  - golden sunlight
  - sapphire water
  - white flowers
binaural_suggestion:
  state: alpha_theta_bridge
  frequency: 8-10 Hz
```

### Binaural Wave Presets

Location: `knowledge/binaural_presets/`

```yaml
# Example: knowledge/binaural_presets/deep-theta.yaml
name: Deep Theta Journey
carrier: 200 Hz
curve:
  - time: "0:00"
    freq: 10
    state: alpha
  - time: "5:00"
    freq: 7
    state: theta
  - time: "15:00"
    freq: 4
    state: deep_theta
  - time: "25:00"
    freq: 7
    state: theta
  - time: "30:00"
    freq: 10
    state: alpha
```

---

## 12. Division of Labor

### Serena Handles (Engineering)

- Repetitive code generation
- Pipeline maintenance
- Format standardization
- Component wiring
- Database operations
- Backend plumbing
- File orchestration
- Pattern-based edits
- Cross-file refactoring

### Claude Focuses On (Creative)

- Journey architecture
- Archetypal design
- Hypnotic cadence
- Emotional transformation
- Storytelling
- Symbolism
- World-building
- Sensory imagery
- Mystical resonance

**Principle:** Serena handles the engineering of your magic. You handle the magic itself.
