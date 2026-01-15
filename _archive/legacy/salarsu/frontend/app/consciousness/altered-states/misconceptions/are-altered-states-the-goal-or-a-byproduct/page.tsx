import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/misconceptions/are-altered-states-the-goal-or-a-byproduct`;

export const metadata: Metadata = {
  title: "Are altered states the goal or a byproduct? | Salars Consciousness",
  description: "Altered states can be either goal or byproduct depending on context. In therapeutic and spiritual practices, they're often intentional targets. In other si",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Are altered states the goal or a byproduct?",
    description: "Altered states can be either goal or byproduct depending on context. In therapeutic and spiritual practices, they're often intentional targets. In other si",
    url: pageUrl,
    type: "article",
  },
  keywords: ["intentional induction", "spontaneous states", "therapeutic outcomes", "spiritual bypassing", "state-dependent learning", "consciousness exploration", "mystical experiences", "psychedelic integration"],
};

export default function AreAlteredStatesTheGoalOrAByproductPage() {
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
            Are altered states the goal or a byproduct?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Altered states can be either goal or byproduct depending on context. In therapeutic and spiritual practices, they're often intentional targets. In other situations, they emerge as unintended consequences.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              This distinction matters because it determines how altered states are approached, measured, and integrated. When altered states are the goal, practitioners develop specific techniques and frameworks to achieve and navigate them safely. When they're byproducts, they may catch people unprepared, leading to confusion or distress. Understanding the intent behind altered state induction helps predict outcomes and guides appropriate preparation or response strategies.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The boundary shifts based on individual awareness and training. Experienced meditators may initially seek altered states as goals but eventually view them as natural byproducts of deeper practice. Clinical contexts typically frame altered states as therapeutic tools rather than end goals.
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