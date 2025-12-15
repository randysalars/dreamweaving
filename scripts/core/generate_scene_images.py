#!/usr/bin/env python3
"""
Scene Image Generator for Sacred Digital Dreamweaver

Primary image generation script that supports multiple methods:
1. Stable Diffusion (DEFAULT) - Local generation using HuggingFace Diffusers
2. Midjourney Prompts - Generate prompts for external Midjourney use
3. Stock Images - Search and download from Unsplash/Pexels/Pixabay
4. PIL Procedural - Fast procedural generation for placeholders

Usage:
    # Generate scenes with Stable Diffusion (default)
    python3 scripts/core/generate_scene_images.py sessions/{session}/

    # Generate with upscaling to 1920x1080
    python3 scripts/core/generate_scene_images.py sessions/{session}/ --upscale

    # Generate Midjourney prompts only (no images)
    python3 scripts/core/generate_scene_images.py sessions/{session}/ --midjourney-only

    # Generate both SD images and Midjourney prompts
    python3 scripts/core/generate_scene_images.py sessions/{session}/ --with-prompts

    # Use stock images (opens search URLs, guides through download)
    python3 scripts/core/generate_scene_images.py sessions/{session}/ --method stock

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
import subprocess
import webbrowser
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import warnings
import urllib.parse

# Ensure project root is on path when executed as a script (needed for imports like scripts.core.generate_images_sd)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
    },
    "volcanic_forge": {
        "suffix": ", volcanic landscape, molten fire, glowing embers, "
                 "ancient forge, primal power, dramatic lighting, "
                 "8k resolution, cinematic, hyper-detailed",
        "negative": "cartoon, text, watermark, blurry, cute",
        "colors": {
            "primary": (255, 69, 0),        # Orange-red
            "secondary": (139, 0, 0),       # Dark red
            "accent": (255, 215, 0),        # Gold
            "background": (20, 10, 5)       # Deep dark
        }
    }
}

# =============================================================================
# PERFORMANCE PRESETS
# =============================================================================

DEFAULT_SDXL_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
PERFORMANCE_PRESETS = {
    "quality": {
        "model_id": DEFAULT_SDXL_MODEL,
        "steps": 40,
        "guidance": 7.0,
        "use_refiner": True,
        "max_gen_side": 1216,
        "compile_unet": False,
        "disable_safety_checker": False,
    },
    "balanced": {
        "model_id": DEFAULT_SDXL_MODEL,
        "steps": 32,
        "guidance": 6.5,
        "use_refiner": True,
        "max_gen_side": 1152,
        "compile_unet": False,
        "disable_safety_checker": False,
    },
    "speed": {
        "model_id": DEFAULT_SDXL_MODEL,
        "steps": 18,
        "guidance": 5.5,
        "use_refiner": False,
        "max_gen_side": 960,
        "compile_unet": True,
        "disable_safety_checker": True,
    },
    "turbo": {
        "model_id": "stabilityai/sdxl-turbo",
        "steps": 4,
        "guidance": 0.0,
        "use_refiner": False,
        "max_gen_side": 1024,
        "compile_unet": False,
        "disable_safety_checker": True,
    },
}


# =============================================================================
# DEPTH STAGE VISUAL MODIFIERS (Journey-Aware Enhancement)
# =============================================================================
# These modifiers adjust image generation prompts based on hypnosis depth stage,
# creating visual consistency with the audio journey's emotional arc.

DEPTH_STAGE_MODIFIERS = {
    "pre_talk": {
        "description": "Grounded, safe, welcoming opening",
        "visual_modifiers": [
            "warm natural lighting",
            "clear and grounded composition",
            "inviting atmosphere",
            "stable perspective"
        ],
        "color_shift": {"brightness": 1.1, "saturation": 0.9},
        "mood": "welcoming and stable",
        "vignette_strength": 0.1
    },
    "induction": {
        "description": "Beginning relaxation, softening edges",
        "visual_modifiers": [
            "soft diffused light",
            "gentle bokeh background",
            "calming colors",
            "slightly dreamy atmosphere"
        ],
        "color_shift": {"brightness": 1.0, "saturation": 0.85},
        "mood": "peaceful and calming",
        "vignette_strength": 0.2
    },
    "deepening": {
        "description": "Descending into trance, boundaries dissolving",
        "visual_modifiers": [
            "ethereal glow",
            "misty atmosphere",
            "deeper shadows",
            "soft-focus elements",
            "dreamlike quality"
        ],
        "color_shift": {"brightness": 0.9, "saturation": 0.8},
        "mood": "deep and hypnotic",
        "vignette_strength": 0.3
    },
    "journey": {
        "description": "Active visualization, rich sensory detail",
        "visual_modifiers": [
            "vivid imagination space",
            "rich saturated colors",
            "detailed textures",
            "immersive atmosphere",
            "subtle movement suggestion"
        ],
        "color_shift": {"brightness": 1.0, "saturation": 1.1},
        "mood": "immersive and visionary",
        "vignette_strength": 0.25
    },
    "helm_deep_trance": {
        "description": "Peak experience, transcendent, sacred",
        "visual_modifiers": [
            "divine light emanating",
            "transcendent atmosphere",
            "sacred geometry elements",
            "profound depth",
            "luminous presence",
            "cosmic scale"
        ],
        "color_shift": {"brightness": 1.2, "saturation": 1.0},
        "mood": "transcendent and sacred",
        "vignette_strength": 0.15
    },
    "integration": {
        "description": "Processing, gathering wisdom, preparing to return",
        "visual_modifiers": [
            "soft golden light",
            "peaceful resolution",
            "gentle integration",
            "centered composition"
        ],
        "color_shift": {"brightness": 1.05, "saturation": 0.9},
        "mood": "peaceful and resolving",
        "vignette_strength": 0.2
    },
    "awakening": {
        "description": "Returning, grounded, refreshed",
        "visual_modifiers": [
            "clear morning light",
            "grounded stable composition",
            "refreshed atmosphere",
            "gentle warmth"
        ],
        "color_shift": {"brightness": 1.15, "saturation": 1.0},
        "mood": "refreshed and grounded",
        "vignette_strength": 0.1
    }
}


def get_depth_stage_from_section(section_name: str) -> str:
    """Map section names to depth stages for visual modifier application."""
    name_lower = section_name.lower()

    if 'pre' in name_lower and 'talk' in name_lower:
        return 'pre_talk'
    elif 'induction' in name_lower:
        return 'induction'
    elif 'deepen' in name_lower:
        return 'deepening'
    elif any(x in name_lower for x in ['helm', 'apex', 'peak', 'core', 'luminous']):
        return 'helm_deep_trance'
    elif 'integrat' in name_lower:
        return 'integration'
    elif any(x in name_lower for x in ['awaken', 'return', 'closing']):
        return 'awakening'
    elif 'journey' in name_lower:
        return 'journey'
    else:
        return 'journey'  # Default


def apply_depth_stage_to_prompt(prompt: str, depth_stage: str) -> str:
    """Enhance a scene prompt with depth-stage visual modifiers."""
    if depth_stage not in DEPTH_STAGE_MODIFIERS:
        return prompt

    stage = DEPTH_STAGE_MODIFIERS[depth_stage]

    # Add visual modifiers to the prompt
    modifiers = stage['visual_modifiers']
    mood = stage['mood']

    # Construct enhanced prompt
    enhanced = prompt.rstrip(',.')
    enhanced += f", {mood} mood"
    enhanced += f", {', '.join(modifiers[:3])}"  # Add top 3 modifiers

    return enhanced


def get_depth_stage_color_adjustment(depth_stage: str) -> Dict[str, float]:
    """Get color adjustment parameters for a depth stage."""
    if depth_stage not in DEPTH_STAGE_MODIFIERS:
        return {"brightness": 1.0, "saturation": 1.0}

    return DEPTH_STAGE_MODIFIERS[depth_stage]['color_shift']


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
    depth_stage: str = "journey"  # Hypnosis depth stage for visual modifiers


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

        # Determine depth stage for visual modifiers
        depth_stage = get_depth_stage_from_section(name)

        # Apply depth-stage visual modifiers to the prompt
        enhanced_prompt = apply_depth_stage_to_prompt(prompt, depth_stage)

        scenes.append(Scene(
            number=i,
            name=name,
            prompt=enhanced_prompt,
            filename=image_file,
            start_time=float(start) if start else None,
            end_time=float(end) if end else None,
            depth_stage=depth_stage
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
# STABLE DIFFUSION GENERATION (SDXL DEFAULT)
# =============================================================================

def resolve_generation_config(
    performance: str,
    steps: Optional[int],
    guidance_scale: Optional[float],
    use_refiner: bool,
    max_generation_side: Optional[int],
    model_path: Optional[str]
) -> Dict[str, Any]:
    """Apply performance presets while honoring user overrides."""
    preset = PERFORMANCE_PRESETS.get(performance, PERFORMANCE_PRESETS["balanced"])

    return {
        "model_id": model_path or preset.get("model_id", DEFAULT_SDXL_MODEL),
        "steps": steps if steps is not None else preset["steps"],
        "guidance": guidance_scale if guidance_scale is not None else preset["guidance"],
        "use_refiner": preset["use_refiner"] if performance in ("speed", "turbo") else use_refiner,
        "max_gen_side": max_generation_side or preset["max_gen_side"],
        "compile_unet": preset.get("compile_unet", False),
        "disable_safety_checker": preset.get("disable_safety_checker", False),
    }


def generate_sd_scenes(
    session_dir: Path,
    scenes: List[Scene],
    style_preset: str = "neural_network",
    steps: Optional[int] = None,
    guidance_scale: Optional[float] = None,
    upscale: bool = True,
    force: bool = False,
    model_path: str = None,
    use_refiner: bool = True,
    max_generation_side: Optional[int] = None,
    performance: str = "balanced",
    compile_unet: bool = False,
    disable_safety_checker: bool = False,
    enable_vae_tiling: bool = True
) -> List[str]:
    """Generate scene images using SDXL (with optional refiner)."""

    try:
        from scripts.core.generate_images_sd import ImageGenerator
    except Exception as e:
        print("Error: could not import SDXL generator. Install dependencies:")
        print("  pip install diffusers transformers accelerate torch Pillow")
        print(f"Reason: {e}")
        return []

    preset = STYLE_PRESETS.get(style_preset, STYLE_PRESETS["neural_network"])

    gen_config = resolve_generation_config(
        performance=performance,
        steps=steps,
        guidance_scale=guidance_scale,
        use_refiner=use_refiner,
        max_generation_side=max_generation_side,
        model_path=model_path,
    )

    effective_steps = gen_config["steps"]
    effective_guidance = gen_config["guidance"]
    effective_refiner = gen_config["use_refiner"]
    effective_max_side = gen_config["max_gen_side"]
    effective_model = gen_config["model_id"]
    effective_compile = compile_unet or gen_config["compile_unet"]
    effective_disable_safety = disable_safety_checker or gen_config["disable_safety_checker"]

    # Output directory
    output_dir = session_dir / "images" / "uploaded"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading SDXL pipeline (base" + (" + refiner" if effective_refiner else "") + ")...")
    generator = ImageGenerator(
        model_id=effective_model,
        use_fp16=True,
        enable_optimizations=True,
        use_refiner=effective_refiner,
        max_generation_side=effective_max_side,
        compile_unet=effective_compile,
        disable_safety_checker=effective_disable_safety,
        enable_vae_tiling=enable_vae_tiling
    )
    print("Pipeline loaded successfully!")

    results = []

    target_width = 1920 if upscale else 1280
    target_height = 1080 if upscale else 720

    # Generate session-specific seed offset for image diversity across videos
    # This ensures different sessions with similar topics get visually distinct images
    session_name = session_dir.name
    session_seed_offset = sum(ord(c) for c in session_name) * 7919  # Prime multiplier for better distribution

    print(f"\nGenerating {len(scenes)} scene images...")
    print(f"Output: {output_dir}")
    print(f"Session seed offset: {session_seed_offset} (from '{session_name}')")
    print(f"Performance: {performance} | Steps: {effective_steps}, Guidance: {effective_guidance}, Refiner: {'on' if effective_refiner else 'off'}")
    print(f"Model: {effective_model}")
    if effective_compile:
        print("Compile: torch.compile enabled for UNet")
    if effective_disable_safety:
        print("Safety checker: disabled for speed")
    print(f"Resolution: {target_width}x{target_height} (native side capped at {effective_max_side}px)")
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

        # Compute unique seed: session_offset + scene_number * 1000
        # This ensures: same session = reproducible, different sessions = different images
        scene_seed = session_seed_offset + (scene.number * 1000)

        print(f"\n[{i}/{len(scenes)}] {scene.filename}")
        print(f"  Prompt: {scene.prompt[:60]}...")
        print(f"  Seed: {scene_seed}")
        print(f"  Generating...", end=" ", flush=True)

        try:
            generator.generate_and_save(
                prompt=full_prompt,
                negative_prompt=negative_prompt,
                output_path=str(output_file),
                width=target_width,
                height=target_height,
                num_inference_steps=effective_steps,
                guidance_scale=effective_guidance,
                seed=scene_seed,
                num_candidates=1,
                save_metadata=True
            )
            print("Done!")
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
# STOCK IMAGE SOURCING
# =============================================================================

# Stock image search query mappings for common themes
STOCK_SEARCH_QUERIES = {
    "pretalk": ["peaceful entrance nature", "welcoming path light", "threshold doorway"],
    "induction": ["calm water reflection", "soft light peaceful", "gentle mist morning"],
    "deepening": ["stairway descending light", "deep cave beautiful", "tunnel light end"],
    "journey": ["mystical landscape", "ethereal scene", "dreamlike atmosphere"],
    "helm": ["light burst dramatic", "revelation sacred", "peak experience glow"],
    "integration": ["ascending light", "dawn breaking horizon", "emerging light"],
    "awakening": ["morning light peaceful", "sunrise gentle", "fresh start morning"],
}

PLATFORM_URLS = {
    "unsplash": "https://unsplash.com/s/photos/{query}?orientation=landscape",
    "pexels": "https://www.pexels.com/search/{query}/?orientation=landscape",
    "pixabay": "https://pixabay.com/images/search/{query}/?orientation=horizontal&min_width=1920",
}


def get_search_query_for_scene(scene: 'Scene', style_preset: str) -> str:
    """Generate a search query for a scene based on its name and prompt."""
    # Check for section-specific queries
    scene_lower = scene.name.lower()
    for section, queries in STOCK_SEARCH_QUERIES.items():
        if section in scene_lower:
            return queries[0]  # Return first suggested query

    # Extract key terms from prompt
    prompt = scene.prompt.lower()

    # Style-specific terms
    style_terms = {
        "garden_eden": "enchanted forest garden paradise",
        "cosmic_journey": "nebula galaxy cosmic space",
        "ancient_temple": "ancient temple mystical stone",
        "sacred_light": "divine golden light ethereal",
        "celestial_blue": "heavenly clouds celestial blue",
        "neural_network": "abstract energy light",
    }

    base_query = style_terms.get(style_preset, "mystical peaceful")

    # Add specific elements from prompt if present
    keywords = ["forest", "ocean", "mountain", "temple", "garden", "cave", "river", "sky"]
    for kw in keywords:
        if kw in prompt:
            return f"{kw} {base_query.split()[0]}"

    return base_query


def create_stock_manifest_entry(
    filename: str,
    platform: str,
    url: str,
    photographer: str,
    photographer_url: str,
    theme: str,
    original_filename: str,
    dimensions: str = "",
    has_people: bool = False,
    has_logos: bool = False
) -> dict:
    """Create a license manifest entry for a stock image."""
    license_types = {
        "unsplash": "unsplash",
        "pexels": "pexels",
        "pixabay": "pixabay",
    }

    return {
        "filename": filename,
        "source": {
            "platform": platform,
            "url": url,
            "photo_id": url.split("/")[-1] if url else "",
            "photographer": photographer,
            "photographer_url": photographer_url,
        },
        "license": {
            "type": license_types.get(platform, "unknown"),
            "commercial_use": True,
            "attribution_required": False,
            "retrieved_date": datetime.now().strftime("%Y-%m-%d"),
        },
        "content": {
            "has_people": has_people,
            "has_logos": has_logos,
            "theme": theme,
        },
        "original": {
            "filename": original_filename,
            "dimensions": dimensions,
        }
    }


def process_stock_image(
    input_path: Path,
    output_path: Path,
    target_width: int = 1920,
    target_height: int = 1080
) -> bool:
    """Process a downloaded stock image to production format."""
    try:
        # Use FFmpeg for reliable scaling and format conversion
        cmd = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-vf", f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
                   f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2",
            str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"  Error processing image: {e}")
        return False


def interactive_stock_sourcing(
    session_dir: Path,
    scenes: List['Scene'],
    style_preset: str,
    platform: str = "unsplash"
) -> List[str]:
    """
    Interactive workflow for sourcing stock images.

    Opens search URLs in browser and guides user through download/documentation.
    """
    output_dir = session_dir / "images" / "uploaded"
    cache_dir = session_dir / "images" / "stock_cache"
    manifest_path = session_dir / "images" / "license_manifest.yaml"

    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 70)
    print("STOCK IMAGE SOURCING MODE")
    print("=" * 70)
    print(f"\nSession: {session_dir.name}")
    print(f"Platform: {platform.title()}")
    print(f"Scenes to source: {len(scenes)}")
    print(f"\nOutput directory: {output_dir}")
    print(f"Cache directory: {cache_dir}")
    print("\n" + "-" * 70)

    # Load or create manifest
    manifest = {"version": "1.0", "session": session_dir.name, "images": []}
    if manifest_path.exists() and yaml:
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f) or manifest

    results = []

    for i, scene in enumerate(scenes, 1):
        print(f"\n{'=' * 70}")
        print(f"SCENE {i}/{len(scenes)}: {scene.name}")
        print(f"{'=' * 70}")
        print(f"Filename: {scene.filename}")
        print(f"Prompt: {scene.prompt[:80]}...")

        output_file = output_dir / scene.filename

        # Check if already exists
        if output_file.exists():
            print(f"\n[EXISTS] Image already exists at {output_file}")
            choice = input("Skip this scene? [Y/n]: ").strip().lower()
            if choice != 'n':
                results.append(str(output_file))
                continue

        # Generate search query
        query = get_search_query_for_scene(scene, style_preset)
        encoded_query = urllib.parse.quote(query)

        print(f"\nSuggested search: \"{query}\"")
        custom = input("Custom search query (or Enter to use suggested): ").strip()
        if custom:
            query = custom
            encoded_query = urllib.parse.quote(query)

        # Build and open search URL
        url_template = PLATFORM_URLS.get(platform, PLATFORM_URLS["unsplash"])
        search_url = url_template.format(query=encoded_query)

        print(f"\nOpening: {search_url}")
        try:
            webbrowser.open(search_url)
        except Exception:
            print(f"Could not open browser. Visit manually: {search_url}")

        print("\n" + "-" * 70)
        print("INSTRUCTIONS:")
        print("1. Find and download a suitable image (largest size)")
        print("2. Check: No recognizable faces, no logos/brands")
        print("3. Note the photographer name and image URL")
        print("-" * 70)

        # Wait for user to download
        input("\nPress Enter when you've downloaded the image...")

        # Ask for downloaded file location
        print("\nEnter the path to the downloaded image")
        print("(or drag-and-drop the file here)")
        download_path = input("> ").strip().strip("'\"")

        if not download_path:
            print("Skipping this scene...")
            continue

        download_path = Path(download_path).expanduser()

        if not download_path.exists():
            print(f"File not found: {download_path}")
            continue

        # Get metadata from user
        print("\n--- License Documentation ---")
        photo_url = input("Image page URL: ").strip()
        photographer = input("Photographer name: ").strip()
        photographer_url = input("Photographer profile URL: ").strip()

        # Content checks
        has_people = input("Does image contain people? [y/N]: ").strip().lower() == 'y'
        has_logos = input("Does image contain logos/brands? [y/N]: ").strip().lower() == 'y'

        if has_people:
            print("\n⚠️  WARNING: Images with recognizable people may have model release issues.")
            confirm = input("Are you sure you want to use this image? [y/N]: ").strip().lower()
            if confirm != 'y':
                print("Skipping this image...")
                continue

        if has_logos:
            print("\n⚠️  WARNING: Images with logos may have trademark issues.")
            confirm = input("Are you sure you want to use this image? [y/N]: ").strip().lower()
            if confirm != 'y':
                print("Skipping this image...")
                continue

        # Copy to cache
        cache_filename = f"{platform}_{Path(download_path).stem}{download_path.suffix}"
        cache_path = cache_dir / cache_filename
        print(f"\nCopying to cache: {cache_path}")
        shutil.copy2(download_path, cache_path)

        # Process to production format
        print(f"Processing to: {output_file}")
        if process_stock_image(cache_path, output_file):
            print("✓ Image processed successfully!")
            results.append(str(output_file))

            # Add to manifest
            entry = create_stock_manifest_entry(
                filename=scene.filename,
                platform=platform,
                url=photo_url,
                photographer=photographer,
                photographer_url=photographer_url,
                theme=scene.prompt[:100],
                original_filename=cache_filename,
                has_people=has_people,
                has_logos=has_logos,
            )
            manifest["images"].append(entry)
        else:
            print("✗ Failed to process image")

    # Save manifest
    if yaml and manifest["images"]:
        manifest["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
        print(f"\n✓ License manifest saved: {manifest_path}")

    print("\n" + "=" * 70)
    print(f"COMPLETE: Sourced {len(results)}/{len(scenes)} images")
    print("=" * 70)

    return results


def generate_stock_search_guide(
    session_dir: Path,
    scenes: List['Scene'],
    style_preset: str
) -> str:
    """Generate a markdown guide with search URLs for all scenes."""
    lines = [
        f"# Stock Image Search Guide",
        f"",
        f"**Session:** {session_dir.name}",
        f"**Style:** {style_preset}",
        f"**Total Scenes:** {len(scenes)}",
        f"",
        f"## Quick Links",
        f"",
    ]

    for i, scene in enumerate(scenes, 1):
        query = get_search_query_for_scene(scene, style_preset)
        encoded = urllib.parse.quote(query)

        lines.extend([
            f"### Scene {i}: {scene.name}",
            f"",
            f"**Filename:** `{scene.filename}`",
            f"**Prompt:** {scene.prompt[:100]}...",
            f"**Suggested search:** `{query}`",
            f"",
            f"| Platform | Search Link |",
            f"|----------|-------------|",
            f"| Unsplash | [Search]({PLATFORM_URLS['unsplash'].format(query=encoded)}) |",
            f"| Pexels | [Search]({PLATFORM_URLS['pexels'].format(query=encoded)}) |",
            f"| Pixabay | [Search]({PLATFORM_URLS['pixabay'].format(query=encoded)}) |",
            f"",
        ])

    lines.extend([
        f"---",
        f"",
        f"## Checklist Per Image",
        f"",
        f"- [ ] No recognizable faces",
        f"- [ ] No brand logos or text",
        f"- [ ] Landscape orientation (16:9)",
        f"- [ ] High resolution (1920x1080+)",
        f"- [ ] Mood matches scene purpose",
        f"",
        f"## After Download",
        f"",
        f"1. Save original to `images/stock_cache/`",
        f"2. Process with FFmpeg:",
        f"   ```bash",
        f"   ffmpeg -i input.jpg -vf \"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2\" images/uploaded/scene_XX.png",
        f"   ```",
        f"3. Add entry to `images/license_manifest.yaml`",
        f"4. Run: `python3 scripts/utilities/validate_image_licenses.py {session_dir}/`",
    ])

    content = "\n".join(lines)

    # Write guide
    guide_path = session_dir / "stock-image-guide.md"
    guide_path.write_text(content)
    print(f"Stock image guide saved to: {guide_path}")

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
  # Generate SDXL images (default)
  python3 generate_scene_images.py sessions/my-session/

  # Generate with upscaling
  python3 generate_scene_images.py sessions/my-session/ --upscale

  # Generate Midjourney prompts only
  python3 generate_scene_images.py sessions/my-session/ --midjourney-only

  # Generate both SD images and Midjourney prompts
  python3 generate_scene_images.py sessions/my-session/ --with-prompts

  # Custom style and steps
  python3 generate_scene_images.py sessions/my-session/ --style cosmic_journey --steps 32 --guidance 6.5

  # Fast renders (turbo model, 4 steps)
  python3 generate_scene_images.py sessions/my-session/ --performance turbo --steps 4 --guidance 0 --no-refiner --no-upscale
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
        choices=["sd", "sdxl", "midjourney", "stock", "pil"],
        default="sd",
        help="Generation method: sd/sdxl (Stable Diffusion XL), midjourney (prompts only), stock (source from Unsplash/Pexels/Pixabay), pil (procedural)"
    )
    parser.add_argument(
        "--platform",
        choices=["unsplash", "pexels", "pixabay"],
        default="unsplash",
        help="Stock image platform to use (default: unsplash)"
    )
    parser.add_argument(
        "--stock-guide",
        action="store_true",
        help="Generate stock image search guide markdown (non-interactive)"
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
        "--performance",
        choices=list(PERFORMANCE_PRESETS.keys()),
        default="balanced",
        help="Speed/quality preset: quality | balanced | speed | turbo"
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
        default=None,
        help="Override preset inference steps (default: preset-defined)"
    )
    parser.add_argument(
        "--guidance",
        type=float,
        default=None,
        help="Override preset guidance scale (default: preset-defined)"
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
    parser.add_argument(
        "--no-refiner",
        action="store_true",
        help="Disable SDXL refiner pass (faster, slightly softer details)"
    )
    parser.add_argument(
        "--max-gen-side",
        type=int,
        default=None,
        help="Maximum side length to generate natively before upscaling (default: preset-defined)"
    )
    parser.add_argument(
        "--compile-unet",
        action="store_true",
        help="Compile UNet for faster inference (PyTorch 2+, CUDA only)"
    )
    parser.add_argument(
        "--disable-safety-checker",
        action="store_true",
        help="Skip NSFW safety checker (faster; disable only if you control prompts)"
    )
    parser.add_argument(
        "--no-vae-tiling",
        action="store_true",
        help="Disable VAE tiling (uses more VRAM; only needed if you see tiling artifacts)"
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

    # Check for local SDXL model if not provided
    model_path = args.model
    if not model_path:
        candidates = [
            Path.home() / "sd-webui" / "models" / "Stable-diffusion" / "sd_xl_base_1.0.safetensors",
            Path.home() / "sd-webui" / "models" / "Stable-diffusion" / "sdxl_base_1.0.safetensors"
        ]
        for cand in candidates:
            if cand.exists():
                model_path = str(cand)
                print(f"Found local SDXL model: {model_path}")
                break

    # Generate based on method
    if args.method == "midjourney":
        generate_midjourney_prompts(session_dir, scenes, style)
        print("\nMidjourney prompts generated. Create images in Midjourney and place in images/uploaded/")

    elif args.method in ["sd", "sdxl"]:
        results = generate_sd_scenes(
            session_dir=session_dir,
            scenes=scenes,
            style_preset=style,
            steps=args.steps,
            guidance_scale=args.guidance,
            upscale=upscale,
            force=args.force,
            model_path=model_path,
            use_refiner=not args.no_refiner,
            max_generation_side=args.max_gen_side,
            performance=args.performance,
            compile_unet=args.compile_unet,
            disable_safety_checker=args.disable_safety_checker,
            enable_vae_tiling=not args.no_vae_tiling
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

    elif args.method == "stock":
        if args.stock_guide:
            # Non-interactive: generate search guide markdown
            generate_stock_search_guide(session_dir, scenes, style)
            print("\nStock image search guide generated.")
            print("Use the guide to manually source images, then run validation.")
        else:
            # Interactive: walk through each scene
            results = interactive_stock_sourcing(
                session_dir=session_dir,
                scenes=scenes,
                style_preset=style,
                platform=args.platform
            )

            if results:
                print(f"\nSuccess! Sourced {len(results)} images")
                print("\nNext steps:")
                print(f"  1. Run: python3 scripts/utilities/validate_image_licenses.py {session_dir}/")
                print("  2. Review images in images/uploaded/")
                sys.exit(0)
            else:
                print("\nNo images sourced")
                sys.exit(1)

    elif args.method == "pil":
        # PIL procedural generation - fast fallback using generate_video_images.py
        print("Using PIL procedural image generation...")

        # Add project root to path for imports
        project_root = Path(__file__).resolve().parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        # Import the video images generator
        try:
            from scripts.core.generate_video_images import (
                generate_scene_background,
                IMAGE_SPECS,
                ImageType,
                PALETTES,
            )
        except ImportError as e:
            print(f"ERROR: Could not import generate_video_images module: {e}")
            print("Ensure scripts/core/generate_video_images.py exists")
            sys.exit(1)

        # Create output directory
        output_dir = session_dir / "images" / "uploaded"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load manifest for context
        manifest = None
        manifest_path = session_dir / "manifest.yaml"
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = yaml.safe_load(f)

        # Detect palette from session name or manifest
        palette_name = "sacred_light"  # Default
        session_name = session_dir.name.lower()
        if "cosmic" in session_name or "space" in session_name or "star" in session_name:
            palette_name = "cosmic_journey"
        elif "garden" in session_name or "eden" in session_name or "nature" in session_name:
            palette_name = "garden_eden"
        elif "temple" in session_name or "ancient" in session_name:
            palette_name = "ancient_temple"
        elif "neural" in session_name or "mind" in session_name:
            palette_name = "neural_network"
        elif "fire" in session_name or "forge" in session_name or "volcanic" in session_name:
            palette_name = "volcanic_forge"
        elif "elven" in session_name or "forest" in session_name or "woodland" in session_name:
            palette_name = "garden_eden"
        palette = PALETTES.get(palette_name, PALETTES["sacred_light"])
        print(f"Using palette: {palette_name}")

        # Generate scene backgrounds (5 images for typical video)
        spec = IMAGE_SPECS[ImageType.SCENE_BACKGROUND]
        generated_count = 0

        for i in range(1, 6):
            try:
                output_path = generate_scene_background(
                    session_dir, palette, spec, i, None
                )
                if output_path and output_path.exists():
                    # Copy to images/uploaded/ for video assembly
                    dest_path = output_dir / f"scene_{i:02d}.png"
                    import shutil
                    shutil.copy(output_path, dest_path)
                    generated_count += 1
                    print(f"  Generated: {dest_path.name}")
            except Exception as e:
                print(f"  Warning: Scene {i} failed: {e}")

        if generated_count > 0:
            print(f"\nGenerated {generated_count} scene images in {output_dir}")
            sys.exit(0)
        else:
            print("\nNo images generated")
            sys.exit(1)


if __name__ == "__main__":
    main()
