"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function ConfirmClient() {
  const params = useSearchParams();
  const [status, setStatus] = useState<"idle" | "working" | "done" | "error">("idle");
  const [message, setMessage] = useState<string>("Ready to confirm.");

  const token = (params.get("token") || "").trim();
  const orderId = (params.get("order_id") || "").trim();

  useEffect(() => {
    // Strip token from URL quickly to reduce exposure in screenshots/history/referrers.
    try {
      const url = new URL(window.location.href);
      url.searchParams.delete("token");
      window.history.replaceState({}, document.title, url.toString());
    } catch {
      // ignore
    }
  }, []);

  async function confirmNow() {
    if (!token) {
      setStatus("error");
      setMessage("Missing confirmation token.");
      return;
    }
    setStatus("working");
    setMessage("Confirming your order…");
    try {
      const resp = await fetch("/api/orders/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, order_id: orderId || undefined }),
        cache: "no-store",
      });
      const json = (await resp.json()) as Record<string, unknown>;
      if (!resp.ok) {
        throw new Error(typeof json.error === "string" ? json.error : `HTTP ${resp.status}`);
      }
      setStatus("done");
      setMessage("Confirmed. You can return to your purchase.");
    } catch (e) {
      setStatus("error");
      setMessage(e instanceof Error ? e.message : String(e));
    }
  }

  useEffect(() => {
    if (status !== "idle") return;
    void confirmNow();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-amber-50 text-slate-900">
      <main className="mx-auto flex max-w-xl flex-col gap-6 px-6 py-12">
        <Card>
          <CardHeader>
            <CardTitle>Confirm Order</CardTitle>
            <CardDescription>Finishing verification and releasing access.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <div className="text-sm text-slate-700">{message}</div>
            {status === "error" ? (
              <Button onClick={confirmNow} variant="outline">
                Try again
              </Button>
            ) : null}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

