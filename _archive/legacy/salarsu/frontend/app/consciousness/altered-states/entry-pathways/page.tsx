import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/entry-pathways`;

export const metadata: Metadata = {
  title: "Entry Pathways & Triggers | Altered States",
  description: "How altered states begin and the various triggers that induce them.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Entry Pathways & Triggers",
    description: "How altered states begin and the various triggers that induce them.",
    url: pageUrl,
    type: "website",
  },
};

export default function EntryPathwaysPage() {
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
              Entry Pathways & Triggers
            </h1>
            <p className="text-lg text-muted-foreground">
              How altered states begin and the various triggers that induce them.
            </p>
          </div>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Questions in this category
            </h2>
            <div className="grid gap-3">
              <Link
                href="/consciousness/altered-states/entry-pathways/how-do-altered-states-begin"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do altered states begin?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/entry-pathways/what-are-the-most-common-entry-pathways-into-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are the most common entry pathways into altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/entry-pathways/can-breathing-techniques-induce-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can breathing techniques induce altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/entry-pathways/can-movement-or-posture-trigger-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can movement or posture trigger altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/entry-pathways/can-sensory-deprivation-cause-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can sensory deprivation cause altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/entry-pathways/can-sensory-overload-cause-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can sensory overload cause altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/entry-pathways/can-intense-focus-create-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can intense focus create altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/entry-pathways/can-emotional-shock-trigger-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can emotional shock trigger altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/entry-pathways/can-pain-induce-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can pain induce altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/entry-pathways/can-pleasure-induce-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can pleasure induce altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/entry-pathways/can-fatigue-or-sleep-deprivation-induce-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can fatigue or sleep deprivation induce altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/entry-pathways/can-fasting-induce-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can fasting induce altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/entry-pathways/can-rhythmic-sound-or-music-induce-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can rhythmic sound or music induce altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/entry-pathways/can-chanting-or-mantra-induce-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can chanting or mantra induce altered states?</span>
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
