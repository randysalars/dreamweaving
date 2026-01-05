import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/meditation/benefits-science/how-does-meditation-change-the-brain`;

export const metadata: Metadata = {
  title: "How does meditation change the brain? | Salars Consciousness",
  description: "Meditation increases gray matter density in attention and emotional regulation areas while reducing activity in the default mode network associated with mi",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How does meditation change the brain?",
    description: "Meditation increases gray matter density in attention and emotional regulation areas while reducing activity in the default mode network associated with mi",
    url: pageUrl,
    type: "article",
  },
  keywords: ["neuroplasticity", "default mode network", "gray matter", "prefrontal cortex", "hippocampus", "mindfulness-based stress reduction", "attention regulation", "brain imaging"],
};

export default function HowDoesMeditationChangeTheBrainPage() {
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
            How does meditation change the brain?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Meditation increases gray matter density in attention and emotional regulation areas while reducing activity in the default mode network associated with mind-wandering.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Regular meditation practice triggers neuroplasticity, the brain's ability to reorganize and form new neural connections. This results in structural changes in regions like the prefrontal cortex, which governs executive function, and the hippocampus, which supports memory formation. The decreased activity in the default mode network leads to reduced rumination and self-referential thinking patterns that contribute to anxiety and depression.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Measurable brain changes typically emerge after 8 weeks of consistent practice, though some functional changes appear within days. The magnitude of change correlates with practice frequency and duration, with experienced meditators showing more pronounced structural differences.
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
                href="/consciousness/meditation/benefits-science/can-meditation-help-with-stress-and-anxiety"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can meditation help with stress and anxiety?</span>
              </Link>
              
              <Link
                href="/consciousness/meditation/benefits-science/does-meditation-improve-focus-and-concentration"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Does meditation improve focus and concentration?</span>
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