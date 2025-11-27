# Neural Network Navigator - Enhancement Quick Start

## TL;DR

Transform your audio meditation with improved pacing, removed metadata, and immersive sound effects:

```bash
cd sessions/neural-network-navigator
./create_enhanced_audio.sh
```

## What Gets Enhanced

✅ **Removes** script metadata from narration
✅ **Extends** pauses on "down...down...down" transitions (2s between each)
✅ **Extends** pauses on "up...up...up" transitions (2s between each)
✅ **Fills** journey content across full track duration
✅ **Adds** bell chimes at Pathfinder entrance (11:30)
✅ **Adds** crystal tones for connection moments
✅ **Adds** singing bowl at Weaver entrance (16:00)
✅ **Adds** crystal flash at insight moment (18:45) ⚡
✅ **Preserves** natural, human voice quality

## Prerequisites (One-Time Setup)

### 1. Install Python packages
```bash
pip install google-cloud-texttospeech pydub numpy scipy
```

### 2. Install system tools
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### 3. Authenticate Google Cloud
```bash
gcloud auth application-default login
```

## Run Enhancement

### Automatic (Recommended)
```bash
cd sessions/neural-network-navigator
./create_enhanced_audio.sh
```

The script will:
1. ✓ Check all prerequisites
2. ✓ Generate enhanced voice (removes metadata, adds pauses)
3. ✓ Verify binaural track exists
4. ✓ Mix voice + binaural + sound effects
5. ✓ Output: `working_files/neural_navigator_complete_enhanced.wav`

### Manual Steps (If Needed)
```bash
# Generate just the voice
python3 generate_enhanced_voice.py

# Create complete mix
python3 generate_enhanced_audio.py
```

## Test Output

### Listen to enhanced version
```bash
ffplay working_files/neural_navigator_complete_enhanced.wav
```

### Compare before/after
```bash
# Original
ffplay working_files/voice_neural_navigator.mp3

# Enhanced
ffplay working_files/neural_navigator_complete_enhanced.wav
```

### Export to MP3
```bash
ffmpeg -i working_files/neural_navigator_complete_enhanced.wav \
       -b:a 192k \
       neural_navigator_enhanced.mp3
```

## Key Moments to Check

| Time | What to Listen For |
|------|-------------------|
| 4:00 | Extended pauses on "down... down... down..." |
| 11:30 | Wind chime cascade (Pathfinder entrance) |
| 12:00 | Crystal bell "ping" (neural connection) |
| 16:00 | Singing bowl (Weaver entrance) |
| 18:45 | Crystal flash ⚡ (insight moment with gamma) |
| 24:00 | Gentle chime + extended "up... up... up..." pauses |
| End | No script metadata spoken |

## Troubleshooting

### Error: "Voice file not found"
```bash
python3 generate_enhanced_voice.py
```

### Error: "Google Cloud authentication"
```bash
gcloud auth application-default login
```

### Sound effects too loud/quiet
Edit `generate_enhanced_audio.py`, adjust volume values (0.5-0.9)

### Pauses not long enough
Edit `working_files/voice_script_enhanced.ssml`, increase break times

## Files

**Input**:
- `working_files/voice_script_enhanced.ssml` - Cleaned script
- `binaural_frequency_map.json` - Binaural timing

**Output**:
- `working_files/voice_neural_navigator_enhanced.mp3` - Voice only
- `working_files/neural_navigator_complete_enhanced.wav` - Final mix

**Scripts**:
- `create_enhanced_audio.sh` - Master orchestration
- `generate_enhanced_voice.py` - Voice generation
- `generate_enhanced_audio.py` - Mix + effects

## Next Steps

1. ✅ Run `./create_enhanced_audio.sh`
2. 🎧 Listen to verify quality
3. 📤 Export to MP3 for distribution
4. 🎬 Use for video production or standalone audio

## Full Documentation

See [ENHANCEMENT_GUIDE.md](ENHANCEMENT_GUIDE.md) for:
- Detailed technical specifications
- Sound effect algorithms
- Mixing strategy
- Verification checklist
- Advanced troubleshooting

---

**Need help?** Check [ENHANCEMENT_GUIDE.md](ENHANCEMENT_GUIDE.md) or review script comments.
