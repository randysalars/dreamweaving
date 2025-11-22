#!/bin/bash

# Helper script to create a new hypnosis session

if [ -z "$1" ]; then
    echo "Usage: ./create_new_session.sh session-name"
    echo "Example: ./create_new_session.sh inner-child-healing"
    exit 1
fi

SESSION_NAME="$1"
SESSION_DIR="sessions/$SESSION_NAME"

# Create session structure
mkdir -p "$SESSION_DIR/output"

# Create placeholder SSML
cat > "$SESSION_DIR/${SESSION_NAME}.ssml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">

<!-- SECTION 1: PRE-TALK INTRODUCTION -->
<prosody rate="slow" pitch="-2st">
<break time="1s"/>
Welcome, beloved traveler...
<!-- Add your pre-talk here -->
</prosody>

<!-- SECTION 2: INDUCTION -->
<!-- Add your induction here -->

<!-- SECTION 3: MAIN JOURNEY -->
<!-- Add your main visualization here -->

<!-- SECTION 4: INTEGRATION & RETURN -->
<!-- Add your return sequence here -->

<!-- SECTION 5: POST-HYPNOTIC SUGGESTIONS & ANCHORS -->
<!-- Add your anchors here -->

</speak>
EOF

# Create session README
cat > "$SESSION_DIR/README.md" << READMEEOF
# $SESSION_NAME

## Session Information

**Theme:** [Describe the theme]
**Duration:** [Target duration]
**Goal:** [Therapeutic goal]
**Created:** $(date +%Y-%m-%d)

## Generate Audio

\`\`\`bash
python scripts/generate_audio_chunked.py \\
    sessions/$SESSION_NAME/${SESSION_NAME}.ssml \\
    sessions/$SESSION_NAME/output/${SESSION_NAME}.mp3
\`\`\`

## Notes

[Add any session-specific notes here]
READMEEOF

echo "✅ Session created: $SESSION_DIR"
echo ""
echo "Next steps:"
echo "1. Edit: sessions/$SESSION_NAME/${SESSION_NAME}.ssml"
echo "2. Generate: python scripts/generate_audio_chunked.py sessions/$SESSION_NAME/${SESSION_NAME}.ssml sessions/$SESSION_NAME/output/${SESSION_NAME}.mp3"
