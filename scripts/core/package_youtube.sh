#!/bin/bash
# Package YouTube deliverables for a session.
# Copies final video, thumbnail, and description into deliverables/.
#
# Usage:
#   ./scripts/core/package_youtube.sh sessions/garden-of-eden

set -euo pipefail

SESSION_DIR="${1:-}"
if [ -z "$SESSION_DIR" ]; then
  echo "Usage: $0 <session_dir>"
  exit 1
fi

if [ ! -d "$SESSION_DIR" ]; then
  echo "❌ Session directory not found: $SESSION_DIR"
  exit 1
fi

OUTPUT_DIR="$SESSION_DIR/output"
VIDEO_DIR="$OUTPUT_DIR/video"
DELIVER_DIR="$SESSION_DIR/deliverables"
mkdir -p "$DELIVER_DIR"

# Locate assets
VIDEO_FILE=""
if [ -f "$VIDEO_DIR/session_final.mp4" ]; then
  VIDEO_FILE="$VIDEO_DIR/session_final.mp4"
elif [ -f "$VIDEO_DIR/garden_of_eden_FINAL.mp4" ]; then
  VIDEO_FILE="$VIDEO_DIR/garden_of_eden_FINAL.mp4"
fi

THUMB_FILE=""
if [ -f "$VIDEO_DIR/thumbnail_final.jpg" ]; then
  THUMB_FILE="$VIDEO_DIR/thumbnail_final.jpg"
fi

DESC_FILE=""
if [ -f "$SESSION_DIR/YOUTUBE_DESCRIPTION.md" ]; then
  DESC_FILE="$SESSION_DIR/YOUTUBE_DESCRIPTION.md"
elif [ -f "$SESSION_DIR/youtube-description.md" ]; then
  DESC_FILE="$SESSION_DIR/youtube-description.md"
fi

if [ -z "$VIDEO_FILE" ]; then
  echo "❌ Final video not found (expected session_final.mp4 or garden_of_eden_FINAL.mp4)"
  exit 1
fi

cp "$VIDEO_FILE" "$DELIVER_DIR/"
echo "📦 Video: $(basename "$VIDEO_FILE")"
if [ -n "$THUMB_FILE" ]; then
  cp "$THUMB_FILE" "$DELIVER_DIR/"
  echo "📦 Thumbnail: $(basename "$THUMB_FILE")"
fi
if [ -n "$DESC_FILE" ]; then
  cp "$DESC_FILE" "$DELIVER_DIR/"
  echo "📦 Description: $(basename "$DESC_FILE")"
fi

cat > "$DELIVER_DIR/README.txt" <<EOF
YouTube Upload Package
======================
- Video: $(basename "$VIDEO_FILE")
- Thumbnail: $(basename "$THUMB_FILE" 2>/dev/null || echo "N/A")
- Description: $(basename "$DESC_FILE" 2>/dev/null || echo "N/A")

Suggested settings:
- Category: Education or People & Blogs
- License: Standard YouTube License
- Comments: Enabled (moderated)
- Age restriction: No (include binaural disclaimer)

Tags/description: see the copied description file.
EOF

echo "✅ Deliverables packaged in: $DELIVER_DIR"
