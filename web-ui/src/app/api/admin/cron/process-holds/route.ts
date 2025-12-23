import { NextRequest, NextResponse } from "next/server";
import { getSql } from "@/lib/analytics/db";
import { refundPaypalForOrder, refundStripeForOrder } from "@/lib/analytics/refunds";
import { sanitizeProps } from "@/lib/analytics/sanitize";

export const runtime = "nodejs";

function requireCron(request: NextRequest): string | null {
  const secret = process.env.DW_CRON_SECRET;
  if (!secret) return "missing_cron_secret";
  const token = request.headers.get("x-dw-cron-secret");
  if (!token || token !== secret) return "unauthorized";
  return null;
}

type CandidateRow = {
  order_id: string;
  provider: string;
  provider_txn_id: string | null;
  held_at: string | null;
  risk_decision: string | null;
  status: string;
};

export async function POST(request: NextRequest) {
  const authError = requireCron(request);
  if (authError) return NextResponse.json({ ok: false, error: authError }, { status: 401 });

  const hoursRaw = process.env.DW_AUTO_REFUND_UNCONFIRMED_HOURS;
  const hours = hoursRaw && Number.isFinite(Number(hoursRaw)) ? Math.max(1, Number(hoursRaw)) : 24;
  const limitRaw = process.env.DW_CRON_BATCH_LIMIT;
  const limit = limitRaw && Number.isFinite(Number(limitRaw)) ? Math.max(1, Math.min(200, Number(limitRaw))) : 50;

  const sql = getSql();

  const candidates = (await sql`
    select
      o.order_id::text as order_id,
      o.provider,
      o.provider_txn_id,
      o.held_at::text as held_at,
      o.risk_decision,
      o.status
    from dw_orders o
    where o.held_at is not null
      and o.hold_released_at is null
      and o.risk_decision = 'require_email_confirmation'
      and o.status in ('completed', 'refund_requested', 'created')
      and o.held_at <= now() - (${hours}::int * interval '1 hour')
    order by o.held_at asc
    limit ${limit}
  `) as unknown as CandidateRow[];

  let processed = 0;
  const results: Array<{ order_id: string; action: string; ok: boolean; error?: string }> = [];

  for (const c of candidates) {
    processed += 1;
    try {
      if (c.provider === "stripe" && c.provider_txn_id) {
        await refundStripeForOrder({
          orderId: c.order_id,
          providerTxnId: c.provider_txn_id,
          reason: "unconfirmed_timeout",
        });
      } else if (c.provider === "paypal" && c.provider_txn_id) {
        await refundPaypalForOrder({
          orderId: c.order_id,
          captureId: c.provider_txn_id,
          reason: "unconfirmed_timeout",
        });
      } else {
        results.push({ order_id: c.order_id, action: "skip_unsupported_or_missing_txn", ok: false });
        continue;
      }

      await sql`
        update dw_orders
        set hold_released_at = coalesce(hold_released_at, now()),
            hold_released_reason = coalesce(hold_released_reason, 'auto_refund_unconfirmed'),
            updated_at = now()
        where order_id = ${c.order_id}::uuid
      `;

      await sql`
        insert into dw_events (session_id, user_id, name, path, props)
        values (
          null,
          null,
          'order_auto_refunded_unconfirmed',
          null,
          ${JSON.stringify(sanitizeProps({ order_id: c.order_id, after_hours: hours }))}::jsonb
        )
      `;

      results.push({ order_id: c.order_id, action: "refund_requested", ok: true });
    } catch (e) {
      results.push({ order_id: c.order_id, action: "refund_failed", ok: false, error: e instanceof Error ? e.message : String(e) });
    }
  }

  return NextResponse.json({ ok: true, hours, processed, candidates: candidates.length, results });
}
