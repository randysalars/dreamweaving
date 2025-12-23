import { NextRequest, NextResponse } from "next/server";
import { getSql } from "@/lib/analytics/db";
import { sanitizeProps } from "@/lib/analytics/sanitize";

export const runtime = "nodejs";

type AckPolicyBody = {
  policy_version?: string;
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

  const data = body as AckPolicyBody;
  const policyVersion =
    typeof data.policy_version === "string" && data.policy_version.trim()
      ? data.policy_version.trim().slice(0, 100)
      : "v1";

  const sessionId = request.cookies.get(SESSION_COOKIE)?.value || null;
  const sql = getSql();

  const row = await sql`
    select order_id::text as order_id, session_id, user_id
    from dw_orders
    where order_id = ${orderId}::uuid
    limit 1
  `;
  const rows = Array.isArray(row) ? (row as Array<{ order_id: string; session_id: string | null; user_id: string | null }>) : [];
  const order = rows.length > 0 ? rows[0] : null;
  if (!order) return NextResponse.json({ ok: false, error: "order_not_found" }, { status: 404 });

  await sql`
    update dw_orders
    set policy_version = coalesce(policy_version, ${policyVersion}),
        policy_ack_at = coalesce(policy_ack_at, now()),
        updated_at = now()
    where order_id = ${orderId}::uuid
  `;

  await sql`
    insert into dw_events (session_id, user_id, name, path, props)
    values (
      ${order.session_id ?? sessionId},
      ${order.user_id},
      'policy_acknowledged',
      null,
      ${JSON.stringify(sanitizeProps({ order_id: orderId, policy_version: policyVersion }))}::jsonb
    )
  `;

  return NextResponse.json({ ok: true, order_id: orderId, policy_version: policyVersion });
}

