# Dreamweaving Production Workflow Stages

**VERSION:** 1.0
**LAST UPDATED:** 2025-12-02
**STATUS:** ✅ CANONICAL USER WORKFLOW

This documents the actual production workflow as practiced, with clear stages and checkpoints.

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: CREATIVE DESIGN                                               │
│  ├── Brainstorm journey ideas from topic                                │
│  ├── Select archetypes, binaural frequencies, hypnotic sounds           │
│  └── Generate SSML script for chosen concept                            │
├─────────────────────────────────────────────────────────────────────────┤
│  STAGE 2: VOICE SCRIPT                                        ✓ CHECK  │
│  ├── Create voice-ready SSML (strip SFX markers)                        │
│  └── User reviews for suitability                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  STAGE 3: AUDIO GENERATION                                    ✓ CHECK  │
│  ├── Generate binaural beats track                                      │
│  ├── Generate sound effects track                                       │
│  └── User reviews audio elements                                        │
├─────────────────────────────────────────────────────────────────────────┤
│  STAGE 4: AUDIO MIXING                                        ✓ CHECK  │
│  ├── Mix voice + binaural + SFX                                         │
│  └── User reviews mix balance                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  STAGE 5: HYPNOTIC POST-PROCESSING                            ✓ CHECK  │
│  ├── Apply psychoacoustic enhancements                                  │
│  ├── Master for broadcast (-14 LUFS)                                    │
│  └── User reviews final audio                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  STAGE 5.5: VIDEO IMAGES                                     (AUTO)    │
│  ├── Generate title card, section slides, chapter markers              │
│  ├── Generate outro, lower thirds, social preview                       │
│  └── python3 scripts/core/generate_video_images.py session/ --all      │
├─────────────────────────────────────────────────────────────────────────┤
│  STAGE 6: VIDEO PRODUCTION                                    ✓ CHECK  │
│  ├── Use generated video images for assembly                            │
│  ├── Assemble video with audio                                          │
│  └── User reviews final video                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  STAGE 7: YOUTUBE PACKAGING                                   ✓ CHECK  │
│  ├── Generate title, description, tags, chapters                        │
│  ├── Generate thumbnail                                                 │
│  ├── Create VTT subtitles                                               │
│  └── User uploads to YouTube                                            │
├─────────────────────────────────────────────────────────────────────────┤
│  STAGE 8: CLEANUP                                                       │
│  ├── Archive working files                                              │
│  ├── Remove temporary files                                             │
│  └── Update session status                                              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Stage Breakdown

### STAGE 1: CREATIVE DESIGN
**Purpose:** Transform a topic into a complete hypnotic journey concept

**Inputs:**
- Topic or theme from user

**Process:**
1. Brainstorm 3-5 journey ideas around the topic
2. For each idea, suggest:
   - Core archetypes (Guide, Healer, Guardian, etc.)
   - Binaural beat frequencies (alpha/theta/delta progression)
   - Hypnotic sound elements (bells, nature, pads, etc.)
   - Emotional arc and transformation
3. User selects preferred concept
4. Generate complete SSML script with:
   - All sections (pre-talk, induction, journey, integration, closing)
   - SFX markers for sound design
   - Proper prosody and break timing

**Outputs:**
- `manifest.yaml` - Session configuration
- `working_files/script_production.ssml` - Full script with SFX markers
- `notes.md` - Design rationale and archetypes

**Slash Command:** `/brainstorm <topic>` or `/new-session <name>`

---

### STAGE 2: VOICE SCRIPT
**Purpose:** Prepare script for TTS generation

**Inputs:**
- `script_production.ssml`

**Process:**
1. Strip all `[SFX: ...]` markers
2. Validate SSML syntax
3. Check NLP patterns and hypnotic language
4. Present to user for review

**Outputs:**
- `working_files/script_voice_clean.ssml` - TTS-ready script

**User Checkpoint:** ✓ Review script for suitability before voice generation

**Slash Command:** `/generate-script <session>`

