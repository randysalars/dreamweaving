#!/usr/bin/env python3
"""
Create YouTube Thumbnail for Neural Network Navigator
Eye-catching design optimized for YouTube discovery
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os

def create_thumbnail():
    """Create a professional YouTube thumbnail"""

    # YouTube thumbnail size
    width = 1280
    height = 720

    # Create base image with dark gradient background
    img = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Create gradient background (deep blue to purple to black)
    for y in range(height):
        # Calculate gradient colors
        ratio = y / height

        # Deep space blue to purple gradient
        r = int(20 + (60 - 20) * ratio)
        g = int(10 + (20 - 10) * ratio)
        b = int(60 + (80 - 60) * ratio)

        draw.rectangle([(0, y), (width, y+1)], fill=(r, g, b))

    # Load one of the session images as background element
    try:
        # Try to use the neural garden scene as a subtle background
        scene_img = Image.open('images/scene_03_neural_garden_FINAL.png')

        # Resize and crop to fit thumbnail
        scene_img = scene_img.resize((width, height), Image.Resampling.LANCZOS)

        # Make it semi-transparent and blurred for background effect
        scene_img = scene_img.filter(ImageFilter.GaussianBlur(radius=15))
        enhancer = ImageEnhance.Brightness(scene_img)
        scene_img = enhancer.enhance(0.3)  # Darken significantly

        # Blend with gradient background
        img = Image.blend(img, scene_img, alpha=0.4)
        draw = ImageDraw.Draw(img)

    except Exception as e:
        print(f"Note: Could not load background image: {e}")
        print("Using gradient background only")

    # Add glowing neural network nodes effect
    # Create overlay for glow effects
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Draw neural network nodes (circles with glow)
    nodes = [
        (200, 150, 40, (100, 200, 255, 180)),  # Top left - blue
        (1000, 200, 35, (150, 100, 255, 160)), # Top right - purple
        (600, 400, 45, (255, 150, 200, 180)),  # Center - pink
        (300, 550, 30, (100, 255, 200, 160)),  # Bottom left - cyan
        (950, 500, 38, (200, 150, 255, 170)),  # Bottom right - lavender
    ]

    for x, y, size, color in nodes:
        # Outer glow
        for i in range(size, 0, -2):
            alpha = int(color[3] * (i / size) * 0.3)
            overlay_draw.ellipse(
                [(x - i, y - i), (x + i, y + i)],
                fill=(*color[:3], alpha)
            )
        # Core
        overlay_draw.ellipse(
            [(x - size//3, y - size//3), (x + size//3, y + size//3)],
            fill=color
        )

    # Draw connecting lines between nodes
    for i in range(len(nodes) - 1):
        x1, y1 = nodes[i][:2]
        x2, y2 = nodes[i + 1][:2]
        overlay_draw.line([(x1, y1), (x2, y2)], fill=(150, 200, 255, 80), width=2)

    # Merge overlay
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img)

    # Try to load fonts, fall back to default if not available
    try:
        # Large bold font for main title
        title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 90)
        subtitle_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 45)
        badge_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 35)
    except:
        print("Note: Using default fonts")
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        badge_font = ImageFont.load_default()

    # Add text with shadow/glow effect
    title_text = "NEURAL NETWORK"
    subtitle_text = "NAVIGATOR"

    # Calculate text positions (centered)
    # Title
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = 200

    # Subtitle
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title_y + 100

    # Draw text shadow (multiple layers for glow effect)
    for offset in range(8, 0, -1):
        shadow_alpha = int(255 * (offset / 8) * 0.6)
        # Create temporary image for shadow
        shadow_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)

        # Title shadow
        shadow_draw.text(
            (title_x, title_y),
            title_text,
            font=title_font,
            fill=(100, 200, 255, shadow_alpha)
        )

        # Subtitle shadow
        shadow_draw.text(
            (subtitle_x, subtitle_y),
            subtitle_text,
            font=subtitle_font,
            fill=(200, 150, 255, shadow_alpha)
        )

        # Blur and merge
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=offset//2))
        img = Image.alpha_composite(img.convert('RGBA'), shadow_layer).convert('RGB')
        draw = ImageDraw.Draw(img)

    # Draw main text (bright white with slight color tint)
    draw.text(
        (title_x, title_y),
        title_text,
        font=title_font,
        fill=(255, 255, 255)
    )

    draw.text(
        (subtitle_x, subtitle_y),
        subtitle_text,
        font=subtitle_font,
        fill=(220, 240, 255)
    )

    # Add tagline
    tagline = "Guided Hypnosis • Theta Waves • Deep Learning"
    tagline_bbox = draw.textbbox((0, 0), tagline, font=badge_font)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    tagline_x = (width - tagline_width) // 2
    tagline_y = subtitle_y + 80

    # Tagline background box
    box_padding = 20
    box_coords = [
        (tagline_x - box_padding, tagline_y - 10),
        (tagline_x + tagline_width + box_padding, tagline_y + 50)
    ]
    draw.rounded_rectangle(
        box_coords,
        radius=10,
        fill=(40, 20, 80, 200),
        outline=(150, 200, 255),
        width=2
    )

    draw.text(
        (tagline_x, tagline_y),
        tagline,
        font=badge_font,
        fill=(200, 230, 255)
    )

    # Add duration badge in corner
    duration_text = "23:41"
    duration_x = width - 150
    duration_y = height - 80

    # Duration background
    draw.rounded_rectangle(
        [(duration_x - 20, duration_y - 10), (duration_x + 120, duration_y + 50)],
        radius=8,
        fill=(0, 0, 0, 220),
        outline=(255, 255, 255),
        width=2
    )

    draw.text(
        (duration_x, duration_y),
        duration_text,
        font=badge_font,
        fill=(255, 255, 255)
    )

    # Add "40Hz GAMMA" badge (highlighting unique feature)
    gamma_text = "40Hz GAMMA"
    gamma_x = 50
    gamma_y = height - 80

    # Gamma badge with bright accent
    draw.rounded_rectangle(
        [(gamma_x - 15, gamma_y - 10), (gamma_x + 180, gamma_y + 50)],
        radius=8,
        fill=(120, 0, 255, 230),
        outline=(255, 200, 0),
        width=3
    )

    draw.text(
        (gamma_x, gamma_y),
        gamma_text,
        font=badge_font,
        fill=(255, 255, 100)
    )

    # Save thumbnail
    output_path = 'final_export/neural_network_navigator_THUMBNAIL.jpg'
    os.makedirs('final_export', exist_ok=True)

    # Convert to RGB and save as high-quality JPEG
    img = img.convert('RGB')
    img.save(output_path, 'JPEG', quality=95, optimize=True)

    print("="*70)
    print("✓ YOUTUBE THUMBNAIL CREATED")
    print("="*70)
    print()
    print(f"Thumbnail: {output_path}")
    print(f"Size: 1280x720 (YouTube standard)")
    print()
    print("Features:")
    print("  ✓ Eye-catching neural network visual theme")
    print("  ✓ Clear, bold title text with glow effects")
    print("  ✓ Highlighted unique features (40Hz Gamma)")
    print("  ✓ Professional gradient background")
    print("  ✓ Duration badge for viewer info")
    print()

    return output_path

if __name__ == '__main__':
    os.chdir('/home/rsalars/Projects/dreamweaving/sessions/neural-network-navigator')
    create_thumbnail()
