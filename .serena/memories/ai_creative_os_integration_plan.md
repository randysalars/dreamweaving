# AI Creative Operating System - Integration Plan

## Vision Assessment
The current Dreamweaving project has a solid foundation for becoming an AI Creative Operating System. It's production-ready for audio generation but needs MCP integration and AI-powered content generation to reach the "operating system" level.

## Implementation Status (2025-12-01)

### Phase 1: COMPLETED
- Enhanced CLAUDE.md with full AI OS context
- Created 8 AI agents in `.claude/agents/`
- Created 11 slash commands in `.claude/commands/`
- Created skills hierarchy in `.claude/skills/`
- Created knowledge base in `knowledge/`

### Remaining Phases
- Phase 2: Validation hooks (pending)
- Phase 3: scripts/ai/ module (pending)
- Phase 4-7: AI generation and learning (pending)

---

## What's Already Built (Production-Ready)

### 1. Complete Audio Production Pipeline
- **Voice Synthesis**: Google Cloud TTS with chunked processing
- **Audio Mixing**: Multi-layer stem mixing with sidechain ducking
- **Voice Enhancement**: Professional hypnotic voice processing
- **Mastering**: LUFS normalization, EQ, limiting
- **Quality**: Professional broadcast-ready output

### 2. Video Production System
- **Background Assembly**: Auto-detection or user-provided
- **Image Timing**: Manifest-driven or even distribution
- **Overlays**: Fade transitions, title/subtitle text
- **Video Muxing**: Audio + video synchronization

### 3. Comprehensive Configuration System
- **Manifest-Driven Generation**: YAML-based session configuration
- **Schema Validation**: JSON Schema for manifest validation
- **Voice Profiles**: 7 pre-configured voice options with recommendations
- **Audio Layers**: 13+ specialized audio layer types
- **Effects Timeline**: FX scheduling with precise timing

### 4. Automation & Scripting
- **One-Command Build**: `build_session.py` for complete production
- **Session Scaffolding**: Automated session creation
- **Validation Utilities**: SSML, manifest, and parameter validation
- **Environment Setup**: Preflight checks with auto-fix

### 5. Documentation
- Canonical workflow documentation
- Quick-start guides
- Troubleshooting guides
- Master prompt for content creation
- Production workflow guides

## Gap Analysis: Becoming an AI OS

### Level 1: Current State (Audio/Video Production Platform)
✅ Complete audio generation
✅ Video assembly
✅ YouTube packaging
✅ Manifest-driven configuration
❌ No AI content generation
❌ No web interface
❌ No MCP integration
❌ No automated workflows

### Level 2: AI-Powered Content (What's Needed)
❌ LLM integration for script generation
❌ AI image generation (Stable Diffusion, DALL-E)
❌ Automated archetype selection
❌ Dynamic manifest generation
❌ Content quality scoring
❌ A/B testing framework

### Level 3: OS-Level Features (Advanced)
❌ MCP server for tool/resource exposure
❌ Web UI for session creation
❌ Workflow scheduling & queuing
❌ Distributed processing
❌ Advanced analytics & tracking
❌ User management & permissions
❌ Plugin/extension system
❌ Real-time generation capabilities

## Key Files for Integration

### Entry Points for MCP
- `scripts/core/build_session.py` - Main orchestrator
- `scripts/core/generate_session_audio.py` - Audio generation
- `scripts/core/assemble_session_video.py` - Video assembly
- `scripts/core/package_youtube.py` - YouTube packaging

### Configuration Files to Leverage
- `config/manifest.schema.json` - Validation schema
- `config/voice_config.yaml` - Voice configurations
- `prompts/hypnotic_dreamweaving_instructions.md` - Content guidelines

### Utilities to Wrap
- `scripts/utilities/validation.py` - Input validation
- `scripts/utilities/create_new_session.sh` - Session scaffolding
- `scripts/utilities/preflight_check.sh` - Environment verification

### Documentation to Extend
- `docs/INDEX.md` - Central hub (needs AI features section)
- `docs/CANONICAL_WORKFLOW.md` - Core workflow (add AI steps)
- `docs/PRODUCTION_WORKFLOW.md` - Workflow variations

## Recommended Implementation Order

