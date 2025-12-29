#!/usr/bin/env python3
"""
Build all audio sessions for digital products.
Generates TTS voice with enhancement for each session.
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

# Product configurations
PRODUCTS = {
    "consciousness-expansion-pack": {
        "sessions": [
            "01-foundation-grounding",
            "02-breath-gateway",
            "03-deep-relaxation",
            "04-inner-sanctuary",
            "05-witness-state",
            "06-symbolic-journey",
            "07-integration",
            "08-threshold"
        ]
    },
    "mind-expansion-techniques": {
        "sessions": [
            "01-mental-clearing",
            "02-focus-enhancement",
            "03-creative-visualization",
            "04-memory-palace",
            "05-intuition-activation",
            "06-problem-solving",
            "07-cognitive-flexibility",
            "08-genius-state"
        ]
    },
    "contemplative-practice": {
        "sessions": [
            "01-sacred-stillness",
            "02-lectio-divina",
            "03-centering-prayer",
            "04-contemplative-examination",
            "05-divine-presence"
        ]
    },
    "holistic-wellness": {
        "sessions": [
            "01-body-scan",
            "02-breath-vitality",
            "03-healing-visualization",
            "04-stress-release",
            "05-restorative-sleep"
        ]
    },
    "daily-joy-activation": {
        "single_session": True
    },
    "frontier-wisdom-narrated": {
        "single_session": True
    }
}

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}", flush=True)

def build_session(session_path):
    """Build a single session."""
    script_path = session_path / "working_files" / "script.ssml"
    output_path = session_path / "output"

    if not script_path.exists():
        log(f"No script found: {script_path}", "WARN")
        return False

    # Check if already built
    enhanced_mp3 = output_path / "voice_enhanced.mp3"
    if enhanced_mp3.exists():
        log(f"Already built: {session_path.name}", "SKIP")
        return True

    log(f"Building: {session_path.name}")

    cmd = [
        sys.executable,
        "scripts/core/generate_voice.py",
        str(script_path),
        str(output_path),
        "--provider", "coqui",
        "--quality", "hypnotic"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=900  # 15 min timeout
        )

        if result.returncode == 0:
            log(f"Complete: {session_path.name}", "OK")
            return True
        else:
            log(f"Failed: {session_path.name} - {result.stderr[:200]}", "ERROR")
            return False
    except subprocess.TimeoutExpired:
        log(f"Timeout: {session_path.name}", "ERROR")
        return False
    except Exception as e:
        log(f"Error: {session_path.name} - {e}", "ERROR")
        return False

def build_product(product_name, config):
    """Build all sessions for a product."""
    log(f"=" * 60)
    log(f"Building product: {product_name}")
    log(f"=" * 60)

    product_path = Path("sessions") / product_name

    if not product_path.exists():
        log(f"Product not found: {product_path}", "ERROR")
        return 0, 0

    success = 0
    failed = 0

    if config.get("single_session"):
        # Single session product
        if build_session(product_path):
            success += 1
        else:
            failed += 1
    else:
        # Multi-session product
        for session_name in config.get("sessions", []):
            session_path = product_path / session_name
            if session_path.exists():
                if build_session(session_path):
                    success += 1
                else:
                    failed += 1
            else:
                log(f"Session not found: {session_path}", "WARN")
                failed += 1

    log(f"Product {product_name}: {success} succeeded, {failed} failed")
    return success, failed

def main():
    log("=" * 60)
    log("DIGITAL PRODUCTS AUDIO BUILD")
    log("=" * 60)

    # Change to project root
    os.chdir(Path(__file__).parent.parent.parent)

    total_success = 0
    total_failed = 0

    for product_name, config in PRODUCTS.items():
        success, failed = build_product(product_name, config)
        total_success += success
        total_failed += failed

    log("=" * 60)
    log(f"BUILD COMPLETE")
    log(f"Total: {total_success} succeeded, {total_failed} failed")
    log("=" * 60)

if __name__ == "__main__":
    main()
