import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/duration-aftereffects`;

export const metadata: Metadata = {
  title: "Duration & Aftereffects | Altered States",
  description: "How long altered states last and their lingering effects.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Duration & Aftereffects",
    description: "How long altered states last and their lingering effects.",
    url: pageUrl,
    type: "website",
  },
};

export default function DurationAftereffectsPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-4xl space-y-8">
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Altered States
            </Link>
          </div>

          <div className="space-y-3">
            <h1 className="text-4xl font-semibold tracking-tight text-foreground">
              Duration & Aftereffects
            </h1>
            <p className="text-lg text-muted-foreground">
              How long altered states last and their lingering effects.
            </p>
          </div>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Questions in this category
            </h2>
            <div className="grid gap-3">
              <Link
                href="/consciousness/altered-states/duration-aftereffects/how-long-do-altered-states-typically-last"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How long do altered states typically last?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/duration-aftereffects/can-altered-states-end-suddenly"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states end suddenly?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/duration-aftereffects/can-altered-states-fade-gradually"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states fade gradually?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/duration-aftereffects/do-altered-states-leave-lingering-effects"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do altered states leave lingering effects?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/duration-aftereffects/can-altered-states-change-mood-afterward"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states change mood afterward?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/duration-aftereffects/can-altered-states-affect-memory-afterward"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states affect memory afterward?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/duration-aftereffects/can-altered-states-alter-perception-days-later"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states alter perception days later?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/duration-aftereffects/do-repeated-altered-states-accumulate-effects"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do repeated altered states accumulate effects?</span>
              </Link>
            </div>
          </section>

          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/altered-states"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Altered States categories
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>
        </div>
      </main>
    </div>
  );
}
