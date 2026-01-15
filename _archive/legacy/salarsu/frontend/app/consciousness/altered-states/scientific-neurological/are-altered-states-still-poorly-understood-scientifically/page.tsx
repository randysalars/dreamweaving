import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/scientific-neurological/are-altered-states-still-poorly-understood-scientifically`;

export const metadata: Metadata = {
  title: "Are altered states still poorly understood scientifically? | Salars Consciousness",
  description: "Yes, altered states of consciousness remain poorly understood scientifically despite advances in neuroimaging and neuropharmacology research over recent de",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Are altered states still poorly understood scientifically?",
    description: "Yes, altered states of consciousness remain poorly understood scientifically despite advances in neuroimaging and neuropharmacology research over recent de",
    url: pageUrl,
    type: "article",
  },
  keywords: ["consciousness research", "neuroimaging", "psychedelic studies", "meditation research", "brain wave patterns", "subjective experience", "neuropharmacology", "phenomenology"],
};

export default function AreAlteredStatesStillPoorlyUnderstoodScientificallyPage() {
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
            Are altered states still poorly understood scientifically?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Yes, altered states of consciousness remain poorly understood scientifically despite significant advances in neuroimaging and neuropharmacology research over recent decades.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The subjective nature of consciousness makes altered states difficult to measure objectively, because researchers must rely on self-reports and indirect neural markers rather than direct observation. Current neuroimaging techniques can identify brain activity patterns associated with different altered states, but these correlations don't fully explain the mechanisms that generate subjective experiences. This gap between neural activity and phenomenological experience represents one of the fundamental challenges in consciousness research, leading to ongoing debates about how brain states translate into specific conscious experiences.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Some aspects of altered states show more scientific clarity than others, particularly the neurochemical mechanisms underlying drug-induced states and the brain wave patterns during meditation or sleep stages. Research progress varies significantly depending on the specific altered state and available measurement technologies.
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