# 🌿 Sacred Digital Dreamweaver - Complete Setup Guide

## One-Command Professional Setup

This guide will set up a complete, professional Python environment for creating unlimited hypnotic audio sessions.

---

## 📦 What You'll Get

```
~/Projects/dreamweaving/
├── venv/                              # Python virtual environment
├── scripts/
│   ├── generate_audio_chunked.py     # Main audio generator (reusable)
│   ├── generate_audio.py             # Simple version
│   └── create_new_session.sh         # Helper to create new sessions
├── sessions/
│   ├── garden-of-eden/               # Your first session
│   │   ├── garden_of_eden_hypnosis.ssml
│   │   └── output/
│   └── [future-sessions]/            # Add more here
├── prompts/
│   └── hypnotic_dreamweaving_instructions.md  # Original prompt (for creating new scripts)
├── templates/
│   └── hypnosis_template.ssml        # SSML template
├── docs/                              # All documentation
├── requirements.txt                   # Python dependencies
├── activate.sh                        # Quick activation script
└── README.md                          # Project documentation
```

---

## 🚀 Step 1: Run the Setup Script

### Download and Run

```bash
# Download the setup script (if not already downloaded)
cd ~/Downloads  # or wherever you saved it

# Make it executable
chmod +x setup_dreamweaving_project.sh

# Run the setup
./setup_dreamweaving_project.sh
```

The script will:
- ✅ Create complete project structure
- ✅ Set up Python virtual environment
- ✅ Install all Python dependencies
- ✅ Create VS Code configuration
- ✅ Add the original prompt template
- ✅ Create SSML templates
- ✅ Set up helper scripts

**Time required:** 2-3 minutes

---

## 🔧 Step 2: Complete Dependencies

### Install FFmpeg (Required for Audio Concatenation)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Verify:**
```bash
ffmpeg -version
```

### Setup Google Cloud (One-Time)

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize
gcloud init

# Authenticate for API access
gcloud auth application-default login

# Enable Text-to-Speech API
gcloud services enable texttospeech.googleapis.com
```

---

## 📁 Step 3: Move Your Garden of Eden Files

```bash
# Navigate to project
cd ~/Projects/dreamweaving

# Move your SSML script
mv ~/path/to/garden_of_eden_hypnosis.ssml sessions/garden-of-eden/

# Move the generator script (if you have it separately)
mv ~/path/to/generate_audio_chunked.py scripts/

# Or download them fresh - the setup already created the scripts folder
```

---

## 💻 Step 4: Open in VS Code

```bash
cd ~/Projects/dreamweaving
code .
```

VS Code will:
- ✅ Auto-detect the Python virtual environment
- ✅ Enable SSML syntax highlighting
- ✅ Configure debugging
- ✅ Activate venv in integrated terminal

---

## 🎙️ Step 5: Generate Your First Audio

### Activate Environment

```bash
cd ~/Projects/dreamweaving
source venv/bin/activate
```

You should see `(venv)` in your prompt.

### Generate Garden of Eden Audio

```bash
python scripts/generate_audio_chunked.py \
    sessions/garden-of-eden/garden_of_eden_hypnosis.ssml \
    sessions/garden-of-eden/output/garden_of_eden.mp3
```

**Output:**
- Audio file: `sessions/garden-of-eden/output/garden_of_eden.mp3`
- Duration: ~27 minutes
- Size: ~12 MB
- Quality: Professional, 24kHz

---

## 🆕 Creating New Hypnosis Sessions

### Method 1: Use the Helper Script (Recommended)

```bash
# Activate environment
source venv/bin/activate

# Create new session
./scripts/create_new_session.sh inner-child-healing

# This creates:
# sessions/inner-child-healing/
# ├── inner-child-healing.ssml  (template)
# ├── output/                    (for generated audio)
# └── README.md                  (session notes)
```

### Method 2: Manual Creation

```bash
# Create session folder
mkdir -p sessions/abundance-meditation/output

# Copy template
cp templates/hypnosis_template.ssml \
   sessions/abundance-meditation/abundance.ssml

