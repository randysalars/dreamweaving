import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/meditation/challenges/is-it-normal-to-feel-worse-after-meditation`;

export const metadata: Metadata = {
  title: "Is it normal to feel worse after meditation? | Salars Consciousness",
  description: "Yes, feeling worse after meditation is common, especially for beginners. This occurs because meditation increases awareness of suppressed emotions, physica",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Is it normal to feel worse after meditation?",
    description: "Yes, feeling worse after meditation is common, especially for beginners. This occurs because meditation increases awareness of suppressed emotions, physica",
    url: pageUrl,
    type: "article",
  },
  keywords: ["meditation side effects", "emotional release", "mindfulness discomfort", "beginner meditation", "increased awareness", "suppressed emotions", "meditation adjustment period", "sitting meditation difficulties"],
};

export default function IsItNormalToFeelWorseAfterMeditationPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/meditation/challenges"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Common Challenges
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Is it normal to feel worse after meditation?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Yes, feeling worse after meditation is common, especially for beginners. This occurs because meditation increases awareness of suppressed emotions, physical tension, and mental patterns that were previously ignored.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Meditation removes the usual mental distractions that mask underlying psychological and physical states, making practitioners suddenly aware of anxiety, sadness, or bodily discomfort they hadn't noticed. This heightened awareness can initially feel overwhelming because the mind interprets increased sensitivity as distress. Additionally, sitting still and focusing attention can trigger the release of stored emotional content or highlight racing thoughts that feel more intense when observed directly.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              These difficult experiences typically decrease as practitioners develop greater tolerance for uncomfortable sensations and emotions. Most people report improvements after several weeks of consistent practice, though the timeline varies significantly based on individual sensitivity and life circumstances.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/meditation/challenges/how-do-i-deal-with-a-busy-or-wandering-mind-during-meditation"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do I deal with a busy or wandering mind during meditation?</span>
              </Link>
              
              <Link
                href="/consciousness/meditation/challenges/what-should-i-do-if-i-feel-restless-or-fidgety-during-meditation"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What should I do if I feel restless or fidgety during meditation?</span>
              </Link>
              
              <Link
                href="/consciousness/meditation/challenges/why-do-i-feel-sleepy-or-fall-asleep-when-i-meditate"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Why do I feel sleepy or fall asleep when I meditate?</span>
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
              href="/consciousness/meditation/challenges"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Common Challenges questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}