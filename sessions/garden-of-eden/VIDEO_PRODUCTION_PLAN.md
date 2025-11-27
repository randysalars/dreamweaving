# Garden of Eden Video Production Plan
## Using 100% Free & Open-Source Tools

---

## Overview

Create a 25-minute meditation video with three visual phases:
1. **Opening (0-2:30)**: Beautiful Garden archway for thumbnail/pre-talk
2. **Journey (2:30-20:00)**: Chakra color gradients synced to meditation
3. **Return (20:00-25:00)**: Peaceful nature scene for awakening

**Total Production Time:** 6-10 hours (first time)
**Total Cost:** $0 (100% free tools)

---

## Tools Required

### 1. Image Generation
- **Stable Diffusion Web** (browser-based, no installation)
  - URL: https://huggingface.co/spaces/stabilityai/stable-diffusion
  - Alternative: https://www.craiyon.com (DALL-E Mini)
- **No installation needed**, works in browser

### 2. Video Generation
- **Python + MoviePy** (programmatic video creation)
  - Already in your venv: `pip install moviepy pillow numpy`
- **FFmpeg** (command-line video processing)
  - Install: `sudo apt install ffmpeg` (Linux) or already installed

### 3. Video Editing (Optional)
- **Blender** (if you want GUI editing)
  - Download: https://www.blender.org/download/
- **Or stick with Python scripts** (recommended for automation)

---

## Phase 1: Generate Images (2-3 hours)

### A. Garden of Eden Opening Image

**Use Stable Diffusion or Craiyon:**

**Prompt 1 (Garden Archway):**
```
mystical garden archway made of living emerald vines, golden sunlight streaming through,
paradise garden beyond, ethereal sacred atmosphere, glowing light particles,
cinematic lighting, highly detailed, spiritual art, fantasy landscape,
vibrant colors, photorealistic quality
```

**Prompt 2 (Alternative Meadow):**
```
lush paradise meadow with impossible colored flowers, sapphire roses and emerald lilies,
soft grass, golden afternoon light, ethereal spiritual atmosphere,
translucent light, sacred garden, cinematic quality, highly detailed
```

**Prompt 3 (Tree of Life):**
```
mystical Tree of Life with seven glowing chakra points, rainbow energy centers,
ruby red roots, emerald green heart, violet crown, golden light,
sacred geometry, spiritual art, fantasy landscape, highly detailed
```

**Instructions:**
1. Go to https://huggingface.co/spaces/stabilityai/stable-diffusion
2. Paste prompt
3. Click "Generate"
4. Download best result
5. Generate 3-5 variations
6. Save as: `eden_opening.png`, `eden_tree.png`, etc.

**Expected Time:** 1-2 hours (including iterations)

---

## Phase 2: Generate Background Videos with Python (3-4 hours)

### A. Chakra Gradient Generator Script

Create this script in your project:

**File:** `generate_video_background.py`

