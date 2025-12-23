import { NextRequest, NextResponse } from "next/server";
import { getSql } from "@/lib/analytics/db";
import { buildConfirmationLink, createOrRefreshOrderConfirmation, maybeNotifyConfirmationWebhook } from "@/lib/analytics/confirmations";

export const runtime = "nodejs";

function requireAdmin(request: NextRequest): string | null {
  const secret = process.env.DW_ADMIN_TOKEN;
  if (!secret) return "missing_admin_secret";
  const token = request.headers.get("x-dw-admin-token");
  if (!token || token !== secret) return "unauthorized";
  return null;
}

export async function POST(request: NextRequest, context: { params: Promise<{ orderId: string }> }) {
  const authError = requireAdmin(request);
  if (authError) return NextResponse.json({ ok: false, error: authError }, { status: 401 });

  const { orderId } = await context.params;
  if (!orderId) return NextResponse.json({ ok: false, error: "missing_order_id" }, { status: 400 });

  const sql = getSql();
  const rows = (await sql`
    select order_id::text as order_id, customer_email, risk_score
    from dw_orders
    where order_id = ${orderId}::uuid
    limit 1
  `) as unknown as Array<{ order_id: string; customer_email: string | null; risk_score: number | null }>;
  const order = Array.isArray(rows) && rows.length > 0 ? rows[0] : null;
  if (!order) return NextResponse.json({ ok: false, error: "order_not_found" }, { status: 404 });
  if (!order.customer_email) return NextResponse.json({ ok: false, error: "missing_customer_email" }, { status: 400 });

  const created = await createOrRefreshOrderConfirmation(order.order_id, {
    sessionId: null,
    userId: null,
    forceNew: true,
  });
  if (!created.token) return NextResponse.json({ ok: false, error: "token_create_failed" }, { status: 500 });

  const confirmUrl = await buildConfirmationLink({ token: created.token, orderId: order.order_id });
  await maybeNotifyConfirmationWebhook({
    order_id: order.order_id,
    customer_email: order.customer_email,
    confirm_url: confirmUrl,
    risk_score: order.risk_score,
    reasons: ["admin_resend"],
  });

  return NextResponse.json({ ok: true, order_id: order.order_id, confirm_url: confirmUrl });
}

