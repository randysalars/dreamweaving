# Dreamweaving Conventions

> **Purpose:** Coding standards and patterns that AI assistants must follow.

---

## File Naming

| Type | Convention | Example |
|------|------------|---------|
| Sessions | kebab-case | `garden-of-eden-pathworking` |
| Python files | snake_case | `generate_voice.py` |
| YAML configs | snake_case | `manifest.yaml` |
| SSML scripts | snake_case | `script_production.ssml` |
| Output audio | `{session}_MASTER.mp3` | `eden-garden_MASTER.mp3` |

---

## Directory Structure Per Session

```
sessions/{session-name}/
├── manifest.yaml              # REQUIRED: Session configuration
├── notes.md                   # Optional: Design notes
├── midjourney-prompts.md      # Optional: Image prompts
├── working_files/
│   ├── script_production.ssml # Full script with [SFX:] markers
│   └── script_voice_clean.ssml # Script for TTS (no SFX)
├── images/
│   └── uploaded/              # Scene images (1920x1080)
└── output/
    ├── voice.mp3              # Raw TTS output (DON'T USE)
    ├── voice_enhanced.mp3     # Enhanced voice (USE THIS)
    ├── binaural_dynamic.wav   # Binaural beats track
    ├── sfx_track.wav          # Sound effects track
    ├── session_mixed.wav      # All stems mixed
    ├── {session}_MASTER.mp3   # FINAL mastered audio
    └── youtube_package/       # Complete YouTube bundle
```

---

## SSML Rules (CRITICAL)

### Rate: Always 1.0
```xml
<!-- CORRECT -->
<prosody rate="1.0" pitch="-2st">
  Take a deep breath... <break time="2s"/>
</prosody>

<!-- WRONG - sounds robotic -->
<prosody rate="0.85" pitch="-2st">
  Take a deep breath...
</prosody>
```

### Use Breaks for Pacing
| Context | Duration |
|---------|----------|
| Between phrases | 700ms - 1.0s |
| After sentences | 1.0s - 1.7s |
| Breathing cues | 2.0s - 3.0s |
| Visualization | 3.0s - 4.0s |
| Major transitions | 4.0s - 5.5s |

### Pitch by Section
| Section | Pitch |
|---------|-------|
| Pre-talk | 0st |
| Induction | -2st |
| Journey | -1st |
| Integration | -1st |
| Closing | 0st |

### SFX Markers
```xml
<!-- CORRECT: On their own line -->
[SFX: Deep ceremonial bell, resonant, 4 seconds]

<prosody rate="1.0" pitch="-2st">
  The sound echoes...
</prosody>

<!-- WRONG: Inline with text -->
Here is text [SFX: bell] and more text.
```

---

## Audio Production Rules (NON-NEGOTIABLE)

### Stem Levels
| Stem | Level | Notes |
|------|-------|-------|
| Voice | -6 dB | Always voice_enhanced, never raw |
| Binaural | -6 dB | Was -12 dB in old configs |
| SFX | 0 dB | Reference level |

### FFmpeg Mix Command
```bash
ffmpeg -y \
  -i voice_enhanced.wav \
  -i binaural_dynamic.wav \
  -i sfx_track.wav \
  -filter_complex \
    "[0:a]volume=-6dB[voice]; \
     [1:a]volume=-6dB[bin]; \
     [2:a]volume=0dB[sfx]; \
     [voice][bin][sfx]amix=inputs=3:duration=longest:normalize=0[mixed]" \
  -map "[mixed]" \
  -acodec pcm_s16le \
  session_mixed.wav
```

**CRITICAL:** Always use `normalize=0` to prevent unpredictable levels.

### Quality Targets
| Metric | Target |
|--------|--------|
| LUFS | -14 |
| True Peak | -1.5 dBTP max |
| Sample Rate | 48 kHz |
| Bit Depth | 24-bit (WAV), 320 kbps (MP3) |

---

## Python Code Style

### Imports
```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
import yaml
import numpy as np

# Local
from scripts.utilities.logging_config import get_logger
```

### Logging (Prefer over print)
```python
from scripts.utilities.logging_config import get_logger

logger = get_logger(__name__)

def process_audio(session_path):
    logger.info(f"Processing audio for {session_path}")
    try:
        # ... work
        logger.info("Audio processing complete")
    except Exception as e:
        logger.error(f"Audio processing failed: {e}", exc_info=True)
        raise
```

### Error Handling
```python
# CORRECT: Specific exceptions with context
try:
    audio = load_audio(path)
except FileNotFoundError:
    logger.error(f"Audio file not found: {path}")
    raise
except Exception as e:
    logger.error(f"Failed to load audio: {e}", exc_info=True)
    raise

# WRONG: Bare except or silent failures
try:
    audio = load_audio(path)
except:
    pass
```

### Function Documentation
```python
def mix_audio_stems(voice_path: Path, binaural_path: Path, output_path: Path) -> Path:
    """
    Mix voice and binaural stems with standard levels.

    Args:
        voice_path: Path to voice_enhanced.wav
        binaural_path: Path to binaural_dynamic.wav
        output_path: Path for output session_mixed.wav

    Returns:
        Path to the mixed audio file

    Raises:
        FileNotFoundError: If input files don't exist
        subprocess.CalledProcessError: If FFmpeg fails
    """
```

---

## Manifest Schema

```yaml
# Required fields
session:
  name: "session-name"           # kebab-case
  title: "Human Readable Title"
  duration_minutes: 25           # 5-60 range
  desired_outcome: "healing"     # From outcome_registry

# Optional fields
  voice:
    model: "en-US-Neural2-H"     # Default production voice
    speaking_rate: 0.88
    pitch: 0

  visualization_level: 3         # 1-5, determines DVE modules

  archetypes:
    primary: "Healer"
    supporting: ["Guide", "Guardian"]
```

---

## Git Commit Messages

```
[type]: Brief description (imperative mood)

- More details if needed
- Reference issue/session if applicable

🤖 Generated with Claude Code

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

---

## Invariants (Never Break These)

1. **Never use raw `voice.mp3`** - Always `voice_enhanced.mp3`
2. **Never slow SSML rate** - Use `rate="1.0"` with breaks
3. **Never mix without levels** - Voice/binaural at -6dB
4. **Never skip validation** - Run validators before generation
5. **Never commit secrets** - Check `.env` files
6. **Never overwrite without backup awareness** - Check file exists
7. **Always activate venv** - Before running Python scripts
8. **Always use correlation IDs** - For debugging chains
