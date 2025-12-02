---
name: full-build
description: Complete pipeline from manifest to YouTube package
arguments:
  - name: session
    required: true
    description: Session name or path
agents:
  - dreamweaver
  - manifest-architect
  - script-writer
  - visual-artist
  - audio-engineer
  - video-producer
  - quality-control
---

# /full-build Command

Run the complete production pipeline from topic to YouTube-ready package.

## Usage
```
/full-build <session>
```

## Example
```
/full-build inner-child-healing
```

## Complete Pipeline

### Stage 1: Configuration
1. Validate/generate manifest
2. Apply lessons from knowledge base
3. Confirm settings

### Stage 2: Content Generation
4. Generate SSML script (if missing)
5. Validate SSML
6. Generate Midjourney prompts

### Stage 3: User Action (Pause)
7. **USER**: Create images on Midjourney
8. **USER**: Upload to `images/uploaded/`
9. **USER**: Resume build

### Stage 4: Audio Production
10. **Generate voice audio (CANONICAL METHOD)**
    ```bash
    python3 scripts/core/generate_voice.py \
        sessions/{session}/working_files/script.ssml \
        sessions/{session}/output
    ```
    - Uses production voice: `en-US-Neural2-H` (bright female)
    - Automatically applies enhancement (warmth, room, layers)
    - Output: `voice_enhanced.mp3` (USE THIS for mixing)

11. Generate binaural bed (match to voice_enhanced.mp3 duration)
12. Mix stems (use voice_enhanced.mp3, NOT voice.mp3)
13. Master audio

### Stage 5: Video Production
15. Generate VTT subtitles
16. Assemble video
17. Generate YouTube package

### Stage 6: Quality Control
18. Validate all outputs
19. Generate quality report
20. Package complete

## Progress Tracking

The build uses TODO list to track progress:

```
[✓] Generate manifest
[✓] Generate script
[✓] Generate Midjourney prompts
[ ] Wait for user images
[ ] Build audio
[ ] Build video
[ ] Package for YouTube
```

## Outputs

```
sessions/{session}/
├── manifest.yaml
├── working_files/script.ssml
├── midjourney-prompts.md
├── images/uploaded/
│   └── [user images]
└── output/
    ├── voice.mp3              # Raw TTS (backup)
    ├── voice_enhanced.mp3     # Enhanced voice (USE THIS)
    ├── voice_enhanced.wav     # High-quality enhanced
    ├── binaural.wav
    ├── mixed.mp3
    ├── final.mp3
    ├── subtitles.vtt
    ├── video/
    │   └── final.mp4
    └── youtube_package/
        ├── {session}_FINAL.mp4
        ├── thumbnail.jpg
        ├── subtitles.vtt
        ├── description.txt
        ├── tags.txt
        └── upload_guide.md
```

## Time Estimate

| Stage | Time |
|-------|------|
| Config + Script | ~5 min |
| Midjourney (user) | Variable |
| Audio Build | ~15 min |
| Video Build | ~5 min |
| **Total** | **~25 min + Midjourney** |

## Pause Points

The build will pause at:
1. **After prompts generated** - Wait for user to create images
2. **After video complete** - User review before packaging

## Resume Build

If paused, resume with:
```
/full-build <session> --resume
```

## Quality Gates

Build stops if:
- SSML validation fails
- Audio loudness out of range
- Critical errors in any stage

## Learning Integration

- Applies lessons from `knowledge/lessons_learned.yaml`
- After completion, prompts user for analytics feedback
- Enables continuous improvement
