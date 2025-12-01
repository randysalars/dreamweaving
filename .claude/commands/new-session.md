---
name: new-session
description: Create a new session with AI-generated manifest stub
arguments:
  - name: session_name
    required: true
    description: Name of the session (kebab-case)
agent: dreamweaver
---

# /new-session Command

Create a new hypnotic journey session with scaffolding and AI-generated manifest.

## Usage
```
/new-session <session-name>
```

## Example
```
/new-session inner-child-healing
```

## Process

1. **Validate session name**
   - Must be kebab-case (lowercase, hyphens)
   - Must not already exist

2. **Create session directory**
   ```bash
   ./scripts/utilities/create_new_session.sh "{session_name}"
   ```

3. **Prompt for session details**
   - Topic/theme
   - Target duration (default: 30 minutes)
   - Style (healing, confidence, sleep, spiritual, general)
   - Target audience

4. **Generate manifest stub**
   - Use Manifest Architect agent
   - Pre-fill based on user input
   - Apply lessons from knowledge base

5. **Create placeholder files**
   - `manifest.yaml` - Generated configuration
   - `working_files/script.ssml` - Template
   - `midjourney-prompts.md` - Placeholder
   - `notes.md` - Session notes

6. **Report created files**
   - List all files created
   - Provide next steps

## Output Structure
```
sessions/{session-name}/
├── manifest.yaml           # AI-generated configuration
├── working_files/
│   └── script.ssml         # SSML template
├── images/
│   └── uploaded/           # For Midjourney images
├── midjourney-prompts.md   # Placeholder
├── notes.md                # Session notes
└── output/                 # For generated files
```

## Next Steps After Creation

1. Review and edit `manifest.yaml`
2. Run `/generate-script` to create SSML
3. Run Visual Artist for Midjourney prompts
4. Create images on Midjourney
5. Run `/full-build` for production
