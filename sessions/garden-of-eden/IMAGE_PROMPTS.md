# Image Generation Prompts for Garden of Eden Video

## Quick Instructions

1. Go to: https://huggingface.co/spaces/stabilityai/stable-diffusion
2. Copy each prompt below
3. Generate images (try 2-3 variations of each)
4. Download the best results
5. Save them with the exact filenames shown below

---

## Opening Image (Pre-talk: 0:00-2:30)

**Filename:** `eden_opening.png`

**Prompt:**
```
mystical garden archway made of living emerald vines and golden flowers,
warm sunlight streaming through, paradise garden beyond,
ethereal sacred atmosphere, glowing light particles,
soft golden hour lighting, highly detailed botanical elements,
spiritual art, peaceful and inviting, 8k, photorealistic
```

**Negative prompt:**
```
people, faces, text, watermark, dark, scary, dead plants, winter
```

**Settings:**
- Style: Photorealistic or Cinematic
- Aspect ratio: 16:9 (landscape)

**What to look for:** Warm, inviting, golden-green tones, mystical but peaceful

---

## Closing Image (Return: 23:00-25:00)

**Filename:** `eden_closing.png`

**Prompt:**
```
serene pathway leading out of paradise garden at golden hour sunset,
warm gentle sunlight, feeling of peaceful completion and gratitude,
soft bokeh background, ethereal glow, spiritual awakening,
photorealistic, highly detailed, 8k, cinematic lighting,
sense of fulfillment and inner peace
```

**Negative prompt:**
```
people, faces, text, watermark, dark, ominous, sad
```

**Settings:**
- Style: Photorealistic or Cinematic
- Aspect ratio: 16:9 (landscape)

**What to look for:** Warm, peaceful, sense of gentle return to waking consciousness

---

## Alternative: Simpler Prompts

If the above prompts don't work well, try these simpler versions:

### Opening (simpler):
```
beautiful garden entrance with vines and flowers,
golden sunlight, peaceful paradise, photorealistic
```

### Closing (simpler):
```
sunset garden path, warm light, peaceful and serene, photorealistic
```

---

## After Generating Images

Save the images in this directory as:
- `eden_opening.png` - Will appear at 30-40 seconds (fade in/out)
- `eden_closing.png` - Will appear at 23:00-23:30 (fade in/out)

Then run: `./create_final_video.sh` to regenerate the video with images included.

---

## Backup Option: Free Stock Images

If Stable Diffusion is unavailable, search these sites for "garden archway sunset" or "paradise garden":
- https://pixabay.com (CC0 - no attribution needed)
- https://unsplash.com (free for commercial use)
- https://pexels.com (CC0 - no attribution needed)

Look for 1920x1080 or higher resolution landscape images.
