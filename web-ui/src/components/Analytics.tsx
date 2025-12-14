"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import { track } from "@/lib/analytics/client";

function isExternalLink(href: string): boolean {
  try {
    const target = new URL(href, window.location.href);
    return target.origin !== window.location.origin;
  } catch {
    return false;
  }
}

export function Analytics() {
  const pathname = usePathname();
  const landingTracked = useRef(false);

  useEffect(() => {
    const pathWithQuery = `${window.location.pathname}${window.location.search}`;
    track("page_view", { path: pathWithQuery }, pathname);
    if (!landingTracked.current) {
      landingTracked.current = true;
      track("landing_view", { path: pathWithQuery }, pathname);
    }
  }, [pathname]);

  useEffect(() => {
    function onClick(ev: MouseEvent) {
      const target = ev.target as HTMLElement | null;
      if (!target) return;

      const ctaEl = target.closest("[data-dw-cta]") as HTMLElement | null;
      if (ctaEl?.dataset.dwCta) {
        track("cta_click", {
          cta_label: ctaEl.dataset.dwCta,
          message_type: ctaEl.dataset.dwMessage,
          placement: ctaEl.dataset.dwPlacement,
        });
      }

      const link = target.closest("a[href]") as HTMLAnchorElement | null;
      if (!link) return;
      if (!isExternalLink(link.href)) return;
      track("outbound_click", {
        url: link.href,
        text: (link.textContent || "").trim().slice(0, 140),
      });
    }

    document.addEventListener("click", onClick, { capture: true });
    return () => document.removeEventListener("click", onClick, { capture: true });
  }, []);

  return null;
}
