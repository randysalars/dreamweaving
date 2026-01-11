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
- **Project MCP Config:** `config/mcp_servers.json` **(CANONICAL)**
- **CLI MCP Config:** `mcp.json` (CLI overrides only)
- **Claude Desktop Config:** `~/.config/claude/claude_desktop_config.json`
- **User Settings:** `~/.claude/settings.json`

---

## Configuration Architecture

MCP servers are configured in multiple locations with this precedence:

1. **config/mcp_servers.json** (CANONICAL)
   - Project-specific configuration
   - Includes workflow staging
   - Tool categories
   - Single source of truth

2. **mcp.json** (CLI overrides)
   - Claude Code CLI context
   - Used for local development
   - Should defer to project config

3. **~/.claude/settings.json** (user defaults)
   - Per-user defaults
   - Serena configuration

4. **~/.config/claude/claude_desktop_config.json** (desktop)
   - Claude Desktop app only

**Best Practice:** Always edit `config/mcp_servers.json` as the canonical source. Other configs should reference or override it sparingly.

---

## Why Dreamweaving Doesn't Use Standard Development MCPs

This project uses **specialized MCP servers** instead of generic web development ones:

| Standard MCP | Why Not Used | Our Alternative |
|--------------|--------------|-----------------|
| **filesystem** | Claude Code has native file tools (Read, Write, Glob, Grep) | Serena MCP (semantic code search, superior to file search) |
| **Context7** | Generic library docs, not domain-specific | Notion MCP + dreamweaving-rag (our knowledge base) |
| **Postgres** | No database in Dreamweaving | File-based YAML/JSON configuration |
| **Shadcn** | React/Next.js UI component library | Not applicable (Python/video project) |
| **Playwright** | Web browser testing framework | FFmpeg + media-processing skill (video pipelines) |
| **Terminal** | Claude has native Bash tool | Built-in Bash tool (already available) |
| **Git/GitHub** | Claude has native git via Bash | Built-in Bash tool + git commands |
| **Vercel** | Vercel cloud deployment | Coolify (self-hosted deployment) |

**Key Principle:** We use Claude Code's built-in tools (Read, Write, Bash) for generic operations, and specialized MCPs (Serena, Notion, image-gen-sd) for domain-specific capabilities.

**Why This Is Better:**
- Lower token overhead (specialized tools are more efficient than generic)
- Domain-optimized (tools designed for creative AI content production)
- Local-first (reduced API costs with local SD, Coqui TTS)
- Workflow-aware (staged loading based on production phase)

---

## Multi-Project MCP Strategy

This project (Dreamweaving) uses **specialized MCPs** because it's a Python/video/AI content production project. However, **other projects need different tools**.

### MCP Servers by Project Type

| Project | Type | MCP Setup | Rationale |
|---------|------|-----------|-----------|
| **Dreamweaving** | Python/Video/AI | Serena, Notion, image-gen-sd, dreamweaving-rag, coin-rag | Specialized for creative AI content production |
| **Salarsu** | Next.js/Postgres | Serena, Context7, Postgres, Shadcn, Playwright, coin-knowledge | Full-stack web development with database operations |
| **Salars.net** | Next.js Frontend | Serena, Context7, Shadcn, Playwright | Frontend web development with UI components and testing |

### Why Project-Specific Configs?

Different projects have fundamentally different tooling needs:

- **Dreamweaving:** No database, no web UI, Python-based video production pipeline
- **Salarsu:** Next.js + Postgres + React components + E2E testing for web application
- **Context Window Optimization:** Only load tools needed for the current project type

### Setting Up Other Projects

For web development projects (salarsu, salars.net), create a project-specific `mcp.json` in the project root:

```bash
# Example: Setting up salarsu project
cd ~/Projects/salarsu

# The mcp.json includes:
# - Serena (shared across all projects)
# - Context7 (React/Next.js/Tailwind docs)
# - Postgres (database operations)
# - Shadcn (UI component scaffolding)
# - Playwright (E2E testing)
```

See [Salarsu MCP Setup](../../salarsu/docs/MCP_SETUP.md) for complete configuration and usage examples.

### Project Switching Workflow

When switching between projects, Claude Code automatically loads the appropriate MCP servers:

```bash
# Working on Dreamweaving (creative AI tools loaded)
cd ~/Projects/dreamweaving
# Active: Serena, Notion, image-gen-sd, dreamweaving-rag

# Switching to Salarsu (web dev tools loaded)
cd ~/Projects/salarsu
# Active: Serena, Context7, Postgres, Shadcn, Playwright
```

Each project maintains its own `mcp.json` configuration optimized for its specific workflow.

---

## Important Distinction: Skills vs MCP Servers

