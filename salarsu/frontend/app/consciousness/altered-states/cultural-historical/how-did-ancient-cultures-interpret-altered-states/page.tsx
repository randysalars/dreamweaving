import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/cultural-historical/how-did-ancient-cultures-interpret-altered-states`;

export const metadata: Metadata = {
  title: "How did ancient cultures interpret altered states? | Salars Consciousness",
  description: "Ancient cultures typically interpreted altered states as spiritual communications, divine possession, shamanic journeys, or contact with ancestral realms r",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How did ancient cultures interpret altered states?",
    description: "Ancient cultures typically interpreted altered states as spiritual communications, divine possession, shamanic journeys, or contact with ancestral realms r",
    url: pageUrl,
    type: "article",
  },
  keywords: ["shamanism", "divine possession", "mystical experiences", "religious ceremonies", "ancestral communication", "traditional healing", "spiritual visions", "sacred rituals"],
};

export default function HowDidAncientCulturesInterpretAlteredStatesPage() {
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
            How did ancient cultures interpret altered states?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Ancient cultures typically interpreted altered states as spiritual communications, divine possession, shamanic journeys, or contact with ancestral realms rather than neurological phenomena.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              These interpretations developed because altered states often produced vivid visions, mystical experiences, and profound psychological insights that seemed to transcend ordinary reality. Ancient societies lacked modern neuroscience frameworks, so they explained these phenomena through their existing religious and cosmological worldviews. This led to the integration of altered states into healing practices, religious ceremonies, and social governance because they were viewed as accessing sacred knowledge or divine guidance.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Interpretations varied significantly across cultures - some emphasized healing and divination while others focused on warrior initiation or artistic inspiration. The advent of scientific materialism in recent centuries shifted dominant interpretations toward psychological and neurochemical explanations, though traditional spiritual frameworks persist in many cultures.
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
                href="/consciousness/altered-states/cultural-historical/were-altered-states-used-in-ritual-or-initiation"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Were altered states used in ritual or initiation?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/cultural-historical/how-do-spiritual-traditions-describe-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do spiritual traditions describe altered states?</span>
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