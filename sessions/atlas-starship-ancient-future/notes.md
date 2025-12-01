# Session Notes — ATLAS, THE STARSHIP OF THE ANCIENT FUTURE

## Intent
- Install skill: *Cosmic Pattern Recognition* (perceive synchronicities, hidden alignments).
- Tone: Cosmic, awe, benevolent AI vessel; ancient-future myth.
- Length target: ~30-35 min (extended version).

## Structure (SSML aligned) — Extended Version
- Pretalk (0:00–3:30): Safety, intent, Atlas intro, preparation.
- Induction Breath (3:30–7:00): Progressive relaxation, body scan, breath work.
- Induction Drift (7:00–11:00): Twilight consciousness, nested loops, 10-count deepening.
- Atlas Appears (11:00–14:30): Ship materialization, recognition, 5-count boarding.
- Boarding Interior (14:30–18:30): Bridge over nebulae, telepathic architecture, consciousness teachings.
- The Guides Appear (18:30–22:30): Star Navigator, Scribe of the Infinite, Atlas revelations.
- Helm Arrival (22:30–27:00): Helm of Observation, becoming sequence, xenolinguistic tones.
- Download Gift (27:00–32:00): Navigational Attunement, Harbinger, inner allies.
- Download Practice (32:00–37:30): Simulation exercises, three practice rounds, skill sealing.
- Integration Return (37:30–42:00): Return corridor, somatic return, final guidance.
- Awakening Count (42:00–46:00): 10-count return, somatic markers, eye opening.
- Post-Hypnotic (46:00–50:00): Three anchors, future pacing, closing.
- Anchors: Breath (3 slow breaths), Symbol (rotating polyhedron), Sensation (warm hum base of spine).

## Audio Plan
- Binaural base: Theta 6.0 Hz; Delta drift 2.5–3 Hz segment; return to 8 Hz.
- Harmonic drone: 111 Hz light-chord feel (carrier ~432 Hz acceptable).
- Sub-bass resonance: ~1 Hz tremor (felt hull hum).
- Textures: hyperspace wind, xenolinguistic microtonal tones, ship-memory echoes.
- Mix targets: Voice 0 dB ref; bed ~ -10 dB; final LUFS ~ -16 voice / -14 master (per manifest).

## Image Beats (PNG names in images/uploaded) — Extended Version
- 01_pretalk (0:00–3:30): Starry threshold, silhouette of Atlas.
- 02_induction (3:30–11:00): Approach/hatch opening, twilight consciousness.
- 03_journey_outer (11:00–18:30): Plasma corridor, glyph bridge, nebula abyss.
- 04_corridor_glyphs (18:30–22:30): Floating glyphs, Star Navigator, Scribe.
- 05_helm_attunement (22:30–32:00): Liquid-light sphere, observer inside, Harbinger.
- 06_gift_download (32:00–42:00): Light lattice download, practice, integration.
- 07_return (42:00–50:00): Cosmic dawn, ship receding, return.

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
