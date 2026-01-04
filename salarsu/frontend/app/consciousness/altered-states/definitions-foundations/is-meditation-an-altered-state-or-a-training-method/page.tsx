import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/definitions-foundations/is-meditation-an-altered-state-or-a-training-method`;

export const metadata: Metadata = {
  title: "Is meditation an altered state or a training method? | Salars Consciousness",
  description: "Meditation is both a training method that develops attentional skills and a practice that can produce altered states during sessions, with long-term practitioners experiencing trait-level consciousness changes.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Is meditation an altered state or a training method?",
    description: "Meditation is both a training method that develops attentional skills and a practice that can produce altered states during sessions, with long-term practitioners experiencing trait-level consciousness changes.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["meditation", "altered states", "training", "mindfulness", "consciousness", "practice"],
};

export default function IsMeditationAnAlteredStateOrATrainingMethodPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/definitions-foundations"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Core Definitions & Foundations
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Is meditation an altered state or a training method?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Meditation is both a training method that develops attentional control and metacognitive awareness, and a practice that produces altered states during sessions, with long-term practitioners experiencing lasting trait-level changes in baseline consciousness.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Understanding meditation as dual-purpose matters because it clarifies confusion around whether meditation is the goal or the path. As a training method, meditation strengthens executive attention, emotional regulation, and self-awareness through neuroplastic changes in prefrontal regions and the default mode network. During practice sessions, meditation can induce temporary altered states (deep calm, expanded awareness, dissolution of self-boundaries) that resemble other altered states. Over years of practice, these temporary states can lead to permanent trait shifts, resulting in a fundamentally different baseline consciousness even when not actively meditating.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The distinction blurs in advanced stages where the "training" and the "state" become inseparable—practitioners report continuous meditative awareness even during daily activities. Similarly, some traditions emphasize meditation purely as a tool for insight development rather than state cultivation, while others (like jhana practices) explicitly aim to induce progressively deeper altered states. Beginners may experience minimal state changes during early practice, making meditation feel more like skill-building than consciousness alteration.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
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
              
              <Link
                href="/consciousness/altered-states/definitions-foundations/how-do-altered-states-differ-from-everyday-awareness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do altered states differ from everyday awareness?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/natural-vs-induced/what-are-natural-altered-states-of-consciousness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are natural altered states of consciousness?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/natural-vs-induced/what-causes-natural-altered-states-to-occur"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What causes natural altered states to occur?</span>
              </Link>
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/altered-states/definitions-foundations"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Core Definitions & Foundations questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}