# Garden of Eden Video Production

**VERSION:** 1.0 (Session-Specific)
**LAST UPDATED:** 2025-11-28
**SESSION:** Garden of Eden
**STATUS:** ✅ Current and Valid

> **📖 For universal workflow:** See [../../docs/CANONICAL_WORKFLOW.md](../../docs/CANONICAL_WORKFLOW.md)

---

Quick guide to creating your 25-minute meditation video using 100% free tools.

## Quick Start

```bash
# 1. Generate or download stills from prompts
#    - Use sessions/garden-of-eden/images/prompts.md
#    - Save PNGs to sessions/garden-of-eden/images/uploaded/

# 2. Generate background video (30-60 min)
python3 generate_video_background.py

# 3. Compile frames to video (5-15 min)
python3 compile_video.py video_frames output/video/background_gradient.mp4

# 4. Create final video with audio (2-5 min)
./create_final_video.sh

# 5. Create thumbnail
./create_thumbnail.sh

# 6. Prepare YouTube package
#    - Video: output/video/garden_of_eden_FINAL.mp4
#    - Thumbnail: output/video/thumbnail_final.jpg
#    - Description/Tags: YOUTUBE_DESCRIPTION.md (and youtube-description.md)
#    - Copy/paste checklist from AUDIO_PRODUCTION_README.md

# One-command build (audio+video) then package
python3 scripts/core/build_session.py \
  --session sessions/garden-of-eden \
  --ssml sessions/garden-of-eden/script.ssml \
  --voice en-US-Neural2-D \
  --title "Garden of Eden" --subtitle "Guided Meditation"
./scripts/core/package_youtube.sh sessions/garden-of-eden
```

## Optional: Add Custom Garden Images

1. Open the prompts at `sessions/garden-of-eden/images/prompts.md`
2. Generate each image (any SD/DALL·E-like tool) and save PNGs as:
   `01_pretalk.png, 02_induction.png, 03_meadow.png, 04_serpent.png, 05_tree.png, 06_divine.png, 07_return.png`
   into `sessions/garden-of-eden/images/uploaded/`
3. Run `./create_final_video.sh` (the script auto-detects these files with fades)

## Files You'll Get

- `output/video/background_gradient.mp4` - Chakra gradient background
- `output/video/garden_of_eden_FINAL.mp4` - Complete video with audio ⭐
- `output/video/thumbnail_final.jpg` - YouTube thumbnail
- `YOUTUBE_DESCRIPTION.md` (and youtube-description.md) - Description/tags for upload

## What's Included

✅ 25-minute chakra color progression synced to your meditation script
✅ Warm gold (pre-talk) → Green (induction) → All 7 chakras (tree section) → Violet/white (divine) → Gold (return)
✅ Subtle breathing animation effect
✅ Professional titles with fade in/out
✅ Your natural hypnotic voice with ultimate binaural beats
✅ YouTube-ready thumbnail with text overlays

## Total Time

- **First production:** 1-2 hours (mostly frame generation)
- **Subsequent videos:** 30-60 minutes (reuse template)

## Troubleshooting

**Q: Frame generation is slow**
A: This is normal! 45,000 frames takes time. Let it run in the background.

**Q: FFmpeg not found**
A: Install with: `sudo apt install ffmpeg`

**Q: Want to skip image generation?**
A: The video works great with just the chakra gradients!

**Q: Want higher quality?**
A: In `compile_video.py`, change `-crf 18` to `-crf 15` (larger file)

## Next Steps

1. Review video: `vlc output/video/garden_of_eden_FINAL.mp4`
2. Check thumbnail: `eog output/video/thumbnail_final.jpg`
3. Upload to YouTube
4. Use description from: `YOUTUBE_DESCRIPTION.md`

## Full Documentation

See `VIDEO_PRODUCTION_PLAN.md` for complete details, alternatives, and advanced options.
