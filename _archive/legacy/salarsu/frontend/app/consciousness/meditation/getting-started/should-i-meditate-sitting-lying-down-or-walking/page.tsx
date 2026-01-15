import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/meditation/getting-started/should-i-meditate-sitting-lying-down-or-walking`;

export const metadata: Metadata = {
  title: "Should I meditate sitting, lying down, or walking? | Salars Consciousness",
  description: "Sitting meditation offers the most stable foundation for developing concentration and awareness. Walking meditation cultivates mindfulness in motion, while",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Should I meditate sitting, lying down, or walking?",
    description: "Sitting meditation offers the most stable foundation for developing concentration and awareness. Walking meditation cultivates mindfulness in motion, while",
    url: pageUrl,
    type: "article",
  },
  keywords: ["posture", "mindfulness meditation", "walking meditation", "body scan", "concentration practice", "alertness", "spinal alignment", "sitting position"],
};

export default function ShouldIMeditateSittingLyingDownOrWalkingPage() {
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
            Should I meditate sitting, lying down, or walking?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Sitting meditation offers the most stable foundation for developing concentration and awareness. Walking meditation cultivates mindfulness in motion, while lying down increases drowsiness risk.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Posture directly affects alertness and attention stability because spinal alignment influences nervous system arousal. Sitting upright maintains optimal balance between relaxation and vigilance, allowing sustained focus without excessive effort. Walking meditation integrates awareness with physical movement, demonstrating how mindfulness translates to daily activities. Lying down triggers the body's rest response, which can lead to sleep rather than meditative awareness.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Physical limitations or chronic pain may require modified positions or lying meditation. Advanced practitioners can maintain clear awareness in any posture. Different meditation types suit different positions - body scans work well lying down, while concentration practices benefit from sitting.
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