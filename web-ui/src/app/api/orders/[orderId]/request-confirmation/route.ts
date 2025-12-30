import { NextRequest, NextResponse } from "next/server";
import { getSql } from "@/lib/analytics/db";
import { buildConfirmationLink, createOrRefreshOrderConfirmation, maybeNotifyConfirmationWebhook } from "@/lib/analytics/confirmations";

export const runtime = "nodejs";

type RequestConfirmationBody = {
  // Optional override; otherwise uses dw_orders.customer_email.
  customer_email?: string;
  force_new?: boolean;
};

const SESSION_COOKIE = "dw_sid";

export async function POST(request: NextRequest, context: { params: Promise<{ orderId: string }> }) {
  const { orderId } = await context.params;
  if (!orderId) return NextResponse.json({ ok: false, error: "missing_order_id" }, { status: 400 });

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    body = {};
  }

  const data = body as RequestConfirmationBody;
  const sessionId = request.cookies.get(SESSION_COOKIE)?.value || null;

  const sql = getSql();
  const rows = await sql<
    { order_id: string; session_id: string | null; user_id: string | null; customer_email: string | null; risk_score: number | null }[]
  >`
    select order_id::text as order_id, session_id, user_id, customer_email, risk_score
    from dw_orders
    where order_id = ${orderId}::uuid
    limit 1
  `;
  const order = rows.length > 0 ? rows[0] : null;
  if (!order) return NextResponse.json({ ok: false, error: "order_not_found" }, { status: 404 });

  const email =
    typeof data.customer_email === "string" && data.customer_email.trim()
      ? data.customer_email.trim()
      : order.customer_email;
  if (!email) return NextResponse.json({ ok: false, error: "missing_customer_email" }, { status: 400 });

  const created = await createOrRefreshOrderConfirmation(order.order_id, {
    sessionId: order.session_id ?? sessionId,
    userId: order.user_id,
    headers: request.headers,
    forceNew: data.force_new === true,
  });

  // If we created a new confirmation, we can build a link. For an already-pending token, we can't reconstruct the token.
  const confirmUrl = created.token ? await buildConfirmationLink({ token: created.token, orderId: order.order_id }) : null;

  if (confirmUrl) {
    await maybeNotifyConfirmationWebhook({
      order_id: order.order_id,
      customer_email: email,
      confirm_url: confirmUrl,
      risk_score: order.risk_score,
      reasons: null,
    });
  }

  return NextResponse.json({
    ok: true,
    order_id: order.order_id,
    already_pending: created.already_pending,
    confirm_url: confirmUrl,
  });
}
