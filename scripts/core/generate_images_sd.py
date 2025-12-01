#!/usr/bin/env python3
"""
Automated Stable Diffusion Image Generation
Generates high-quality meditation images from text prompts
Uses SDXL for best results
"""

import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from pathlib import Path
import logging
from typing import Optional, List, Dict
from PIL import Image
import json
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageGenerator:
    """Automated image generation using Stable Diffusion XL"""

    def __init__(
        self,
        model_id: str = "stabilityai/stable-diffusion-xl-base-1.0",
        device: Optional[str] = None,
        use_fp16: bool = True,
        enable_optimizations: bool = True
    ):
        """
        Initialize the image generator

        Args:
            model_id: Hugging Face model ID
            device: Device to use ('cuda', 'mps', 'cpu', or None for auto-detect)
            use_fp16: Use half precision for faster inference (requires GPU)
            enable_optimizations: Enable memory optimizations
        """
        # Auto-detect device if not specified
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
                logger.info(f"🎮 CUDA available: {torch.cuda.get_device_name(0)}")
                logger.info(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            elif torch.backends.mps.is_available():
                device = "mps"  # Apple Silicon
                logger.info("🍎 Apple Silicon GPU detected")
            else:
                device = "cpu"
                logger.warning("⚠️  No GPU detected, using CPU (will be slow)")

        self.device = device
        self.use_fp16 = use_fp16 and device == "cuda"

        logger.info(f"🔧 Loading Stable Diffusion XL: {model_id}")
        logger.info(f"📍 Device: {device}")

        # Load model
        dtype = torch.float16 if self.use_fp16 else torch.float32

        try:
            # Check if model is already cached
            from huggingface_hub import scan_cache_dir
            cache_info = scan_cache_dir()
            model_cached = any(model_id in str(repo.repo_id) for repo in cache_info.repos)

            if not model_cached:
                logger.info("📥 First run: Downloading SDXL model (~13 GB)")
                logger.info("⏱️  This will take 10-30 minutes depending on connection")
                logger.info("💡 Model will be cached for future use")

            self.pipe = StableDiffusionXLPipeline.from_pretrained(
                model_id,
                torch_dtype=dtype,
                use_safetensors=True,
                variant="fp16" if self.use_fp16 else None
            )

            # Optimize scheduler for quality
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config,
                use_karras_sigmas=True  # Better quality
            )

            # Move to device
            self.pipe = self.pipe.to(device)

            # Enable memory optimizations
            if enable_optimizations:
                if device == "cuda":
                    # Check VRAM
                    vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9

                    if vram_gb < 12:
                        logger.info("💡 Low VRAM detected, enabling CPU offloading")
                        self.pipe.enable_model_cpu_offload()

                    # Always enable these for better memory efficiency
                    self.pipe.enable_attention_slicing(1)
                    self.pipe.enable_vae_slicing()

                    # Try to enable xformers if available
                    try:
                        self.pipe.enable_xformers_memory_efficient_attention()
                        logger.info("✅ xformers acceleration enabled")
                    except (ImportError, ModuleNotFoundError, RuntimeError):
                        logger.info("ℹ️  xformers not available (install with: pip install xformers)")

            logger.info("✅ Model loaded successfully")

        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            raise

    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "blurry, ugly, duplicate, poorly drawn, deformed, text, watermark, low quality, distorted",
        width: int = 1920,
        height: int = 1080,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        num_images: int = 1
    ) -> List[Image.Image]:
        """
        Generate images from text prompt

        Args:
            prompt: Text description of desired image
            negative_prompt: Things to avoid in the image
            width: Image width (must be divisible by 8)
            height: Image height (must be divisible by 8)
            num_inference_steps: Number of denoising steps (30-80, higher=better quality)
            guidance_scale: How closely to follow prompt (5-15, 7-9 recommended for SDXL)
            seed: Random seed for reproducibility (None=random)
            num_images: Number of images to generate

        Returns:
            List of PIL Image objects
        """
        # Ensure dimensions are divisible by 8
        width = (width // 8) * 8
        height = (height // 8) * 8

        # Set seed if specified
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)

        logger.info(f"\n🎨 Generating {num_images} image(s)...")
        logger.info(f"📝 Prompt: {prompt[:100]}...")
        logger.info(f"📐 Size: {width}x{height}")
        logger.info(f"🔢 Steps: {num_inference_steps}, Guidance: {guidance_scale}")
        if seed:
            logger.info(f"🎲 Seed: {seed}")

        start_time = time.time()

        try:
            # Generate images
            result = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
                num_images_per_prompt=num_images
            )

            images = result.images
            elapsed = time.time() - start_time
            logger.info(f"✅ Generated {len(images)} image(s) in {elapsed:.1f}s")

            return images

        except Exception as e:
            logger.error(f"❌ Error generating image: {e}")
            raise

    def generate_and_save(
        self,
        prompt: str,
        output_path: str,
        negative_prompt: str = "blurry, ugly, duplicate, poorly drawn, deformed, text, watermark, low quality, distorted",
        width: int = 1920,
        height: int = 1080,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        num_candidates: int = 1,
        save_metadata: bool = True
    ) -> str:
        """
        Generate image and save to file

        Args:
            prompt: Text description
            output_path: Path to save image (e.g., 'eden_01_pretalk.png')
            num_candidates: Generate multiple and save all for selection
            save_metadata: Save generation parameters to JSON

        Returns:
            Path to saved image
        """
        images = self.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            seed=seed,
            num_images=num_candidates
        )

        # Save first image
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        images[0].save(output_path, quality=95)
        logger.info(f"💾 Saved to: {output_path}")

        # Save metadata
        if save_metadata:
            metadata = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "seed": seed,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            metadata_path = output_path.parent / f"{output_path.stem}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"📋 Metadata saved to: {metadata_path}")

        # If multiple candidates, save them too
        if num_candidates > 1:
            for idx, img in enumerate(images[1:], start=2):
                candidate_path = output_path.parent / f"{output_path.stem}_candidate{idx}{output_path.suffix}"
                img.save(candidate_path, quality=95)
                logger.info(f"💾 Saved candidate {idx} to: {candidate_path}")

        return str(output_path)


