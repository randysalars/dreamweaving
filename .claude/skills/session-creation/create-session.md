---
name: Create Session
level: basic
description: Quick session scaffolding using the create_new_session.sh script
---

# Create Session Skill

## Overview
Create a new session directory with all required scaffolding.

## Quick Command
```bash
./scripts/utilities/create_new_session.sh "session-name"
```

## What Gets Created

```
sessions/{session-name}/
├── manifest.yaml          # Template configuration
├── working_files/
│   └── script.ssml        # SSML template
├── images/
│   ├── uploaded/          # For Midjourney images
│   └── example/           # Example images
├── notes.md               # Session notes
└── output/                # Generated files
    └── video/
```

## Naming Convention

- Use kebab-case (lowercase with hyphens)
- Be descriptive but concise
- Examples:
  - `inner-child-healing`
  - `confidence-boost-morning`
  - `deep-sleep-forest`

## Next Steps

1. Edit `manifest.yaml` with session details
2. Write or generate SSML script
3. Create images on Midjourney
4. Run build commands
