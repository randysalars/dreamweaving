# Garden of Eden - Audio Production Guide

Complete guide for generating the final audio with voice, binaural beats, and optional nature sounds.

---

## Quick Start (Automated)

### Option 1: Complete Automated Workflow

Run everything with one command:

```bash
# First time: Install dependencies
pip install numpy scipy pydub

# Generate complete audio (voice + binaural beats)
./create_complete_audio.sh en-US-Neural2-D
```

This will create:
- `output/voice_only.mp3` - Voice track
- `output/binaural_track.wav` - Binaural beats
- `output/garden_of_eden_complete.mp3` - **FINAL MIX** (ready for upload!)

---

## Manual Step-by-Step Process

### Step 1: Generate Voice Audio

```bash
python ../../../scripts/core/generate_audio_chunked.py \
    script.ssml \
    output/voice_only.mp3 \
    en-US-Neural2-D
```

**Voice options:**
- `en-US-Neural2-D` - Deep resonant male (recommended)
- `en-US-Neural2-I` - Warm compassionate male
- `en-US-Neural2-J` - Rich mature male

**Output:** `output/voice_only.mp3` (~25-27 minutes)

---

### Step 2: Generate Binaural Beats

#### Option A: Full Multi-Section Track (Recommended)

```bash
python generate_binaural_beats.py
# Choose option 1 when prompted
```

This creates a sophisticated track with:
- Pre-talk: Silence
- Induction: 12→6 Hz ramp (Alpha to Theta)
- Meadow: 6 Hz + 396 Hz (shame release)
- Serpent: 7.5 Hz + 528 Hz (transformation)
- Tree of Life: 7.83 Hz + 639 Hz (heart chakra)
- Divine: 8 Hz + 963 Hz (crown chakra)
- Return: 8→12 Hz ramp (Theta to Alpha)
- Anchors: 10 Hz + 432 Hz (grounding)

**Output:** `binaural_track.wav` (~27 minutes)

#### Option B: Simple Single-Frequency Track (Easier)

```bash
python generate_binaural_beats.py simple
```

This creates a constant 7.83 Hz (Schumann Resonance) with 432 Hz carrier throughout.

**Output:** `simple_theta_track.wav` (~27 minutes)

---

### Step 3: Mix Voice and Binaural

```bash
python mix_audio.py \
    output/voice_only.mp3 \
    binaural_track.wav \
    output/garden_of_eden_complete.mp3
```

**Output:** `output/garden_of_eden_complete.mp3` (FINAL - ready for YouTube!)

---

## Optional: Add Nature Sounds

If you have a nature soundscape file (forest, rain, creek):

```bash
python mix_audio.py \
    output/voice_only.mp3 \
    binaural_track.wav \
    output/garden_of_eden_base.mp3 \
    path/to/forest_sounds.mp3
```

**Output:**
- `output/garden_of_eden_base.mp3` (voice + binaural)
- `output/garden_of_eden_base_with_nature.mp3` (voice + binaural + nature)

**Recommended nature sounds:**
- Gentle flowing stream/creek
- Soft forest ambience
- Light wind through trees
- Distant bird songs
- **Volume:** Very subtle (automatically set to 15% of voice)

---

## Files Overview

### Generated Files

```
sessions/garden-of-eden/
├── script.ssml                           # Input: SSML script
├── generate_binaural_beats.py            # Script to create binaural beats
├── mix_audio.py                          # Script to mix audio tracks
├── create_complete_audio.sh              # Automated workflow
└── output/
    ├── voice_only.mp3                    # Voice track (no binaural)
    ├── binaural_track.wav                # Binaural beats only
    └── garden_of_eden_complete.mp3       # FINAL MIX (upload this!)
```

---

## Audio Specifications

### Final Output (garden_of_eden_complete.mp3)

- **Format:** MP3
- **Bitrate:** 320 kbps (highest quality)
- **Sample Rate:** 48 kHz
- **Channels:** Stereo (required for binaural effect)
- **Duration:** ~25-27 minutes
- **File Size:** ~45-55 MB

### Volume Mixing Ratios

- **Voice:** 100% (reference, -3dB peak)
- **Binaural Beats:** 30% of voice (-10dB)
- **Nature Sounds:** 15% of voice (-25dB) *if used*

**Critical:** Voice must always be clearly dominant!

---

## Testing Your Final Audio

Before uploading, verify:

### ✅ Technical Tests
- [ ] File plays without errors
- [ ] Duration is correct (~25-27 min)
- [ ] No clipping or distortion
- [ ] Smooth transitions between sections
- [ ] Proper stereo field (binaural effect)

### 🎧 Headphone Tests
- [ ] Voice is clear and dominant
- [ ] Binaural beats are subtle but present
- [ ] No jarring frequency transitions
- [ ] Comfortable listening volume
- [ ] Creates relaxed/trance feeling

### 🔊 Speaker Tests
- [ ] Still pleasant without binaural effect
- [ ] Voice remains clear
- [ ] Not too much bass/low frequency
- [ ] Works on phone/tablet/computer speakers

---

## Troubleshooting

### "Binaural beats are too loud"

Adjust volume in `mix_audio.py`:
```python
mix_tracks(voice_file, binaural_file, output_file,
           voice_volume=0,
           binaural_volume=-15)  # Changed from -10 to -15
```

### "Binaural beats are too quiet"

```python
mix_tracks(voice_file, binaural_file, output_file,
           voice_volume=0,
           binaural_volume=-5)  # Changed from -10 to -5
```

