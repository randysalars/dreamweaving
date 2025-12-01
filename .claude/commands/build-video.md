---
name: build-video
description: Build video for a session (requires audio to exist)
arguments:
  - name: session
    required: true
    description: Session name or path
agent: video-producer
---

# /build-video Command

Build video from audio and images, generate VTT subtitles.

## Usage
```
/build-video <session>
```

## Example
```
/build-video inner-child-healing
```

## Prerequisites

- Audio must already be built (`output/final.mp3` exists)
- Images should be in `images/uploaded/` (or will use background)

## Process

1. **Pre-flight checks**
   - Verify audio exists
   - Check for images
   - Validate manifest

2. **Generate VTT subtitles**
   - Parse SSML for text
   - Calculate timing
   - Scale to audio duration
   - Save to `output/subtitles.vtt`

3. **Assemble video**
   ```bash
   python3 scripts/core/assemble_session_video.py \
       --session sessions/{session} \
       --audio sessions/{session}/output/final.mp3 \
       --background auto
   ```

4. **Apply transitions**
   - Fade between images
   - Time to manifest sections
   - Add title/subtitle overlay

5. **Generate YouTube package**
   ```bash
   python3 scripts/core/package_youtube.py sessions/{session}
   ```

6. **Save outputs**
   - `output/video/final.mp4`
   - `output/youtube_package/` with all assets

## Output Package

```
output/youtube_package/
├── {session}_FINAL.mp4      # Final video
├── thumbnail.jpg            # YouTube thumbnail
├── subtitles.vtt           # Closed captions
├── description.txt         # Video description
├── tags.txt               # Comma-separated tags
└── upload_guide.md        # Upload instructions
```

## Image Handling

### If Images Exist
- Map images to manifest sections
- Apply fade transitions
- Time to section boundaries

### If No Images
- Use solid color background
- Or specified background image
- Still generate complete video

## VTT Generation

VTT subtitles are:
- Parsed from SSML script
- Timed based on speech rate + breaks
- Scaled to actual audio duration
- Merged for readability

## Video Specs

- Resolution: 1920x1080
- Frame Rate: 30 fps
- Codec: H.264
- Audio: AAC 320kbps

## Troubleshooting

### No Audio
- Run `/build-audio` first

### Wrong Duration
- Verify audio file
- Check SSML parsing

### Missing Images
- Will fallback to background
- Add images to `images/uploaded/`
