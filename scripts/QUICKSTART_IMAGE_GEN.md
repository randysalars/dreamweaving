# Image Generation Quick Start

**One-page reference for automated image generation**

---

## Setup (First Time Only)

```bash
cd /home/rsalars/Projects/dreamweaving
./scripts/core/setup_image_generation.sh
```

**First run downloads:** SDXL model (~13 GB, one-time, cached locally)

---

## Generate Images

### Quick Commands

```bash
# Basic (normal quality, 3 candidates per image)
python3 scripts/core/generate_images_sd.py

# Fast test (draft quality, 1 candidate)
python3 scripts/core/generate_images_sd.py --quality draft --candidates 1

# Best quality (slow, 3 candidates)
python3 scripts/core/generate_images_sd.py --quality high

# Custom session
python3 scripts/core/generate_images_sd.py --session-dir sessions/my-session
```

---

## Options Reference

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--quality` | draft, normal, high | normal | Generation quality (26/32/40 steps) |
| `--candidates` | 1-10 | 3 | Number of variations per image |
| `--session-dir` | path | sessions/garden-of-eden | Output directory |

---

## Quality vs Speed

| Quality | Steps | Time (GPU) | Time (CPU) | Use Case |
|---------|-------|------------|------------|----------|
| draft | 30 | 20-30s | 3-5 min | Testing prompts |
| normal | 50 | 40-60s | 5-8 min | Production (recommended) |
| high | 80 | 80-120s | 8-12 min | Final/hero images |

---

## Output Files

```
sessions/garden-of-eden/
├── eden_01_pretalk.png              ← Main image
├── eden_01_pretalk_candidate2.png   ← Alternative
├── eden_01_pretalk_candidate3.png   ← Alternative
├── eden_01_pretalk_metadata.json    ← Generation params
└── ...
```

**After generation:** Review candidates, keep best, delete others.

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **GPU** | NVIDIA 8 GB VRAM | NVIDIA 10+ GB VRAM |
| **RAM** | 16 GB | 32 GB |
| **Storage** | 15 GB free | 20 GB free |
| **Time/image** | 30-60s (GPU) | 20-40s (GPU) |

**No GPU?** Works on CPU (5-10 min per image) or Apple Silicon M1/M2/M3 (40-80s)

---

## Troubleshooting

### Out of Memory
- Reduce resolution: Edit script, change `width=1280, height=720`
- Use fewer candidates: `--candidates 1`
- Close other GPU applications

### Slow Generation
- Use draft quality: `--quality draft`
- Generate 1 candidate: `--candidates 1`
- Install xformers: `pip install xformers`

### Bad Results
- Increase quality: `--quality high`
- Generate more options: `--candidates 5`
- Check prompt in metadata JSON file
- Try different seed

---

## Custom Images (Programmatic)

```python
#!/usr/bin/env python3
import sys
sys.path.append('scripts/core')
from generate_images_sd import ImageGenerator

generator = ImageGenerator()

generator.generate_and_save(
    prompt="your custom prompt, 8k uhd, highly detailed, masterpiece",
    output_path="sessions/my-session/my_image.png",
    width=1920,
    height=1080,
    num_inference_steps=50,
    guidance_scale=7.5,
    seed=42,  # Optional, for reproducibility
    num_candidates=3
)
```

---

## Integration with Video Pipeline

Images are automatically used by [create_final_video.sh](../sessions/garden-of-eden/create_final_video.sh)

**Required images for Garden of Eden:**
1. eden_01_pretalk.png
2. eden_02_induction.png
3. eden_03_meadow.png
4. eden_04_serpent.png
5. eden_05_tree.png
6. eden_06_divine.png
7. eden_07_return.png

---

## Next Steps

1. **Setup:** `./scripts/core/setup_image_generation.sh`
2. **Test:** `python3 scripts/core/generate_images_sd.py --quality draft --candidates 1`
3. **Generate:** `python3 scripts/core/generate_images_sd.py`
4. **Review:** Check images, keep best candidates
5. **Video:** Run `./sessions/garden-of-eden/create_final_video.sh`

---

**Full Guide:** [IMAGE_GENERATION_GUIDE.md](IMAGE_GENERATION_GUIDE.md)

**100% Free & Open Source** | No API costs | Unlimited generation
