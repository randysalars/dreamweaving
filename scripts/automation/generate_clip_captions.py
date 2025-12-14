#!/usr/bin/env python3
"""
Generate captions for clip_### assets.

Reads a caption bank JSON and emits one caption per clip (clip_001..N),
optionally appending a landing-page link.

Usage:
    PATH="venv/bin:$PATH" python -m scripts.automation.generate_clip_captions \
      --bank config/caption_bank.json \
      --count 40 \
      --link https://salars.net/dreamweaving/xmas/video \
      --out-dir output/blessing_clips_grid/captions
"""

from __future__ import annotations

import argparse
import json
import logging
import random
from pathlib import Path
from typing import List


def load_bank(path: Path) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    captions: List[str] = []
    for items in data.values():
        captions.extend(items)
    if not captions:
        raise ValueError("Caption bank is empty")
    return captions


def generate_captions(captions: List[str], count: int, seed: int) -> List[str]:
    random.seed(seed)
    pool = captions[:]
    random.shuffle(pool)
    if len(pool) < count:
        # Repeat/shuffle to cover all clips
        needed = count - len(pool)
        pool.extend(random.choices(captions, k=needed))
    return pool[:count]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate clip captions from a caption bank.")
    parser.add_argument("--bank", type=Path, required=True, help="Path to caption_bank.json")
    parser.add_argument("--count", type=int, default=40, help="Number of captions to emit")
    parser.add_argument("--out-dir", type=Path, required=True, help="Output directory for .txt captions")
    parser.add_argument(
        "--link",
        type=str,
        default="https://salars.net/dreamweaving/xmas/video",
        help="Landing page URL appended to each caption",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for selection")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")

    captions = load_bank(args.bank)
    selected = generate_captions(captions, args.count, args.seed)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for idx, text in enumerate(selected, start=1):
        caption = f"{text} {args.link}".strip()
        out_path = args.out_dir / f"clip_{idx:03d}.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(caption + "\n")
        logging.info("Wrote %s", out_path)


if __name__ == "__main__":
    main()
