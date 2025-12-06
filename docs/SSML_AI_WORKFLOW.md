# 🎙️ VS Code SSML Generation Workflow (Claude → Codex Fallback)

**Purpose:** Keep SSML generation uninterrupted by using the VS Code Claude extension (subscription) as primary and the VS Code Codex/ChatGPT extension (subscription) as automatic fallback. Applies to all dreamweaving SSML script creation.

---

## What You Need
- VS Code with both extensions installed and signed in via subscriptions (no API keys).
- Workspace: `~/Projects/dreamweaving` opened in VS Code.
- Prompts: `prompts/hypnotic_dreamweaving_instructions.md` for style/structure.
- Templates: `templates/base/` (standard), `templates/themes/` (topic-specific).

---

## Primary Path — Claude (Default)
1. Open/create session: `./scripts/utilities/create_new_session.sh "session-name"`.
2. Open `sessions/session-name/script.ssml` in VS Code.
3. In Claude chat, paste the **Standard SSML prompt** (below) with your topic/duration; optionally feed any notes from `sessions/session-name/notes.md`.
4. Ask Claude to return **only SSML**; drop it into `script.ssml`.
5. Run validation:  
   ```bash
   python3 scripts/utilities/validate_ssml_enhanced.py sessions/session-name/script.ssml --fix
   ```
6. If validation fails, fix/re-prompt Claude with the validator errors.

---

## Fallback Triggers — Switch to Codex/ChatGPT When:
- Claude times out or hangs twice in a row.
- Claude returns rate-limit/subscription/access errors.
- Claude replies with empty/garbled output.

**Fast retry policy:** One quick retry with a shorter “please continue with the last prompt” message. If still failing, switch immediately.

---

## Secondary Path — Codex/ChatGPT
1. In the Codex/ChatGPT VS Code extension, reuse the same **Standard SSML prompt**.
2. If Claude produced partial SSML, paste it and ask Codex to continue in the **exact same tone/structure**.
3. Save to `sessions/session-name/script.ssml`, replacing the partial draft.
4. Run the same validator command (above) and fix issues; keep style consistent with the prompt guide.

---

## Quality & Consistency Checklist (Both Tools)
- One root `<speak>` tag; close all tags.
- Use `<prosody rate="0.85" pitch="-2st">` for hypnotic pacing; add `<break time="2-4s"/>` for breaths.
- Use `<phoneme alphabet="ipa" ph="...">` for tricky terms/names.
- Keep within target duration you set in the prompt (default 60–90s per ~160 wpm unless otherwise specified).
- Preserve the 5-section structure from the prompt guide (pre-talk → induction → journey → integration → post-hypnotic).
- Re-run `validate_ssml_enhanced.py --fix` after edits.
- Record which tool you used plus any issues in `sessions/session-name/notes.md` (helps future debugging).

---

## Standard SSML Prompt (Paste into Claude or Codex)
```
Generate an SSML script for a dreamweaving scene about [TOPIC].
Requirements:
- One <speak> root, valid SSML.
- Use prosody for pacing (rate, pitch) and <break> for pauses.
- Add <phoneme alphabet="ipa" ph="..."> for difficult words.
- Maintain a calm, immersive, hypnotic tone with gentle emphasis on key phrases.
- Keep it [DURATION GOAL] (~160 wpm unless I specify otherwise).
Return only SSML.
```

---

## Mini Runbook (Print-and-Go)
- **Primary:** Claude VS Code extension → run validator.
- **Fail once?** Retry quickly. **Fail twice?** Switch to Codex.
- **Fallback:** Codex VS Code extension with same prompt → continue any partial SSML → run validator.
- **Always:** Save to `sessions/<name>/script.ssml`, log which tool was used in `notes.md`.

