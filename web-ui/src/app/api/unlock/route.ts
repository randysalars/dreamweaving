import { NextRequest, NextResponse } from "next/server";
import { getSql } from "@/lib/analytics/db";
import { sanitizeProps } from "@/lib/analytics/sanitize";

export const runtime = "nodejs";

type UnlockRequest = {
  unlock_token?: string;
  session_id?: string;
};

const SESSION_COOKIE = "dw_sid";

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ ok: false, error: "invalid_json" }, { status: 400 });
  }

  const data = body as UnlockRequest;
  const token = typeof data.unlock_token === "string" ? data.unlock_token.trim() : "";
  if (!token) return NextResponse.json({ ok: false, error: "missing_unlock_token" }, { status: 400 });

  const sessionId = data.session_id || request.cookies.get(SESSION_COOKIE)?.value || null;
  const sql = getSql();

  const rows = (await sql`
    select f.order_id::text as order_id, f.product_sku, f.unlock_token, f.revoked_at::text as revoked_at, f.revoke_reason, o.user_id
    from dw_fulfillments f
    join dw_orders o on o.order_id = f.order_id
    where f.unlock_token = ${token}
    limit 1
  `) as unknown as Array<{
    order_id: string;
    product_sku: string | null;
    unlock_token: string;
    revoked_at: string | null;
    revoke_reason: string | null;
    user_id: string | null;
  }>;

  const row = Array.isArray(rows) && rows.length > 0 ? rows[0] : null;
  if (!row) return NextResponse.json({ ok: false, error: "invalid_unlock_token" }, { status: 404 });

  if (row.revoked_at) {
    await sql`
      insert into dw_events (session_id, user_id, name, path, props)
      values (
        ${sessionId},
        ${row.user_id},
        'content_access_denied',
        null,
        ${JSON.stringify(
          sanitizeProps({
            order_id: row.order_id,
            product_sku: row.product_sku,
            unlock_token_prefix: token.slice(0, 8) + "…",
            reason: row.revoke_reason ?? "revoked",
          })
        )}::jsonb
      )
    `;
    return NextResponse.json({ ok: false, error: "revoked" }, { status: 403 });
  }

  if (sessionId) {
    await sql`
      insert into dw_sessions (session_id)
      values (${sessionId})
      on conflict (session_id) do update set last_seen = now()
    `;
  }

  await sql`
    insert into dw_events (session_id, user_id, name, path, props)
    values (
      ${sessionId},
      ${row.user_id},
      'content_access',
      null,
      ${JSON.stringify(
        sanitizeProps({
          order_id: row.order_id,
          product_sku: row.product_sku,
          unlock_token_prefix: token.slice(0, 8) + "…",
          method: "unlock_token",
        })
      )}::jsonb
    )
  `;

  return NextResponse.json({ ok: true, order_id: row.order_id, product_sku: row.product_sku });
}
