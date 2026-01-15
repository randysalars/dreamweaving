import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/natural-vs-induced/can-daily-life-trigger-altered-states`;

export const metadata: Metadata = {
  title: "Can daily life trigger altered states? | Salars Consciousness",
  description: "Yes, routine activities like driving, exercising, daydreaming, and sleep transitions naturally trigger mild altered states through changes in attention, br",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Can daily life trigger altered states?",
    description: "Yes, routine activities like driving, exercising, daydreaming, and sleep transitions naturally trigger mild altered states through changes in attention, br",
    url: pageUrl,
    type: "article",
  },
  keywords: ["highway hypnosis", "flow states", "daydreaming", "hypnagogic states", "runner's high", "default mode network", "microsleep", "automatic behavior"],
};

export default function CanDailyLifeTriggerAlteredStatesPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/natural-vs-induced"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Natural vs Induced Altered States
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Can daily life trigger altered states?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Yes, routine activities like driving, exercising, daydreaming, and sleep transitions naturally trigger mild altered states through changes in attention, brain chemistry, and neural patterns.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              These everyday altered states occur because repetitive activities reduce conscious attention while maintaining automatic functioning, allowing the brain to shift into different processing modes. Sleep-wake transitions alter neurotransmitter levels, while physical exertion releases endorphins and changes oxygen flow to the brain. Daydreaming and highway hypnosis demonstrate how the default mode network activates when focused attention decreases, resulting in time distortion and reduced environmental awareness.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The intensity varies significantly based on individual sensitivity, fatigue levels, and environmental factors. Some people experience more pronounced shifts during routine tasks, while others require more extreme conditions to notice altered awareness.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
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
              
              <Link
                href="/consciousness/altered-states/natural-vs-induced/what-are-induced-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are induced altered states?</span>
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
              href="/consciousness/altered-states/natural-vs-induced"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Natural vs Induced Altered States questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}