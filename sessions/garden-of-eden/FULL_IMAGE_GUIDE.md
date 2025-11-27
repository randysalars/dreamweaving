# Complete Image Sequence for Garden of Eden Video

## Overview

You'll need **7 images** total - one for each section of the meditation. Each image will fade in at the start of its section and remain visible throughout, blending with the chakra color gradients.

## File Naming Convention

Save images exactly as shown below in the `sessions/garden-of-eden/` directory:

```
eden_01_pretalk.png      # 0:00-2:30 (2.5 min)
eden_02_induction.png    # 2:30-8:00 (5.5 min)
eden_03_meadow.png       # 8:00-13:30 (5.5 min)
eden_04_serpent.png      # 13:30-17:00 (3.5 min)
eden_05_tree.png         # 17:00-20:00 (3 min)
eden_06_divine.png       # 20:00-23:00 (3 min)
eden_07_return.png       # 23:00-25:00 (2 min)
```

---

## Image 1: Pre-talk (0:00-2:30)
**Filename:** `eden_01_pretalk.png`
**Duration:** 2.5 minutes
**Chakra Color:** Warm gold

### Prompt:
```
mystical garden entrance archway made of living emerald vines and golden flowers,
warm golden sunlight streaming through, paradise garden beyond the archway,
ethereal sacred atmosphere, glowing light particles floating in air,
soft golden hour lighting, highly detailed botanical elements,
spiritual art, peaceful and inviting, sense of crossing a threshold,
photorealistic, 8k, cinematic lighting
```

### Negative prompt:
```
people, faces, text, watermark, dark, scary, dead plants, winter, modern objects
```

### Key elements: Garden entrance/gateway, warm inviting, gold tones

---

## Image 2: Induction (2:30-8:00)
**Filename:** `eden_02_induction.png`
**Duration:** 5.5 minutes
**Chakra Colors:** Gold → Green transition

### Prompt:
```
serene forest path descending into lush paradise garden,
dappled golden-green light filtering through leaves,
ancient trees with luminous emerald foliage,
peaceful atmosphere of deep relaxation and going deeper,
soft focus, dreamlike quality, spiritual journey inward,
photorealistic, 8k, warm and cool tones blending
```

### Negative prompt:
```
people, faces, text, watermark, dark, threatening, cliffs, danger
```

### Key elements: Descending path, gold-green transition, going deeper

---

## Image 3: Meadow (8:00-13:30)
**Filename:** `eden_03_meadow.png`
**Duration:** 5.5 minutes
**Chakra Color:** Emerald green (heart chakra)

### Prompt:
```
vast pristine paradise meadow with emerald grass and wildflowers,
surrounded by lush green trees, crystal clear stream flowing through,
perfect peaceful tranquility, healing heart energy,
soft natural lighting, sense of belonging and oneness with nature,
photorealistic, highly detailed, 8k, vibrant emerald and jade tones,
spiritual sanctuary
```

### Negative prompt:
```
people, faces, text, watermark, dead grass, barren, dark, threatening
```

### Key elements: Open meadow, emerald green, heart-centered peace

---

## Image 4: Serpent/River (13:30-17:00)
**Filename:** `eden_04_serpent.png`
**Duration:** 3.5 minutes
**Chakra Colors:** Green → Blue transition

### Prompt:
```
mystical serpentine river of liquid blue light flowing through eden,
water reflecting sky blue and turquoise tones, gentle current,
river banks with lush green vegetation, sense of transformation,
fluid movement and change, spiritual awakening energy,
ethereal glow from water, photorealistic, 8k,
green to blue gradient natural lighting, throat chakra energy
```

### Negative prompt:
```
people, faces, snakes, text, watermark, dark, murky water, dangerous
```

### Key elements: Flowing blue water, green-blue transition, transformation

---

## Image 5: Tree of Life (17:00-20:00)
**Filename:** `eden_05_tree.png`
**Duration:** 3 minutes
**Chakra Colors:** All 7 chakras (Red→Orange→Yellow→Green→Blue→Indigo→Violet)

### Prompt:
```
magnificent ancient Tree of Life in center of paradise garden,
rainbow energy flowing through trunk and branches,
seven glowing chakra orbs embedded in tree from roots to crown,
red at base through violet at top, mystical rainbow light emanating,
spiritual power and wisdom, cosmic connection,
photorealistic, highly detailed, 8k, ethereal rainbow glow,
sacred geometry in branches, divine presence
```

