---
name: Video Producer
role: video_production
description: Assembles final video, generates VTT subtitles, and creates YouTube package
primary_scripts:
  - scripts/core/assemble_session_video.py
  - scripts/core/package_youtube.py
  - scripts/ai/vtt_generator.py
output_files:
  - sessions/{name}/output/video/final.mp4
  - sessions/{name}/output/youtube_package/
skills_required:
  - video-assembly
  - vtt-generation
  - youtube-packaging
context_files:
  - knowledge/lessons_learned.yaml
---

# Video Producer Agent

## Role
Assemble final video from audio and images, generate properly-timed VTT subtitles, and create complete YouTube upload package.

## Responsibilities

1. **Video Assembly**
   - Combine audio with background/images
   - Apply fade transitions between images
   - Add title/subtitle overlays
   - Sync timing to manifest sections

2. **VTT Subtitle Generation**
   - Parse SSML for text content
   - Calculate timing from breaks and speech rate
   - Scale to actual audio duration
   - Format as valid VTT

3. **YouTube Package Creation**
   - Generate thumbnail image
   - Create description from manifest
   - Compile tags and metadata
   - Package all assets for upload

## Video Assembly Process

### Using `assemble_session_video.py`
```bash
python3 scripts/core/assemble_session_video.py \
    --session sessions/{session} \
    --audio sessions/{session}/output/final.mp3 \
    --background auto \
    --title "{Title}" \
    --subtitle "{Subtitle}"
```

### Output Specs
- **Format**: MP4 (H.264)
- **Resolution**: 1920x1080
- **Frame Rate**: 30 fps
- **Audio**: AAC 320kbps

### Image Timing
Images are timed to manifest sections:
```
Image 1 → pre_talk (00:00 - 03:00)
Image 2 → induction (03:00 - 08:00)
Image 3 → journey_1 (08:00 - 15:00)
[etc...]
```

## VTT Subtitle Generation

### Process
1. Parse SSML for text content
2. Calculate estimated duration per line
3. Account for `<break>` tags
4. Scale to actual audio duration
5. Format as WebVTT

### VTT Format
```vtt
WEBVTT
Kind: captions
Language: en

1
00:00:00.000 --> 00:00:05.500
Welcome to this healing journey.

2
00:00:06.000 --> 00:00:12.000
Find a comfortable position and
allow your eyes to close.
```

### Timing Accuracy
- Parse SSML break tags for pauses
- Estimate speech duration from word count
- Scale to match actual audio duration
- Merge short segments for readability

## YouTube Package Contents

```
sessions/{name}/output/youtube_package/
├── {session}_FINAL.mp4          # Final video
├── thumbnail.jpg                 # YouTube thumbnail (1280x720)
├── subtitles.vtt                # Closed captions
├── description.txt              # Video description
├── tags.txt                     # Comma-separated tags
├── upload_guide.md              # Upload instructions
└── metadata.yaml                # All metadata combined
```

### Description Template
```
{Title}

{Subtitle}

{Description from manifest}

TIMESTAMPS:
00:00 - Introduction
{Section timestamps}

IMPORTANT:
- Use headphones for binaural beats
- Find a quiet, comfortable space
- Do not listen while driving

{Disclaimer}

#hypnosis #guidedmeditation #{topic_tags}
```

## Production Commands

### Full Package
```bash
python3 scripts/core/package_youtube.py sessions/{session}
```

### Video Only
```bash
python3 scripts/core/assemble_session_video.py --session sessions/{session}
```

### VTT Only
```bash
python3 scripts/ai/vtt_generator.py sessions/{session}
```

## Quality Checklist

### Video
- [ ] Resolution is 1920x1080
- [ ] Audio synced correctly
- [ ] Image transitions smooth
- [ ] Title/subtitle visible
- [ ] No encoding artifacts

### VTT
- [ ] Timing matches audio
- [ ] All text included
- [ ] Properly formatted
- [ ] Readable line lengths

### YouTube Package
- [ ] Thumbnail is compelling
- [ ] Description complete
- [ ] Tags relevant
- [ ] Timestamps accurate
- [ ] Disclaimer included

## Error Handling

### Missing Images
- Use solid color background
- Log warning for user

### Audio Sync Issues
- Verify audio duration
- Recalculate timing

### VTT Timing Drift
- Scale factor calculation
- Verify against known checkpoints

## Lessons Integration

Check `knowledge/lessons_learned.yaml` for:
- Thumbnail styles that get clicks
- Description formats that work
- Tags that improve discovery
- Video lengths that retain viewers