# Edit in VS Code
code sessions/abundance-meditation/abundance.ssml
```

---

## ✍️ Writing New Scripts

### Follow the Original Prompt

The complete prompt instructions are in:
```
prompts/hypnotic_dreamweaving_instructions.md
```

This contains:
- ✅ All 5 mandatory sections
- ✅ Writing style guidelines
- ✅ SSML formatting examples
- ✅ Thematic elements
- ✅ Quality checklist

### Use the SSML Template

Start with:
```
templates/hypnosis_template.ssml
```

This template includes:
- Proper XML/SSML structure
- All 5 sections pre-marked
- Example tags and formatting
- Comments guiding you

### Key Points

1. **Always use the 5-section structure:**
   - Pre-talk Introduction
   - Induction
   - Main Journey
   - Integration & Return
   - Post-Hypnotic Anchors

2. **Include all 5 senses** in visualizations

3. **Use proper SSML tags:**
   - `<break time="2s"/>` for pauses
   - `<prosody rate="slow" pitch="-2st">` for voice control
   - `<emphasis level="moderate">` for key words
   - `<phoneme>` for pronunciation

4. **Test pronunciation** especially:
   - "path-working" (use phoneme tag or write "path-working")
   - Technical terms
   - Non-English words

---

## 🔄 Daily Workflow

### Starting Work

```bash
# Navigate to project
cd ~/Projects/dreamweaving

# Activate environment (option 1)
source venv/bin/activate

# OR use the helper (option 2)
source activate.sh

# Open VS Code
code .
```

### Creating a New Session

```bash
# 1. Use helper to create structure
./scripts/create_new_session.sh confidence-building

# 2. Write your script (follow prompt template)
code sessions/confidence-building/confidence-building.ssml

# 3. Generate audio
python scripts/generate_audio_chunked.py \
    sessions/confidence-building/confidence-building.ssml \
    sessions/confidence-building/output/confidence.mp3

# 4. Test and refine
# Listen, adjust SSML, regenerate as needed
```

### When Finished

```bash
# Deactivate virtual environment
deactivate
```

---

## 🎨 Customization Options

### Change Voice

Edit `scripts/generate_audio_chunked.py` or pass as argument:

```bash
python scripts/generate_audio_chunked.py \
    sessions/my-session/script.ssml \
    sessions/my-session/output/audio.mp3 \
    en-US-Neural2-D  # Male voice
```

**Voice Options:**
- Female: Neural2-A (default), Neural2-C, Neural2-E, Neural2-F
- Male: Neural2-D, Neural2-I, Neural2-J

### Adjust Speaking Rate

Edit `generate_audio_chunked.py` line ~120:
```python
speaking_rate=0.85,  # Change to 0.75 (slower) or 0.95 (faster)
```

### Adjust Pitch

Edit `generate_audio_chunked.py` line ~121:
```python
pitch=-2.0,  # Change to -4.0 (deeper) or 0.0 (normal)
```

---

## 📊 Project Organization

### Session Structure

Each session should have:
```
sessions/session-name/
├── script.ssml           # The hypnosis script
├── output/
│   ├── audio.mp3        # Generated audio
│   └── audio_v2.mp3     # Iterations
└── README.md            # Session notes
```

### Session README Template

```markdown
# Session Name

**Theme:** Inner child healing
**Goal:** Release childhood trauma, reconnect with innocence
**Duration:** 30 minutes
**Created:** 2025-11-22

## Generate

\`\`\`bash
python scripts/generate_audio_chunked.py \
    sessions/session-name/script.ssml \
    sessions/session-name/output/audio.mp3
\`\`\`

## Notes
- Version 1: Initial script
- Version 2: Added longer pauses in return sequence
```

---

## 🛠️ Troubleshooting

### Virtual Environment Issues

**Problem:** `source venv/bin/activate` doesn't work

**Solution:**
```bash
# Make sure you're in project root
cd ~/Projects/dreamweaving

# Try with full path
source ~/Projects/dreamweaving/venv/bin/activate

# Or use the helper
source activate.sh
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'pydub'`

**Solution:**
```bash
# Make sure venv is activated (see (venv) in prompt)
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### FFmpeg Not Found

**Problem:** `FFmpeg not found` or `decoder not available`

**Solution:**
```bash
# Install FFmpeg
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS

