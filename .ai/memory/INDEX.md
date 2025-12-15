# Memory Index

> **Purpose:** Cross-reference for incident memories. Search by tag or category.

---

## How to Use

1. **Search by keyword:**
   ```bash
   rg -n "keyword" .ai/memory/
   ```

2. **List all memories:**
   ```bash
   ls -la .ai/memory/*.md | grep -v TEMPLATE | grep -v INDEX
   ```

3. **Add new memory:**
   - Copy `TEMPLATE.md` to `YYYY-MM-DD__short-title.md`
   - Fill in all sections
   - Add entry to this index

---

## Categories

### Audio
Issues related to voice generation, mixing, binaural, mastering.

| Memory | Date | Keywords |
|--------|------|----------|
| (none yet) | | |

### SSML
Issues related to script syntax, TTS rendering, prosody.

| Memory | Date | Keywords |
|--------|------|----------|
| (none yet) | | |

### Video
Issues related to video assembly, encoding, sync.

| Memory | Date | Keywords |
|--------|------|----------|
| (none yet) | | |

### API
Issues related to Google Cloud, external services.

| Memory | Date | Keywords |
|--------|------|----------|
| (none yet) | | |

### Deployment
Issues related to website upload, Vercel, R2 storage.

| Memory | Date | Keywords |
|--------|------|----------|
| (none yet) | | |

### Build
Issues related to session builds, pipeline failures.

| Memory | Date | Keywords |
|--------|------|----------|
| (none yet) | | |

### Validation
Issues related to validators, schema checks.

| Memory | Date | Keywords |
|--------|------|----------|
| (none yet) | | |

---

## Tag Cloud

Common keywords for searching:

**Audio:** `silent`, `clipping`, `levels`, `mix`, `binaural`, `ffmpeg`, `voice`, `enhancement`

**SSML:** `rate`, `break`, `prosody`, `markers`, `sfx`, `tts`, `neural2`

**Video:** `sync`, `encoding`, `resolution`, `vtt`, `subtitles`, `thumbnail`

**API:** `auth`, `credentials`, `google-cloud`, `quota`, `timeout`

**Build:** `venv`, `dependencies`, `timeout`, `disk`, `memory`

---

## Statistics

- **Total memories:** 0
- **Last updated:** (auto-update on add)
- **Most common category:** (pending)

---

## Maintenance

When adding a memory:
1. Create file with date prefix: `YYYY-MM-DD__title.md`
2. Add row to appropriate category table above
3. Update tag cloud if new keywords used
4. Update statistics count

When a memory becomes obsolete (code changed significantly):
1. Move to `.ai/memory/archive/`
2. Remove from index
3. Note replacement if applicable
