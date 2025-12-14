# Dreamweaving Christmas Video — Analytics & Intelligence Implementation

Single source of truth for tracking, attribution, and reporting.

Note: If you are using the first-party Next.js + Neon tracking stack (recommended), follow `web-ui/ANALYTICS.md` instead of GTM/GA4.

## Stack
- **GA4 + GTM (web)** for client events.
- **GA4 Measurement Protocol (server)** for PayPal return/webhook parity.
- **BigQuery export** enabled for modeling/Looker Studio.
- **Cross-domain**: enable GA4 link decoration to PayPal; also pass `session_id` + `client_id` to server calls.

## Data layer contract (all events)
Push as `dataLayer` object keys:
- `event` (GA4 event name), `stage` (awareness|engagement|intent|conversion|reflection)
- `message_type` (christ_centered|gift_for_loved_one|love_offering|healing_peace|silent_suffering|other)
- `cta_label` (e.g., blessing_cta_top), `placement` (hero|footer|modal|inline)
- `video_id`
- `amount`, `currency`, `preset` (bool) for donation selections
- `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`
- `session_id`, `client_id`, `transaction_id` (when present)

## Event map (GA4 events)
| Stage | Event | Trigger | Key params |
| --- | --- | --- | --- |
| Awareness | `page_view_light` | Page load | utm*, session_id, client_id |
| Awareness | `scroll_25/50/75/100` | Scroll thresholds |  |
| Engagement | `time_30s/90s/180s` | Timer thresholds |  |
| Engagement | `exit_before_video` | Before unload if no video_start |  |
| Engagement | `video_start` | First play | video_id, message_type |
| Engagement | `video_25/50/75/95` | Quartiles | video_id |
| Engagement | `video_complete` | Ended | video_id |
| Reflection | `video_replay` | Second play+ | video_id |
| Intent | `donation_cta_click` | Primary CTA click | cta_label, message_type, placement |
| Intent | `donation_amount_selected` | Amount chosen | amount, currency, preset |
| Intent | `paypal_opened` | Redirect/modal open |  |
| Conversion | `donation_success` | PayPal return/webhook | amount, currency, transaction_id, cta_label, message_type, source_medium_campaign |
| Reflection | `share_click` | Share UI | channel |
| Derived | `donation_abandon` | paypal_opened without success after 30m | transaction_id? (if available) |

Mark `donation_success` as a GA4 conversion.

## UTM and CTA taxonomy
- `utm_campaign`: `dreamweaving_christmas_2024`
- `utm_medium`: facebook_post, facebook_group, email, pinterest, youtube, qr, direct
- `utm_source`: channel handle/page/list name
- `utm_content`: blessing_cta_top, gift_for_loved_one, love_offering_faith, healing_peace, silent_suffering, footer_cta, qr_card
- CTA URLs must include the above; QR/print links must preserve UTMs.

## Frontend implementation (GTM)
1) Install GTM container snippet. Enable GA4 config tag with cross-domain for PayPal.
2) Add dataLayer helper (see `dreamweaver/analytics/frontend_tracking.js`):
   - Expose `trackEvent(name, params)` merging defaults (utm, session_id/client_id).
   - Scroll depth listener (25/50/75/100).
   - Timers for 30s/90s/180s.
   - Video hooks (YouTube/HTML5 API) for start/quartiles/95/complete/replay.
   - CTA click handler with `cta_label`, `message_type`, `placement`.
   - `paypal_opened` on redirect/modal open.
3) GTM tags: GA4 event tags for each event above; triggers wired to dataLayer events.

## Server implementation (Measurement Protocol)
- Endpoint should accept `client_id`, `session_id`, `transaction_id`, `amount`, `currency`, `cta_label`, `message_type`, `source_medium_campaign`.
- On PayPal webhook/IPN or return page, POST GA4 MP `donation_success` (see `dreamweaver/analytics/server_mp.py`).
- Scheduled job or worker emits `donation_abandon` MP if no success within 30 minutes of `paypal_opened`.
- Use same GA4 property `measurement_id` and `api_secret`; include `timestamp_micros`.

## QA checklist
- GA4 DebugView: verify every event fires with params (page load, scrolls, timers, video quartiles, CTA, PayPal open/return, abandon).
- BigQuery export enabled and rows arriving.
- UTMs present on every CTA/QR; confirm values in GA4/BigQuery.
- Cross-domain preserves session across PayPal.
- MP parity: server `donation_success` arrives even if client blocked.

## Reporting (Looker Studio on BigQuery)
- Daily board: visitors, video starts/completions, donations, conversion %, avg donation, top 5 sources.
- Funnel: Awareness→Engagement→Intent→Conversion with drop-off; segment by `message_type` and `cta_label`.
- Messaging: CTR→video_start, completion→donation, avg donation by `message_type`/`utm_content`.
- Friction: paypal_opened→donation_success %, video_complete without donation, high scroll/low engagement.
- Reflection: replays, shares, return visits.

## Runbook
- Pre-launch: deploy GTM, confirm DebugView, test PayPal flow in sandbox, verify MP from webhook.
- Launch: monitor daily board; reallocate to top-performing message_type/utm_content.
- Post-campaign: export insights doc (best source, best message, best CTA, spiritual engagement depth, revenue vs reach). Reuse taxonomy for future seasons.
