# Serena MCP Usage Guide

This guide documents how the Serena MCP server is integrated into the Dreamweaving project and how to use its capabilities effectively.

## Overview

Serena is an advanced MCP server that provides:
1. **Semantic Code Analysis**: Understanding code structure via Language Server Protocol (LSP)
2. **Project Memory**: Persistent knowledge storage in `.serena/memories/`
3. **Dreamweaver Tools**: Specialized tools for hypnotic content creation

## Configuration

- **Location**: `/home/rsalars/Projects/serena/` (Server implementation)
- **Project Config**: `.serena/project.yml` (Dreamweaving-specific settings)
- **Memories**: `.serena/memories/` (Knowledge base)

## Key Capabilities

### 1. Project Memories
Serena maintains a set of markdown files that document critical workflows and methodologies. These are automatically available to the agent when working on the project.

**Critical Memories:**
- `dreamweaver_journey_design.md`: Methodology for designing hypnotic journeys
- `audio_production_methodology.md`: Mixing levels, mastering, stem handling
- `script_production_workflow.md`: SSML writing, section structure
- `voice_pacing_guidelines.md`: Quick reference for prosody
- `dreamweaving_project_overview.md`: Architecture overview

### 2. Dreamweaver Tools
Implemented in `scripts/ai/dreamweaver_tools.py`, these tools automate core production tasks:

| Tool Function | Description |
|---------------|-------------|
| `generate_journey_outline` | Creates structured journey with archetypes and timing |
| `generate_ssml_section` | Wraps text in SSML with correct prosody for the section |
| `suggest_audio_bed` | Generates binaural/ambience/SFX plan based on target state |
| `generate_youtube_package` | Creates title, description, tags, and chapters |

### 3. Semantic Code Navigation
Serena uses LSP to understand the codebase structure. This allows for:
- Precise symbol finding (functions, classes)
- Safe refactoring
- Understanding dependencies

## Workflow Integration

### Starting a New Session
When asking Claude to start a new session, Serena's `dreamweaver_journey_design` memory provides the methodology, and `generate_journey_outline` tool creates the structure.

**Example Prompt:**
> "Create a new Layer 2 session about 'Crystal Cave Healing'. Use the dreamweaver tools to generate the outline."

### Writing Scripts
Serena uses `script_production_workflow` memory and `generate_ssml_section` tool to ensure correct SSML formatting.

**Example Prompt:**
> "Write the induction section for the Crystal Cave session. Use the 'deep_induction' speech profile."

### Audio Production
Serena uses `audio_production_methodology` memory and `suggest_audio_bed` tool to design the soundscape.

**Example Prompt:**
> "Generate an audio plan for this session targeting deep theta state with a mineral/cave ambience."

## Maintenance

### Updating Memories
To update the project knowledge, simply edit the markdown files in `.serena/memories/`.
- **Add new memory**: Create a new `.md` file in the directory
- **Update existing**: Edit the file directly

### Updating Tools
The tools are Python functions in `scripts/ai/dreamweaver_tools.py`.
- To add a new tool, implement the function and update `project.yml` (if needed for explicit registration, though currently they are Python library tools).

## Troubleshooting

If Serena seems to "forget" how to do something:
1. Check if the relevant memory file exists in `.serena/memories/`
2. Verify `project.yml` lists the memory (though it reads all files in the dir)
3. Remind the agent to "read the [memory_name] memory"

## Reference: Depth Levels

| Level | Duration | Purpose |
|-------|----------|---------|
| **Layer 1** | 15-20 min | Light relaxation, simple visualization |
| **Layer 2** | 20-30 min | Medium trance, transformational work |
| **Layer 3** | 30-45 min | Deep trance, complex archetypes |
| **Ipsissimus** | 45-60+ min | Deepest work, mystical experience |
