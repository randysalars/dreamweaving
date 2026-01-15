import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/meditation/benefits-science/can-meditation-boost-creativity`;

export const metadata: Metadata = {
  title: "Can meditation boost creativity? | Salars Consciousness",
  description: "Meditation enhances creativity by increasing divergent thinking, reducing cognitive rigidity, and strengthening connections between brain networks involved",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Can meditation boost creativity?",
    description: "Meditation enhances creativity by increasing divergent thinking, reducing cognitive rigidity, and strengthening connections between brain networks involved",
    url: pageUrl,
    type: "article",
  },
  keywords: ["divergent thinking", "cognitive flexibility", "default mode network", "insight meditation", "creative problem solving", "neural plasticity", "mindfulness creativity", "open monitoring meditation"],
};

export default function CanMeditationBoostCreativityPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/meditation/benefits-science"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Benefits & Science of Meditation
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Can meditation boost creativity?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Meditation enhances creativity by increasing divergent thinking, reducing cognitive rigidity, and strengthening connections between brain networks involved in insight and novel idea generation.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Regular meditation practice activates the default mode network while simultaneously engaging focused attention networks, creating optimal conditions for creative insights. This dual activation allows the mind to make novel connections between previously unrelated concepts because it reduces the brain's tendency to follow habitual thought patterns. Studies demonstrate that meditators show increased activity in brain regions associated with cognitive flexibility and original thinking, particularly in areas that integrate information across different neural networks.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The creativity boost depends on meditation type, with open monitoring practices showing stronger effects than focused attention techniques. Benefits typically emerge after 4-8 weeks of consistent practice, though individual responses vary significantly based on baseline creativity levels and meditation experience.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/meditation/benefits-science/what-does-scientific-research-say-about-meditation-benefits"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What does scientific research say about meditation benefits?</span>
              </Link>
              
              <Link
                href="/consciousness/meditation/benefits-science/how-does-meditation-change-the-brain"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How does meditation change the brain?</span>
              </Link>
              
              <Link
                href="/consciousness/meditation/benefits-science/can-meditation-help-with-stress-and-anxiety"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can meditation help with stress and anxiety?</span>
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
              href="/consciousness/meditation/benefits-science"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Benefits & Science of Meditation questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}