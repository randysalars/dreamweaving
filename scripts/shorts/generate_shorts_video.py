#!/usr/bin/env python3
"""
Generate Shorts Video with Scrolling Subtitles

Interactive CLI tool that:
1. Prompts for image folder path
2. Prompts for script text (one line per slide)
3. Generates TTS audio per slide
4. Assembles video with scrolling subtitles + URL overlay
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from google.cloud import texttospeech

# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, continue without it

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Check if Ollama is available
def check_ollama_available() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False

OLLAMA_AVAILABLE = check_ollama_available()


def parse_script_input() -> list:
    """
    Parse multi-line script input with 'Slide X:' markers.

    Example input:
        Slide 1: Christmas Eve. Pause here.
        Let the day fall away.

        Slide 2: Long before joy had a name...
        Darkness held its breath.
        END

    Returns list of slide texts.
    """
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break

        if line.strip().upper() == 'END':
            break
        lines.append(line)

    # Parse slides from collected lines
    slides = {}
    current_slide = None
    current_text = []

    # Match slide header, ignore title after em-dash
    slide_pattern = re.compile(r'^[#*\s]*[Ss]lide\s*(\d+)\s*[:\-—]')

    for line in lines:
        match = slide_pattern.match(line.strip())
        if match:
            # Save previous slide if exists
            if current_slide is not None:
                slides[current_slide] = ' '.join(current_text).strip()

            # Start new slide
            current_slide = int(match.group(1))
            current_text = []  # Start fresh, don't capture header text
        elif current_slide is not None and line.strip():
            # Skip markdown horizontal rules (---, ___, ***)
            if re.match(r'^[-_*]{3,}\s*$', line.strip()):
                continue
            # Strip markdown formatting from content
            clean_line = re.sub(r'\*+', '', line.strip())  # Remove asterisks
            clean_line = re.sub(r'^#+\s*', '', clean_line)  # Remove leading hashes
            clean_line = re.sub(r'^[-_]{2,}\s*', '', clean_line)  # Remove leading dashes/underscores
            if clean_line:
                current_text.append(clean_line)

    # Save last slide
    if current_slide is not None:
        slides[current_slide] = ' '.join(current_text).strip()

    # Convert to ordered list
    if not slides:
        return []

    max_slide = max(slides.keys())
    result = []
    for i in range(1, max_slide + 1):
        if i in slides:
            result.append(slides[i])
        else:
            result.append(f"[Slide {i} missing]")

    return result


def generate_script_from_topic(topic: str, num_slides: int) -> list:
    """Generate slide scripts using Claude API."""
    if not ANTHROPIC_AVAILABLE:
        print("Error: anthropic package not installed. Run: pip install anthropic")
        return []

    # Check for API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("\nError: ANTHROPIC_API_KEY not found in environment.")
        print("To use script generation, you need an Anthropic API key:")
        print("  1. Go to https://console.anthropic.com/")
        print("  2. Create an API key")
        print("  3. Add to your .env file: ANTHROPIC_API_KEY=sk-ant-api03-xxxxx")
        print("\nNote: Claude Pro subscription is separate from API access.")
        return []

    print(f"\nGenerating {num_slides} slides for topic: {topic}")
    print("Please wait...")

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Generate {num_slides} short, poetic slides for a meditative/spiritual video about: {topic}

Requirements:
- Each slide should be 1-3 sentences (15-30 words)
- Tone: calm, reflective, spiritual, comforting
- No markdown formatting, no asterisks, no headers
- Just the words to be spoken aloud
- Build a gentle emotional arc across the slides
- End with a sense of peace or blessing

Format your response EXACTLY like this (just the text, nothing else):
Slide 1: [text for slide 1]
Slide 2: [text for slide 2]
...and so on for all {num_slides} slides"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse response using the same parser
    response_text = response.content[0].text
    lines = response_text.strip().split('\n')

    slides = {}
    current_slide = None
    current_text = []
    slide_pattern = re.compile(r'^[Ss]lide\s*(\d+)\s*[:\-]\s*(.*)$')

    for line in lines:
        match = slide_pattern.match(line.strip())
        if match:
            if current_slide is not None:
                slides[current_slide] = ' '.join(current_text).strip()
            current_slide = int(match.group(1))
            initial_text = match.group(2).strip()
            current_text = [initial_text] if initial_text else []
        elif current_slide is not None and line.strip():
            current_text.append(line.strip())

    if current_slide is not None:
        slides[current_slide] = ' '.join(current_text).strip()

    # Convert to ordered list
    result = []
    for i in range(1, num_slides + 1):
        if i in slides:
            result.append(slides[i])
        else:
            result.append(f"[Slide {i} missing]")

    return result


def generate_script_with_ollama(topic: str, num_slides: int, model: str = "llama3.2:latest") -> list:
    """Generate slide scripts using local Ollama model."""
    import requests

    print(f"\nGenerating {num_slides} slides for topic: {topic}")
    print(f"Using Ollama model: {model}")
    print("Please wait...")

    prompt = f"""Generate {num_slides} short, poetic slides for a meditative/spiritual video about: {topic}

