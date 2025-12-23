import { NextRequest, NextResponse } from "next/server";
import { getSql } from "@/lib/analytics/db";
import { confirmOrderByToken } from "@/lib/analytics/confirmations";
import { fulfillOrderOnce } from "@/lib/analytics/payments";
import { sanitizeProps } from "@/lib/analytics/sanitize";

export const runtime = "nodejs";

const SESSION_COOKIE = "dw_sid";

function responseHeaders(): Headers {
  return new Headers({
    "Cache-Control": "no-store",
    Pragma: "no-cache",
    "Referrer-Policy": "no-referrer",
  });
}

async function processConfirm(request: NextRequest, input: { token: string; order_id?: string | null }) {
  const headers = responseHeaders();
  const token = input.token.trim();
  const orderIdHint = (input.order_id || "").trim();
  if (!token) return NextResponse.json({ ok: false, error: "missing_token" }, { status: 400, headers });

  const sessionId = request.cookies.get(SESSION_COOKIE)?.value || null;
  const sql = getSql();

  let confirmed;
  try {
    confirmed = await confirmOrderByToken(token, { sessionId, userId: null, headers: request.headers });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "invalid_token";
    return NextResponse.json({ ok: false, error: msg }, { status: 400, headers });
  }

  const resolvedOrderId = confirmed.order_id || orderIdHint;

  const rows = (await sql`
    select order_id::text as order_id, session_id, user_id, product_sku
    from dw_orders
    where order_id = ${resolvedOrderId}::uuid
    limit 1
  `) as unknown as Array<{ order_id: string; session_id: string | null; user_id: string | null; product_sku: string | null }>;
  const order = Array.isArray(rows) && rows.length > 0 ? rows[0] : null;
  if (!order) return NextResponse.json({ ok: false, error: "order_not_found" }, { status: 404, headers });

  if (order.session_id) {
    await sql`
      insert into dw_sessions (session_id)
      values (${order.session_id})
      on conflict (session_id) do update set last_seen = now()
    `;
  }

  const fulfillment = await fulfillOrderOnce({
    orderId: order.order_id,
    sessionId: order.session_id ?? sessionId,
    userId: order.user_id,
    productSku: order.product_sku,
    meta: { released_by: "email_confirm" },
  });

  await sql`
    insert into dw_events (session_id, user_id, name, path, props)
    values (
      ${order.session_id ?? sessionId},
      ${order.user_id},
      'fulfillment_released',
      null,
      ${JSON.stringify(
        sanitizeProps({
          order_id: order.order_id,
          released_by: "email_confirm",
          already_fulfilled: fulfillment.already_fulfilled,
          unlock_token_prefix: fulfillment.unlock_token ? fulfillment.unlock_token.slice(0, 8) + "…" : null,
        })
      )}::jsonb
    )
  `;

  const successRedirect = process.env.DW_CONFIRM_SUCCESS_URL;
  if (successRedirect) {
    const out = new URL(successRedirect);
    out.searchParams.set("order_id", order.order_id);
    const resp = NextResponse.redirect(out.toString(), { status: 302 });
    headers.forEach((v, k) => resp.headers.set(k, v));
    return resp;
  }

  return NextResponse.json({ ...confirmed, ...fulfillment }, { headers });
}

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const token = (url.searchParams.get("token") || "").trim();
  const orderIdHint = (url.searchParams.get("order_id") || "").trim();
  return processConfirm(request, { token, order_id: orderIdHint });
}

export async function POST(request: NextRequest) {
  const headers = responseHeaders();
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ ok: false, error: "invalid_json" }, { status: 400, headers });
  }
  const data = body as { token?: string; order_id?: string };
  const token = typeof data.token === "string" ? data.token : "";
  const orderIdHint = typeof data.order_id === "string" ? data.order_id : null;
  return processConfirm(request, { token, order_id: orderIdHint });
}
