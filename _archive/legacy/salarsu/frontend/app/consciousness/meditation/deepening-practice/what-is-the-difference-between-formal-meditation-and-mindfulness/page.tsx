import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/meditation/deepening-practice/what-is-the-difference-between-formal-meditation-and-mindfulness`;

export const metadata: Metadata = {
  title: "What is the difference between formal meditation and mindfulness? | Salars Consciousness",
  description: "Formal meditation involves structured practice sessions with specific techniques, while mindfulness refers to maintaining present-moment awareness througho",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "What is the difference between formal meditation and mindfulness?",
    description: "Formal meditation involves structured practice sessions with specific techniques, while mindfulness refers to maintaining present-moment awareness througho",
    url: pageUrl,
    type: "article",
  },
  keywords: ["contemplative practice", "mindful awareness", "sitting meditation", "informal practice", "present moment", "attention training", "daily mindfulness", "meditative states"],
};

export default function WhatIsTheDifferenceBetweenFormalMeditationAndMindfulnessPage() {
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
            What is the difference between formal meditation and mindfulness?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Formal meditation involves structured practice sessions with specific techniques, while mindfulness refers to maintaining present-moment awareness throughout daily activities.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Formal meditation creates concentrated training periods that strengthen attention and awareness skills through deliberate practice. This focused approach results in measurable changes in brain structure and function because sustained attention activates specific neural networks. Mindfulness represents the application of these cultivated skills in real-world contexts, leading to integration of meditative awareness into ordinary experience.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The distinction blurs when formal sessions become very brief or when daily activities become highly structured contemplative practices. Some traditions emphasize one approach over the other, and advanced practitioners often experience continuous awareness that dissolves the formal/informal boundary.
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