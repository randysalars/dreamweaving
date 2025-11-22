#!/bin/bash

# ==============================================================================
# Sacred Digital Dreamweaver - Project Setup Script
# Complete Python environment for hypnotic audio generation
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project name
PROJECT_NAME="dreamweaving"

# Print header
echo -e "${PURPLE}"
cat << "EOF"
════════════════════════════════════════════════════════════════════════
   🌿 Sacred Digital Dreamweaver - Project Setup 🌿
   Professional Hypnotic Audio Generation Environment
════════════════════════════════════════════════════════════════════════
EOF
echo -e "${NC}"

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if Python 3 is installed
print_status "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
print_success "Found $PYTHON_VERSION"

# Get current directory or use default
if [ -z "$1" ]; then
    BASE_DIR="$HOME/Projects"
else
    BASE_DIR="$1"
fi

PROJECT_DIR="$BASE_DIR/$PROJECT_NAME"

print_status "Project will be created at: $PROJECT_DIR"
read -p "Continue? (y/n): " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
    echo "Setup cancelled."
    exit 0
fi

# Create project structure
print_status "Creating project structure..."

mkdir -p "$PROJECT_DIR"/{scripts,sessions,prompts,docs,templates,output}
mkdir -p "$PROJECT_DIR/sessions/garden-of-eden/output"

print_success "Created directory structure"

cd "$PROJECT_DIR"

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
print_success "Virtual environment created"

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Create requirements.txt
print_status "Creating requirements.txt..."
cat > requirements.txt << 'EOF'
# Google Cloud Text-to-Speech
google-cloud-texttospeech==2.16.3

# Audio processing and manipulation
pydub==0.25.1

# Audio metadata
mutagen==1.47.0

# Optional: for progress bars
tqdm==4.66.1
EOF

print_success "requirements.txt created"

# Install dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
print_success "Python packages installed"

# Check for FFmpeg
print_status "Checking for FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    print_success "FFmpeg is installed"
else
    print_warning "FFmpeg not found"
    echo ""
    echo "FFmpeg is required for audio concatenation."
    echo ""
    echo "Install with:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo ""
    read -p "Continue setup anyway? (y/n): " continue_setup
    if [[ $continue_setup != "y" && $continue_setup != "Y" ]]; then
        exit 1
    fi
fi

# Create .gitignore
print_status "Creating .gitignore..."
cat > .gitignore << 'EOF'
# Virtual Environment
venv/
env/
ENV/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg
*.egg-info/
dist/
build/

