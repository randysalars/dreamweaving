#!/usr/bin/env python3
"""
Stable Diffusion API Client for Dreamweaver

Interfaces with AUTOMATIC1111 WebUI API for image generation.
Optimized for CPU-only inference with Neural Network Navigator style prompts.

Usage:
    from sd_api_client import SDAPIClient

    client = SDAPIClient()
    image_path = client.generate_image(
        prompt="vast neural network landscape, glowing synapses, cosmic void",
        output_path="output/scene_01.png"
    )
"""

import base64
import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any
import requests


class SDAPIClient:
    """Client for AUTOMATIC1111 Stable Diffusion WebUI API."""

    DEFAULT_URL = "http://127.0.0.1:7860"

    # Neural Network Navigator style defaults
    DEFAULT_NEGATIVE_PROMPT = (
        "blurry, low quality, pixelated, text, watermark, signature, "
        "oversaturated, cartoon, anime, illustration, painting, drawing, "
        "deformed, distorted, disfigured, bad anatomy, wrong proportions"
    )

    # Style presets for Dreamweaver sessions
    STYLE_PRESETS = {
        "neural_network": {
            "suffix": ", bioluminescent neural pathways, cyan and magenta glow, "
                     "cosmic void background, sacred geometry, ethereal atmosphere, "
                     "8k resolution, hyper-detailed, cinematic lighting",
            "negative": "text, watermark, cartoon, anime, blurry, low quality"
        },
        "sacred_light": {
            "suffix": ", golden divine light, ethereal glow, sacred geometry, "
                     "volumetric lighting, heavenly atmosphere, mystical, "
                     "8k resolution, cinematic, photorealistic",
            "negative": "dark, gloomy, text, watermark, cartoon, blurry"
        },
        "cosmic_journey": {
            "suffix": ", deep space, nebula, starfield, cosmic dust, "
                     "purple and blue tones, ethereal, vast expanse, "
                     "8k resolution, cinematic, hyper-detailed",
            "negative": "text, watermark, cartoon, anime, blurry, low quality"
        },
        "garden_eden": {
            "suffix": ", lush paradise garden, golden light filtering through trees, "
                     "crystal clear water, vibrant flowers, peaceful atmosphere, "
                     "8k resolution, photorealistic, ethereal",
            "negative": "dead plants, dark, gloomy, text, watermark, blurry"
        }
    }

    def __init__(self, api_url: str = None, timeout: int = 300):
        """
        Initialize the SD API client.

        Args:
            api_url: URL of the AUTOMATIC1111 API (default: http://127.0.0.1:7860)
            timeout: Request timeout in seconds (CPU generation is slow)
        """
        self.api_url = api_url or self.DEFAULT_URL
        self.timeout = timeout
        self._session = requests.Session()

    def is_available(self) -> bool:
        """Check if the API server is running and responsive."""
        try:
            response = self._session.get(
                f"{self.api_url}/internal/ping",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def wait_for_server(self, max_wait: int = 60, poll_interval: int = 2) -> bool:
        """
        Wait for the server to become available.

        Args:
            max_wait: Maximum seconds to wait
            poll_interval: Seconds between checks

        Returns:
            True if server became available, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self.is_available():
                return True
            time.sleep(poll_interval)
        return False

    def get_models(self) -> list:
        """Get list of available SD models."""
        try:
            response = self._session.get(
                f"{self.api_url}/sdapi/v1/sd-models",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting models: {e}")
            return []

    def get_current_model(self) -> Optional[str]:
        """Get the currently loaded model name."""
        try:
            response = self._session.get(
                f"{self.api_url}/sdapi/v1/options",
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("sd_model_checkpoint")
        except requests.exceptions.RequestException as e:
            print(f"Error getting current model: {e}")
            return None

    def generate_image(
        self,
        prompt: str,
        output_path: str,
        negative_prompt: str = None,
        style_preset: str = None,
        width: int = 512,
        height: int = 512,
        steps: int = 8,
        cfg_scale: float = 7.0,
        seed: int = -1,
        sampler_name: str = "Euler a"
    ) -> Optional[str]:
        """
        Generate an image using the SD API.

        Args:
            prompt: Text description of the image
            output_path: Where to save the generated image
            negative_prompt: What to avoid in the image
            style_preset: One of STYLE_PRESETS keys for automatic styling
            width: Image width (512 recommended for CPU)
            height: Image height (512 recommended for CPU)
            steps: Number of sampling steps (6-10 for CPU, 20+ for GPU)
            cfg_scale: Classifier-free guidance scale (7-8 typical)
            seed: Random seed (-1 for random)
            sampler_name: Sampling method

        Returns:
            Path to saved image, or None if failed
        """
        # Apply style preset if specified
        if style_preset and style_preset in self.STYLE_PRESETS:
            preset = self.STYLE_PRESETS[style_preset]
            prompt = prompt + preset["suffix"]
            if negative_prompt is None:
                negative_prompt = preset["negative"]

        if negative_prompt is None:
            negative_prompt = self.DEFAULT_NEGATIVE_PROMPT

        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "sampler_name": sampler_name,
            "batch_size": 1,
            "n_iter": 1
        }

        print(f"Generating image with prompt: {prompt[:80]}...")
        print(f"Settings: {width}x{height}, {steps} steps, CFG {cfg_scale}")

        try:
            start_time = time.time()
            response = self._session.post(
                f"{self.api_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            elapsed = time.time() - start_time
            print(f"Generation completed in {elapsed:.1f}s")

            result = response.json()

            if "images" not in result or not result["images"]:
                print("Error: No images in response")
                return None

            # Decode and save the first image
            image_data = base64.b64decode(result["images"][0])

            # Ensure output directory exists
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                f.write(image_data)

            print(f"Image saved to: {output_path}")
            return str(output_path)

        except requests.exceptions.Timeout:
            print(f"Error: Generation timed out after {self.timeout}s")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error generating image: {e}")
            return None

    def generate_scene_image(
        self,
        scene_description: str,
        output_path: str,
        scene_number: int = 1,
        style_preset: str = "neural_network",
        aspect_ratio: str = "16:9"
    ) -> Optional[str]:
        """
        Generate a scene image for Dreamweaver videos.

        Optimized for video backgrounds with appropriate dimensions.

        Args:
            scene_description: Description of the scene
            output_path: Where to save the image
            scene_number: Scene number (affects seed for consistency)
            style_preset: Visual style to apply
            aspect_ratio: "16:9" or "1:1"

        Returns:
            Path to saved image, or None if failed
        """
        # Determine dimensions based on aspect ratio
        # Using smaller sizes for CPU efficiency, will upscale later
        if aspect_ratio == "16:9":
            width, height = 768, 432  # 16:9 ratio, CPU-friendly
        else:
            width, height = 512, 512

        # Use scene number as seed base for reproducibility
        seed = scene_number * 1000

        return self.generate_image(
            prompt=scene_description,
            output_path=output_path,
            style_preset=style_preset,
            width=width,
            height=height,
            steps=8,  # Lower steps for CPU
            cfg_scale=7.5,
            seed=seed
        )

    def generate_batch(
        self,
        prompts: list,
        output_dir: str,
        style_preset: str = None,
        **kwargs
    ) -> list:
        """
        Generate multiple images in sequence.

        Args:
            prompts: List of (filename, prompt) tuples
            output_dir: Directory to save images
            style_preset: Style to apply to all
            **kwargs: Additional arguments passed to generate_image

        Returns:
            List of paths to generated images
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = []
        for i, (filename, prompt) in enumerate(prompts):
            output_path = output_dir / filename
            print(f"\n[{i+1}/{len(prompts)}] Generating: {filename}")

            result = self.generate_image(
                prompt=prompt,
                output_path=str(output_path),
                style_preset=style_preset,
                seed=i * 1000,  # Consistent seeds
                **kwargs
            )

            if result:
                results.append(result)
            else:
                print(f"Failed to generate: {filename}")

        return results


def generate_neural_network_scenes(output_dir: str, client: SDAPIClient = None) -> list:
    """
    Generate all 8 scene images for Neural Network Navigator.

    Args:
        output_dir: Directory to save images
        client: Optional SDAPIClient instance

    Returns:
        List of generated image paths
    """
    if client is None:
        client = SDAPIClient()

    if not client.is_available():
        print("Error: SD API server not available at", client.api_url)
        print("Start the server with: cd ~/sd-webui && ./webui.sh")
        return []

    scenes = [
        ("scene_01_welcome.png",
         "Person standing at threshold of infinite neural cosmos, silhouette backlit by "
         "soft bioluminescent threads of cyan and gold light stretching into darkness, "
         "sacred geometry patterns in background, ethereal mist at feet"),

        ("scene_02_induction.png",
         "Figure descending through layers of soft glowing neural clouds, each layer "
         "different shade from violet to deep blue to cyan, gentle spiral staircase "
         "of light particles, dreamlike descent into consciousness"),

        ("scene_03_neural_vista.png",
         "Vast infinite neural network landscape stretching to horizons, millions of "
         "glowing synaptic threads in cyan gold and magenta connecting luminous nodes, "
         "standing figure gazing at magnificent web of consciousness"),

        ("scene_04_learning_core.png",
         "Magnificent luminous sphere floating at center of neural hub, thousands of "
         "glowing pathways converging like roots to tree of light, sphere rotating "
         "slowly pulsing with intelligent golden-white radiance"),

        ("scene_05_navigator_guide.png",
         "Ethereal guide figure made of pure intelligent light in neural corridor, "
         "humanoid form of flowing luminous threads and sacred geometry, wise presence "
         "radiating soft cyan and gold light"),

        ("scene_06_expansion.png",
         "Explosive moment of neural pathway creation, new threads of brilliant light "
         "branching outward, connections forming creating bridges of understanding, "
         "cascade of golden synaptic sparks, neuroplasticity in action"),

        ("scene_07_integration.png",
         "Figure walking along wide pathway of soft golden light, carrying aura of "
         "integrated wisdom, neural network brighter and more connected, peaceful "
         "journey homeward, starlight atmosphere"),

        ("scene_08_awakening.png",
         "Person opening eyes with subtle neural light in irises, transition from "
         "inner cosmos to outer world, peaceful expression, soft morning light "
         "mixing with fading bioluminescent threads")
    ]

    print(f"Generating {len(scenes)} Neural Network Navigator scenes...")
    print(f"Output directory: {output_dir}")
    print("=" * 60)

    results = client.generate_batch(
        prompts=scenes,
        output_dir=output_dir,
        style_preset="neural_network",
        steps=8,
        cfg_scale=7.5
    )

    print("\n" + "=" * 60)
    print(f"Generated {len(results)}/{len(scenes)} images successfully")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stable Diffusion API Client")
    parser.add_argument("--check", action="store_true", help="Check if server is available")
    parser.add_argument("--models", action="store_true", help="List available models")
    parser.add_argument("--generate", type=str, help="Generate image from prompt")
    parser.add_argument("--output", type=str, default="output.png", help="Output path")
    parser.add_argument("--style", type=str, help="Style preset to use")
    parser.add_argument("--neural-scenes", type=str, help="Generate Neural Network Navigator scenes to directory")

    args = parser.parse_args()

    client = SDAPIClient()

    if args.check:
        if client.is_available():
            print("Server is available!")
            model = client.get_current_model()
            print(f"Current model: {model}")
        else:
            print("Server is not available")
            print(f"Expected at: {client.api_url}")

    elif args.models:
        models = client.get_models()
        print("Available models:")
        for m in models:
            print(f"  - {m.get('title', m.get('model_name', 'Unknown'))}")

    elif args.generate:
        result = client.generate_image(
            prompt=args.generate,
            output_path=args.output,
            style_preset=args.style
        )
        if result:
            print(f"Success! Image saved to: {result}")

    elif args.neural_scenes:
        results = generate_neural_network_scenes(args.neural_scenes, client)
        print(f"\nGenerated {len(results)} scene images")

    else:
        parser.print_help()
