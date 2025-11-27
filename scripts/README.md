# Dreamweaving Scripts

**Complete toolkit for automated meditation video production**

All tools for audio generation, image generation, and video production.

---

## Quick Links

- **[Image Generation Guide](IMAGE_GENERATION_GUIDE.md)** - Complete guide for AI image generation
- **[Quick Start](QUICKSTART_IMAGE_GEN.md)** - Quick reference for images
- **[Production Manual](../sessions/garden-of-eden/PRODUCTION_MANUAL.md)** - Complete workflow

---

## Directory Structure

```
scripts/
├── core/
│   ├── generate_images_sd.py          # AI image generation (NEW!)
│   ├── setup_image_generation.sh      # Setup for image generation
│   ├── generate_audio_chunked.py      # Audio generation
│   └── generate_audio.py              # Simple audio generation
├── synthesis/                         # Specialized synthesis scripts
├── utilities/                         # Helper scripts and tools
├── IMAGE_GENERATION_GUIDE.md          # Complete image generation guide (NEW!)
├── QUICKSTART_IMAGE_GEN.md            # Quick reference card (NEW!)
└── README.md                          # This file
```

---

## Core Scripts

Located in `scripts/core/`

### generate_images_sd.py ⭐ NEW!

**Purpose:** Automated meditation image generation using Stable Diffusion XL

**Usage:**
```bash
# One-time setup (first time only)
./scripts/core/setup_image_generation.sh

# Generate images for Garden of Eden
python3 scripts/core/generate_images_sd.py

# Custom session
python3 scripts/core/generate_images_sd.py --session-dir sessions/my-session

# Quality options
python3 scripts/core/generate_images_sd.py --quality draft   # Fast (30 steps)
python3 scripts/core/generate_images_sd.py --quality normal  # Balanced (50 steps)
python3 scripts/core/generate_images_sd.py --quality high    # Best (80 steps)

# Candidate selection
python3 scripts/core/generate_images_sd.py --candidates 5   # Generate 5 versions per image
```

**Features:**
- **100% free** - No API costs, unlimited generation
- **Highest quality** - Uses Stable Diffusion XL
- **GPU accelerated** - 20-60 seconds per image (or CPU/Apple Silicon)
- **Multiple candidates** - Generate 3+ versions, pick best
- **Metadata saving** - Reproducible with seeds
- **Draft mode** - Quick testing of prompts

**System Requirements:**
- GPU: NVIDIA 8+ GB VRAM (recommended: 10+ GB)
- RAM: 16 GB minimum (32 GB recommended)
- Storage: 15 GB for model cache (one-time download)
- Time: 20-60 seconds per image (GPU), 5-10 minutes (CPU)

**First run:** Downloads SDXL model (~13 GB), cached for future use

**Documentation:** See [IMAGE_GENERATION_GUIDE.md](IMAGE_GENERATION_GUIDE.md) for complete guide

---

### generate_audio_chunked.py

**Purpose:** Main audio generation script for SSML files of any size. Automatically splits large files into chunks.

**Usage:**
```bash
python scripts/core/generate_audio_chunked.py INPUT.ssml OUTPUT.mp3 [VOICE_NAME]
```

**Examples:**
```bash
# Basic usage (default voice: en-US-Neural2-A)
python scripts/core/generate_audio_chunked.py \
    sessions/my-session/script.ssml \
    sessions/my-session/output/audio.mp3

# With custom voice
python scripts/core/generate_audio_chunked.py \
    sessions/my-session/script.ssml \
    sessions/my-session/output/audio.mp3 \
    en-US-Neural2-D

# From any directory
python ~/Projects/dreamweaving/scripts/core/generate_audio_chunked.py \
    ~/path/to/script.ssml \
    ~/path/to/output.mp3
```

**Features:**
- Automatically chunks SSML files >5000 bytes
- Splits at natural sentence boundaries
- Merges all chunks into single MP3
- Progress indicators
- Optimized settings for hypnosis (rate: 0.85, pitch: -2.0)

