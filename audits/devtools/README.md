# DevTools MCP Audits

This folder stores repeatable **browser-truth audits** (performance, analytics, checkout) captured via Chrome DevTools MCP.

Structure:
- `audits/devtools/<YYYY-MM-DD>/<slug>/report.md`
- `audits/devtools/<YYYY-MM-DD>/<slug>/artifacts/` (ignored by git; store traces/log exports here)

Scaffold a new audit:
- `./scripts/utilities/new_devtools_audit.sh "<slug>" --url "https://www.salars.net/xmas/light"`

Diff two audits (report-only):
- `./scripts/utilities/diff_devtools_audits.sh <pathA>/report.md <pathB>/report.md`
