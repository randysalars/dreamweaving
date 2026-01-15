import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/levels-and-depth/can-altered-states-fluctuate-in-intensity`;

export const metadata: Metadata = {
  title: "Can altered states fluctuate in intensity? | Salars Consciousness",
  description: "Altered states naturally fluctuate in intensity throughout their duration, shifting between deeper and lighter phases based on neurochemical changes, exter",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Can altered states fluctuate in intensity?",
    description: "Altered states naturally fluctuate in intensity throughout their duration, shifting between deeper and lighter phases based on neurochemical changes, exter",
    url: pageUrl,
    type: "article",
  },
  keywords: ["consciousness fluctuation", "neurochemical dynamics", "default mode network", "attention regulation", "psychedelic waves", "meditative depth", "brain state transitions", "awareness intensity"],
};

export default function CanAlteredStatesFluctuateInIntensityPage() {
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
            Can altered states fluctuate in intensity?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Altered states naturally fluctuate in intensity throughout their duration, shifting between deeper and lighter phases based on neurochemical changes, external stimuli, and individual physiological responses.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              These fluctuations occur because altered states depend on dynamic brain chemistry that responds to multiple variables simultaneously. Neurotransmitter levels rise and fall, attention shifts between internal and external awareness, and the brain's default mode network alternates between suppression and reactivation. This creates waves of intensity rather than static experiences, demonstrating that consciousness operates as a fluid system rather than fixed states.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Some pharmaceutical interventions can maintain more consistent intensity levels for specific durations. Experienced practitioners of meditation or breathwork may develop greater control over fluctuation patterns through trained attention regulation.
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
                href="/consciousness/altered-states/levels-and-depth/what-distinguishes-shallow-vs-deep-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What distinguishes shallow vs deep altered states?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/levels-and-depth/can-altered-states-deepen-over-time"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states deepen over time?</span>
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