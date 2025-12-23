"use client";

import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

type HoldRow = Record<string, unknown> & { order_id?: string };

async function apiGet(path: string, adminToken: string): Promise<unknown> {
  const resp = await fetch(path, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "x-dw-admin-token": adminToken,
    },
    cache: "no-store",
  });
  const json = (await resp.json()) as unknown;
  if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${JSON.stringify(json)}`);
  return json;
}

async function apiPost(path: string, adminToken: string, body: unknown = {}): Promise<unknown> {
  const resp = await fetch(path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-dw-admin-token": adminToken,
    },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  const json = (await resp.json()) as unknown;
  if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${JSON.stringify(json)}`);
  return json;
}

function asString(v: unknown): string {
  return typeof v === "string" ? v : v == null ? "" : String(v);
}

export default function HoldsAdminPage() {
  const [adminToken, setAdminToken] = useState("");
  const [limit, setLimit] = useState(50);
  const [holds, setHolds] = useState<HoldRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const [packetJson, setPacketJson] = useState<string | null>(null);

  useEffect(() => {
    const saved = window.sessionStorage.getItem("dw_admin_token");
    if (saved) setAdminToken(saved);
  }, []);

  useEffect(() => {
    if (!adminToken) return;
    window.sessionStorage.setItem("dw_admin_token", adminToken);
  }, [adminToken]);

  const canQuery = useMemo(() => adminToken.trim().length > 0, [adminToken]);

  async function refresh() {
    setError(null);
    setPacketJson(null);
    setSelectedOrderId(null);
    setLoading(true);
    try {
      const json = (await apiGet(`/api/admin/orders/holds?limit=${encodeURIComponent(String(limit))}`, adminToken)) as {
        holds?: HoldRow[];
      };
      setHolds(Array.isArray(json.holds) ? json.holds : []);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  async function getPacket(orderId: string) {
    setError(null);
    setSelectedOrderId(orderId);
    setPacketJson(null);
    setLoading(true);
    try {
      const json = (await apiGet(`/api/admin/orders/${encodeURIComponent(orderId)}/evidence-packet`, adminToken)) as unknown;
      setPacketJson(JSON.stringify(json, null, 2));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  async function release(orderId: string) {
    setError(null);
    setLoading(true);
    try {
      await apiPost(`/api/admin/orders/${encodeURIComponent(orderId)}/release-hold`, adminToken, { reason: "admin_ui_release" });
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setLoading(false);
    }
  }

  async function refund(orderId: string) {
    setError(null);
    setLoading(true);
    try {
      await apiPost(`/api/admin/orders/${encodeURIComponent(orderId)}/refund`, adminToken, { reason: "admin_ui_refund" });
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setLoading(false);
    }
  }

  async function resendConfirmation(orderId: string) {
    setError(null);
    setLoading(true);
    try {
      const res = (await apiPost(
        `/api/admin/orders/${encodeURIComponent(orderId)}/resend-confirmation`,
        adminToken,
        {}
      )) as Record<string, unknown>;
      const url = typeof res.confirm_url === "string" ? res.confirm_url : null;
      if (url) {
        setSelectedOrderId(orderId);
        setPacketJson(`Resent confirmation link:\n${url}`);
      }
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-amber-50 text-slate-900">
      <main className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-10">
        <Card>
          <CardHeader>
            <CardTitle>Held Orders</CardTitle>
            <CardDescription>Manual review queue: evidence packet, release hold, or refund (Stripe only).</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <div className="grid gap-3 md:grid-cols-3">
              <div className="md:col-span-2">
                <label className="text-sm font-medium text-slate-700">Admin token</label>
                <Input
                  type="password"
                  value={adminToken}
                  onChange={(e) => setAdminToken(e.target.value)}
                  placeholder="DW_ADMIN_TOKEN"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Limit</label>
                <Input
                  type="number"
                  min={1}
                  max={200}
                  value={limit}
                  onChange={(e) => setLimit(Number(e.target.value))}
                />
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button disabled={!canQuery || loading} onClick={refresh}>
                {loading ? "Loading..." : "Refresh"}
              </Button>
              <Button
                variant="outline"
                disabled={!adminToken}
                onClick={() => {
                  window.sessionStorage.removeItem("dw_admin_token");
                  setAdminToken("");
                }}
              >
                Clear token
              </Button>
            </div>
            {error ? <pre className="whitespace-pre-wrap rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</pre> : null}
          </CardContent>
        </Card>

        <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
          <div className="flex flex-col gap-3">
            {holds.length === 0 ? (
              <Card>
                <CardContent className="py-10 text-center text-sm text-slate-600">
                  {loading ? "Loading..." : "No held orders found."}
                </CardContent>
              </Card>
            ) : (
              holds.map((h) => {
                const orderId = asString(h.order_id);
                const risk = asString(h.risk_score);
                const decision = asString(h.risk_decision);
                const email = asString(h.customer_email);
                const heldAt = asString(h.held_at);
                const amount = asString(h.amount);
                const currency = asString(h.currency);
                const provider = asString(h.provider);
                const sku = asString(h.product_sku);
                const confirmRequested = asString(h.confirm_requested_at);
                const confirmConfirmed = asString(h.confirm_confirmed_at);
                const canResend = decision === "require_email_confirmation" && Boolean(email) && !Boolean(confirmConfirmed);

                return (
                  <Card key={orderId} className={orderId === selectedOrderId ? "ring-2 ring-amber-300" : ""}>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base">{orderId}</CardTitle>
                      <CardDescription>
                        {provider} • {amount} {currency} • {sku || "no_sku"} • held {heldAt || "?"}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-col gap-2">
                      <div className="text-sm text-slate-700">
                        Risk: <span className="font-semibold">{risk || "?"}</span> • Decision:{" "}
                        <span className="font-semibold">{decision || "?"}</span>
                      </div>
                      <div className="text-sm text-slate-700">Email: {email || "(none)"} </div>
                      <div className="text-xs text-slate-600">
                        Confirm requested: {confirmRequested || "(none)"} • confirmed: {confirmConfirmed || "(none)"}
                      </div>
                      <div className="flex flex-wrap gap-2 pt-1">
                        <Button size="sm" variant="outline" disabled={loading} onClick={() => getPacket(orderId)}>
                          Evidence packet
                        </Button>
                        <Button size="sm" variant="outline" disabled={loading || !canResend} onClick={() => resendConfirmation(orderId)}>
                          Resend confirm
                        </Button>
                        <Button size="sm" disabled={loading} onClick={() => release(orderId)}>
                          Release
                        </Button>
                        <Button size="sm" variant="destructive" disabled={loading} onClick={() => refund(orderId)}>
                          Refund
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })
            )}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Evidence Packet</CardTitle>
              <CardDescription>Generated JSON (saved server-side as an artifact too).</CardDescription>
            </CardHeader>
            <CardContent>
              {packetJson ? (
                <pre className="max-h-[70vh] overflow-auto whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-xs text-slate-800">
                  {packetJson}
                </pre>
              ) : (
                <div className="text-sm text-slate-600">Select “Evidence packet” on an order to view it here.</div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
