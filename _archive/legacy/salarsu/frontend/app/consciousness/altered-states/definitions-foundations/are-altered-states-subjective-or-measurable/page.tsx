import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/definitions-foundations/are-altered-states-subjective-or-measurable`;

export const metadata: Metadata = {
  title: "Are altered states subjective or measurable? | Salars Consciousness",
  description: "Altered states are both subjective experiences and measurable phenomena, with brain imaging, EEG, and physiological markers providing objective correlates of reported consciousness changes.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Are altered states subjective or measurable?",
    description: "Altered states are both subjective experiences and measurable phenomena, with brain imaging, EEG, and physiological markers providing objective correlates of reported consciousness changes.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["altered states", "measurement", "subjective experience", "neuroscience", "EEG", "brain imaging"],
};

export default function AreAlteredStatesSubjectiveOrMeasurablePage() {
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
            Are altered states subjective or measurable?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Altered states are both subjective experiences and measurable phenomena, with brain imaging, EEG patterns, heart rate variability, and biochemical markers providing objective correlates of reported consciousness changes.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Understanding this duality matters because it bridges the gap between first-person experience and third-person science. Subjectively, altered states involve qualitative shifts in how awareness feels—time may slow, colors intensify, or self-boundaries dissolve. These subjective reports can be correlated with objective measurements: theta brainwaves during deep meditation, reduced default mode network activity during psychedelic states, or elevated cortisol during acute stress states. This correlation doesn't reduce the experience to brain activity but demonstrates that consciousness changes leave measurable signatures, allowing researchers to study states that were once considered purely mystical or unmeasurable.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The correlation weakens for subtle states where physiological changes are minimal or for unique experiences that don't map onto existing measurement frameworks. Two people can show identical EEG signatures yet report vastly different subjective experiences, demonstrating that objective measures capture correlates but not the full phenomenology of consciousness.
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