import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/misconceptions/can-altered-states-be-faked-or-imagined`;

export const metadata: Metadata = {
  title: "Can altered states be faked or imagined? | Salars Consciousness",
  description: "Altered states involve measurable physiological changes in brain activity, heart rate, and hormone levels that cannot be consciously faked, though subjecti",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Can altered states be faked or imagined?",
    description: "Altered states involve measurable physiological changes in brain activity, heart rate, and hormone levels that cannot be consciously faked, though subjecti",
    url: pageUrl,
    type: "article",
  },
  keywords: ["neuroimaging", "brainwave patterns", "physiological markers", "neurotransmitter systems", "autonomic responses", "placebo effects", "suggestibility", "expectation bias"],
};

export default function CanAlteredStatesBeFakedOrImaginedPage() {
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
            Can altered states be faked or imagined?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Altered states involve measurable physiological changes in brain activity, heart rate, and hormone levels that cannot be consciously faked, though subjective experiences can be exaggerated.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Neuroimaging studies demonstrate distinct brainwave patterns and neural network changes during genuine altered states that differ markedly from baseline consciousness. These physiological markers occur because altered states involve specific neurotransmitter systems and brain regions that produce observable biological signatures. The autonomic nervous system responses during deep meditative or psychedelic states result in measurable changes that voluntary imagination alone cannot replicate.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Mild altered states or brief experiences may be more easily simulated through acting or self-suggestion. Individual differences in suggestibility and expectation can blur the line between genuine and imagined experiences in some cases.
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