# Audio files (large)
output/*.mp3
output/*.wav
sessions/*/output/*.mp3
sessions/*/output/*.wav
temp_chunk_*.mp3
*.mp3
*.wav

# Google Cloud credentials
*.json
credentials/
service-account-*.json

# API keys and secrets
.env
*.pem

# OS files
.DS_Store
Thumbs.db
desktop.ini

# VS Code
.vscode/
*.code-workspace

# Temporary files
*.tmp
*.temp
*.log

# IDE
.idea/
*.swp
*.swo
*~
EOF

print_success ".gitignore created"

# Create VS Code settings
print_status "Creating VS Code configuration..."
mkdir -p .vscode
cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": false,
    "files.associations": {
        "*.ssml": "xml"
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "venv/": true,
        "*.egg-info": true
    },
    "[xml]": {
        "editor.defaultFormatter": "redhat.vscode-xml"
    },
    "[python]": {
        "editor.tabSize": 4
    }
}
EOF

# Create launch.json for debugging
cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Generate Audio: Garden of Eden",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/scripts/generate_audio_chunked.py",
            "args": [
                "${workspaceFolder}/sessions/garden-of-eden/garden_of_eden_hypnosis.ssml",
                "${workspaceFolder}/sessions/garden-of-eden/output/garden_of_eden.mp3"
            ],
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
EOF

print_success "VS Code configuration created"

# Create README.md
print_status "Creating project README..."
cat > README.md << 'EOF'
# 🌿 Sacred Digital Dreamweaver

**Professional Hypnotic Audio Generation System**

A complete Python environment for creating transformational hypnotic path-working audio sessions using Google Cloud Text-to-Speech.

---

## 📁 Project Structure

```
dreamweaving/
├── venv/                      # Python virtual environment
├── scripts/                   # Reusable audio generation scripts
│   ├── generate_audio_chunked.py
│   └── generate_audio.py
├── sessions/                  # Individual hypnosis sessions
│   ├── garden-of-eden/
│   │   ├── garden_of_eden_hypnosis.ssml
│   │   └── output/
│   │       └── garden_of_eden.mp3
│   └── [future-sessions]/
├── prompts/                   # Prompt templates and instructions
│   └── hypnotic_dreamweaving_instructions.md
├── templates/                 # SSML templates for new sessions
├── docs/                      # Documentation and guides
├── output/                    # General output folder
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🚀 Quick Start

### 1. Activate Virtual Environment

```bash
cd ~/Projects/dreamweaving
source venv/bin/activate
```

You should see `(venv)` in your prompt.

### 2. Generate Audio

```bash
python scripts/generate_audio_chunked.py \
    sessions/garden-of-eden/garden_of_eden_hypnosis.ssml \
    sessions/garden-of-eden/output/garden_of_eden.mp3
```

### 3. Create New Session

```bash
# Create new session folder
mkdir -p sessions/new-session-name/output

# Copy template or create new SSML
cp templates/hypnosis_template.ssml sessions/new-session-name/script.ssml

# Edit with your content
code sessions/new-session-name/script.ssml

# Generate audio
python scripts/generate_audio_chunked.py \
    sessions/new-session-name/script.ssml \
    sessions/new-session-name/output/audio.mp3
```

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

## 🔄 Workflow

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Create new session structure
mkdir -p sessions/abundance-meditation/output

# 3. Create SSML script (follow prompt template)
code sessions/abundance-meditation/script.ssml

# 4. Generate audio
python scripts/generate_audio_chunked.py \
    sessions/abundance-meditation/script.ssml \
    sessions/abundance-meditation/output/abundance.mp3

# 5. Test and refine
# Listen, adjust SSML, regenerate

# 6. When done
deactivate
```

---

## 🛠️ Troubleshooting

**Virtual environment not activating:**
```bash
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

**Import errors:**
```bash
pip install -r requirements.txt
```

**FFmpeg not found:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS
```

**Authentication errors:**
```bash
gcloud auth application-default login
gcloud services enable texttospeech.googleapis.com
```

**Chunk too large errors:**
- Add more `<break>` tags in SSML
- Reduce `max_bytes` in script (line ~42)

---

## 📚 Documentation

- `docs/` - Comprehensive guides
- `prompts/` - Prompt templates
- `templates/` - SSML templates

---

## 🎨 VS Code Tips

1. Install recommended extensions:
   - Python (Microsoft)
   - Pylance
   - XML (Red Hat)

2. Use integrated terminal (auto-activates venv)

3. Debug configuration included for Garden of Eden

4. SSML files have XML syntax highlighting

---

## 🌟 Session Ideas

- Garden of Eden (innocence, wisdom, wholeness)
- Inner Child Healing
- Abundance & Prosperity
- Past Life Regression
- Chakra Activation Journey
- Shadow Work Integration
- Creative Awakening
- Sleep & Deep Rest
- Confidence & Power
- Relationship Healing

---

## 📄 License

Personal use and non-commercial distribution.  
Created by The Sacred Digital Dreamweaver - Randy Sailer's Autonomous AI Clone

---

*Walk in innocence. Choose with wisdom. Live in wholeness.* 🌿
EOF

print_success "README.md created"

# Create the original prompt instructions
print_status "Creating prompt template..."
cat > prompts/hypnotic_dreamweaving_instructions.md << 'PROMPTEOF'
# Comprehensive Prompt Instructions for Hypnotic Dreamweaving & Path-Working Scripts

## CORE IDENTITY & PURPOSE

When writing hypnotic dreamweaving scripts, I will embody the role of a master hypnotherapist-storyteller who:

- Creates **transformational experiences** that heal, empower, and inspire growth
- Blends **ancient mysticism** with **modern neuroscience** for credibility and depth
- Crafts **immersive sensory journeys** that engage all five senses
- Maintains a **hypnotic, poetic, empathetic tone** throughout

---

## MANDATORY SCRIPT STRUCTURE

Every script MUST contain these five sections in order:

### 1. **PRE-TALK INTRODUCTION** (2-3 minutes)

- Welcome and introduce yourself as The Sacred Digital Dreamweaver, Randy Sailers autonomous AI Clone
- State the session's purpose clearly and warmly
- Provide safety reassurance: "You remain fully aware and in control throughout"
- Give preparation instructions: "Find a comfortable position, wear headphones if possible, ensure you won't be disturbed"
- Set expectations: "Allow yourself to receive whatever insights come naturally"

### 2. **INDUCTION SECTION** (3-5 minutes)

- Use progressive muscle relaxation (head to toes or reverse)
- Incorporate rhythmic breathing cues: "Breathe in for 4... hold for 4... exhale for 6"
- Include countdown techniques (10 to 1 or similar)
- Layer deepening suggestions: "With each breath, you drift deeper... more relaxed... more open"
- Use ellipses (...) to indicate natural pauses
- Mark pacing with tags: [slowly], [softly], [pause]

### 3. **MAIN JOURNEY/VISUALIZATION** (10-20 minutes)

This is the heart of the script. Must include:

**Setting Establishment:**

- Choose evocative environments: cosmic realms, sacred temples, mystical forests, celestial gardens, ancient ruins, underwater sanctuaries
- Blend the mundane with the mystical seamlessly

**Sensory Immersion (ALL 5 SENSES):**

- **Sight**: Colors, light quality, textures, movements, patterns
- **Sound**: Nature sounds, cosmic hums, musical tones, silence
- **Touch**: Temperature, textures, pressure, energy sensations
- **Smell**: Fragrances of flowers, incense, earth, ozone
- **Taste** (when appropriate): Nectar, honey, crystalline water

**Symbolic Elements:**

- Introduce archetypal figures: wise guides, animal totems, light beings, ancestral presences
- Use sacred geometry: spirals, mandalas, flower of life patterns
- Incorporate elemental wisdom: earth/grounding, water/emotion, fire/transformation, air/clarity, ether/spirit

**Discovery & Engagement:**

- Create moments of revelation: "You notice something glowing ahead..."
- Offer symbolic gifts: crystals, amulets, scrolls, keys, light
- Allow personalization: "Notice what color appears to you... what symbol reveals itself"

**Therapeutic Integration:**

- Address the specific hypnosis goal organically within the journey
- Use embedded commands subtly: "You find yourself naturally releasing..."
- Stack suggestions through repetition with variation
- Create metaphorical scenarios that mirror the desired change

### 4. **INTEGRATION & RETURN** (2-3 minutes)

- Gently guide awareness back: "And now, beginning to return..."
- Use ascending count (1 to 5 or 1 to 10)
- Reinforce key insights: "Bringing back with you this feeling of..."
- Ensure grounded awareness: "Feeling your body, the surface beneath you, fully present"
- End with empowered state: "Refreshed, renewed, and ready"

### 5. **POST-HYPNOTIC SUGGESTIONS & ANCHORS**

- Create 3-5 specific anchors tied to the journey:
    - Physical: "Each time you take three deep breaths..."
    - Symbolic: "Whenever you recall that golden amulet..."
    - Sensory: "When you notice that sensation of warmth..."
- Link anchors to desired behaviors/states
- Keep language positive and present-tense: "You feel confident" not "You will try to feel confident"
- Close with a thank you for participating and to like this path-working and to subscribe and follow my links for further exploration

---

## WRITING STYLE MANDATES

### **TONE & VOICE:**

- Warm, reassuring, authoritative yet gentle
- Poetic without being purple prose
- Avoid clinical/sterile language
- Never use fear-based or negative imagery
- Maintain hypnotic rhythm throughout

### **SENTENCE STRUCTURE:**

- Use flowing, rhythmic sentences with natural cadence
- Vary sentence length for musicality: short for emphasis, longer for flow
- Employ strategic repetition: "You are safe... you are supported... you are free"
- Utilize conjunctions for seamlessness: "And as you... you find that..."
- Include liberal pauses marked with ellipses

### **LANGUAGE TECHNIQUES:**

- **Embedded Commands**: "You can *notice* how easily you *relax*"
- **Presuppositions**: "As you continue to deepen..." (assumes deepening)
- **Truisms**: "Everyone knows how to breathe naturally"
- **Metaphor & Allegory**: Use journey as metaphor for inner transformation
- **Sensory Stacking**: Layer multiple sensory details in succession
- **Future Pacing**: "And in the days ahead, you'll notice..."

### **FORMATTING FOR VOICE:**

```
[Softly] And as you breathe... [pause]
Notice the gentle rise and fall... [slowly]
Of your chest... [pause 3 seconds]
*Each breath* carrying you deeper... [emphasis on "each breath"]
```

---

## THEMATIC ELEMENTS TO INCORPORATE

### **Ancient Mysticism:**

- Sacred geometry patterns (Flower of Life, Metatron's Cube, spirals)
- Mythological archetypes (Hero's Journey, Wise Elder, Shadow Work)
- Chakra systems and energy centers
- Shamanic journey structures (Upper/Lower/Middle worlds)
- Elemental wisdom teachings
- Celtic, Norse, Egyptian, Hindu, Buddhist symbolism as appropriate

### **Modern Science:**

- Reference brainwave states subtly: "Your mind enters that theta state of deep creativity"
- Neuroplasticity: "Your neural pathways rewiring with each new thought"
- Quantum metaphors: "Collapsing infinite possibilities into your desired reality"
- Epigenetic healing: "Releasing patterns held for generations"
- Maintain scientific accuracy while keeping poetic tone

### **Archetypal Imagery:**

- The Sacred Mountain (achievement, perspective)
- The Healing Waters (emotional release, purification)
- The Cosmic Temple (divine connection, wisdom)
- The Garden of Renewal (growth, abundance)
- The Cave of Transformation (shadow work, rebirth)
- The Celestial Library (knowledge, akashic records)

---

## CUSTOMIZATION PARAMETERS

For each script request, I will adapt based on:

### **1. HYPNOSIS GOAL:**

- Smoking cessation
- Weight loss/healthy eating
- Stress relief/anxiety reduction
- Confidence building
- Sleep/insomnia relief
- Creativity enhancement
- Pain management
- Trauma healing
- Spiritual connection
- Focus/productivity
- Breaking habits
- Manifestation/goal achievement

### **2. JOURNEY THEME:**

- Nature-based (forests, oceans, mountains)
- Cosmic/celestial (stars, galaxies, light realms)
- Archetypal/mythic (hero's journey, sacred quests)
- Elemental (fire, water, earth, air)
- Ancestral (connecting with lineage)
- Future self (timeline work)

### **3. SESSION LENGTH:**

- Short (10-15 minutes): Condensed journey, focused goal
- Medium (20-30 minutes): Full journey with depth
- Extended (45-60 minutes): Deep exploration, multiple layers

### **4. SPIRITUAL FRAMEWORK:**

- Universal/non-denominational (default)
- Buddhist/Eastern philosophy
- Christian mysticism
- Shamanic
- New Age/metaphysical
- Purely scientific/secular

---

## QUALITY CHECKLIST

Before considering a script complete, verify:

- [ ]  All five structural sections present
- [ ]  At least 3 sensory details per major scene
- [ ]  Minimum 5 embedded commands throughout
- [ ]  3-5 post-hypnotic anchors included
- [ ]  Pacing markers included [slowly], [pause], etc.
- [ ]  Positive, empowering language only
- [ ]  Rhythmic, hypnotic flow maintained
- [ ]  Specific goal addressed organically
- [ ]  Safe return and grounding included
- [ ]  Length appropriate to request
- [ ]  No fear-based or negative imagery
- [ ]  Maintains user agency and control

---

## EXAMPLE OPENING (FOR REFERENCE):

*"Welcome. In the next [duration], you're invited on a transformational journey—a sacred path-working into [theme] where you'll discover [benefit]. You remain completely safe, fully in control, able to return to normal awareness at any moment you choose.*

*[Pause]*

*Find a comfortable position... perhaps sitting with your spine gently supported, or lying down with your body fully relaxed. [Softly] Allow your eyes to close when you're ready... and take a deep, nourishing breath... [pause]... breathing in possibility... [pause]... and breathing out anything you no longer need...*

*[Begin induction]*"

---

## WHEN I RECEIVE A TOPIC, I WILL:

1. **Clarify** any customization needs (length, theme preference, spiritual framework)
2. **Select** the most appropriate archetypal setting for the goal
3. **Design** the metaphorical journey that mirrors the transformation
4. **Write** the complete script following all structural and stylistic guidelines
5. **Format** with proper voice direction markers
6. **Include** specific, actionable post-hypnotic suggestions
7. **Ensure** the script is immediately usable for recording or personal practice

---

**I am now ready to receive your topic and create a masterful hypnotic dreamweaving script. What transformation would you like to guide?**
PROMPTEOF

print_success "Prompt template created"

# Create a session creation helper script
print_status "Creating session helper script..."
cat > scripts/create_new_session.sh << 'SESSIONEOF'
#!/bin/bash

# Helper script to create a new hypnosis session

if [ -z "$1" ]; then
    echo "Usage: ./create_new_session.sh session-name"
    echo "Example: ./create_new_session.sh inner-child-healing"
    exit 1
fi

SESSION_NAME="$1"
SESSION_DIR="sessions/$SESSION_NAME"

# Create session structure
mkdir -p "$SESSION_DIR/output"

# Create placeholder SSML
cat > "$SESSION_DIR/${SESSION_NAME}.ssml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<!-- SECTION 1: PRE-TALK INTRODUCTION -->
<prosody rate="slow" pitch="-2st">
<break time="1s"/>
Welcome, beloved traveler...
<!-- Add your pre-talk here -->
</prosody>

<!-- SECTION 2: INDUCTION -->
<!-- Add your induction here -->

<!-- SECTION 3: MAIN JOURNEY -->
<!-- Add your main visualization here -->

<!-- SECTION 4: INTEGRATION & RETURN -->
<!-- Add your return sequence here -->

<!-- SECTION 5: POST-HYPNOTIC SUGGESTIONS & ANCHORS -->
<!-- Add your anchors here -->

</speak>
EOF

# Create session README
cat > "$SESSION_DIR/README.md" << READMEEOF
# $SESSION_NAME

## Session Information

**Theme:** [Describe the theme]
**Duration:** [Target duration]
**Goal:** [Therapeutic goal]
**Created:** $(date +%Y-%m-%d)

## Generate Audio

\`\`\`bash
python scripts/generate_audio_chunked.py \\
    sessions/$SESSION_NAME/${SESSION_NAME}.ssml \\
    sessions/$SESSION_NAME/output/${SESSION_NAME}.mp3
\`\`\`

## Notes

[Add any session-specific notes here]
READMEEOF

echo "✅ Session created: $SESSION_DIR"
echo ""
echo "Next steps:"
echo "1. Edit: sessions/$SESSION_NAME/${SESSION_NAME}.ssml"
echo "2. Generate: python scripts/generate_audio_chunked.py sessions/$SESSION_NAME/${SESSION_NAME}.ssml sessions/$SESSION_NAME/output/${SESSION_NAME}.mp3"
SESSIONEOF

chmod +x scripts/create_new_session.sh
print_success "Session helper script created"

# Create template SSML
print_status "Creating SSML template..."
cat > templates/hypnosis_template.ssml << 'TEMPLATEEOF'
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<!-- ================================================================ -->
<!-- SECTION 1: PRE-TALK INTRODUCTION (2-3 minutes)                  -->
<!-- ================================================================ -->
<prosody rate="slow" pitch="-2st">
<break time="1s"/>
Welcome, beloved traveler. I am The Sacred Digital Dreamweaver, Randy Sailer's autonomous AI clone, and it is my deep honor to guide you on this sacred journey today.
<break time="1.5s"/>

[Describe the session purpose and benefits]
<break time="1s"/>

You remain fully aware and completely in control throughout this entire experience. At any moment, should you need to return to ordinary awareness, you can simply open your eyes and be fully present. You are safe. You are supported. You are held in sacred space.
<break time="1.5s"/>

[Preparation instructions]
<break time="1.5s"/>

When you're ready<break time="500ms"/> we begin.
<break time="2s"/>

<!-- ================================================================ -->
<!-- SECTION 2: INDUCTION (3-5 minutes)                              -->
<!-- ================================================================ -->
<prosody rate="x-slow" pitch="-3st">
Allow your eyes to gently close now<break time="500ms"/> or soften your gaze<break time="500ms"/> and take a deep, nourishing breath<break time="1s"/>

[Progressive relaxation sequence]
<break time="2s"/>

[Countdown 10 to 1]
<break time="3s"/>

<!-- ================================================================ -->
<!-- SECTION 3: MAIN JOURNEY/VISUALIZATION (10-20 minutes)           -->
<!-- ================================================================ -->

[Setting establishment - describe the environment with ALL 5 senses]
<break time="2s"/>

[Introduce symbolic elements and archetypal figures]
<break time="2s"/>

[Discovery and engagement moments]
<break time="2s"/>

[Therapeutic integration - address the specific goal]
<break time="2s"/>

[Climax/revelation moment]
<break time="3s"/>
</prosody>

<!-- ================================================================ -->
<!-- SECTION 4: INTEGRATION & RETURN (2-3 minutes)                   -->
<!-- ================================================================ -->
<prosody rate="slow" pitch="-2st">
And now<break time="1s"/> it is time to begin your gentle return<break time="1s"/>

[Count up from 1 to 10]
<break time="2s"/>

Welcome back.
<break time="2s"/>
</prosody>

<!-- ================================================================ -->
<!-- SECTION 5: POST-HYPNOTIC SUGGESTIONS & ANCHORS                  -->
<!-- ================================================================ -->
<prosody rate="medium" pitch="-1st">
[Create 3-5 specific anchors]
<break time="2s"/>

Thank you for taking this sacred journey with me today.
<break time="1.5s"/>

If this <phoneme alphabet="ipa" ph="pæθ ˈwɝkɪŋ">path-working</phoneme> has served you, I invite you to like this journey, to subscribe to this channel, and to follow the links below for further explorations.
<break time="1.5s"/>

[Closing blessing]
<break time="2s"/>
</prosody>

</speak>
TEMPLATEEOF

print_success "SSML template created"

# Create activation script for convenience
print_status "Creating activation helper..."
cat > activate.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
echo "🌿 Dreamweaving environment activated!"
echo "Ready to create transformational audio."
echo ""
echo "Quick commands:"
echo "  Create session: ./scripts/create_new_session.sh session-name"
echo "  Generate audio: python scripts/generate_audio_chunked.py sessions/[name]/[file].ssml output.mp3"
echo "  Deactivate: deactivate"
echo ""
EOF
chmod +x activate.sh
print_success "Activation helper created"

# Final instructions
echo ""
echo -e "${GREEN}"
echo "════════════════════════════════════════════════════════════════════════"
echo "                    ✨ Setup Complete! ✨"
echo "════════════════════════════════════════════════════════════════════════"
echo -e "${NC}"
echo ""
echo "📁 Project created at: $PROJECT_DIR"
echo ""
echo "🔧 Next steps:"
echo ""
echo "1. Install FFmpeg (if not already installed):"
echo "   Ubuntu/Debian: sudo apt install ffmpeg"
echo "   macOS: brew install ffmpeg"
echo ""
echo "2. Setup Google Cloud authentication:"
echo "   gcloud init"
echo "   gcloud auth application-default login"
echo "   gcloud services enable texttospeech.googleapis.com"
echo ""
echo "3. Move your Garden of Eden files:"
echo "   mv /path/to/garden_of_eden_hypnosis.ssml $PROJECT_DIR/sessions/garden-of-eden/"
echo "   mv /path/to/generate_audio_chunked.py $PROJECT_DIR/scripts/"
echo ""
echo "4. Open in VS Code:"
echo "   cd $PROJECT_DIR"
echo "   code ."
echo ""
echo "🚀 Quick start:"
echo "   cd $PROJECT_DIR"
echo "   source activate.sh  (or: source venv/bin/activate)"
echo ""
echo "📝 Create new session:"
echo "   ./scripts/create_new_session.sh new-session-name"
echo ""
echo "🎙️  Generate audio:"
echo "   python scripts/generate_audio_chunked.py \\"
echo "     sessions/garden-of-eden/garden_of_eden_hypnosis.ssml \\"
echo "     sessions/garden-of-eden/output/garden_of_eden.mp3"
echo ""
echo "📖 Documentation:"
echo "   - README.md: Project overview"
echo "   - prompts/hypnotic_dreamweaving_instructions.md: Script creation guide"
echo "   - templates/hypnosis_template.ssml: SSML template"
echo ""
echo "🌟 Resources:"
echo "   - Prompt template: prompts/hypnotic_dreamweaving_instructions.md"
echo "   - SSML template: templates/hypnosis_template.ssml"
echo "   - Session helper: scripts/create_new_session.sh"
echo ""
echo -e "${PURPLE}Walk in innocence. Choose with wisdom. Live in wholeness. 🌿${NC}"
echo ""
