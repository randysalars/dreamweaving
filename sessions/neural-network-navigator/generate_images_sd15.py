#!/usr/bin/env python3
"""
OPTIMIZED: Generate 8 neural network images using SD 1.5 (4x faster than SDXL)
Using draft quality for faster generation on CPU
"""

import sys
sys.path.insert(0, '../../scripts/core')

import torch
from diffusers import StableDiffusionPipeline, DDIMScheduler
from PIL import Image
import os
import time

# Image prompts from VISUAL_SCENES.md
SCENES = [
    {
        "name": "scene_01_opening",
        "prompt": "A mesmerizing close-up view of bioluminescent neural pathways in deep space, billions of softly glowing neurons like tiny blue and purple stars, delicate synaptic connections forming an intricate web of light, gentle pulsing animation suggesting alive consciousness, cosmic nebula background in deep indigo and violet, particles of light drifting slowly, ethereal and mystical atmosphere, photorealistic digital art, extremely detailed, soft focus with depth of field, 8K quality, cinematic lighting, peaceful and inviting mood",
        "negative": "harsh lighting, bright colors, chaotic, cluttered, mechanical, artificial, cartoon, anime, text, watermark, human figures, faces, body parts, aggressive, scary, dark horror"
    },
    {
        "name": "scene_02_descent",
        "prompt": "First-person perspective descending through layers of consciousness into a vast inner cosmos, billions of glowing neurons arranged in massive three-dimensional networks stretching infinitely in all directions, golden and blue-white synaptic pathways creating a living starfield, sense of floating weightlessly through neural space, soft clouds of luminous neurotransmitters drifting past, deep purple and indigo cosmic background, photorealistic with slight dreamy quality, volumetric god rays of soft light, extremely detailed neural structures, 8K quality, cinematic depth of field, serene and awe-inspiring",
        "negative": "claustrophobic, enclosed spaces, walls, ceilings, harsh lighting, mechanical circuits, computer graphics, geometric patterns, text, watermark, human faces, bodies, falling sensation, threatening, scary"
    },
    {
        "name": "scene_03_neural_garden",
        "prompt": "A breathtaking panoramic view of a mystical neural garden, glowing synaptic connections blooming like bioluminescent flowers, some pathways bright and pulsing with frequent use, others dim and waiting to awaken, massive clusters of luminous neurons representing skills and knowledge, fractal branching patterns creating organic architecture, warm golden light flows through active pathways like liquid sunshine, cool blue light in potential pathways, fields of shimmering dark matter between bright clusters suggesting infinite possibility, photorealistic with magical realism, extremely detailed neural dendrites and axons, soft volumetric fog, 8K quality, wonder-filled and alive, vast but intimate scale",
        "negative": "literal flowers, plants, trees, earth garden, mechanical, circuitry, computer chips, geometric, artificial, cluttered, chaotic, harsh colors, neon, faces, figures, text, watermark"
    },
    {
        "name": "scene_04_pathfinder",
        "prompt": "Dynamic neural pathways forming new connections in real-time, rivers of golden and sapphire light flowing between neurons like liquid electricity, a playful ethereal presence made of light trails suggesting the Pathfinder archetype, crystalline bridges of synaptic connection suddenly linking distant neurons with brilliant sparks, cascading chains of activation rippling through the network like dominoes of light, fractal branching patterns growing and extending, time-lapse photography style showing growth and connection, photorealistic with energetic movement, particles of light flowing along pathways, deep space background, extremely detailed, 8K quality, sense of discovery and adventure, warm inviting colors",
        "negative": "human figure, face, body, mechanical, static, frozen, disconnected, dark, scary, chaotic, computer graphics, circuit boards, wires, harsh angles, text, watermark"
    },
    {
        "name": "scene_05_weaver",
        "prompt": "An transcendent view of a unified neural web, golden threads of integration weaving through the entire network creating harmonious patterns, a magnificent presence made of golden light suggesting the Weaver archetype, long-range connections linking distant parts of the brain, everything interconnected in sacred geometry, the network resonating in perfect harmony, visible waves of coherence rippling through the system, warm golden and honey-colored light dominating, deep violet background, photorealistic with spiritual quality, gossamer threads of light creating a cosmic tapestry, extremely detailed, 8K quality, profound sense of wholeness and unity, breathtaking beauty",
        "negative": "human figure, face, body, mechanical, chaotic, disconnected, harsh, cold colors, geometric grids, artificial patterns, circuit boards, text, watermark, dark, ominous"
    },
    {
        "name": "scene_06_gamma_burst",
        "prompt": "An explosive moment of unified consciousness, the entire neural network illuminated simultaneously in brilliant white-gold light, every synapse firing at once creating a supernova of awareness, cascading waves of light rippling outward from center, sacred geometric patterns visible in the coherent activation, sense of sudden profound understanding, photorealistic with transcendent spiritual quality, extremely bright but not harsh, particles of pure light filling the entire space, deep purple-white background, 8K quality, crystalline clarity, overwhelming beauty, the visual equivalent of AHA insight moment, divine illumination",
        "negative": "explosion, destruction, chaos, harsh, aggressive, scary, dark, mechanical, circuit board, human face, body, text, watermark, cluttered"
    },
    {
        "name": "scene_07_consolidation",
        "prompt": "A serene view of strengthened neural pathways with stable, steady glow, crystalline structures forming along well-used connections showing consolidation, the network more organized and coherent than before, soft blue-white and gentle gold pathways pulsing with healthy rhythm, sense of solid architecture and reliable structure, new pathways integrated into the existing network seamlessly, peaceful cosmic background in soft purple and deep blue, photorealistic with calming quality, extremely detailed synaptic structures showing strength, 8K quality, depth of field, sense of confidence and stability, everything in its right place",
        "negative": "chaotic, disorganized, dim, fading, breaking apart, mechanical, artificial, harsh, human figures, faces, text, watermark, geometric grids, circuit boards"
    },
    {
        "name": "scene_08_return",
        "prompt": "An uplifting view ascending gently through layers of consciousness back toward waking awareness, the neural landscape gradually fading into soft luminous clouds, but maintaining a subtle inner glow suggesting permanent positive changes, warm morning light filtering through layers, sense of returning home with gifts, gentle gradient from deep purple cosmos below to lighter lavender and soft blue above, the neural network still visible but becoming more abstract and dreamlike, photorealistic with hopeful optimistic quality, soft focus, particles of light ascending, 8K quality, peaceful transition, keeping inner light alive, sense of completion and new beginning",
        "negative": "harsh light, stark, jarring, completely dark, total disappearance, harsh transition, falling, descending, mechanical, faces, figures, text, watermark, sad, melancholy"
    }
]

