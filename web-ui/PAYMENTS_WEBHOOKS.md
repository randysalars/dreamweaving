# Dreamweaver Payments → Unified Tracking + Fulfillment

Goal: Stripe, PayPal, and Bitcoin invoice callbacks all produce the same canonical, server-authoritative internal events and fulfill exactly once.

## Canonical internal events (server-auth)
- `payment_completed` → fulfill + unlock
- `payment_failed` → no fulfillment
- `payment_pending` → no fulfillment (optional)
- `refund_issued` → flag/revoke as needed
- `chargeback_received` → hold/investigate

All are written to `dw_events` and orders are upserted in `dw_orders`.

## Idempotency (required)
Every webhook request is deduped via:
- `dw_webhook_events(provider, provider_event_id)` unique

Duplicate webhooks return 200 but do not re-fulfill.

## Fulfillment (idempotent)
On `payment_completed`:
- Issue one unlock token in `dw_fulfillments(order_id)` (unique)
- Emit `dw_events: content_unlock` with `{ order_id, product_sku, unlock_token }`

## Chargeback prevention (risk holds)
On `payment_completed`, the server runs a risk check and may hold fulfillment:
- `dw_events: risk_assessed` (score + decision)
- `dw_events: fulfillment_held` when held (manual release required)

If the decision is `require_email_confirmation`, fulfillment is held until the buyer clicks an email confirmation link:
- `POST /api/orders/:orderId/request-confirmation` (generates a token + confirm URL for sending)
- UI confirm: `/confirm?token=...&order_id=...` (page POSTs token to server and releases fulfillment)
- (Legacy) `GET /api/orders/confirm?token=...&order_id=...` (still supported)

Manual release endpoint:
- `POST /api/admin/orders/:orderId/release-hold` (requires `DW_ADMIN_TOKEN` header `x-dw-admin-token`)

Evidence packet (admin):
- `GET /api/admin/orders/:orderId/evidence-packet` (requires `DW_ADMIN_TOKEN`)

Manual review helpers (admin):
- `GET /api/admin/orders/holds` (requires `DW_ADMIN_TOKEN`)
- `POST /api/admin/orders/:orderId/refund` (Stripe/PayPal; requires `DW_ADMIN_TOKEN`)
- `POST /api/admin/orders/:orderId/resend-confirmation` (email-confirm holds; requires `DW_ADMIN_TOKEN`)
- UI: `/admin/holds` (paste token; review/release/refund + view evidence packet)

reCAPTCHA verification (optional helper):
- `POST /api/verify/recaptcha` (server-side verify; requires `RECAPTCHA_SECRET_KEY`)

Auto-refund cron (unconfirmed email holds):
- `POST /api/admin/cron/process-holds` (requires `DW_CRON_SECRET` header `x-dw-cron-secret`)

## Shared primitives
- Create an order: `POST /api/orders`
- Webhooks:
  - `POST /api/webhooks/stripe`
  - `POST /api/webhooks/paypal`
  - `POST /api/webhooks/bitcoin`

## Frontend checkout truth test (Chrome DevTools MCP)
Use this when you want evidence that the UI triggers the provider flow and no client-side errors block payments.

Prereq: enable `chrome-devtools` MCP for this workspace (see `docs/CHROME_DEVTOOLS_MCP.md`).

What to verify:
- Love-offering buttons are visible, not overlapped, and clickable (also keyboard-focusable)
- Provider scripts load successfully (Stripe/PayPal)
- Checkout-triggering requests fire once (no duplicate initiations)
- No console errors during checkout start (hydration/runtime errors)

Copy/paste prompt:
```text
Use Chrome DevTools MCP.

Load https://www.salars.net/xmas/light.

1) Verify the love-offering buttons are visible and clickable (no overlays).
2) Click to start checkout.
3) Inspect Network for Stripe/PayPal script loads and any checkout requests.
4) Confirm no duplicate initiations.
5) Capture console warnings/errors during the flow.

Report only what you observe, including key request URLs + status codes.
```

## 0) Create an order first (recommended)
Client/server calls:
`POST /api/orders` with JSON:
```json
{
  "provider":"stripe",
  "amount":25,
  "currency":"USD",
  "product_sku":"xmas_light",
  "policy_version":"v1",
  "recaptcha_token":"<client_token>",
  "recaptcha_action":"checkout_start",
  "device_signals": { "vpn_suspected": false },
  "attrib": { "utm_source":"facebook" }
}
```

Response includes:
- `order_id`
- `paypal_custom_id` (JSON string for PayPal `custom_id` or `invoice_id`)
- `stripe_metadata` (object for Stripe metadata)

Use these as the “attribution snapshot” you attach to the provider checkout object so webhooks can map back to your `dw_orders`.

### reCAPTCHA v3 (optional, recommended)
If you have a browser frontend that calls `POST /api/orders`, generate a token client-side and send it as `recaptcha_token` + `recaptcha_action`.

Helper (client): `web-ui/src/lib/analytics/recaptchaClient.ts`
```ts
import { getRecaptchaToken } from "@/lib/analytics/recaptchaClient";

const token = await getRecaptchaToken({
  siteKey: process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY!,
  action: "checkout_start",
});
```

## Stripe

### Minimum webhook events (subscribe)
If using **Checkout**:
- `checkout.session.completed`
- `checkout.session.async_payment_succeeded` (delayed methods)
- `checkout.session.async_payment_failed` (optional)

If using **Payment Intents**:
- `payment_intent.succeeded`
- `payment_intent.payment_failed`

Recommended:
- `charge.refunded`
- `charge.dispute.created`

### Verify
- Header: `stripe-signature`
- Secret: `STRIPE_WEBHOOK_SECRET`

### Mapping
Stripe route: `POST /api/webhooks/stripe`
- Uses `event.id` as `provider_event_id` (idempotency)
- Uses `payment_intent` (or session/charge id) as `provider_txn_id`
- Reads `metadata.order_id`, `metadata.session_id`, `metadata.product_sku` + UTMs for attribution

To attach attribution, set Stripe metadata when creating Checkout Session / PaymentIntent:
- `order_id`, `session_id`, `product_sku`, `utm_*`, `gclid`, `fbclid`, `landing_path`, `referrer`

## PayPal

### Minimum webhook events (subscribe)
- `PAYMENT.CAPTURE.COMPLETED` (authoritative “paid”)
- `PAYMENT.CAPTURE.DENIED` (failed)
- `PAYMENT.CAPTURE.PENDING` (optional)
- `CHECKOUT.ORDER.APPROVED` (optional signal; not “paid”)
- `CHECKOUT.PAYMENT-APPROVAL.REVERSED` (optional)
- `PAYMENT.CAPTURE.REFUNDED` (refund)
- `CUSTOMER.DISPUTE.CREATED` (dispute)
- `CUSTOMER.DISPUTE.UPDATED` (dispute)
- `CUSTOMER.DISPUTE.RESOLVED` (dispute)

### Verify
PayPal signature verification via PayPal API:
- Requires `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, `PAYPAL_WEBHOOK_ID`

Development only:
- `PAYPAL_ALLOW_UNVERIFIED_WEBHOOKS=true`

### Mapping
PayPal route: `POST /api/webhooks/paypal`
- Uses `event.id` as `provider_event_id` (idempotency)
- Uses capture id / order id as `provider_txn_id`
- Reads `custom_id` (recommended) as JSON string containing:
  - `order_id`, `session_id`, `product_sku`, UTMs/referrer/landing

When creating PayPal orders/captures, pass:
- `custom_id = JSON.stringify({ order_id, session_id, product_sku, utm_source, ... })`

## Bitcoin QR (invoice layer)
A raw QR address has no webhooks. Use an invoice system (e.g., BTCPay, Coinbase Commerce, etc.) and forward invoice state changes to your first-party endpoint.

### Endpoint
Bitcoin route: `POST /api/webhooks/bitcoin`

### Verify
- Header: `x-dw-signature` = `sha256=<hex>`
- Secret: `BTC_WEBHOOK_SECRET`
- Signature is HMAC-SHA256 of the raw request body.

### Payload (expected)
```json
{
  "provider_event_id": "unique-event-id",
  "invoice_id": "invoice-or-tx-id",
  "status": "paid|confirmed|settled|expired|invalid|failed",
  "amount": 25,
  "currency": "USD",
  "order_id": "your-order-uuid",
  "session_id": "dw_sid",
  "product_sku": "xmas_light",
  "attrib": { "utm_source": "facebook" }
}
```

### Mapping rule
- `confirmed` / `settled` → `payment_completed` (fulfill)
- `paid` → `payment_pending` (no fulfill)
- `expired` / `invalid` / `failed` → `payment_failed`

## Notes
- Webhooks are the truth layer. Do not trust browser redirects for revenue.
- Always attach `order_id` into provider metadata so refunds/chargebacks can map back cleanly.
