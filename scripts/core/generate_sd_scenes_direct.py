#!/usr/bin/env python3
"""
Direct Stable Diffusion Scene Generator using Diffusers

Generates scene images using HuggingFace Diffusers library directly,
without needing the AUTOMATIC1111 WebUI server.

This is a simpler, more compatible approach for CPU-based generation.

Usage:
    # Generate scenes for a session
    python3 scripts/core/generate_sd_scenes_direct.py sessions/neural-network-navigator/

    # With upscaling
    python3 scripts/core/generate_sd_scenes_direct.py sessions/neural-network-navigator/ --upscale
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import warnings

# Suppress various warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import torch
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    from PIL import Image
except ImportError as e:
    print(f"Error: Required package not installed: {e}")
    print("Install with: pip install diffusers transformers accelerate torch")
    sys.exit(1)

try:
    import yaml
except ImportError:
    yaml = None


# Style presets for Dreamweaver sessions
STYLE_PRESETS = {
    "neural_network": {
        "suffix": ", bioluminescent neural pathways, cyan and magenta glow, "
                 "cosmic void background, sacred geometry, ethereal atmosphere, "
                 "8k resolution, hyper-detailed, cinematic lighting",
        "negative": "text, watermark, cartoon, anime, blurry, low quality, deformed"
    },
    "sacred_light": {
        "suffix": ", golden divine light, ethereal glow, sacred geometry, "
                 "volumetric lighting, heavenly atmosphere, mystical, "
                 "8k resolution, cinematic, photorealistic",
        "negative": "dark, gloomy, text, watermark, cartoon, blurry"
    },
    "cosmic_journey": {
        "suffix": ", deep space, nebula, starfield, cosmic dust, "
                 "purple and blue tones, ethereal, vast expanse, "
                 "8k resolution, cinematic, hyper-detailed",
        "negative": "text, watermark, cartoon, anime, blurry, low quality"
    },
    "garden_eden": {
        "suffix": ", lush paradise garden, golden light filtering through trees, "
                 "crystal clear water, vibrant flowers, peaceful atmosphere, "
                 "8k resolution, photorealistic, ethereal",
        "negative": "dead plants, dark, gloomy, text, watermark, blurry"
    }
}


def parse_midjourney_prompts(prompts_file: Path) -> List[Tuple[str, str]]:
    """Parse Midjourney prompts file to extract scene descriptions."""
    scenes = []

    if not prompts_file.exists():
        return scenes

    content = prompts_file.read_text()

    # Find all scene blocks
    scene_pattern = r'## Scene (\d+):\s*([^\n]+).*?```\n/imagine prompt:\s*([^`]+)```'
    matches = re.findall(scene_pattern, content, re.DOTALL)

    for num, title, prompt in matches:
        # Clean up the prompt
        prompt = prompt.strip()
        # Remove Midjourney parameters
        prompt = re.sub(r'--\w+\s+\S+', '', prompt).strip()
        prompt = prompt.rstrip(',').strip()

        scene_name = f"scene_{int(num):02d}_{title.lower().replace(' ', '_').replace('/', '_')}"
        scene_name = re.sub(r'[^a-z0-9_]', '', scene_name)

        scenes.append((scene_name, prompt))

    return scenes


def load_pipeline(model_path: str = None) -> StableDiffusionPipeline:
    """Load the Stable Diffusion pipeline."""

    # Try local model first, then fall back to HuggingFace
    if model_path and Path(model_path).exists():
        print(f"Loading model from: {model_path}")
        pipe = StableDiffusionPipeline.from_single_file(
            model_path,
            torch_dtype=torch.float32,  # Use float32 for CPU
            use_safetensors=True
        )
    else:
        print("Downloading model from HuggingFace (this may take a while first time)...")
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float32,
            use_safetensors=True
        )

    # Use DPM solver for faster inference
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

    # CPU mode
    pipe = pipe.to("cpu")

    # Enable memory efficient attention if available
    try:
        pipe.enable_attention_slicing()
    except:
        pass

    return pipe


def generate_image(
    pipe: StableDiffusionPipeline,
    prompt: str,
    negative_prompt: str,
    width: int = 512,
    height: int = 512,
    steps: int = 15,
    guidance_scale: float = 7.5,
    seed: int = -1
) -> Image.Image:
    """Generate a single image."""

    # Set seed for reproducibility
    if seed >= 0:
        generator = torch.Generator("cpu").manual_seed(seed)
    else:
        generator = None

    with torch.no_grad():
        result = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=steps,
            guidance_scale=guidance_scale,
            generator=generator
        )

    return result.images[0]


def upscale_image(img: Image.Image, target_width: int = 1920) -> Image.Image:
    """Upscale image using Lanczos resampling."""
    aspect_ratio = img.height / img.width
    new_width = target_width
    new_height = int(target_width * aspect_ratio)
    return img.resize((new_width, new_height), Image.LANCZOS)


def generate_session_scenes(
    session_dir: Path,
    style_preset: str = None,
    upscale: bool = False,
    steps: int = 15,
    force: bool = False,
    model_path: str = None
) -> List[str]:
    """Generate scene images for a Dreamweaver session."""

    session_dir = Path(session_dir)

    # Get scenes from midjourney prompts
    prompts_file = session_dir / "midjourney-prompts.md"
    scenes = parse_midjourney_prompts(prompts_file)

    if not scenes:
        print(f"Error: No scenes found in {prompts_file}")
        return []

    print(f"Found {len(scenes)} scenes")

    # Auto-detect style preset
    if style_preset is None:
        session_name = session_dir.name.lower()
        if 'neural' in session_name or 'network' in session_name:
            style_preset = "neural_network"
        elif 'eden' in session_name or 'garden' in session_name:
            style_preset = "garden_eden"
        elif 'cosmic' in session_name or 'space' in session_name:
            style_preset = "cosmic_journey"
        else:
            style_preset = "neural_network"
        print(f"Auto-detected style: {style_preset}")

    preset = STYLE_PRESETS.get(style_preset, STYLE_PRESETS["neural_network"])

    # Output directories
    sd_output_dir = session_dir / "images" / "sd_generated"
    sd_output_dir.mkdir(parents=True, exist_ok=True)

    if upscale:
        upscaled_dir = session_dir / "images" / "uploaded"
        upscaled_dir.mkdir(parents=True, exist_ok=True)

    # Load pipeline
    print("Loading Stable Diffusion pipeline...")
    pipe = load_pipeline(model_path)
    print("Pipeline loaded successfully!")

    results = []

    print(f"\nGenerating {len(scenes)} scene images...")
    print(f"Output: {sd_output_dir}")
    print(f"Steps: {steps}, Style: {style_preset}")
    print("=" * 60)

    for i, (scene_name, base_prompt) in enumerate(scenes, 1):
        output_file = sd_output_dir / f"{scene_name}.png"

        # Skip if exists and not forcing
        if output_file.exists() and not force:
            print(f"\n[{i}/{len(scenes)}] {scene_name}: exists, skipping")
            results.append(str(output_file))
            continue

        # Enhance prompt with style
        prompt = base_prompt + preset["suffix"]
        negative_prompt = preset["negative"]

        print(f"\n[{i}/{len(scenes)}] {scene_name}")
        print(f"  Prompt: {base_prompt[:60]}...")
        print(f"  Generating...", end=" ", flush=True)

        try:
            # Generate at 512x288 for 16:9 aspect ratio
            img = generate_image(
                pipe=pipe,
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=512,
                height=288,  # 16:9 ratio
                steps=steps,
                guidance_scale=7.5,
                seed=i * 1000
            )

            # Save generated image
            img.save(output_file, quality=95)
            print(f"Done!")
            results.append(str(output_file))

            # Upscale if requested
            if upscale:
                upscaled_file = upscaled_dir / f"{scene_name}.png"
                print(f"  Upscaling to 1920x1080...", end=" ", flush=True)
                upscaled = upscale_image(img, target_width=1920)
                upscaled.save(upscaled_file, quality=95)
                print("Done!")

        except Exception as e:
            print(f"Error: {e}")
            continue

    print("\n" + "=" * 60)
    print(f"Generated {len(results)}/{len(scenes)} images")

    if upscale:
        print(f"Upscaled images in: {upscaled_dir}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate scene images using Stable Diffusion (Direct Diffusers)"
    )
    parser.add_argument(
        "session_dir",
        help="Path to session directory"
    )
    parser.add_argument(
        "--style",
        choices=["neural_network", "sacred_light", "cosmic_journey", "garden_eden"],
        help="Style preset (auto-detected if not specified)"
    )
    parser.add_argument(
        "--upscale",
        action="store_true",
        help="Upscale generated images to 1920x1080"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=15,
        help="Number of inference steps (default: 15)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even if images exist"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Path to local model file (optional)"
    )

    args = parser.parse_args()

    session_dir = Path(args.session_dir)
    if not session_dir.exists():
        print(f"Error: Session directory not found: {session_dir}")
        sys.exit(1)

    # Check for local model
    model_path = args.model
    if not model_path:
        local_model = Path.home() / "sd-webui" / "models" / "Stable-diffusion" / "sd-v1-5-pruned-emaonly.safetensors"
        if local_model.exists():
            model_path = str(local_model)
            print(f"Found local model: {model_path}")

    results = generate_session_scenes(
        session_dir=session_dir,
        style_preset=args.style,
        upscale=args.upscale,
        steps=args.steps,
        force=args.force,
        model_path=model_path
    )

    if results:
        print(f"\nSuccess! Generated {len(results)} images")
        sys.exit(0)
    else:
        print("\nNo images generated")
        sys.exit(1)


if __name__ == "__main__":
    main()
