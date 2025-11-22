# Changelog

All notable changes to the Dreamweaving project will be documented in this file.

---

## [2.0.0] - 2025-11-22

### 🎉 Major Reorganization & Enhancement

Complete project restructure for scalability, organization, and ease of use.

### Added

**Documentation:**
- Created comprehensive `docs/` directory with all documentation
- Added `docs/INDEX.md` as master navigation guide
- Created `docs/QUICK_START.md` for 5-minute onboarding
- Added `docs/WORKFLOW_GUIDE.md` (placeholder for complete workflow)
- Created `docs/TROUBLESHOOTING.md` with common issues and solutions
- Added `docs/SSML_REFERENCE.md` (placeholder for SSML formatting guide)
- Added `docs/AUDIO_GENERATION.md` (placeholder for technical details)

**Templates:**
- Created `templates/base/` directory with:
  - `hypnosis_template.ssml` - Standard 20-30 min session
  - `short_session.ssml` - 10-15 min quick session
  - `extended_session.ssml` - 45-60 min deep session
- Created `templates/themes/` directory with:
  - `healing_journey.ssml` - Inner healing themed template
  - `confidence_building.ssml` - Confidence activation template
  - `abundance_activation.ssml` (placeholder)
  - `spiritual_connection.ssml` (placeholder)
- Created `templates/components/` directory structure for:
  - `inductions/` - Reusable induction techniques
  - `deepeners/` - Deepening methods
  - `closings/` - Return and grounding scripts
  - `anchors/` - Post-hypnotic suggestion templates

**Utilities:**
- Added `scripts/utilities/validate_ssml.py` - SSML validation tool
- Added `scripts/utilities/create_new_session.sh` - Session creation helper
- Created `scripts/utilities/batch_generate.py` (placeholder)
- Created `scripts/utilities/audio_merger.py` (placeholder)

**Configuration:**
- Created `config/` directory
- Added `config/voice_profiles.json` with:
  - 7 pre-configured voice profiles
  - Session type recommendations
  - Audio quality settings
- Added `config/google_cloud_setup.md` (placeholder)

**Structure:**
- Created `resources/` directory for supporting materials
- Added `resources/background_audio/` for optional tracks
- Created `tests/` directory for validation scripts
- Added `.archive/` directory for old/deprecated files
- Created `sessions/_template/` as session folder template

### Changed

**Directory Structure:**
- Reorganized `scripts/` into subdirectories:
  - `scripts/core/` - Core audio generation tools
  - `scripts/synthesis/` - Specialized synthesis scripts
  - `scripts/utilities/` - Helper scripts
- Moved all synthesis scripts from root to `scripts/synthesis/`
- Moved core generation scripts to `scripts/core/`
- Reorganized templates into `templates/base/` and `templates/themes/`

**Documentation:**
- Updated `README.md` to reflect new v2.0 structure
- Changed README to point to comprehensive docs in `docs/INDEX.md`
- Simplified main README, moved details to specific guides

**Files Moved:**
- `generate_audio_chunked.py` → `scripts/core/generate_audio_chunked.py`
- `generate_audio.py` → `scripts/core/generate_audio.py`
- `synthesize_pretalk.py` → `scripts/synthesis/synthesize_pretalk.py`
- `synthesize_closing.py` → `scripts/synthesis/synthesize_closing.py`
- `synthesize_hypnotic_opening.py` → `scripts/synthesis/synthesize_hypnotic_opening.py`
- `synthesize_natural_hypnotic.py` → `scripts/synthesis/synthesize_natural_hypnotic.py`
- `synthesize_matched_hypnotic.py` → `scripts/synthesis/synthesize_matched_hypnotic.py`
- `synthesize_intro_natural.py` → `scripts/synthesis/synthesize_intro_natural.py`
- `synthesize_ai_pretalk.py` → `scripts/synthesis/synthesize_ai_pretalk.py`
- `templates/hypnosis_template.ssml` → `templates/base/hypnosis_template.ssml`