**When to use:** For any SSML file, especially files >5KB. This is the recommended script.

---

### generate_audio.py

**Purpose:** Simple audio generation for small SSML files.

**Usage:**
```bash
python scripts/core/generate_audio.py INPUT.ssml OUTPUT.mp3 [VOICE_NAME]
```

**When to use:**
- SSML files <5000 bytes
- Testing small snippets
- Quick prototyping

**Limitation:** Will error if SSML exceeds 5000 bytes. Use `generate_audio_chunked.py` instead.

---

## Synthesis Scripts

Located in `scripts/synthesis/`

Specialized scripts for generating specific sections or testing voice synthesis.

### synthesize_pretalk.py
Generate pre-talk/introduction sections only.

### synthesize_opening.py (synthesize_hypnotic_opening.py)
Generate induction/opening sections with hypnotic pacing.

### synthesize_closing.py
Generate closing/return sections.

### synthesize_natural_hypnotic.py
Natural voice with hypnotic pacing.

### synthesize_matched_hypnotic.py
Matched voice characteristics for consistency.

### synthesize_intro_natural.py
Natural-sounding introductions.

### synthesize_ai_pretalk.py
AI-focused pre-talk generation.

**Note:** These are specialized tools. Most users should use `scripts/core/generate_audio_chunked.py` for complete sessions.

---

## Utility Scripts

Located in `scripts/utilities/`

### create_new_session.sh

**Purpose:** Quickly create a new session folder structure.

**Usage:**
```bash
./scripts/utilities/create_new_session.sh "session-name"
```

**Example:**
```bash
./scripts/utilities/create_new_session.sh "inner-child-healing"
```

**Creates:**
```
sessions/inner-child-healing/
├── script.ssml          # From base template
├── notes.md             # Session notes file
├── output/              # For generated audio
└── variants/            # For alternative versions
```

**Permissions:** Make executable if needed:
```bash
chmod +x scripts/utilities/create_new_session.sh
```

---

### validate_ssml.py

**Purpose:** Validate SSML syntax and provide helpful feedback before generating audio.

**Usage:**
```bash
python scripts/utilities/validate_ssml.py path/to/script.ssml
```

**Example:**
```bash
python scripts/utilities/validate_ssml.py sessions/my-session/script.ssml
```

**Output:**
- ✅ XML syntax validation
- 📊 File size and chunk analysis
- 📋 Content statistics (word count, element counts)
- ⏱️ Estimated duration
- 🔍 Common issues detection
- ⚠️ Warnings for potential problems

**Features:**
- Checks for unmatched tags
- Detects placeholders that need replacement
- Warns about low break density
- Identifies special characters needing escaping
- Provides actionable recommendations

**When to use:** Before generating audio to catch errors early.

---

### batch_generate.py

**Purpose:** Generate audio for multiple sessions at once.

**Usage:**
```bash
python scripts/utilities/batch_generate.py sessions/*/script.ssml
```

**Status:** Placeholder - to be implemented in v2.1

---

### audio_merger.py

**Purpose:** Merge audio files with optional background audio.

**Usage:**
```bash
python scripts/utilities/audio_merger.py \
    sessions/my-session/output/audio.mp3 \
    resources/background_audio/nature/rain.mp3 \
    sessions/my-session/output/audio_with_bg.mp3
```

**Status:** Placeholder - to be implemented in v2.1

---

## Common Workflows

### Generate a new session

```bash
# 1. Create session structure
./scripts/utilities/create_new_session.sh "my-session"

# 2. Edit the script
code sessions/my-session/script.ssml

# 3. Validate (optional but recommended)
python scripts/utilities/validate_ssml.py sessions/my-session/script.ssml

# 4. Generate audio
python scripts/core/generate_audio_chunked.py \
    sessions/my-session/script.ssml \
    sessions/my-session/output/audio.mp3
```

