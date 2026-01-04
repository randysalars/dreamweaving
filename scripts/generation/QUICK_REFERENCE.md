# Answer Pages Automation - Quick Reference

## 🎯 Current Status

- **Altered States**: 3/124 complete (2.4%)
- **111 placeholder pages** ready for content
- **3 completed pages** (dreams, hypnosis, flow state)

---

## ⚡ Quick Commands

### See What's Next
```bash
python3 scripts/generation/track_content_progress.py --next 10
```

### Generate ALL Pages (with Claude API)
```bash
export ANTHROPIC_API_KEY="your-key"
python3 scripts/generation/batch_generate_content.py --topic altered_states
```

### Generate Placeholders (no API needed)
```bash
python3 scripts/generation/batch_generate_content.py --topic altered_states --template-mode
```

### Validate Quality
```bash
python3 scripts/generation/validate_content_quality.py
```

### Preview Without Generating
```bash
python3 scripts/generation/batch_generate_content.py --topic altered_states --dry-run
```

---

## 📊 Cost Estimates

| Mode | Pages | Cost | Time |
|------|-------|------|------|
| **API (Sonnet 4)** | 111 | $1.10 | 15 min |
| **Template** | 111 | $0 | Instant |
| **Manual Fill** | 111 | $0 | 6-8 days |

---

## ✅ AEO Content Template

### Short Answer (20-35 words)
Direct, declarative. No fluff. Explain WHAT or HOW.

### Why This Matters (2-4 sentences)
Use causal language: **because**, **results in**, **leads to**, **demonstrates**
Be specific about mechanisms.

### Where This Changes (1-3 sentences)
Address boundaries, limits, exceptions.
Spectrum thinking without contradiction.

### ❌ Forbidden Words
Never use: always, never, guaranteed, proven, the best, revolutionary

---

## 🔄 Workflow Options

### Option 1: Full Automation (Fastest)
```bash
# 1. Setup (one-time)
export ANTHROPIC_API_KEY="your-key"

# 2. Generate all
python3 batch_generate_content.py --topic altered_states --concurrent 6

# 3. Validate
python3 validate_content_quality.py

# 4. Deploy
cd salarsu && npm run build && git push
```
**Timeline**: 30 minutes | **Cost**: $1.10

### Option 2: Hybrid (Best Quality)
```bash
# 1. API generate
python3 batch_generate_content.py --topic altered_states

# 2. Find weak pages
python3 validate_content_quality.py | grep WARNING

# 3. Manually refine flagged pages

# 4. Deploy
```
**Timeline**: 15 min + 2-3 hours | **Quality**: Highest

### Option 3: Manual (Current)
```bash
# 1. See next 10
python3 track_content_progress.py --next 10

# 2. Fill each page (VS Code)

# 3. Validate as you go
python3 validate_content_quality.py

# 4. Deploy batch
```
**Timeline**: 6-8 days | **Quality**: High

---

## 🎨 Example Completed Pages

**See these for reference**:
- `salarsu/frontend/app/consciousness/altered-states/definitions-foundations/are-dreams-considered-altered-states/page.tsx`
- `is-hypnosis-an-altered-state-of-consciousness/page.tsx`
- `is-flow-state-an-altered-state/page.tsx`

All follow perfect AEO structure.

---

## 🚨 Safety Features

✅ **Won't overwrite** completed pages (checks for placeholders first)
✅ **Logs everything** to `batch_log_{topic}_{timestamp}.json`
✅ **Dry-run mode** available (`--dry-run`)
✅ **Can resume** from any point (`--skip 50`)

---

## 📈 Progress Tracking

### By Numbers
```bash
python3 track_content_progress.py
```

Shows:
- Overall: X/124 complete (%)
- By cluster: X/Y complete per category
- Next pages to fill

### By Cluster
```bash
python3 track_content_progress.py --cluster "definitions-foundations"
```

---

## 🔍 Quality Validation

```bash
python3 validate_content_quality.py
```

Checks:
- Short Answer: 20-35 words ✓
- Causal language in "Why This Matters" ✓
- No forbidden words ✓
- All sections present ✓

---

## 📦 Next Topics

### Meditation (~130-150 pages)
```bash
# 1. Create meditation_questions.yaml from Marketing_3.md
# 2. Run same batch commands with --topic meditation
```

### Memory Systems (~50-60 pages)
```bash
# 1. Create memory_questions.yaml from Marketing_3.md
# 2. Run same batch commands with --topic memory
```

**Total**: 250+ pages across all 3 topics
**Total Cost**: ~$2.50 for full API automation
**Total Time**: ~35 minutes (API) or 3-4 weeks (manual)

---

## 🆘 Troubleshooting

### "anthropic package not installed"
```bash
pip install anthropic
```

### "API key not set"
```bash
export ANTHROPIC_API_KEY="your-key-here"
# Or add to ~/.bashrc for permanent
```

### Generated placeholders instead of content
You're in template mode. Set API key or fill manually.

### Overwrote my completed pages
Restore from git:
```bash
git checkout HEAD -- path/to/page.tsx
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `batch_generate_content.py` | Main automation script |
| `altered_states_questions.yaml` | 124 questions database |
| `track_content_progress.py` | Progress tracker |
| `validate_content_quality.py` | AEO quality checker |
| `BATCH_AUTOMATION_README.md` | Full documentation |

---

## 💡 Pro Tips

1. **Start with API** - Generate all at once, then refine weak pages
2. **Validate often** - Catch issues early
3. **Use dry-run** - Preview before committing
4. **Check logs** - Every run saves detailed execution log
5. **Resume anywhere** - Use `--skip N` to resume from question N

---

**Last Updated**: 2026-01-04
**Status**: Production Ready ✅
