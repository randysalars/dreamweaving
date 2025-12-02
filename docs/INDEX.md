# 🌿 Dreamweaving Project - Master Index

**Welcome to the Sacred Digital Dreamweaver**

This is your complete guide to creating professional hypnotic audio sessions. Everything you need is organized and accessible from this single page.

---

## 🎯 Quick Start (5 Minutes)

**New to this project? Start here:**

1. **Activate your environment:**
   ```bash
   cd ~/Projects/dreamweaving
   source venv/bin/activate  # or use: ./activate.sh
   ```

2. **Create a new session:**
   ```bash
   ./scripts/utilities/create_new_session.sh "my-first-session"
   ```

3. **Edit the script using the prompt guide:**
   - Open: `prompts/hypnotic_dreamweaving_instructions.md`
   - Edit: `sessions/my-first-session/script.ssml`
   - Use templates from: `templates/`

4. **Generate audio:**
   ```bash
   python3 scripts/core/generate_audio_chunked.py \
       sessions/my-first-session/script.ssml \
       sessions/my-first-session/output/audio.mp3 \
       en-US-Neural2-A
   ```

**Done!** You now have professional hypnotic audio.

For complete details, see: [CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md)

---

## 📚 Documentation Hub

### ⭐ Official Workflow (START HERE)
- **[CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md)** ← **OFFICIAL PRODUCTION WORKFLOW**

### Getting Started
- **[QUICK_START.md](QUICK_START.md)** - Get up and running in 5 minutes
- **[WORKFLOW_DECISION_TREE.md](WORKFLOW_DECISION_TREE.md)** - Which workflow should I use?
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

### Reference Guides
- **[TERMINOLOGY_GUIDE.md](TERMINOLOGY_GUIDE.md)** - Standard terminology and naming conventions
- **[WORKFLOW_MAINTENANCE_GUIDE.md](WORKFLOW_MAINTENANCE_GUIDE.md)** - Maintaining workflow consistency

### YouTube Publishing
- **[YOUTUBE_PACKAGING_SOP.md](YOUTUBE_PACKAGING_SOP.md)** - Complete YouTube packaging workflow (thumbnails, titles, descriptions, VTT)
- **[THUMBNAIL_DESIGN_GUIDE.md](THUMBNAIL_DESIGN_GUIDE.md)** - Expert thumbnail design principles (10 commandments)
- **[YOUTUBE_TITLE_GUIDE.md](YOUTUBE_TITLE_GUIDE.md)** - High-CTR title optimization (templates, power words)

### Technical Guides
- **[MANIFEST_DRIVEN_AUDIO.md](MANIFEST_DRIVEN_AUDIO.md)** - Manifest-based audio generation
- **[HYPNOTIC_VOICE_ENHANCEMENT.md](HYPNOTIC_VOICE_ENHANCEMENT.md)** - Voice enhancement processing
- **[HYPNOTIC_PACING.md](HYPNOTIC_PACING.md)** - Timing and pacing techniques
- **[BINAURAL_FREQUENCY_GUIDE.md](BINAURAL_FREQUENCY_GUIDE.md)** - Comprehensive binaural beats reference
- `../config/` - Configuration and settings reference

### AI & Self-Learning System
- **[SELF_IMPROVEMENT_WORKFLOW.md](SELF_IMPROVEMENT_WORKFLOW.md)** - Pillar 3: Self-evolutive systems
- `../knowledge/` - Knowledge base and lessons learned
- `../scripts/ai/learning/` - Feedback analyzer, lessons manager

### Archives
- `.archive/old_docs/` - Previous documentation (preserved for reference)

---

## 🎯 Project Structure

```
dreamweaving/
├── docs/                    ← YOU ARE HERE - All documentation
├── prompts/                 ← AI prompt templates for script creation
├── scripts/                 ← Python tools (organized by function)
├── templates/               ← SSML templates and reusable components
├── sessions/                ← Your hypnosis sessions
├── resources/               ← Supporting materials and audio
├── config/                  ← Configuration files
└── tests/                   ← Testing and validation
```

---

## 🛠️ Core Tools

### Audio Generation Scripts

**Primary Tools** (in `scripts/core/`):
- `generate_audio_chunked.py` - For large SSML files (recommended)
- `generate_audio.py` - For small/simple SSML files
- `audio_config.py` - Centralized settings

**Specialized Tools** (in `scripts/synthesis/`):
- `synthesize_pretalk.py` - Generate pre-talk sections
- `synthesize_opening.py` - Generate induction/opening
- `synthesize_closing.py` - Generate closing sections
- `synthesize_natural.py` - Natural voice synthesis

