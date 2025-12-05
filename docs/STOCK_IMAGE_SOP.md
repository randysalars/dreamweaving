# Stock Image Standard Operating Procedure

> Quick reference for sourcing, vetting, and documenting stock images for dreamweaving sessions.

## Quick Start Checklist

```
□ Search on approved platform (Unsplash/Pexels/Pixabay)
□ Verify: No faces, no logos, no text
□ Download highest resolution
□ Process to 1920x1080 PNG
□ Add entry to license_manifest.yaml
□ Run validation script
```

---

## 1. Approved Platforms

| Platform | URL | Commercial | Notes |
|----------|-----|------------|-------|
| **Unsplash** | https://unsplash.com | ✅ YES | Best for nature/landscapes |
| **Pexels** | https://www.pexels.com | ✅ YES | NO wallpaper apps |
| **Pixabay** | https://pixabay.com | ✅ YES | NO standalone sales |
| **Openverse** | https://openverse.org | ✅ Filter for commercial | CC0/CC BY only |

### NEVER Use

- **CC BY-NC** content (non-commercial)
- **Getty/iStock/Shutterstock** without paid license
- **Pinterest/Google Images** without source verification

---

## 2. Search Strategy

### Pre-Built Search URLs

Copy these and replace `[QUERY]`:

```
Unsplash:
https://unsplash.com/s/photos/[QUERY]?orientation=landscape

Pexels:
https://www.pexels.com/search/[QUERY]/?orientation=landscape

Pixabay:
https://pixabay.com/images/search/[QUERY]/?orientation=horizontal&min_width=1920

Openverse (commercial only):
https://openverse.org/search/image?q=[QUERY]&license_type=commercial
```

### Theme-Specific Queries

| Session Theme | Search Terms |
|---------------|--------------|
| **Eden/Garden** | "enchanted forest mist", "garden path sunlight", "paradise nature" |
| **Cosmic/Space** | "nebula abstract", "galaxy stars", "cosmic dust purple" |
| **Atlantean** | "underwater temple", "ancient ruins underwater", "submerged city" |
| **Temple/Ancient** | "stone doorway mist", "ancient corridor torch", "temple entrance" |
| **Desert/Steppe** | "desert sunset", "steppe landscape", "horseman silhouette" |
| **Sacred Geometry** | "mandala abstract", "golden spiral", "sacred pattern light" |
| **Healing/Calm** | "calm lake sunset", "peaceful meadow", "soft morning light" |

---

## 3. Image Vetting Checklist

Before downloading, verify:

### MUST Check

- [ ] **No recognizable faces** - Silhouettes OK, clear faces NOT OK
- [ ] **No brand logos** - Nike swoosh, Apple logo, etc.
- [ ] **No text overlays** - Signs, watermarks, typography
- [ ] **No religious symbols** - Unless generic sacred geometry
- [ ] **Resolution ≥ 1920x1080** - Or can be upscaled

### SHOULD Check

- [ ] **Mood matches session** - Calm for meditation, dramatic for journey
- [ ] **Color palette fits** - Warm for healing, cool for cosmic
- [ ] **No busy/cluttered scenes** - Simple compositions work best
- [ ] **No high contrast/jarring** - Soft transitions, gentle colors

---

## 4. Download & Processing

### Step 1: Download Original

1. Click **Download** on the image page
2. Select **Original** or **Large** size
3. Save to: `sessions/{session}/images/stock_cache/`
4. Rename: `{platform}_{photo-id}.jpg`

Example:
```
unsplash_abc123xyz.jpg
pexels_12345678.jpg
pixabay_987654.jpg
```

### Step 2: Process to Production Format

Run this FFmpeg command:

```bash
ffmpeg -i images/stock_cache/unsplash_abc123.jpg \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \
    images/uploaded/scene_01_pretalk.png
```

This will:
- Scale to fit within 1920x1080
- Add black bars if aspect ratio differs
- Output as PNG for video pipeline

### Optional: WebP for App Distribution

```bash
ffmpeg -i images/uploaded/scene_01_pretalk.png \
    -c:v libwebp -quality 85 \
    images/uploaded/scene_01_pretalk.webp
```

---

## 5. License Documentation

### Add Entry to Manifest

Edit `sessions/{session}/images/license_manifest.yaml`:

