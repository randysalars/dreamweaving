# 🌿 Dreamweaving Project Reorganization Plan

## Current Status Analysis

**Issues Identified:**
- 9+ Python synthesis scripts scattered in root directory
- Duplicate documentation (START_HERE, QUICK_REFERENCE)
- Duplicate "garden of eden1" folder with redundant files
- Audio output files mixed with source files
- Creativity folders with ~1.8GB of audio files with unclear purpose
- No clear workflow for script generation

---

## Proposed Optimal Structure

```
dreamweaving/
│
├── 📚 docs/                           # ALL documentation in one place
│   ├── INDEX.md                       # Master navigation guide (START HERE)
│   ├── QUICK_START.md                 # Getting started in 5 minutes
│   ├── WORKFLOW_GUIDE.md              # Complete workflow documentation
│   ├── AUDIO_GENERATION.md            # Audio generation technical guide
│   ├── SSML_REFERENCE.md              # SSML formatting guide
│   └── TROUBLESHOOTING.md             # Common issues and solutions
│
├── 🎯 prompts/                        # AI prompt templates
│   ├── hypnotic_dreamweaving_instructions.md  # Master prompt (KEEP)
│   ├── session_themes/                # Theme-specific variations
│   │   ├── healing.md
│   │   ├── abundance.md
│   │   ├── confidence.md
│   │   └── spiritual.md
│   └── customization_examples.md      # Examples of customized prompts
│
├── 🛠️ scripts/                        # Python tools (organized by function)
│   ├── core/                          # Core audio generation
│   │   ├── generate_audio_chunked.py  # Main generator (large files)
│   │   ├── generate_audio.py          # Simple generator (small files)
│   │   └── audio_config.py            # Centralized settings
│   │
│   ├── synthesis/                     # Specialized synthesis scripts
│   │   ├── synthesize_pretalk.py
│   │   ├── synthesize_opening.py
│   │   ├── synthesize_closing.py
│   │   └── synthesize_natural.py
│   │
│   ├── utilities/                     # Helper scripts
│   │   ├── create_new_session.sh
│   │   ├── validate_ssml.py
│   │   ├── batch_generate.py
│   │   └── audio_merger.py
│   │
│   └── README.md                      # Script usage documentation
│
├── 📝 templates/                      # SSML and session templates
│   ├── base/                          # Base templates
│   │   ├── hypnosis_template.ssml     # Standard template
│   │   ├── short_session.ssml         # 10-15 min template
│   │   └── extended_session.ssml      # 45-60 min template
│   │
│   ├── themes/                        # Theme-specific templates
│   │   ├── healing_journey.ssml
│   │   ├── abundance_activation.ssml
│   │   ├── confidence_building.ssml
│   │   └── spiritual_connection.ssml
│   │
│   └── components/                    # Reusable SSML components
│       ├── inductions/
│       ├── deepeners/
│       ├── closings/
│       └── anchors/
│
├── 🎵 sessions/                       # Individual hypnosis sessions
│   ├── garden-of-eden/
│   │   ├── script.ssml                # The hypnosis script
│   │   ├── notes.md                   # Session notes and intentions
│   │   ├── output/                    # Generated audio
│   │   │   └── garden_of_eden.mp3
│   │   └── variants/                  # Alternative versions
│   │       └── garden_of_eden_v2.ssml
│   │
│   ├── inner-child-healing/           # Future session example
│   │   ├── script.ssml
│   │   ├── notes.md
│   │   └── output/
│   │
│   └── _template/                     # Session folder template
│       ├── script.ssml
│       ├── notes.md
│       └── output/
│
├── 🎨 resources/                      # Supporting resources
│   ├── voice_samples/                 # Voice test samples
│   ├── background_audio/              # Optional background tracks
│   │   ├── creativity/                # Move creativity files here
│   │   ├── nature/
│   │   └── binaural/
│   └── reference/                     # Reference materials
│       ├── hypnosis_techniques.md
│       ├── voice_settings.md
│       └── best_practices.md
│
├── 🧪 tests/                          # Testing and validation
│   ├── test_ssml_validation.py
│   ├── test_audio_generation.py
│   └── sample_outputs/
│
├── 📦 .archive/                       # Archived/deprecated files
│   ├── old_scripts/
│   ├── old_docs/
│   └── README.md                      # What's archived and why
│
├── 🔧 config/                         # Configuration files
│   ├── voice_profiles.json            # Voice settings presets
│   ├── project_settings.json          # Project-wide settings
│   └── google_cloud_setup.md          # GCP setup instructions
│
├── venv/                              # Python virtual environment
├── .vscode/                           # VS Code settings
│   ├── settings.json
│   ├── launch.json
│   └── tasks.json
│
├── .gitignore                         # Git ignore rules
├── requirements.txt                   # Python dependencies
├── activate.sh                        # Quick venv activation
├── README.md                          # Project overview (points to docs/INDEX.md)
└── CHANGELOG.md                       # Track project changes

```