```python
#!/usr/bin/env python3
"""
Chakra gradient video generator for Garden of Eden meditation
Creates 25-minute gradient progression through all 7 chakra colors
"""

import numpy as np
from PIL import Image
import os
from pathlib import Path

class ChakraGradientGenerator:
    def __init__(self, width=1920, height=1080, duration_seconds=1500, fps=30):
        self.width = width
        self.height = height
        self.duration = duration_seconds
        self.fps = fps
        self.total_frames = duration_seconds * fps

        # Chakra colors (RGB)
        self.chakras = {
            'root': (200, 0, 0),         # Deep red
            'sacral': (255, 127, 0),     # Orange
            'solar': (255, 220, 0),      # Golden yellow
            'heart': (0, 200, 0),        # Emerald green
            'throat': (0, 150, 255),     # Sky blue
            'third_eye': (75, 0, 130),   # Indigo
            'crown': (160, 32, 240)      # Violet
        }

        # Timing for each section (in seconds)
        self.sections = {
            'pretalk': (0, 150),          # 0:00-2:30 - Warm gold
            'induction': (150, 480),      # 2:30-8:00 - Gold to green
            'meadow': (480, 810),         # 8:00-13:30 - Green
            'serpent': (810, 1020),       # 13:30-17:00 - Green to blue
            'tree_chakras': (1020, 1200), # 17:00-20:00 - All 7 chakras
            'divine': (1200, 1380),       # 20:00-23:00 - Violet to white
            'return': (1380, 1500)        # 23:00-25:00 - White to soft gold
        }

    def get_color_for_time(self, seconds):
        """Determine color based on meditation section"""
        if seconds < 150:  # Pre-talk
            return (200, 150, 50)  # Warm gold

        elif seconds < 480:  # Induction
            progress = (seconds - 150) / (480 - 150)
            gold = np.array([200, 150, 50])
            green = np.array(self.chakras['heart'])
            return tuple((gold * (1-progress) + green * progress).astype(int))

        elif seconds < 810:  # Meadow
            return self.chakras['heart']

        elif seconds < 1020:  # Serpent
            progress = (seconds - 810) / (1020 - 810)
            green = np.array(self.chakras['heart'])
            blue = np.array(self.chakras['throat'])
            return tuple((green * (1-progress) + blue * progress).astype(int))

        elif seconds < 1200:  # Tree - Chakra progression
            duration = 1200 - 1020  # 180 seconds
            progress = (seconds - 1020) / duration
            chakra_list = list(self.chakras.values())

            chakra_float = progress * (len(chakra_list) - 1)
            chakra_idx = int(chakra_float)
            local_progress = chakra_float - chakra_idx

            color1 = np.array(chakra_list[chakra_idx])
            color2 = np.array(chakra_list[min(chakra_idx + 1, len(chakra_list) - 1)])
            return tuple((color1 * (1-local_progress) + color2 * local_progress).astype(int))

        elif seconds < 1380:  # Divine
            progress = (seconds - 1200) / (1380 - 1200)
            violet = np.array(self.chakras['crown'])
            white = np.array([255, 255, 255])
            return tuple((violet * (1-progress) + white * progress).astype(int))

        else:  # Return
            progress = (seconds - 1380) / (1500 - 1380)
            white = np.array([255, 255, 255])
            gold = np.array([200, 150, 50])
            return tuple((white * (1-progress) + gold * progress).astype(int))

    def create_gradient_frame(self, color, frame_num):
        """Create single gradient frame with vertical blend"""
        # Add subtle animation (very slow breathing effect)
        breath_phase = np.sin(frame_num / (self.fps * 8)) * 0.05 + 0.95

        img_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        for y in range(self.height):
            vertical_blend = (y / self.height) * 0.4  # Darken toward bottom

            # Apply color with vertical gradient
            final_color = np.array(color) * (1 - vertical_blend) * breath_phase
            final_color = np.clip(final_color, 0, 255)

            img_array[y, :] = final_color.astype(np.uint8)

        return Image.fromarray(img_array)

    def generate_frames(self, output_dir="video_frames"):
        """Generate all frames"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        print(f"🎨 Generating {self.total_frames} frames ({self.duration/60:.1f} minutes)...")
        print(f"   Output: {output_dir}/")

        for frame_num in range(self.total_frames):
            seconds = frame_num / self.fps
            color = self.get_color_for_time(seconds)

            frame = self.create_gradient_frame(color, frame_num)
            frame_path = output_path / f"frame_{frame_num:06d}.png"
            frame.save(frame_path)

            if frame_num % 300 == 0:  # Every 10 seconds
                mins = int(seconds // 60)
                secs = int(seconds % 60)
                print(f"   Progress: {frame_num}/{self.total_frames} frames ({mins}:{secs:02d})")

        print(f"✅ Frame generation complete!")
        return output_path

# Usage
if __name__ == "__main__":
    print("=" * 70)
    print("Garden of Eden - Chakra Gradient Video Generator")
    print("=" * 70)
    print()

    generator = ChakraGradientGenerator(duration_seconds=1500)  # 25 minutes
    frame_dir = generator.generate_frames()

    print()
    print("Next step: Run compile script to create video from frames")
    print(f"  python3 compile_video.py {frame_dir}")
```

**Run it:**
```bash
cd /home/rsalars/Projects/dreamweaving/sessions/garden-of-eden
python3 generate_video_background.py
```

**Expected Time:** 30-60 minutes to generate all frames

---

### B. Compile Video Script

**File:** `compile_video.py`