Requirements:
- Each slide should be 1-3 sentences (15-30 words)
- Tone: calm, reflective, spiritual, comforting
- No markdown formatting, no asterisks, no headers
- Just the words to be spoken aloud
- Build a gentle emotional arc across the slides
- End with a sense of peace or blessing

Format your response EXACTLY like this (just the text, nothing else):
Slide 1: [text for slide 1]
Slide 2: [text for slide 2]
...and so on for all {num_slides} slides"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120  # Allow up to 2 minutes for generation
        )
        response.raise_for_status()
        response_text = response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama: {e}")
        return []

    # Parse response
    lines = response_text.strip().split('\n')

    slides = {}
    current_slide = None
    current_text = []
    slide_pattern = re.compile(r'^[Ss]lide\s*(\d+)\s*[:\-]\s*(.*)$')

    for line in lines:
        match = slide_pattern.match(line.strip())
        if match:
            if current_slide is not None:
                slides[current_slide] = ' '.join(current_text).strip()
            current_slide = int(match.group(1))
            initial_text = match.group(2).strip()
            current_text = [initial_text] if initial_text else []
        elif current_slide is not None and line.strip():
            current_text.append(line.strip())

    if current_slide is not None:
        slides[current_slide] = ' '.join(current_text).strip()

    # Convert to ordered list
    result = []
    for i in range(1, num_slides + 1):
        if i in slides:
            result.append(slides[i])
        else:
            result.append(f"[Slide {i} missing]")

    return result


def generate_images_with_sd(topic: str, num_images: int, output_dir: str) -> bool:
    """Generate vertical images for shorts using Stable Diffusion."""
    try:
        import torch
        from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
        from PIL import Image
    except ImportError:
        print("Error: diffusers/torch not installed. Run: pip install diffusers transformers accelerate torch")
        return False

    print(f"\nGenerating {num_images} images for: {topic}")
    print("This may take several minutes on CPU...")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load pipeline
    print("Loading Stable Diffusion model...")
    model_path = os.path.expanduser("~/sd-webui/models/Stable-diffusion/sd-v1-5-pruned-emaonly.safetensors")

    if os.path.exists(model_path):
        print(f"Using local model: {model_path}")
        pipe = StableDiffusionPipeline.from_single_file(
            model_path,
            torch_dtype=torch.float32,
            use_safetensors=True
        )
    else:
        print("Downloading model from HuggingFace...")
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float32,
            use_safetensors=True
        )

    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    pipe = pipe.to("cpu")
    try:
        pipe.enable_attention_slicing()
    except:
        pass

    # Style suffix for Christmas/spiritual content
    style_suffix = (
        ", ethereal golden light, sacred atmosphere, soft glow, "
        "spiritual, peaceful, divine light rays, cinematic, "
        "8k resolution, professional photography"
    )
    negative_prompt = "text, watermark, cartoon, anime, blurry, low quality, deformed, ugly, dark, gloomy"

    # Generate prompts based on topic
    base_prompts = [
        f"Christmas scene {topic}, holy night, stars",
        f"Divine light entering through clouds, {topic}",
        f"Sacred heart with golden rays, {topic}",
        f"Peaceful winter night with stars, {topic}",
        f"Light descending from heaven, {topic}",
        f"Ethereal golden glow surrounding person, {topic}",
        f"Christmas blessing scene, {topic}, peace and hope",
    ]

    # Generate images (vertical 9:16 aspect ratio for shorts)
    # Generate at 384x672 (maintains 9:16), then upscale
    width, height = 384, 672

    for i in range(num_images):
        prompt = base_prompts[i % len(base_prompts)] + style_suffix
        print(f"\nGenerating image {i+1}/{num_images}...")
        print(f"  Prompt: {prompt[:60]}...")

        with torch.no_grad():
            result = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=15,
                guidance_scale=7.5
            )

        img = result.images[0]

        # Upscale to 816x1456 (matching existing shorts dimensions)
        img = img.resize((816, 1456), Image.LANCZOS)

        output_path = os.path.join(output_dir, f"{i+1}.png")
        img.save(output_path, "PNG")
        print(f"  Saved: {output_path}")

    print(f"\nGenerated {num_images} images in {output_dir}")
    return True