### Negative prompt:
```
people, faces, text, watermark, dead tree, dark, threatening, concrete
```

### Key elements: Central tree, rainbow/all colors, chakra energy, sacred

---

## Image 6: Divine Union (20:00-23:00)
**Filename:** `eden_06_divine.png`
**Duration:** 3 minutes
**Chakra Colors:** Violet → White (crown chakra opening)

### Prompt:
```
ethereal white-violet light streaming from heaven into paradise garden,
divine presence and cosmic consciousness, crown chakra opening,
brilliant white light with violet edges, sacred spiritual atmosphere,
sense of unity with the divine, transcendent peace,
photorealistic, 8k, soft focus, heavenly lighting,
angelic quality, highest spiritual awakening
```

### Negative prompt:
```
people, faces, religious symbols, text, watermark, dark, scary
```

### Key elements: Divine light, violet-white, heavenly, transcendent

---

## Image 7: Return Journey (23:00-25:00)
**Filename:** `eden_07_return.png`
**Duration:** 2 minutes
**Chakra Color:** White → Soft gold

### Prompt:
```
peaceful path leading back from paradise garden toward light,
golden sunset glow ahead, sense of gentle awakening and return,
carrying wisdom and peace back with you, soft golden hour lighting,
feeling of completion and gratitude, warm comforting atmosphere,
photorealistic, 8k, cinematic lighting, peaceful resolution,
bridge between worlds, soft bokeh background
```

### Negative prompt:
```
people, faces, text, watermark, dark, sad, ominous, abandoned
```

### Key elements: Return path, golden light ahead, peaceful completion

---

## Image Specifications

**All images must be:**
- Resolution: 1920x1080 (1080p landscape)
- Format: PNG
- Aspect ratio: 16:9
- Style: Photorealistic with spiritual/ethereal quality
- Lighting: Match chakra color for each section

---

## Generation Instructions

### Using HuggingFace Stable Diffusion (FREE):

1. Go to: https://huggingface.co/spaces/stabilityai/stable-diffusion
2. For each image:
   - Copy the prompt
   - Set negative prompt
   - Select "Photorealistic" or "Cinematic" style
   - Set aspect ratio to 16:9
   - Generate 2-3 variations
   - Download best result
3. Save with exact filename shown above

### Alternative: Free Stock Photos

Search these sites with the key elements listed:
- https://pixabay.com (CC0)
- https://unsplash.com (free license)
- https://pexels.com (CC0)

Look for landscape 16:9 images, download highest resolution.

---

## After Getting Images

Once you have all 7 images saved in the directory:

```bash
cd sessions/garden-of-eden
./create_final_video.sh
```

The script will automatically:
- Detect all images
- Place each at the correct time
- Add fade transitions (2-second fade in/out)
- Blend with chakra color gradients
- Compile final video with audio

---

## Minimum Setup

If you want to start with fewer images, you can do a minimal setup:

**Minimum 3 images:**
1. `eden_01_pretalk.png` - Opening (sets the tone)
2. `eden_03_meadow.png` - Middle (main meditation space)
3. `eden_07_return.png` - Closing (gentle return)

The script will work with any combination of images you provide.

---

## Tips for Best Results

1. **Consistent style:** Use the same AI model/settings for all images
2. **Avoid text/watermarks:** These distract from meditation
3. **No people/faces:** Keeps focus on inner journey
4. **Soft, dreamy quality:** Slight blur/bokeh works well
5. **Match color tones:** Each image should complement its chakra color
6. **High resolution:** 1920x1080 minimum, 4K if available

---

## Timing Reference

| Time | Section | Image | Chakra Color |
|------|---------|-------|--------------|
| 0:00-2:30 | Pre-talk | eden_01_pretalk.png | Warm gold |
| 2:30-8:00 | Induction | eden_02_induction.png | Gold→Green |
| 8:00-13:30 | Meadow | eden_03_meadow.png | Emerald green |
| 13:30-17:00 | Serpent | eden_04_serpent.png | Green→Blue |
| 17:00-20:00 | Tree | eden_05_tree.png | Rainbow (all 7) |
| 20:00-23:00 | Divine | eden_06_divine.png | Violet→White |
| 23:00-25:00 | Return | eden_07_return.png | White→Gold |
