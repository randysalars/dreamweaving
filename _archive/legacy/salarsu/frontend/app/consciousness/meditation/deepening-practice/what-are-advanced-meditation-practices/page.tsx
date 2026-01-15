import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/meditation/deepening-practice/what-are-advanced-meditation-practices`;

export const metadata: Metadata = {
  title: "What are advanced meditation practices? | Salars Consciousness",
  description: "Advanced meditation practices include concentration techniques like jhanas, insight methods examining mental formations, and awareness practices that disso",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "What are advanced meditation practices?",
    description: "Advanced meditation practices include concentration techniques like jhanas, insight methods examining mental formations, and awareness practices that disso",
    url: pageUrl,
    type: "article",
  },
  keywords: ["jhanas", "vipassana", "zen koan practice", "mahamudra", "dzogchen", "contemplative inquiry", "non-dual awareness", "samadhi states"],
};

export default function WhatAreAdvancedMeditationPracticesPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/meditation/deepening-practice"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Deepening Your Practice
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            What are advanced meditation practices?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Advanced meditation practices include concentration techniques like jhanas, insight methods examining mental formations, and awareness practices that dissolve subject-object boundaries through sustained attention training.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              These practices build upon foundational mindfulness because they require stable attention as a prerequisite for deeper states. Concentration practices like jhanas produce altered states of consciousness through progressive mental absorption, while insight techniques lead to direct perception of mental processes and their impermanent nature. The dissolution of ordinary self-other distinctions in awareness practices results from sustained observation of consciousness itself rather than its contents.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              These techniques become accessible after developing consistent daily practice for months or years, as they require attentional stability that beginners typically lack. The specific progression varies significantly between contemplative traditions, with some emphasizing concentration first while others integrate insight and awareness simultaneously.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/meditation/deepening-practice/how-do-i-progress-from-beginner-to-intermediate-meditation"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do I progress from beginner to intermediate meditation?</span>
              </Link>
              
              <Link
                href="/consciousness/meditation/deepening-practice/what-are-different-meditation-states-concentration-vs-insight"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are different meditation states (concentration vs insight)?</span>
              </Link>
              
              <Link
                href="/consciousness/meditation/deepening-practice/how-do-i-build-consistency-in-my-meditation-practice"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do I build consistency in my meditation practice?</span>
              </Link>
              
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
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/meditation/deepening-practice"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Deepening Your Practice questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}