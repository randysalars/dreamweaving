# Neural Network Navigator - Production Workflow

**VERSION:** 2.0 (Session-Specific)
**LAST UPDATED:** 2025-11-30
**SESSION DURATION:** V1: 23:41 (1421s) | V2: 28:43 (1723s)
**STATUS:** ✅ Current and Valid - See [DURATION_NOTES.md](DURATION_NOTES.md)

> **📖 For universal workflow:** See [../../docs/CANONICAL_WORKFLOW.md](../../docs/CANONICAL_WORKFLOW.md)
> This document covers **session-specific** enhancements only.

---

## Complete Production Pipeline

This session uses the **ultimate audio mix** workflow for professional quality output.

### Quick Start

```bash
# 1. Generate/fix voice (if needed)
python3 generate_voice_v2_ava.py

# 2. Create ultimate audio mix
./create_ultimate_audio.sh

# 3. Create final video
python3 create_final_v2_ava.py
```

## Phase 1: Voice Generation

**Files**:
- Input: `working_files/voice_script_enhanced_v2.ssml`
- Output: `working_files/neural_navigator_v2_ava.wav`

**SSML Validation**:
Always validate SSML before generating voice to avoid text being read aloud:
```bash
python3 ../../scripts/utilities/validate_ssml.py \
  working_files/voice_script_enhanced_v2.ssml
```

**Common SSML Issues**:
- ❌ `<emphasis level="moderate">` - NOT supported by Edge TTS
- ✅ `<emphasis level="strong">` - Supported
- ✅ `<emphasis level="reduced">` - Supported

**Generate Voice**:
```bash
python3 generate_voice_v2_ava.py
```
- Voice: en-US-AvaNeural (warm, professional)
- Duration: ~23:32 (varies by script)
- Output: 8.1 MB MP3 or WAV

**Apply Mastering**:
```bash
ffmpeg -i working_files/neural_navigator_v2_ava.wav \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11,\
       equalizer=f=250:t=h:width=200:g=1.5,\
       equalizer=f=3000:t=h:width=2000:g=1.0,\
       highshelf=f=10000:g=-0.5,\
       alimiter=limit=0.9:attack=5:release=50" \
  -c:a pcm_s24le -ar 48000 -y \
  working_files/neural_navigator_v2_ava_MASTERED_FIXED_NEW.wav
```
- Target: -14 LUFS (YouTube broadcast standard)
- Professional EQ and dynamic range control

## Phase 2: Ultimate Audio Mix

**CRITICAL**: Always use the ultimate mix for final video (not simple voice+binaural).

**What It Creates**:
A comprehensive 9-layer soundscape:
1. Mastered voice (corrected SSML)
2. Dynamic binaural beats (Alpha 10Hz → Theta 5Hz → Gamma 40Hz → Alpha 10Hz)
3. Pink noise ambient pad (from cached asset library, instant generation)
4. Singing bowls at anchor moments (5 strategic placements)
5. Crystal bells at transitions (3 key moments)
6. Wind chime at awakening
7. Gamma burst noise during peak focus
8-9. Additional atmospheric layers

**Run Script**:
```bash
./create_ultimate_audio.sh
```

**Output**:
- `working_files/neural_navigator_ULTIMATE_MIX.wav`
- Duration: 23:41 (1421 seconds)
- Size: ~389 MB (24-bit 48kHz stereo WAV)

**Benefits**:
- ✅ Pink noise cached and trimmed instantly (vs 5+ minutes generation)
- ✅ Professional mix levels across all layers
- ✅ Sound effects timed to script sections
- ✅ Immersive soundscape for deep experience

## Phase 3: Final Video

**Prerequisites**:
- Ultimate mix exists: `working_files/neural_navigator_ULTIMATE_MIX.wav`
- Images exist: `images/scene_*.png` (8 scenes)

**Create Video**:
```bash
python3 create_final_v2_ava.py
```

**Create YouTube Thumbnail**:
```bash
python3 create_youtube_thumbnail.py
```

**What It Does**:
- Combines ultimate audio mix with 8 scene images
- Creates 1920x1080 @ 30fps video
- H.264 encoding (YouTube optimized)
- AAC audio at 256kbps
- Faststart flag for web streaming

**Output**:
- `final_export/neural_network_navigator_v2_ava_FINAL.mp4` - Final video
- `final_export/neural_network_navigator_THUMBNAIL.jpg` - YouTube thumbnail
- Duration: 23:41
- Video size: ~97 MB
- Thumbnail: 1280x720, ~122 KB