def get_user_input():
    """Prompt user for image path and script text."""
    print("\n" + "="*60)
    print("  SHORTS VIDEO GENERATOR")
    print("="*60 + "\n")

    # Prompt 1: Image source
    print("How would you like to provide images?")
    print("  1. Enter path to existing images folder")
    print("  2. Generate images with Stable Diffusion")
    image_choice = input("> ").strip()

    if image_choice == "2":
        # Generate images with SD
        topic = input("\nEnter topic/theme for images (e.g., 'Christmas light', 'divine peace'):\n> ").strip()
        if not topic:
            topic = "Christmas divine light spiritual"

        num_images = input("Number of images to generate (default 7): ").strip()
        num_images = int(num_images) if num_images.isdigit() else 7

        # Create output directory
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.expanduser(f"~/Projects/dreamweaving/output/shorts/sd_{timestamp}")

        success = generate_images_with_sd(topic, num_images, output_dir)
        if not success:
            print("Image generation failed. Please provide an existing image path.")
            image_choice = "1"
        else:
            image_path = output_dir
            images = sorted([f for f in os.listdir(image_path) if f.endswith('.png') and f[0].isdigit()])
            print(f"\nUsing generated images: {', '.join(images)}")

    if image_choice != "2" or 'image_path' not in dir():
        # Manual path input
        while True:
            image_path = input("\nEnter path to images folder (containing 1.png, 2.png, etc.):\n> ").strip()
            image_path = os.path.expanduser(image_path)

            if not os.path.isdir(image_path):
                print(f"Error: Directory not found: {image_path}")
                continue

            # Count images
            images = sorted([f for f in os.listdir(image_path) if f.endswith('.png') and f[0].isdigit()])
            if not images:
                print("Error: No numbered PNG images found (1.png, 2.png, etc.)")
                continue

            print(f"Found {len(images)} images: {', '.join(images)}")
            break

    # Prompt 2: Choose script input method
    print("\nHow would you like to provide the script?")
    print("  1. Paste script with slide markers")
    if OLLAMA_AVAILABLE:
        print("  2. Generate script with Ollama (local, free)")
    if ANTHROPIC_AVAILABLE:
        print("  3. Generate script with Claude API (requires API key)")
    choice = input("> ").strip()

    slides = None

    # Option 2: Ollama (local)
    if choice == "2" and OLLAMA_AVAILABLE:
        topic = input("\nEnter topic/theme for the video:\n> ").strip()
        if topic:
            # Let user choose model
            print("\nAvailable Ollama models:")
            print("  1. llama3.2 (fast, 2GB)")
            print("  2. qwen3-coder (better quality, 18GB)")
            print("  3. phi3 (balanced, 2.2GB)")
            model_choice = input("Choose model (1-3, default=1): ").strip()
            model_map = {"1": "llama3.2:latest", "2": "qwen3-coder:latest", "3": "phi3:latest"}
            model = model_map.get(model_choice, "llama3.2:latest")

            slides = generate_script_with_ollama(topic, len(images), model)
            if slides:
                print(f"\nGenerated {len(slides)} slides:")
                for i, text in enumerate(slides, 1):
                    print(f"  Slide {i}: {text}")
                confirm = input("\nUse this script? (y/n/r to regenerate): ").strip().lower()
                while confirm == 'r':
                    slides = generate_script_with_ollama(topic, len(images), model)
                    print(f"\nRegenerated {len(slides)} slides:")
                    for i, text in enumerate(slides, 1):
                        print(f"  Slide {i}: {text}")
                    confirm = input("\nUse this script? (y/n/r to regenerate): ").strip().lower()
                if confirm != 'y':
                    print("Script rejected. Falling back to manual input...")
                    slides = None

    # Option 3: Claude API
    elif choice == "3" and ANTHROPIC_AVAILABLE:
        topic = input("\nEnter topic/theme for the video:\n> ").strip()
        if topic:
            slides = generate_script_from_topic(topic, len(images))
            if slides:
                print(f"\nGenerated {len(slides)} slides:")
                for i, text in enumerate(slides, 1):
                    print(f"  Slide {i}: {text}")
                confirm = input("\nUse this script? (y/n/r to regenerate): ").strip().lower()
                while confirm == 'r':
                    slides = generate_script_from_topic(topic, len(images))
                    print(f"\nRegenerated {len(slides)} slides:")
                    for i, text in enumerate(slides, 1):
                        print(f"  Slide {i}: {text}")
                    confirm = input("\nUse this script? (y/n/r to regenerate): ").strip().lower()
                if confirm != 'y':
                    print("Script rejected. Falling back to manual input...")
                    slides = None

    if not slides:
        # Manual paste mode
        print("\nPaste your script with 'Slide X:' markers.")
        print("Example:")
        print("  Slide 1: Christmas Eve. Pause here.")
        print("  Let the day fall away.")
        print("  Slide 2: Long before joy had a name...")
        print("  END")
        print("\nType 'END' on its own line when done:\n")

        slides = parse_script_input()

    if not slides:
        print("Error: No slides parsed from input.")
        sys.exit(1)

    print(f"\nParsed {len(slides)} slides:")
    for i, text in enumerate(slides, 1):
        preview = text[:50] + "..." if len(text) > 50 else text
        print(f"  Slide {i}: {preview}")

    if len(slides) != len(images):
        print(f"\nWarning: {len(slides)} slides parsed, but {len(images)} images found.")
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm != 'y':
            sys.exit(0)

    # Prompt 3: URL overlay
    default_url = "salars.net/xmas/video"
    url = input(f"\nEnter URL for overlay (default: {default_url}):\n> ").strip()
    if not url:
        url = default_url

    return image_path, slides, url, images


