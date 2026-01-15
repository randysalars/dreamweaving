import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/natural-vs-induced`;

export const metadata: Metadata = {
  title: "Natural vs Induced Altered States | Altered States",
  description: "Understanding naturally occurring versus deliberately induced altered states.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Natural vs Induced Altered States",
    description: "Understanding naturally occurring versus deliberately induced altered states.",
    url: pageUrl,
    type: "website",
  },
};

export default function NaturalVsInducedPage() {
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
              Natural vs Induced Altered States
            </h1>
            <p className="text-lg text-muted-foreground">
              Understanding naturally occurring versus deliberately induced altered states.
            </p>
          </div>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Questions in this category
            </h2>
            <div className="grid gap-3">
              <Link
                href="/consciousness/altered-states/natural-vs-induced/what-are-natural-altered-states-of-consciousness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are natural altered states of consciousness?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/natural-vs-induced/what-causes-natural-altered-states-to-occur"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What causes natural altered states to occur?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/natural-vs-induced/what-are-induced-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are induced altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/natural-vs-induced/how-are-altered-states-intentionally-induced"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How are altered states intentionally induced?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/natural-vs-induced/are-natural-altered-states-safer-than-induced-ones"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Are natural altered states safer than induced ones?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/natural-vs-induced/can-daily-life-trigger-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can daily life trigger altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/natural-vs-induced/are-altered-states-common-in-childhood"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Are altered states common in childhood?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/natural-vs-induced/do-altered-states-occur-during-illness-or-fever"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do altered states occur during illness or fever?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/natural-vs-induced/can-stress-induce-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can stress induce altered states?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/natural-vs-induced/are-altered-states-part-of-normal-human-functioning"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Are altered states part of normal human functioning?</span>
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
