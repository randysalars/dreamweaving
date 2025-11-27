#!/usr/bin/env python3
"""Debug script to examine the filter_complex chain"""

from pathlib import Path

session_dir = Path(__file__).parent

# Image timings (path, start_sec, end_sec)
images_config = [
    (str(session_dir / "eden_01_pretalk.png"), 0, 150),
    (str(session_dir / "eden_02_induction.png"), 150, 480),
    (str(session_dir / "eden_03_meadow.png"), 480, 810),
    (str(session_dir / "eden_04_serpent.png"), 810, 1020),
    (str(session_dir / "eden_05_tree.png"), 1020, 1200),
    (str(session_dir / "eden_06_divine.png"), 1200, 1380),
    (str(session_dir / "eden_07_return.png"), 1380, 1500),
]

# Build filter_complex
filters = []
overlays = []

for idx, (img_path, start_sec, end_sec) in enumerate(images_config):
    input_num = idx + 1
    duration = end_sec - start_sec
    fade_frames = 60  # 2 seconds at 30fps

    # Create filter for this image: fade in/out, scale, pad
    img_filter = (
        f"[{input_num}:v]"
        f"fade=in:0:{fade_frames},"
        f"fade=out:{duration*30-fade_frames}:{fade_frames},"
        f"scale=1920:1080:force_original_aspect_ratio=decrease,"
        f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
        f"[img{idx}]"
    )
    filters.append(img_filter)
    overlays.append((f"img{idx}", start_sec, end_sec))

# Build overlay chain
current_stream = "[0:v]"
for idx, (img_label, start_sec, end_sec) in enumerate(overlays):
    if idx == len(overlays) - 1:
        overlay_filter = (
            f"{current_stream}[{img_label}]"
            f"overlay=0:0:enable='between(t,{start_sec},{end_sec})'"
            f"[out]"
        )
    else:
        overlay_filter = (
            f"{current_stream}[{img_label}]"
            f"overlay=0:0:enable='between(t,{start_sec},{end_sec})'"
            f"[tmp{idx}]"
        )
        current_stream = f"[tmp{idx}]"
    filters.append(overlay_filter)

# Join all filters
filter_complex = "; ".join(filters)

print("="*80)
print("FILTER COMPLEX:")
print("="*80)
print(filter_complex)
print("\n" + "="*80)
print("BREAKDOWN:")
print("="*80)
for i, f in enumerate(filters):
    print(f"\n{i+1}. {f}")
