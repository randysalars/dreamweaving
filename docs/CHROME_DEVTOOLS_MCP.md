# Chrome DevTools MCP (Dreamweaving)

This repo supports **browser-truth audits** (performance/network/console/accessibility) via **Chrome DevTools MCP**.

Use it when you need facts about what the site is actually doing (no guessing): Core Web Vitals causes, render blockers, hydration errors, payment requests, analytics duplication, etc.

---

## What it is (mental model)

```
Codex (VS Code) / Claude Code
  │
  │ MCP tool calls
  ▼
Chrome DevTools MCP server
  │
  │ Chrome DevTools Protocol (CDP)
  ▼
Live Chromium target (real JS, real layout, real network)
```

Key idea: this is a **debugger interface**, not a “robot browser.” You query runtime truth (network logs, console exceptions, traces).

---

## Enable it in this repo

### VS Code (Codex) MCP config
- This repo’s MCP config is `mcp.json`.
- It includes a `chrome-devtools` server using `scripts/mcp/run_chrome_devtools_mcp_server.sh`.

Optional pinning:
- Preferred: copy `config/devtools_mcp.env.example` → `config/devtools_mcp.env` and set:
  - `CHROME_DEVTOOLS_MCP_VERSION` (pin for stability)
  - `CHROME_DEVTOOLS_MCP_ARGS` (extra CLI args if needed)

### Quick sanity check
Before using it in VS Code, you can confirm the server responds and lists tools:
- `./scripts/utilities/smoke_mcp_server.py chrome-devtools --timeout 10`

---

## How to run audits (recommended standard)

Run each audit twice:
1) **Mobile viewport first** (conversion-critical)
2) **Desktop** (sanity check)

Guidelines:
- Do one run with **cache disabled** (find real bottlenecks).
- Prefer a **clean browser profile** (extensions change layout/network).
- Report only observed data; no speculation.

---

## Prompt templates (copy/paste)

### 1) Performance + trust audit

```
Use Chrome DevTools MCP.

Load: https://www.salars.net/xmas/light

Do:
1) Mobile viewport; cache disabled
2) Capture performance metrics and the primary LCP element
3) Identify CLS sources (what shifted and why)
4) List render-blocking resources (CSS/JS/fonts)
5) Collect console warnings/errors (Next.js hydration, runtime exceptions)

Output:
- Issues with evidence (what you observed)
- Priority (High/Medium/Low)
- Specific fix recommendations (Next.js/code-level)
```

### 2) Payments checkout truth test (Stripe/PayPal)

```
Use Chrome DevTools MCP.

Load: https://www.salars.net/xmas/light

Do:
1) Verify love-offering buttons are visible, not overlapped, and clickable
2) Trigger the checkout flow (click the button)
3) Inspect Network for Stripe/PayPal script loads and API requests
4) Check for duplicate requests
5) Capture console errors during the flow

Output:
- What worked / what failed (only what you observed)
- Network evidence: key request URLs + statuses
- Console evidence: errors/warnings
- Suggested fixes (front-end + webhook safety)
```

### 3) Analytics + funnel integrity

```
Use Chrome DevTools MCP.

Load: https://www.salars.net/xmas/light

Do:
1) Confirm POST /api/track events fire as expected:
   - page_view once per route load
   - landing_view once per browser load
   - cta_click once per click
2) Confirm UTM parameters persist across navigation and checkout start
3) Ensure no duplicate event bursts on hydration/route changes

Output:
- Event evidence: request payload keys + counts (not raw PII)
- Duplicates/missing events
- Recommendations to fix event emission
```

---

## Where these audits map in this repo

- Analytics architecture + expectations: `web-ui/ANALYTICS.md`
- Provider webhook truth layer: `web-ui/PAYMENTS_WEBHOOKS.md`
- Pre-launch checklist: `docs/PRE_LAUNCH_MCP_CHECKLIST.md`

## Recording audits

Scaffold a report folder:
- `./scripts/utilities/new_devtools_audit.sh "<slug>" --url "https://www.salars.net/xmas/light"`

Reports live under `audits/devtools/<YYYY-MM-DD>/<slug>/report.md` (artifacts are ignored by git).
