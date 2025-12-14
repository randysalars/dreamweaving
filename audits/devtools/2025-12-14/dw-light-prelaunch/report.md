# DevTools MCP Audit: dw-light-prelaunch

- Date: 2025-12-14
- Target URL: https://www.salars.net/dreamweaving/light
- Device profiles: Mobile first, then Desktop
- Cache: Disabled (at least one run)
- Browser profile: Clean (no extensions) recommended

## Scope

- [ ] Performance + trust audit
- [ ] Analytics integrity
- [ ] Checkout initiation (UI + provider scripts)

## Findings (summary)

- High:
- Medium:
- Low:

## Evidence (what you observed)

### Performance + trust
- LCP element + timing:
- CLS sources:
- Render blockers:
- Long tasks / main-thread blocking:
- Console warnings/errors:

### Analytics integrity (Network)
- /api/track counts:
  - page_view:
  - landing_view:
  - cta_click:
- Attribution keys present/persist:
- Duplicates/missing:

### Checkout initiation (Network + Console)
- Provider script loads (Stripe/PayPal) + statuses:
- Checkout-related requests + statuses:
- Duplicate initiations:
- Console errors during flow:

## Recommendations (actionable)

- 1.
- 2.
- 3.

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
