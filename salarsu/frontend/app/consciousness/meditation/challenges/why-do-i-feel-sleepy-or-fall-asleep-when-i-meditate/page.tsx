import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/meditation/challenges/why-do-i-feel-sleepy-or-fall-asleep-when-i-meditate`;

export const metadata: Metadata = {
  title: "Why do I feel sleepy or fall asleep when I meditate? | Salars Consciousness",
  description: "Meditation sleepiness occurs because relaxation activates the parasympathetic nervous system, which naturally promotes rest, especially when the body is al",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Why do I feel sleepy or fall asleep when I meditate?",
    description: "Meditation sleepiness occurs because relaxation activates the parasympathetic nervous system, which naturally promotes rest, especially when the body is al",
    url: pageUrl,
    type: "article",
  },
  keywords: ["parasympathetic nervous system", "alpha waves", "meditation posture", "sleep hygiene", "mindfulness fatigue", "relaxation response", "cortical activity", "meditative awareness"],
};

export default function WhyDoIFeelSleepyOrFallAsleepWhenIMeditatePage() {
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
            Why do I feel sleepy or fall asleep when I meditate?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Meditation sleepiness occurs because relaxation activates the parasympathetic nervous system, which naturally promotes rest, especially when the body is already fatigued.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The meditative state closely resembles the brain's preparation for sleep, with reduced cortical activity and increased alpha waves. This physiological similarity causes the nervous system to interpret meditation as a cue for sleep, particularly when practitioners are already tired or practicing in comfortable positions. The phenomenon demonstrates the powerful connection between relaxation techniques and the body's natural sleep mechanisms.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Sleepiness typically decreases with regular practice as the brain learns to distinguish between meditative awareness and sleep preparation. Alert postures and meditation during naturally wakeful hours reduce this tendency.
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
                href="/consciousness/meditation/challenges/how-do-i-handle-physical-discomfort-or-pain-while-meditating"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do I handle physical discomfort or pain while meditating?</span>
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