import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/misconceptions/are-altered-states-signs-of-enlightenment`;

export const metadata: Metadata = {
  title: "Are altered states signs of enlightenment? | Salars Consciousness",
  description: "Altered states are neurological phenomena that can occur through various means and do not inherently indicate enlightenment or spiritual advancement.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Are altered states signs of enlightenment?",
    description: "Altered states are neurological phenomena that can occur through various means and do not inherently indicate enlightenment or spiritual advancement.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["mystical experiences", "spiritual bypassing", "meditation states", "psychedelic experiences", "consciousness research", "contemplative practice", "peak experiences", "spiritual materialism"],
};

export default function AreAlteredStatesSignsOfEnlightenmentPage() {
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
            Are altered states signs of enlightenment?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Altered states are neurological phenomena that can occur through various means and do not inherently indicate enlightenment or spiritual advancement.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Altered states result from changes in brain chemistry and neural activity that can be induced by meditation, psychedelics, sensory deprivation, or sleep deprivation. These neurobiological changes affect perception, cognition, and self-awareness but represent temporary shifts in consciousness rather than permanent spiritual development. The confusion arises because many contemplative traditions involve altered states as part of practice, leading people to conflate the experience with the outcome.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Some altered states may facilitate insights or psychological breakthroughs that contribute to personal growth. However, the subjective intensity or unusualness of an experience does not correlate with spiritual progress or wisdom development.
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