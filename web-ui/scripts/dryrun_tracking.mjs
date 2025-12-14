import { spawn } from "node:child_process";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import path from "node:path";
import net from "node:net";
import process from "node:process";

import Stripe from "stripe";
import { neon } from "@neondatabase/serverless";

function requireEnv(name) {
  const v = process.env[name];
  if (!v) throw new Error(`Missing required env var: ${name}`);
  return v;
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function waitFor(url, { timeoutMs = 60_000 } = {}) {
  const start = Date.now();
  while (true) {
    try {
      const res = await fetch(url);
      if (res.ok) return;
    } catch {
      // ignore until timeout
    }
    if (Date.now() - start > timeoutMs) throw new Error(`Timeout waiting for ${url}`);
    await sleep(350);
  }
}

function hmacSha256Hex(raw, secret) {
  return crypto.createHmac("sha256", secret).update(raw).digest("hex");
}

function json(obj) {
  return JSON.stringify(obj);
}

async function postJson(url, body, headers = {}) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json", ...headers },
    body: json(body),
  });
  const text = await res.text();
  let parsed = null;
  try {
    parsed = text ? JSON.parse(text) : null;
  } catch {
    parsed = { raw: text };
  }
  return { status: res.status, ok: res.ok, body: parsed };
}

async function main() {
  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const webUiDir = path.resolve(scriptDir, "..");
  const databaseUrl = requireEnv("DATABASE_URL");
  const port = await (async () => {
    if (process.env.DRYRUN_PORT) return Number(process.env.DRYRUN_PORT);
    return new Promise((resolve, reject) => {
      const srv = net.createServer();
      srv.unref();
      srv.on("error", reject);
      srv.listen(0, "127.0.0.1", () => {
        const addr = srv.address();
        if (!addr || typeof addr === "string") return reject(new Error("Failed to allocate port"));
        const p = addr.port;
        srv.close(() => resolve(p));
      });
    });
  })();
  const baseUrl = `http://127.0.0.1:${port}`;

  const stripeWebhookSecret = process.env.STRIPE_WEBHOOK_SECRET || "whsec_dryrun_secret";
  const stripeSecretKey = process.env.STRIPE_SECRET_KEY || "sk_test_dryrun";
  const paypalAllowUnverified = process.env.PAYPAL_ALLOW_UNVERIFIED_WEBHOOKS || "true";
  const btcWebhookSecret = process.env.BTC_WEBHOOK_SECRET || "btc_dryrun_secret";
  const ipHashSalt = process.env.DW_IP_HASH_SALT || "dw_dryrun_salt";

  const env = {
    ...process.env,
    DATABASE_URL: databaseUrl,
    DW_IP_HASH_SALT: ipHashSalt,
    STRIPE_SECRET_KEY: stripeSecretKey,
    STRIPE_WEBHOOK_SECRET: stripeWebhookSecret,
    PAYPAL_ALLOW_UNVERIFIED_WEBHOOKS: paypalAllowUnverified,
    BTC_WEBHOOK_SECRET: btcWebhookSecret,
    PORT: String(port),
  };

  console.log(`[dryrun] building web-ui`);
  const build = spawn("npm", ["run", "build"], { stdio: "inherit", env, cwd: webUiDir });
  const buildCode = await new Promise((resolve) => build.on("exit", resolve));
  if (buildCode !== 0) {
    throw new Error(`web-ui build failed with exit code ${buildCode}`);
  }

  console.log(`[dryrun] starting web-ui on ${baseUrl}`);
  const server = spawn("npm", ["run", "start", "--", "-p", String(port)], {
    stdio: "inherit",
    env,
    cwd: webUiDir,
  });
  const serverExitEarly = new Promise((resolve) => {
    server.once("exit", (code) => resolve(code));
  });

  const killServer = async () => {
    if (server.killed) return;
    server.kill("SIGTERM");
    await sleep(500);
    if (!server.killed) server.kill("SIGKILL");
  };

  const sql = neon(databaseUrl);
  const created = {
    session_id: null,
    order_id: null,
    webhook_events: [],
  };

  try {
    const early = await Promise.race([waitFor(`${baseUrl}/`, { timeoutMs: 30_000 }).then(() => null), serverExitEarly]);
    if (early !== null) {
      throw new Error(`web-ui server exited early with code ${early}`);
    }
    console.log(`[dryrun] POST /api/track`);
    const trackRes = await postJson(`${baseUrl}/api/track`, {
      name: "page_view",
      path: "/xmas/light",
      props: {
        utm_source: "dryrun",
        utm_medium: "cli",
        utm_campaign: "dw_dryrun",
        utm_content: "test",
        landing_path: "/xmas/light",
        referrer: "https://example.com/",
      },
    });
    if (!trackRes.ok) throw new Error(`track failed: ${json(trackRes)}`);
    created.session_id = trackRes.body?.session_id || null;
    if (!created.session_id) throw new Error(`track did not return session_id: ${json(trackRes.body)}`);

    console.log(`[dryrun] POST /api/orders`);
    const ordersRes = await postJson(`${baseUrl}/api/orders`, {
      provider: "stripe",
      amount: 25,
      currency: "USD",
      product_sku: "xmas_light",
      session_id: created.session_id,
      attrib: {
        utm_source: "dryrun",
        utm_medium: "cli",
        utm_campaign: "dw_dryrun",
      },
    });
    if (!ordersRes.ok) throw new Error(`orders failed: ${json(ordersRes)}`);
    created.order_id = ordersRes.body?.order_id || null;
    if (!created.order_id) throw new Error(`orders did not return order_id: ${json(ordersRes.body)}`);

    console.log(`[dryrun] POST /api/webhooks/bitcoin (settled → fulfill)`);
    const btcEventId = `btc_evt_${crypto.randomUUID()}`;
    const btcPayload = {
      provider_event_id: btcEventId,
      provider_event_type: "invoice.settled",
      invoice_id: `inv_${crypto.randomUUID()}`,
      status: "settled",
      amount: 25,
      currency: "USD",
      order_id: created.order_id,
      session_id: created.session_id,
      product_sku: "xmas_light",
      attrib: { utm_source: "dryrun" },
    };
    const btcRaw = json(btcPayload);
    const btcSig = `sha256=${hmacSha256Hex(btcRaw, btcWebhookSecret)}`;
    const btcRes = await fetch(`${baseUrl}/api/webhooks/bitcoin`, {
      method: "POST",
      headers: { "content-type": "application/json", "x-dw-signature": btcSig },
      body: btcRaw,
    });
    if (!btcRes.ok) throw new Error(`bitcoin webhook failed: ${btcRes.status} ${await btcRes.text()}`);
    created.webhook_events.push({ provider: "btc", provider_event_id: btcEventId });

    console.log(`[dryrun] POST /api/webhooks/paypal (CAPTURE.COMPLETED → fulfill)`);
    const paypalEventId = `WH-${crypto.randomUUID()}`;
    const paypalCaptureId = `CAP-${crypto.randomUUID()}`;
    const paypalCustom = JSON.stringify({ order_id: created.order_id, session_id: created.session_id, product_sku: "xmas_light" }).slice(0, 127);
    const paypalPayload = {
      id: paypalEventId,
      event_type: "PAYMENT.CAPTURE.COMPLETED",
      resource: {
        id: paypalCaptureId,
        custom_id: paypalCustom,
        amount: { value: "25.00", currency_code: "USD" },
      },
    };
    const paypalRes = await postJson(`${baseUrl}/api/webhooks/paypal`, paypalPayload);
    if (!paypalRes.ok) throw new Error(`paypal webhook failed: ${json(paypalRes)}`);
    created.webhook_events.push({ provider: "paypal", provider_event_id: paypalEventId });

    console.log(`[dryrun] POST /api/webhooks/stripe (signed → fulfill)`);
    const stripe = new Stripe(stripeSecretKey, { apiVersion: "2025-02-24.acacia" });
    const stripeEvent = {
      id: `evt_${crypto.randomUUID().replace(/-/g, "")}`,
      object: "event",
      api_version: "2025-02-24.acacia",
      created: Math.floor(Date.now() / 1000),
      data: {
        object: {
          id: `pi_${crypto.randomUUID().replace(/-/g, "")}`,
          object: "payment_intent",
          amount_received: 2500,
          currency: "usd",
          metadata: {
            order_id: created.order_id,
            session_id: created.session_id,
            product_sku: "xmas_light",
            utm_source: "dryrun",
          },
        },
      },
      livemode: false,
      pending_webhooks: 1,
      request: { id: null, idempotency_key: null },
      type: "payment_intent.succeeded",
    };
    const stripeRaw = json(stripeEvent);
    const stripeSig = stripe.webhooks.generateTestHeaderString({
      payload: stripeRaw,
      secret: stripeWebhookSecret,
    });
    const stripeRes = await fetch(`${baseUrl}/api/webhooks/stripe`, {
      method: "POST",
      headers: { "stripe-signature": stripeSig, "content-type": "application/json" },
      body: stripeRaw,
    });
    if (!stripeRes.ok) throw new Error(`stripe webhook failed: ${stripeRes.status} ${await stripeRes.text()}`);
    created.webhook_events.push({ provider: "stripe", provider_event_id: stripeEvent.id });

    console.log(`[dryrun] verifying DB writes`);
    const events = await sql`
      select name, ts
      from dw_events
      where session_id = ${created.session_id}
      order by ts desc
      limit 50
    `;
    const names = new Set((events || []).map((r) => r.name));
    const mustHave = ["page_view", "checkout_start", "payment_completed", "content_unlock"];
    for (const n of mustHave) {
      if (!names.has(n)) {
        throw new Error(`missing expected event '${n}' for session_id=${created.session_id}`);
      }
    }

    const fulfillments = await sql`
      select order_id, unlock_token
      from dw_fulfillments
      where order_id = ${created.order_id}::uuid
      limit 1
    `;
    const fulfillmentRow = (fulfillments || [])[0];
    if (!fulfillmentRow?.unlock_token) {
      throw new Error(`missing fulfillment for order_id=${created.order_id}`);
    }

    console.log(`[dryrun] OK`);
    console.log(
      json({
        session_id: created.session_id,
        order_id: created.order_id,
        fulfillment_unlock_token_prefix: String(fulfillmentRow.unlock_token).slice(0, 8) + "…",
      })
    );
  } finally {
    console.log(`[dryrun] cleanup + shutdown`);
    try {
      if (created.order_id) {
        await sql`delete from dw_fulfillments where order_id = ${created.order_id}::uuid`;
        await sql`delete from dw_orders where order_id = ${created.order_id}::uuid`;
      }
      if (created.session_id) {
        await sql`delete from dw_events where session_id = ${created.session_id}`;
        await sql`delete from dw_sessions where session_id = ${created.session_id}`;
      }
      for (const ev of created.webhook_events) {
        await sql`delete from dw_webhook_events where provider = ${ev.provider} and provider_event_id = ${ev.provider_event_id}`;
      }
    } catch (e) {
      console.warn(`[dryrun] cleanup warning: ${e?.message || String(e)}`);
    }
    await killServer();
  }
}

main().catch((err) => {
  console.error(`[dryrun] FAILED: ${err?.message || String(err)}`);
  process.exit(1);
});
