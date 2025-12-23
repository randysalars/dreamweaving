import { NextRequest, NextResponse } from "next/server";
import { verifyRecaptchaV3 } from "@/lib/analytics/recaptcha";

export const runtime = "nodejs";

type Body = {
  token?: string;
  action?: string;
};

function firstHeaderIp(request: NextRequest): string | null {
  const xff = request.headers.get("x-forwarded-for");
  if (xff) return xff.split(",")[0]?.trim() || null;
  const realIp = request.headers.get("x-real-ip");
  return realIp?.trim() || null;
}

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ ok: false, error: "invalid_json" }, { status: 400 });
  }

  const data = body as Body;
  const token = typeof data.token === "string" ? data.token.trim() : "";
  if (!token) return NextResponse.json({ ok: false, error: "missing_token" }, { status: 400 });

  const action = typeof data.action === "string" && data.action.trim() ? data.action.trim().slice(0, 80) : null;
  const ip = firstHeaderIp(request);

  try {
    const result = await verifyRecaptchaV3({ token, expectedAction: action, remoteip: ip });
    return NextResponse.json(result);
  } catch (e) {
    return NextResponse.json(
      { ok: false, error: e instanceof Error ? e.message : "recaptcha_error" },
      { status: 500 }
    );
  }
}

