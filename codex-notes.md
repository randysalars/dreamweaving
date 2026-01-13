# Codex Notes (Dreamweaving)

- VS Code MCP routing policy is defined in `AGENTS.md`.

- Dreamweaving repo: hypnotic audio/video production workflow with SSML scripts, binaural generation, and packaging utilities.
- Session focus: audit existing Dreamweaver automation, normalize entrypoints, and document stable tooling without breaking current flows.

## Dreamweaver Tooling Audit – 2025-12-07
- Inventory current Dreamweaver-related scripts, manifests, and configs.
- Build a capability matrix (what exists vs. where it lives vs. notes/assumptions).
- Define target capabilities and map them to existing implementations or wrappers.
- Capture gaps and lightweight adapter ideas that preserve backward compatibility.
- Added `docs/dreamweaver_tooling.md` summarizing canonical CLI entrypoints per capability.

## Capability Matrix
- Capability: Journey scaffolding
  - Implementation: `scripts/utilities/create_new_session.sh`, `scripts/ai/dreamweaver_tools.py:create_session_scaffold`, template scaffold in `sessions/_template/*`
  - Notes: Shell copies manifest/script/notes from template; Python version also writes outline, audio_plan, youtube_package, notes.md.
- Capability: Journey spec/manifest format
  - Implementation: `sessions/_template/manifest.yaml`, `config/manifest.schema.json` + `schemas/manifest.schema.json`, `config/categories.yaml`
  - Notes: Manifest drives sections + sound_bed/binaural params; used by `generate_session_audio.py` (beat schedule) and YouTube packaging.
- Capability: SSML generation
  - Implementation: Section generators in `scripts/synthesis/*` (v1/v2 variants), templates in `templates/ENHANCED_SCRIPT_TEMPLATE.md` and `templates/sessions/*.yaml`, prompt guides `prompts/hypnotic_dreamweaving_instructions.md`, `prompts/nlp_dreamweaving_techniques.md`
  - Notes: Per-section CLIs; manual assembly into session `script.ssml`.
- Capability: SSML validation/quality
  - Implementation: `scripts/utilities/validate_ssml.py`, `validate_ssml_enhanced.py`, `validate_hypnotic_standards.py`, `validate_session_structure.py`, `validate_manifest.py`, shared rules in `scripts/utilities/validation.py`
  - Notes: Checks syntax, hypnotic standards, safety clauses, structure; enhanced validator can auto-fix common issues.
- Capability: Audio/TTS pipeline
  - Implementation: `scripts/core/generate_audio_chunked.py`, `generate_audio.py`, `generate_session_audio.py`, `generate_voice.py` (+ `audio/voice_enhancement.py`), mixer/mastering helpers under `scripts/core/audio/*`, one-command `scripts/core/build_session.py`
  - Notes: Uses Google TTS; chunked synthesis for large SSML; generate_session_audio mixes binaural bed + voice; build_session wraps audio+video assembly.
- Capability: Audio bed / binaural generation
  - Implementation: `scripts/core/generate_dynamic_binaural.py`, `generate_binaural.py`, presets in `knowledge/audio/binaural_presets.yaml`, engine `scripts/core/audio/binaural.py`, other layers `generate_pink_noise.py`, `audio/nature.py`
  - Notes: Dynamic generator supports manifest-based schedules, preset curves, or frequency-map JSON; saves stems via `audio/binaural.save_stem`.
- Capability: Timeline/SFX metadata
  - Implementation: Markers + alignment in `scripts/core/sfx_sync.py`, session manifest sections for timings, `scripts/ai/dreamweaver_tools.suggest_audio_bed` → `working_files/audio_plan.json`, `scripts/utilities/session_consistency_report.py`
  - Notes: SFX parsing supports natural-language markers; manifest timings feed beat schedules.
- Capability: Image/thumbnail generation
  - Implementation: SDXL tooling `scripts/core/generate_images_sd.py`, `generate_scene_images.py`/`generate_video_images.py`, thumbnail builder `scripts/core/generate_thumbnail.py`, guides `scripts/IMAGE_GENERATION_GUIDE.md`, `scripts/QUICKSTART_IMAGE_GEN.md`
  - Notes: Uses local SDXL (setup script) and ffmpeg-based thumbnail cropper; Midjourney prompt files stored under session working_files.
- Capability: YouTube metadata/packaging
  - Implementation: `scripts/core/package_youtube.py` (+ `package_youtube.sh`), `scripts/ai/dreamweaver_tools.generate_youtube_package/save_youtube_package`
  - Notes: Reads manifest for title/theme/duration, builds description, tags, chapters; can auto-generate thumbnail from session images.
- Capability: Smoke/E2E pipeline
  - Implementation: Orchestrator `scripts/ai/pipeline.py` (validate→voice→binaural→mix→master→vtt→prompts→video→package), simpler audio+video wrapper `scripts/core/build_session.py`, smoke/unit tests under `tests/` (e.g., `tests/unit/test_manifest_validation.py`, `tests/audio_component_smoke.sh`)
  - Notes: Pipeline supports headless/audio-only/skip-validation flags; tests cover validators and config defaults.

## Target Capabilities
- C1: Scaffold a new session (dirs + manifest + starter script/notes).
- C2: Generate SSML content for sections/full script from templates/prompts.
- C3: Validate SSML + manifests + session structure for production standards.
- C4: Generate/mix voice + binaural audio from SSML (chunk-safe, enhanced voice).
- C5: Design/render binaural/audio beds (static or dynamic progressions).
- C6: Produce timeline metadata (section timings, SFX markers/plan).
- C7: Generate imagery/thumbnail prompts and exported assets.
- C8: Generate YouTube/publication package (title/description/tags/chapters/thumbnail).
- C9: Run a smoke end-to-end build for a session (validation → audio → video/package).

