# Archived Scripts

This directory contains legacy code that is no longer in active use.

## Archive Date
2024-12-23

## Reason for Archival
Code audit identified these files as deprecated, unused, or superseded by newer implementations.

## Contents

### synthesis/
Legacy TTS synthesis scripts that were replaced by the unified `scripts/core/generate_voice.py`.

Files:
- `synthesize_pretalk.py` / `synthesize_pretalk_v2.py`
- `synthesize_closing.py` / `synthesize_closing_v2.py`
- `synthesize_natural_hypnotic.py` / `synthesize_natural_hypnotic_v2.py`
- `synthesize_matched_hypnotic.py` / `synthesize_matched_hypnotic_v2.py`
- `synthesize_hypnotic_opening.py` / `synthesize_hypnotic_opening_v2.py`
- `synthesize_ai_pretalk.py` / `synthesize_ai_pretalk_v2.py`
- `synthesize_intro_natural.py` / `synthesize_intro_natural_v2.py`
- `base_synthesizer.py`

### audio/
Legacy audio processing modules superseded by newer implementations.

Files:
- `hypnotic_pacing.py` - Explicitly marked deprecated in code comments

## Restoration
If any of this code needs to be restored, simply move it back to its original location:
- `synthesis/*.py` -> `scripts/synthesis/`
- `audio/*.py` -> `scripts/core/audio/`

## Note
These files remain in version control history and can also be recovered via git if needed.
