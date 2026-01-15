import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/navigational/which-altered-states-occur-most-commonly`;

export const metadata: Metadata = {
  title: "Which altered states occur most commonly? | Salars Consciousness",
  description: "Sleep states, meditation, daydreaming, and flow states occur most commonly, with sleep representing the most frequent altered state that all humans experie",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Which altered states occur most commonly?",
    description: "Sleep states, meditation, daydreaming, and flow states occur most commonly, with sleep representing the most frequent altered state that all humans experie",
    url: pageUrl,
    type: "article",
  },
  keywords: ["sleep cycles", "meditation states", "flow experience", "daydreaming", "default mode network", "circadian rhythms", "consciousness spectrum", "attention regulation"],
};

export default function WhichAlteredStatesOccurMostCommonlyPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/navigational"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Navigational & Exploratory Prompts
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Which altered states occur most commonly?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Sleep states, meditation, daydreaming, and flow states occur most commonly, with sleep representing the most frequent altered state that all humans experience daily.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              These states emerge because the brain naturally cycles through different modes of consciousness based on circadian rhythms, attention patterns, and neural network activity. Sleep occurs due to adenosine buildup and circadian clock regulation, while meditative and flow states result from focused attention that shifts default mode network activity. These common altered states demonstrate that consciousness operates on a spectrum rather than as a fixed baseline condition.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Frequency varies significantly across individuals and cultures, with some people experiencing meditation or flow states regularly while others encounter them rarely. Certain conditions like insomnia, ADHD, or depression can alter the natural occurrence patterns of these states.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/navigational/which-altered-states-are-easiest-to-access"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Which altered states are easiest to access?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/navigational/which-altered-states-are-hardest-to-describe"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Which altered states are hardest to describe?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/navigational/which-altered-states-change-identity-perception"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Which altered states change identity perception?</span>
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
              href="/consciousness/altered-states/navigational"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Navigational & Exploratory Prompts questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}