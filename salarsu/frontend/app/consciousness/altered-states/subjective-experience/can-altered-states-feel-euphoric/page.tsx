import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/subjective-experience/can-altered-states-feel-euphoric`;

export const metadata: Metadata = {
  title: "Can altered states feel euphoric? | Salars Consciousness",
  description: "Many altered states produce intense euphoria through changes in neurotransmitter activity, particularly dopamine and endorphin release in reward pathways.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Can altered states feel euphoric?",
    description: "Many altered states produce intense euphoria through changes in neurotransmitter activity, particularly dopamine and endorphin release in reward pathways.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["euphoria", "dopamine release", "reward pathways", "mystical experiences", "neurotransmitters", "bliss states", "psychedelic effects", "endorphins"],
};

export default function CanAlteredStatesFeelEuphoricPage() {
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
            Can altered states feel euphoric?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Many altered states produce intense euphoria through changes in neurotransmitter activity, particularly dopamine and endorphin release in reward pathways.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Euphoric altered states occur because psychoactive substances, meditation, or other triggers stimulate the brain's reward circuitry, flooding areas like the ventral tegmental area and nucleus accumbens with dopamine. This neurochemical cascade creates feelings of bliss, unity, and transcendence that characterize many mystical and drug-induced experiences. The intensity of euphoria often correlates with the degree of normal consciousness disruption, demonstrating how altered brain chemistry directly translates to transformed subjective experience.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Not all altered states produce euphoria - some generate anxiety, confusion, or dysphoria depending on the trigger, individual brain chemistry, and environmental context. Euphoric intensity varies widely across different induction methods and individual responses.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/subjective-experience/how-do-altered-states-feel-subjectively"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do altered states feel subjectively?</span>
              </Link>
              
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