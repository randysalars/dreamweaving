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

Load https://www.salars.net/dreamweaving/light.

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
{ "provider":"stripe", "amount":25, "currency":"USD", "product_sku":"xmas_light", "attrib": { "utm_source":"facebook" } }
```

Response includes:
- `order_id`
- `paypal_custom_id` (JSON string for PayPal `custom_id` or `invoice_id`)
- `stripe_metadata` (object for Stripe metadata)

Use these as the “attribution snapshot” you attach to the provider checkout object so webhooks can map back to your `dw_orders`.

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