```python
#!/usr/bin/env python3
"""
Compile video frames into MP4 using FFmpeg
"""

import subprocess
import sys
from pathlib import Path

def compile_video(frames_dir="video_frames", output="background_gradient.mp4", fps=30):
    """Use FFmpeg to compile frames into video"""

    frames_path = Path(frames_dir)
    if not frames_path.exists():
        print(f"❌ Error: Frames directory not found: {frames_dir}")
        sys.exit(1)

    frame_pattern = str(frames_path / "frame_%06d.png")

    print(f"🎬 Compiling video from frames...")
    print(f"   Input: {frame_pattern}")
    print(f"   Output: {output}")

    cmd = [
        'ffmpeg',
        '-framerate', str(fps),
        '-i', frame_pattern,
        '-c:v', 'libx264',
        '-preset', 'slow',      # Better compression
        '-crf', '18',            # High quality (18-23 is good range)
        '-pix_fmt', 'yuv420p',   # Compatibility
        '-y',                    # Overwrite
        output
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Video compiled successfully!")
        print(f"   Output: {output}")

        # Get file size
        output_path = Path(output)
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"   Size: {size_mb:.1f} MB")

    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error:")
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    frames_dir = sys.argv[1] if len(sys.argv) > 1 else "video_frames"
    compile_video(frames_dir)
```

**Run it:**
```bash
python3 compile_video.py video_frames
```

**Expected Time:** 5-15 minutes to compile

---

### C. Add Particle Effects (Optional)

**File:** `generate_particles.py`

```python
#!/usr/bin/env python3
"""
Generate particle effect overlay (fireflies/light specks)
Creates transparent overlay with floating particles
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import os
from pathlib import Path

class ParticleOverlay:
    def __init__(self, width=1920, height=1080, num_particles=150):
        self.width = width
        self.height = height
        self.num_particles = num_particles

        # Initialize particles
        self.positions = np.random.rand(num_particles, 2) * [width, height]
        self.velocities = (np.random.rand(num_particles, 2) - 0.5) * 1.5
        self.sizes = np.random.randint(2, 8, num_particles)
        self.glow_phases = np.random.rand(num_particles) * np.pi * 2
        self.glow_speeds = np.random.rand(num_particles) * 0.03 + 0.02

    def update(self):
        """Update particle positions and glow"""
        self.positions += self.velocities

        # Wrap around edges
        self.positions[:, 0] = self.positions[:, 0] % self.width
        self.positions[:, 1] = self.positions[:, 1] % self.height

        # Update glow
        self.glow_phases += self.glow_speeds
        glows = (np.sin(self.glow_phases) + 1) / 2  # 0 to 1

        return glows

    def render_frame(self):
        """Render single frame"""
        # Semi-transparent background
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        glows = self.update()

        for i in range(self.num_particles):
            x, y = self.positions[i]
            size = self.sizes[i]
            alpha = int(glows[i] * 180)  # Max 180 alpha for subtlety

            # Warm golden particle
            color = (255, 240, 180, alpha)

            # Draw particle
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)

            # Optional: Add glow
            if size > 4:
                glow_size = size * 1.5
                glow_color = (255, 240, 180, alpha // 3)
                draw.ellipse([x-glow_size, y-glow_size,
                             x+glow_size, y+glow_size], fill=glow_color)

        # Slight blur for dreaminess
        img = img.filter(ImageFilter.GaussianBlur(radius=1))

        return img

    def generate_sequence(self, duration=1500, fps=30, output_dir="particle_frames"):
        """Generate full particle sequence"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        total_frames = duration * fps
        print(f"✨ Generating {total_frames} particle frames...")

        for frame_num in range(total_frames):
            frame = self.render_frame()
            frame_path = output_path / f"particle_{frame_num:06d}.png"
            frame.save(frame_path)

            if frame_num % 300 == 0:
                print(f"   Progress: {frame_num}/{total_frames}")

        print(f"✅ Particle frames complete!")
        return output_path

if __name__ == "__main__":
    particles = ParticleOverlay(num_particles=200)
    particles.generate_sequence(duration=1500)

    print()
    print("Next: Compile particle overlay video")
    print("  python3 compile_video.py particle_frames particles_overlay.mp4")
```

---

## Phase 3: Composite Final Video (1-2 hours)

### Master Composition Script

**File:** `create_final_video.sh`

