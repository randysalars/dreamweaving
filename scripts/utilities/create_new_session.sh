#!/bin/bash
#
# Create a new hypnosis session from template
#
# Usage: ./create_new_session.sh session-name
# Example: ./create_new_session.sh inner-child-healing
#

set -e

# Find project root (directory containing sessions/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [ -z "$1" ]; then
    echo "Usage: ./create_new_session.sh session-name"
    echo "Example: ./create_new_session.sh inner-child-healing"
    exit 1
fi

SESSION_NAME="$1"
SESSION_DIR="$PROJECT_ROOT/sessions/$SESSION_NAME"
TEMPLATE_DIR="$PROJECT_ROOT/sessions/_template"

# Check if session already exists
if [ -d "$SESSION_DIR" ]; then
    echo "Error: Session already exists: $SESSION_DIR"
    exit 1
fi

# Check if template exists
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "Error: Template directory not found: $TEMPLATE_DIR"
    exit 1
fi

echo "Creating session: $SESSION_NAME"
echo ""

# Create session directory structure (matching template)
mkdir -p "$SESSION_DIR/output"
mkdir -p "$SESSION_DIR/working_files/stems"
mkdir -p "$SESSION_DIR/images/uploaded"
mkdir -p "$SESSION_DIR/variants"
mkdir -p "$SESSION_DIR/final_export"

# Copy and customize manifest.yaml
if [ -f "$TEMPLATE_DIR/manifest.yaml" ]; then
    sed "s/my-session-name/$SESSION_NAME/g" "$TEMPLATE_DIR/manifest.yaml" > "$SESSION_DIR/manifest.yaml"
    echo "  Created manifest.yaml"
fi

# Copy script.ssml template
if [ -f "$TEMPLATE_DIR/script.ssml" ]; then
    cp "$TEMPLATE_DIR/script.ssml" "$SESSION_DIR/script.ssml"
    echo "  Created script.ssml"
fi

# Create session README
cat > "$SESSION_DIR/README.md" << READMEEOF
# $SESSION_NAME

## Session Information

**Theme:** [Describe the theme]
**Duration:** [Target duration in minutes]
**Goal:** [Therapeutic goal]
**Created:** $(date +%Y-%m-%d)

## Directory Structure

\`\`\`
$SESSION_NAME/
├── manifest.yaml      # Session configuration
├── script.ssml        # Voice script (SSML format)
├── notes.md           # Production notes
├── README.md          # This file
├── output/            # Final audio/video files
├── working_files/     # Intermediate files
│   └── stems/         # Individual audio stems
├── images/            # Session images
│   └── uploaded/      # Images from external sources
├── variants/          # Alternative versions
└── final_export/      # Release-ready files
\`\`\`

## Quick Start

1. Edit \`manifest.yaml\` with session details
2. Write voice script in \`script.ssml\`
3. Add images to \`images/uploaded/\`
4. Generate audio:
   \`\`\`bash
   python scripts/core/build_session.py \\
       --session sessions/$SESSION_NAME \\
       --ssml sessions/$SESSION_NAME/script.ssml
   \`\`\`

## Validate Structure

\`\`\`bash
python scripts/utilities/validate_session_structure.py sessions/$SESSION_NAME
\`\`\`

## Notes

[Add any session-specific notes here]
READMEEOF
echo "  Created README.md"

# Create notes.md
cat > "$SESSION_DIR/notes.md" << NOTESEOF
# Production Notes: $SESSION_NAME

## Session Goals

[What do you want the listener to experience?]

## Key Themes

- [Theme 1]
- [Theme 2]

## Archetypes & Symbols

- [Archetype or symbol used]

## Technical Notes

- Voice: [Voice choice and why]
- Duration: [Target duration]
- Binaural: [Frequency progression notes]

## Revision History

- $(date +%Y-%m-%d): Created session
NOTESEOF
echo "  Created notes.md"

# Create .gitkeep files
touch "$SESSION_DIR/output/.gitkeep"
touch "$SESSION_DIR/variants/.gitkeep"
touch "$SESSION_DIR/final_export/.gitkeep"

echo ""
echo "Session created: $SESSION_DIR"
echo ""
echo "Next steps:"
echo "  1. Edit manifest.yaml with session configuration"
echo "  2. Write voice script in script.ssml"
echo "  3. Add images to images/uploaded/"
echo "  4. Run: python scripts/core/build_session.py --session sessions/$SESSION_NAME --ssml sessions/$SESSION_NAME/script.ssml"
echo ""
echo "Validate structure:"
echo "  python scripts/utilities/validate_session_structure.py sessions/$SESSION_NAME"
