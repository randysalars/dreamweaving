import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/cultural-historical/how-do-indigenous-traditions-approach-altered-states`;

export const metadata: Metadata = {
  title: "How do indigenous traditions approach altered states? | Salars Consciousness",
  description: "Indigenous traditions typically view altered states as sacred pathways to spiritual realms, ancestral communication, and healing, integrated into ceremonia",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How do indigenous traditions approach altered states?",
    description: "Indigenous traditions typically view altered states as sacred pathways to spiritual realms, ancestral communication, and healing, integrated into ceremonia",
    url: pageUrl,
    type: "article",
  },
  keywords: ["shamanism", "plant medicine", "ritual healing", "ancestral communication", "sacred ceremonies", "traditional knowledge", "spiritual realms", "community healing"],
};

export default function HowDoIndigenousTraditionsApproachAlteredStatesPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/cultural-historical"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Cultural & Historical Perspectives
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            How do indigenous traditions approach altered states?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Indigenous traditions typically view altered states as sacred pathways to spiritual realms, ancestral communication, and healing, integrated into ceremonial practices rather than isolated experiences.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              These approaches demonstrate how altered states function as structured cultural technologies because they're embedded within specific rituals, community guidance, and cosmological frameworks. Indigenous practices show that set and setting extend beyond individual psychology to include generational knowledge transmission, where altered states serve as bridges between ordinary reality and spiritual dimensions. This integration results in altered states being viewed as functional tools for community healing, divination, and maintaining cultural continuity rather than recreational or purely therapeutic activities.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Practices vary significantly across different indigenous cultures, from Amazonian ayahuasca ceremonies to Native American sweat lodges to Australian Aboriginal dreamtime practices. The degree of community involvement, specific substances or techniques used, and underlying spiritual beliefs create distinct approaches even when the fundamental reverence for altered states remains consistent.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/cultural-historical/how-have-altered-states-been-viewed-historically"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How have altered states been viewed historically?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/cultural-historical/how-did-ancient-cultures-interpret-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How did ancient cultures interpret altered states?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/cultural-historical/were-altered-states-used-in-ritual-or-initiation"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Were altered states used in ritual or initiation?</span>
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
              href="/consciousness/altered-states/cultural-historical"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Cultural & Historical Perspectives questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}