import { NextRequest, NextResponse } from "next/server";
import { getSql } from "@/lib/analytics/db";

export const runtime = "nodejs";

function requireAdmin(request: NextRequest): string | null {
  const secret = process.env.DW_ADMIN_TOKEN;
  if (!secret) return "missing_admin_secret";
  const token = request.headers.get("x-dw-admin-token");
  if (!token || token !== secret) return "unauthorized";
  return null;
}

export async function GET(request: NextRequest) {
  const authError = requireAdmin(request);
  if (authError) return NextResponse.json({ ok: false, error: authError }, { status: 401 });

  const url = new URL(request.url);
  const limitRaw = url.searchParams.get("limit");
  const limit = limitRaw && Number.isFinite(Number(limitRaw)) ? Math.max(1, Math.min(200, Number(limitRaw))) : 50;

  const sql = getSql();

  const rows = (await sql`
    select
      o.order_id::text as order_id,
      o.created_at,
      o.updated_at,
      o.provider,
      o.provider_txn_id,
      o.status,
      o.amount,
      o.currency,
      o.product_sku,
      o.customer_email,
      o.risk_score,
      o.risk_decision,
      o.held_at,
      o.hold_reason,
      oc.requested_at as confirm_requested_at,
      oc.confirmed_at as confirm_confirmed_at,
      oc.expires_at as confirm_expires_at,
      f.delivered_at,
      f.revoked_at,
      f.revoke_reason
    from dw_orders o
    left join lateral (
      select requested_at, confirmed_at, expires_at
      from dw_order_confirmations
      where order_id = o.order_id
      order by created_at desc
      limit 1
    ) oc on true
    left join lateral (
      select delivered_at, revoked_at, revoke_reason
      from dw_fulfillments
      where order_id = o.order_id
      limit 1
    ) f on true
    where o.held_at is not null and o.hold_released_at is null
    order by o.held_at desc
    limit ${limit}
  `) as unknown as Array<Record<string, unknown>>;

  return NextResponse.json({ ok: true, holds: rows });
}

