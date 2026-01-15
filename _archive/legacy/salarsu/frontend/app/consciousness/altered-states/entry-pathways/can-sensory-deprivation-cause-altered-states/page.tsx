import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/entry-pathways/can-sensory-deprivation-cause-altered-states`;

export const metadata: Metadata = {
  title: "Can sensory deprivation cause altered states? | Salars Consciousness",
  description: "Sensory deprivation reliably triggers altered states by disrupting normal neural input patterns, leading to hallucinations, time distortion, and profound c",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Can sensory deprivation cause altered states?",
    description: "Sensory deprivation reliably triggers altered states by disrupting normal neural input patterns, leading to hallucinations, time distortion, and profound c",
    url: pageUrl,
    type: "article",
  },
  keywords: ["float tanks", "isolation chambers", "perceptual distortion", "hallucinations", "consciousness research", "neural plasticity", "meditation states", "sensory gating"],
};

export default function CanSensoryDeprivationCauseAlteredStatesPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/entry-pathways"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Entry Pathways & Triggers
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Can sensory deprivation cause altered states?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Sensory deprivation reliably triggers altered states by disrupting normal neural input patterns, leading to hallucinations, time distortion, and profound changes in consciousness within hours.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              When the brain receives minimal external stimuli, it compensates by amplifying internal neural activity and generating its own perceptual experiences. This process demonstrates how consciousness depends on the constant interplay between sensory input and neural processing. The phenomenon reveals that our normal waking state requires continuous sensory feedback to maintain stable perception and self-awareness.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Individual sensitivity varies significantly—some people experience effects within 15 minutes while others require several hours. Pre-existing mental health conditions, expectations, and environmental factors influence both the intensity and type of altered states that emerge.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
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
              href="/consciousness/altered-states/entry-pathways"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Entry Pathways & Triggers questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}