---

## Migration Steps

### Phase 1: Documentation Consolidation
1. Create `docs/` directory structure
2. Consolidate all START_HERE, QUICK_REFERENCE into unified docs
3. Create `docs/INDEX.md` as the single source of truth
4. Archive old documentation

### Phase 2: Script Organization
1. Create `scripts/core/`, `scripts/synthesis/`, `scripts/utilities/`
2. Move Python scripts into appropriate categories
3. Remove duplicate scripts
4. Update import paths if needed

### Phase 3: Template Enhancement
1. Create `templates/base/`, `templates/themes/`, `templates/components/`
2. Create reusable SSML components (inductions, deepeners, etc.)
3. Develop theme-specific templates

### Phase 4: Resource Organization
1. Create `resources/` directory
2. Move creativity audio files to `resources/background_audio/creativity/`
3. Create structure for future resources

### Phase 5: Session Cleanup
1. Remove duplicate "garden of eden1" folder
2. Standardize session folder structure
3. Create session template

### Phase 6: Configuration
1. Create `config/` directory
2. Extract hardcoded settings into config files
3. Create voice profile presets

---

## Benefits of New Structure

### 🎯 Clarity
- Single entry point: `docs/INDEX.md`
- Clear separation of concerns
- Easy to find any file within 2-3 clicks

### 🚀 Scalability
- Organized for 100+ sessions
- Template system for quick creation
- Reusable components save time

### 🔧 Maintainability
- Deprecated files archived, not deleted
- Clear script organization
- Version control ready

### 🎨 Creativity Support
- Theme templates inspire new sessions
- Component library for mix-and-match
- Example prompts for different goals

### 📚 Learning Friendly
- Progressive documentation (quick start → advanced)
- Examples and references organized
- Clear workflow guides

---

## Files to Archive

Move to `.archive/` directory:
- Duplicate documentation files
- `garden of eden1/` folder (redundant)
- Old synthesis scripts (after consolidation)
- Root-level audio files (after organizing)

## Files to Keep in Root

Only essential files:
- `README.md` (project overview, points to docs)
- `requirements.txt`
- `activate.sh`
- `.gitignore`
- `CHANGELOG.md`

---

## Workflow After Reorganization

### Creating a New Session (3 steps):

1. **Choose your approach:**
   ```bash
   # Option A: Use helper script
   ./scripts/utilities/create_new_session.sh "confidence-builder"

   # Option B: Copy template
   cp -r sessions/_template sessions/my-new-session
   ```

2. **Create the script:**
   ```bash
   # Review the prompt guide
   cat prompts/hypnotic_dreamweaving_instructions.md

   # Choose a theme template or start from base
   cp templates/themes/confidence_building.ssml sessions/my-new-session/script.ssml

   # Edit in VS Code
   code sessions/my-new-session/script.ssml
   ```

3. **Generate audio:**
   ```bash
   python scripts/core/generate_audio_chunked.py \
       sessions/my-new-session/script.ssml \
       sessions/my-new-session/output/audio.mp3
   ```

### Finding Information (clear paths):

- **"How do I get started?"** → `docs/INDEX.md`
- **"What voices are available?"** → `config/voice_profiles.json`
- **"How do I format SSML?"** → `docs/SSML_REFERENCE.md`
- **"What's the workflow?"** → `docs/WORKFLOW_GUIDE.md`
- **"I have an error"** → `docs/TROUBLESHOOTING.md`

---

## Implementation Timeline

**Immediate (Today):**
- Create new directory structure
- Move and consolidate documentation
- Organize Python scripts

**This Week:**
- Create template library
- Build component system
- Update all documentation

**Ongoing:**
- Migrate sessions as you work on them
- Build out theme templates
- Add new utilities as needed

---

## Next Steps

Would you like me to:

1. **Execute the full reorganization automatically** - I'll create the structure and move all files
2. **Do it step-by-step with your approval** - I'll show you each change before making it
3. **Create just the new structure** - You manually move files at your own pace
4. **Customize the plan first** - Adjust the structure based on your preferences

The reorganization will preserve all your work while making the project significantly more usable and scalable.

---

*Organized by: Claude Code*
*Date: November 22, 2025*