def main():
    print("=" * 70)
    print("NEURAL NETWORK NAVIGATOR - SD 1.5 OPTIMIZED (4x faster)")
    print("=" * 70)
    print("\n🚀 Using Stable Diffusion 1.5 for 4x speedup")
    print(f"⚡ Draft quality: 20 steps with DDIM scheduler")
    print(f"   Generating {len(SCENES)} images...")
    print(f"   Estimated: 10-12 min per image, ~1.5 hours total\n")

    # Initialize SD 1.5
    print("Initializing SD 1.5 (much faster than SDXL)...")

    model_id = "runwayml/stable-diffusion-v1-5"

    try:
        # Load model
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32,  # CPU uses float32
            safety_checker=None,  # Disable for speed
            requires_safety_checker=False
        )

        # Use DDIM scheduler (faster convergence at low steps)
        pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)

        # Move to CPU
        pipe = pipe.to("cpu")

        # Enable optimizations
        pipe.enable_attention_slicing(1)

        print("✓ SD 1.5 initialized\n")

    except Exception as e:
        print(f"✗ Error initializing SD 1.5: {e}")
        return 1

    # Create output directory
    os.makedirs("images", exist_ok=True)

    # Generate each image
    total_images = len(SCENES)
    total_start = time.time()

    for i, scene in enumerate(SCENES, 1):
        print(f"\n{'='*70}")
        print(f"Image {i}/{total_images}: {scene['name']}")
        print(f"{'='*70}")

        output_path = f"images/{scene['name']}_FINAL.png"

        # Skip if already exists
        if os.path.exists(output_path):
            print(f"⏩ Already exists, skipping: {output_path}")
            continue

        img_start = time.time()

        try:
            # Generate with SD 1.5 optimized settings
            result = pipe(
                prompt=scene['prompt'],
                negative_prompt=scene['negative'],
                width=1920,
                height=1080,
                num_inference_steps=20,  # Reduced from 30 (DDIM converges faster)
                guidance_scale=7.5,
                num_images_per_prompt=1
            )

            # Save
            image = result.images[0]
            image.save(output_path, 'PNG')

            img_elapsed = time.time() - img_start
            file_size = os.path.getsize(output_path) / (1024 * 1024)

            print(f"✓ Saved: {output_path} ({file_size:.1f} MB)")
            print(f"⏱️  Time: {img_elapsed/60:.1f} minutes")

            # Estimate remaining time
            if i < total_images:
                avg_time = (time.time() - total_start) / i
                remaining = (total_images - i) * avg_time
                print(f"📊 Estimated remaining: {remaining/60:.1f} minutes")

        except Exception as e:
            print(f"✗ Error generating {scene['name']}: {e}")
            continue

    total_elapsed = time.time() - total_start
    print("\n" + "="*70)
    print("✓ Image generation complete!")
    print("="*70)
    print(f"\n⏱️  Total time: {total_elapsed/60:.1f} minutes")
    print(f"📁 Generated {total_images} images in images/ directory")
    print(f"\nNext: Run video compositor")
    print(f"  python3 composite_final_video_optimized.py")

    return 0

if __name__ == '__main__':
    exit(main())
