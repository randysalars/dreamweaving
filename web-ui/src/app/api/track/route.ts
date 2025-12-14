import { NextRequest, NextResponse } from "next/server";
import { getSql } from "@/lib/analytics/db";
import { hashIp, hashUserAgent } from "@/lib/analytics/privacy";
import { sanitizeProps } from "@/lib/analytics/sanitize";
import { TrackRequestSchema } from "@/lib/analytics/taxonomy";

export const runtime = "nodejs";

const SESSION_COOKIE = "dw_sid";
const SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 30;

function firstHeaderIp(request: NextRequest): string | null {
  const xff = request.headers.get("x-forwarded-for");
  if (xff) return xff.split(",")[0]?.trim() || null;
  const realIp = request.headers.get("x-real-ip");
  return realIp?.trim() || null;
}

function getOrCreateSessionId(request: NextRequest, bodySessionId?: string): string {
  const cookieSession = request.cookies.get(SESSION_COOKIE)?.value;
  return cookieSession || bodySessionId || crypto.randomUUID();
}

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ ok: false, error: "invalid_json" }, { status: 400 });
  }

  const parsed = TrackRequestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { ok: false, error: "invalid_payload", details: parsed.error.flatten() },
      { status: 400 }
    );
  }

  const { name, path, props, session_id, user_id } = parsed.data;
  const sql = getSql();

  const sessionId = getOrCreateSessionId(request, session_id);
  const cleanedProps = sanitizeProps(props);

  const ua = request.headers.get("user-agent") || "";
  const ip = firstHeaderIp(request) || "";
  const salt = process.env.DW_IP_HASH_SALT;
  const userAgentHash = hashUserAgent(ua, salt);
  const ipHash = ip ? hashIp(ip, salt) : null;

  const referrer =
    (typeof cleanedProps.referrer === "string" && cleanedProps.referrer) ||
    request.headers.get("referer") ||
    null;
  const landingPath =
    (typeof cleanedProps.landing_path === "string" && cleanedProps.landing_path) ||
    (typeof path === "string" ? path : null);

  const utmSource = typeof cleanedProps.utm_source === "string" ? cleanedProps.utm_source : null;
  const utmMedium = typeof cleanedProps.utm_medium === "string" ? cleanedProps.utm_medium : null;
  const utmCampaign = typeof cleanedProps.utm_campaign === "string" ? cleanedProps.utm_campaign : null;
  const utmContent = typeof cleanedProps.utm_content === "string" ? cleanedProps.utm_content : null;
  const utmTerm = typeof cleanedProps.utm_term === "string" ? cleanedProps.utm_term : null;
  const gclid = typeof cleanedProps.gclid === "string" ? cleanedProps.gclid : null;
  const fbclid = typeof cleanedProps.fbclid === "string" ? cleanedProps.fbclid : null;

  await sql`
    insert into dw_sessions (
      session_id,
      landing_path,
      referrer,
      utm_source,
      utm_medium,
      utm_campaign,
      utm_content,
      utm_term,
      gclid,
      fbclid,
      user_agent_hash,
      ip_hash
    )
    values (
      ${sessionId},
      ${landingPath},
      ${referrer},
      ${utmSource},
      ${utmMedium},
      ${utmCampaign},
      ${utmContent},
      ${utmTerm},
      ${gclid},
      ${fbclid},
      ${userAgentHash},
      ${ipHash}
    )
    on conflict (session_id) do update
      set last_seen = now(),
          landing_path = coalesce(dw_sessions.landing_path, excluded.landing_path),
          referrer = coalesce(dw_sessions.referrer, excluded.referrer),
          utm_source = coalesce(dw_sessions.utm_source, excluded.utm_source),
          utm_medium = coalesce(dw_sessions.utm_medium, excluded.utm_medium),
          utm_campaign = coalesce(dw_sessions.utm_campaign, excluded.utm_campaign),
          utm_content = coalesce(dw_sessions.utm_content, excluded.utm_content),
          utm_term = coalesce(dw_sessions.utm_term, excluded.utm_term),
          gclid = coalesce(dw_sessions.gclid, excluded.gclid),
          fbclid = coalesce(dw_sessions.fbclid, excluded.fbclid),
          user_agent_hash = coalesce(dw_sessions.user_agent_hash, excluded.user_agent_hash),
          ip_hash = coalesce(dw_sessions.ip_hash, excluded.ip_hash)
  `;

  await sql`
    insert into dw_events (session_id, user_id, name, path, props)
    values (${sessionId}, ${user_id ?? null}, ${name}, ${path ?? null}, ${JSON.stringify(cleanedProps)}::jsonb)
  `;

  const response = NextResponse.json({ ok: true, session_id: sessionId });
  if (!request.cookies.get(SESSION_COOKIE)?.value) {
    response.cookies.set(SESSION_COOKIE, sessionId, {
      httpOnly: false,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: SESSION_MAX_AGE_SECONDS,
    });
  }
  return response;
}
