import { NextRequest, NextResponse } from "next/server";
import { getSql } from "@/lib/analytics/db";
import { sanitizeProps } from "@/lib/analytics/sanitize";
import { fulfillOrderOnce } from "@/lib/analytics/payments";

export const runtime = "nodejs";

function requireAdmin(request: NextRequest): string | null {
  const secret = process.env.DW_ADMIN_TOKEN;
  if (!secret) return "missing_admin_secret";
  const token = request.headers.get("x-dw-admin-token");
  if (!token || token !== secret) return "unauthorized";
  return null;
}

type ReleaseHoldBody = { reason?: string };

export async function POST(request: NextRequest, context: { params: Promise<{ orderId: string }> }) {
  const authError = requireAdmin(request);
  if (authError) return NextResponse.json({ ok: false, error: authError }, { status: 401 });

  const { orderId } = await context.params;
  if (!orderId) return NextResponse.json({ ok: false, error: "missing_order_id" }, { status: 400 });

  let body: ReleaseHoldBody = {};
  try {
    body = (await request.json()) as ReleaseHoldBody;
  } catch {
    body = {};
  }

  const reason =
    typeof body.reason === "string" && body.reason.trim()
      ? body.reason.trim().slice(0, 200)
      : "manual_release";

  const sql = getSql();
  const rows = (await sql`
    select order_id::text as order_id, session_id, user_id, product_sku, held_at, hold_released_at
    from dw_orders
    where order_id = ${orderId}::uuid
    limit 1
  `) as unknown as Array<{
    order_id: string;
    session_id: string | null;
    user_id: string | null;
    product_sku: string | null;
    held_at: string | null;
    hold_released_at: string | null;
  }>;

  const order = Array.isArray(rows) && rows.length > 0 ? rows[0] : null;
  if (!order) return NextResponse.json({ ok: false, error: "order_not_found" }, { status: 404 });

  if (order.held_at && !order.hold_released_at) {
    await sql`
      update dw_orders
      set hold_released_at = now(), hold_released_reason = ${reason}, updated_at = now()
      where order_id = ${orderId}::uuid and hold_released_at is null
    `;
  }

  if (order.session_id) {
    await sql`
      insert into dw_sessions (session_id)
      values (${order.session_id})
      on conflict (session_id) do update set last_seen = now()
    `;
  }

  const fulfillment = await fulfillOrderOnce({
    orderId: order.order_id,
    sessionId: order.session_id,
    userId: order.user_id,
    productSku: order.product_sku,
    meta: { released_by: "admin", release_reason: reason },
  });

  await sql`
    insert into dw_events (session_id, user_id, name, path, props)
    values (
      ${order.session_id},
      ${order.user_id},
      'fulfillment_released',
      null,
      ${JSON.stringify(
        sanitizeProps({
          order_id: order.order_id,
          reason,
          already_fulfilled: fulfillment.already_fulfilled,
          unlock_token_prefix: fulfillment.unlock_token ? fulfillment.unlock_token.slice(0, 8) + "…" : null,
        })
      )}::jsonb
    )
  `;

  return NextResponse.json({ ok: true, ...fulfillment });
}
