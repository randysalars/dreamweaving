import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/meditation/getting-started/how-long-should-i-meditate-each-day-when-starting-out`;

export const metadata: Metadata = {
  title: "How long should I meditate each day when starting out? | Salars Consciousness",
  description: "Beginning meditators typically start with 5-10 minutes daily. This duration allows initial habit formation without creating resistance or overwhelming the ",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How long should I meditate each day when starting out?",
    description: "Beginning meditators typically start with 5-10 minutes daily. This duration allows initial habit formation without creating resistance or overwhelming the ",
    url: pageUrl,
    type: "article",
  },
  keywords: ["beginner meditation", "meditation duration", "attention span training", "mindfulness practice length", "meditation habit formation", "concentration building", "daily meditation routine", "meditation consistency"],
};

export default function HowLongShouldIMeditateEachDayWhenStartingOutPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/meditation/getting-started"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Getting Started with Meditation
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            How long should I meditate each day when starting out?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Beginning meditators typically start with 5-10 minutes daily. This duration allows initial habit formation without creating resistance or overwhelming the untrained attention span.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Short initial sessions work because the mind's capacity for sustained attention develops gradually, similar to physical conditioning. Starting with manageable durations leads to consistent practice, which results in neuroplasticity changes that strengthen attention networks. Excessive initial duration often creates aversion because untrained minds experience discomfort when forced to maintain focus beyond their current capacity.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Duration can extend to 15-20 minutes after several weeks of consistent practice. Some individuals with prior focus training or natural concentration ability may start with longer sessions without developing resistance.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/meditation/getting-started/what-is-meditation-and-how-does-it-work"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is meditation and how does it work?</span>
              </Link>
              
              <Link
                href="/consciousness/meditation/getting-started/how-do-i-start-a-meditation-practice-as-a-complete-beginner"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do I start a meditation practice as a complete beginner?</span>
              </Link>
              
              <Link
                href="/consciousness/meditation/getting-started/do-i-need-special-equipment-or-training-to-meditate"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do I need special equipment or training to meditate?</span>
              </Link>
              
              <Link
                href="/consciousness/meditation/techniques/what-is-breath-awareness-meditation-and-how-do-i-practice-it"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is breath awareness meditation and how do I practice it?</span>
              </Link>
              
              <Link
                href="/consciousness/meditation/techniques/what-is-mindfulness-meditation"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is mindfulness meditation?</span>
              </Link>
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/meditation/getting-started"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Getting Started with Meditation questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}