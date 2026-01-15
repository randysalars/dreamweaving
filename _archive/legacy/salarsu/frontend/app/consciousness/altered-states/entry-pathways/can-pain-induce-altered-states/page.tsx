import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/entry-pathways/can-pain-induce-altered-states`;

export const metadata: Metadata = {
  title: "Can pain induce altered states? | Salars Consciousness",
  description: "Pain can trigger altered states through neurochemical responses, sensory overload, and dissociative mechanisms that shift normal consciousness patterns.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Can pain induce altered states?",
    description: "Pain can trigger altered states through neurochemical responses, sensory overload, and dissociative mechanisms that shift normal consciousness patterns.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["endorphins", "dissociation", "pain tolerance", "sensory overload", "stress response", "endogenous opioids", "trauma consciousness", "nociception"],
};

export default function CanPainInduceAlteredStatesPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/entry-pathways"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Entry Pathways & Triggers
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Can pain induce altered states?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Pain can trigger altered states of consciousness through neurochemical responses, sensory overload, and dissociative mechanisms that shift normal awareness patterns.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Intense pain activates the body's endogenous opioid system, releasing endorphins and other neurochemicals that alter perception and awareness. Pain also overwhelms sensory processing capacity, which can lead to dissociation as a protective mechanism. These physiological responses demonstrate how extreme physical stress naturally modifies consciousness to help organisms cope with trauma.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The intensity and duration of pain determine the depth of altered states, with chronic pain sometimes dulling these responses. Individual pain tolerance and psychological factors significantly influence whether pain leads to transcendent experiences or purely negative states.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/entry-pathways/how-do-altered-states-begin"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do altered states begin?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/entry-pathways/what-are-the-most-common-entry-pathways-into-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are the most common entry pathways into altered states?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/entry-pathways/can-breathing-techniques-induce-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can breathing techniques induce altered states?</span>
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
              href="/consciousness/altered-states/entry-pathways"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Entry Pathways & Triggers questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}