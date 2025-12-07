# Automated Image Generation Guide

Complete guide for generating meditation images using Stable Diffusion XL.

---

## Quick Start

### 1. Install Dependencies

```bash
# Run the setup script
cd /home/rsalars/Projects/dreamweaving
chmod +x scripts/core/setup_image_generation.sh
./scripts/core/setup_image_generation.sh
```

**What this installs:**
- PyTorch (GPU or CPU version)
- Diffusers library (official Stable Diffusion implementation)
- Transformers, Accelerate, SafeTensors
- xformers (optional, for better GPU performance)

**First-time download:** On first run, the script will download the SDXL model (~13 GB). This happens once and the model is cached at `~/.cache/huggingface/hub/` for future use.

---

## 2. Generate Images

### Basic Usage

```bash
# Navigate to project root
cd /home/rsalars/Projects/dreamweaving

# Generate all Garden of Eden images (normal quality)
python3 scripts/core/generate_images_sd.py
```

### Quality Options

```bash
# Draft mode (26 steps, ~20-25 seconds per image)
# Good for testing prompts and checking framing
python3 scripts/core/generate_images_sd.py --quality draft --candidates 1

# Normal mode (32 steps, ~35-50 seconds per image)
# Recommended balance of quality and speed
python3 scripts/core/generate_images_sd.py --quality normal

# High quality (40 steps, ~60-90 seconds per image)
# Best results, takes longer
python3 scripts/core/generate_images_sd.py --quality high
```

### Candidate Selection

The script can generate multiple versions of each image:

```bash
# Generate 3 candidates per image (default)
python3 scripts/core/generate_images_sd.py --candidates 3

# Generate 5 candidates per image (more choice)
python3 scripts/core/generate_images_sd.py --candidates 5

# Generate only 1 image per prompt (faster)
python3 scripts/core/generate_images_sd.py --candidates 1
```

**Candidates are saved as:**
- `eden_01_pretalk.png` (main image)
- `eden_01_pretalk_candidate2.png`
- `eden_01_pretalk_candidate3.png`

Review and choose the best one, then delete the candidates.

---

## 3. Custom Sessions

### Generate for Different Session

```bash
python3 scripts/core/generate_images_sd.py \
  --session-dir sessions/my-new-session \
  --quality high \
  --candidates 3 \
  --max-gen-side 1152            # generate near SDXL native res, upscale to target

# Disable refiner if VRAM is tight
python3 scripts/core/generate_images_sd.py --no-refiner
```

### Programmatic Usage

```python
#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.append('scripts/core')
from generate_images_sd import ImageGenerator

# Initialize generator
generator = ImageGenerator()

# Generate single image
generator.generate_and_save(
    prompt="peaceful mountain lake at sunset, serene meditation scene, 8k uhd",
    output_path="sessions/my-session/my_image.png",
    width=1920,
    height=1080,
    num_inference_steps=50,
    guidance_scale=7.5,
    seed=42,  # For reproducibility
    num_candidates=3
)
```

---

## System Requirements

### Minimum (GPU)
- **GPU**: NVIDIA with 8 GB VRAM
- **RAM**: 16 GB
- **Storage**: 15 GB free (model cache)
- **Time**: 30-60 seconds per image

### Recommended (GPU)
- **GPU**: NVIDIA with 10+ GB VRAM (RTX 3080, RTX 4070, or better)
- **RAM**: 32 GB
- **Storage**: 20 GB free
- **Time**: 20-40 seconds per image

### CPU Only (Fallback)
- **RAM**: 32 GB minimum
- **Storage**: 15 GB free
- **Time**: 5-10 minutes per image
- **Note**: Works but very slow, only for testing

### Apple Silicon
- **Mac**: M1/M2/M3 with 16+ GB unified memory
- **Device**: Uses `mps` backend automatically
- **Time**: 40-80 seconds per image
- **Note**: Quality comparable to GPU, decent speed

---

## Output Structure

After generation, your session directory will contain:

```
sessions/garden-of-eden/
├── eden_01_pretalk.png              # Generated image
├── eden_01_pretalk_metadata.json    # Generation parameters
├── eden_01_pretalk_candidate2.png   # Alternative version
├── eden_01_pretalk_candidate3.png   # Alternative version
├── eden_02_induction.png
├── eden_02_induction_metadata.json
... (and so on)
```

### Metadata Files

Each image has a corresponding JSON file with generation parameters:

```json
{
  "prompt": "magnificent garden archway entrance...",
  "negative_prompt": "blurry, ugly, duplicate...",
  "width": 1920,
  "height": 1080,
  "steps": 50,
  "guidance_scale": 7.5,
  "seed": 42,
  "timestamp": "2025-11-25 14:30:00"
}
```

**Use metadata to:**
- Reproduce exact same image (using same seed)
- Tweak prompts for similar images
- Document generation parameters

---

## Performance Optimization

### Low VRAM (<8 GB)

If you get out-of-memory errors, the script automatically enables:

1. **Model CPU offloading** - Moves parts of model to RAM
2. **Attention slicing** - Processes attention in smaller chunks
3. **VAE slicing** - Processes VAE in smaller chunks

You can also reduce resolution:

```python
# Generate at 1280x720 instead of 1920x1080
generator.generate_and_save(
    prompt=prompt,
    output_path=output_path,
    width=1280,  # Smaller
    height=720,  # Smaller
    num_inference_steps=40  # Fewer steps = less memory
)
```

### Speed Optimization

Install xformers for 20-30% speed boost:

```bash
pip install xformers
```

The script will automatically use it if available.

### Batch Processing

To generate multiple sessions efficiently:

```python
sessions = [
    "sessions/garden-of-eden",
    "sessions/ocean-depths",
    "sessions/mountain-peak"
]

generator = ImageGenerator()  # Load model once

for session_dir in sessions:
    generate_images_for_session(generator, session_dir)
```

---

## Prompt Engineering Tips

### Structure of Good Prompts

```
[Main Subject] + [Details] + [Style] + [Quality]
```

**Example:**
```
magnificent garden archway,              # Main subject
ornate stone arch with roses,           # Details
fantasy landscape art,                   # Style
8k uhd, highly detailed, masterpiece    # Quality tags
```

### Quality Keywords (for SDXL)

Add these to improve results:
- `8k uhd`
- `highly detailed`
- `masterpiece`
- `professional photography`
- `cinematic lighting`
- `photorealistic`

### Negative Prompts

Default negative prompt works well:
```
blurry, ugly, duplicate, poorly drawn, deformed, text, watermark, low quality, distorted
```

Add specific things to avoid:
```
negative_prompt = "blurry, ugly, text, people, faces, animals, modern buildings"
```

### Guidance Scale

- **5-7**: More creative, varied results
- **7-9**: Balanced (recommended for SDXL)
- **9-15**: Strict adherence to prompt (may look overprocessed)

### Seeds for Reproducibility

Using seeds ensures you get the same image:

```python
# Generate image with seed
generator.generate_and_save(prompt="...", seed=42)

# Will produce identical image
generator.generate_and_save(prompt="...", seed=42)

# Different seed = different image
generator.generate_and_save(prompt="...", seed=123)
```

**Strategy:**
1. Generate with random seed (`seed=None`)
2. Note the seed from metadata if you like the result
3. Re-generate with same seed and modified prompt

---

## Troubleshooting

### Issue: Out of Memory Error

**Error:** `CUDA out of memory` or `RuntimeError: Out of memory`

**Solutions:**
1. Close other GPU applications
2. Reduce image resolution (1280x720)
3. Reduce batch size (use `--candidates 1`)
4. Script will auto-enable CPU offloading, but you can force it:

```python
generator = ImageGenerator(enable_optimizations=True)
# Optimizations are enabled by default
```

### Issue: Model Download Fails

**Error:** `Connection error` or `timeout`

**Solutions:**
1. Check internet connection
2. Try again (resume is automatic)
3. Manual download:

```bash
huggingface-cli download stabilityai/stable-diffusion-xl-base-1.0
```

### Issue: Slow Generation (CPU)

**Problem:** Taking 5-10 minutes per image

**Solutions:**
1. Use draft quality for testing: `--quality draft`
2. Generate fewer candidates: `--candidates 1`
3. Use smaller model (SD 1.5 instead of SDXL):

```python
generator = ImageGenerator(
    model_id="runwayml/stable-diffusion-v1-5"  # Faster, lower quality
)
```

### Issue: Images Look Wrong/Bad

**Problem:** Generated images don't match prompt

**Solutions:**
1. Increase guidance scale: `guidance_scale=9.0`
2. Increase steps: `--quality high`
3. Improve prompt with more details
4. Generate more candidates: `--candidates 5`
5. Try different seeds

### Issue: Text in Images

**Problem:** Unwanted text or watermarks

**Solution:**
Already included in negative prompt, but emphasize:

```python
negative_prompt = "text, watermark, signature, logo, words, letters, typography, ..."
```

---

## Alternative Models

### Stable Diffusion 1.5 (Faster)

```python
generator = ImageGenerator(
    model_id="runwayml/stable-diffusion-v1-5"
)
# Pros: Faster (20-30 sec), less VRAM (4 GB)
# Cons: Lower quality than SDXL
```

### DreamShaper (Community Favorite)

```python
generator = ImageGenerator(
    model_id="Lykon/dreamshaper-8"
)
# Pros: Great for fantasy/dreamlike scenes
# Cons: Same size as SD 1.5
```

### Realistic Vision (Photorealistic)

```python
generator = ImageGenerator(
    model_id="SG161222/Realistic_Vision_V6.0_B1_noVAE"
)
# Pros: Extremely realistic photos
# Cons: May not be ideal for meditation imagery
```

### SDXL Turbo (Fastest)

```python
from diffusers import AutoPipelineForText2Image

pipe = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/sdxl-turbo",
    torch_dtype=torch.float16
)
# Pros: 1 step generation (1-2 seconds!)
# Cons: Lower quality, less control
```

---

## Integration with Video Pipeline

### Update create_final_video.sh

```bash
#!/bin/bash
# Add to the beginning of create_final_video.sh

SESSION_DIR="$(dirname "$0")"

# Check if images exist, generate if missing
REQUIRED_IMAGES=(
    "eden_01_pretalk.png"
    "eden_02_induction.png"
    "eden_03_meadow.png"
    "eden_04_serpent.png"
    "eden_05_tree.png"
    "eden_06_divine.png"
    "eden_07_return.png"
)

MISSING_IMAGES=false
for img in "${REQUIRED_IMAGES[@]}"; do
    if [ ! -f "$SESSION_DIR/$img" ]; then
        echo "⚠️  Missing: $img"
        MISSING_IMAGES=true
    fi
done

if [ "$MISSING_IMAGES" = true ]; then
    echo ""
    echo "🎨 Generating missing images..."
    python3 ../../scripts/core/generate_images_sd.py \
        --session-dir "$SESSION_DIR" \
        --quality normal \
        --candidates 3
    echo ""
fi

# Continue with video creation...
```

---

## Cost & Licensing

### Cost
- **100% FREE** - No API costs, no subscriptions
- **One-time download** - Model cached locally (~13 GB)
- **Unlimited generation** - Generate as many images as you want

### Licensing

**SDXL Model License:** CreativeML Open RAIL++-M
- ✅ Commercial use allowed
- ✅ You own generated images
- ⚠️ Cannot use for illegal purposes
- ⚠️ Cannot claim images are human-created

**Code License:** All provided scripts are open-source

**Full license:** https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/LICENSE.md

---

## Advanced: Custom Prompts

To generate images for a new session:

1. **Copy the script:**
```bash
cp scripts/core/generate_images_sd.py scripts/core/generate_my_session.py
```

2. **Edit the `images_to_generate` list:**
```python
images_to_generate = [
    {
        "filename": "my_image_01.png",
        "prompt": "your custom prompt here, 8k uhd, masterpiece",
        "seed": 42  # Optional
    },
    # Add more...
]
```

3. **Run:**
```bash
python3 scripts/core/generate_my_session.py --session-dir sessions/my-session
```

---

## Monitoring GPU Usage

```bash
# Watch GPU usage in real-time
watch -n 1 nvidia-smi

# Check current usage
nvidia-smi
```

Expected usage:
- **VRAM:** 8-10 GB during generation
- **GPU Utilization:** 90-100%
- **Power:** Near max TDP

---

## Next Steps

1. **Run setup:** `./scripts/core/setup_image_generation.sh`
2. **Test with draft quality:** `python3 scripts/core/generate_images_sd.py --quality draft --candidates 1`
3. **Review first image:** Check if quality/style matches expectations
4. **Generate all images:** `python3 scripts/core/generate_images_sd.py --quality normal`
5. **Select best candidates:** Review and delete unwanted candidates
6. **Create video:** Run `./create_final_video.sh` as usual

---

## Support

**Documentation:**
- Diffusers: https://huggingface.co/docs/diffusers
- SDXL: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0

**Community:**
- r/StableDiffusion: https://reddit.com/r/StableDiffusion
- Stable Diffusion Discord: https://discord.gg/stablediffusion

---

**Happy generating!** 🎨✨