---

### STAGE 3: AUDIO GENERATION
**Purpose:** Create all audio stems

**Inputs:**
- `script_voice_clean.ssml`
- `manifest.yaml` (for binaural settings)
- SFX markers from `script_production.ssml`

**Process:**
1. Generate voice using Google Cloud TTS
   - Voice: en-US-Neural2-H (production standard)
   - Apply voice enhancement (warmth, room, layers)
2. Generate binaural beats track
   - Follow frequency progression from manifest
   - Carrier frequency, beat transitions
3. Generate SFX track
   - Time effects to script markers
   - Apply appropriate reverb/decay

**Outputs:**
- `output/voice.mp3` - Raw TTS
- `output/voice_enhanced.mp3` - Enhanced voice (USE THIS)
- `output/binaural_dynamic.wav` - Binaural track
- `output/sfx_track.wav` - Sound effects track

**User Checkpoint:** ✓ Review binaural and SFX elements

**Slash Command:** `/build-audio <session>` (partial - voice only currently)

---

### STAGE 4: AUDIO MIXING
**Purpose:** Combine all audio stems into cohesive mix

**Inputs:**
- `voice_enhanced.mp3` (or .wav)
- `binaural_dynamic.wav`
- `sfx_track.wav`

**Process:**
1. Set stem levels:
   - Voice: -6 dB
   - Binaural: -6 dB
   - SFX: 0 dB
2. Mix with amix filter (normalize=0)
3. Verify no clipping

**Outputs:**
- `output/session_mixed.wav` - Combined mix

**User Checkpoint:** ✓ Review mix balance

**Command:**
```bash
ffmpeg -y \
  -i voice_enhanced.wav -i binaural_dynamic.wav -i sfx_track.wav \
  -filter_complex "[0:a]volume=-6dB[v];[1:a]volume=-6dB[b];[2:a]volume=0dB[s];[v][b][s]amix=inputs=3:duration=longest:normalize=0" \
  session_mixed.wav
```

---

### STAGE 5: HYPNOTIC POST-PROCESSING
**Purpose:** Apply psychoacoustic mastering for hypnotic effect

**Inputs:**
- `session_mixed.wav`

**Process:**
1. Apply loudnorm to -14 LUFS (YouTube standard)
2. True peak limiting to -1.5 dBTP
3. Optional enhancements:
   - Subtle low-frequency warmth
   - Gentle high-frequency roll-off
   - Stereo widening for immersion

**Outputs:**
- `output/final_master.mp3` - Production-ready audio
- `output/final_master.wav` - Lossless version

**User Checkpoint:** ✓ Review final mastered audio

---

### STAGE 5.5: VIDEO IMAGES (AUTOMATIC)
**Purpose:** Generate all supporting video imagery

**Inputs:**
- `manifest.yaml` (for sections, title, theme)
- `images/uploaded/` (optional base images)

**Process:**
1. Run video image generator:
   ```bash
   python3 scripts/core/generate_video_images.py sessions/{session}/ --all
   ```
2. Selects palette based on visual_style or theme

**Outputs:**
- `output/video_images/title_card.png` - Video intro (1920×1080)
- `output/video_images/sections/section_*.png` - Chapter transitions
- `output/video_images/outro.png` - End screen with CTA zones
- `output/video_images/lower_thirds/*.png` - Transparent overlays
- `output/video_images/chapters/chapter_*.png` - Chapter markers
- `output/video_images/social_preview.png` - Square format (1080×1080)
- `output/video_images/backgrounds/scene_*.png` - Plain backgrounds

**Available Palettes:**
- `sacred_light` - Gold/cream (default)
- `cosmic_journey` - Purple/blue
- `garden_eden` - Emerald/gold
- `ancient_temple` - Antique gold
- `neural_network` - Cyan/purple
- `volcanic_forge` - Red-gold
- `celestial_blue` - Royal blue

**No user checkpoint required** - automatic generation from manifest data

---

