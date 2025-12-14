import { NextRequest, NextResponse } from "next/server";
import { applyPaymentEvent } from "@/lib/analytics/payments";

export const runtime = "nodejs";

type PaypalWebhookEvent = {
  id?: string;
  event_type?: string;
  resource?: Record<string, unknown>;
};

function paypalBaseUrl(): string {
  const env = (process.env.PAYPAL_ENV || "live").toLowerCase();
  return env === "sandbox" ? "https://api-m.sandbox.paypal.com" : "https://api-m.paypal.com";
}

async function paypalAccessToken(): Promise<string> {
  const clientId = process.env.PAYPAL_CLIENT_ID;
  const clientSecret = process.env.PAYPAL_CLIENT_SECRET;
  if (!clientId || !clientSecret) {
    throw new Error("Missing PAYPAL_CLIENT_ID or PAYPAL_CLIENT_SECRET.");
  }
  const auth = Buffer.from(`${clientId}:${clientSecret}`).toString("base64");
  const resp = await fetch(`${paypalBaseUrl()}/v1/oauth2/token`, {
    method: "POST",
    headers: {
      Authorization: `Basic ${auth}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: "grant_type=client_credentials",
  });
  if (!resp.ok) throw new Error(`PayPal token error ${resp.status}`);
  const json = (await resp.json()) as { access_token?: string };
  if (!json.access_token) throw new Error("PayPal token missing access_token.");
  return json.access_token;
}

async function verifyPaypalWebhookSignature(request: NextRequest, eventBody: unknown): Promise<boolean> {
  const webhookId = process.env.PAYPAL_WEBHOOK_ID;
  if (!webhookId) throw new Error("Missing PAYPAL_WEBHOOK_ID.");

  const transmissionId = request.headers.get("paypal-transmission-id");
  const transmissionTime = request.headers.get("paypal-transmission-time");
  const transmissionSig = request.headers.get("paypal-transmission-sig");
  const certUrl = request.headers.get("paypal-cert-url");
  const authAlgo = request.headers.get("paypal-auth-algo");

  if (!transmissionId || !transmissionTime || !transmissionSig || !certUrl || !authAlgo) {
    return false;
  }

  const token = await paypalAccessToken();
  const resp = await fetch(`${paypalBaseUrl()}/v1/notifications/verify-webhook-signature`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      auth_algo: authAlgo,
      cert_url: certUrl,
      transmission_id: transmissionId,
      transmission_sig: transmissionSig,
      transmission_time: transmissionTime,
      webhook_id: webhookId,
      webhook_event: eventBody,
    }),
  });
  if (!resp.ok) return false;
  const json = (await resp.json()) as { verification_status?: string };
  return json.verification_status === "SUCCESS";
}

function readString(obj: Record<string, unknown> | undefined, key: string): string | null {
  const v = obj?.[key];
  return typeof v === "string" && v ? v : null;
}

function readNestedString(obj: unknown, path: string[]): string | null {
  let cur: unknown = obj;
  for (const part of path) {
    if (cur && typeof cur === "object" && part in (cur as Record<string, unknown>)) {
      cur = (cur as Record<string, unknown>)[part];
    } else {
      return null;
    }
  }
  return typeof cur === "string" && cur ? cur : null;
}

function extractAmount(resource: Record<string, unknown> | undefined): { amount: number | null; currency: string | null } {
  const value = readNestedString(resource, ["amount", "value"]);
  const currency = readNestedString(resource, ["amount", "currency_code"]);
  if (!value) return { amount: null, currency };
  const n = Number(value);
  return { amount: Number.isFinite(n) ? n : null, currency };
}

function tryParseCustom(customId: string | null): Record<string, unknown> {
  if (!customId) return {};
  const trimmed = customId.trim();
  if (!trimmed) return {};
  if (trimmed.startsWith("{") && trimmed.endsWith("}")) {
    try {
      return JSON.parse(trimmed) as Record<string, unknown>;
    } catch {
      return {};
    }
  }
  return { custom_id: trimmed };
}

export async function POST(request: NextRequest) {
  const allowUnverified = process.env.PAYPAL_ALLOW_UNVERIFIED_WEBHOOKS === "true";

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ ok: false, error: "invalid_json" }, { status: 400 });
  }

  if (!allowUnverified) {
    let verified = false;
    try {
      verified = await verifyPaypalWebhookSignature(request, body);
    } catch {
      verified = false;
    }
    if (!verified) {
      return NextResponse.json({ ok: false, error: "signature_verification_failed" }, { status: 401 });
    }
  }

  const event = body as PaypalWebhookEvent;
  const eventType = event.event_type || "unknown";
  const providerEventId = event.id || "";
  if (!providerEventId) {
    return NextResponse.json({ ok: false, error: "missing_event_id" }, { status: 400 });
  }

  const resource = (event.resource || {}) as Record<string, unknown>;
  const providerTxnId =
    readNestedString(resource, ["supplementary_data", "related_ids", "capture_id"]) ||
    readString(resource, "id") ||
    readNestedString(resource, ["supplementary_data", "related_ids", "order_id"]) ||
    null;

  const { amount, currency } = extractAmount(resource);

  const customId =
    readString(resource, "custom_id") ||
    readNestedString(resource, ["purchase_units", "0", "custom_id"]) ||
    readNestedString(resource, ["purchase_units", "0", "invoice_id"]) ||
    null;

  const custom = tryParseCustom(customId);
  const sessionId = typeof custom.session_id === "string" ? custom.session_id : null;
  const orderId = typeof custom.order_id === "string" ? custom.order_id : null;
  const productSku = typeof custom.product_sku === "string" ? custom.product_sku : null;

  const attrib = {
    utm_source: custom.utm_source,
    utm_medium: custom.utm_medium,
    utm_campaign: custom.utm_campaign,
    utm_content: custom.utm_content,
    utm_term: custom.utm_term,
    gclid: custom.gclid,
    fbclid: custom.fbclid,
    referrer: custom.referrer,
    landing_path: custom.landing_path,
  };

  const status =
    eventType === "PAYMENT.CAPTURE.COMPLETED"
      ? "completed"
      : eventType === "PAYMENT.CAPTURE.PENDING" || eventType === "CHECKOUT.ORDER.APPROVED"
        ? "pending"
        : eventType === "PAYMENT.CAPTURE.REFUNDED"
          ? "refund_issued"
          : eventType === "PAYMENT.CAPTURE.DENIED" || eventType === "CHECKOUT.PAYMENT-APPROVAL.REVERSED"
            ? "failed"
            : null;

  if (!status) {
    return NextResponse.json({ ok: true, ignored: true });
  }

  await applyPaymentEvent({
    provider: "paypal",
    providerEventId: providerEventId,
    providerEventType: eventType,
    providerTxnId: providerTxnId,
    orderId: orderId,
    sessionId: sessionId,
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
