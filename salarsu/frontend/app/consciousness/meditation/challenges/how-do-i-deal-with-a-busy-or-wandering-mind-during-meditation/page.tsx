import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/meditation/challenges/how-do-i-deal-with-a-busy-or-wandering-mind-during-meditation`;

export const metadata: Metadata = {
  title: "How do I deal with a busy or wandering mind during meditation? | Salars Consciousness",
  description: "A wandering mind during meditation is normal brain activity. Gently redirect attention back to the chosen focus point when distractions arise without judgm",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How do I deal with a busy or wandering mind during meditation?",
    description: "A wandering mind during meditation is normal brain activity. Gently redirect attention back to the chosen focus point when distractions arise without judgm",
    url: pageUrl,
    type: "article",
  },
  keywords: ["default mode network", "attention regulation", "mindfulness", "concentration", "mental noting", "meditation object", "executive control", "intrusive thoughts"],
};

export default function HowDoIDealWithABusyOrWanderingMindDuringMeditationPage() {
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
            How do I deal with a busy or wandering mind during meditation?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              A wandering mind during meditation is normal brain activity. Gently redirect attention back to the chosen focus point when distractions arise without judgment.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The default mode network in the brain generates spontaneous thoughts, memories, and mental chatter even during focused attention tasks. This neural activity results from the mind's natural tendency to make associations and process information. Noticing when attention drifts and returning focus to the meditation object strengthens attention regulation pathways because it exercises the brain's executive control networks.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Mind wandering typically decreases with consistent practice as attention stability improves. Some meditation traditions deliberately work with thoughts rather than redirecting attention, and certain states of deep concentration can temporarily reduce mental chatter.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
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