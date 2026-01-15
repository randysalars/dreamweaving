import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/scientific-neurological/are-altered-states-studied-in-neuroscience`;

export const metadata: Metadata = {
  title: "Are altered states studied in neuroscience? | Salars Consciousness",
  description: "Yes, neuroscience extensively studies altered states using neuroimaging, EEG, and other technologies to map brain changes during meditation, psychedelic ex",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Are altered states studied in neuroscience?",
    description: "Yes, neuroscience extensively studies altered states using neuroimaging, EEG, and other technologies to map brain changes during meditation, psychedelic ex",
    url: pageUrl,
    type: "article",
  },
  keywords: ["neuroimaging", "psychedelic research", "meditation neuroscience", "anesthesia consciousness", "sleep states", "neural correlates", "brain connectivity", "consciousness research"],
};

export default function AreAlteredStatesStudiedInNeurosciencePage() {
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
            Are altered states studied in neuroscience?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Yes, neuroscience extensively studies altered states using neuroimaging, EEG, and other technologies to map brain changes during meditation, psychedelic experiences, anesthesia, and sleep states.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Altered states reveal how consciousness can be modified through changes in neural networks, neurotransmitter systems, and brain connectivity patterns. This research demonstrates that normal waking consciousness represents just one configuration of brain activity, while other states show distinct neural signatures. These findings help scientists understand the neural basis of subjective experience and how different brain states produce varying levels of awareness, perception, and self-reflection.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Research quality varies significantly depending on the altered state being studied and available technology. Some states like REM sleep and anesthesia are well-mapped neurologically, while others like mystical experiences or certain drug states remain more challenging to study systematically.
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