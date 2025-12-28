#!/usr/bin/env python3
"""
Package digital products into downloadable ZIP files.
Combines PDFs with audio files for each product.
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

# Product to PDF mapping
PRODUCTS = {
    "consciousness-expansion-pack": {
        "pdf_source": "consciousness-expansion-guide.md",
        "pdf_name": "Consciousness-Expansion-Guide.pdf",
        "sessions": [
            "01-foundation-grounding",
            "02-breath-gateway",
            "03-deep-relaxation",
            "04-inner-sanctuary",
            "05-witness-state",
            "06-symbolic-journey",
            "07-integration",
            "08-threshold"
        ],
        "audio_names": [
            "01-Foundation-Grounding.mp3",
            "02-Breath-Gateway.mp3",
            "03-Deep-Relaxation.mp3",
            "04-Inner-Sanctuary.mp3",
            "05-Witness-State.mp3",
            "06-Symbolic-Journey.mp3",
            "07-Integration.mp3",
            "08-The-Threshold.mp3"
        ]
    },
    "mind-expansion-techniques": {
        "pdf_source": "consciousness-starter-guide.md",
        "pdf_name": "Mind-Expansion-Techniques.pdf",
        "sessions": [
            "01-mental-clearing",
            "02-focus-beam",
            "03-memory-palace",
            "04-creative-flow",
            "05-problem-solving",
            "06-intuition-access",
            "07-peak-performance",
            "08-genius-state"
        ],
        "audio_names": [
            "01-Mental-Clearing.mp3",
            "02-Focus-Beam.mp3",
            "03-Memory-Palace.mp3",
            "04-Creative-Flow.mp3",
            "05-Problem-Solving.mp3",
            "06-Intuition-Access.mp3",
            "07-Peak-Performance.mp3",
            "08-Genius-State.mp3"
        ]
    },
    "contemplative-practice-manual": {
        "pdf_source": "seekers-compass.md",
        "pdf_name": "Contemplative-Practice-Manual.pdf",
        "sessions_dir": "contemplative-practice",
        "sessions": [
            "01-sacred-stillness",
            "02-lectio-divina",
            "03-centering-prayer",
            "04-contemplative-examen",
            "05-divine-presence"
        ],
        "audio_names": [
            "01-Sacred-Stillness.mp3",
            "02-Lectio-Divina.mp3",
            "03-Centering-Prayer.mp3",
            "04-Contemplative-Examen.mp3",
            "05-Divine-Presence.mp3"
        ]
    },
    "holistic-wellness-protocol": {
        "pdf_source": "holistic-health-foundations.md",
        "pdf_name": "Holistic-Wellness-Protocol.pdf",
        "sessions_dir": "holistic-wellness",
        "sessions": [
            "01-body-scan",
            "02-breath-regulation",
            "03-sleep-preparation",
            "04-energy-restoration",
            "05-holistic-integration"
        ],
        "audio_names": [
            "01-Body-Scan-Awareness.mp3",
            "02-Breath-Regulation.mp3",
            "03-Sleep-Preparation.mp3",
            "04-Energy-Restoration.mp3",
            "05-Holistic-Integration.mp3"
        ]
    },
    "daily-joy-protocol": {
        "pdf_source": "daily-joy-practice.md",
        "pdf_name": "Daily-Joy-Protocol.pdf",
        "sessions_dir": "daily-joy-activation",
        "single_session": True,
        "audio_name": "Daily-Joy-Activation.mp3"
    },
    "frontier-wisdom-collection": {
        "pdf_source": "frontier-legends.md",
        "pdf_name": "Frontier-Wisdom-Collection.pdf",
        "sessions_dir": "frontier-wisdom-narrated",
        "single_session": True,
        "audio_name": "Frontier-Wisdom-Narrated.mp3"
    }
}

# Paths
SALARSU_PATH = Path("/home/rsalars/Projects/salarsu/frontend")
DREAMWEAVING_PATH = Path("/home/rsalars/Projects/dreamweaving")
PDF_SOURCE_PATH = SALARSU_PATH / "content/lead-magnets"
OUTPUT_PATH = SALARSU_PATH / "public/downloads/digital-products"

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}", flush=True)

def create_readme():
    """Create a README file for the package."""
    return """# Thank You for Your Purchase!

## What's Included

This package contains:
- PDF Guide with comprehensive instructions
- Audio sessions (MP3 format) for guided practice

## How to Use

1. Read the PDF guide first to understand the practice
2. Listen to audio sessions with headphones for best results
3. Find a quiet, comfortable space for practice
4. Practice consistently for best results

## Audio Tips

- Use headphones to experience binaural beats
- Listen at a comfortable volume
- Don't drive or operate machinery while listening
- Allow time after each session before resuming activities

## Support

Visit salars.net for more resources and support.

Enjoy your journey!

---
© Salar's - salars.net
"""

def package_product(product_slug, config):
    """Create ZIP package for a product."""
    log(f"Packaging: {product_slug}")

    # Determine sessions directory
    sessions_dir = config.get("sessions_dir", product_slug)
    sessions_path = DREAMWEAVING_PATH / "sessions" / sessions_dir

    if not sessions_path.exists():
        log(f"Sessions not found: {sessions_path}", "ERROR")
        return False

    # Create output directory
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    zip_path = OUTPUT_PATH / f"{product_slug}.zip"

    # Create ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add README
        zf.writestr("README.txt", create_readme())

        # Add PDF (for now, add markdown - PDF generation would be separate step)
        pdf_source = PDF_SOURCE_PATH / config["pdf_source"]
        if pdf_source.exists():
            # Add as markdown for now
            zf.write(pdf_source, config["pdf_name"].replace(".pdf", ".md"))
            log(f"  Added: {config['pdf_source']} (as markdown)")
        else:
            log(f"  PDF source not found: {pdf_source}", "WARN")

        # Add audio files
        audio_count = 0
        if config.get("single_session"):
            # Single session product
            audio_path = sessions_path / "output" / "voice_enhanced.mp3"
            if audio_path.exists():
                zf.write(audio_path, f"audio/{config['audio_name']}")
                audio_count += 1
                log(f"  Added audio: {config['audio_name']}")
            else:
                log(f"  Audio not found: {audio_path}", "WARN")
        else:
            # Multi-session product
            for i, session_name in enumerate(config.get("sessions", [])):
                session_path = sessions_path / session_name
                audio_path = session_path / "output" / "voice_enhanced.mp3"

                if audio_path.exists():
                    audio_name = config["audio_names"][i]
                    zf.write(audio_path, f"audio/{audio_name}")
                    audio_count += 1
                    log(f"  Added audio: {audio_name}")
                else:
                    log(f"  Audio not found: {audio_path}", "WARN")

    # Report
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    log(f"Created: {zip_path.name} ({size_mb:.1f} MB, {audio_count} audio files)")
    return True

def main():
    log("=" * 60)
    log("DIGITAL PRODUCTS PACKAGING")
    log("=" * 60)

    success = 0
    failed = 0

    for product_slug, config in PRODUCTS.items():
        try:
            if package_product(product_slug, config):
                success += 1
            else:
                failed += 1
        except Exception as e:
            log(f"Error packaging {product_slug}: {e}", "ERROR")
            failed += 1

    log("=" * 60)
    log(f"PACKAGING COMPLETE: {success} succeeded, {failed} failed")
    log(f"Output: {OUTPUT_PATH}")
    log("=" * 60)

if __name__ == "__main__":
    main()
