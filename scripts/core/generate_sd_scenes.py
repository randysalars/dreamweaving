#!/usr/bin/env python3
"""
Stable Diffusion Scene Generator for Dreamweaver Sessions

Generates high-quality scene images using local Stable Diffusion API.
Reads scene descriptions from manifest.yaml or midjourney-prompts.md.

Usage:
    # Generate scenes for a session
    python3 scripts/core/generate_sd_scenes.py sessions/neural-network-navigator/

    # With upscaling to 1920x1080
    python3 scripts/core/generate_sd_scenes.py sessions/neural-network-navigator/ --upscale

    # Only specific scenes
    python3 scripts/core/generate_sd_scenes.py sessions/neural-network-navigator/ --scenes 1,3,5
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Add scripts/core to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from sd_api_client import SDAPIClient
except ImportError:
    print("Error: Could not import sd_api_client")
    print("Make sure sd_api_client.py is in the same directory")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("Warning: PyYAML not installed, manifest parsing limited")
    yaml = None

try:
    from PIL import Image
except ImportError:
    print("Warning: Pillow not installed, upscaling disabled")
    Image = None


def parse_midjourney_prompts(prompts_file: Path) -> List[Tuple[str, str]]:
    """
    Parse Midjourney prompts file to extract scene descriptions.

    Returns:
        List of (scene_name, prompt_text) tuples
    """
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
        # Clean up any trailing commas
        prompt = prompt.rstrip(',').strip()

        scene_name = f"scene_{int(num):02d}_{title.lower().replace(' ', '_').replace('/', '_')}"
        scene_name = re.sub(r'[^a-z0-9_]', '', scene_name)

        scenes.append((scene_name, prompt))

    return scenes


def parse_manifest_sections(manifest_file: Path) -> List[Tuple[str, str]]:
    """
    Parse manifest.yaml to extract section descriptions for scene generation.

    Returns:
        List of (section_name, description) tuples
    """
    if yaml is None or not manifest_file.exists():
        return []

    with open(manifest_file) as f:
        manifest = yaml.safe_load(f)

    scenes = []
    sections = manifest.get('sections', [])

    for i, section in enumerate(sections, 1):
        name = section.get('name', f'Section {i}')
        # Use visual_theme if available, else construct from name and mood
        visual = section.get('visual_theme', '')
        mood = section.get('mood', '')
        journey = section.get('journey', '')

        # Build a descriptive prompt
        description_parts = []
        if visual:
            description_parts.append(visual)
        if mood:
            description_parts.append(f"{mood} atmosphere")
        if journey:
            # Take first sentence of journey
            first_sentence = journey.split('.')[0]
            if len(first_sentence) < 200:
                description_parts.append(first_sentence)

        if description_parts:
            description = ', '.join(description_parts)
        else:
            description = f"Abstract mystical scene for {name}"

        scene_name = f"scene_{i:02d}_{name.lower().replace(' ', '_')}"
        scene_name = re.sub(r'[^a-z0-9_]', '', scene_name)

        scenes.append((scene_name, description))

    return scenes


def upscale_image(input_path: Path, output_path: Path, target_width: int = 1920) -> bool:
    """
    Upscale an image to target resolution while maintaining aspect ratio.

    Uses high-quality Lanczos resampling.
    """
    if Image is None:
        print("Warning: Pillow not available for upscaling")
        return False

    try:
        img = Image.open(input_path)
        original_width, original_height = img.size

        # Calculate new dimensions
        aspect_ratio = original_height / original_width
        new_width = target_width
        new_height = int(target_width * aspect_ratio)

        # Upscale with high-quality resampling
        upscaled = img.resize((new_width, new_height), Image.LANCZOS)
        upscaled.save(output_path, quality=95)

        print(f"  Upscaled: {original_width}x{original_height} -> {new_width}x{new_height}")
        return True

    except Exception as e:
        print(f"  Upscale error: {e}")
        return False


def generate_session_scenes(
    session_dir: Path,
    client: SDAPIClient,
    style_preset: str = None,
    upscale: bool = False,
    scene_indices: List[int] = None,
    steps: int = 8,
    force: bool = False
) -> List[str]:
    """
    Generate scene images for a Dreamweaver session.

    Args:
        session_dir: Path to session directory
        client: SDAPIClient instance
        style_preset: Style preset to apply (auto-detected if None)
        upscale: Whether to upscale to 1920x1080
        scene_indices: Only generate these scene numbers (1-indexed)
        steps: Sampling steps (more = better quality, slower)
        force: Regenerate even if images exist

    Returns:
        List of generated image paths
    """
    session_dir = Path(session_dir)

    # Try to get scenes from midjourney prompts first
    prompts_file = session_dir / "midjourney-prompts.md"
    manifest_file = session_dir / "manifest.yaml"

    scenes = parse_midjourney_prompts(prompts_file)
    source = "midjourney-prompts.md"

    if not scenes:
        scenes = parse_manifest_sections(manifest_file)
        source = "manifest.yaml"

    if not scenes:
        print(f"Error: No scene descriptions found in {session_dir}")
        print("Expected either midjourney-prompts.md or manifest.yaml with sections")
        return []

    print(f"Found {len(scenes)} scenes from {source}")

    # Filter to requested scenes if specified
    if scene_indices:
        scenes = [(name, prompt) for i, (name, prompt) in enumerate(scenes, 1)
                  if i in scene_indices]
        print(f"Filtering to {len(scenes)} requested scenes")

    # Auto-detect style preset from session name
    if style_preset is None:
        session_name = session_dir.name.lower()
        if 'neural' in session_name or 'network' in session_name:
            style_preset = "neural_network"
        elif 'eden' in session_name or 'garden' in session_name:
            style_preset = "garden_eden"
        elif 'cosmic' in session_name or 'space' in session_name:
            style_preset = "cosmic_journey"
        elif 'sacred' in session_name or 'divine' in session_name:
            style_preset = "sacred_light"
        else:
            style_preset = "neural_network"  # Default
        print(f"Auto-detected style preset: {style_preset}")

    # Output directories
    sd_output_dir = session_dir / "images" / "sd_generated"
    sd_output_dir.mkdir(parents=True, exist_ok=True)

    if upscale:
        upscaled_dir = session_dir / "images" / "uploaded"
        upscaled_dir.mkdir(parents=True, exist_ok=True)

    results = []

    print(f"\nGenerating {len(scenes)} scene images...")
    print(f"Output: {sd_output_dir}")
    print(f"Steps: {steps}, Style: {style_preset}")
    print("=" * 60)

    for i, (scene_name, prompt) in enumerate(scenes, 1):
        output_file = sd_output_dir / f"{scene_name}.png"

        # Skip if exists and not forcing
        if output_file.exists() and not force:
            print(f"\n[{i}/{len(scenes)}] {scene_name}: exists, skipping")
            results.append(str(output_file))
            continue

        print(f"\n[{i}/{len(scenes)}] {scene_name}")
        print(f"  Prompt: {prompt[:80]}...")

        # Generate at 768x432 (16:9) for CPU efficiency
        result = client.generate_image(
            prompt=prompt,
            output_path=str(output_file),
            style_preset=style_preset,
            width=768,
            height=432,
            steps=steps,
            cfg_scale=7.5,
            seed=i * 1000
        )

        if result:
            results.append(result)

            # Upscale if requested
            if upscale:
                upscaled_file = upscaled_dir / f"{scene_name}.png"
                print("  Upscaling to 1920x1080...")
                upscale_image(Path(result), upscaled_file, target_width=1920)

    print("\n" + "=" * 60)
    print(f"Generated {len(results)}/{len(scenes)} images")

    if upscale:
        print(f"Upscaled images in: {upscaled_dir}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate scene images using Stable Diffusion API"
    )
    parser.add_argument(
        "session_dir",
        help="Path to session directory"
    )
    parser.add_argument(
        "--style",
        choices=["neural_network", "sacred_light", "cosmic_journey", "garden_eden"],
        help="Style preset (auto-detected from session name if not specified)"
    )
    parser.add_argument(
        "--upscale",
        action="store_true",
        help="Upscale generated images to 1920x1080"
    )
    parser.add_argument(
        "--scenes",
        type=str,
        help="Comma-separated list of scene numbers to generate (e.g., '1,3,5')"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=8,
        help="Sampling steps (default: 8 for CPU, use 20+ for GPU)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even if images exist"
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://127.0.0.1:7860",
        help="URL of Stable Diffusion API"
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for server to become available"
    )

    args = parser.parse_args()

    session_dir = Path(args.session_dir)
    if not session_dir.exists():
        print(f"Error: Session directory not found: {session_dir}")
        sys.exit(1)

    # Parse scene indices if specified
    scene_indices = None
    if args.scenes:
        try:
            scene_indices = [int(x.strip()) for x in args.scenes.split(',')]
        except ValueError:
            print("Error: --scenes must be comma-separated integers")
            sys.exit(1)

    # Initialize client
    client = SDAPIClient(api_url=args.api_url)

    # Check if server is available
    if not client.is_available():
        if args.wait:
            print(f"Waiting for server at {args.api_url}...")
            if not client.wait_for_server(max_wait=120):
                print("Error: Server did not become available")
                print("Start the server with: cd ~/sd-webui && ./webui.sh")
                sys.exit(1)
        else:
            print(f"Error: SD API server not available at {args.api_url}")
            print("Start the server with: cd ~/sd-webui && ./webui.sh")
            print("Or use --wait to wait for it to start")
            sys.exit(1)

    print(f"Connected to SD API at {args.api_url}")
    model = client.get_current_model()
    if model:
        print(f"Current model: {model}")

    # Generate scenes
    results = generate_session_scenes(
        session_dir=session_dir,
        client=client,
        style_preset=args.style,
        upscale=args.upscale,
        scene_indices=scene_indices,
        steps=args.steps,
        force=args.force
    )

    if results:
        print(f"\nSuccess! Generated {len(results)} images")
        sys.exit(0)
    else:
        print("\nNo images generated")
        sys.exit(1)


if __name__ == "__main__":
    main()