def create_ssml_files(image_path: str, slides: list):
    """Create SSML files for each slide."""
    slides_dir = os.path.join(image_path, "slides")
    os.makedirs(slides_dir, exist_ok=True)

    for i, text in enumerate(slides, 1):
        if i == 1:
            # Add 500ms pause at start of first slide
            # Journey voices don't support pitch parameter in SSML
            ssml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<speak>
  <break time="500ms"/>
  <prosody rate="0.95">
    {text}
  </prosody>
</speak>
'''
        else:
            ssml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<speak>
  <prosody rate="0.95">
    {text}
  </prosody>
</speak>
'''
        ssml_path = os.path.join(slides_dir, f"slide{i}.ssml")
        with open(ssml_path, 'w') as f:
            f.write(ssml_content)
        print(f"Created: {ssml_path}")

    return slides_dir


def generate_tts_audio(slides_dir: str, num_slides: int):
    """Generate TTS audio for each slide."""
    print("\nGenerating TTS audio...")
    client = texttospeech.TextToSpeechClient()

    for i in range(1, num_slides + 1):
        ssml_path = os.path.join(slides_dir, f"slide{i}.ssml")
        output_path = os.path.join(slides_dir, f"slide{i}.mp3")

        with open(ssml_path, 'r') as f:
            ssml = f.read()

        synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-F",  # Reliable Neural2 voice
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.95,  # Closer to natural speech
            pitch=-1.0,  # Slightly warmer
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        with open(output_path, 'wb') as f:
            f.write(response.audio_content)

        print(f"Generated: {output_path}")

    return slides_dir


def get_audio_durations(slides_dir: str, num_slides: int) -> list:
    """Get duration of each audio file."""
    durations = []
    for i in range(1, num_slides + 1):
        audio_path = os.path.join(slides_dir, f"slide{i}.mp3")
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'csv=p=0', audio_path],
            capture_output=True, text=True
        )
        duration = float(result.stdout.strip())
        durations.append(duration)
        print(f"Slide {i}: {duration:.3f}s")
    return durations


def concatenate_audio(slides_dir: str, output_path: str, num_slides: int):
    """Concatenate all slide audio files."""
    inputs = ' '.join([f"-i {os.path.join(slides_dir, f'slide{i}.mp3')}" for i in range(1, num_slides + 1)])
    filter_inputs = ''.join([f"[{i}:a]" for i in range(num_slides)])

    cmd = f"ffmpeg -y {inputs} -filter_complex \"{filter_inputs}concat=n={num_slides}:v=0:a=1[out]\" -map \"[out]\" {output_path}"
    subprocess.run(cmd, shell=True, capture_output=True)
    print(f"Concatenated audio: {output_path}")


