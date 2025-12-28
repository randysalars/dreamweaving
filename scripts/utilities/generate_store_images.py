#!/usr/bin/env python3
"""
Generate category images for digital store using Stable Diffusion 1.5.
Creates 1024x1024 images matching the style of existing store category images.
"""

import os
import sys
import torch
from pathlib import Path
from diffusers import StableDiffusionPipeline

# Output directory
OUTPUT_DIR = "/home/rsalars/Projects/salarsu/frontend/public/images/store/digital"

# SD 1.5 model path
MODEL_PATH = os.path.expanduser("~/sd-webui/models/Stable-diffusion/sd-v1-5-pruned-emaonly.safetensors")

# Image specifications
IMAGE_SIZE = 1024
NUM_INFERENCE_STEPS = 50
GUIDANCE_SCALE = 7.5

# Category image prompts - designed to match existing ethereal/mystical store aesthetic
CATEGORY_PROMPTS = {
    "consciousness": {
        "prompt": "ethereal glowing human brain made of light and neural networks, cosmic consciousness, purple and blue nebula background, sacred geometry patterns, mystical energy flows, digital art, highly detailed, 8k, spiritual awakening concept",
        "negative": "text, watermark, ugly, blurry, low quality, distorted"
    },
    "ai": {
        "prompt": "futuristic digital brain with circuit patterns, harmonious blend of human and artificial intelligence, cyan and magenta glow, sacred geometry circuits, holographic display, digital art, highly detailed, 8k, technology meets spirituality",
        "negative": "text, watermark, ugly, blurry, low quality, distorted, scary robot"
    },
    "spirituality": {
        "prompt": "serene meditation scene with golden candlelight, sacred geometry mandala, soft ethereal glow, ancient wisdom symbols, peaceful contemplative atmosphere, warm amber and gold tones, digital art, highly detailed, 8k",
        "negative": "text, watermark, ugly, blurry, low quality, distorted, dark, scary"
    },
    "survival": {
        "prompt": "vintage compass on ancient map with protective shield symbol, nature survival elements, forest and mountains in background, earth tones with golden accents, adventure and preparedness theme, digital art, highly detailed, 8k",
        "negative": "text, watermark, ugly, blurry, low quality, distorted, weapons, violence"
    },
    "poetry": {
        "prompt": "elegant antique quill pen with flowing golden ink becoming words and light, moonlit night sky with stars, creative inspiration theme, romantic and artistic atmosphere, purple and gold tones, digital art, highly detailed, 8k",
        "negative": "text, watermark, ugly, blurry, low quality, distorted"
    },
    "treasure": {
        "prompt": "ancient treasure map with golden compass and glowing artifacts, adventure discovery theme, mysterious amber light, vintage parchment and jewels, explorer aesthetic, warm gold and brown tones, digital art, highly detailed, 8k",
        "negative": "text, watermark, ugly, blurry, low quality, distorted, pirate skull"
    },
    "old-west": {
        "prompt": "majestic desert sunset with cowboy silhouette on horseback, western frontier landscape, golden hour light, iconic American west scenery, warm orange and red sky, digital art, highly detailed, 8k, nostalgic frontier spirit",
        "negative": "text, watermark, ugly, blurry, low quality, distorted, violence, guns"
    },
    "love": {
        "prompt": "two glowing hearts intertwined with soft ethereal light, warm pink and rose gold glow, romantic connection energy, sacred geometry of love, gentle radiant atmosphere, digital art, highly detailed, 8k, pure love concept",
        "negative": "text, watermark, ugly, blurry, low quality, distorted, explicit"
    },
    "happiness": {
        "prompt": "radiant golden sunrise over peaceful landscape, warm light rays spreading joy, uplifting energy visualization, yellow and gold ethereal glow, positive wellbeing concept, blooming flowers, digital art, highly detailed, 8k",
        "negative": "text, watermark, ugly, blurry, low quality, distorted, dark, sad"
    }
}


def load_pipeline():
    """Load the Stable Diffusion pipeline."""
    print(f"Loading SD 1.5 model from: {MODEL_PATH}")

    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found at {MODEL_PATH}")
        sys.exit(1)

    # Load pipeline
    pipe = StableDiffusionPipeline.from_single_file(
        MODEL_PATH,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        use_safetensors=True
    )

    # Move to GPU if available
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
        print("Using CUDA GPU")
    else:
        print("Using CPU (this will be slow)")

    # Enable memory optimizations
    if hasattr(pipe, 'enable_attention_slicing'):
        pipe.enable_attention_slicing()

    return pipe


def generate_image(pipe, category_name, prompt_data):
    """Generate a single category image."""
    output_path = os.path.join(OUTPUT_DIR, f"{category_name}.png")

    # Skip if image already exists
    if os.path.exists(output_path):
        print(f"  Skipping {category_name}.png (already exists)")
        return True

    print(f"  Generating {category_name}.png...")

    try:
        # Generate image
        image = pipe(
            prompt=prompt_data["prompt"],
            negative_prompt=prompt_data["negative"],
            height=IMAGE_SIZE,
            width=IMAGE_SIZE,
            num_inference_steps=NUM_INFERENCE_STEPS,
            guidance_scale=GUIDANCE_SCALE,
        ).images[0]

        # Save as PNG
        image.save(output_path, "PNG")
        print(f"  Saved: {output_path}")
        return True

    except Exception as e:
        print(f"  Error generating {category_name}: {e}")
        return False


def main():
    """Main function to generate all category images."""
    print("=" * 60)
    print("Digital Store Category Image Generator")
    print("=" * 60)

    # Create output directory if needed
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Check which images are needed
    needed = []
    for category in CATEGORY_PROMPTS:
        path = os.path.join(OUTPUT_DIR, f"{category}.png")
        if not os.path.exists(path):
            needed.append(category)

    if not needed:
        print("All category images already exist!")
        return

    print(f"\nImages to generate: {', '.join(needed)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # Load pipeline
    pipe = load_pipeline()
    print()

    # Generate images
    success = 0
    failed = 0

    for category in needed:
        if generate_image(pipe, category, CATEGORY_PROMPTS[category]):
            success += 1
        else:
            failed += 1

    # Summary
    print()
    print("=" * 60)
    print(f"Complete: {success} generated, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
