import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/scientific-neurological/how-do-psychologists-classify-altered-states`;

export const metadata: Metadata = {
  title: "How do psychologists classify altered states? | Salars Consciousness",
  description: "Psychologists classify altered states using dimensional approaches that measure consciousness along continuums of awareness, attention, self-control, and s",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How do psychologists classify altered states?",
    description: "Psychologists classify altered states using dimensional approaches that measure consciousness along continuums of awareness, attention, self-control, and s",
    url: pageUrl,
    type: "article",
  },
  keywords: ["consciousness spectrum", "awareness levels", "attention states", "sensory processing", "cognitive control", "neural networks", "state induction methods", "phenomenological classification"],
};

export default function HowDoPsychologistsClassifyAlteredStatesPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/scientific-neurological"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Scientific & Neurological Models
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            How do psychologists classify altered states?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Psychologists classify altered states using dimensional approaches that measure consciousness along continuums of awareness, attention, self-control, and sensory processing rather than discrete categories.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              This classification system emerges because consciousness exists on multiple spectrums rather than binary states, allowing researchers to map how different factors like drugs, meditation, or sleep deprivation affect specific cognitive functions. Dimensional models enable more precise measurement of consciousness changes and help identify which neural networks become enhanced or suppressed during different experiences. This approach demonstrates that altered states involve predictable patterns of brain activity that can be studied systematically.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Some researchers still use categorical systems that group states by their induction method (pharmacological, physiological, psychological) or by their primary characteristics. The classification becomes more complex when multiple factors interact, such as combining sensory deprivation with psychoactive substances.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/scientific-neurological/what-happens-in-the-brain-during-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What happens in the brain during altered states?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/scientific-neurological/are-altered-states-linked-to-brainwave-changes"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Are altered states linked to brainwave changes?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/scientific-neurological/do-altered-states-involve-neurotransmitter-shifts"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do altered states involve neurotransmitter shifts?</span>
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
              href="/consciousness/altered-states/scientific-neurological"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Scientific & Neurological Models questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}