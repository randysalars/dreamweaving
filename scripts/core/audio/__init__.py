"""
Universal Dreamweaving Audio Generation Modules
Complete audio production pipeline from generation to mastering

Sound Generation (IMPLEMENTED):
✓ binaural: Binaural beats (different frequencies per ear)
✓ monaural: Monaural beats (same beat frequency both ears)
✓ isochronic: Isochronic tones (evenly spaced pulses)
✓ panning_beats: Intensity-modulated tones that pan L/R
✓ alternate_beeps: Short tones alternating between ears
✓ am_tones: Amplitude-modulated tones (40-200 Hz)
✓ pink_noise: 1/f noise for relaxation
✓ nature: Procedural nature sounds (rain, stream, forest, ocean)
✓ percussion: Shamanic drumming and rhythmic patterns

Audio Production (IMPLEMENTED):
✓ mixer: Universal stem mixing with sidechain ducking
✓ mastering: LUFS normalization and professional mastering chain

Future modules (TODO):
- ssml_gen: SSML script generation from templates
- tts_gen: Google Cloud TTS integration
- generate_session: Main session orchestrator
"""

__version__ = "1.0.1"
__all__ = [
    # Sound generators
    "binaural",
    "monaural",
    "isochronic",
    "panning_beats",
    "alternate_beeps",
    "am_tones",
    "pink_noise",
    "nature",
    "percussion",
    # Production pipeline
    "mixer",
    "mastering"
]