def generate_garden_of_eden_images(
    session_dir: str = "sessions/garden-of-eden",
    quality: str = "high",
    num_candidates: int = 3
):
    """
    Generate all 7 Garden of Eden meditation images

    Args:
        session_dir: Directory to save images
        quality: 'draft' (30 steps), 'normal' (50 steps), 'high' (80 steps)
        num_candidates: Generate multiple versions per image for selection
    """

    # Quality presets
    quality_settings = {
        "draft": {"steps": 30, "guidance": 7.0},
        "normal": {"steps": 50, "guidance": 7.5},
        "high": {"steps": 80, "guidance": 8.0}
    }

    settings = quality_settings.get(quality, quality_settings["normal"])

    logger.info("="*70)
    logger.info("GARDEN OF EDEN - IMAGE GENERATION")
    logger.info("="*70)
    logger.info(f"📁 Output directory: {session_dir}")
    logger.info(f"🎨 Quality: {quality} ({settings['steps']} steps)")
    logger.info(f"🖼️  Candidates per image: {num_candidates}")
    logger.info("="*70)

    # Initialize generator
    generator = ImageGenerator(
        model_id="stabilityai/stable-diffusion-xl-base-1.0",
        use_fp16=True,
        enable_optimizations=True
    )

    # Image prompts with enhanced quality keywords for SDXL
    images_to_generate = [
        {
            "filename": "eden_01_pretalk.png",
            "prompt": "magnificent garden archway entrance, ornate ancient stone arch covered in blooming roses and purple wisteria, golden sunset light streaming through, mystical ethereal atmosphere, peaceful and inviting, professional photography, depth of field, bokeh, cinematic lighting, 8k uhd, masterpiece, highly detailed",
            "seed": 42
        },
        {
            "filename": "eden_02_induction.png",
            "prompt": "enchanted forest path descending through ancient towering trees, soft diffused sunlight filtering through dense canopy, moss-covered stones and fallen leaves, ethereal mist floating, peaceful and deeply calming atmosphere, dreamlike quality, fantasy landscape art, highly detailed, serene and mystical, cinematic composition",
            "seed": 123
        },
        {
            "filename": "eden_03_meadow.png",
            "prompt": "breathtaking paradise meadow filled with colorful wildflowers, crystal clear mountain stream flowing gently, majestic snow-capped mountains in background, brilliant blue sky with soft white clouds, vibrant saturated colors, serene peaceful atmosphere, professional landscape photography, golden hour lighting, photorealistic, 8k uhd, masterpiece",
            "seed": 456
        },
        {
            "filename": "eden_04_serpent.png",
            "prompt": "mystical bioluminescent blue river with glowing ethereal water, graceful serpent made of light energy swimming elegantly, underwater plants glowing in blues and purples, magical transformation scene, fantasy digital art, surreal and beautiful, vibrant colors, highly detailed, peaceful transcendent energy, cinematic",
            "seed": 789
        },
        {
            "filename": "eden_05_tree.png",
            "prompt": "magnificent Rainbow Tree of Life, massive ancient sacred tree with glowing chakra-colored luminous fruits, vibrant red orange yellow green blue indigo violet lights radiating, mystical spiritual energy flowing, sacred geometry patterns, fantasy landscape, radiant aura, incredibly detailed bark texture and leaves, cinematic lighting, 8k uhd, masterpiece",
            "seed": 101
        },
        {
            "filename": "eden_06_divine.png",
            "prompt": "divine transcendent white-violet light radiating powerfully from celestial heavens above, ethereal clouds parting, crown chakra activation visualization, spiritual ascension and enlightenment, golden and violet rays of pure energy, transcendent peaceful atmosphere, sacred spiritual art, photorealistic lighting effects, cinematic composition, highly detailed, 8k uhd",
            "seed": 202
        },
        {
            "filename": "eden_07_return.png",
            "prompt": "peaceful forest path gently ascending back to surface world, warm golden morning sunlight filtering through trees, gentle transition from mystical to natural, grounding earthly energy, professional nature photography, soft bokeh background, warm inviting colors, safe and complete feeling, peaceful closure, cinematic composition, highly detailed",
            "seed": 303
        }
    ]

    # Generate all images
    session_path = Path(session_dir)
    session_path.mkdir(parents=True, exist_ok=True)

    total_images = len(images_to_generate)
    successful = 0
    failed = 0

    for idx, config in enumerate(images_to_generate, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"IMAGE {idx}/{total_images}: {config['filename']}")
        logger.info(f"{'='*70}")

        output_path = session_path / config['filename']

        # Skip if already exists
        if output_path.exists():
            logger.info(f"⏭️  File already exists, skipping: {config['filename']}")
            logger.info(f"💡 Delete the file to regenerate")
            successful += 1
            continue

        try:
            generator.generate_and_save(
                prompt=config['prompt'],
                output_path=str(output_path),
                width=1920,
                height=1080,
                num_inference_steps=settings['steps'],
                guidance_scale=settings['guidance'],
                seed=config.get('seed'),
                num_candidates=num_candidates,
                save_metadata=True
            )
            successful += 1

        except Exception as e:
            logger.error(f"❌ Failed to generate {config['filename']}: {e}")
            failed += 1
            continue

    # Summary
    logger.info(f"\n{'='*70}")
    logger.info(f"GENERATION COMPLETE")
    logger.info(f"{'='*70}")
    logger.info(f"✅ Successful: {successful}/{total_images}")
    if failed > 0:
        logger.info(f"❌ Failed: {failed}/{total_images}")
    logger.info(f"📁 Location: {session_path.absolute()}")
    logger.info(f"{'='*70}\n")

    # List generated files
    logger.info("Generated files:")
    for img_file in sorted(session_path.glob("eden_*.png")):
        size_mb = img_file.stat().st_size / (1024 * 1024)
        logger.info(f"  • {img_file.name} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate meditation images using Stable Diffusion XL")
    parser.add_argument(
        "--session-dir",
        type=str,
        default="sessions/garden-of-eden",
        help="Output directory for images"
    )
    parser.add_argument(
        "--quality",
        type=str,
        choices=["draft", "normal", "high"],
        default="normal",
        help="Generation quality: draft (30 steps), normal (50 steps), high (80 steps)"
    )
    parser.add_argument(
        "--candidates",
        type=int,
        default=3,
        help="Number of candidate images to generate per prompt"
    )

    args = parser.parse_args()

    generate_garden_of_eden_images(
        session_dir=args.session_dir,
        quality=args.quality,
        num_candidates=args.candidates
    )
