# Stock Image Search Guide

**Session:** journey-to-the-land-of-endless-prosperit-20251205
**Style:** neural_network
**Total Scenes:** 5

## Quick Links

### Scene 1: pretalk

**Filename:** `scene_01_pretalk.png`
**Prompt:** Welcome and introduction to Journey to the Land of Endless Prosperity: Unlock your Abundance Mindset...
**Suggested search:** `peaceful entrance nature`

| Platform | Search Link |
|----------|-------------|
| Unsplash | [Search](https://unsplash.com/s/photos/peaceful%20entrance%20nature?orientation=landscape) |
| Pexels | [Search](https://www.pexels.com/search/peaceful%20entrance%20nature/?orientation=landscape) |
| Pixabay | [Search](https://pixabay.com/images/search/peaceful%20entrance%20nature/?orientation=horizontal&min_width=1920) |

### Scene 2: induction

**Filename:** `scene_02_induction.png`
**Prompt:** Relaxation and descent into on a sacred path that winds through realms of transformation, where each...
**Suggested search:** `calm water reflection`

| Platform | Search Link |
|----------|-------------|
| Unsplash | [Search](https://unsplash.com/s/photos/calm%20water%20reflection?orientation=landscape) |
| Pexels | [Search](https://www.pexels.com/search/calm%20water%20reflection/?orientation=landscape) |
| Pixabay | [Search](https://pixabay.com/images/search/calm%20water%20reflection/?orientation=horizontal&min_width=1920) |

### Scene 3: journey

**Filename:** `scene_03_journey.png`
**Prompt:** Main journey: a sacred journey through cosmic realms toward abundance, immersive and visionary mood,...
**Suggested search:** `mystical landscape`

| Platform | Search Link |
|----------|-------------|
| Unsplash | [Search](https://unsplash.com/s/photos/mystical%20landscape?orientation=landscape) |
| Pexels | [Search](https://www.pexels.com/search/mystical%20landscape/?orientation=landscape) |
| Pixabay | [Search](https://pixabay.com/images/search/mystical%20landscape/?orientation=horizontal&min_width=1920) |

### Scene 4: integration

**Filename:** `scene_04_integration.png`
**Prompt:** Integration: opening fully to receive the universe's infinite gifts, peaceful and resolving mood, so...
**Suggested search:** `ascending light`

| Platform | Search Link |
|----------|-------------|
| Unsplash | [Search](https://unsplash.com/s/photos/ascending%20light?orientation=landscape) |
| Pexels | [Search](https://www.pexels.com/search/ascending%20light/?orientation=landscape) |
| Pixabay | [Search](https://pixabay.com/images/search/ascending%20light/?orientation=horizontal&min_width=1920) |

### Scene 5: awakening

**Filename:** `scene_05_awakening.png`
**Prompt:** Gentle return to full waking awareness, refreshed and grounded mood, clear morning light, grounded s...
**Suggested search:** `morning light peaceful`

| Platform | Search Link |
|----------|-------------|
| Unsplash | [Search](https://unsplash.com/s/photos/morning%20light%20peaceful?orientation=landscape) |
| Pexels | [Search](https://www.pexels.com/search/morning%20light%20peaceful/?orientation=landscape) |
| Pixabay | [Search](https://pixabay.com/images/search/morning%20light%20peaceful/?orientation=horizontal&min_width=1920) |

---

## Checklist Per Image

- [ ] No recognizable faces
- [ ] No brand logos or text
- [ ] Landscape orientation (16:9)
- [ ] High resolution (1920x1080+)
- [ ] Mood matches scene purpose

## After Download

1. Save original to `images/stock_cache/`
2. Process with FFmpeg:
   ```bash
   ffmpeg -i input.jpg -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" images/uploaded/scene_XX.png
   ```
3. Add entry to `images/license_manifest.yaml`
4. Run: `python3 scripts/utilities/validate_image_licenses.py /home/rsalars/Projects/dreamweaving/sessions/journey-to-the-land-of-endless-prosperit-20251205/`