### Try different voices

```bash
# Female voices
python scripts/core/generate_audio_chunked.py input.ssml output_warm.mp3 en-US-Neural2-A
python scripts/core/generate_audio_chunked.py input.ssml output_soft.mp3 en-US-Neural2-C
python scripts/core/generate_audio_chunked.py input.ssml output_deep.mp3 en-US-Neural2-E

# Male voices
python scripts/core/generate_audio_chunked.py input.ssml output_male.mp3 en-US-Neural2-D
python scripts/core/generate_audio_chunked.py input.ssml output_warm_male.mp3 en-US-Neural2-I
```

See `config/voice_profiles.json` for all available voices.

### Regenerate after editing

```bash
# Edit SSML
code sessions/my-session/script.ssml

# Regenerate (overwrites existing)
python scripts/core/generate_audio_chunked.py \
    sessions/my-session/script.ssml \
    sessions/my-session/output/audio.mp3
```

---

## Voice Settings

### Default Settings (Optimized for Hypnosis)

All scripts use these defaults:
- **Speaking Rate:** 0.85 (slower, hypnotic)
- **Pitch:** -2.0 semitones (calming)
- **Audio Format:** MP3
- **Sample Rate:** 24kHz
- **Device Optimization:** Headphone-class

### Available Voices

See `config/voice_profiles.json` for complete list.

**Recommended for hypnosis:**
- `en-US-Neural2-A` - Warm, calming female (default)
- `en-US-Neural2-C` - Soft, nurturing female
- `en-US-Neural2-D` - Deep, resonant male
- `en-US-Neural2-I` - Warm, compassionate male

---

## Troubleshooting

### Script not found
```bash
# Ensure you're in project root
cd ~/Projects/dreamweaving

# Or use absolute paths
python ~/Projects/dreamweaving/scripts/core/generate_audio_chunked.py ...
```

### Permission denied
```bash
# Make scripts executable
chmod +x scripts/utilities/*.sh
chmod +x scripts/utilities/*.py
```

### Import errors
```bash
# Activate virtual environment first
source venv/bin/activate

# Verify installation
pip list | grep google-cloud-texttospeech
```

### Chunk too large
Add more `<break>` tags in your SSML to create natural split points.

---

## Advanced Usage

### Custom Audio Settings

Edit `scripts/core/generate_audio_chunked.py` to modify:
- Speaking rate (line ~100)
- Pitch adjustment (line ~101)
- Sample rate (line ~95)
- Audio encoding (line ~94)

### Batch Processing

```bash
# Generate all sessions
for session in sessions/*/script.ssml; do
    dir=$(dirname "$session")
    python scripts/core/generate_audio_chunked.py \
        "$session" \
        "$dir/output/audio.mp3"
done
```

### Testing SSML Snippets

Create a test file and generate quickly:
```bash
cat > test.ssml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
<prosody rate="slow" pitch="-2st">
This is a test.<break time="1s"/> Just testing.
</prosody>
</speak>
EOF

python scripts/core/generate_audio.py test.ssml test.mp3
```

---

## Adding New Scripts

When creating new scripts:

1. **Place in appropriate directory:**
   - Core audio generation → `scripts/core/`
   - Specialized synthesis → `scripts/synthesis/`
   - Helper tools → `scripts/utilities/`

2. **Make executable:**
   ```bash
   chmod +x scripts/utilities/my_script.py
   ```

3. **Add shebang:**
   ```python
   #!/usr/bin/env python3
   ```

4. **Document in this README**

---

## Related Documentation

- [Quick Start Guide](../docs/QUICK_START.md)
- [Workflow Guide](../docs/WORKFLOW_GUIDE.md)
- [Troubleshooting](../docs/TROUBLESHOOTING.md)
- [Voice Profiles](../config/voice_profiles.json)
- [Master Index](../docs/INDEX.md)

---

*For complete project documentation, see [docs/INDEX.md](../docs/INDEX.md)*
