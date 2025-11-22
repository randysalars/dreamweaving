# 🌿 Sacred Digital Dreamweaver

**Professional Hypnotic Audio Generation System**
*Version 2.0 - Reorganized & Enhanced*

A complete Python environment for creating transformational hypnotic path-working audio sessions using Google Cloud Text-to-Speech.

---

## 📖 **START HERE: [Complete Documentation](docs/INDEX.md)**

**Everything you need is organized and accessible:**
- 🚀 [5-Minute Quick Start](docs/QUICK_START.md)
- 📚 [Complete Workflow Guide](docs/WORKFLOW_GUIDE.md)
- 🔧 [Troubleshooting](docs/TROUBLESHOOTING.md)
- 🎯 [Master Prompt Guide](prompts/hypnotic_dreamweaving_instructions.md)

---

## 📁 Project Structure

```
dreamweaving/
├── docs/                      # 📚 All documentation (START HERE)
│   ├── INDEX.md              # Master navigation guide
│   ├── QUICK_START.md        # Get started in 5 minutes
│   ├── WORKFLOW_GUIDE.md     # Complete workflow
│   └── TROUBLESHOOTING.md    # Common issues & solutions
│
├── prompts/                   # 🎯 AI prompt templates
│   ├── hypnotic_dreamweaving_instructions.md
│   └── session_themes/       # Theme-specific guides
│
├── scripts/                   # 🛠️ Python tools
│   ├── core/                 # Core audio generation
│   │   ├── generate_audio_chunked.py
│   │   └── generate_audio.py
│   ├── synthesis/            # Specialized synthesis
│   └── utilities/            # Helper scripts
│       ├── create_new_session.sh
│       └── validate_ssml.py
│
├── templates/                 # 📝 SSML templates
│   ├── base/                 # Base session templates
│   │   ├── hypnosis_template.ssml
│   │   ├── short_session.ssml (10-15 min)
│   │   └── extended_session.ssml (45-60 min)
│   ├── themes/               # Theme-specific templates
│   │   ├── healing_journey.ssml
│   │   └── confidence_building.ssml
│   └── components/           # Reusable SSML components
│
├── sessions/                  # 🎵 Your hypnosis sessions
│   ├── garden-of-eden/       # Example session
│   └── _template/            # Session folder template
│
├── resources/                 # 🎨 Supporting resources
│   └── background_audio/     # Optional background tracks
│
├── config/                    # 🔧 Configuration
│   └── voice_profiles.json   # Voice settings & presets
│
├── venv/                      # Python virtual environment
└── requirements.txt           # Python dependencies
```

---

## 🚀 Ultra-Quick Start (3 Commands)

```bash
# 1. Activate environment
cd ~/Projects/dreamweaving && source venv/bin/activate

# 2. Create new session
./scripts/utilities/create_new_session.sh "my-session"

# 3. Generate audio (after editing script.ssml)
python scripts/core/generate_audio_chunked.py \
    sessions/my-session/script.ssml \
    sessions/my-session/output/audio.mp3
```

**For complete instructions:** See [docs/QUICK_START.md](docs/QUICK_START.md)

---

## 📦 Dependencies

### Python Packages (installed via requirements.txt)
- `google-cloud-texttospeech` - Google TTS API
- `pydub` - Audio manipulation
- `mutagen` - Audio metadata
- `tqdm` - Progress bars

### System Requirements
- **Python 3.8+**
- **FFmpeg** - For audio concatenation
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`
- **Google Cloud SDK** - For authentication
  - Install: `curl https://sdk.cloud.google.com | bash`

---

## 🔧 Setup

### Google Cloud Authentication

```bash
# Initialize gcloud
gcloud init

# Authenticate
gcloud auth application-default login

# Enable Text-to-Speech API
gcloud services enable texttospeech.googleapis.com
```

### Verify Setup

```bash
# Check Python packages
pip list | grep google-cloud-texttospeech

# Check FFmpeg
ffmpeg -version

# Check gcloud auth
gcloud auth application-default print-access-token
```

---

## 🎙️ Voice Options

**Recommended for Hypnosis:**

Female Voices:
- `en-US-Neural2-A` ⭐ Default - Warm, calming
- `en-US-Neural2-C` - Soft, nurturing
- `en-US-Neural2-E` - Deeper, relaxing
- `en-US-Neural2-F` - Clear, serene