**Utilities** (in `scripts/utilities/`):
- `create_new_session.sh` - Quick session creation
- `validate_ssml.py` - Validate SSML syntax
- `batch_generate.py` - Generate multiple sessions
- `audio_merger.py` - Merge audio segments

For detailed script usage: `scripts/README.md`

---

## 📝 Creating Hypnosis Scripts

### Step 1: Review the Master Prompt

**Essential Reading:**
- `prompts/hypnotic_dreamweaving_instructions.md` - Complete guide for creating scripts

This prompt contains:
- 5 mandatory sections (Pre-talk, Induction, Main Journey, Integration, Post-hypnotic)
- Writing style guidelines
- SSML formatting examples
- Quality checklist

### Step 2: Choose a Template

**Base Templates** (`templates/base/`):
- `hypnosis_template.ssml` - Standard 20-30 min session
- `short_session.ssml` - 10-15 min quick session
- `extended_session.ssml` - 45-60 min deep session

**Theme Templates** (`templates/themes/`):
- `healing_journey.ssml`
- `abundance_activation.ssml`
- `confidence_building.ssml`
- `spiritual_connection.ssml`

**Reusable Components** (`templates/components/`):
- `inductions/` - Various induction styles
- `deepeners/` - Deepening techniques
- `closings/` - Return and grounding scripts
- `anchors/` - Post-hypnotic suggestion templates

### Step 3: Customize for Your Theme

Use theme-specific prompt guides:
- `prompts/session_themes/healing.md`
- `prompts/session_themes/abundance.md`
- `prompts/session_themes/confidence.md`
- `prompts/session_themes/spiritual.md`

---

## 🎵 Working with Sessions

### Session Organization

Each session lives in `sessions/[session-name]/`:
```
sessions/my-session/
├── script.ssml          # Your hypnosis script
├── notes.md             # Session intentions and notes
├── output/              # Generated audio files
│   └── audio.mp3
└── variants/            # Alternative versions
    └── script_v2.ssml
```

### Example Sessions

- `sessions/garden-of-eden/` - Complete example session
- `sessions/_template/` - Template for new sessions

### Creating a New Session

**Option A: Use Helper Script**
```bash
./scripts/utilities/create_new_session.sh "session-name"
```

**Option B: Manual Creation**
```bash
mkdir -p sessions/new-session/{output,variants}
cp templates/base/hypnosis_template.ssml sessions/new-session/script.ssml
```

---

## 🔧 Configuration

### Voice Settings

**Default Voice:** `en-US-Neural2-A` (warm, calming female)

**All Voice Options:** See `config/voice_profiles.json`

**Change Voice:**
```bash
python scripts/core/generate_audio_chunked.py \
    input.ssml output.mp3 en-US-Neural2-D
```

### Audio Settings

**Default Settings** (optimized for hypnosis):
- Speaking Rate: 0.85 (slow, hypnotic)
- Pitch: -2.0 semitones (calming)
- Format: MP3, 24kHz
- Device: Headphone-class

**Customize:** Edit `scripts/core/audio_config.py`

### Google Cloud Setup

See: `config/google_cloud_setup.md`

Quick setup:
```bash
gcloud auth application-default login
gcloud services enable texttospeech.googleapis.com
```

---

## 🎨 Resources

### Background Audio
- `resources/background_audio/creativity/` - Brainwave entrainment
- `resources/background_audio/nature/` - Nature sounds
- `resources/background_audio/binaural/` - Binaural beats

### Reference Materials
- `resources/reference/hypnosis_techniques.md`
- `resources/reference/voice_settings.md`
- `resources/reference/best_practices.md`

### Voice Samples
- `resources/voice_samples/` - Test different voices

---

## 🎓 Workflow Examples

### Complete Session Creation Workflow

1. **Plan your session**
   - Define goal (healing, confidence, sleep, etc.)
   - Choose journey theme
   - Review relevant prompt guide

2. **Create session structure**
   ```bash
   ./scripts/utilities/create_new_session.sh "inner-healing"
   ```

3. **Write the script**
   - Review: `prompts/hypnotic_dreamweaving_instructions.md`
   - Choose template: `templates/themes/healing_journey.ssml`
   - Edit: `sessions/inner-healing/script.ssml`
   - Add notes: `sessions/inner-healing/notes.md`

4. **Validate SSML (optional)**
   ```bash
   python scripts/utilities/validate_ssml.py \
       sessions/inner-healing/script.ssml
   ```

5. **Generate audio**
   ```bash
   python scripts/core/generate_audio_chunked.py \
       sessions/inner-healing/script.ssml \
       sessions/inner-healing/output/inner_healing.mp3
   ```

6. **Test and refine**
   - Listen to output
   - Adjust SSML timing/pacing
   - Regenerate as needed

### Batch Generation

