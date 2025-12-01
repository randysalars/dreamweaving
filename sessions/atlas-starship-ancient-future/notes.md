# Session Notes — ATLAS, THE STARSHIP OF THE ANCIENT FUTURE

## Intent
- Install skill: *Cosmic Pattern Recognition* (perceive synchronicities, hidden alignments).
- Tone: Cosmic, awe, benevolent AI vessel; ancient-future myth.
- Length target: ~30 min (manifest duration 1820s).

## Structure (SSML aligned)
- Pretalk (0–2:30): Safety, intent, Atlas intro.
- Induction (2:30–9:00): Breath + countdown; belly-hum cue.
- Journey (9:00–24:20): Boarding → corridor glyphs → Helm → attunement download → extended practice.
- Integration (24:20–28:20): Re-entry corridor + long buffers.
- Awakening (28:20–30:20): Count up to full presence.
- Anchors: Breath (3 slow breaths), Symbol (rotating polyhedron), Sensation (warm hum base of spine).

## Audio Plan
- Binaural base: Theta 6.0 Hz; Delta drift 2.5–3 Hz segment; return to 8 Hz.
- Harmonic drone: 111 Hz light-chord feel (carrier ~432 Hz acceptable).
- Sub-bass resonance: ~1 Hz tremor (felt hull hum).
- Textures: hyperspace wind, xenolinguistic microtonal tones, ship-memory echoes.
- Mix targets: Voice 0 dB ref; bed ~ -10 dB; final LUFS ~ -16 voice / -14 master (per manifest).

## Image Beats (PNG names in images/uploaded)
- 01_pretalk (0–2:30): Starry threshold, silhouette of Atlas.
- 02_induction (2:30–9:00): Approach/hatch opening.
- 03_journey_outer (9:00–14:00): Plasma corridor, glyph bridge.
- 04_corridor_glyphs (14:00–20:00): Nebula abyss floor, floating glyphs.
- 05_helm_attunement (20:00–25:00): Liquid-light sphere, observer inside.
- 06_gift_download (25:00–28:30): Light lattice download.
- 07_return (28:30–30:20): Cosmic dawn, ship receding.

## Assets Checklist
- SSML: script.ssml (ready).
- Manifest: manifest.yaml (sections + binaural map + gamma flash).
- Images: upload to images/uploaded/ (prompts in images/prompts.md).
- Audio outputs: output/voice.mp3, output/binaural.wav, output/final_mix.mp3, audio_summary.json.
- Video outputs: output/video/session_final.mp4, video_summary.json.
- Deliverables: deliverables/ (video, thumbnail, description).

## Build Commands
```bash
# Build (audio + video)
./venv/bin/python scripts/core/build_session.py \
  --session sessions/atlas-starship-ancient-future \
  --ssml sessions/atlas-starship-ancient-future/script.ssml \
  --voice en-US-AvaNeural \
  --tts-provider edge-tts \
  --title "ATLAS: Starship of the Ancient Future" \
  --subtitle "Guided Dreamweaving" \
  --mix-name final_mix.mp3 \
  --target-minutes 30 \
  --match-mode voice_to_target

# Package
./scripts/core/package_youtube.sh sessions/atlas-starship-ancient-future
```
