import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/scientific-neurological/do-altered-states-increase-neural-plasticity`;

export const metadata: Metadata = {
  title: "Do altered states increase neural plasticity? | Salars Consciousness",
  description: "Research indicates altered states of consciousness can enhance neural plasticity by promoting neurogenesis, increasing BDNF levels, and facilitating new sy",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Do altered states increase neural plasticity?",
    description: "Research indicates altered states of consciousness can enhance neural plasticity by promoting neurogenesis, increasing BDNF levels, and facilitating new sy",
    url: pageUrl,
    type: "article",
  },
  keywords: ["neuroplasticity", "BDNF", "default mode network", "neurogenesis", "synaptic plasticity", "meditation research", "psychedelic neuroscience", "brain connectivity"],
};

export default function DoAlteredStatesIncreaseNeuralPlasticityPage() {
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
            Do altered states increase neural plasticity?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Research indicates altered states of consciousness can enhance neural plasticity by promoting neurogenesis, increasing BDNF levels, and facilitating new synaptic connections.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Altered states appear to reduce activity in the default mode network while increasing neurotropic factors like BDNF (brain-derived neurotrophic factor), which supports the growth of new neurons and synapses. This neurochemical environment facilitates learning and memory consolidation because it creates optimal conditions for neural rewiring. Studies of meditation, psychedelics, and sensory deprivation demonstrate measurable increases in dendritic branching and synaptic density following these experiences.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The plasticity enhancement varies significantly based on the type, duration, and intensity of the altered state. Some states may temporarily reduce plasticity during the acute phase while increasing it during recovery periods.
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