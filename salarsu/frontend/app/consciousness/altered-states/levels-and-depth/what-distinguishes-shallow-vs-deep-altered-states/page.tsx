import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/levels-and-depth/what-distinguishes-shallow-vs-deep-altered-states`;

export const metadata: Metadata = {
  title: "What distinguishes shallow vs deep altered states? | Salars Consciousness",
  description: "Exploring what distinguishes shallow vs deep altered states - understanding consciousness and awareness.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "What distinguishes shallow vs deep altered states?",
    description: "Exploring what distinguishes shallow vs deep altered states - understanding consciousness and awareness.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["altered states", "consciousness", "awareness", "distinguishes", "shallow", "altered"],
};

export default function WhatDistinguishesShallowVsDeepAlteredStatesPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/levels-and-depth"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Levels, Depths & Intensity
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            What distinguishes shallow vs deep altered states?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              [Claude: Write a 20-35 word direct answer to: What distinguishes shallow vs deep altered states?]
            </p>
          </section>

          {/* Context Paragraph */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              [Claude: Explain in 2-4 sentences why what distinguishes shallow vs deep altered states matters and what mechanisms are involved]
            </p>
          </section>

          {/* Boundary Paragraph */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              [Claude: Add 1-3 sentences about when this changes or what limits exist]
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/levels-and-depth/are-there-levels-of-altered-states-of-consciousness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Are there levels of altered states of consciousness?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/levels-and-depth/can-altered-states-deepen-over-time"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states deepen over time?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/levels-and-depth/can-a-person-control-the-depth-of-an-altered-state"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can a person control the depth of an altered state?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/definitions-foundations/what-is-an-altered-state-of-consciousness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is an altered state of consciousness?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/definitions-foundations/what-defines-normal-waking-consciousness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What defines normal waking consciousness?</span>
              </Link>
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/altered-states/levels-and-depth"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Levels, Depths & Intensity questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}