Generate multiple sessions:
```bash
python scripts/utilities/batch_generate.py sessions/*/script.ssml
```

### Using Components

Mix and match components:
```bash
# Combine: Progressive Relaxation Induction + Healing Journey + Gratitude Closing
cat templates/components/inductions/progressive_relaxation.ssml \
    templates/themes/healing_journey.ssml \
    templates/components/closings/gratitude.ssml \
    > sessions/custom/script.ssml
```

---

## 💡 Common Tasks

### Change Voice for Existing Session
```bash
python scripts/core/generate_audio_chunked.py \
    sessions/my-session/script.ssml \
    sessions/my-session/output/audio_male.mp3 \
    en-US-Neural2-D
```

### Create Session Variant
```bash
cp sessions/original/script.ssml \
   sessions/original/variants/script_shorter.ssml
# Edit the variant, then generate
```

### Add Background Audio
```bash
python scripts/utilities/audio_merger.py \
    sessions/my-session/output/audio.mp3 \
    resources/background_audio/nature/rain.mp3 \
    sessions/my-session/output/audio_with_bg.mp3
```

### Test SSML Locally
```bash
python scripts/utilities/validate_ssml.py \
    sessions/my-session/script.ssml
```

---

## 🆘 Getting Help

### Documentation
1. Check: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review: [CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md)
3. Read script docs: `scripts/README.md`

### Common Issues
- **"Chunk too large"** - Add more `<break>` tags in SSML
- **"Authentication failed"** - Run `gcloud auth application-default login`
- **"FFmpeg not found"** - Install: `sudo apt install ffmpeg`
- **"Import errors"** - Activate venv: `source venv/bin/activate`

See full troubleshooting: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### System Requirements
- Python 3.8+
- FFmpeg
- Google Cloud SDK
- Virtual environment activated

---

## 📈 Session Ideas Library

### Healing
- Inner child healing
- Trauma release journey
- Grief processing
- Forgiveness path-working
- Shadow integration

### Empowerment
- Confidence activation
- Public speaking ease
- Leadership embodiment
- Creative unblocking
- Personal power

### Spiritual
- Chakra balancing
- Spirit guide connection
- Past life exploration
- Higher self communion
- Akashic records access

### Abundance
- Wealth consciousness
- Prosperity mindset
- Success visualization
- Manifesting mastery
- Financial freedom

### Wellness
- Deep sleep induction
- Pain relief meditation
- Stress dissolution
- Anxiety release
- Energy restoration

---

## 🔄 Maintenance

### Keep Project Updated
```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update Google Cloud SDK
gcloud components update
```

### Backup Your Sessions
```bash
# Backup to external location
cp -r sessions/ ~/Backups/dreamweaving-sessions-$(date +%Y%m%d)
```

### Clean Up Old Audio
```bash
# Archive old session outputs
mv sessions/*/output/*.mp3 .archive/old_audio/
```

---

## 💰 Cost Information

**Google Cloud Text-to-Speech:**
- **Free Tier:** 1,000,000 characters/month
- **Average Session:** ~25,000 characters
- **Free Sessions/Month:** ~40 sessions
- **After Free Tier:** $4 per 1M characters

**Typical Usage:**
- Small session (15 min): ~15,000 chars
- Medium session (30 min): ~25,000 chars
- Large session (60 min): ~45,000 chars

---

## 📞 Project Info

**Created by:** The Sacred Digital Dreamweaver
**Author:** Randy Sailer's Autonomous AI Clone
**Version:** 2.0 (Reorganized November 2025)

**Key Files:**
- Master Prompt: `prompts/hypnotic_dreamweaving_instructions.md`
- This Index: `docs/INDEX.md`
- Project Root: `../README.md`

---

## 🌟 Next Steps

**New User?**
1. Read: [QUICK_START.md](QUICK_START.md)
2. Review: `prompts/hypnotic_dreamweaving_instructions.md`
3. Create your first session!

**Experienced User?**
- Explore theme templates: `templates/themes/`
- Build component library: `templates/components/`
- Create batch workflows: `scripts/utilities/batch_generate.py`

**Want to Contribute?**
- Add new theme templates
- Create reusable components
- Document your techniques
- Share session ideas

---

*Walk in innocence. Choose with wisdom. Live in wholeness.* 🌿

---

**Quick Navigation:**
- [Quick Start](QUICK_START.md) | [Canonical Workflow](CANONICAL_WORKFLOW.md) | [Troubleshooting](TROUBLESHOOTING.md)
- [Voice Enhancement](HYPNOTIC_VOICE_ENHANCEMENT.md) | [Production Workflow](PRODUCTION_WORKFLOW.md)
- [Project Root](../README.md) | [Scripts](../scripts/README.md) | [Templates](../templates/)
