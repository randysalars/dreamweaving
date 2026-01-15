import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/levels-and-depth/are-extreme-altered-states-rare`;

export const metadata: Metadata = {
  title: "Are extreme altered states rare? | Salars Consciousness",
  description: "Extreme altered states occur infrequently in most populations, though prevalence varies significantly based on cultural context, intentional practices, and",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Are extreme altered states rare?",
    description: "Extreme altered states occur infrequently in most populations, though prevalence varies significantly based on cultural context, intentional practices, and",
    url: pageUrl,
    type: "article",
  },
  keywords: ["mystical experiences", "psychedelic states", "dissociative episodes", "transcendent consciousness", "peak experiences", "non-ordinary states", "consciousness disruption", "neuroplasticity"],
};

export default function AreExtremeAlteredStatesRarePage() {
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
            Are extreme altered states rare?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Extreme altered states occur infrequently in most populations, though prevalence varies significantly based on cultural context, intentional practices, and individual neurological factors.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Extreme altered states require substantial neurochemical disruption or intense psychological conditions that don't arise during normal daily functioning. These states typically result from specific triggers like high-dose psychedelics, prolonged meditation, severe trauma, or certain medical conditions because they involve dramatic shifts in brain network connectivity and neurotransmitter activity. Their rarity demonstrates the brain's tendency toward homeostatic regulation and the significant energy required to maintain such dramatically altered patterns of consciousness.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Frequency increases substantially in populations with specific mental health conditions, dedicated spiritual practitioners, or those in cultures with ritualistic use of consciousness-altering substances. Individual neurological sensitivity and genetic factors also create significant variation in both susceptibility and intensity thresholds.
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