```bash
#!/bin/bash

# Garden of Eden - Final Video Compositor
# Combines background, particles, images, and audio

set -e  # Exit on error

echo "======================================================================"
echo "   Garden of Eden - Final Video Production"
echo "======================================================================"
echo ""

SESSION_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SESSION_DIR/output/video"
mkdir -p "$OUTPUT_DIR"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: Create background gradient video
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if [ ! -f "$OUTPUT_DIR/background_gradient.mp4" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "STEP 1: Generating chakra gradient background"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    python3 generate_video_background.py
    python3 compile_video.py video_frames "$OUTPUT_DIR/background_gradient.mp4"
else
    echo "✓ Background gradient already exists, skipping..."
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: Create particle overlay (optional)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if [ "$1" == "--with-particles" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "STEP 2: Generating particle overlay"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    python3 generate_particles.py
    python3 compile_video.py particle_frames "$OUTPUT_DIR/particles.mp4"

    USE_PARTICLES=true
else
    echo "Skipping particle overlay (use --with-particles to enable)"
    USE_PARTICLES=false
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: Add Garden images with fade effects
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Compositing Garden images"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if we have Garden images
if [ -f "eden_opening.png" ]; then
    echo "Adding Garden of Eden images with fade effects..."

    ffmpeg -i "$OUTPUT_DIR/background_gradient.mp4" \
      -loop 1 -t 10 -i eden_opening.png \
      -filter_complex "\
        [1:v]fade=in:0:30,fade=out:240:30,scale=1920:1080:force_original_aspect_ratio=decrease,\
        pad=1920:1080:(ow-iw)/2:(oh-ih)/2[eden]; \
        [0:v][eden]overlay=0:0:enable='between(t,30,40)'[out]" \
      -map "[out]" -c:v libx264 -crf 18 \
      "$OUTPUT_DIR/composite_with_images.mp4"

    COMPOSITE_FILE="$OUTPUT_DIR/composite_with_images.mp4"
else
    echo "No Garden images found, using background only..."
    COMPOSITE_FILE="$OUTPUT_DIR/background_gradient.mp4"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: Add title overlay
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Adding title overlay"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ffmpeg -i "$COMPOSITE_FILE" \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:\
text='GARDEN OF EDEN':fontcolor=white@0.9:fontsize=72:x=(w-text_w)/2:y=100:\
shadowcolor=black@0.8:shadowx=3:shadowy=3:enable='between(t,5,30)',\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:\
text='Guided Meditation | 25 Minutes':fontcolor=white@0.8:fontsize=36:x=(w-text_w)/2:y=200:\
shadowcolor=black@0.8:shadowx=2:shadowy=2:enable='between(t,5,30)'" \
  -c:v libx264 -crf 18 \
  "$OUTPUT_DIR/video_with_titles.mp4"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: Add meditation audio
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: Adding meditation audio"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Use the natural v2 audio we generated
AUDIO_FILE="output/natural/garden_of_eden_NATURAL_v2.mp3"

if [ -f "$AUDIO_FILE" ]; then
    ffmpeg -i "$OUTPUT_DIR/video_with_titles.mp4" \
      -i "$AUDIO_FILE" \
      -c:v copy \
      -c:a aac \
      -b:a 192k \
      -shortest \
      "$OUTPUT_DIR/garden_of_eden_FINAL.mp4"

    echo ""
    echo "======================================================================"
    echo "✨ FINAL VIDEO COMPLETE! ✨"
    echo "======================================================================"
    echo ""
    echo "📁 Output: $OUTPUT_DIR/garden_of_eden_FINAL.mp4"

    # Get file info
    FILE_SIZE=$(du -h "$OUTPUT_DIR/garden_of_eden_FINAL.mp4" | cut -f1)
    echo "📊 File size: $FILE_SIZE"

    echo ""
    echo "Next steps:"
    echo "  1. Review video: vlc $OUTPUT_DIR/garden_of_eden_FINAL.mp4"
    echo "  2. Create thumbnail from opening frame"
    echo "  3. Upload to YouTube with description from YOUTUBE_DESCRIPTION.md"

else
    echo "❌ Error: Audio file not found: $AUDIO_FILE"
    echo "   Generate it first with: ./create_natural_audio.sh"
    exit 1
fi
```

**Make it executable and run:**
```bash
chmod +x create_final_video.sh
./create_final_video.sh
```

---

## Phase 4: Create Thumbnail (30 minutes)

### Extract Opening Frame

```bash
# Extract frame at 30 seconds (after title fades in)
ffmpeg -i output/video/garden_of_eden_FINAL.mp4 -ss 00:00:30 -vframes 1 thumbnail_base.png

# Or use your generated Garden image directly
cp eden_opening.png thumbnail_base.png
```

### Add Text Overlay for Thumbnail

**File:** `create_thumbnail.sh`