### "Voice audio generation failed"

Check:
1. Virtual environment is activated: `source venv/bin/activate`
2. Google Cloud credentials: `gcloud auth application-default login`
3. SSML syntax is valid: `python ../../../scripts/utilities/validate_ssml.py script.ssml`

### "Import errors for numpy/scipy"

```bash
pip install numpy scipy pydub
```

For pydub on Linux, also need ffmpeg:
```bash
sudo apt install ffmpeg
```

### "Binaural track doesn't match voice duration"

The `mix_audio.py` script automatically handles this by:
- Extending binaural with silence if too short
- Trimming binaural if too long

If issues persist, manually check durations and adjust in `generate_binaural_beats.py`.

---

## Creating Alternative Versions

### Version A: Voice Only (No Binaural)

Use `output/voice_only.mp3` directly.

**Good for:**
- Users who don't like binaural beats
- Accessibility
- Epilepsy-safe version

### Version B: Simple Theta (Less Complex)

```bash
python generate_binaural_beats.py simple
python mix_audio.py output/voice_only.mp3 simple_theta_track.wav output/simple_version.mp3
```

**Good for:**
- Easier production
- More conservative approach
- First-time binaural users

### Version C: With Nature Sounds

Follow the optional nature sounds workflow above.

**Good for:**
- Enhanced immersion
- Users who enjoy ambient sound
- Outdoor/nature-themed sessions

---

## YouTube Upload Checklist

Before uploading `garden_of_eden_complete.mp3`:

- [ ] File tested with headphones ✅
- [ ] File tested with speakers ✅
- [ ] Duration confirmed (~25-27 min) ✅
- [ ] No audio errors/clipping ✅
- [ ] Title decided (see youtube-description.md)
- [ ] Description written (see youtube-description.md)
- [ ] Thumbnail created
- [ ] Binaural warning added to description
- [ ] Tags/keywords added
- [ ] Timestamps added to description

**Important YouTube Settings:**
- **Category:** Education or People & Blogs
- **License:** Standard YouTube License
- **Comments:** Enabled (moderated)
- **Age Restriction:** No (but include disclaimer)

---

## Advanced: Frequency Customization

To modify frequencies, edit `generate_binaural_beats.py`:

### Change Theta Frequency
```python
# Line ~85: Meadow section
meadow = generate_binaural_beat(396, 6, 5.0 * 60)
#                                    ^ Change this (6 Hz)
```

### Change Solfeggio Carrier
```python
# Line ~85: Meadow section
meadow = generate_binaural_beat(396, 6, 5.0 * 60)
#                               ^^^ Change this (396 Hz)
```

### Adjust Section Durations
```python
# Line ~85: Meadow section
meadow = generate_binaural_beat(396, 6, 5.0 * 60)
#                                       ^^^ Change duration (5 min)
```

**Common Solfeggio Frequencies:**
- 174 Hz - Foundation, security
- 285 Hz - Healing, regeneration
- 396 Hz - Liberation from fear/guilt
- 417 Hz - Facilitating change
- 528 Hz - Transformation, DNA repair
- 639 Hz - Relationships, connection
- 741 Hz - Expression, solutions
- 852 Hz - Intuition, spiritual order
- 963 Hz - Divine consciousness, pineal activation

**Common Theta Frequencies:**
- 4 Hz - Deep meditation, creativity
- 5 Hz - Unusual problem solving
- 6 Hz - Deep relaxation, hypnosis
- 7 Hz - Meditation, mental imagery
- 7.83 Hz - Schumann Resonance (Earth)
- 8 Hz - Past life recall, shamanic states

---

## Dependencies

```bash
# Python packages
pip install numpy scipy pydub

# System dependencies (Linux)
sudo apt install ffmpeg

# System dependencies (Mac)
brew install ffmpeg
```

---

## Production Timeline

### First Time Setup (20 min)
1. Install dependencies: 5 min
2. Test voice generation: 10 min
3. Test binaural generation: 5 min

### Each Production Run (30-45 min)
1. Generate voice: 15-20 min
2. Generate binaural: 2-3 min
3. Mix tracks: 2-3 min
4. Test playback: 10-15 min

### Using Automated Script (20-30 min)
1. Run `./create_complete_audio.sh`: 18-22 min
2. Test playback: 10-15 min

---

## Tips for Best Results

### Audio Quality
✅ Always use 48kHz sample rate
✅ Export at 320kbps MP3 for YouTube
✅ Keep voice at -3dB peak maximum
✅ Test on multiple devices before uploading

### Binaural Effectiveness
✅ Ensure smooth frequency transitions
✅ Keep binaural subtle (30% or less)
✅ Use headphones for generation/testing
✅ Start conservative with frequency choices

### Production Workflow
✅ Generate voice first (it takes longest)
✅ Generate binaural while reviewing voice
✅ Mix and test before committing
✅ Keep raw files for re-mixing if needed

---

## Support & Resources

### Official Documentation
- Audio Enhancement Guide: `audio-enhancement-guide.md`
- YouTube Description: `youtube-description.md`
- Session Notes: `notes.md`

### External Resources
- Binaural beats research: Search "theta waves hypnosis studies"
- Solfeggio frequencies: Search "solfeggio healing frequencies"
- Audio mixing tutorials: YouTube "mixing voice and music"

---

*For questions or issues, refer to the troubleshooting section or the main project documentation.*

**🌿 Walk in innocence. Choose with wisdom. Live in wholeness. 🌿**
