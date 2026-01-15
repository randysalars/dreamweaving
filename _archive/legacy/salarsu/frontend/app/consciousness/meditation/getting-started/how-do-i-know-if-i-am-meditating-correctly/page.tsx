import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/meditation/getting-started/how-do-i-know-if-i-am-meditating-correctly`;

export const metadata: Metadata = {
  title: "How do I know if I am meditating correctly? | Salars Consciousness",
  description: "Correct meditation involves sustained attention without forcing concentration, accompanied by moments of awareness when the mind wanders and gentle return ",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How do I know if I am meditating correctly?",
    description: "Correct meditation involves sustained attention without forcing concentration, accompanied by moments of awareness when the mind wanders and gentle return ",
    url: pageUrl,
    type: "article",
  },
  keywords: ["mindfulness", "metacognition", "attention training", "meditation techniques", "concentration practice", "awareness", "mental noting", "beginner meditation"],
};

export default function HowDoIKnowIfIAmMeditatingCorrectlyPage() {
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
            How do I know if I am meditating correctly?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Correct meditation involves sustained attention without forcing concentration, accompanied by moments of awareness when the mind wanders and gentle return to the meditation object.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The wandering mind is part of the process, not a failure, because noticing distraction and returning attention strengthens metacognitive awareness. This cycle of attention, distraction, and gentle redirection trains the brain's attention networks and develops mindfulness skills. The quality of awareness matters more than the duration of unbroken focus because meditation cultivates the capacity to observe mental states without judgment.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Different meditation styles have varying markers of correct practice - concentration-based methods emphasize sustained focus while mindfulness approaches welcome all experiences. Advanced practitioners may experience deeper states of absorption or effortless awareness that transcend the basic attention-distraction cycle.
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
                href="/consciousness/meditation/getting-started/how-long-should-i-meditate-each-day-when-starting-out"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How long should I meditate each day when starting out?</span>
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