```bash
#!/bin/bash

# Create YouTube thumbnail with text overlay

ffmpeg -i thumbnail_base.png \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,\
pad=1280:720:(ow-iw)/2:(oh-ih)/2,\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:\
text='GARDEN OF EDEN':fontcolor=white:fontsize=96:x=(w-text_w)/2:y=150:\
borderw=4:bordercolor=black,\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:\
text='25 Min Theta Meditation':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=280:\
borderw=3:bordercolor=black,\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:\
text='🎧 HEADPHONES REQUIRED':fontcolor=yellow:fontsize=36:x=50:y=50:\
borderw=2:bordercolor=black,\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:\
text='🌟 3D BINAURAL AUDIO':fontcolor=yellow:fontsize=36:x=50:y=100:\
borderw=2:bordercolor=black" \
  -frames:v 1 thumbnail_final.jpg

echo "✅ Thumbnail created: thumbnail_final.jpg"
```

---

## Production Timeline

### First-Time Complete Workflow

| Phase | Task | Time | Dependencies |
|-------|------|------|--------------|
| 1 | Generate Garden images | 1-2h | Stable Diffusion web |
| 2 | Generate gradient frames | 0.5-1h | Python script |
| 3 | Compile gradient video | 0.25h | FFmpeg |
| 4 | (Optional) Particle overlay | 1-2h | Python + FFmpeg |
| 5 | Composite with images | 0.5h | FFmpeg |
| 6 | Add audio | 0.25h | Natural audio ready |
| 7 | Create thumbnail | 0.25h | FFmpeg |
| **TOTAL** | **4-7 hours** | | |

### Subsequent Videos (Template Ready)

| Phase | Task | Time |
|-------|------|------|
| 1 | Adjust gradient colors | 0.25h |
| 2 | Generate new frames | 0.5h |
| 3 | Run composition script | 0.5h |
| **TOTAL** | **1.25 hours** | |

---

## File Structure

```
sessions/garden-of-eden/
├── generate_video_background.py    # Gradient generator
├── generate_particles.py           # Particle overlay
├── compile_video.py                # Frame compiler
├── create_final_video.sh          # Master compositor
├── create_thumbnail.sh            # Thumbnail generator
├── eden_opening.png               # Generated image
├── eden_tree.png                  # Generated image
├── video_frames/                  # Generated frames
│   └── frame_000000.png ... frame_045000.png
├── particle_frames/               # Particle frames (optional)
└── output/
    ├── video/
    │   ├── background_gradient.mp4
    │   ├── particles.mp4
    │   ├── composite_with_images.mp4
    │   ├── video_with_titles.mp4
    │   └── garden_of_eden_FINAL.mp4  ⭐ FINAL VIDEO
    └── natural/
        └── garden_of_eden_NATURAL_v2.mp3  (audio)
```

---

## Quick Start Commands

```bash
# 1. Install dependencies (if needed)
pip install moviepy pillow numpy
sudo apt install ffmpeg  # or: brew install ffmpeg

# 2. Generate Garden images
# Go to: https://huggingface.co/spaces/stabilityai/stable-diffusion
# Use prompts from Phase 1
# Download and save as eden_opening.png

# 3. Generate video
python3 generate_video_background.py
python3 compile_video.py video_frames output/video/background_gradient.mp4

# 4. Create final video
./create_final_video.sh

# 5. Create thumbnail
./create_thumbnail.sh

# Done! Your video is ready for YouTube!
```

---

## Alternative: Simple Static Version (2-3 hours)

If you want to start even simpler:

```bash
# 1. Generate one great Garden image

# 2. Create video from static image + audio
ffmpeg -loop 1 -i eden_opening.png \
  -i output/natural/garden_of_eden_NATURAL_v2.mp3 \
  -c:v libx264 -tune stillimage \
  -c:a aac -b:a 192k \
  -pix_fmt yuv420p \
  -shortest \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,\
pad=1920:1080:(ow-iw)/2:(oh-ih)/2,\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:\
text='GARDEN OF EDEN':fontcolor=white:fontsize=80:x=(w-text_w)/2:y=150:\
borderw=4:bordercolor=black,fade=in:0:60:alpha=1,fade=out:120:60:alpha=1" \
  output/video/garden_of_eden_simple.mp4

echo "✅ Simple version created!"
```

This creates a meditation video with a single beautiful image that fades in/out titles.

---

## Next Steps

1. **Choose your approach:**
   - Full chakra gradient (recommended, most professional)
   - Simple static image (fastest, still good quality)

2. **Generate images** using Stable Diffusion web

3. **Run the scripts** in order

4. **Review the output** video

5. **Create thumbnail** and upload to YouTube

Would you like me to create these Python scripts in your project directory now?