**MCP Servers:**
- External processes that provide tools via Model Context Protocol
- Examples: Serena, Notion, image-gen-sd
- Location: Various (npm packages, Python scripts, uvx)
- Run as separate processes communicating over stdio/HTTP
- Configured in `config/mcp_servers.json` or `mcp.json`

**Skills (Claude Code Plugins):**
- Workflow plugins for Claude Code
- Examples: media-processing, tier1-neural-core
- Location: `~/.claude/skills/`
- NOT MCP servers (different technology)
- Installed via `npx claude-plugins skills install`

**Important:** Do not confuse media-processing (a skill) with an MCP server. It provides FFmpeg/ImageMagick capabilities but runs through Claude Code's plugin system, not MCP.

---

## Workflow-Aware Tool Loading

The project uses **staged tool loading** to optimize context window usage. Tools are loaded dynamically based on production workflow stage:

| Stage | Name | Tools Loaded |
|-------|------|--------------|
| 1 | Creative Design | Core only (Serena, Notion, RAG) |
| 2 | Voice Script | Core only |
| 3 | Audio Generation | Core + Audio (ElevenLabs) |
| 4 | Audio Mixing | Core + Audio + Media |
| 5 | Hypnotic Post-Process | Core + Audio + Media |
| 5.5 | Scene Images | Core + Image (SD, Stability AI) |
| 6 | Video Production | Core + Video |
| 7 | YouTube Packaging | Core + Publishing |
| 8 | Cleanup | Core only |
| 9 | Website Upload | Core only |

**Benefits:**
- Reduces context window consumption (2K-5K vs 20K+ tokens)
- Loads only relevant tools per workflow phase
- Prevents tool overload and confusion
- Optimizes for task-specific operations

**Configuration:** See `config/mcp_servers.json` → `toolCategories` and `stageToolMapping` for full definitions.

---

## MCP Server Inventory

Complete list of all MCP servers available to this project:

| Server | Status | Purpose | Config Location |
|--------|--------|---------|-----------------|
| **serena** | ✅ Active | Semantic code tools (find_symbol, refactoring, memories) | config/mcp_servers.json |
| **image-gen-sd** | ✅ Active | Local Stable Diffusion WebUI | config/mcp_servers.json |
| **notion** | ✅ Active | Official Notion API (page/DB access) | config/mcp_servers.json |
| **dreamweaving-rag** | ✅ Active | Notion semantic search (Qdrant) | config/mcp_servers.json |
| **coin-rag** | ✅ Available | Rare coin knowledge (specialized) | config/mcp_servers.json |
| **elevenlabs** | ⏸️ Disabled | TTS, voice cloning (needs API key) | config/mcp_servers.json |
| **stability-ai** | ⏸️ Disabled | Cloud images, SD 3.5 (needs key) | config/mcp_servers.json |
| **chrome-devtools** | ⏸️ Disabled | Browser inspection (optional) | config/mcp_servers.json |
| **midjourney** | 🔮 Future | Midjourney API integration | Not installed yet |

**Legend:**
- ✅ Active - Currently enabled and operational
- ⏸️ Disabled - Configured but requires setup (API keys, etc.)
- 🔮 Future - Documented as future enhancement

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

#### Midjourney MCP Server (FUTURE ENHANCEMENT)

**Status:** 🔮 NOT CURRENTLY INSTALLED

**Purpose:** High-quality image generation through Midjourney API

**Current Approach:** Generate Midjourney prompts as markdown files (`midjourney-prompts.md`) and manually create images on Midjourney web interface.

**Why Beneficial for Dreamweavings (when implemented):**
- Professional quality for YouTube thumbnails
- Consistent style across sessions
- Better for marketing materials

**Future Installation (when ready):**
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

### 2.3 Code & Knowledge MCP Servers

#### Serena MCP Server (SEMANTIC CODE TOOLS - INSTALLED)

