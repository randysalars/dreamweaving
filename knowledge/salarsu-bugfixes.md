# Bugfix Patterns

> Reusable fix recipes. Append here after solving meaningful bugs.

## MDX Compilation

### Stray Opening Braces
**Symptom**: `Error: Unexpected token` in MDX files  
**Root cause**: Unescaped `{` in MDX content (treated as JSX expression)  
**Fix**: Escape with `\{` or `&#123;`  
**Reference**: `PLAYBOOKS/bugfix.md`

### Missing Frontmatter Delimiter
**Symptom**: YAML parsing error in MDX file  
**Root cause**: Missing closing `---` in frontmatter  
**Fix**: Add closing `---` delimiter after frontmatter block

---

## Hydration Mismatches

### Dynamic Content in SSR
**Symptom**: `Text content does not match server-rendered HTML`  
**Root cause**: Date/time or random content rendered differently on server vs client  
**Fix**: Move dynamic content to `useEffect` or add `suppressHydrationWarning`

---

## Database

### Prisma Client Out of Sync
**Symptom**: `The column X does not exist in the current database`  
**Root cause**: Schema changed without regenerating client  
**Fix**: `npm run db:generate`

---

## Build

### Next.js `force-dynamic` in Layout
**Symptom**: All pages become dynamic, losing static optimization  
**Root cause**: `export const dynamic = 'force-dynamic'` in a layout file  
**Fix**: Remove from layout, wrap components using `useSearchParams` in `<Suspense>`

---

_Append new patterns below this line._

### Cron Time Slot Collision — 2026-02-12
**When**: Adding ANY new cron job
**Fix**: Run `crontab -l` first, identify occupied time slots, stagger by 15-30 minutes. Use `$WRAP` and `$SU` variables from crontab header. Keep `scripts/control-plane-cron.txt` as the source of truth for CP jobs.
**Why**: Three control plane cron jobs nearly collided with ntfs-check, answer-page-builder, and daily-briefing.
**Source**: GEMINI.md HARD RULE

### Secrets Scan False Positive — 2026-02-12
**When**: Secrets scan flags placeholder strings like `sk_live_...`
**Fix**: Use regex that requires minimum key length (e.g., `sk_live_[a-zA-Z0-9]{10,}`) to exclude obvious placeholders with dots/ellipsis.
**Why**: `APIDashboard.js` had `sk_live_...` as example text, not a real key.
**Source**: EVIDENCE/agent_gate fix
