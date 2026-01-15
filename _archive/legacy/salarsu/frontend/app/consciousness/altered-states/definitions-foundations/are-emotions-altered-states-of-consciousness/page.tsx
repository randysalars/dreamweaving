import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/definitions-foundations/are-emotions-altered-states-of-consciousness`;

export const metadata: Metadata = {
  title: "Are emotions altered states of consciousness? | Salars Consciousness",
  description: "Intense emotions can temporarily alter consciousness through neurochemical shifts and attentional narrowing, but they differ from classical altered states in duration and controllability.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Are emotions altered states of consciousness?",
    description: "Intense emotions can temporarily alter consciousness through neurochemical shifts and attentional narrowing, but they differ from classical altered states in duration and controllability.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["altered states", "emotions", "consciousness", "affect", "neurochemistry", "arousal"],
};

export default function AreEmotionsAlteredStatesOfConsciousnessPage() {
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
            Are emotions altered states of consciousness?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Intense emotions can temporarily alter consciousness through neurochemical shifts, attentional narrowing, and physiological arousal, but they differ from classical altered states in duration, depth of perceptual change, and degree of controllability.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Understanding emotions as consciousness-altering phenomena matters because it reveals how everyday affective experiences operate through similar neurobiological mechanisms as recognized altered states. Peak emotional moments trigger dopamine, norepinephrine, and cortisol cascades that reshape attention, memory encoding, and decision-making, resulting in temporary shifts away from baseline awareness. This recognition helps distinguish between transient emotional states (anger, fear, ecstasy) and sustained altered states (meditation, hypnosis), where the depth and duration of perceptual transformation differ significantly. Emotions demonstrate that consciousness exists on a spectrum rather than in discrete categories.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The classification becomes less clear during extreme emotional experiences like mystical awe, overwhelming grief, or euphoric joy, where consciousness shifts can approach the depth of psychedelic or meditative states. Chronic emotional conditions like anxiety disorders or mania represent sustained alterations rather than temporary shifts. Conversely, mild emotions (contentment, mild irritation) create minimal consciousness change and wouldn't qualify as altered states despite involving similar neural pathways at lower intensity.
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
                href="/consciousness/altered-states/definitions-foundations/what-defines-normal-waking-consciousness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What defines normal waking consciousness?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/definitions-foundations/how-do-altered-states-differ-from-everyday-awareness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do altered states differ from everyday awareness?</span>
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