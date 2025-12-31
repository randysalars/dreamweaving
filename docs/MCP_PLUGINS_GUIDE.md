# MCP Servers & Plugins Guide for Dreamweavings

This guide documents the MCP (Model Context Protocol) servers and Claude Code plugins evaluated and **implemented** for the Dreamweavings creative workflow system.

---

## Overview

The Dreamweavings project produces hypnotic audio/video sessions using multiple specialized AI tools and workflows. This document covers:

1. **Installed Plugins** - Claude Code skills and plugins currently enabled
2. **Installed MCP Servers** - External AI services for image/audio generation
3. **MCP Implementation Plan** - Strategy for managing multiple AI tools efficiently
4. **Usage Instructions** - How to leverage these tools in the workflow

---

## Quick Start

### Start Stable Diffusion WebUI (Required for Image Generation)
```bash
./scripts/utilities/start_sd_webui.sh --background
```

### Configuration Files
- **Project MCP Config:** `config/mcp_servers.json`
- **Claude Desktop Config:** `~/.config/claude/claude_desktop_config.json`

---

## 1. Installed Claude Code Plugins

### Media Processing Skill

**Location:** `~/.claude/skills/media-processing/`

A comprehensive skill for multimedia processing using FFmpeg and ImageMagick.

**Capabilities:**
- **Video Tasks:** H.264/H.265/VP9 encoding, transcoding, HLS/DASH streaming manifests, hardware acceleration (NVENC, QSV)
- **Audio Work:** Conversion, extraction from video, format conversion, mixing
- **Image Operations:** Resizing, cropping, format conversion, effects, watermarks, batch processing

**When to Use:**
- Converting session audio between formats (WAV → MP3)
- Creating streaming-ready video versions
- Batch processing video thumbnails
- Extracting audio tracks for analysis
- Applying filters to video outputs

**Installation:**
```bash
npx claude-plugins skills install @mrgoonie/claudekit-skills/media-processing
```

**Verification:**
```bash
ls ~/.claude/skills/media-processing/
```

---

## 2. Installed MCP Servers

### 2.1 Image Generation MCP Servers

#### image-gen-mcp (LOCAL - INSTALLED)

