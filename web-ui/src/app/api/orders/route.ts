import { NextRequest, NextResponse } from "next/server";
import { getSql } from "@/lib/analytics/db";
import { sanitizeProps } from "@/lib/analytics/sanitize";

export const runtime = "nodejs";

type CreateOrderRequest = {
  provider: "stripe" | "paypal" | "btc";
  amount?: number;
  currency?: string;
  product_sku?: string;
  session_id?: string;
  attrib?: Record<string, unknown>;
};

const SESSION_COOKIE = "dw_sid";

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ ok: false, error: "invalid_json" }, { status: 400 });
  }

  const data = body as CreateOrderRequest;
  if (!data?.provider) {
    return NextResponse.json({ ok: false, error: "missing_provider" }, { status: 400 });
  }

  const sessionId = data.session_id || request.cookies.get(SESSION_COOKIE)?.value || null;
  const amount = typeof data.amount === "number" && Number.isFinite(data.amount) ? data.amount : null;
  const currency = typeof data.currency === "string" && data.currency ? data.currency : "USD";
  const productSku = typeof data.product_sku === "string" && data.product_sku ? data.product_sku : null;
  const attrib = sanitizeProps(data.attrib ?? {});

  const sql = getSql();

  const inserted = await sql`
    insert into dw_orders (session_id, provider, status, amount, currency, product_sku, attrib, updated_at)
    values (${sessionId}, ${data.provider}, 'created', ${amount}, ${currency}, ${productSku}, ${JSON.stringify(attrib)}::jsonb, now())
    returning order_id
  `;

  const rows = Array.isArray(inserted) ? (inserted as Array<{ order_id: string }>) : [];
  const orderId = rows.length > 0 ? rows[0].order_id : null;
  if (!orderId) return NextResponse.json({ ok: false, error: "order_create_failed" }, { status: 500 });

  await sql`
    insert into dw_events (session_id, user_id, name, path, props)
    values (
      ${sessionId},
      null,
      'checkout_start',
      null,
      ${JSON.stringify({ provider: data.provider, order_id: orderId, amount, currency, product_sku: productSku, ...attrib })}::jsonb
    )
  `;

  const providerMetadata = {
    order_id: String(orderId),
    session_id: sessionId ?? undefined,
    product_sku: productSku ?? undefined,
    ...attrib,
  };

  return NextResponse.json({
    ok: true,
    order_id: orderId,
    session_id: sessionId,
    provider_metadata: providerMetadata,
    paypal_custom_id: JSON.stringify(providerMetadata),
    stripe_metadata: providerMetadata,
  });
}

