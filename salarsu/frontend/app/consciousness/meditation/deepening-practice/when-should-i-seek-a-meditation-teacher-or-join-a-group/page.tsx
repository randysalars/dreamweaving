import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/meditation/deepening-practice/when-should-i-seek-a-meditation-teacher-or-join-a-group`;

export const metadata: Metadata = {
  title: "When should I seek a meditation teacher or join a group? | Salars Consciousness",
  description: "Seek guidance when experiencing persistent obstacles, lacking progress after 6+ months of regular practice, or needing accountability for consistent medita",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "When should I seek a meditation teacher or join a group?",
    description: "Seek guidance when experiencing persistent obstacles, lacking progress after 6+ months of regular practice, or needing accountability for consistent medita",
    url: pageUrl,
    type: "article",
  },
  keywords: ["meditation teacher", "sangha", "meditation group", "dharma teacher", "meditation obstacles", "meditation accountability", "spiritual mentor", "practice guidance"],
};

export default function WhenShouldISeekAMeditationTeacherOrJoinAGroupPage() {
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
            When should I seek a meditation teacher or join a group?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Seek guidance when experiencing persistent obstacles, lacking progress after 6+ months of regular practice, or needing accountability for consistent meditation.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Teachers provide personalized instruction that addresses specific difficulties because meditation challenges vary significantly between individuals. Group practice creates social accountability and shared learning experiences that help maintain consistency, while experienced instructors can identify subtle errors in technique that self-guided practitioners often miss. This guidance prevents the development of unhelpful habits and accelerates skill development through targeted feedback.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Advanced practitioners may benefit from periodic teacher consultation rather than ongoing instruction. Some meditation styles require minimal guidance, while others like Zen or Vipassana traditionally emphasize teacher-student relationships.
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