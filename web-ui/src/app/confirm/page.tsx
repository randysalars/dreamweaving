import { Suspense } from "react";
import ConfirmClient from "./ConfirmClient";

export const runtime = "nodejs";

export default function ConfirmPage() {
  return (
    <Suspense fallback={<div className="p-6 text-sm text-slate-600">Loading…</div>}>
      <ConfirmClient />
    </Suspense>
  );
}