def assemble_video(image_path: str, images: list, slides: list, durations: list, url: str, output_path: str):
    """Assemble final video with scrolling subtitles."""
    print("\nAssembling video...")

    # Build input arguments
    input_args = []
    for i, (img, dur) in enumerate(zip(images, durations)):
        input_args.extend(['-loop', '1', '-t', str(dur), '-i', os.path.join(image_path, img)])

    # Add audio input
    audio_path = os.path.join(image_path, "combined_voice.mp3")
    input_args.extend(['-i', audio_path])

    # Get image dimensions from first image
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
         '-show_entries', 'stream=width,height', '-of', 'csv=p=0',
         os.path.join(image_path, images[0])],
        capture_output=True, text=True
    )
    width, height = result.stdout.strip().split(',')

    # Build filter_complex
    num_slides = len(images)

    # Scale each input
    scale_filters = []
    for i in range(num_slides):
        scale_filters.append(f"[{i}:v]scale={width}:{height},setsar=1,fps=30[v{i}]")

    # Concat
    concat_inputs = ''.join([f"[v{i}]" for i in range(num_slides)])
    scale_filters.append(f"{concat_inputs}concat=n={num_slides}:v=1:a=0[vconcat]")

    # Calculate cumulative timestamps
    timestamps = [0.0]
    for dur in durations[:-1]:
        timestamps.append(timestamps[-1] + dur)

    # Add scrolling text for each slide
    drawtext_filters = []
    for i, (slide_text, start_time, duration) in enumerate(zip(slides, timestamps, durations)):
        end_time = start_time + duration
        # Escape single quotes in text
        escaped_text = slide_text.replace("'", "'\\''")

        if i == 0:
            drawtext_filters.append(
                f"[vconcat]drawtext=text='{escaped_text}':fontsize=24:fontcolor=white:"
                f"box=1:boxcolor=black@0.8:boxborderw=10:"
                f"x=w-mod(t*100\\,w+tw):y=20:enable='between(t,{start_time},{end_time})'"
            )
        else:
            drawtext_filters.append(
                f"drawtext=text='{escaped_text}':fontsize=24:fontcolor=white:"
                f"box=1:boxcolor=black@0.8:boxborderw=10:"
                f"x=w-mod((t-{start_time})*100\\,w+tw):y=20:enable='between(t,{start_time},{end_time})'"
            )

    # Add URL overlay on last slide
    last_start = timestamps[-1]
    drawtext_filters.append(
        f"drawtext=text='{url}':fontsize=48:fontcolor=gold:"
        f"borderw=4:bordercolor=black:x=(w-text_w)/2:y=h-120:enable='gte(t,{last_start})'[vout]"
    )

    # Combine all filters
    filter_complex = ';'.join(scale_filters) + ';' + ','.join(drawtext_filters)

    # Build ffmpeg command
    cmd = ['ffmpeg', '-y'] + input_args + [
        '-filter_complex', filter_complex,
        '-map', '[vout]', '-map', f'{num_slides}:a',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', '192k', '-shortest',
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr}")
        return False

    print(f"Video created: {output_path}")
    return True


def main():
    # Get user input
    image_path, slides, url, images = get_user_input()

    # Ensure we have matching slides for images
    num_slides = min(len(slides), len(images))
    slides = slides[:num_slides]
    images = images[:num_slides]

    print(f"\nProcessing {num_slides} slides...")

    # Create SSML files
    slides_dir = create_ssml_files(image_path, slides)

    # Generate TTS audio
    generate_tts_audio(slides_dir, num_slides)

    # Get durations
    print("\nGetting audio durations...")
    durations = get_audio_durations(slides_dir, num_slides)

    total_duration = sum(durations)
    print(f"Total duration: {total_duration:.2f}s")

    # Concatenate audio
    combined_audio = os.path.join(image_path, "combined_voice.mp3")
    concatenate_audio(slides_dir, combined_audio, num_slides)

    # Assemble video
    output_video = os.path.join(image_path, "shorts_video.mp4")
    if assemble_video(image_path, images, slides, durations, url, output_video):
        # Copy audio file
        audio_output = os.path.join(image_path, "shorts_audio.mp3")
        subprocess.run(['cp', combined_audio, audio_output])

        print("\n" + "="*60)
        print("  COMPLETE!")
        print("="*60)
        print(f"Video: {output_video}")
        print(f"Audio: {audio_output}")
        print(f"Duration: {total_duration:.2f}s")
    else:
        print("\nError: Video assembly failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
