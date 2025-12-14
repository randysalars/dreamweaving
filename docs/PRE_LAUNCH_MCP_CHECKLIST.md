# Pre-Launch MCP Checklist (Dreamweaving Web)

Use this checklist before launches/promotions and after changes to `web-ui` (analytics, checkout UI, payment providers).

Prereq: enable Chrome DevTools MCP for this workspace (see `docs/CHROME_DEVTOOLS_MCP.md`).

---

## When to run (recommended gates)

Run this checklist when any of the following changes:
- Anything in `web-ui/src/` affecting checkout buttons, modals, redirects, or pricing
- Anything in `web-ui/src/components/Analytics.tsx` (or analytics helpers)
- Any `/api/*` routes related to orders or webhooks
- Any changes to third-party script loading (Stripe/PayPal/analytics tags)

Also run:
- Before promotions/launches
- After major dependency upgrades (Next.js, Stripe SDK)

## Targets (fill these in)

- Primary landing: `https://www.salars.net/dreamweaving/light`
- Any campaign landing(s): `https://www.salars.net/xmas/light` (example)
- Checkout start: (button click on landing)
- Confirmation/thank-you: (provider-dependent)

---

## 1) Performance + trust (mobile first)

Run on mobile viewport with cache disabled, then desktop.

Pass conditions:
- No runtime errors/hydration warnings that impact UI
- LCP/CLS issues identified with actionable causes (no guessing)
- No obvious render-blocking regressions (new heavy scripts/fonts)

Runbook + prompt: `docs/CHROME_DEVTOOLS_MCP.md`

---

## 2) Analytics integrity

Pass conditions (Network evidence):
- `POST /api/track` fires:
  - `landing_view` once per browser load
  - `page_view` once per route load
  - `cta_click` once per click
- Attribution keys persist (`utm_*`, `gclid`, `fbclid`, `landing_path`, `referrer`)
- No duplicate bursts caused by hydration or rerenders

Reference: `web-ui/ANALYTICS.md`

---

## 3) Checkout initiation (UI + provider scripts)

Pass conditions:
- Love-offering buttons visible and clickable (not overlapped)
- Provider scripts load successfully (Stripe/PayPal)
- No duplicate checkout initiations
- No console errors during checkout start

Reference: `web-ui/PAYMENTS_WEBHOOKS.md`

---

## 4) Webhook truth layer (server-auth)

Pass conditions:
- Webhooks are signature-verified in production
- Idempotency holds: duplicate provider events do not re-fulfill
- `payment_completed` produces exactly one fulfillment + `content_unlock`

Reference: `web-ui/PAYMENTS_WEBHOOKS.md`

---

## 5) Record an audit (recommended)

Create an audit folder + report template:
- `./scripts/utilities/new_devtools_audit.sh "<slug>" --url "https://www.salars.net/dreamweaving/light"`

Then paste MCP findings (counts, request URLs/statuses, console errors) into the report.

If you want stable audits over time, pin the MCP server version:
- copy `config/devtools_mcp.env.example` → `config/devtools_mcp.env` and set `CHROME_DEVTOOLS_MCP_VERSION`.

Sanity-check MCP wiring:
- `./scripts/utilities/smoke_mcp_server.py chrome-devtools --timeout 10`
