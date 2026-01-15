import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/duration-aftereffects/can-altered-states-affect-memory-afterward`;

export const metadata: Metadata = {
  title: "Can altered states affect memory afterward? | Salars Consciousness",
  description: "Altered states frequently disrupt memory formation and retrieval, creating gaps in episodic memory, distorted recollections, or enhanced recall of specific",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Can altered states affect memory afterward?",
    description: "Altered states frequently disrupt memory formation and retrieval, creating gaps in episodic memory, distorted recollections, or enhanced recall of specific",
    url: pageUrl,
    type: "article",
  },
  keywords: ["memory consolidation", "hippocampus function", "blackout episodes", "state-dependent learning", "retrograde amnesia", "psychedelic memory", "dissociative amnesia", "flashback memories"],
};

export default function CanAlteredStatesAffectMemoryAfterwardPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/duration-aftereffects"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Duration & Aftereffects
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Can altered states affect memory afterward?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Altered states frequently disrupt memory formation and retrieval, creating gaps in episodic memory, distorted recollections, or enhanced recall of specific experiences.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Memory disruption occurs because altered states modify neurotransmitter activity in the hippocampus and prefrontal cortex, regions critical for memory consolidation. Different states affect memory through distinct mechanisms - alcohol blocks encoding pathways, psychedelics alter temporal perception and narrative construction, while meditative states can enhance certain types of memory formation. These effects demonstrate how consciousness and memory systems are deeply interconnected.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Memory effects vary dramatically by substance, dosage, and individual brain chemistry. Some altered states like certain meditation practices or mild psychedelic experiences can actually improve memory consolidation and recall.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/duration-aftereffects/how-long-do-altered-states-typically-last"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How long do altered states typically last?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/duration-aftereffects/can-altered-states-end-suddenly"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states end suddenly?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/duration-aftereffects/can-altered-states-fade-gradually"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states fade gradually?</span>
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
              href="/consciousness/altered-states/duration-aftereffects"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Duration & Aftereffects questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}