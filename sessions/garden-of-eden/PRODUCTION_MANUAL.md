# Guided Meditation Video Production Manual

**Complete Workflow for AI-Assisted Hypnotic Video Creation**

This manual documents the complete production process used to create the "Garden of Eden" meditation video (25 minutes, 1080p, with binaural beats and 7 meditation images). Follow these steps to replicate the process for any meditation/hypnosis video project.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Script Writing Process](#2-script-writing-process)
3. [Audio Generation](#3-audio-generation)
4. [Binaural Beat Production](#4-binaural-beat-production)
5. [Sound Effect Integration](#5-sound-effect-integration)
6. [Image Generation](#6-image-generation)
7. [Video Background Creation](#7-video-background-creation)
8. [Image Compositing](#8-image-compositing)
9. [Final Video Assembly](#9-final-video-assembly)
10. [YouTube Optimization](#10-youtube-optimization)
11. [Quality Control Checklist](#11-quality-control-checklist)
12. [Technical Troubleshooting](#12-technical-troubleshooting)

---

## 1. Project Structure

### Directory Layout

Create this structure for each meditation session:

```
sessions/garden-of-eden/
├── output/
│   ├── natural/          # Natural voice audio files
│   ├── enhanced/         # Audio with frequency tracks
│   └── video/            # Video output files
├── scripts/              # Hypnosis script text files
├── eden_01_pretalk.png   # Section images (WebP format, .png extension)
├── eden_02_induction.png
├── eden_03_meadow.png
├── eden_04_serpent.png
├── eden_05_tree.png
├── eden_06_divine.png
├── eden_07_return.png
├── composite_images.py   # Image compositor script
├── generate_video_background.py  # Background generator
├── create_final_video.sh # Master assembly script
└── create_thumbnail.sh   # YouTube thumbnail generator
```

### Required Tools

**All Free & Open Source:**

- **Python 3.x** with libraries:
  - `edge-tts` (Microsoft Edge TTS)
  - `pydub` (audio manipulation)
  - `Pillow` (PIL - image generation)
  - `numpy` (numerical operations)

- **FFmpeg** (video/audio processing)
- **Stable Diffusion** (or similar - for image generation)

Install dependencies:
```bash
pip install edge-tts pydub pillow numpy
sudo apt install ffmpeg  # Linux
brew install ffmpeg      # macOS
```

---

## 2. Script Writing Process

### Structure Requirements

A meditation script should have these sections:

1. **Pre-talk** (2-3 minutes)
   - Builds rapport and sets expectations
   - Explains the meditation journey
   - Establishes authority and safety

2. **Induction** (5-6 minutes)
   - Progressive relaxation (body scan)
   - Deepening techniques
   - Countdown or staircase descent
   - Binaural beat integration instructions

3. **Core Meditation** (12-15 minutes)
   - Primary visualization/journey
   - Divided into 4-5 distinct scenes
   - Each scene 3-4 minutes
   - Sensory-rich descriptions (VAKOG: Visual, Auditory, Kinesthetic, Olfactory, Gustatory)

4. **Transformation/Integration** (2-3 minutes)
   - Peak experience or realization
   - Symbolic transformation
   - Emotional release or insight

5. **Return/Awakening** (2-3 minutes)
   - Gradual return to awareness
   - Count-up (1-5 or 1-10)
   - Post-hypnotic suggestions
   - Grounding and orientation

### Script Template

```markdown
# [SESSION TITLE]

**Duration**: 25 minutes
**Theme**: [Transformation/Healing/Exploration]
**Frequency**: [Theta/Alpha/Delta range]

## PRE-TALK (0:00-2:30)

Welcome message and journey overview...

## INDUCTION (2:30-8:00)

Progressive relaxation script...

## MEDITATION CORE

### Scene 1: [Name] (8:00-11:00)
Vivid sensory description...

### Scene 2: [Name] (11:00-14:00)
Continuation with deeper engagement...

[Continue for all scenes]

## AWAKENING (23:00-25:00)

Return and grounding script...
```

### Writing Guidelines

**Language Patterns:**

- Use present tense ("You see..." not "You will see...")
- Employ permissive language ("You may notice..." "Perhaps you feel...")
- Create compound suggestions ("As you relax deeper, you feel more peaceful")
- Use embedded commands (italicized in script: "You can *release tension* now")
- Include confusion techniques sparingly ("The more you try to stay awake, the deeper you go")

**Pacing:**

- Slow, deliberate pacing throughout
- Longer pauses (3-5 seconds) marked with `[pause]`
- Very long pauses (5-10 seconds) marked with `[long pause]`
- Match breathing rhythm when appropriate

**Sensory Richness:**

- Visual: Colors, shapes, light quality, movement
- Auditory: Nature sounds, silence, inner sounds
- Kinesthetic: Textures, temperature, physical sensations
- Olfactory: Scents that match environment
- Gustatory: Tastes (when appropriate)

**Safety:**

- Always include awakening procedure
- Provide clear return pathway
- Add disclaimer: "If you need to wake fully at any time, you can simply open your eyes"

---

## 3. Audio Generation

### Method 1: Edge TTS (Primary Method)

**Why Edge TTS:**
- Free, no API key required
- High-quality, natural voices
- Good prosody control via SSML
- Consistent pronunciation

**Voice Selection:**

For meditation/hypnosis, use:
- **en-US-AvaMultilingualNeural** (warm, soothing female)
- **en-US-AndrewMultilingualNeural** (calm, authoritative male)
- **en-GB-SoniaNeural** (soft British female)

**Script Conversion for TTS:**

Prepare script with SSML markup:

```python
#!/usr/bin/env python3
"""Generate natural meditation audio using Edge TTS"""
import asyncio
import edge_tts
from pathlib import Path

async def generate_audio(script_text, output_file, voice="en-US-AvaMultilingualNeural"):
    """Generate audio from script using Edge TTS"""

    # Add SSML markup for better prosody
    ssml_script = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
    <voice name='{voice}'>
        <prosody rate='-20%' pitch='-5%'>
            {script_text}
        </prosody>
    </voice>
</speak>"""

    communicate = edge_tts.Communicate(ssml_script, voice)
    await communicate.save(output_file)
    print(f"✅ Audio generated: {output_file}")

# Usage
script_file = Path("scripts/garden_of_eden_script.txt")
output_file = Path("output/natural/garden_of_eden_NATURAL.mp3")

script_text = script_file.read_text()
asyncio.run(generate_audio(script_text, str(output_file)))
```

**Key Parameters:**

- `rate='-20%'` - Slows speech by 20% for meditation pacing
- `pitch='-5%'` - Slightly lower pitch for calming effect
- Add `<break time='3s'/>` for pauses in script
- Add `<emphasis level='moderate'>` for key phrases

**Expected Output:**

- Duration: Matches script timing (~25 minutes)
- Format: MP3, 192kbps
- File size: ~35-40 MB
- Sample rate: 24kHz or 48kHz

---

## 4. Binaural Beat Production

### Frequency Selection

**Meditation States:**

- **Delta (0.5-4 Hz)**: Deep sleep, healing, unconscious
- **Theta (4-8 Hz)**: Deep meditation, creativity, hypnosis ← *Primary for meditation*
- **Alpha (8-13 Hz)**: Relaxation, light meditation, pre-sleep
- **Beta (13-30 Hz)**: Normal waking consciousness
- **Gamma (30-100 Hz)**: Peak awareness, transcendent states

**Garden of Eden Frequency Map:**

| Section | Frequency | State |
|---------|-----------|-------|
| Pre-talk | 10 Hz (Alpha) | Relaxed alertness |
| Induction | 8 → 6 Hz | Alpha to Theta transition |
| Core meditation | 5 Hz (Theta) | Deep meditation |
| Peak experience | 40 Hz (Gamma) | Transcendent insight |
| Return | 6 → 10 Hz | Theta to Alpha transition |

### Implementation Script

```python
#!/usr/bin/env python3
"""Generate binaural beats with smooth frequency transitions"""
import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine

def generate_binaural_beat(duration_ms, base_freq=200, beat_freq=6, sample_rate=44100):
    """
    Generate binaural beat
    duration_ms: Length in milliseconds
    base_freq: Carrier frequency (Hz) - typically 150-250 Hz
    beat_freq: Beat frequency (Hz) - the difference that creates the effect
    """
    left_freq = base_freq
    right_freq = base_freq + beat_freq

    # Generate sine waves
    left_channel = Sine(left_freq, sample_rate=sample_rate).to_audio_segment(duration=duration_ms)
    right_channel = Sine(right_freq, sample_rate=sample_rate).to_audio_segment(duration=duration_ms)

    # Combine to stereo
    stereo = AudioSegment.from_mono_audiosegments(left_channel, right_channel)

    # Reduce volume to -20dB (background level)
    return stereo - 20

def create_frequency_track(duration_sec=1500):  # 25 minutes
    """Create complete frequency track with transitions"""

    segments = []

    # Pre-talk: 10 Hz alpha (150 seconds)
    segments.append(generate_binaural_beat(150000, base_freq=200, beat_freq=10))

    # Induction transition: 8 Hz → 6 Hz (330 seconds)
    for i in range(33):  # 10-second segments
        progress = i / 33
        beat_freq = 8 - (2 * progress)  # 8 Hz → 6 Hz
        segments.append(generate_binaural_beat(10000, base_freq=200, beat_freq=beat_freq))

    # Core meditation: 5 Hz theta (720 seconds - 12 minutes)
    segments.append(generate_binaural_beat(720000, base_freq=200, beat_freq=5))

    # Peak: 40 Hz gamma (60 seconds)
    segments.append(generate_binaural_beat(60000, base_freq=200, beat_freq=40))

    # Return transition: 6 Hz → 10 Hz (180 seconds)
    for i in range(18):
        progress = i / 18
        beat_freq = 6 + (4 * progress)  # 6 Hz → 10 Hz
        segments.append(generate_binaural_beat(10000, base_freq=200, beat_freq=beat_freq))

    # Combine all segments
    full_track = segments[0]
    for segment in segments[1:]:
        full_track += segment

    return full_track

# Generate and export
frequency_track = create_frequency_track()
frequency_track.export("frequency_track.wav", format="wav")
print("✅ Binaural beat track generated")
```

**Key Principles:**

1. **Carrier Frequency**: 150-250 Hz (inaudible "base" tone)
2. **Beat Frequency**: The difference between left/right ears (4-10 Hz for meditation)
3. **Volume**: Keep at -20dB to -25dB (background, not intrusive)
4. **Transitions**: Gradual frequency changes over 30-60 seconds
5. **Stereo Required**: Binaural beats ONLY work with headphones

---

## 5. Sound Effect Integration

### Natural Ambience Selection

**Garden of Eden Sound Palette:**

- **Forest ambience** (induction): Birds, gentle breeze, rustling leaves
- **Water sounds** (meadow): Flowing stream, gentle waterfall
- **Wind chimes** (transformation): Crystalline, ethereal
- **Om/singing bowls** (divine section): Resonant, spiritual

### Mixing Levels

**Audio Hierarchy (in dB):**

1. Voice: 0 dB (reference level)
2. Binaural beats: -20 dB (subtle, background)
3. Ambience: -15 to -18 dB (noticeable but not distracting)
4. Musical accents: -12 dB (occasional, brief)

### Implementation

```python
#!/usr/bin/env python3
"""Mix voice, binaural beats, and sound effects"""
from pydub import AudioSegment

def create_ultimate_mix(voice_file, frequency_file, output_file):
    """Create final audio mix"""

    # Load components
    voice = AudioSegment.from_mp3(voice_file)
    frequency = AudioSegment.from_wav(frequency_file)

    # Match durations (trim longer one)
    duration = min(len(voice), len(frequency))
    voice = voice[:duration]
    frequency = frequency[:duration]

    # Set frequency level to -20dB
    frequency = frequency - 20

    # Optional: Add nature ambience
    # ambience = AudioSegment.from_wav("forest_ambience.wav")
    # ambience = ambience[:duration] - 18

    # Mix components
    mixed = voice.overlay(frequency)
    # mixed = mixed.overlay(ambience)  # If using ambience

    # Apply gentle fade in/out
    mixed = mixed.fade_in(3000).fade_out(5000)

    # Export final mix
    mixed.export(output_file, format="mp3", bitrate="192k")
    print(f"✅ Ultimate mix created: {output_file}")

# Usage
create_ultimate_mix(
    "output/natural/garden_of_eden_NATURAL_v2.mp3",
    "frequency_track.wav",
    "output/enhanced/garden_of_eden_ULTIMATE.mp3"
)
```

---

## 6. Image Generation

### Image Requirements

**Specifications:**

- **Resolution**: Minimum 1920x1080 (1080p), prefer 1920x1080 exactly
- **Format**: PNG or WebP (save as .png regardless)
- **Aspect Ratio**: 16:9
- **Style**: Consistent across all images
- **Quality**: High detail, meditation-appropriate (calming, no disturbing elements)

### Number of Images

Calculate based on meditation duration:

- **Short (10-15 min)**: 4-5 images
- **Medium (20-25 min)**: 6-8 images  ← *Garden of Eden used 7*
- **Long (30-45 min)**: 10-12 images

**Rule of thumb**: One image per 3-4 minute section

### Naming Convention

```
[session_name]_01_[section_name].png
[session_name]_02_[section_name].png
...
```

**Garden of Eden Example:**
```
eden_01_pretalk.png      (0:00-2:30)
eden_02_induction.png    (2:30-8:00)
eden_03_meadow.png       (8:00-13:30)
eden_04_serpent.png      (13:30-17:00)
eden_05_tree.png         (17:00-20:00)
eden_06_divine.png       (20:00-23:00)
eden_07_return.png       (23:00-25:00)
```

### Image Generation Process

**Using Stable Diffusion (or similar):**

1. **Create detailed prompts** matching script sections
2. **Maintain consistent style** (same model, similar prompt structure)
3. **Generate multiple candidates** (3-5 per section)
4. **Select best match** for meditation mood

**Example Prompts:**

```
Eden Pretalk:
"Garden archway entrance, ornate stone arch covered in flowering vines,
golden sunset light, mystical atmosphere, peaceful and inviting,
professional photography, depth of field, 8k quality"

Eden Induction:
"Forest path descending through ancient trees, soft diffused light filtering
through canopy, moss-covered stones, peaceful and calming, dreamlike quality,
fantasy art style, high detail"

Eden Meadow:
"Paradise meadow with wildflowers, crystal clear stream, majestic mountains
in background, blue sky with soft clouds, vibrant colors, serene atmosphere,
landscape photography, golden hour lighting"
```

**Prompt Guidelines:**

- Start with main subject
- Add environment details
- Specify lighting/atmosphere
- Include mood descriptors
- Add quality/style tags
- Avoid text in images

### Image Processing

After generation, process images:

```bash
# Resize to exact 1920x1080 if needed
ffmpeg -i input.png -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" output.png

# Convert to WebP (optional - smaller file size)
ffmpeg -i input.png -c:v libwebp -quality 95 output.webp
```

---

## 7. Video Background Creation

### Background Options

**Option 1: Solid Color Progression** (Simple, fast)
- Single color that transitions through meditation sections
- Minimal distraction from images

**Option 2: Gradient Animation** (Recommended for Garden of Eden)
- Smooth color transitions synchronized to script sections
- Chakra-based color system for spiritual themes

**Option 3: Subtle Particle Effects**
- Floating particles, sacred geometry, mandalas
- More processing time, more visual interest

### Garden of Eden Implementation: Chakra Gradients

**Color Mapping:**

```python
CHAKRA_COLORS = {
    'root':     (196, 25, 25),    # Red
    'sacral':   (217, 119, 40),   # Orange
    'solar':    (242, 202, 73),   # Yellow
    'heart':    (73, 191, 111),   # Green
    'throat':   (73, 151, 242),   # Blue
    'third_eye': (100, 73, 242),  # Indigo
    'crown':    (167, 73, 242)    # Violet
}
```

**Section Color Mapping:**

| Section | Duration | Color Transition |
|---------|----------|-----------------|
| Pre-talk | 0:00-2:30 | Warm gold (custom) |
| Induction | 2:30-8:00 | Gold → Green (grounding) |
| Meadow | 8:00-13:30 | Green (heart chakra) |
| Serpent | 13:30-17:00 | Green → Blue (transformation) |
| Tree | 17:00-20:00 | Rainbow (all chakras) |
| Divine | 20:00-23:00 | Violet → White (crown) |
| Return | 23:00-25:00 | Blue → Gold (grounding) |

### Frame Generation Script

```python
#!/usr/bin/env python3
"""Generate video background frames with gradient progression"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

class VideoBackgroundGenerator:
    def __init__(self, width=1920, height=1080, fps=30, duration_sec=1500):
        self.width = width
        self.height = height
        self.fps = fps
        self.duration_sec = duration_sec
        self.total_frames = fps * duration_sec  # 45,000 frames for 25 min

        self.chakras = {
            'root': (196, 25, 25),
            'sacral': (217, 119, 40),
            'solar': (242, 202, 73),
            'heart': (73, 191, 111),
            'throat': (73, 151, 242),
            'third_eye': (100, 73, 242),
            'crown': (167, 73, 242)
        }

    def get_color_for_time(self, seconds):
        """Return RGB color for given timestamp"""
        if seconds < 150:  # Pre-talk (0-2:30)
            return (200, 150, 50)  # Warm gold

        elif seconds < 480:  # Induction (2:30-8:00)
            # Transition from gold to green
            progress = (seconds - 150) / (480 - 150)
            gold = np.array([200, 150, 50])
            green = np.array(self.chakras['heart'])
            color = gold * (1 - progress) + green * progress
            return tuple(color.astype(int))

        elif seconds < 810:  # Meadow (8:00-13:30)
            return self.chakras['heart']  # Green

        elif seconds < 1020:  # Serpent (13:30-17:00)
            # Transition green to blue
            progress = (seconds - 810) / (1020 - 810)
            green = np.array(self.chakras['heart'])
            blue = np.array(self.chakras['throat'])
            color = green * (1 - progress) + blue * progress
            return tuple(color.astype(int))

        elif seconds < 1200:  # Tree (17:00-20:00)
            # Rainbow transition through all chakras
            progress = (seconds - 1020) / (1200 - 1020)
            chakra_list = list(self.chakras.values())
            index = progress * (len(chakra_list) - 1)
            lower_idx = int(index)
            upper_idx = min(lower_idx + 1, len(chakra_list) - 1)
            blend = index - lower_idx

            lower_color = np.array(chakra_list[lower_idx])
            upper_color = np.array(chakra_list[upper_idx])
            color = lower_color * (1 - blend) + upper_color * blend
            return tuple(color.astype(int))

        elif seconds < 1380:  # Divine (20:00-23:00)
            # Transition violet to white
            progress = (seconds - 1200) / (1380 - 1200)
            violet = np.array(self.chakras['crown'])
            white = np.array([255, 255, 255])
            color = violet * (1 - progress) + white * progress
            return tuple(color.astype(int))

        else:  # Return (23:00-25:00)
            # Transition back to warm gold
            progress = (seconds - 1380) / (1500 - 1380)
            blue = np.array(self.chakras['throat'])
            gold = np.array([200, 150, 50])
            color = blue * (1 - progress) + gold * progress
            return tuple(color.astype(int))

    def create_gradient_frame(self, color1, color2):
        """Create vertical gradient from color1 to color2"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)

        for y in range(self.height):
            progress = y / self.height
            r = int(color1[0] * (1-progress) + color2[0] * progress)
            g = int(color1[1] * (1-progress) + color2[1] * progress)
            b = int(color1[2] * (1-progress) + color2[2] * progress)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        return img

    def generate_all_frames(self, output_dir="video_frames"):
        """Generate all frames"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        print(f"Generating {self.total_frames} frames...")

        for frame_num in range(self.total_frames):
            seconds = frame_num / self.fps

            # Get color for this timestamp
            base_color = self.get_color_for_time(seconds)

            # Create gradient (darker at bottom)
            dark_color = tuple(int(c * 0.6) for c in base_color)
            img = self.create_gradient_frame(base_color, dark_color)

            # Save frame
            frame_filename = output_path / f"frame_{frame_num:06d}.png"
            img.save(frame_filename)

            # Progress indicator
            if frame_num % 1000 == 0:
                progress = (frame_num / self.total_frames) * 100
                print(f"Progress: {progress:.1f}% ({frame_num}/{self.total_frames})")

        print(f"✅ All frames generated in {output_dir}/")

# Usage
if __name__ == "__main__":
    generator = VideoBackgroundGenerator()
    generator.generate_all_frames()
```

**Execution Time:**

- 45,000 frames @ ~15 frames/sec = ~50 minutes
- Output: ~530 MB of PNG frames

### Frame Compilation

```python
#!/usr/bin/env python3
"""Compile frames to MP4 video"""
import subprocess
from pathlib import Path

def compile_frames_to_video(frame_dir, output_file, fps=30):
    """Use FFmpeg to compile frames"""

    cmd = [
        'ffmpeg',
        '-framerate', str(fps),
        '-i', f'{frame_dir}/frame_%06d.png',
        '-c:v', 'libx264',
        '-crf', '18',  # High quality
        '-preset', 'slow',  # Better compression
        '-pix_fmt', 'yuv420p',
        '-y',
        output_file
    ]

    print(f"Compiling frames to video...")
    subprocess.run(cmd, check=True)
    print(f"✅ Video compiled: {output_file}")

# Usage
compile_frames_to_video("video_frames", "output/video/background_gradient.mp4")
```

---

## 8. Image Compositing

### Critical Technical Requirement

**IMPORTANT**: FFmpeg's `fade` filter operates on **input frame numbers**, but `overlay enable` uses **video timeline seconds**. This mismatch causes only 1-2 images to render.

**SOLUTION**: Use `geq` filter for time-based alpha channel manipulation.

### Compositor Script (FINAL WORKING VERSION)

```python
#!/usr/bin/env python3
"""
Composite multiple images onto video with proper timing and fade effects
FINAL VERSION: Uses geq filter for time-based alpha fading
"""

import subprocess
import sys
from pathlib import Path

def composite_images(base_video, output_video, images_config):
    """
    Composite images onto base video with smooth fades

    images_config: list of (image_path, start_time, end_time) tuples
    """

    if not images_config:
        print("No images to composite")
        return False

    # Build FFmpeg command
    cmd = ['ffmpeg', '-i', base_video]

    # Add all image inputs
    for img_path, _, _ in images_config:
        cmd.extend(['-loop', '1', '-i', img_path])

    # Build filter_complex
    filters = []

    # Scale, pad, and add alpha channel to all images
    for idx in range(len(images_config)):
        input_num = idx + 1
        scale_filter = (
            f"[{input_num}:v]"
            f"scale=1920:1080:force_original_aspect_ratio=decrease,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
            f"format=yuva420p"  # Add alpha channel
            f"[scaled{idx}]"
        )
        filters.append(scale_filter)

    # Apply time-based alpha for each image using geq filter
    for idx, (img_path, start_sec, end_sec) in enumerate(images_config):
        fade_duration = 2.0  # 2 second fades
        fade_in_end = start_sec + fade_duration
        fade_out_start = end_sec - fade_duration

        # Build alpha expression for geq filter
        # T is the video timeline in seconds
        # Alpha goes from 0-255 (not 0-1 in geq)

        alpha_expr = (
            f"'if(lt(T,{start_sec}),0,"
            f"if(lt(T,{fade_in_end}),(T-{start_sec})*{255/fade_duration},"
            f"if(lt(T,{fade_out_start}),255,"
            f"if(lt(T,{end_sec}),({end_sec}-T)*{255/fade_duration},0))))'"
        )

        # Apply geq to modify only the alpha channel
        geq_filter = (
            f"[scaled{idx}]"
            f"geq=lum='p(X,Y)':cb='p(X,Y)':cr='p(X,Y)':a={alpha_expr}"
            f"[alpha{idx}]"
        )
        filters.append(geq_filter)

    # Build overlay chain (now all images have time-based alpha)
    current_stream = "[0:v]"
    for idx in range(len(images_config)):
        if idx == len(images_config) - 1:
            # Last overlay
            overlay_filter = f"{current_stream}[alpha{idx}]overlay=0:0[out]"
        else:
            # Intermediate overlay
            overlay_filter = f"{current_stream}[alpha{idx}]overlay=0:0[tmp{idx}]"
            current_stream = f"[tmp{idx}]"
        filters.append(overlay_filter)

    # Join all filters
    filter_complex = "; ".join(filters)

    # Complete command
    cmd.extend([
        '-filter_complex', filter_complex,
        '-map', '[out]',
        '-c:v', 'libx264',
        '-crf', '18',
        '-t', '1500',  # 25 minutes
        '-y',
        output_video
    ])

    print(f"\nCompositing {len(images_config)} images with 2-second fades...")
    print(f"Output: {output_video}\n")

    # Run FFmpeg
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Compositing complete with all fades")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ FFmpeg error during compositing")
        return False


if __name__ == "__main__":
    # Define image configuration
    session_dir = Path(__file__).parent
    output_dir = session_dir / "output" / "video"

    base_video = output_dir / "background_gradient.mp4"
    output_video = output_dir / "composite_with_images.mp4"

    # Image timings (path, start_sec, end_sec)
    images = []

    if (session_dir / "eden_01_pretalk.png").exists():
        images.append((str(session_dir / "eden_01_pretalk.png"), 0, 150))
        print("✓ eden_01_pretalk.png (0:00-2:30)")

    if (session_dir / "eden_02_induction.png").exists():
        images.append((str(session_dir / "eden_02_induction.png"), 150, 480))
        print("✓ eden_02_induction.png (2:30-8:00)")

    if (session_dir / "eden_03_meadow.png").exists():
        images.append((str(session_dir / "eden_03_meadow.png"), 480, 810))
        print("✓ eden_03_meadow.png (8:00-13:30)")

    if (session_dir / "eden_04_serpent.png").exists():
        images.append((str(session_dir / "eden_04_serpent.png"), 810, 1020))
        print("✓ eden_04_serpent.png (13:30-17:00)")

    if (session_dir / "eden_05_tree.png").exists():
        images.append((str(session_dir / "eden_05_tree.png"), 1020, 1200))
        print("✓ eden_05_tree.png (17:00-20:00)")

    if (session_dir / "eden_06_divine.png").exists():
        images.append((str(session_dir / "eden_06_divine.png"), 1200, 1380))
        print("✓ eden_06_divine.png (20:00-23:00)")

    if (session_dir / "eden_07_return.png").exists():
        images.append((str(session_dir / "eden_07_return.png"), 1380, 1500))
        print("✓ eden_07_return.png (23:00-25:00)")

    if not images:
        print("❌ No images found")
        sys.exit(1)

    success = composite_images(str(base_video), str(output_video), images)

    sys.exit(0 if success else 1)
```

**Why This Works:**

1. `format=yuva420p` adds alpha channel to images
2. `geq` filter uses `T` variable (video timeline in seconds)
3. Alpha expression creates smooth fades: 0 → 255 (2 sec) → 255 → 0 (2 sec)
4. No `enable` filter needed - alpha channel handles visibility
5. All overlay operations use consistent timeline reference

**Execution Time:**

- 7 images, 25 minutes video = ~40-50 minutes processing
- Output: composite_with_images.mp4 (~400-500 MB)

### Verification Commands

After compositing, extract test frames:

```bash
# Check each image appears at correct time
ffmpeg -i composite_with_images.mp4 -ss 00:01:00 -vframes 1 test_pretalk.jpg
ffmpeg -i composite_with_images.mp4 -ss 00:05:00 -vframes 1 test_induction.jpg
ffmpeg -i composite_with_images.mp4 -ss 00:10:00 -vframes 1 test_meadow.jpg
ffmpeg -i composite_with_images.mp4 -ss 00:15:00 -vframes 1 test_serpent.jpg
ffmpeg -i composite_with_images.mp4 -ss 00:18:00 -vframes 1 test_tree.jpg
ffmpeg -i composite_with_images.mp4 -ss 00:21:00 -vframes 1 test_divine.jpg
ffmpeg -i composite_with_images.mp4 -ss 00:24:00 -vframes 1 test_return.jpg
```

---

## 9. Final Video Assembly

### Master Assembly Script

```bash
#!/bin/bash
# create_final_video.sh - Complete video assembly pipeline

set -e  # Exit on error

SESSION_DIR="$(dirname "$0")"
OUTPUT_DIR="$SESSION_DIR/output/video"
mkdir -p "$OUTPUT_DIR"

echo "================================"
echo "GARDEN OF EDEN - VIDEO ASSEMBLY"
echo "================================"

# STEP 1: Generate background gradient frames
echo ""
echo "STEP 1: Generating background gradient frames..."
python3 "$SESSION_DIR/generate_video_background.py"

# STEP 2: Compile frames to video
echo ""
echo "STEP 2: Compiling frames to video..."
python3 "$SESSION_DIR/compile_video.py" "$SESSION_DIR/video_frames" "$OUTPUT_DIR/background_gradient.mp4"

# STEP 3: Composite meditation images
echo ""
echo "STEP 3: Compositing meditation images..."
if python3 "$SESSION_DIR/composite_images.py"; then
    COMPOSITE_FILE="$OUTPUT_DIR/composite_with_images.mp4"
    echo "✅ Images composited successfully"
else
    echo "⚠️  Image compositing failed, using gradient only"
    COMPOSITE_FILE="$OUTPUT_DIR/background_gradient.mp4"
fi

# STEP 4: Add title overlay
echo ""
echo "STEP 4: Adding title overlay..."
ffmpeg -i "$COMPOSITE_FILE" \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:\
text='GARDEN OF EDEN':fontcolor=white@0.9:fontsize=72:\
x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,5)',\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf:\
text='A Guided Meditation Journey':fontcolor=white@0.8:fontsize=36:\
x=(w-text_w)/2:y=(h-text_h)/2+100:enable='between(t,0,5)'" \
  -c:v libx264 -crf 18 -c:a copy -y \
  "$OUTPUT_DIR/video_with_titles.mp4"

echo "✅ Titles added"

# STEP 5: Mix with audio
echo ""
echo "STEP 5: Mixing with meditation audio..."

# Find audio file (try ULTIMATE first, then NATURAL_v2)
if [ -f "$SESSION_DIR/output/enhanced/garden_of_eden_ULTIMATE.mp3" ]; then
    AUDIO_FILE="$SESSION_DIR/output/enhanced/garden_of_eden_ULTIMATE.mp3"
    echo "Using ULTIMATE audio (with binaural beats)"
elif [ -f "$SESSION_DIR/output/natural/garden_of_eden_NATURAL_v2.mp3" ]; then
    AUDIO_FILE="$SESSION_DIR/output/natural/garden_of_eden_NATURAL_v2.mp3"
    echo "Using NATURAL_v2 audio"
else
    echo "❌ No audio file found!"
    exit 1
fi

# Combine video and audio
ffmpeg -i "$OUTPUT_DIR/video_with_titles.mp4" \
  -i "$AUDIO_FILE" \
  -c:v copy -c:a aac -b:a 192k -shortest \
  -y "$OUTPUT_DIR/garden_of_eden_FINAL.mp4"

echo ""
echo "================================"
echo "✅ FINAL VIDEO COMPLETE"
echo "================================"
echo "Output: $OUTPUT_DIR/garden_of_eden_FINAL.mp4"
echo ""

# Get file size
FILE_SIZE=$(du -h "$OUTPUT_DIR/garden_of_eden_FINAL.mp4" | cut -f1)
echo "File size: $FILE_SIZE"

# Get duration
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT_DIR/garden_of_eden_FINAL.mp4")
MINUTES=$(echo "$DURATION / 60" | bc)
SECONDS=$(echo "$DURATION % 60" | bc)
echo "Duration: ${MINUTES}m ${SECONDS}s"

echo ""
echo "Next step: Create thumbnail with ./create_thumbnail.sh"
```

**Execution:**

```bash
chmod +x create_final_video.sh
./create_final_video.sh
```

**Total Processing Time:**

1. Frame generation: ~50 minutes
2. Frame compilation: ~2-3 minutes
3. Image compositing: ~40-50 minutes
4. Title overlay: ~2-3 minutes
5. Audio mixing: ~1-2 minutes

**Total: ~100-110 minutes (1.5-2 hours)**

---

## 10. YouTube Optimization

### Thumbnail Creation

```bash
#!/bin/bash
# create_thumbnail.sh - Generate YouTube thumbnail

SESSION_DIR="$(dirname "$0")"
OUTPUT_DIR="$SESSION_DIR/output/video"

# Find best image for thumbnail (prefer pretalk, meadow, or tree)
if [ -f "$SESSION_DIR/eden_01_pretalk.png" ]; then
    BASE_IMAGE="$SESSION_DIR/eden_01_pretalk.png"
elif [ -f "$SESSION_DIR/eden_03_meadow.png" ]; then
    BASE_IMAGE="$SESSION_DIR/eden_03_meadow.png"
elif [ -f "$SESSION_DIR/eden_05_tree.png" ]; then
    BASE_IMAGE="$SESSION_DIR/eden_05_tree.png"
else
    echo "❌ No suitable image found for thumbnail"
    exit 1
fi

echo "Creating thumbnail from: $(basename "$BASE_IMAGE")"

# Create thumbnail with text overlay
ffmpeg -i "$BASE_IMAGE" \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,\
pad=1280:720:(ow-iw)/2:(oh-ih)/2,\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:\
text='GARDEN OF EDEN':fontcolor=white:fontsize=96:bordercolor=black:borderw=4:\
x=(w-text_w)/2:y=100,\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf:\
text='Guided Meditation Journey':fontcolor=white:fontsize=48:bordercolor=black:borderw=3:\
x=(w-text_w)/2:y=220,\
drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:\
text='25 Minutes | Binaural Beats':fontcolor=yellow:fontsize=36:bordercolor=black:borderw=2:\
x=(w-text_w)/2:y=650" \
  -vframes 1 -q:v 2 -y \
  "$OUTPUT_DIR/thumbnail_final.jpg"

echo "✅ Thumbnail created: $OUTPUT_DIR/thumbnail_final.jpg"
```

### Video Metadata

**Title Format:**
```
[Theme] Guided Meditation | [Duration] Minutes | Binaural Beats | [Special Features]
```

**Garden of Eden Example:**
```
Garden of Eden Guided Meditation | 25 Minutes | Deep Theta Binaural Beats | Hypnotic Journey
```

**Description Template:**

```
🌳 GARDEN OF EDEN - GUIDED MEDITATION JOURNEY 🌳

Experience a profound 25-minute hypnotic meditation journey through the mythical Garden of Eden. This guided meditation combines:

✨ Professional hypnotic voice guidance
🧠 Theta-wave binaural beats (4-8 Hz)
🎨 Beautiful meditation imagery
🌈 Chakra-based color therapy
🌿 Deep relaxation and transformation

TIMESTAMPS:
0:00 - Pre-Talk: Journey Overview
2:30 - Induction: Deep Relaxation
8:00 - Paradise Meadow: Heart Opening
13:30 - Transformation: Releasing Limitations
17:00 - Tree of Life: Chakra Activation
20:00 - Divine Light: Crown Chakra
23:00 - Return: Integration & Awakening

BEST EXPERIENCED WITH:
🎧 Headphones (required for binaural beats)
🛋️ Comfortable position (sitting or lying down)
🕯️ Quiet environment
⏰ Uninterrupted time

SAFETY NOTE:
Do not listen while driving or operating machinery. If you need to wake fully at any time, simply open your eyes.

---

🔔 Subscribe for more guided meditations
💬 Share your experience in the comments
🌟 Like if this meditation resonated with you

---

#GuidedMeditation #BinauralBeats #HypnoticMeditation #ThetaWaves #Relaxation #Mindfulness #Spirituality #ChakraHealing #DeepMeditation
```

**Tags (50 max):**
```
guided meditation, binaural beats, theta waves, hypnosis, deep relaxation,
meditation music, sleep meditation, healing meditation, spiritual journey,
chakra meditation, visualization, mindfulness, stress relief, anxiety relief,
inner peace, consciousness, transformation, garden of eden, paradise meditation,
hypnotic voice, meditation for beginners, 25 minute meditation
```

### Upload Settings

**Category**: Education or Howto & Style
**Language**: English
**Privacy**: Public
**License**: Standard YouTube License
**Comments**: Enabled (moderate)
**Age Restriction**: None

**Playlist Suggestions**:
- "Guided Meditations"
- "Binaural Beat Meditations"
- "Transformational Journeys"
- "25-Minute Meditations"

---

## 11. Quality Control Checklist

### Pre-Production Checklist

- [ ] Script completed and proofread
- [ ] Timing calculated (target duration determined)
- [ ] Audio generation method selected
- [ ] Binaural beat frequencies mapped to script sections
- [ ] Image prompts written
- [ ] All required tools installed and tested

### Audio Quality Checklist

- [ ] Voice is clear and understandable
- [ ] Pacing is slow and deliberate (no rushing)
- [ ] Pauses are appropriate length
- [ ] Binaural beats are present in stereo
- [ ] Binaural beats are audible but subtle (-20dB)
- [ ] No audio clipping or distortion
- [ ] Smooth fade in/out (3-5 seconds)
- [ ] Total duration matches target

### Visual Quality Checklist

- [ ] All images are 1920x1080 resolution
- [ ] Images match script sections thematically
- [ ] Consistent visual style across all images
- [ ] No disturbing or jarring imagery
- [ ] Colors are calming and meditation-appropriate
- [ ] All 7 images appear in video (verify with frame extraction)
- [ ] Image fades are smooth (2-second transitions)
- [ ] Background gradient transitions are imperceptible
- [ ] Title overlay is readable and properly timed (0-5 seconds)

### Technical Quality Checklist

- [ ] Video resolution: 1920x1080 (1080p)
- [ ] Frame rate: 30fps
- [ ] Video codec: H.264 (libx264)
- [ ] Video quality: CRF 18 or better
- [ ] Audio codec: AAC
- [ ] Audio bitrate: 192kbps or better
- [ ] Audio is stereo (required for binaural beats)
- [ ] Video and audio are synchronized
- [ ] No rendering artifacts or glitches
- [ ] File size is reasonable (<500MB for 25 min)

### YouTube Readiness Checklist

- [ ] Thumbnail created (1280x720, eye-catching)
- [ ] Title is compelling and SEO-friendly
- [ ] Description is detailed with timestamps
- [ ] Tags are relevant and comprehensive
- [ ] End screen elements added
- [ ] Cards added at key moments (subscribe, playlists)
- [ ] Closed captions uploaded (optional but recommended)

### Final Verification

Before uploading, perform these tests:

```bash
# 1. Check video information
ffprobe garden_of_eden_FINAL.mp4

# 2. Extract test frames at each section
ffmpeg -i garden_of_eden_FINAL.mp4 -ss 00:01:00 -vframes 1 verify_01.jpg
ffmpeg -i garden_of_eden_FINAL.mp4 -ss 00:05:00 -vframes 1 verify_02.jpg
ffmpeg -i garden_of_eden_FINAL.mp4 -ss 00:10:00 -vframes 1 verify_03.jpg
ffmpeg -i garden_of_eden_FINAL.mp4 -ss 00:15:00 -vframes 1 verify_04.jpg
ffmpeg -i garden_of_eden_FINAL.mp4 -ss 00:18:00 -vframes 1 verify_05.jpg
ffmpeg -i garden_of_eden_FINAL.mp4 -ss 00:21:00 -vframes 1 verify_06.jpg
ffmpeg -i garden_of_eden_FINAL.mp4 -ss 00:24:00 -vframes 1 verify_07.jpg

# 3. Visually inspect all extracted frames
# All 7 images should be visible and correct

# 4. Listen to first 2 minutes with headphones
# Verify binaural beats are present (subtle pulsing in stereo)

# 5. Scrub through entire video
# Check for any glitches, artifacts, or missing sections
```

---

## 12. Technical Troubleshooting

### Common Issues & Solutions

#### Issue 1: Only 1-2 Images Appear in Video

**Symptoms**: Video plays but only shows first couple of images, rest are missing

**Root Cause**: FFmpeg `fade` filter uses frame numbers (0-indexed per input), but `overlay enable` uses video timeline seconds. This mismatch breaks the overlay chain.

**Solution**: Use `geq` filter for time-based alpha manipulation instead of `fade` filter.

**Fix**:
```python
# WRONG (frame-based)
fade_filter = f"fade=in:0:{fade_frames},fade=out:{duration*30-fade_frames}:{fade_frames}"

# CORRECT (time-based)
alpha_expr = f"'if(lt(T,{start_sec}),0,if(lt(T,{end_sec}),255,0))'"
geq_filter = f"geq=lum='p(X,Y)':cb='p(X,Y)':cr='p(X,Y)':a={alpha_expr}"
```

See [composite_images.py](#image-compositing) for complete working implementation.

#### Issue 2: Binaural Beats Not Working

**Symptoms**: No perceived effect, audio sounds normal

**Possible Causes**:
1. Not using headphones (binaural beats REQUIRE stereo separation)
2. Binaural beats too quiet (should be -20dB, audible as subtle background)
3. Mono audio output (check with `ffprobe`)
4. Wrong frequency range (meditation requires 4-10 Hz)

**Solutions**:
```bash
# Check if audio is stereo
ffprobe -show_streams garden_of_eden_FINAL.mp4 | grep channels
# Should show: channels=2

# Test binaural beat generation
python3 -c "
from pydub.generators import Sine
from pydub import AudioSegment
left = Sine(200).to_audio_segment(duration=5000)
right = Sine(206).to_audio_segment(duration=5000)  # 6 Hz beat
stereo = AudioSegment.from_mono_audiosegments(left, right)
stereo.export('test_binaural.wav', format='wav')
print('Test binaural beat created. Listen with HEADPHONES.')
"
```

#### Issue 3: Frame Generation Takes Forever

**Symptoms**: Generating 45,000 frames takes multiple hours

**Solutions**:
1. Lower resolution (1280x720 instead of 1920x1080)
2. Reduce total duration (20 minutes = 36,000 frames)
3. Lower frame rate (24fps instead of 30fps)
4. Use simpler gradients (solid colors instead of complex blends)

```python
# Optimized settings
generator = VideoBackgroundGenerator(
    width=1280,  # Down from 1920
    height=720,  # Down from 1080
    fps=24,      # Down from 30
    duration_sec=1200  # 20 minutes instead of 25
)
```

#### Issue 4: Video File Too Large

**Symptoms**: Final MP4 is 1-2 GB (too large for YouTube)

**Solutions**:
1. Increase CRF value (18→23 for smaller file, still good quality)
2. Use preset 'medium' instead of 'slow'
3. Reduce audio bitrate (192k→128k)

```bash
# Re-encode with smaller size
ffmpeg -i garden_of_eden_FINAL.mp4 \
  -c:v libx264 -crf 23 -preset medium \
  -c:a aac -b:a 128k \
  garden_of_eden_FINAL_compressed.mp4
```

**YouTube limits**: 256 GB or 12 hours (whichever is less) - you should be fine!

#### Issue 5: Audio/Video Out of Sync

**Symptoms**: Voice doesn't match visuals, images appear at wrong times

**Solutions**:
1. Ensure all inputs have same frame rate (30fps)
2. Use `-async 1` flag in FFmpeg
3. Re-generate audio with exact duration match

```bash
# Check video duration
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 video.mp4

# Check audio duration
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 audio.mp3

# If mismatch, trim longer one to match shorter
ffmpeg -i longer.mp4 -t 1500 -c copy output.mp4
```

#### Issue 6: Edge TTS Voice Sounds Robotic

**Symptoms**: Voice lacks emotion, sounds too synthetic

**Solutions**:
1. Add more SSML markup (prosody, emphasis, breaks)
2. Try different voice (see voice list)
3. Slow down rate further (-25% or -30%)
4. Add subtle background music to mask TTS artifacts

```python
# Enhanced SSML
ssml_script = f"""<speak version='1.0'>
    <voice name='en-US-AvaMultilingualNeural'>
        <prosody rate='-25%' pitch='-5%' volume='medium'>
            <emphasis level='moderate'>Welcome</emphasis> to this meditation...
            <break time='3s'/>
            Allow yourself to <emphasis>relax</emphasis>...
        </prosody>
    </voice>
</speak>"""
```

#### Issue 7: Images Look Pixelated in Video

**Symptoms**: Generated images appear blurry or low-quality

**Solutions**:
1. Generate images at higher resolution (2560x1440, then downscale)
2. Use PNG instead of JPG (no compression artifacts)
3. Increase Stable Diffusion steps (50-75 instead of 20-30)
4. Use upscaler (Real-ESRGAN, waifu2x)

```bash
# Upscale image before using
ffmpeg -i eden_01_pretalk.png -vf "scale=3840:2160:flags=lanczos" eden_01_pretalk_4k.png
```

---

## Summary Workflow

**Complete End-to-End Process:**

```
1. WRITE SCRIPT (2-4 hours)
   ↓
2. GENERATE AUDIO (10-20 minutes)
   ↓
3. CREATE BINAURAL BEATS (5-10 minutes)
   ↓
4. MIX AUDIO (5 minutes)
   ↓
5. GENERATE IMAGES (1-2 hours)
   ↓
6. CREATE VIDEO BACKGROUND (50 minutes)
   ↓
7. COMPOSITE IMAGES (40-50 minutes)
   ↓
8. ADD TITLES (2-3 minutes)
   ↓
9. COMBINE VIDEO + AUDIO (1-2 minutes)
   ↓
10. CREATE THUMBNAIL (5 minutes)
   ↓
11. UPLOAD TO YOUTUBE (10-30 minutes)
```

**Total Time**: 5-8 hours (mostly processing time)
**Total Cost**: $0 (100% free and open-source)

---

## Files Required for Replication

Save these files in your session directory:

1. **generate_video_background.py** - Background frame generator
2. **compile_video.py** - Frame-to-video compiler
3. **composite_images.py** - Image compositor (FINAL version)
4. **create_final_video.sh** - Master assembly script
5. **create_thumbnail.sh** - Thumbnail generator
6. **generate_audio_edge_tts.py** - Audio generation script
7. **create_binaural_beats.py** - Frequency track generator
8. **mix_ultimate_audio.py** - Final audio mixer

All scripts are documented in this manual with complete, working code.

---

## Credits & License

**Tools Used:**
- Python 3.x (PSF License)
- FFmpeg (GPL/LGPL)
- Edge TTS (MIT License)
- Pillow (PIL - HPND License)
- Stable Diffusion (CreativeML Open RAIL-M License)

**This Production Manual**: Public Domain (CC0)

**Generated Content**: Your meditation videos and scripts are yours to use freely. Consider crediting the open-source tools used.

---

**End of Production Manual**

For questions, issues, or improvements, consult:
- FFmpeg documentation: https://ffmpeg.org/documentation.html
- Edge TTS repo: https://github.com/rany2/edge-tts
- Stable Diffusion guides: https://stable-diffusion-art.com/

Happy creating! 🧘‍♀️✨