### STAGE 6: VIDEO PRODUCTION
**Purpose:** Create visual component for YouTube

**Inputs:**
- `final_master.mp3`
- `output/video_images/` - Generated video images
- Session theme/archetypes
- `manifest.yaml`

**Process:**
1. Generate Midjourney prompts for key scenes
   - Or use AI image generation
2. User creates/provides images in `images/uploaded/`
3. Assemble video:
   - Use generated title_card.png for intro
   - Use section slides for chapter transitions
   - Ken Burns effects on scene images
   - Fade transitions
   - Sync to audio duration
   - Use outro.png for end screen
4. Generate VTT subtitles

**Outputs:**
- `midjourney-prompts.md` - Image generation prompts
- `images/uploaded/` - Final images
- `output/final_video.mp4` - Complete video
- `output/subtitles.vtt` - Timed captions

**User Checkpoint:** ✓ Review final video

**Slash Command:** `/build-video <session>`

---

### STAGE 7: YOUTUBE PACKAGING
**Purpose:** Prepare complete upload package

**Inputs:**
- `final_video.mp4`
- `manifest.yaml`
- Session content

**Process:**
1. Generate optimized title (CTR-focused)
2. Write description with:
   - Hook paragraph
   - Benefits
   - Disclaimers
   - Timestamps/chapters
3. Generate relevant tags
4. Create thumbnail:
   - High contrast
   - Mobile-readable text
   - Curiosity-inducing

**Outputs:**
- `output/youtube_package/`
  - `video.mp4`
  - `thumbnail.png`
  - `subtitles.vtt`
  - `metadata.yaml` (title, description, tags)

**User Checkpoint:** ✓ Upload to YouTube

**Slash Command:** `/full-build <session>` (includes this stage)

---

### STAGE 8: CLEANUP
**Purpose:** Archive and clean session

**Inputs:**
- All working files

**Process:**
1. Archive working files if needed
2. Remove temporary/intermediate files
3. Update manifest status to "published"
4. Log completion in session notes

**Outputs:**
- Clean session directory
- Updated `manifest.yaml` with status

---

## Stage Reference Table

| Stage | Name | Key Output | Checkpoint |
|-------|------|------------|------------|
| 1 | Creative Design | `script_production.ssml` | - |
| 2 | Voice Script | `script_voice_clean.ssml` | ✓ User review |
| 3 | Audio Generation | `voice_enhanced.mp3`, binaural, SFX | ✓ User review |
| 4 | Audio Mixing | `session_mixed.wav` | ✓ User review |
| 5 | Post-Processing | `final_master.mp3` | ✓ User review |
| 5.5 | **Video Images** | `output/video_images/` | - (automatic) |
| 6 | Video Production | `final_video.mp4` | ✓ User review |
| 7 | YouTube Packaging | `youtube_package/` | ✓ User uploads |
| 8 | Cleanup | Clean directory | - |

---

## Current Stage Tracking

When working on a session, Claude should:
1. Identify which stage we're in
2. State it clearly: "We are in **STAGE X: [NAME]**"
3. Complete that stage before moving on
4. Wait for user checkpoint before proceeding

Example:
> "We are in **STAGE 4: AUDIO MIXING**. I've mixed the stems. Please review the mix balance before we proceed to post-processing."

---

## File Location Quick Reference

| Stage | Key Files |
|-------|-----------|
| 1 | `manifest.yaml`, `working_files/script_production.ssml` |
| 2 | `working_files/script_voice_clean.ssml` |
| 3 | `output/voice_enhanced.mp3`, `output/binaural_dynamic.wav`, `output/sfx_track.wav` |
| 4 | `output/session_mixed.wav` |
| 5 | `output/final_master.mp3` |
| 5.5 | `output/video_images/*` (title_card, sections/, chapters/, outro, social_preview, lower_thirds/, backgrounds/) |
| 6 | `output/final_video.mp4`, `images/uploaded/` |
| 7 | `output/youtube_package/*` |
| 8 | - |
