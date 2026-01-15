import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/subjective-experience/how-do-altered-states-feel-subjectively`;

export const metadata: Metadata = {
  title: "How do altered states feel subjectively? | Salars Consciousness",
  description: "Altered states create distinct subjective experiences including distorted time perception, enhanced sensory awareness, emotional intensity shifts, dissolut",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How do altered states feel subjectively?",
    description: "Altered states create distinct subjective experiences including distorted time perception, enhanced sensory awareness, emotional intensity shifts, dissolut",
    url: pageUrl,
    type: "article",
  },
  keywords: ["ego dissolution", "mystical experiences", "time distortion", "synesthesia", "depersonalization", "flow states", "psychedelic effects", "meditation states"],
};

export default function HowDoAlteredStatesFeelSubjectivelyPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/subjective-experience"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Subjective Experience & Perception Changes
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            How do altered states feel subjectively?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Altered states create distinct subjective experiences including distorted time perception, enhanced sensory awareness, emotional intensity shifts, dissolution of self-boundaries, and modified thought patterns.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              These subjective changes occur because altered states modify neural connectivity patterns and neurotransmitter activity in regions controlling perception, memory, and self-awareness. The brain's default mode network, which maintains normal self-referential thinking, becomes disrupted, leading to characteristic experiences like ego dissolution or mystical feelings. Understanding these subjective reports helps researchers map how consciousness emerges from specific neural mechanisms.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The intensity and specific qualities vary dramatically based on the method of induction, individual brain chemistry, psychological state, and environmental context. Some people experience minimal subjective changes while others report profound alterations from identical triggers.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/subjective-experience/do-altered-states-change-perception-of-time"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do altered states change perception of time?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/subjective-experience/do-altered-states-affect-sensory-clarity"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do altered states affect sensory clarity?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/subjective-experience/can-altered-states-increase-vividness-of-experience"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states increase vividness of experience?</span>
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
              href="/consciousness/altered-states/subjective-experience"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Subjective Experience & Perception Changes questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}