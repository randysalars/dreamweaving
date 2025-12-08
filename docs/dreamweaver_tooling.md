# Dreamweaver Toolkit (CLI Entry Points)

Audience: maintainers/operators who need a single place to find the production-ready Dreamweaving commands. Prefer these interfaces before touching lower-level modules.

## Core Interfaces
- Scaffold session: `./scripts/utilities/create_new_session.sh <slug>` (copies `sessions/_template`); programmatic scaffold via `scripts/ai/dreamweaver_tools.create_session_scaffold`.
- SSML generation: use `scripts/synthesis/*` (v2 variants) to draft sections; templates live in `templates/ENHANCED_SCRIPT_TEMPLATE.md` and `templates/sessions/*.yaml`; assemble into `sessions/<slug>/script.ssml`.
- Validate content: `python scripts/utilities/validate_ssml.py <ssml>` (syntax/stats), `python scripts/utilities/validate_ssml_enhanced.py <ssml> [--fix]`, and session QA with `python scripts/utilities/validate_hypnotic_standards.py sessions/<slug>`; manifest check `python scripts/utilities/validate_manifest.py sessions/<slug>/manifest.yaml`.
- Voice/binaural mix: `python scripts/core/generate_session_audio.py --ssml <path> --voice en-US-Neural2-D --target-minutes <min>` for voice+bed+mix; use `python scripts/core/generate_audio_chunked.py` for voice-only or `python scripts/core/generate_voice.py` for the canonical enhanced voice track.
- Dynamic binaural: `python scripts/core/generate_dynamic_binaural.py --manifest sessions/<slug>/manifest.yaml --output sessions/<slug>/output/binaural_dynamic.wav` (or `--preset <name>` / `--frequency-map <json>`). Static bed alternative: `python scripts/core/generate_binaural.py ...`.
- Timeline/SFX helpers: markers and alignment in `scripts/core/sfx_sync.py`; audio plan writer `scripts/ai/dreamweaver_tools.suggest_audio_bed` saves to `working_files/audio_plan.json`.
- Images/thumbnail: `python scripts/core/generate_images_sd.py --session sessions/<slug> --quality normal`; thumbnail crop/overlay `python scripts/core/generate_thumbnail.py sessions/<slug> [--template ... --palette ...]`.
- YouTube package: `python scripts/core/package_youtube.py --session sessions/<slug>` (builds description/tags/chapters and optional thumbnail).
- Smoke pipeline: `python scripts/ai/pipeline.py sessions/<slug> [--audio-only|--skip-validation|--headless]` or lightweight `python scripts/core/build_session.py --session ... --ssml ... --auto-package`.
- MCP-friendly wrapper: `python scripts/ai/dreamweaver_cli.py <subcommand>` (scaffold | outline | audio-plan | youtube-package) for automation layers that need structured outputs.

## Config References
- Manifest schema: `config/manifest.schema.json` (also `schemas/manifest.schema.json`); template: `sessions/_template/manifest.yaml`.
- Voice defaults: `config/voice_config.yaml` (Google Neural2 profiles, prosody defaults); production voice script `scripts/core/generate_voice.py`.
- Binaural presets: `knowledge/audio/binaural_presets.yaml`; dynamic generator presets embedded in `scripts/core/generate_dynamic_binaural.py`.
- Project/meta config: `.serena/project.yml` (tooling ignores media artifacts; outlines MCP workflows).
