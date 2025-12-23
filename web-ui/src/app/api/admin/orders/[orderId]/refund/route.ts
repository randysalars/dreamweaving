import { NextRequest, NextResponse } from "next/server";
import { getSql } from "@/lib/analytics/db";
import { refundPaypalForOrder, refundStripeForOrder } from "@/lib/analytics/refunds";
import { sanitizeProps } from "@/lib/analytics/sanitize";

export const runtime = "nodejs";

function requireAdmin(request: NextRequest): string | null {
  const secret = process.env.DW_ADMIN_TOKEN;
  if (!secret) return "missing_admin_secret";
  const token = request.headers.get("x-dw-admin-token");
  if (!token || token !== secret) return "unauthorized";
  return null;
}

type Body = { reason?: string };

export async function POST(request: NextRequest, context: { params: Promise<{ orderId: string }> }) {
  const authError = requireAdmin(request);
  if (authError) return NextResponse.json({ ok: false, error: authError }, { status: 401 });

  const { orderId } = await context.params;
  if (!orderId) return NextResponse.json({ ok: false, error: "missing_order_id" }, { status: 400 });

  let body: Body = {};
  try {
    body = (await request.json()) as Body;
  } catch {
    body = {};
  }

  const reason = typeof body.reason === "string" && body.reason.trim() ? body.reason.trim().slice(0, 200) : "manual_refund";

  const sql = getSql();
  const rows = (await sql`
    select order_id::text as order_id, provider, provider_txn_id, session_id, user_id, held_at, hold_released_at
    from dw_orders
    where order_id = ${orderId}::uuid
    limit 1
  `) as unknown as Array<{
    order_id: string;
    provider: string;
    provider_txn_id: string | null;
    session_id: string | null;
    user_id: string | null;
    held_at: string | null;
    hold_released_at: string | null;
  }>;
  const order = Array.isArray(rows) && rows.length > 0 ? rows[0] : null;
  if (!order) return NextResponse.json({ ok: false, error: "order_not_found" }, { status: 404 });

  if (order.provider === "stripe" && order.provider_txn_id) {
    await refundStripeForOrder({ orderId: order.order_id, providerTxnId: order.provider_txn_id, reason: "manual_refund" });
  } else if (order.provider === "paypal" && order.provider_txn_id) {
    await refundPaypalForOrder({ orderId: order.order_id, captureId: order.provider_txn_id, reason: "manual_refund" });
  } else {
    return NextResponse.json({ ok: false, error: "unsupported_provider_or_missing_txn" }, { status: 400 });
  }

  await sql`
    update dw_orders
    set hold_released_at = coalesce(hold_released_at, now()),
        hold_released_reason = coalesce(hold_released_reason, ${reason}),
        updated_at = now()
    where order_id = ${order.order_id}::uuid
  `;

  await sql`
    insert into dw_events (session_id, user_id, name, path, props)
    values (
      ${order.session_id},
      ${order.user_id},
      'order_refunded_manual',
      null,
      ${JSON.stringify(sanitizeProps({ order_id: order.order_id, reason }))}::jsonb
    )
  `;

  return NextResponse.json({ ok: true, order_id: order.order_id });
}