```yaml
images:
  - filename: "scene_01_pretalk.png"
    source:
      platform: "unsplash"
      url: "https://unsplash.com/photos/abc123xyz"
      photo_id: "abc123xyz"
      photographer: "Jane Smith"
      photographer_url: "https://unsplash.com/@janesmith"
    license:
      type: "unsplash"
      commercial_use: true
      attribution_required: false
      retrieved_date: "2025-12-04"
    content:
      has_people: false
      has_logos: false
      theme: "misty forest path with morning light"
    original:
      filename: "unsplash_abc123xyz.jpg"
      dimensions: "4000x2667"
```

### Required Fields

| Field | Required | Description |
|-------|----------|-------------|
| `filename` | YES | Final processed filename |
| `source.platform` | YES | unsplash, pexels, pixabay, openverse |
| `source.url` | YES | Direct link to image page |
| `license.type` | YES | License identifier |
| `license.commercial_use` | YES | Must be `true` |
| `license.retrieved_date` | YES | YYYY-MM-DD format |
| `content.has_people` | YES | Boolean |
| `content.has_logos` | YES | Boolean |

---

## 6. Validation

### Run Validation Script

```bash
# Single session
python3 scripts/utilities/validate_image_licenses.py sessions/{session}/

# All sessions
python3 scripts/utilities/validate_image_licenses.py --all

# Strict mode (fails on people/logos)
python3 scripts/utilities/validate_image_licenses.py sessions/{session}/ --strict
```

### Expected Output

```
============================================================
Session: eden-garden-pathworking
============================================================
✓ All license checks passed
```

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `UNTRACKED: scene_01.png has no license record` | Missing manifest entry | Add entry to license_manifest.yaml |
| `PROHIBITED: uses non-commercial license` | CC BY-NC image | Replace with commercial-licensed image |
| `ATTRIBUTION REQUIRED` | CC BY images without credits | Add attribution_credits block |

---

## 7. CC BY Attribution

If using CC BY licensed images (Openverse/Flickr), add attribution:

```yaml
attribution_credits: |
  Images used under Creative Commons licenses:
  - "Forest Path" by Jane Smith (CC BY 4.0): https://flickr.com/janesmith/12345
  - "Mountain Vista" by John Doe (CC BY 4.0): https://flickr.com/johndoe/67890
```

Include this credit in:
- App settings/credits screen
- YouTube video description
- Any published materials

---

## 8. File Naming Convention

### Scene Images

```
scene_{NN}_{section}.png
```

Examples:
- `scene_01_pretalk.png`
- `scene_02_induction.png`
- `scene_03_journey_outer.png`
- `scene_04_journey_inner.png`
- `scene_05_helm.png`
- `scene_06_integration.png`
- `scene_07_awakening.png`

### Stock Cache

```
{platform}_{photo_id}.{ext}
```

Examples:
- `unsplash_abc123xyz.jpg`
- `pexels_12345678.jpg`
- `pixabay_987654.png`

---

## 9. Decision Matrix: Stock vs AI

| Need | Use Stock | Use AI (SD/MJ) |
|------|-----------|----------------|
| Realistic nature | ✅ YES | Maybe |
| Generic meditation bg | ✅ YES | Either |
| Abstract cosmic | Either | ✅ YES |
| Mythological scene | NO | ✅ YES |
| Branded/consistent style | NO | ✅ YES |
| Legal certainty | ✅ YES | Uncertain |
| Fast prototype | ✅ YES | Slower |

---

## 10. Quick Reference Card

### Safe Platforms
- ✅ Unsplash, Pexels, Pixabay, CC0, CC BY

### Never Use
- ❌ CC BY-NC, Pinterest, Google Images without source

### Checklist Per Image (~12 min total)
1. Search (5 min)
2. Verify no faces/logos (2 min)
3. Download original (1 min)
4. Process to 1920x1080 (2 min)
5. Document in manifest (2 min)

### FFmpeg One-Liner
```bash
ffmpeg -i input.jpg -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" output.png
```

### Validation
```bash
python3 scripts/utilities/validate_image_licenses.py sessions/{session}/
```

---

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Main project reference
- [CANONICAL_WORKFLOW.md](CANONICAL_WORKFLOW.md) - Production workflow
- [generate_scene_images.py](../scripts/core/generate_scene_images.py) - AI image generation
