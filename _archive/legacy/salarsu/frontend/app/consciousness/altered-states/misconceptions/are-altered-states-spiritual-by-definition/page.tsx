import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/misconceptions/are-altered-states-spiritual-by-definition`;

export const metadata: Metadata = {
  title: "Are altered states spiritual by definition? | Salars Consciousness",
  description: "No, altered states are neurobiological phenomena that can occur through various means including meditation, psychedelics, sleep deprivation, or medical con",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Are altered states spiritual by definition?",
    description: "No, altered states are neurobiological phenomena that can occur through various means including meditation, psychedelics, sleep deprivation, or medical con",
    url: pageUrl,
    type: "article",
  },
  keywords: ["mystical experiences", "psychedelic research", "meditation states", "consciousness research", "neurobiology", "set and setting", "phenomenology", "religious experiences"],
};

export default function AreAlteredStatesSpiritualByDefinitionPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/misconceptions"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Misconceptions & Clarifications
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Are altered states spiritual by definition?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              No, altered states are neurobiological phenomena that can occur through various means including meditation, psychedelics, sleep deprivation, or medical conditions, regardless of spiritual context or interpretation.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Altered states result from measurable changes in brain activity, neurotransmitter levels, and neural connectivity patterns. These neurobiological shifts occur because the brain's normal filtering and processing mechanisms become disrupted or modified, leading to altered perception, cognition, and awareness. The spiritual interpretation represents one cultural framework among many for understanding these universal human experiences.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Individual interpretation varies significantly based on cultural background, personal beliefs, and the specific context in which the altered state occurs. Some people experience identical neurobiological changes but interpret them through secular, psychological, or scientific frameworks rather than spiritual ones.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/misconceptions/are-altered-states-hallucinations"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Are altered states hallucinations?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/misconceptions/do-altered-states-mean-losing-control"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do altered states mean losing control?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/misconceptions/are-altered-states-escapism"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Are altered states escapism?</span>
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
              href="/consciousness/altered-states/misconceptions"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Misconceptions & Clarifications questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}