## Mapping to Target Capabilities
- C1 Scaffold: Canonical CLI `./scripts/utilities/create_new_session.sh <slug>` (copies sessions/_template). Programmatic scaffold via `scripts/ai/dreamweaver_tools.create_session_scaffold` (writes outline.json, working_files/audio_plan.json, youtube_package.md, notes.md).
- C2 SSML generation: Section CLIs in `scripts/synthesis/*` (v2 preferred), plus templates `templates/ENHANCED_SCRIPT_TEMPLATE.md` and `templates/sessions/*.yaml`; prompts in `prompts/`. Manual assembly into `sessions/<slug>/script.ssml`.
- C3 Validation: Run `python scripts/utilities/validate_ssml.py <ssml>` or `validate_ssml_enhanced.py [--fix] <ssml>`; session-level QA via `python scripts/utilities/validate_hypnotic_standards.py sessions/<slug>` and `validate_session_structure.py`; manifest checks via `validate_manifest.py`.
- C4 Voice/audio mix: Voice-only with `python scripts/core/generate_audio_chunked.py <ssml> <out.mp3> [voice]` (chunk-safe) or production voice via `python scripts/core/generate_voice.py <ssml> <out_dir> [--voice ...]`; full mix via `python scripts/core/generate_session_audio.py --ssml ... [--target-minutes ...]` or one-command audio+video `python scripts/core/build_session.py --session ... --ssml ... [--auto-package]`.
- C5 Binaural bed: Dynamic progression `python scripts/core/generate_dynamic_binaural.py (--manifest ... | --frequency-map ... | --preset <name>) --output ...`; static/preset bed `python scripts/core/generate_binaural.py ...`; presets documented in `knowledge/audio/binaural_presets.yaml`; engine functions in `scripts/core/audio/binaural.py`.
- C6 Timeline/SFX: SFX marker parsing/alignment in `scripts/core/sfx_sync.py` (used by pipeline); manifest `sections` + `sound_bed` timing feed beat schedules; audio plan writer `scripts/ai/dreamweaver_tools.suggest_audio_bed` → `working_files/audio_plan.json`; cross-session reporting via `scripts/utilities/session_consistency_report.py`.
- C7 Imagery/thumbnail: SDXL generator `python scripts/core/generate_images_sd.py --session sessions/<slug> [--quality draft|normal|high]`; scene render helpers `generate_scene_images.py`/`generate_video_images.py`; thumbnail crop/overlay `python scripts/core/generate_thumbnail.py sessions/<slug> [--template ... --palette ...]`.
- C8 YouTube package: `python scripts/core/package_youtube.py --session sessions/<slug>` (reads manifest, builds description/tags/chapters, optional thumbnail); programmatic helpers `dreamweaver_tools.generate_youtube_package` + `save_youtube_package`.
- C9 Smoke pipeline: `python scripts/ai/pipeline.py sessions/<slug> [--audio-only|--skip-validation|--headless]`; lightweight smoke `python scripts/core/build_session.py --session ... --ssml ...`; existing unit tests under `tests/unit` (validators/config) and `tests/audio_component_smoke.sh`.

## Configs/Defaults Observed
- Project config: `.serena/project.yml` (languages python/bash/yaml, ignores media, notes session structure and MCP workflows).
- Manifest schema: `config/manifest.schema.json` and `schemas/manifest.schema.json`; template at `sessions/_template/manifest.yaml`.
- Voice defaults: `config/voice_config.yaml` consolidates profiles/recommendations and prosody defaults; production voice script `scripts/core/generate_voice.py` documents canonical settings.
- Binaural presets/reference: `knowledge/audio/binaural_presets.yaml` (dated 2025-12-05); dynamic generator presets in `scripts/core/generate_dynamic_binaural.py`.
- Session templates and checklists: `templates/` (session archetypes, enhancement checklist), `templates/sessions/*.yaml`, `templates/SESSION_PRODUCTION_CHECKLIST.md`.

## Public Interfaces (recommended)
- CLI-first: prefer `scripts/core/*` for audio/binaural/video/package, `scripts/utilities/*` for validation/scaffolding, and `scripts/ai/pipeline.py` for end-to-end runs.
- MCP-friendly CLI: `scripts/ai/dreamweaver_cli.py` adds stable subcommands (`scaffold`, `outline`, `audio-plan`, `youtube-package`) that wrap `dreamweaver_tools` for automation.
- Programmatic: `scripts/ai/dreamweaver_tools.py` exposes outline/audio-plan/YT package generators and session scaffold helper for Serena/MCP integrations.

## Toolkit Commands (quick ref)
- Scaffold: `./scripts/utilities/create_new_session.sh my-session` or Python scaffold in `scripts/ai/dreamweaver_tools.py`.
- Validate SSML: `python scripts/utilities/validate_ssml.py sessions/my-session/script.ssml` (or `validate_hypnotic_standards.py sessions/my-session` for full QA).
- Voice/Binaural Mix: `python scripts/core/generate_session_audio.py --ssml sessions/my-session/script.ssml --voice en-US-Neural2-D --target-minutes 25`.
- Dynamic Binaural: `python scripts/core/generate_dynamic_binaural.py --manifest sessions/my-session/manifest.yaml --output sessions/my-session/output/binaural_dynamic.wav`.
- Images: `python scripts/core/generate_images_sd.py --session sessions/my-session --quality normal`.
- YouTube Package: `python scripts/core/package_youtube.py --session sessions/my-session`.
- Smoke E2E: `python scripts/ai/pipeline.py sessions/my-session --audio-only` or `python scripts/core/build_session.py --session sessions/my-session --ssml sessions/my-session/script.ssml --auto-package`.