Male Voices:
- `en-US-Neural2-D` - Deep, resonant
- `en-US-Neural2-I` - Warm, compassionate
- `en-US-Neural2-J` - Rich, mature

To use different voice:
```bash
python scripts/generate_audio_chunked.py \
    sessions/my-session/script.ssml \
    sessions/my-session/output/audio.mp3 \
    en-US-Neural2-D
```

---

## 📝 Creating New Sessions

1. **Review the Prompt Template**
   - See `prompts/hypnotic_dreamweaving_instructions.md`
   - Follow the 5-section structure
   - Include all mandatory elements

2. **Create SSML Script**
   - Use XML/SSML formatting
   - Add proper `<break>` tags for pauses
   - Use `<prosody>` for voice control
   - Include `<emphasis>` for key suggestions

3. **Test Pronunciation**
   - Use `<phoneme>` tags for special words
   - Test hyphenated words like "path-working"

4. **Generate Audio**
   - Use chunked script for files >5000 bytes
   - Review output for quality

---

## 🎯 Audio Settings

Default optimized settings for hypnosis:
- **Speaking Rate:** 0.85 (hypnotic pace)
- **Pitch:** -2.0 semitones (calming)
- **Format:** MP3, 24kHz
- **Optimization:** Headphone-class device

Edit in `generate_audio_chunked.py` to adjust.

---

## 💰 Cost

**Google Cloud TTS:**
- Free tier: 1,000,000 characters/month
- Average session: ~25,000 characters
- ~40 sessions free per month
- After free tier: $4 per 1M characters

---

## 🎯 Key Features (New in v2.0)

✨ **Organized Structure**
- All documentation in one place ([docs/INDEX.md](docs/INDEX.md))
- Scripts organized by function (core, synthesis, utilities)
- Template library with base + theme templates
- Reusable SSML components

✨ **Enhanced Templates**
- Short session (10-15 min)
- Standard session (20-30 min)
- Extended session (45-60 min)
- Theme templates (healing, confidence, etc.)

✨ **Powerful Tools**
- SSML validator ([scripts/utilities/validate_ssml.py](scripts/utilities/validate_ssml.py))
- Session creator ([scripts/utilities/create_new_session.sh](scripts/utilities/create_new_session.sh))
- Voice profile configurations ([config/voice_profiles.json](config/voice_profiles.json))

✨ **Scalable**
- Designed for 100+ sessions
- Clear organization
- Easy to navigate

---

## 📚 Full Documentation

**Everything is in [docs/INDEX.md](docs/INDEX.md):**
- Complete workflow guide
- Voice options & settings
- SSML formatting reference
- Troubleshooting solutions
- Session creation examples

**Essential Guides:**
- [Quick Start](docs/QUICK_START.md) - 5 minutes to your first session
- [Workflow Guide](docs/WORKFLOW_GUIDE.md) - Step-by-step instructions
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues solved
- [Master Prompt](prompts/hypnotic_dreamweaving_instructions.md) - Script creation guide

---

## 🌟 What's New in v2.0

**Reorganized:** November 22, 2025
- Complete directory restructure
- Consolidated all documentation
- Created template library
- Added utility scripts
- Centralized configuration
- Improved workflow
- Enhanced navigation

See [CHANGELOG.md](CHANGELOG.md) for full details.

---

## 🎨 Session Ideas

**Healing:**
- Inner Child Healing
- Emotional Release
- Trauma Integration
- Grief Processing

**Empowerment:**
- Confidence Building
- Public Speaking
- Leadership
- Creative Unblocking

**Spiritual:**
- Chakra Balancing
- Spirit Guide Connection
- Past Life Exploration
- Higher Self

**Abundance:**
- Wealth Consciousness
- Prosperity Mindset
- Success Visualization

**Wellness:**
- Deep Sleep
- Pain Relief
- Stress Dissolution
- Anxiety Release

---

## 📄 License

Personal use and non-commercial distribution.  
Created by The Sacred Digital Dreamweaver - Randy Sailer's Autonomous AI Clone

---

*Walk in innocence. Choose with wisdom. Live in wholeness.* 🌿
