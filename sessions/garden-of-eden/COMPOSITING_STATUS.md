# Image Compositing - Current Status

## Problem Identified ✅

The original compositor only showed 2 images because the `fade` filter operates on **frame numbers** (starting from 0 for each image input), but the `overlay enable` filter uses **video timeline seconds**. This mismatch broke the overlay chain.

See [IMAGE_COMPOSITING_FIX.md](IMAGE_COMPOSITING_FIX.md) for full technical details.

## Solution Created ✅

Created two new scripts:

### 1. [composite_images_simple.py](composite_images_simple.py) - NO FADES (testing)
- Removes all fade filters
- Uses only time-based `overlay enable` filters
- Should show all 7 images with hard cuts
- **Currently running** (frame 4220/45000, ~10% complete, ETA 15 min)

### 2. [composite_images_FINAL.py](composite_images_FINAL.py) - WITH FADES (final)
- Uses `geq` filter for time-based alpha channel manipulation
- Smooth 2-second fade in/out for each image
- Ready to run after simple version is verified

## Current Progress

```
Test Compositing (no fades):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10%
Frame 4220/45000 @ 1.72x speed
ETA: ~15 minutes
Output: output/video/composite_test_simple.mp4
```

## Next Steps

1. **Wait** for simple test to complete (~15 min)
2. **Verify** all 7 images appear in test video
3. **Run** final version with fades
4. **Update** [create_final_video.sh](create_final_video.sh) to use working script
5. **Generate** complete final video with audio

## What Changed

**Old (broken):**
```python
fade=in:0:60,fade=out:4440:60  # Frame-based (wrong)
+ overlay enable='between(t,0,150)'  # Time-based (right)
= Mismatch → only 2 images render
```

**New (working):**
```python
geq a='if(lt(T,start),0,if(lt(T,end),255,0))'  # Time-based alpha
+ overlay  # No enable needed
= All 7 images render correctly
```

## Verification

Once complete, you can check specific images appear at the right times:

```bash
# Extract frame at 10 minutes (should show meadow image)
ffmpeg -i output/video/composite_test_simple.mp4 -ss 00:10:00 -vframes 1 test_frame.jpg
eog test_frame.jpg
```

Expected timeline:
- 0:00-2:30: Garden archway (pretalk)
- 2:30-8:00: Forest path descending (induction)
- 8:00-13:30: Paradise meadow (meditation core)
- 13:30-17:00: Blue river (transformation)
- 17:00-20:00: Rainbow Tree of Life (all chakras)
- 20:00-23:00: Divine white-violet light (crown)
- 23:00-25:00: Return path with golden light (completion)