**Scene Timings**:
1. Opening/Pretalk: 0:00 - 2:30
2. Induction: 2:30 - 5:00
3. Neural Garden: 5:00 - 10:00
4. Pathfinder: 10:00 - 15:00
5. Weaver: 15:00 - 19:20
6. Gamma Burst: 19:20 - 20:55
7. Consolidation: 20:55 - 23:20
8. Awakening/Closing: 23:20 - 23:41

## Audio Asset Library

This session uses the project-wide asset library for efficient production.

**Cached Assets Used**:
- `pink_noise_24min.wav` (261 MB) - Trimmed to 23:41 instantly
- `singing_bowl.wav` - 8 seconds, placed at anchor moments
- `crystal_bell.wav` - 2 seconds, placed at transitions
- `wind_chime.wav` - 3 seconds, placed at awakening

**Performance**:
- Pink noise generation: 5+ minutes → <1 second (300x faster)
- Consistent quality across all sessions
- Reusable sound design elements

## File Structure

```
sessions/neural-network-navigator/
├── working_files/
│   ├── voice_script_enhanced_v2.ssml           # Source script
│   ├── neural_navigator_v2_ava.wav             # Raw voice
│   ├── neural_navigator_v2_ava_MASTERED_FIXED_NEW.wav  # Mastered voice
│   ├── neural_navigator_ULTIMATE_MIX.wav       # Final audio ★
│   └── temp_audio/                             # Build artifacts (cleaned up)
├── sound_effects/
│   ├── singing_bowl.wav
│   ├── crystal_bell.wav
│   └── wind_chime.wav
├── images/
│   ├── scene_01_opening_FINAL.png
│   ├── scene_02_descent_FINAL.png
│   └── ... (6 more scenes)
├── create_ultimate_audio.sh                    # Audio production
├── create_final_v2_ava.py                      # Video production
├── generate_voice_v2_ava.py                    # Voice generation
└── final_export/
    └── neural_network_navigator_v2_ava_FINAL.mp4  # Final deliverable
```

## Quality Checklist

Before final export:

- [ ] SSML validated (no invalid tags)
- [ ] Voice generated successfully
- [ ] Audio mastered to -14 LUFS
- [ ] Ultimate mix created (389 MB WAV file)
- [ ] All 8 scene images present
- [ ] Video duration matches audio (23:41)
- [ ] Final video tested (plays correctly with all audio layers)

## Fixes Applied in This Session

### SSML Reading Aloud (Fixed)
**Problem**: Voice was reading "emphasis on" around 21:50

**Root Cause**: Invalid `<emphasis level="moderate">` tags (Edge TTS doesn't support "moderate")

**Fix**: Changed to `<emphasis level="strong">` in lines 266 and 272

**Files Changed**:
- `working_files/voice_script_enhanced_v2.ssml`

### Ultimate Mix Implementation
**Problem**: Video was using simple 2-layer mix (voice + binaural)

**Enhancement**: Implemented 9-layer ultimate mix with full soundscape

**Files Changed**:
- `create_final_v2_ava.py` - Now uses `neural_navigator_ULTIMATE_MIX.wav`
- Updated duration from 24:29 to 23:41

## Production Time

**Total**: ~15-20 minutes (with asset caching)

- Voice generation: 2-3 minutes
- Audio mastering: 30 seconds
- Ultimate mix: 8-10 minutes (pink noise cached)
- Video encoding: 5-7 minutes

**First time** (without cached pink noise): ~25-30 minutes

## Troubleshooting

### Voice Reads SSML Tags
- Run SSML validator before generating
- Fix invalid tag attributes
- Regenerate voice

### Pink Noise Takes Forever
- Check asset library: `assets/audio/ambient/pink_noise_24min.wav`
- If missing, first generation takes ~5 minutes
- Subsequent uses are instant (trimming)

### Video Has Wrong Audio
- Verify `create_final_v2_ava.py` uses `ULTIMATE_MIX.wav`
- Not the old `v2_ava_complete_mix.wav`
- Check line 219 of the script

### Mix Sounds Unbalanced
- Voice should be clear and primary (-14 LUFS)
- Binaural subtle background (-28 LUFS)
- Ambient pad deep background (-32 LUFS)
- Check `create_ultimate_audio.sh` volume settings

## Future Sessions

This workflow is now standardized. For new sessions:

1. Copy `create_ultimate_audio.sh` to new session directory
2. Update paths and session name variables
3. Follow the same 3-phase workflow
4. Leverage cached audio assets for speed

See [main workflow documentation](../../docs/AUDIO_VIDEO_WORKFLOW.md) for full details.