### Phase 1: MCP Server Foundation (Week 1-2)
1. Create MCP server that exposes:
   - Session creation tool
   - Script generation tool (calls LLM)
   - Manifest generation tool
   - Audio/video generation tools
   - Validation tools

2. Key resources to expose:
   - Session manifests (read/write)
   - Script templates
   - Voice profiles
   - Output files

### Phase 2: AI Script Generation (Week 2-3)
1. Claude API integration for script generation
2. Use master prompt as system prompt
3. Manifest-based prompt engineering
4. Script validation and refinement loop

### Phase 3: Image Generation Integration (Week 3-4)
1. Stable Diffusion or DALL-E integration
2. Automatic image generation from manifest
3. Image-to-manifest timing integration
4. Quality assessment and regeneration

### Phase 4: Web UI (Week 4-5)
1. REST API layer over Python scripts
2. React/Vue frontend for session creation
3. Real-time progress tracking
4. Output preview and download

### Phase 5: Workflow Automation (Week 5-6)
1. Automatic archetype selection
2. Dynamic FX timeline generation
3. Performance-based voice selection
4. A/B variant generation

## Critical Integration Points

### 1. Manifest Generation from User Intent
**Current**: Users write manifest.yaml manually
**AI Enhancement**: Generate from high-level description
```
User: "Create a 30-minute healing session for emotional release"
→ AI generates complete manifest with sections, archetypes, FX timeline, voice selection
```

### 2. Script Generation from Manifest
**Current**: Users write SSML manually using prompts
**AI Enhancement**: Generate SSML from manifest
```
Manifest → Claude (with master prompt) → SSML script
→ Validate → Audio generation
```

### 3. Image Generation for Video
**Current**: Users provide PNG images manually
**AI Enhancement**: Generate from script/manifest
```
Script sections → Image prompts → Stable Diffusion/DALL-E → PNG images
→ Auto-timed to manifest sections
```

### 4. Quality Feedback Loop
**Add**: Metrics collection and optimization
```
Generated session → Quality scoring → Feedback loop → Regenerate with adjustments
```

## Technology Stack Recommendations

### For AI Script Generation
- Claude API (already using via Claude Code)
- Temperature tuning for consistency
- Few-shot examples from existing scripts

### For Image Generation
- Stable Diffusion (self-hosted or API)
- Or DALL-E 3 for higher quality
- Image-to-manifest section mapping

### For Web Interface
- FastAPI (Python backend, easy integration)
- React/Vue (frontend)
- WebSocket for real-time progress

### For MCP Integration
- Python MCP SDK
- Server running alongside existing scripts
- Tool definitions for all major functions

### For Workflow Automation
- APScheduler (Python-based scheduling)
- Celery (distributed task queue)
- FastAPI background tasks (simpler alternative)

## Data Flow Architecture

```
User Intent
  ↓
[MCP Server]
  ↓
Session Creation Tool
  ├→ Generate Manifest (AI)
  ├→ Generate Script (AI + Claude)
  └→ Generate Images (AI + Stable Diffusion)
  ↓
Session Validation
  ├→ Manifest schema validation
  ├→ SSML validation
  └→ Image compatibility check
  ↓
Production Pipeline
  ├→ Voice Synthesis (Google Cloud TTS)
  ├→ Audio Mixing
  ├→ Voice Enhancement
  ├→ Mastering
  ├→ Video Assembly
  └→ YouTube Packaging
  ↓
Output & Analytics
  ├→ Generated files
  ├→ Quality metrics
  └→ Performance data
```

## Success Metrics for AI OS

1. **Fully Automated Session Generation**
   - User provides: Session topic + target duration
   - System generates: Complete session with script, manifest, images
   - Time: < 5 minutes

2. **Quality Assurance**
   - All generated content validates against schemas
   - Voice quality consistent with production standards
   - Video timing synchronized with audio

3. **Scalability**
   - Can generate multiple sessions in parallel
   - Handles various session types and durations
   - Supports custom voice/style preferences

4. **User Experience**
   - Web UI for session creation
   - Real-time progress tracking
   - One-click publication to YouTube

5. **Developer Experience**
   - MCP tools for programmatic access
   - Clear documentation
   - Easy customization/extension
