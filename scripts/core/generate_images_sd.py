#!/usr/bin/env python3
"""
Automated Stable Diffusion Image Generation
Generates high-quality meditation images from text prompts
Uses SDXL for best results
"""

import torch
from diffusers import (
    AutoencoderKL,
    DPMSolverMultistepScheduler,
    StableDiffusionXLImg2ImgPipeline,
    StableDiffusionXLPipeline
)
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
        refiner_model_id: Optional[str] = "stabilityai/stable-diffusion-xl-refiner-1.0",
        vae_model_id: Optional[str] = "madebyollin/sdxl-vae-fp16-fix",
        device: Optional[str] = None,
        use_fp16: bool = True,
        enable_optimizations: bool = True,
        use_refiner: bool = True,
        refiner_start: float = 0.8,
        refiner_steps: int = 18,
        max_generation_side: int = 1152,
        scheduler_type: str = "dpmpp_2m_karras"
    ):
        """
        Initialize the image generator

        Args:
            model_id: Hugging Face model ID
            refiner_model_id: Optional SDXL refiner model ID for final detail pass
            vae_model_id: Optional VAE override for sharper colors/details
            device: Device to use ('cuda', 'mps', 'cpu', or None for auto-detect)
            use_fp16: Use half precision for faster inference (requires GPU)
            enable_optimizations: Enable memory optimizations
            use_refiner: Run SDXL refiner on final 20% of denoising steps
            refiner_start: Where to split base/refiner denoising (0.0-1.0)
            refiner_steps: Number of refiner steps (kept short to save time)
            max_generation_side: Generate natively up to this side, then upscale to target
            scheduler_type: Scheduler preset ('dpmpp_2m_karras' by default)
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
        self.refiner_start = refiner_start
        self.refiner_steps = refiner_steps
        self.max_generation_side = max_generation_side
        self.scheduler_type = scheduler_type
        self.refiner_model_id = refiner_model_id
        self.model_id = model_id

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

            vae = None
            if vae_model_id:
                try:
                    logger.info(f"🎨 Loading VAE: {vae_model_id}")
                    vae = AutoencoderKL.from_pretrained(
                        vae_model_id,
                        torch_dtype=dtype,
                        use_safetensors=True
                    )
                except Exception as ve:
                    logger.warning(f"⚠️  Could not load custom VAE ({vae_model_id}), using default. Reason: {ve}")

            is_local_model = Path(model_id).exists()
            if is_local_model:
                logger.info(f"📦 Loading local SDXL model file: {model_id}")
                self.pipe = StableDiffusionXLPipeline.from_single_file(
                    model_id,
                    torch_dtype=dtype,
                    use_safetensors=True,
                    vae=vae
                )
            else:
                self.pipe = StableDiffusionXLPipeline.from_pretrained(
                    model_id,
                    torch_dtype=dtype,
                    use_safetensors=True,
                    variant="fp16" if self.use_fp16 else None,
                    vae=vae
                )

            # Optimize scheduler for quality
            if scheduler_type == "dpmpp_2m_karras":
                self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                    self.pipe.scheduler.config,
                    use_karras_sigmas=True,
                    algorithm_type="dpmsolver++"
                )
            logger.info(f"🧠 Scheduler: {self.pipe.scheduler.__class__.__name__} ({scheduler_type})")

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
                if device == "cuda":
                    torch.backends.cuda.matmul.allow_tf32 = True
                    torch.backends.cudnn.allow_tf32 = True

            self.refiner = None
            if use_refiner and refiner_model_id:
                try:
                    logger.info(f"🎨 Loading SDXL refiner: {refiner_model_id}")
                    self.refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained(
                        refiner_model_id,
                        torch_dtype=dtype,
                        use_safetensors=True,
                        variant="fp16" if self.use_fp16 else None,
                        vae=self.pipe.vae
                    ).to(device)

                    if enable_optimizations:
                        if device == "cuda":
                            self.refiner.enable_attention_slicing(1)
                            self.refiner.enable_vae_slicing()
                            try:
                                self.refiner.enable_xformers_memory_efficient_attention()
                            except Exception:
                                pass
                        if device == "cpu":
                            self.refiner.enable_sequential_cpu_offload()

                    logger.info("✅ Refiner loaded successfully")
                except Exception as re:
                    logger.warning(f"⚠️  Refiner unavailable ({re}); continuing with base model only.")
                    self.refiner = None

            logger.info("✅ Model loaded successfully")

        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            raise

    def _prepare_generation_dimensions(self, target_width: int, target_height: int):
        """
        Keep SDXL generation near its native resolution, then optionally upscale.

        Returns:
            (gen_width, gen_height, upscale_target | None)
        """
        target_width = (target_width // 8) * 8
        target_height = (target_height // 8) * 8

        max_side = max(target_width, target_height)
        if max_side <= self.max_generation_side:
            return target_width, target_height, None

        scale = self.max_generation_side / max_side
        gen_width = max(64, int(target_width * scale) // 8 * 8)
        gen_height = max(64, int(target_height * scale) // 8 * 8)

        return gen_width, gen_height, (target_width, target_height)

    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = (
            "blurry, low quality, noisy, duplicate, poorly drawn, deformed, disfigured, extra limbs, extra fingers, "
            "fused anatomy, malformed eyes, text, watermark, signature, logo, oversharpened, jpeg artifacts"
        ),
        width: int = 1920,
        height: int = 1080,
        num_inference_steps: int = 32,
        guidance_scale: float = 6.5,
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
        gen_width, gen_height, upscale_to = self._prepare_generation_dimensions(width, height)

        # Set seed if specified
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)

        logger.info(f"\n🎨 Generating {num_images} image(s)...")
        logger.info(f"📝 Prompt: {prompt[:100]}...")
        if upscale_to:
            logger.info(f"📐 Native: {gen_width}x{gen_height} → Upscale to: {width}x{height}")
        else:
            logger.info(f"📐 Size: {gen_width}x{gen_height}")
        logger.info(f"🔢 Steps: {num_inference_steps}, Guidance: {guidance_scale}, Scheduler: {self.scheduler_type}")
        if seed:
            logger.info(f"🎲 Seed: {seed}")

        start_time = time.time()

        try:
            # Generate images (with optional refiner pass)
            if self.refiner:
                base_output = self.pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=gen_width,
                    height=gen_height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator,
                    num_images_per_prompt=num_images,
                    output_type="latent",
                    denoising_end=self.refiner_start
                )

                refiner_steps = max(
                    self.refiner_steps,
                    int(num_inference_steps * (1 - self.refiner_start))
                )

                refined = self.refiner(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    image=base_output.images,
                    num_inference_steps=refiner_steps,
                    guidance_scale=guidance_scale,
                    generator=generator,
                    denoising_start=self.refiner_start
                )
                images = refined.images
            else:
                result = self.pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=gen_width,
                    height=gen_height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator,
                    num_images_per_prompt=num_images
                )
                images = result.images

            # Optional upscale to requested resolution for SDXL-native friendliness
            if upscale_to:
                target_size = (width, height)
                upscaled = []
                for img in images:
                    upscaled.append(img.resize(target_size, Image.LANCZOS))
                images = upscaled

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
            native_width, native_height, upscale_to = self._prepare_generation_dimensions(width, height)

            metadata = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "native_width": native_width,
                "native_height": native_height,
                "upscaled_to": upscale_to if upscale_to else None,
                "max_generation_side": self.max_generation_side,
                "scheduler": self.scheduler_type,
                "refined": bool(getattr(self, "refiner", None)),
                "refiner_model": self.refiner_model_id if getattr(self, "refiner", None) else None,
                "refiner_start": self.refiner_start if getattr(self, "refiner", None) else None,
                "refiner_steps": self.refiner_steps if getattr(self, "refiner", None) else None,
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
    num_candidates: int = 3,
    use_refiner: bool = True,
    max_generation_side: int = 1152
):
    """
    Generate all 7 Garden of Eden meditation images

    Args:
        session_dir: Directory to save images
        quality: 'draft' (26 steps), 'normal' (32 steps), 'high' (40 steps)
        num_candidates: Generate multiple versions per image for selection
        use_refiner: Whether to run SDXL refiner on final denoising chunk
        max_generation_side: Native generation side before upscaling
    """

    # Quality presets
    quality_settings = {
        "draft": {"steps": 26, "guidance": 5.5},
        "normal": {"steps": 32, "guidance": 6.5},
        "high": {"steps": 40, "guidance": 7.0}
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
        enable_optimizations=True,
        use_refiner=use_refiner,
        max_generation_side=max_generation_side
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
        help="Generation quality: draft (26 steps), normal (32 steps), high (40 steps)"
    )
    parser.add_argument(
        "--candidates",
        type=int,
        default=3,
        help="Number of candidate images to generate per prompt"
    )
    parser.add_argument(
        "--no-refiner",
        action="store_true",
        help="Disable SDXL refiner pass (useful for lower VRAM)"
    )
    parser.add_argument(
        "--max-gen-side",
        type=int,
        default=1152,
        help="Maximum side length to generate natively before upscaling"
    )

    args = parser.parse_args()

    generate_garden_of_eden_images(
        session_dir=args.session_dir,
        quality=args.quality,
        num_candidates=args.candidates,
        use_refiner=not args.no_refiner,
        max_generation_side=args.max_gen_side
    )
