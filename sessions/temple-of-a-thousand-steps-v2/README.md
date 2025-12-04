# temple-of-a-thousand-steps-v2

## Session Information

**Theme:** [Describe the theme]
**Duration:** [Target duration in minutes]
**Goal:** [Therapeutic goal]
**Created:** 2025-12-03

## Directory Structure

```
temple-of-a-thousand-steps-v2/
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
```

## Quick Start

1. Edit `manifest.yaml` with session details
2. Write voice script in `script.ssml`
3. Add images to `images/uploaded/`
4. Generate audio:
   ```bash
   python scripts/core/build_session.py \
       --session sessions/temple-of-a-thousand-steps-v2 \
       --ssml sessions/temple-of-a-thousand-steps-v2/script.ssml
   ```

## Validate Structure

```bash
python scripts/utilities/validate_session_structure.py sessions/temple-of-a-thousand-steps-v2
```

## Notes

[Add any session-specific notes here]
