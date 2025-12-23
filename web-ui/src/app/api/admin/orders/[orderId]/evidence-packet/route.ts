import { NextRequest, NextResponse } from "next/server";
import { generateEvidencePacket } from "@/lib/analytics/evidencePacket";

export const runtime = "nodejs";

function requireAdmin(request: NextRequest): string | null {
  const secret = process.env.DW_ADMIN_TOKEN;
  if (!secret) return "missing_admin_secret";
  const token = request.headers.get("x-dw-admin-token");
  if (!token || token !== secret) return "unauthorized";
  return null;
}

export async function GET(request: NextRequest, context: { params: Promise<{ orderId: string }> }) {
  const authError = requireAdmin(request);
  if (authError) return NextResponse.json({ ok: false, error: authError }, { status: 401 });

  const { orderId } = await context.params;
  if (!orderId) return NextResponse.json({ ok: false, error: "missing_order_id" }, { status: 400 });

  try {
    const packet = await generateEvidencePacket(orderId);
    return NextResponse.json({ ok: true, packet });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "error";
    const status = msg === "order_not_found" ? 404 : 500;
    return NextResponse.json({ ok: false, error: msg }, { status });
  }
}
