# Dreamweaver First-Party Analytics (salars.net)

This is a first-party, privacy-respecting tracking stack for Dreamweaver on Vercel + Neon Postgres.

## What you get
- A **first-party** collector on your own domain: `POST /api/track`
- An **append-only** event store (`dw_events`) + session table (`dw_sessions`) + orders table (`dw_orders`)
- Client-side tracking for: `page_view`, `landing_view`, `cta_click`, `outbound_click`
- A PayPal **webhook stub**: `POST /api/webhooks/paypal` that writes authoritative `payment_completed`/`payment_failed` events

## 1) Provision Postgres (Neon)
1. Create a Neon Postgres database.
2. Copy your connection string as `DATABASE_URL`.
3. Apply migrations in order:
   - `web-ui/migrations/001_dw_analytics.sql`
   - `web-ui/migrations/002_dw_events_nullable_session.sql`
   - `web-ui/migrations/003_dw_webhook_events.sql`
   - `web-ui/migrations/004_dw_fulfillments.sql`

Neon console: paste + run each file in the SQL editor.

## 2) Set required environment variables
In Vercel (Project → Settings → Environment Variables):
- `DATABASE_URL` = Neon connection string
- `DW_IP_HASH_SALT` = a long random secret (used to hash IP + UA; do not rotate often)

Optional (PayPal webhooks):
- `PAYPAL_ENV` = `sandbox` or `live` (default `live`)
- `PAYPAL_CLIENT_ID`
- `PAYPAL_CLIENT_SECRET`
- `PAYPAL_WEBHOOK_ID`
- `PAYPAL_ALLOW_UNVERIFIED_WEBHOOKS` = `true` (development only; do not enable in production)

Optional (Stripe webhooks):
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

Optional (Bitcoin invoice webhooks):
- `BTC_WEBHOOK_SECRET` (HMAC secret for `x-dw-signature`)

## 3) Client tracking (already wired)
`web-ui/src/components/Analytics.tsx` is mounted in `web-ui/src/app/layout.tsx`.

It automatically sends:
- `page_view` on route change
- `landing_view` once per browser load
- `cta_click` when clicking any element with `data-dw-cta="..."`
- `outbound_click` when clicking external links

### Tag CTAs in your UI
Add attributes to any clickable element:
```html
<a
  href="/xmas/light"
  data-dw-cta="blessing_cta_top"
  data-dw-message="christ_centered"
  data-dw-placement="hero"
>
  Experience the Dreamweaving
</a>
```

## 4) Attribution (UTMs)
The client helper persists UTMs + landing/referrer into `localStorage` and attaches them to every event.

Captured keys:
- `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`
- `gclid`, `fbclid`
- `landing_path`, `referrer`

## 5) PayPal “truth layer” (recommended flow)
Webhooks are authoritative for money, but webhooks often don’t contain your session id.

To make attribution reliable, include your own metadata in the PayPal order:
- Put your `session_id` and attribution snapshot into `custom_id` (or `invoice_id`) when creating the PayPal order.
- Example `custom_id` (JSON string):
  `{"session_id":"<dw_sid>","product_sku":"xmas_light","utm_source":"facebook","utm_campaign":"dreamweaving_christmas_2024"}`

Then the webhook route will:
- upsert `dw_orders` and emit `payment_completed`/`payment_failed`
- attach the attribution snapshot to the event/order

Webhook endpoint:
- `POST /api/webhooks/paypal` (verify signatures by default)

## 5b) Unified payments + fulfillment
This repo includes:
- `POST /api/orders` to create a `dw_orders` row and return `paypal_custom_id` + `stripe_metadata` for attribution.
- `POST /api/webhooks/paypal`, `POST /api/webhooks/stripe`, `POST /api/webhooks/bitcoin` to emit canonical server-side events.
- Fulfillment: on `payment_completed` the server issues an idempotent unlock token in `dw_fulfillments` and emits `content_unlock`.

See `web-ui/PAYMENTS_WEBHOOKS.md` for the provider event mapping and verification rules.

## 6) Verifying it works
### Local dev
1. `cd web-ui`
2. `npm run dev`
3. Open the site and click around.
4. Query Neon:
   - `select * from dw_events order by ts desc limit 50;`
   - `select * from dw_sessions order by last_seen desc limit 50;`

### Production
1. Deploy to Vercel.
2. Confirm requests to `/api/track` succeed (Vercel logs).
3. Confirm events are in Neon.

### Browser-truth verification (Chrome DevTools MCP)
Use this when you want high confidence that tracking is firing exactly once and carrying attribution correctly.

Prereq: enable `chrome-devtools` MCP for this workspace (see `docs/CHROME_DEVTOOLS_MCP.md`).

What to check (in Network):
- `POST /api/track` fires:
  - `page_view` once per route load
  - `landing_view` once per browser load
  - `cta_click` once per click (no double-fires)
- Payload includes attribution snapshot keys when present (`utm_*`, `gclid`, `fbclid`, `landing_path`, `referrer`)
- No bursts caused by hydration or rerenders

Copy/paste prompt:
```text
Use Chrome DevTools MCP.

Load https://www.salars.net/xmas/light.

Inspect Network and confirm:
- POST /api/track fires expected events exactly once
- No duplicate event bursts on hydration/route changes
- UTM attribution keys persist across navigation

Report only observed request counts + key payload fields (no raw PII).
```

## 7) Reporting
Start with 3 queries/dashboards (Metabase/Superset/Grafana/SQL):
- Funnel: `landing_view → cta_click → payment_completed`
- Revenue by `utm_source/utm_campaign`
- Top pages by conversion rate (`page_view` + `payment_completed`)

If volume grows, you can later:
- replicate to a warehouse (BigQuery/Snowflake)
- move `dw_events` to ClickHouse for analytics-scale queries
