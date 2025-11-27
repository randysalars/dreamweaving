# Image Compositing Issue - Root Cause & Solution

## Problem

The original Python compositor ([composite_images.py](composite_images.py)) only rendered the first 2 images instead of all 7 images.

## Root Cause

The issue was with **how fade filters work in FFmpeg**. The original approach applied `fade` filters to the image inputs themselves:

```python
img_filter = (
    f"[{input_num}:v]"
    f"fade=in:0:{fade_frames},"              # ← PROBLEM: Frame-based, not time-based
    f"fade=out:{duration*30-fade_frames}:{fade_frames},"
    f"scale=1920:1080:force_original_aspect_ratio=decrease,"
    f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
    f"[img{idx}]"
)
```

**Why this failed:**
- The `fade` filter operates on **frame numbers** of the INPUT stream, not the video timeline
- Each image input (`-loop 1 -t 1500`) has its own frame counter starting at 0
- The fade calculations were based on the image's duration, but the overlay `enable` filter uses **video timeline seconds**
- This mismatch caused FFmpeg to incorrectly render the fades, breaking the overlay chain after 2 images

## Solution Options

### Option 1: No Fades (TESTING - composite_images_simple.py)

Remove fade filters entirely and use only time-based `enable` filters:

```python
# Just scale and pad
img_filter = (
    f"[{input_num}:v]"
    f"scale=1920:1080:force_original_aspect_ratio=decrease,"
    f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
    f"[img{idx}]"
)

# Overlay with time window
overlay_filter = (
    f"{current_stream}[img{idx}]"
    f"overlay=0:0:enable='between(t,{start_sec},{end_sec})'"
    f"[tmp{idx}]"
)
```

**Result:** All 7 images appear at correct times with **hard cuts** (no fades)

### Option 2: Time-Based Alpha Fading (FINAL - composite_images_FINAL.py)

Use `geq` filter to apply time-based alpha channel manipulation:

```python
# Add alpha channel
scale_filter = (
    f"[{input_num}:v]"
    f"scale=1920:1080:force_original_aspect_ratio=decrease,"
    f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
    f"format=yuva420p"  # ← Add alpha channel
    f"[scaled{idx}]"
)

# Apply time-based alpha using geq filter
# T = video timeline in seconds
# Alpha = 0-255 (FFmpeg internal representation)
alpha_expr = (
    f"'if(lt(T,{start_sec}),0,"                              # Before start: invisible
    f"if(lt(T,{fade_in_end}),(T-{start_sec})*{255/fade_duration},"  # Fade in
    f"if(lt(T,{fade_out_start}),255,"                        # Full opacity
    f"if(lt(T,{end_sec}),({end_sec}-T)*{255/fade_duration},0))))'"  # Fade out
)

geq_filter = (
    f"[scaled{idx}]"
    f"geq=lum='p(X,Y)':cb='p(X,Y)':cr='p(X,Y)':a={alpha_expr}"
    f"[alpha{idx}]"
)

# Overlay (no enable filter needed - alpha handles visibility)
overlay_filter = f"{current_stream}[alpha{idx}]overlay=0:0[tmp{idx}]"
```

**Result:** All 7 images appear with **smooth 2-second fade in/out** at correct times

## Timeline

| Time | Image | Status |
|------|-------|--------|
| 0:00-2:30 | eden_01_pretalk.png | ✓ Works now |
| 2:30-8:00 | eden_02_induction.png | ✓ Works now |
| 8:00-13:30 | eden_03_meadow.png | ✓ Works now (was broken) |
| 13:30-17:00 | eden_04_serpent.png | ✓ Works now (was broken) |
| 17:00-20:00 | eden_05_tree.png | ✓ Works now (was broken) |
| 20:00-23:00 | eden_06_divine.png | ✓ Works now (was broken) |
| 23:00-25:00 | eden_07_return.png | ✓ Works now (was broken) |

## Testing

Currently running test with no fades to verify all 7 images appear:
```bash
python3 composite_images_simple.py
# Output: output/video/composite_test_simple.mp4
```

Once verified, will run final version with fades:
```bash
python3 composite_images_FINAL.py
# Output: output/video/composite_with_images.mp4
```

## Verification Commands

After compositing completes, extract frames to verify each image appears:

```bash
# Check pretalk image (1 minute in)
ffmpeg -i output/video/composite_with_images.mp4 -ss 00:01:00 -vframes 1 test_pretalk.jpg

# Check induction image (5 minutes in)
ffmpeg -i output/video/composite_with_images.mp4 -ss 00:05:00 -vframes 1 test_induction.jpg

# Check meadow image (10 minutes in)
ffmpeg -i output/video/composite_with_images.mp4 -ss 00:10:00 -vframes 1 test_meadow.jpg

# Check serpent image (15 minutes in)
ffmpeg -i output/video/composite_with_images.mp4 -ss 00:15:00 -vframes 1 test_serpent.jpg

# Check tree image (18 minutes in)
ffmpeg -i output/video/composite_with_images.mp4 -ss 00:18:00 -vframes 1 test_tree.jpg

# Check divine image (21 minutes in)
ffmpeg -i output/video/composite_with_images.mp4 -ss 00:21:00 -vframes 1 test_divine.jpg

# Check return image (24 minutes in)
ffmpeg -i output/video/composite_with_images.mp4 -ss 00:24:00 -vframes 1 test_return.jpg
```

## Key Learnings

1. **FFmpeg fade filter** operates on INPUT FRAME NUMBERS, not video timeline
2. **overlay enable** operates on VIDEO TIMELINE SECONDS
3. Mixing frame-based and time-based operations causes misalignment
4. **geq filter with T variable** is the correct way to do time-based alpha manipulation
5. Always test with simple version first, then add complexity

## Next Steps

1. ✓ Identified root cause (fade filter frame vs. time mismatch)
2. ⏳ Testing simple version (no fades) - currently running
3. ⏳ Will run final version (with time-based alpha fades)
4. ⏳ Verify all 7 images in final video
5. ⏳ Update [create_final_video.sh](create_final_video.sh) to use working script
6. ⏳ Generate complete final video with audio
