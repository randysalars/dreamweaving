import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/definitions-foundations/what-defines-normal-waking-consciousness`;

export const metadata: Metadata = {
  title: "What defines normal waking consciousness? | Salars Consciousness",
  description: "Normal waking consciousness features stable awareness, logical thinking, sensory processing tied to external stimuli, linear time perception, and maintaine",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "What defines normal waking consciousness?",
    description: "Normal waking consciousness features stable awareness, logical thinking, sensory processing tied to external stimuli, linear time perception, and maintaine",
    url: pageUrl,
    type: "article",
  },
  keywords: ["default mode network", "thalamic regulation", "executive functions", "altered states of consciousness", "baseline consciousness", "awareness levels", "cognitive coherence", "reality testing"],
};

export default function WhatDefinesNormalWakingConsciousnessPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/definitions-foundations"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Core Definitions & Foundations
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            What defines normal waking consciousness?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Normal waking consciousness features stable awareness, logical thinking, sensory processing tied to external stimuli, linear time perception, and maintained sense of self-identity.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              This baseline state results from coordinated brain network activity, particularly between the default mode network and executive control systems. The thalamus acts as a relay station filtering sensory information, while the prefrontal cortex maintains executive functions and self-awareness. These mechanisms create the stable, reality-oriented experience that serves as the reference point for identifying altered states.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              This baseline shifts during sleep, meditation, psychoactive substance use, extreme stress, or neurological conditions. The boundaries become less distinct during drowsiness, daydreaming, or flow states where some normal characteristics remain while others fade.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/definitions-foundations/what-is-an-altered-state-of-consciousness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is an altered state of consciousness?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/definitions-foundations/how-do-altered-states-differ-from-everyday-awareness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do altered states differ from everyday awareness?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/definitions-foundations/are-altered-states-always-intentional"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Are altered states always intentional?</span>
              </Link>
              
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
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/altered-states/definitions-foundations"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Core Definitions & Foundations questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}