**Status:** ✅ INSTALLED
**Location:** `/home/rsalars/Projects/image-gen-mcp/`
**Repository:** [Ichigo3766/image-gen-mcp](https://github.com/Ichigo3766/image-gen-mcp)

**Purpose:** Generate scene images directly from Claude using local Stable Diffusion WebUI (ForgeUI/AUTOMATIC-1111)

**Why Beneficial for Dreamweavings:**
- Automates Stage 5.5 scene image generation
- No per-image API costs (local processing)
- Privacy - all generation on local machine
- Direct integration with existing SD WebUI installation

**Prerequisites:**
- Stable Diffusion WebUI at `~/sd-webui/`
- WebUI running with `--api` flag

**Start SD WebUI:**
```bash
./scripts/utilities/start_sd_webui.sh --background
```

**Available Tools:**
| Tool | Description |
|------|-------------|
| `generate_image` | Text-to-image generation with prompt, negative prompt, steps, CFG, etc. |
| `get_sd_models` | List available checkpoint models |
| `set_sd_model` | Switch active model |
| `get_sd_upscalers` | List available upscaler models |
| `upscale_images` | Upscale images 4x using R-ESRGAN |

**Configuration:**
```json
// In ~/.config/claude/claude_desktop_config.json
{
  "mcpServers": {
    "image-gen-sd": {
      "command": "node",
      "args": ["/home/rsalars/Projects/image-gen-mcp/build/index.js"],
      "env": {
        "SD_WEBUI_URL": "http://127.0.0.1:7860",
        "SD_OUTPUT_DIR": "/home/rsalars/Projects/dreamweaving/sessions"
      }
    }
  }
}
```

#### Stability AI MCP Server (CLOUD - INSTALLED)

**Status:** ✅ INSTALLED (requires API key)
**Location:** `/home/rsalars/Projects/mcp-server-stability-ai/`
**Repository:** [tadasant/mcp-server-stability-ai](https://github.com/tadasant/mcp-server-stability-ai)

**Purpose:** Cloud-based SD 3.5 image generation with advanced editing capabilities

**Cost:** 25 free credits, then $0.01/credit (~$0.03-0.08 per operation)

**Available Tools:**
| Tool | Cost | Description |
|------|------|-------------|
| `generate-image` | $0.03 | Generate image from prompt |
| `generate-image-sd35` | $0.04-0.07 | SD 3.5 with advanced options |
| `remove-background` | $0.02 | Remove background |
| `outpaint` | $0.04 | Extend image in any direction |
| `search-and-replace` | $0.04 | Replace objects in image |
| `upscale-fast` | $0.01 | 4x resolution enhancement |
| `upscale-creative` | $0.25 | Up to 4K enhancement |
| `control-sketch` | $0.03 | Sketch to image |
| `control-style` | $0.04 | Style transfer |

**Setup:**
1. Get API key: https://platform.stability.ai/account/keys
2. Set environment variable: `STABILITY_AI_API_KEY`

#### Midjourney MCP Server (CLOUD)

**Purpose:** High-quality image generation through Midjourney API

**Why Beneficial for Dreamweavings:**
- Professional quality for YouTube thumbnails
- Consistent style across sessions
- Better for marketing materials

**Installation:**
```bash
claude mcp add-json midjourney '{
  "command": "uvx",
  "args": ["--from", "git+https://github.com/z23cc/midjourney-mcp", "midjourney-mcp"],
  "env": {
    "GPTNB_API_KEY": "your-api-key",
    "GPTNB_BASE_URL": "https://api.gptnb.com"
  }
}'
```

**Features:**
- Image generation from prompts
- Blending multiple images
- Upscaling results
- Aspect ratio control

### 2.2 Voice & Audio MCP Servers

#### ElevenLabs MCP Server (OFFICIAL - INSTALLED)

**Status:** ✅ INSTALLED (requires API key)
**Package:** `elevenlabs-mcp` (via uvx)
**Repository:** [elevenlabs/elevenlabs-mcp](https://github.com/elevenlabs/elevenlabs-mcp)

**Purpose:** High-quality TTS, voice cloning, transcription

**Why Beneficial for Dreamweavings:**
- Alternative voice options beyond Google TTS
- Voice cloning for custom narrator voices
- Potentially richer emotional range
- Audio transcription for VTT generation

**Available Tools:**
| Tool | Description |
|------|-------------|
| Text-to-Speech | Generate natural-sounding speech |
| Voice Cloning | Create custom voice models |
| Transcription | Speech-to-text conversion |
| Voice Manipulation | Apply effects and transformations |

**Configuration:**
```json
// In ~/.config/claude/claude_desktop_config.json
{
  "mcpServers": {
    "elevenlabs": {
      "command": "uvx",
      "args": ["elevenlabs-mcp"],
      "env": {
        "ELEVENLABS_API_KEY": "your-api-key"
      }
    }
  }
}
```

**Setup:**
1. Get API key: https://elevenlabs.io (free tier: 10k credits/month)
2. Set environment variable: `ELEVENLABS_API_KEY`

**Cost:** Free tier offers 10,000 credits/month

**Note:** Current production uses Google Cloud TTS (Neural2-H). ElevenLabs is recommended for:
- Custom cloned narrator voices
- Non-English sessions
- Emotional variation experiments

#### Multi-Provider TTS MCP Server (OPTIONAL)

**Purpose:** Unified TTS interface across multiple providers

**Repository:** https://github.com/blacktop/mcp-tts

**Features:**
- Google TTS (Gemini models)
- ElevenLabs TTS
- OpenAI TTS
- macOS native `say` command

---

## 3. MCP Implementation Strategy

### 3.1 Context Window Management

**Challenge:** At ~400-500 tokens per tool definition, loading 50+ tools consumes 20,000-25,000 tokens (most of a 32K context window).

**Solution Strategy:**

1. **Lazy Loading** - Load tool definitions only when needed for current task
2. **Category-Based Discovery** - Group tools by function (audio, image, video)
3. **Dynamic Loading/Unloading** - Activate tools based on workflow stage

### 3.2 Tool Categories for Dreamweavings

| Category | Tools | Load When |
|----------|-------|-----------|
| **Core** | Serena, Bash, Read, Edit, Write | Always loaded |
| **Audio** | ElevenLabs TTS, Google TTS | Stage 2-5 (Script → Audio) |
| **Image** | Stable Diffusion, Midjourney | Stage 5.5 (Scene Images) |
| **Video** | FFmpeg, Media Processing | Stage 6 (Video Assembly) |
| **Publishing** | YouTube API | Stage 7-9 (Packaging → Upload) |

### 3.3 Workflow Stage Tool Mapping

```
Stage 1: Creative Design      → Core tools only
Stage 2: Voice Script         → Core tools only
Stage 3: Audio Generation     → Core + Audio tools
Stage 4: Audio Mixing         → Core + Audio + Media Processing
Stage 5: Hypnotic Post-Process→ Core + Audio + Media Processing
Stage 5.5: Scene Images       → Core + Image tools (SD/MJ)
Stage 6: Video Production     → Core + Video tools
Stage 7: YouTube Packaging    → Core + Publishing tools
```

### 3.4 Tool Search Implementation

**Current Approach:** Use natural language queries to find relevant tools

```
# Example prompt patterns
"I need to generate binaural beats" → routes to audio/binaural.py
"Generate scene images for this session" → routes to SD MCP or generate_scene_images.py
"Apply hypnotic processing" → routes to hypnotic_post_process.py
```

**Future Enhancement:** Implement MCP Tool Search protocol for dynamic discovery:

```yaml
# Proposed tools/discover endpoint
tools/discover:
  category: "image-generation"
  query: "scene images dreamweaving"

# Returns only matching tools without full schemas
```

### 3.5 Programmatic Tool Calling

**Benefit:** Bundle multiple tool executions efficiently

**Example - Full Audio Build:**
```python
# Instead of 5 separate tool calls:
# 1. generate_voice
# 2. generate_binaural
# 3. generate_sfx
# 4. mix_audio
# 5. hypnotic_post_process

# Use programmatic bundling:
pipeline = AudioPipeline(session_path)
pipeline.execute([
    ("voice", {"ssml": script_path}),
    ("binaural", {"duration": duration}),
    ("sfx", {"markers": sfx_timeline}),
    ("mix", {"stems": ["voice", "binaural", "sfx"]}),
    ("master", {"target_lufs": -14})
])
```

---

## 4. Integration with Existing Workflow

### 4.1 Enhanced Pipeline Commands

**Current:**
```bash
/full-build session-name
```

**Enhanced (with MCP tools):**
```bash
/full-build session-name --image-generator=sd --voice-provider=google
```

### 4.2 Image Generation Integration

**Option A: Local Stable Diffusion (default)**
```bash
python3 scripts/core/generate_scene_images.py sessions/{session}/
```

**Option B: MCP Stable Diffusion**
```
# Via Claude conversation with SD MCP server enabled
"Generate scene images for the neural-network-navigator session using
ethereal blue and purple palette, 16:9 aspect ratio"
```

**Option C: Midjourney (quality priority)**
```bash
python3 scripts/core/generate_scene_images.py sessions/{session}/ --midjourney-only
```

### 4.3 Voice Generation Enhancement

**Production Standard (Google TTS):**
```bash
python3 scripts/core/generate_voice.py sessions/{session}/working_files/script.ssml sessions/{session}/output
```

**Alternative (ElevenLabs via MCP):**
- Use for custom cloned voices
- Use for non-English sessions
- Use for emotional variation experiments

---

## 5. Cost Optimization

### 5.1 Tool-by-Tool Costs

| Tool/Service | Cost Model | Monthly Estimate |
|--------------|------------|------------------|
| Google Cloud TTS | ~$4/million chars | ~$2-5/session |
| ElevenLabs | Free tier: 10k credits | $0 (with limits) |
| Stable Diffusion | Local GPU electricity | ~$0.01-0.05/session |
| Midjourney | Subscription + API | ~$0.20-0.50/image |

### 5.2 Recommended Configuration

| Use Case | Image Gen | Voice Gen | Est. Cost/Session |
|----------|-----------|-----------|-------------------|
| **Budget** | Local SD | Google TTS | ~$2-5 |
| **Standard** | Local SD + MJ thumbnails | Google TTS | ~$5-8 |
| **Premium** | All Midjourney | ElevenLabs clone | ~$15-25 |

---

## 6. Future Enhancements

### 6.1 Hierarchical Tool Management (When MCP 2.0 Releases)

```yaml
# Proposed category-based discovery
tools/categories:
  - name: "audio-generation"
    tool_count: 8
    description: "TTS, binaural, SFX generation"

  - name: "image-generation"
    tool_count: 4
    description: "SD, Midjourney, thumbnails"

# Load only what's needed
tools/load:
  category: "audio-generation"
```

### 6.2 Automated Tool Selection

```python
# Future: AI-powered tool routing
def route_to_tool(task_description: str) -> str:
    """Use semantic similarity to find best tool"""
    embeddings = get_tool_embeddings()
    task_embedding = embed(task_description)
    return find_nearest_tool(task_embedding, embeddings)
```

### 6.3 Workflow Templates with Tool Presets

```yaml
# .claude/workflows/full-build.yaml
name: full-build
stages:
  - name: script
    tools: [core]
  - name: audio
    tools: [core, audio, media-processing]
  - name: images
    tools: [core, stable-diffusion]
  - name: video
    tools: [core, media-processing, ffmpeg]
```

---

## 7. Troubleshooting

### MCP Server Connection Issues

```bash
# Check if server is running
curl http://localhost:7860/sdapi/v1/sd-models  # SD WebUI

# Verify MCP config
cat ~/.config/claude/claude_desktop_config.json

# Test MCP server directly
npx @anthropic-ai/mcp-server-test
```

### Plugin Not Loading

```bash
# Verify installation
ls ~/.claude/skills/

# Check skill structure
ls ~/.claude/skills/media-processing/

# Reinstall if needed
npx claude-plugins skills install @mrgoonie/claudekit-skills/media-processing --force
```

### Token Budget Exceeded

1. Reduce number of active MCP servers
2. Use category-based tool loading
3. Clear conversation history with `/clear`
4. Use subagents for isolated tasks

### Serena "Language Server Manager Not Initialized"

This error occurs when Serena's semantic code tools (`find_symbol`, `replace_symbol_body`, etc.) are used but the required language servers are not installed.

**Required Language Servers:**

```bash
# Install Python LSP
pipx install python-lsp-server

# Install Bash and YAML LSPs
npm install --prefix ~/.local bash-language-server yaml-language-server
ln -sf ~/.local/node_modules/.bin/bash-language-server ~/.local/bin/
ln -sf ~/.local/node_modules/.bin/yaml-language-server ~/.local/bin/
```

**Verify installation:**
```bash
which pylsp bash-language-server yaml-language-server
```

**After installing:**
1. Restart VS Code (this restarts the Serena MCP server)
2. Or manually kill and restart Serena processes

**Note:** Memory operations (`read_memory`, `write_memory`, `list_memories`) work without language servers - only semantic code tools require them.

---

## 8. Notion MCP Integration (Knowledge Base RAG)

### Overview

The Notion MCP server enables Claude Code to access the **Sacred Digital Dreamweaver** workspace as a canonical knowledge base. This provides:

- Real-time access to structured databases (Archetypes, Realms, Frequencies, etc.)
- Retrieval of unstructured page content (lore, philosophy, templates)
- Semantic search via embeddings pipeline

### Configuration

**Already configured in `config/mcp_servers.json`:**

```json
{
  "notion": {
    "description": "Read/write Sacred Digital Dreamweaver workspace",
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": {
      "NOTION_TOKEN": "${NOTION_TOKEN}"
    },
    "enabled": true
  }
}
```

### Setup Steps

1. **Create Notion Integration:**
   - Visit https://www.notion.so/profile/integrations
   - Click "New Integration"
   - Name: `Dreamweaving RAG`
   - Enable read permissions

2. **Copy Integration Token:**
   - Add to `.env`: `NOTION_TOKEN=ntn_your_token_here`

3. **Grant Access to Pages:**
   - Open Sacred Digital Dreamweaver page in Notion
   - Click `•••` → Connections → Add `Dreamweaving RAG`
   - Repeat for all databases and subpages

### Knowledge Tools

Three Python modules work together:

| Module | Purpose |
|--------|---------|
| `notion_knowledge_retriever.py` | Direct Notion API queries |
| `notion_embeddings_pipeline.py` | Vector database for semantic search |
| `knowledge_tools.py` | High-level query functions |

### Usage Examples

**Direct database query:**
```bash
python3 -m scripts.ai.notion_knowledge_retriever --db archetypes --filter Navigator
```

**Semantic search (requires indexing):**
```bash
# First, export and index Notion content
python3 -m scripts.ai.notion_knowledge_retriever --export knowledge/notion_export/
python3 -m scripts.ai.notion_embeddings_pipeline --index

# Then search semantically
python3 -m scripts.ai.notion_embeddings_pipeline --search "shadow healing journey"
```

**Build journey context:**
```bash
python3 -m scripts.ai.knowledge_tools --build-context Navigator "Atlantean Crystal Spine" "Gamma Flash"
```

### RAG Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Notion Workspace│────▶│  Export/Index    │────▶│  Qdrant Vector  │
│ (Real-time MCP) │     │  (notion-to-md)  │     │    Database     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                                                │
        │                                                ▼
        │              ┌──────────────────┐     ┌─────────────────┐
        └─────────────▶│ Claude Code via  │◀────│ Semantic Search │
                       │   Notion MCP     │     │   Retrieval     │
                       └──────────────────┘     └─────────────────┘
```

### Configuration File

Full configuration in `config/notion_config.yaml`:

```yaml
notion:
  integration_token: "${NOTION_TOKEN}"
  workspace_root: "1ee2bab3796d80738af6c96bd5077acf"

databases:
  archetypes:
    id: ""  # Add after creating in Notion
  realms:
    id: ""
  frequencies:
    id: ""
  rituals:
    id: ""
  lore:
    id: ""
  scripts:
    id: ""

embeddings:
  model: "text-embedding-3-small"
  chunk_size: 1000
  chunk_overlap: 200

vector_db:
  type: "qdrant"
  path: "./knowledge/vector_db"
  collection: "dreamweaving_knowledge"
```

### Dependencies

```bash
pip install notion-client openai qdrant-client pyyaml
```

### Cost Estimates

| Component | Cost |
|-----------|------|
| Notion API | Free |
| OpenAI Embeddings (initial) | ~$0.50 |
| OpenAI Embeddings (monthly) | ~$0.10 |
| Qdrant (local) | Free |

---

## References

- [Claude Plugins Marketplace](https://claude-plugins.dev/)
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-03-26)
- [ElevenLabs MCP](https://github.com/elevenlabs/elevenlabs-mcp)
- [Stable Diffusion MCP](https://mcp.so/server/stable-diffusion-mcp)
- [Midjourney MCP](https://playbooks.com/mcp/z23cc-midjourney)
- [MCP Hierarchical Tool Management Discussion](https://github.com/orgs/modelcontextprotocol/discussions/532)
- [Glama MCP Server Registry](https://glama.ai/mcp/servers/categories/image-and-video-processing)
- [Notion MCP Documentation](https://developers.notion.com/docs/mcp)
- [Official Notion MCP Server](https://github.com/makenotion/notion-mcp-server)

---

*Last Updated: December 2025*
