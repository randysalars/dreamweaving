# Garden of Eden Video Production

Quick guide to creating your 25-minute meditation video using 100% free tools.

## Quick Start

```bash
# 1. Generate background video (30-60 min)
python3 generate_video_background.py

# 2. Compile frames to video (5-15 min)
python3 compile_video.py video_frames output/video/background_gradient.mp4

# 3. Create final video with audio (2-5 min)
./create_final_video.sh

# 4. Create thumbnail
./create_thumbnail.sh
```

## Optional: Add Custom Garden Images

To add beautiful opening imagery:

1. Go to https://huggingface.co/spaces/stabilityai/stable-diffusion
2. Use this prompt:
   ```
   mystical garden archway made of living emerald vines,
   golden sunlight streaming through, paradise garden beyond,
   ethereal sacred atmosphere, glowing light particles,
   cinematic lighting, highly detailed, spiritual art
   ```
3. Download best result and save as: `eden_opening.png`
4. Run `./create_final_video.sh` again

## Files You'll Get

- `output/video/background_gradient.mp4` - Chakra gradient background
- `output/video/garden_of_eden_FINAL.mp4` - Complete video with audio ⭐
- `output/video/thumbnail_final.jpg` - YouTube thumbnail

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
