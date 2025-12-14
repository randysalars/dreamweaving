import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";
import { applyPaymentEvent, type PaymentStatus } from "@/lib/analytics/payments";

export const runtime = "nodejs";

function getStripe(): Stripe {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) throw new Error("Missing STRIPE_SECRET_KEY.");
  return new Stripe(key, { apiVersion: "2025-02-24.acacia" });
}

function statusFromStripeEventType(type: string): PaymentStatus | null {
  switch (type) {
    case "checkout.session.completed":
    case "checkout.session.async_payment_succeeded":
    case "payment_intent.succeeded":
      return "completed";
    case "checkout.session.async_payment_failed":
    case "payment_intent.payment_failed":
      return "failed";
    case "charge.refunded":
      return "refund_issued";
    case "charge.dispute.created":
      return "chargeback_received";
    default:
      return null;
  }
}

function numFromCents(v: unknown): number | null {
  if (typeof v !== "number") return null;
  if (!Number.isFinite(v)) return null;
  return v / 100;
}

function readMetadata(obj: unknown): Record<string, string> {
  if (!obj || typeof obj !== "object") return {};
  const record = obj as Record<string, unknown>;
  const meta = record.metadata;
  if (!meta || typeof meta !== "object") return {};
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(meta as Record<string, unknown>)) {
    if (typeof v === "string") out[k] = v;
  }
  return out;
}

export async function POST(request: NextRequest) {
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!webhookSecret) {
    return NextResponse.json({ ok: false, error: "missing_stripe_webhook_secret" }, { status: 500 });
  }

  const sig = request.headers.get("stripe-signature");
  if (!sig) return NextResponse.json({ ok: false, error: "missing_signature" }, { status: 400 });

  const rawBody = await request.text();
  let event: Stripe.Event;
  try {
    event = getStripe().webhooks.constructEvent(rawBody, sig, webhookSecret);
  } catch {
    return NextResponse.json({ ok: false, error: "signature_verification_failed" }, { status: 401 });
  }

  const status = statusFromStripeEventType(event.type);
  if (!status) {
    return NextResponse.json({ ok: true, ignored: true });
  }

  const object = event.data.object as unknown as Record<string, unknown>;
  const metadata = readMetadata(object);
  const orderId = metadata.order_id || null;
  const sessionId = metadata.session_id || null;
  const productSku = metadata.product_sku || null;

  let providerTxnId: string | null = null;
  let amount: number | null = null;
  let currency: string | null = null;

  if (event.type.startsWith("checkout.session.")) {
    providerTxnId = (object.payment_intent as string | undefined) || (object.id as string | undefined) || null;
    amount = numFromCents(object.amount_total);
    currency = (typeof object.currency === "string" && object.currency) || null;
  } else if (event.type.startsWith("payment_intent.")) {
    providerTxnId = (object.id as string | undefined) || null;
    amount = numFromCents(object.amount_received ?? object.amount);
    currency = (typeof object.currency === "string" && object.currency) || null;
  } else if (event.type === "charge.refunded" || event.type === "charge.dispute.created") {
    providerTxnId = (object.payment_intent as string | undefined) || (object.id as string | undefined) || null;
    amount = numFromCents(object.amount_refunded ?? object.amount);
    currency = (typeof object.currency === "string" && object.currency) || null;
  }

  const attrib = {
    utm_source: metadata.utm_source,
    utm_medium: metadata.utm_medium,
    utm_campaign: metadata.utm_campaign,
    utm_content: metadata.utm_content,
    utm_term: metadata.utm_term,
    gclid: metadata.gclid,
    fbclid: metadata.fbclid,
    landing_path: metadata.landing_path,
    referrer: metadata.referrer,
  };

  await applyPaymentEvent({
    provider: "stripe",
    providerEventId: event.id,
    providerEventType: event.type,
    providerTxnId,
    orderId,
    sessionId,
    userId: null,
    status,
    amount,
    currency,
    productSku,
    attrib,
    raw: event as unknown as Record<string, unknown>,
  });

  return NextResponse.json({ ok: true });
}
