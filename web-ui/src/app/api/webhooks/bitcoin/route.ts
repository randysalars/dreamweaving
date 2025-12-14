import crypto from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import { applyPaymentEvent } from "@/lib/analytics/payments";

export const runtime = "nodejs";

type BitcoinWebhookPayload = {
  provider_event_id: string;
  provider_event_type?: string;
  invoice_id: string;
  status: "paid" | "confirmed" | "settled" | "expired" | "invalid" | "failed";
  amount?: number;
  currency?: string;
  order_id?: string;
  session_id?: string;
  product_sku?: string;
  attrib?: Record<string, unknown>;
  raw?: Record<string, unknown>;
};

function timingSafeEqualHex(a: string, b: string): boolean {
  try {
    const aBuf = Buffer.from(a, "hex");
    const bBuf = Buffer.from(b, "hex");
    if (aBuf.length !== bBuf.length) return false;
    return crypto.timingSafeEqual(aBuf, bBuf);
  } catch {
    return false;
  }
}

function verifyHmacSha256(raw: string, signatureHeader: string | null, secret: string): boolean {
  if (!signatureHeader) return false;
  const parts = signatureHeader.split("=");
  const sigHex = parts.length === 2 ? parts[1] : signatureHeader;
  const expected = crypto.createHmac("sha256", secret).update(raw).digest("hex");
  return timingSafeEqualHex(expected, sigHex);
}

export async function POST(request: NextRequest) {
  const secret = process.env.BTC_WEBHOOK_SECRET;
  if (!secret) {
    return NextResponse.json({ ok: false, error: "missing_btc_webhook_secret" }, { status: 500 });
  }

  const rawBody = await request.text();
  const sig = request.headers.get("x-dw-signature");
  if (!verifyHmacSha256(rawBody, sig, secret)) {
    return NextResponse.json({ ok: false, error: "signature_verification_failed" }, { status: 401 });
  }

  let payload: BitcoinWebhookPayload;
  try {
    payload = JSON.parse(rawBody) as BitcoinWebhookPayload;
  } catch {
    return NextResponse.json({ ok: false, error: "invalid_json" }, { status: 400 });
  }

  if (!payload.provider_event_id || !payload.invoice_id || !payload.status) {
    return NextResponse.json({ ok: false, error: "missing_fields" }, { status: 400 });
  }

  // Fulfill only on confirmed/settled to avoid 0-conf risk.
  if (payload.status === "paid") {
    await applyPaymentEvent({
      provider: "btc",
      providerEventId: payload.provider_event_id,
      providerEventType: payload.provider_event_type || "invoice.paid",
      providerTxnId: payload.invoice_id,
      orderId: payload.order_id ?? null,
      sessionId: payload.session_id ?? null,
      userId: null,
      status: "pending",
      amount: payload.amount ?? null,
      currency: payload.currency ?? null,
      productSku: payload.product_sku ?? null,
      attrib: payload.attrib ?? {},
      raw: payload.raw ?? (payload as unknown as Record<string, unknown>),
    });
    return NextResponse.json({ ok: true, note: "paid_received_no_fulfillment" });
  }

  const status =
    payload.status === "confirmed" || payload.status === "settled"
      ? "completed"
      : payload.status === "expired" || payload.status === "invalid" || payload.status === "failed"
        ? "failed"
        : "failed";

  await applyPaymentEvent({
    provider: "btc",
    providerEventId: payload.provider_event_id,
    providerEventType: payload.provider_event_type || `invoice.${payload.status}`,
    providerTxnId: payload.invoice_id,
    orderId: payload.order_id ?? null,
    sessionId: payload.session_id ?? null,
    userId: null,
    status,
    amount: payload.amount ?? null,
    currency: payload.currency ?? null,
    productSku: payload.product_sku ?? null,
    attrib: payload.attrib ?? {},
    raw: payload.raw ?? (payload as unknown as Record<string, unknown>),
  });

  return NextResponse.json({ ok: true });
}
