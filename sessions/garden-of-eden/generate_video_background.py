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