### Archived

Moved to `.archive/old_docs/`:
- `COMPLETE_SETUP_GUIDE.md`
- `CHUNKED_AUDIO_GUIDE.md`
- `AUDIO_GENERATION_INSTRUCTIONS.md`
- `QUICK_REFERENCE.txt`
- `START_HERE.txt`
- `garden of eden1/` folder (duplicate)

### Improved

**Navigation:**
- Single entry point: `docs/INDEX.md`
- Clear documentation hierarchy
- Logical file organization
- Everything findable within 2-3 clicks

**Scalability:**
- Structure designed for 100+ sessions
- Template system for quick creation
- Reusable component library
- Clear separation of concerns

**User Experience:**
- 5-minute quick start guide
- Comprehensive troubleshooting
- Voice profile presets
- Session creation helpers
- SSML validation tool

**Maintainability:**
- Scripts organized by function
- Centralized configuration
- Deprecated files archived (not deleted)
- Clear project structure

---

## [1.0.0] - 2025-11-21

### Initial Release

**Core Features:**
- Basic project setup with virtual environment
- Google Cloud Text-to-Speech integration
- SSML script support
- Chunked audio generation for large files
- Garden of Eden example session
- Basic documentation files
- Manual session creation workflow

**Files:**
- `generate_audio_chunked.py` - Main generation script
- `generate_audio.py` - Simple generation script
- `garden_of_eden_hypnosis.ssml` - Example session
- `prompts/hypnotic_dreamweaving_instructions.md` - Master prompt
- Various synthesis scripts for testing
- Basic README and setup guides

---

## Migration Guide (1.0 → 2.0)

### If you were using v1.0:

**Scripts:**
Old locations still work via symlinks (TBD), but update to new paths:
```bash
# Old
python generate_audio_chunked.py input.ssml output.mp3

# New
python scripts/core/generate_audio_chunked.py input.ssml output.mp3
```

**Templates:**
```bash
# Old
cp templates/hypnosis_template.ssml sessions/new/script.ssml

# New
cp templates/base/hypnosis_template.ssml sessions/new/script.ssml
# Or use theme templates:
cp templates/themes/healing_journey.ssml sessions/new/script.ssml
```

**Documentation:**
All old documentation is preserved in `.archive/old_docs/` for reference.
New documentation is in `docs/` - start with `docs/INDEX.md`.

**Sessions:**
No changes needed to existing session folders. They work as-is.

---

## Future Roadmap

### Planned for v2.1
- [ ] Complete `docs/WORKFLOW_GUIDE.md`
- [ ] Complete `docs/SSML_REFERENCE.md`
- [ ] Complete `docs/AUDIO_GENERATION.md`
- [ ] Add more theme templates (abundance, spiritual)
- [ ] Create reusable SSML components library
- [ ] Add `scripts/utilities/batch_generate.py`
- [ ] Add `scripts/utilities/audio_merger.py`
- [ ] Create `prompts/session_themes/` guides
- [ ] Add example sessions beyond Garden of Eden

### Planned for v2.2
- [ ] Web-based SSML editor
- [ ] Voice preview tool
- [ ] Session analytics (duration, word count)
- [ ] Auto-tagging and metadata
- [ ] Export presets (podcast, YouTube, etc.)
- [ ] Multi-voice support in single session

### Planned for v3.0
- [ ] Local TTS option (offline capability)
- [ ] Custom voice training
- [ ] Background audio mixing
- [ ] Visual editor for timing/pacing
- [ ] Session library/marketplace integration
- [ ] Automated quality checks

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible structural changes
- **MINOR** version for new functionality (backwards-compatible)
- **PATCH** version for backwards-compatible bug fixes

---

*For detailed usage instructions, see [docs/INDEX.md](docs/INDEX.md)*