# Verify
ffmpeg -version
which ffmpeg
```

### Google Cloud Authentication

**Problem:** `Authentication required` or `API not enabled`

**Solution:**
```bash
# Re-authenticate
gcloud auth application-default login

# Enable API
gcloud services enable texttospeech.googleapis.com

# Verify
gcloud auth application-default print-access-token
```

### SSML Errors

**Problem:** `Invalid SSML` or parsing errors

**Solution:**
- Check all XML tags are properly closed
- Verify `<speak>` tags at start and end
- Ensure special characters are escaped
- Use XML validator: `xmllint --noout your-script.ssml`

---

## 💰 Cost Management

### Google Cloud TTS Pricing

- **Free tier:** 1,000,000 characters/month
- **Average session:** ~25,000 characters
- **Free sessions per month:** ~40

### Track Usage

```bash
# Check current month's usage
gcloud logging read "resource.type=cloud_function" --limit 50

# Or view in console
https://console.cloud.google.com/apis/api/texttospeech.googleapis.com
```

### Cost After Free Tier

- $4.00 per 1 million characters
- ~$0.10 per session after free tier

---

## 📚 Reference Documentation

### In Your Project

- `README.md` - Project overview and commands
- `prompts/hypnotic_dreamweaving_instructions.md` - Complete script writing guide
- `templates/hypnosis_template.ssml` - SSML template
- `docs/` - Additional documentation

### Online Resources

- [Google Cloud TTS Docs](https://cloud.google.com/text-to-speech/docs)
- [SSML Reference](https://cloud.google.com/text-to-speech/docs/ssml)
- [Voice Options](https://cloud.google.com/text-to-speech/docs/voices)

---

## 🎯 Quick Commands Cheat Sheet

```bash
# Activate environment
source venv/bin/activate

# Create new session
./scripts/create_new_session.sh session-name

# Generate audio
python scripts/generate_audio_chunked.py sessions/NAME/script.ssml sessions/NAME/output/audio.mp3

# With specific voice
python scripts/generate_audio_chunked.py sessions/NAME/script.ssml output.mp3 en-US-Neural2-D

# Check dependencies
pip list | grep google-cloud
ffmpeg -version

# Deactivate
deactivate
```

---

## 🌟 Session Ideas

- **Healing:**
  - Inner child healing
  - Trauma release
  - Grief processing
  - Forgiveness journey

- **Growth:**
  - Confidence building
  - Creativity awakening
  - Leadership empowerment
  - Public speaking ease

- **Spiritual:**
  - Chakra activation
  - Past life regression
  - Spirit guide connection
  - Higher self communication

- **Abundance:**
  - Wealth consciousness
  - Prosperity mindset
  - Success visualization
  - Manifesting goals

- **Wellness:**
  - Deep sleep
  - Pain management
  - Stress release
  - Anxiety relief

- **Relationships:**
  - Self-love
  - Attracting love
  - Healing heartbreak
  - Family harmony

---

## ✅ Setup Verification Checklist

Before generating your first audio, verify:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Python packages installed (`pip list`)
- [ ] FFmpeg installed (`ffmpeg -version`)
- [ ] Google Cloud SDK installed (`gcloud version`)
- [ ] Authenticated (`gcloud auth list`)
- [ ] TTS API enabled
- [ ] VS Code opened with correct Python interpreter
- [ ] Project structure looks correct
- [ ] All files in proper folders

---

## 🎊 You're Ready!

Your professional dreamweaving environment is complete. You can now:

✅ Generate the Garden of Eden audio
✅ Create unlimited new hypnosis sessions
✅ Follow the original prompt for quality scripts
✅ Use templates for faster creation
✅ Organize everything professionally
✅ Scale to dozens or hundreds of sessions

**Start creating transformational audio today!**

```bash
cd ~/Projects/dreamweaving
source venv/bin/activate
python scripts/generate_audio_chunked.py \
    sessions/garden-of-eden/garden_of_eden_hypnosis.ssml \
    sessions/garden-of-eden/output/garden_of_eden.mp3
```

---

*Walk in innocence. Choose with wisdom. Live in wholeness.* 🌿

**Created by: The Sacred Digital Dreamweaver**  
Randy Sailer's Autonomous AI Clone
