# DevTools MCP Audit: dw-light-prelaunch

- Date: 2025-12-14
- Target URL: https://www.salars.net/xmas/light
- Device profiles: Mobile first, then Desktop
- Cache: Fresh profile per run (`--isolated`); cache not explicitly disabled
- Browser profile: Clean (no extensions) recommended

## Scope

- [x] Performance + trust audit
- [x] Analytics integrity
- [x] Checkout initiation (UI + provider scripts)

## Findings (summary)

- High:
  - Stripe.js fails to load on `https://www.salars.net/xmas/light` (1 request observed; console error present).
  - CSP blocks `https://ep2.adtrafficquality.google/sodar/sodar2.js` (console error) and triggers CSP “blocks some resources” issue.
- Medium:
  - Accessibility issue flagged: “A form field element should have an id or name attribute”.
  - `POST /api/track` not observed on either page load (if first‑party analytics is expected here, it’s not currently firing).
- Low:
  - Render-blocking CSS observed (`/_next/static/css/4616f9c78ff70dfd.css`).
  - Heavy third-party payloads (GTM + Google/Doubleclick ads dominate transfer size).

## Evidence (what you observed)

### Performance + trust
- Runs were executed with Chrome DevTools MCP in `--headless --isolated` mode (fresh profile per run).

#### Landing (correct): `https://www.salars.net/xmas/light`
- Status: `200` on both mobile + desktop.
- Mobile (390×844): LCP `623ms`, CLS `0.0`; LCP resource `https://www.salars.net/dreamweaving/light-hero-image.png`
- Desktop (1365×768): LCP `834ms`, CLS `0.0`; LCP resource `https://www.salars.net/dreamweaving/light-hero-image.png`
- Render-blocking (sample):
  - `https://www.salars.net/_next/static/css/4616f9c78ff70dfd.css`
- Top third-party transfer sizes (sample):
  - Google Tag Manager ~`497.7 kB`
  - Google/Doubleclick Ads ~`391.3 kB`

#### Note (bad URL): `https://www.salars.net/dreamweaving/light`
- Status: `404` (route appears missing).

### Analytics integrity (Network)
- `POST /api/track` observed: `0` (all runs).
- Third-party analytics present (requests observed): `www.googletagmanager.com`, `www.google-analytics.com`.
- `data-dw-cta` elements on page: `0` (all runs), so no CTA instrumentation via `data-dw-cta` could be validated.

### Checkout initiation (Network + Console)
- No checkout clicks were triggered (audit focused on load-time truth + script availability).
- Stripe:
  - Network: `js.stripe.com` requests observed on `/xmas/light` (`stripe=1`).
  - Console: `Failed to load Stripe.js` (error observed on `/xmas/light`).
- PayPal:
  - Network: no PayPal requests observed (`paypal=0`).
- Donate UI presence (snapshot):
  - `uid=1_179 button "Donate"` on the `404` route page (target URL).

## Recommendations (actionable)

- 1. Fix or update the canonical landing URL: `https://www.salars.net/dreamweaving/light` currently `404` (either correct the route or update runbooks/prompts to the real landing, e.g. `https://www.salars.net/xmas/light`).
- 2. Fix Stripe loading on `https://www.salars.net/xmas/light`: investigate why Stripe.js fails (CSP allowlist for `https://js.stripe.com` and/or script injection timing).
- 3. Reduce render-blocking + third-party impact: address render-blocking CSS and consider deferring heavy third-party scripts (GTM/Ads) to improve LCP.

## Notes

- Runbooks:
  - docs/CHROME_DEVTOOLS_MCP.md
  - web-ui/ANALYTICS.md
  - web-ui/PAYMENTS_WEBHOOKS.md

## Post-fix rerun (fill in after changes)

- Date:
- What changed:
- Result deltas:
  - Performance:
  - Analytics:
  - Checkout:
