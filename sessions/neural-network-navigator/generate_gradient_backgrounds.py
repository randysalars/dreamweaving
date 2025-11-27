#!/usr/bin/env python3
"""
Generate gradient background images for Neural Network Navigator video
Creates vertical gradient backgrounds that layer behind the SDXL images
"""

from PIL import Image, ImageDraw
import os

# Gradient specifications from master_timeline.json
GRADIENTS = [
    {
        "name": "01_opening",
        "duration": 150,
        "start_time": 0,
        "color_start": "#1a0033",
        "color_end": "#330066",
        "description": "Deep purple gradient"
    },
    {
        "name": "02_descent",
        "duration": 270,
        "start_time": 150,
        "color_start": "#220044",
        "color_end": "#110033",
        "description": "Darkening purple, descent feeling"
    },
    {
        "name": "03_neural_garden",
        "duration": 270,
        "start_time": 420,
        "color_start": "#1a0044",
        "color_end": "#2d0066",
        "description": "Rich purple with depth"
    },
    {
        "name": "04_pathfinder",
        "duration": 270,
        "start_time": 690,
        "color_start": "#0f0044",
        "color_end": "#1f0055",
        "description": "Deep indigo with richness"
    },
    {
        "name": "05_weaver",
        "duration": 270,
        "start_time": 960,
        "color_start": "#1a0055",
        "color_end": "#2d0077",
        "description": "Rich violet, building toward peak"
    },
    {
        "name": "06_gamma_burst",
        "duration": 3,
        "start_time": 1125,
        "color_start": "#ffffff",
        "color_end": "#ffffee",
        "description": "BRIGHT WHITE for gamma flash"
    },
    {
        "name": "07_consolidation",
        "duration": 210,
        "start_time": 1230,
        "color_start": "#1f0055",
        "color_end": "#2a0066",
        "description": "Stabilizing purple, lighter than peak"
    },
    {
        "name": "08_return",
        "duration": 240,
        "start_time": 1440,
        "color_start": "#330066",
        "color_end": "#4d79cc",
        "description": "Purple to soft blue - morning light"
    }
]

WIDTH = 1920
HEIGHT = 1080

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_vertical_gradient(color_start_hex, color_end_hex, width, height):
    """Create a vertical gradient image"""
    # Create new image
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # Convert hex colors to RGB
    color_start = hex_to_rgb(color_start_hex)
    color_end = hex_to_rgb(color_end_hex)

    # Generate gradient
    for y in range(height):
        # Calculate color at this y position
        ratio = y / height

        r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
        b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)

        # Draw horizontal line
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    return img

def main():
    print("=" * 70)
    print("NEURAL NETWORK NAVIGATOR - Gradient Background Generation")
    print("=" * 70)
    print(f"\nGenerating {len(GRADIENTS)} gradient backgrounds...")
    print(f"Resolution: {WIDTH}x{HEIGHT}\n")

    output_dir = "gradients"
    os.makedirs(output_dir, exist_ok=True)

    for gradient_spec in GRADIENTS:
        print(f"Generating {gradient_spec['name']}...")
        print(f"  {gradient_spec['description']}")
        print(f"  Colors: {gradient_spec['color_start']} → {gradient_spec['color_end']}")

        try:
            # Create gradient
            img = create_vertical_gradient(
                gradient_spec['color_start'],
                gradient_spec['color_end'],
                WIDTH,
                HEIGHT
            )

            # Save
            output_path = f"{output_dir}/gradient_{gradient_spec['name']}.png"
            img.save(output_path, 'PNG')

            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"  ✓ Saved: {output_path} ({file_size:.2f} MB)\n")

        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            continue

    print("=" * 70)
    print("✓ Gradient background generation complete!")
    print("=" * 70)
    print(f"\nGenerated {len(GRADIENTS)} gradient backgrounds in {output_dir}/ directory")
    print("\nNext: Composite final video (once images complete)")

    return 0

if __name__ == '__main__':
    exit(main())
