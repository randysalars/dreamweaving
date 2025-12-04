#!/usr/bin/env python3
"""
Scene Image Generator for Sacred Digital Dreamweaver

Primary image generation script that supports multiple methods:
1. Stable Diffusion (DEFAULT) - Local generation using HuggingFace Diffusers
2. Midjourney Prompts - Generate prompts for external Midjourney use
3. PIL Procedural - Fast procedural generation for placeholders

Usage:
    # Generate scenes with Stable Diffusion (default)
    python3 scripts/core/generate_scene_images.py sessions/{session}/

    # Generate with upscaling to 1920x1080
    python3 scripts/core/generate_scene_images.py sessions/{session}/ --upscale

    # Generate Midjourney prompts only (no images)
    python3 scripts/core/generate_scene_images.py sessions/{session}/ --midjourney-only

    # Generate both SD images and Midjourney prompts
    python3 scripts/core/generate_scene_images.py sessions/{session}/ --with-prompts

    # Use PIL procedural generation (fast, no AI)
    python3 scripts/core/generate_scene_images.py sessions/{session}/ --method pil

    # Customize SD generation
    python3 scripts/core/generate_scene_images.py sessions/{session}/ --steps 20 --style cosmic_journey

Dependencies:
    pip install diffusers transformers accelerate torch Pillow pyyaml
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import yaml
except ImportError:
    yaml = None

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow required. Install with: pip install Pillow")
    sys.exit(1)


# =============================================================================
# STYLE PRESETS
# =============================================================================

STYLE_PRESETS = {
    "neural_network": {
        "suffix": ", bioluminescent neural pathways, cyan and magenta glow, "
                 "cosmic void background, sacred geometry, ethereal atmosphere, "
                 "8k resolution, hyper-detailed, cinematic lighting",
        "negative": "text, watermark, cartoon, anime, blurry, low quality, deformed",
        "colors": {
            "primary": (0, 212, 255),      # Cyan
            "secondary": (155, 109, 255),   # Purple
            "accent": (255, 0, 128),        # Magenta
            "background": (10, 10, 26)      # Dark void
        }
    },
    "sacred_light": {
        "suffix": ", golden divine light, ethereal glow, sacred geometry, "
                 "volumetric lighting, heavenly atmosphere, mystical, "
                 "8k resolution, cinematic, photorealistic",
        "negative": "dark, gloomy, text, watermark, cartoon, blurry",
        "colors": {
            "primary": (255, 215, 0),       # Gold
            "secondary": (244, 228, 188),   # Cream
            "accent": (255, 180, 100),      # Warm gold
            "background": (10, 10, 26)      # Cosmic dark
        }
    },
    "cosmic_journey": {
        "suffix": ", deep space, nebula, starfield, cosmic dust, "
                 "purple and blue tones, ethereal, vast expanse, "
                 "8k resolution, cinematic, hyper-detailed",
        "negative": "text, watermark, cartoon, anime, blurry, low quality",
        "colors": {
            "primary": (155, 109, 255),     # Purple
            "secondary": (100, 181, 246),   # Blue
            "accent": (255, 255, 255),      # White stars
            "background": (13, 2, 33)       # Space dark
        }
    },
    "garden_eden": {
        "suffix": ", lush paradise garden, golden light filtering through trees, "
                 "crystal clear water, vibrant flowers, peaceful atmosphere, "
                 "8k resolution, photorealistic, ethereal",
        "negative": "dead plants, dark, gloomy, text, watermark, blurry",
        "colors": {
            "primary": (80, 200, 120),      # Emerald
            "secondary": (255, 215, 0),     # Gold
            "accent": (144, 238, 144),      # Light green
            "background": (15, 40, 24)      # Forest dark
        }
    },
    "ancient_temple": {
        "suffix": ", ancient mystical temple, torchlight, carved stone, "
                 "sacred symbols, mysterious atmosphere, dusty light rays, "
                 "8k resolution, cinematic, photorealistic",
        "negative": "modern, text, watermark, cartoon, blurry",
        "colors": {
            "primary": (212, 175, 55),      # Antique gold
            "secondary": (139, 69, 19),     # Bronze
            "accent": (255, 200, 100),      # Warm light
            "background": (26, 15, 10)      # Shadow
        }
    },
    "celestial_blue": {
        "suffix": ", celestial realm, soft blue light, clouds, "
                 "peaceful heavenly atmosphere, ethereal beings, "
                 "8k resolution, cinematic, dreamy",
        "negative": "dark, scary, text, watermark, cartoon, blurry",
        "colors": {
            "primary": (135, 206, 250),     # Sky blue
            "secondary": (255, 255, 255),   # White
            "accent": (173, 216, 230),      # Light blue
            "background": (25, 25, 112)     # Midnight blue
        }
    }
}


# =============================================================================
# SCENE PARSING
# =============================================================================

@dataclass
class Scene:
    """Represents a scene to be generated."""
    number: int
    name: str
    prompt: str
    filename: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None


def parse_midjourney_prompts(prompts_file: Path) -> List[Scene]:
    """Parse Midjourney prompts file to extract scene descriptions."""
    scenes = []

    if not prompts_file.exists():
        return scenes

    content = prompts_file.read_text()

    # Find all scene blocks
    scene_pattern = r'## Scene (\d+):\s*([^\n]+).*?```\n/imagine prompt:\s*([^`]+)```'
    matches = re.findall(scene_pattern, content, re.DOTALL)

    for num, title, prompt in matches:
        prompt = prompt.strip()
        # Remove Midjourney parameters
        prompt = re.sub(r'--\w+\s+\S+', '', prompt).strip()
        prompt = prompt.rstrip(',').strip()

        scene_name = f"scene_{int(num):02d}_{title.lower().replace(' ', '_').replace('/', '_')}"
        scene_name = re.sub(r'[^a-z0-9_]', '', scene_name)

        scenes.append(Scene(
            number=int(num),
            name=title,
            prompt=prompt,
            filename=f"{scene_name}.png"
        ))

    return scenes


def parse_manifest_sections(manifest_file: Path) -> List[Scene]:
    """Parse manifest.yaml to extract section descriptions for scene generation."""
    if yaml is None or not manifest_file.exists():
        return []

    with open(manifest_file) as f:
        manifest = yaml.safe_load(f)

    scenes = []
    sections = manifest.get('sections', [])

    for i, section in enumerate(sections, 1):
        name = section.get('name', f'Section {i}')
        visual = section.get('visual_theme', '')
        description = section.get('description', '')
        mood = section.get('mood', '')

        # Build a descriptive prompt
        parts = []
        if visual:
            parts.append(visual)
        if description:
            parts.append(description)
        if mood:
            parts.append(f"{mood} atmosphere")

        prompt = ', '.join(parts) if parts else f"Abstract mystical scene for {name}"

        # Get timing if available
        start = section.get('start')
        end = section.get('end')

        # Get image filename if specified
        image_file = section.get('image', f"scene_{i:02d}_{name.lower().replace(' ', '_')}.png")

        scenes.append(Scene(
            number=i,
            name=name,
            prompt=prompt,
            filename=image_file,
            start_time=float(start) if start else None,
            end_time=float(end) if end else None
        ))

    return scenes


def get_scenes(session_dir: Path) -> Tuple[List[Scene], str]:
    """Get scenes from session, trying midjourney prompts first, then manifest."""
    prompts_file = session_dir / "midjourney-prompts.md"
    manifest_file = session_dir / "manifest.yaml"

    scenes = parse_midjourney_prompts(prompts_file)
    if scenes:
        return scenes, "midjourney-prompts.md"

    scenes = parse_manifest_sections(manifest_file)
    if scenes:
        return scenes, "manifest.yaml"

    return [], None


# =============================================================================
# STABLE DIFFUSION GENERATION
# =============================================================================

def load_sd_pipeline(model_path: str = None):
    """Load the Stable Diffusion pipeline."""
    try:
        import torch
        from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    except ImportError:
        print("Error: diffusers/torch not installed.")
        print("Install with: pip install diffusers transformers accelerate torch")
        return None

    # Try local model first, then HuggingFace
    if model_path and Path(model_path).exists():
        print(f"Loading model from: {model_path}")
        pipe = StableDiffusionPipeline.from_single_file(
            model_path,
            torch_dtype=torch.float32,
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

    # Enable memory efficient attention
    try:
        pipe.enable_attention_slicing()
    except:
        pass

    return pipe


def generate_sd_image(
    pipe,
    prompt: str,
    negative_prompt: str,
    width: int = 512,
    height: int = 288,
    steps: int = 15,
    guidance_scale: float = 7.5,
    seed: int = -1
) -> Image.Image:
    """Generate a single image using Stable Diffusion."""
    import torch

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


def generate_sd_scenes(
    session_dir: Path,
    scenes: List[Scene],
    style_preset: str = "neural_network",
    steps: int = 15,
    upscale: bool = True,
    force: bool = False,
    model_path: str = None
) -> List[str]:
    """Generate scene images using Stable Diffusion."""

    preset = STYLE_PRESETS.get(style_preset, STYLE_PRESETS["neural_network"])

    # Output directory
    output_dir = session_dir / "images" / "uploaded"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load pipeline
    print("Loading Stable Diffusion pipeline...")
    pipe = load_sd_pipeline(model_path)
    if pipe is None:
        return []
    print("Pipeline loaded successfully!")

    results = []

    print(f"\nGenerating {len(scenes)} scene images...")
    print(f"Output: {output_dir}")
    print(f"Steps: {steps}, Style: {style_preset}")
    print("=" * 60)

    for i, scene in enumerate(scenes, 1):
        output_file = output_dir / scene.filename

        # Skip if exists and not forcing
        if output_file.exists() and not force:
            print(f"\n[{i}/{len(scenes)}] {scene.filename}: exists, skipping")
            results.append(str(output_file))
            continue

        # Enhance prompt with style
        full_prompt = scene.prompt + preset["suffix"]
        negative_prompt = preset["negative"]

        print(f"\n[{i}/{len(scenes)}] {scene.filename}")
        print(f"  Prompt: {scene.prompt[:60]}...")
        print(f"  Generating...", end=" ", flush=True)

        try:
            img = generate_sd_image(
                pipe=pipe,
                prompt=full_prompt,
                negative_prompt=negative_prompt,
                width=512,
                height=288,  # 16:9 ratio
                steps=steps,
                guidance_scale=7.5,
                seed=scene.number * 1000
            )

            # Upscale if requested
            if upscale:
                img = upscale_image(img, target_width=1920)

            img.save(output_file, quality=95)
            print(f"Done!")
            results.append(str(output_file))

        except Exception as e:
            print(f"Error: {e}")
            continue

    print("\n" + "=" * 60)
    print(f"Generated {len(results)}/{len(scenes)} images")

    return results


# =============================================================================
# MIDJOURNEY PROMPT GENERATION
# =============================================================================

def generate_midjourney_prompts(
    session_dir: Path,
    scenes: List[Scene],
    style_preset: str = "neural_network"
) -> str:
    """Generate Midjourney prompts markdown file."""

    preset = STYLE_PRESETS.get(style_preset, STYLE_PRESETS["neural_network"])

    # Get session info from manifest
    manifest_file = session_dir / "manifest.yaml"
    session_name = session_dir.name.replace('-', ' ').title()

    if yaml and manifest_file.exists():
        with open(manifest_file) as f:
            manifest = yaml.safe_load(f)
        session_name = manifest.get('title', session_name)

    lines = [
        f"# Midjourney Prompts for {session_name}",
        "",
        f"**Style Preset:** {style_preset}",
        f"**Total Scenes:** {len(scenes)}",
        "",
        "## Generation Instructions",
        "",
        "1. Copy each prompt into Midjourney",
        "2. Use aspect ratio --ar 16:9 for video backgrounds",
        "3. Style raw (--style raw) recommended for consistency",
        "4. After generation, place images in `images/uploaded/`",
        "",
        "---",
        ""
    ]

    for scene in scenes:
        # Build Midjourney-specific prompt
        mj_prompt = scene.prompt
        # Add style elements
        mj_suffix = preset["suffix"].replace("8k resolution, ", "").replace(", hyper-detailed", "")
        full_prompt = f"{mj_prompt}{mj_suffix}"

        lines.extend([
            f"## Scene {scene.number}: {scene.name}",
            "",
            f"**Output Filename:** `{scene.filename}`",
            "",
            "```",
            f"/imagine prompt: {full_prompt} --ar 16:9 --style raw --v 6.1",
            "```",
            ""
        ])

        if scene.start_time is not None and scene.end_time is not None:
            duration = scene.end_time - scene.start_time
            lines.append(f"**Timing:** {scene.start_time:.0f}s - {scene.end_time:.0f}s ({duration:.0f}s)")
            lines.append("")

    # Thumbnail section
    lines.extend([
        "---",
        "",
        "## Thumbnail Prompt",
        "",
        "```",
        f"/imagine prompt: {session_name} mystical scene, central luminous focal point, "
        "ethereal lighting, dark vignette edges fading to bright center, "
        "space for text overlay in top third, cinematic composition, "
        f"{preset['suffix'].split(',')[0]}, hyper-detailed --ar 16:9 --style raw --v 6.1",
        "```",
        ""
    ])

    content = "\n".join(lines)

    # Write to file
    output_file = session_dir / "midjourney-prompts.md"
    output_file.write_text(content)
    print(f"Midjourney prompts saved to: {output_file}")

    return content


# =============================================================================
# AUTO-DETECT STYLE
# =============================================================================

def auto_detect_style(session_dir: Path) -> str:
    """Auto-detect the best style preset based on session name/content."""
    session_name = session_dir.name.lower()

    if 'neural' in session_name or 'network' in session_name or 'brain' in session_name:
        return "neural_network"
    elif 'eden' in session_name or 'garden' in session_name:
        return "garden_eden"
    elif 'cosmic' in session_name or 'space' in session_name or 'star' in session_name:
        return "cosmic_journey"
    elif 'temple' in session_name or 'ancient' in session_name:
        return "ancient_temple"
    elif 'sacred' in session_name or 'divine' in session_name or 'light' in session_name:
        return "sacred_light"
    elif 'heaven' in session_name or 'celestial' in session_name:
        return "celestial_blue"
    else:
        return "neural_network"  # Default


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate scene images for Dreamweaver sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate SD images (default)
  python3 generate_scene_images.py sessions/my-session/

  # Generate with upscaling
  python3 generate_scene_images.py sessions/my-session/ --upscale

  # Generate Midjourney prompts only
  python3 generate_scene_images.py sessions/my-session/ --midjourney-only

  # Generate both SD images and Midjourney prompts
  python3 generate_scene_images.py sessions/my-session/ --with-prompts

  # Custom style and steps
  python3 generate_scene_images.py sessions/my-session/ --style cosmic_journey --steps 20
"""
    )

    parser.add_argument(
        "session_dir",
        help="Path to session directory"
    )
    parser.add_argument(
        "--style",
        choices=list(STYLE_PRESETS.keys()),
        help="Style preset (auto-detected if not specified)"
    )
    parser.add_argument(
        "--method",
        choices=["sd", "midjourney", "pil"],
        default="sd",
        help="Generation method: sd (Stable Diffusion), midjourney (prompts only), pil (procedural)"
    )
    parser.add_argument(
        "--midjourney-only",
        action="store_true",
        help="Generate Midjourney prompts only (no images)"
    )
    parser.add_argument(
        "--with-prompts",
        action="store_true",
        help="Generate both SD images and Midjourney prompts"
    )
    parser.add_argument(
        "--upscale",
        action="store_true",
        default=True,
        help="Upscale generated images to 1920x1080 (default: True)"
    )
    parser.add_argument(
        "--no-upscale",
        action="store_true",
        help="Disable upscaling (keep at 512x288)"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=15,
        help="SD inference steps (default: 15, more=better quality but slower)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even if images exist"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Path to local SD model file (optional)"
    )

    args = parser.parse_args()

    session_dir = Path(args.session_dir)
    if not session_dir.exists():
        print(f"Error: Session directory not found: {session_dir}")
        sys.exit(1)

    # Get scenes
    scenes, source = get_scenes(session_dir)
    if not scenes:
        print(f"Error: No scene descriptions found in {session_dir}")
        print("Expected either midjourney-prompts.md or manifest.yaml with sections")
        sys.exit(1)

    print(f"Found {len(scenes)} scenes from {source}")

    # Auto-detect style if not specified
    style = args.style or auto_detect_style(session_dir)
    print(f"Using style: {style}")

    # Handle upscale flag
    upscale = args.upscale and not args.no_upscale

    # Handle --midjourney-only
    if args.midjourney_only:
        args.method = "midjourney"

    # Check for local model
    model_path = args.model
    if not model_path:
        local_model = Path.home() / "sd-webui" / "models" / "Stable-diffusion" / "sd-v1-5-pruned-emaonly.safetensors"
        if local_model.exists():
            model_path = str(local_model)
            print(f"Found local model: {model_path}")

    # Generate based on method
    if args.method == "midjourney":
        generate_midjourney_prompts(session_dir, scenes, style)
        print("\nMidjourney prompts generated. Create images in Midjourney and place in images/uploaded/")

    elif args.method == "sd":
        results = generate_sd_scenes(
            session_dir=session_dir,
            scenes=scenes,
            style_preset=style,
            steps=args.steps,
            upscale=upscale,
            force=args.force,
            model_path=model_path
        )

        # Also generate Midjourney prompts if requested
        if args.with_prompts:
            print("\n" + "=" * 60)
            print("Generating Midjourney prompts as alternative...")
            generate_midjourney_prompts(session_dir, scenes, style)

        if results:
            print(f"\nSuccess! Generated {len(results)} images")
            sys.exit(0)
        else:
            print("\nNo images generated")
            sys.exit(1)

    elif args.method == "pil":
        print("PIL procedural generation not yet implemented in unified script")
        print("Use scripts/core/generate_video_images.py for procedural backgrounds")
        sys.exit(1)


if __name__ == "__main__":
    main()