**Status:** ✅ INSTALLED
**Package:** `serena` (via uvx from GitHub)
**Repository:** [oraios/serena](https://github.com/oraios/serena)

**Purpose:** Semantic code analysis, refactoring, and memory management

**Why Beneficial for Dreamweavings:**
- Superior to generic filesystem tools (semantic search > file search)
- Find symbols across codebase (functions, classes, variables)
- Refactor code safely with references tracking
- Store and retrieve project memories
- Search code patterns intelligently

**Available Tools:**
| Tool | Description |
|------|-------------|
| `find_symbol` | Locate functions, classes, variables by name |
| `find_referencing_symbols` | Find all references to a symbol |
| `search_for_pattern` | Regex search across codebase |
| `get_symbols_overview` | Get file structure and symbols |
| `replace_symbol_body` | Edit symbol definitions precisely |
| `insert_before_symbol` / `insert_after_symbol` | Insert code at specific locations |
| `rename_symbol` | Refactor names across entire codebase |
| `read_memory` / `write_memory` / `list_memories` | Project memory storage |

**Configuration:**
```json
// In config/mcp_servers.json (CANONICAL)
{
  "serena": {
    "command": "uvx",
    "args": [
      "--from",
      "git+https://github.com/oraios/serena",
      "serena",
      "start-mcp-server",
      "--context",
      "ide-assistant"
    ],
    "enabled": true
  }
}
```

**Requirements:**
- Python LSP (for .py files)
- Bash LSP (for .sh files)
- YAML LSP (for .yaml files)

**Note:** Serena replaces generic filesystem MCP servers with intelligent, semantic operations optimized for code.

#### Notion MCP Server (OFFICIAL - INSTALLED)

**Status:** ✅ INSTALLED
**Package:** `@notionhq/notion-mcp-server` (via npx)
**Repository:** [notionhq/notion-mcp-server](https://github.com/notionhq/notion-mcp-server)

**Purpose:** Read/write Dreamweaver workspace content from Notion

**Why Beneficial for Dreamweavings:**
- Access project documentation, specs, and roadmaps
- Read archetypal definitions and journey templates
- Update session notes and planning docs
- Sync knowledge base with Notion pages

**Setup:**
1. Create Notion internal integration: https://www.notion.so/my-integrations
2. Copy integration secret
3. Connect integration to Sacred Digital Dreamweaver workspace
4. Set `NOTION_TOKEN` environment variable

**Configuration:**
```json
// In config/mcp_servers.json (CANONICAL)
{
  "notion": {
    "command": "npx",
    "args": ["-y", "@notionhq/notion-mcp-server"],
    "env": {
      "NOTION_TOKEN": "${NOTION_TOKEN}"
    },
    "enabled": true
  }
}
```

#### Dreamweaving RAG MCP Server (CUSTOM - INSTALLED)

**Status:** ✅ INSTALLED
**Location:** `scripts/mcp/dreamweaving_rag_mcp_server.py`
**Type:** Custom Python MCP server

**Purpose:** Semantic search over Notion export using Qdrant vector index

**Why Beneficial for Dreamweavings:**
- Faster semantic search than querying Notion API directly
- Works offline once synced
- Optimized for dreamweaving domain knowledge
- Replaces generic Context7 MCP with domain-specific retrieval

**Available Tools:**
| Tool | Description |
|------|-------------|
| `search_notion_content` | Semantic search across exported Notion pages |
| `get_notion_page` | Retrieve specific page by title or ID |
| `list_notion_pages` | Browse available pages |
| `sync_notion_export` | Export Notion and re-index (incremental) |

**Prerequisites:**
- Qdrant running locally or remotely
- Notion export in `knowledge/notion_export/`

**Configuration:**
```json
// In config/mcp_servers.json (CANONICAL)
{
  "dreamweaving-rag": {
    "command": "bash",
    "args": ["scripts/mcp/run_dreamweaving_rag_mcp_server.sh"],
    "enabled": true
  }
}
```

**Note:** Works alongside official Notion MCP. Use Notion MCP for direct page writes, use RAG for fast semantic retrieval.

#### Coin RAG MCP Server (SPECIALIZED - AVAILABLE)

**Status:** ✅ AVAILABLE (specialized tool, not required for Dreamweaving)
**Location:** `scripts/mcp/coin_rag_mcp_server.py`
**Type:** Custom Python MCP server

**Purpose:** Semantic search for rare coin knowledge (Morgan/Peace dollars, junk silver, key dates, pricing, grading)

**Why Included:**
- Demonstrates custom RAG server implementation
- Example of specialized knowledge MCP
- Available for numismatic research side projects

**Use Cases:**
- Researching coin values and key dates
- Grading standards and condition assessment
- Historical context for Morgan/Peace dollar designs

**Available Tools:**
| Tool | Description |
|------|-------------|
| `search_coin_knowledge` | Semantic search for coin information |
| `get_coin_details` | Detailed info on specific coins |
| `price_lookup` | Market pricing for grades |

**Configuration:**
```json
// In config/mcp_servers.json (CANONICAL)
{
  "coin-rag": {
    "command": "bash",
    "args": ["scripts/mcp/run_coin_rag_mcp_server.sh"],
    "enabled": true,
    "notes": "Optional specialized tool for numismatic research. Not required for Dreamweaving workflows."
  }
}
```

**Note:** This server is enabled but specialized. It does not interfere with Dreamweaving workflows and can be disabled if not needed.

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
