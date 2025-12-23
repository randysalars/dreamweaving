import { NextRequest, NextResponse } from "next/server";
import { getSql } from "@/lib/analytics/db";
import { recordDeviceSignals, type DeviceSignalsInput } from "@/lib/analytics/deviceSignals";
import { lookupIpReputation } from "@/lib/analytics/ipReputation";
import { verifyRecaptchaV3 } from "@/lib/analytics/recaptcha";
import { sanitizeProps } from "@/lib/analytics/sanitize";

export const runtime = "nodejs";

type CreateOrderRequest = {
  provider: "stripe" | "paypal" | "btc";
  amount?: number;
  currency?: string;
  product_sku?: string;
  session_id?: string;
  customer_email?: string;
  customer_phone?: string;
  policy_version?: string;
  device_signals?: DeviceSignalsInput;
  recaptcha_token?: string;
  recaptcha_action?: string;
  attrib?: Record<string, unknown>;
};

const SESSION_COOKIE = "dw_sid";

function firstHeaderIp(request: NextRequest): string | null {
  const xff = request.headers.get("x-forwarded-for");
  if (xff) return xff.split(",")[0]?.trim() || null;
  const realIp = request.headers.get("x-real-ip");
  return realIp?.trim() || null;
}

function readCountry(request: NextRequest): string | null {
  const candidates = [
    request.headers.get("x-vercel-ip-country"),
    request.headers.get("cf-ipcountry"),
    request.headers.get("x-country"),
  ];
  for (const c of candidates) {
    if (c && typeof c === "string" && c.trim()) return c.trim().slice(0, 8);
  }
  return null;
}

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ ok: false, error: "invalid_json" }, { status: 400 });
  }

  const data = body as CreateOrderRequest;
  if (!data?.provider) {
    return NextResponse.json({ ok: false, error: "missing_provider" }, { status: 400 });
  }

  const sessionId = data.session_id || request.cookies.get(SESSION_COOKIE)?.value || null;
  const amount = typeof data.amount === "number" && Number.isFinite(data.amount) ? data.amount : null;
  const currency = typeof data.currency === "string" && data.currency ? data.currency : "USD";
  const productSku = typeof data.product_sku === "string" && data.product_sku ? data.product_sku : null;
  const customerEmail = typeof data.customer_email === "string" && data.customer_email.trim() ? data.customer_email.trim() : null;
  const customerPhone = typeof data.customer_phone === "string" && data.customer_phone.trim() ? data.customer_phone.trim() : null;
  const policyVersion =
    typeof data.policy_version === "string" && data.policy_version.trim()
      ? data.policy_version.trim().slice(0, 100)
      : null;
  const attrib = sanitizeProps(data.attrib ?? {});
  const deviceSignals = (data.device_signals ?? null) as DeviceSignalsInput | null;
  const country = readCountry(request);
  const recaptchaToken = typeof data.recaptcha_token === "string" ? data.recaptcha_token.trim() : "";
  const recaptchaAction =
    typeof data.recaptcha_action === "string" && data.recaptcha_action.trim()
      ? data.recaptcha_action.trim().slice(0, 80)
      : null;

  const sql = getSql();

  const inserted = await sql`
    insert into dw_orders (session_id, provider, status, amount, currency, product_sku, customer_email, customer_phone, policy_version, policy_ack_at, attrib, updated_at)
    values (
      ${sessionId},
      ${data.provider},
      'created',
      ${amount},
      ${currency},
      ${productSku},
      ${customerEmail},
      ${customerPhone},
      ${policyVersion},
      null,
      ${JSON.stringify(attrib)}::jsonb,
      now()
    )
    returning order_id
  `;

  const rows = Array.isArray(inserted) ? (inserted as Array<{ order_id: string }>) : [];
  const orderId = rows.length > 0 ? rows[0].order_id : null;
  if (!orderId) return NextResponse.json({ ok: false, error: "order_create_failed" }, { status: 500 });

  const reputation = await lookupIpReputation(request.headers);

  let verifiedRecaptchaScore: number | null = null;
  if (recaptchaToken) {
    try {
      const ip = firstHeaderIp(request);
      const res = await verifyRecaptchaV3({ token: recaptchaToken, expectedAction: recaptchaAction, remoteip: ip });
      verifiedRecaptchaScore = typeof res.score === "number" ? res.score : null;
      await sql`
        insert into dw_events (session_id, user_id, name, path, props)
        values (
          ${sessionId},
          null,
          'recaptcha_verified',
          null,
          ${JSON.stringify(
            sanitizeProps({
              order_id: orderId,
              ok: res.ok,
              score: res.score,
              action: res.action,
            })
          )}::jsonb
        )
      `;
    } catch {
      verifiedRecaptchaScore = null;
    }
  }

  if (deviceSignals) {
    try {
      await recordDeviceSignals({
        sessionId,
        orderId,
        provider: data.provider,
        signals: {
          ...deviceSignals,
          ip_country: deviceSignals.ip_country ?? reputation?.ip_country ?? country,
          recaptcha_score: typeof deviceSignals.recaptcha_score === "number" ? deviceSignals.recaptcha_score : verifiedRecaptchaScore,
          vpn_suspected: typeof deviceSignals.vpn_suspected === "boolean" ? deviceSignals.vpn_suspected : reputation?.vpn_suspected ?? null,
          proxy_suspected:
            typeof deviceSignals.proxy_suspected === "boolean" ? deviceSignals.proxy_suspected : reputation?.proxy_suspected ?? null,
          tor_suspected:
            typeof deviceSignals.tor_suspected === "boolean" ? deviceSignals.tor_suspected : reputation?.tor_suspected ?? null,
          ip_risk_score:
            typeof deviceSignals.ip_risk_score === "number" ? deviceSignals.ip_risk_score : reputation?.ip_risk_score ?? null,
          ip_asn: typeof deviceSignals.ip_asn === "number" ? deviceSignals.ip_asn : reputation?.ip_asn ?? null,
          ip_org: typeof deviceSignals.ip_org === "string" ? deviceSignals.ip_org : reputation?.ip_org ?? null,
        },
      });
      await sql`
        insert into dw_events (session_id, user_id, name, path, props)
        values (
          ${sessionId},
          null,
          'device_signals_recorded',
          null,
          ${JSON.stringify(sanitizeProps({ order_id: orderId, provider: data.provider }))}::jsonb
        )
      `;
    } catch {
      // Non-fatal.
    }
  }
  if (!deviceSignals && (country || verifiedRecaptchaScore !== null || reputation)) {
    try {
      await recordDeviceSignals({
        sessionId,
        orderId,
        provider: data.provider,
        signals: {
          ip_country: reputation?.ip_country ?? country,
          recaptcha_score: verifiedRecaptchaScore,
          vpn_suspected: reputation?.vpn_suspected ?? null,
          proxy_suspected: reputation?.proxy_suspected ?? null,
          tor_suspected: reputation?.tor_suspected ?? null,
          ip_risk_score: reputation?.ip_risk_score ?? null,
          ip_asn: reputation?.ip_asn ?? null,
          ip_org: reputation?.ip_org ?? null,
          raw: reputation?.raw ?? {},
        },
      });
    } catch {
      // Non-fatal.
    }
  }

  await sql`
    insert into dw_events (session_id, user_id, name, path, props)
    values (
      ${sessionId},
      null,
      'checkout_start',
      null,
      ${JSON.stringify(
        sanitizeProps({
          provider: data.provider,
          order_id: orderId,
          amount,
          currency,
          product_sku: productSku,
          policy_version: policyVersion ?? undefined,
          policy_acknowledged: Boolean(policyVersion),
          ...attrib,
        })
      )}::jsonb
    )
  `;

  if (policyVersion) {
    await sql`
      update dw_orders
      set policy_ack_at = coalesce(policy_ack_at, now()), updated_at = now()
      where order_id = ${orderId}::uuid
    `;
    await sql`
      insert into dw_events (session_id, user_id, name, path, props)
      values (
        ${sessionId},
        null,
        'policy_acknowledged',
        null,
        ${JSON.stringify(sanitizeProps({ order_id: orderId, policy_version: policyVersion }))}::jsonb
      )
    `;
  }

  const providerMetadata = {
    order_id: String(orderId),
    session_id: sessionId ?? undefined,
    product_sku: productSku ?? undefined,
    ...attrib,
  };

  return NextResponse.json({
    ok: true,
    order_id: orderId,
    session_id: sessionId,
    provider_metadata: providerMetadata,
    paypal_custom_id: JSON.stringify(providerMetadata),
    stripe_metadata: providerMetadata,
  });
}
