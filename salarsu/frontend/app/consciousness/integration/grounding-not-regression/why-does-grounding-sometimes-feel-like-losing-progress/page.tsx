import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/integration/grounding-not-regression/why-does-grounding-sometimes-feel-like-losing-progress`;

export const metadata: Metadata = {
  title: "Why does grounding sometimes feel like losing progress? | Salars Consciousness",
  description: "Grounding temporarily reduces access to expanded states and insights, creating the sensation of losing spiritual or psychological progress despite building",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Why does grounding sometimes feel like losing progress?",
    description: "Grounding temporarily reduces access to expanded states and insights, creating the sensation of losing spiritual or psychological progress despite building",
    url: pageUrl,
    type: "article",
  },
  keywords: ["integration paradox", "spiritual bypassing", "embodiment resistance", "nervous system regulation", "consciousness compression", "foundational stability", "expansion contraction cycle", "somatic integration"],
};

export default function WhyDoesGroundingSometimesFeelLikeLosingProgressPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/integration/grounding-not-regression"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Why Grounding Is Not Regression
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Why does grounding sometimes feel like losing progress?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Grounding temporarily reduces access to expanded states and insights, creating the sensation of losing spiritual or psychological progress despite building foundational stability.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              This occurs because grounding shifts attention from expanded consciousness states to basic embodied awareness, which feels restrictive after accessing higher perspectives. The brain interprets this narrowing of awareness as regression because it contrasts sharply with the expansive feelings of spiritual or psychological breakthroughs. This temporary compression actually consolidates gains by integrating insights into everyday functioning, though the process feels like moving backward.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The regression feeling diminishes as the nervous system adapts to holding both grounded presence and expanded awareness simultaneously. Those with trauma histories may experience more intense temporary regression as grounding initially activates stored survival responses.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/integration/grounding-not-regression/is-grounding-the-same-as-going-backwards-in-consciousness-development"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Is grounding the same as going backwards in consciousness development?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/grounding-not-regression/whats-the-difference-between-healthy-grounding-and-spiritual-bypassing"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What's the difference between healthy grounding and spiritual bypassing?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/grounding-not-regression/can-you-be-both-grounded-and-spiritually-aware-at-the-same-time"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can you be both grounded and spiritually aware at the same time?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/integration-matters/why-does-integration-matter-more-than-insight-in-consciousness-work"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Why does integration matter more than insight in consciousness work?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/integration-matters/what-is-the-difference-between-having-an-insight-and-integrating-it"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is the difference between having an insight and integrating it?</span>
              </Link>
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/integration/grounding-not-regression"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Why Grounding Is Not Regression questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}