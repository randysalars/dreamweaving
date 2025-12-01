#!/usr/bin/env python3
"""
Midjourney Prompt Generator for Dreamweaving

Generates optimized Midjourney prompts for:
- Session visualizations (journey images)
- YouTube thumbnails

Based on session manifest and script content.

Usage:
    python3 scripts/ai/prompt_generator.py sessions/{session}
    python3 scripts/ai/prompt_generator.py sessions/{session} --thumbnail-only
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import re


# Visual style presets for different journey types
STYLE_PRESETS = {
    "spiritual": {
        "base_style": "ethereal, mystical, sacred geometry, divine light rays",
        "color_palette": "golden, soft purple, celestial blue",
        "mood": "transcendent, peaceful, awe-inspiring",
        "lighting": "volumetric god rays, soft ambient glow",
    },
    "nature": {
        "base_style": "organic, lush, flowing, natural beauty",
        "color_palette": "forest green, earth tones, golden sunlight",
        "mood": "serene, grounding, harmonious",
        "lighting": "dappled sunlight, soft shadows, golden hour",
    },
    "cosmic": {
        "base_style": "vast, infinite, stellar, nebulae",
        "color_palette": "deep purple, cosmic blue, stardust silver",
        "mood": "expansive, wonder, infinite possibility",
        "lighting": "starlight, aurora, cosmic glow",
    },
    "underwater": {
        "base_style": "fluid, bioluminescent, deep ocean",
        "color_palette": "deep blue, aquamarine, phosphorescent",
        "mood": "weightless, mysterious, transformative",
        "lighting": "caustic patterns, bioluminescence, filtered sunlight",
    },
    "abstract": {
        "base_style": "flowing forms, energy patterns, consciousness",
        "color_palette": "prismatic, shifting gradients",
        "mood": "meditative, hypnotic, transformative",
        "lighting": "inner glow, radiant energy",
    },
    "dreamscape": {
        "base_style": "surreal, flowing, impossible geometry",
        "color_palette": "soft pastels, ethereal whites, dream haze",
        "mood": "peaceful, floating, safe, expansive",
        "lighting": "soft diffused light, dreamy atmosphere",
    },
}

# Thumbnail-specific elements
THUMBNAIL_ELEMENTS = {
    "composition": "centered focal point, dramatic composition, eye-catching",
    "style": "professional, high contrast, readable at small size",
    "text_space": "negative space on left or right for text overlay",
}


def load_manifest(session_path: Path) -> Dict:
    """Load session manifest."""
    manifest_path = session_path / "manifest.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest.yaml found in {session_path}")

    with open(manifest_path, 'r') as f:
        return yaml.safe_load(f)


def extract_key_imagery(ssml_content: str) -> List[str]:
    """Extract key visual concepts from SSML script."""
    # Remove SSML tags for analysis
    text = re.sub(r'<[^>]+>', '', ssml_content)

    # Look for visual keywords and phrases
    visual_patterns = [
        r'imagine\s+(?:a\s+)?([^.!?]+)',
        r'see\s+(?:yourself\s+)?(?:in\s+)?(?:a\s+)?([^.!?]+)',
        r'picture\s+(?:a\s+)?([^.!?]+)',
        r'visualize\s+(?:a\s+)?([^.!?]+)',
        r'surrounded by\s+([^.!?]+)',
        r'floating\s+(?:in|through)\s+([^.!?]+)',
        r'entering\s+(?:a\s+)?([^.!?]+)',
        r'discover\s+(?:a\s+)?([^.!?]+)',
    ]

    imagery = []
    for pattern in visual_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        imagery.extend(matches)

    # Clean and deduplicate
    cleaned = []
    for item in imagery:
        item = item.strip()
        if len(item) > 10 and len(item) < 200:  # Filter noise
            cleaned.append(item)

    return list(dict.fromkeys(cleaned))[:10]  # Top 10 unique


def determine_style(manifest: Dict) -> str:
    """Determine visual style from manifest."""
    # Check explicit style setting
    if 'visual_style' in manifest:
        return manifest['visual_style']

    # Infer from theme/title
    theme = manifest.get('theme', '').lower()
    title = manifest.get('title', '').lower()
    combined = f"{theme} {title}"

    if any(word in combined for word in ['space', 'star', 'cosmos', 'galaxy', 'universe']):
        return 'cosmic'
    elif any(word in combined for word in ['ocean', 'water', 'sea', 'underwater']):
        return 'underwater'
    elif any(word in combined for word in ['forest', 'garden', 'nature', 'earth', 'tree']):
        return 'nature'
    elif any(word in combined for word in ['spirit', 'soul', 'divine', 'sacred', 'temple']):
        return 'spiritual'
    elif any(word in combined for word in ['dream', 'sleep', 'rest', 'relax']):
        return 'dreamscape'
    else:
        return 'abstract'


def generate_scene_prompts(
    manifest: Dict,
    imagery: List[str],
    style: str,
    num_scenes: int = 5
) -> List[Dict]:
    """Generate prompts for scene images."""
    style_preset = STYLE_PRESETS.get(style, STYLE_PRESETS['abstract'])

    scenes = []
    title = manifest.get('title', 'Hypnotic Journey')

    # Opening scene
    scenes.append({
        "scene": "opening",
        "description": f"Beginning of {title}",
        "prompt": generate_single_prompt(
            subject="gateway or threshold, beginning of a journey",
            style_preset=style_preset,
            mood="inviting, anticipation, safe entry",
            additional=imagery[0] if imagery else "",
        )
    })

    # Journey scenes (from extracted imagery)
    for i, img in enumerate(imagery[1:num_scenes-1], 1):
        scenes.append({
            "scene": f"journey_{i}",
            "description": img[:100],
            "prompt": generate_single_prompt(
                subject=img,
                style_preset=style_preset,
                mood=style_preset['mood'],
            )
        })

    # Closing scene
    scenes.append({
        "scene": "closing",
        "description": f"Completion of {title}",
        "prompt": generate_single_prompt(
            subject="peaceful return, integration, wholeness",
            style_preset=style_preset,
            mood="complete, peaceful, integrated, grounded",
        )
    })

    return scenes


def generate_single_prompt(
    subject: str,
    style_preset: Dict,
    mood: str = "",
    additional: str = "",
    aspect_ratio: str = "16:9",
) -> str:
    """Generate a single Midjourney prompt."""
    parts = [
        subject.strip(),
        style_preset['base_style'],
        f"color palette: {style_preset['color_palette']}",
        f"mood: {mood or style_preset['mood']}",
        f"lighting: {style_preset['lighting']}",
    ]

    if additional:
        parts.insert(1, additional)

    # Add quality parameters
    parts.extend([
        "highly detailed",
        "professional quality",
        "8k resolution",
    ])

    # Midjourney parameters
    params = f"--ar {aspect_ratio} --v 6 --style raw --s 250"

    prompt = ", ".join(parts)
    return f"{prompt} {params}"


def generate_thumbnail_prompt(manifest: Dict, style: str) -> Dict:
    """Generate YouTube thumbnail prompt."""
    style_preset = STYLE_PRESETS.get(style, STYLE_PRESETS['abstract'])
    title = manifest.get('title', 'Hypnotic Journey')

    # Extract core theme for thumbnail
    theme_words = title.lower().replace('-', ' ').split()
    core_theme = ' '.join(theme_words[:3])

    prompt_parts = [
        f"dramatic representation of {core_theme}",
        style_preset['base_style'],
        THUMBNAIL_ELEMENTS['composition'],
        THUMBNAIL_ELEMENTS['style'],
        THUMBNAIL_ELEMENTS['text_space'],
        f"color palette: {style_preset['color_palette']}",
        "cinematic, impactful, mysterious",
        "professional youtube thumbnail quality",
    ]

    params = "--ar 16:9 --v 6 --style raw --s 500"

    return {
        "scene": "thumbnail",
        "description": f"YouTube thumbnail for {title}",
        "prompt": f"{', '.join(prompt_parts)} {params}",
        "notes": [
            "Create with text space for title overlay",
            "Should be eye-catching at small size",
            "Consider A/B testing variations",
        ]
    }


def save_prompts(
    session_path: Path,
    scene_prompts: List[Dict],
    thumbnail_prompt: Dict,
    style: str,
    manifest: Dict,
) -> Path:
    """Save prompts to session directory."""
    output = {
        "session": manifest.get('title', session_path.name),
        "style": style,
        "style_details": STYLE_PRESETS.get(style, {}),
        "thumbnail": thumbnail_prompt,
        "scenes": scene_prompts,
        "instructions": {
            "workflow": [
                "1. Generate images using Midjourney with these prompts",
                "2. Download and save to images_uploaded/ folder",
                "3. Name files: thumbnail.png, scene_01.png, scene_02.png, etc.",
                "4. Run video assembly after images are ready",
            ],
            "tips": [
                "Regenerate if initial results don't match the mood",
                "Use --chaos 20-40 for more variation if needed",
                "Upscale final selections to maximum quality",
            ]
        }
    }

    # Save to working_files
    output_path = session_path / 'working_files' / 'midjourney_prompts.yaml'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return output_path


def main():
    parser = argparse.ArgumentParser(description='Generate Midjourney prompts')
    parser.add_argument('session_path', help='Path to session directory')
    parser.add_argument('--thumbnail-only', action='store_true',
                       help='Generate only thumbnail prompt')
    parser.add_argument('--scenes', type=int, default=5,
                       help='Number of scene prompts to generate')
    parser.add_argument('--style', choices=list(STYLE_PRESETS.keys()),
                       help='Override visual style')
    args = parser.parse_args()

    session_path = Path(args.session_path)

    print(f"Generating Midjourney prompts for {session_path.name}...")

    # Load manifest
    manifest = load_manifest(session_path)

    # Determine style
    style = args.style or determine_style(manifest)
    print(f"  Visual style: {style}")

    # Load SSML for imagery extraction
    imagery = []
    ssml_paths = [
        session_path / 'working_files' / 'script.ssml',
        session_path / 'script.ssml',
    ]
    for ssml_path in ssml_paths:
        if ssml_path.exists():
            with open(ssml_path, 'r') as f:
                imagery = extract_key_imagery(f.read())
            print(f"  Extracted {len(imagery)} visual concepts from script")
            break

    # Generate prompts
    thumbnail_prompt = generate_thumbnail_prompt(manifest, style)

    if args.thumbnail_only:
        scene_prompts = []
    else:
        scene_prompts = generate_scene_prompts(manifest, imagery, style, args.scenes)

    # Save
    output_path = save_prompts(session_path, scene_prompts, thumbnail_prompt, style, manifest)

    print(f"\n  Saved: {output_path}")
    print(f"\n--- THUMBNAIL PROMPT ---")
    print(thumbnail_prompt['prompt'])

    if scene_prompts:
        print(f"\n--- SCENE PROMPTS ({len(scene_prompts)}) ---")
        for scene in scene_prompts:
            print(f"\n[{scene['scene']}]")
            print(scene['prompt'][:200] + "..." if len(scene['prompt']) > 200 else scene['prompt'])


if __name__ == "__main__":
    main()
