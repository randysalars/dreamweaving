import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/sleep-dreams/dream-work/how-do-i-work-with-nightmares-therapeutically`;

export const metadata: Metadata = {
  title: "How do I work with nightmares therapeutically? | Salars Consciousness",
  description: "How do I work with nightmares therapeutically?",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How do I work with nightmares therapeutically?",
    description: "How do I work with nightmares therapeutically?",
    url: pageUrl,
    type: "article",
  },
  keywords: ["consciousness", "awareness", "perception"],
};

export default function HowDoIWorkWithNightmaresTherapeuticallyPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/sleep-dreams/dream-work"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dream Work & Interpretation
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            How do I work with nightmares therapeutically?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Use calming grounding after waking, then work with the nightmare when you’re safe and alert. A common approach is imagery rehearsal: rewrite the ending in a less threatening way and practice it daily to retrain the brain’s threat script.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Nightmares matter because they activate threat circuits and result in sleep avoidance, which leads to worse sleep and more nightmares—a reinforcing loop. Therapeutic work aims to change the brain’s prediction that “danger is inevitable,” so repeated rehearsal results in reduced intensity and frequency. This can improve both sleep quality and daytime anxiety.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              If nightmares are linked to trauma, severe anxiety, or PTSD symptoms, working with a qualified clinician is often safer and more effective than going it alone. Substance withdrawal, fever, and some medications can also spike nightmares, so addressing root causes may be necessary.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/sleep-dreams/dream-work/how-do-i-interpret-my-dreams"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do I interpret my dreams?</span>
              </Link>
              
              <Link
                href="/consciousness/sleep-dreams/dream-work/what-is-dream-journaling-and-how-do-i-start"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is dream journaling and how do I start?</span>
              </Link>
              
              <Link
                href="/consciousness/sleep-dreams/dream-work/do-recurring-dreams-mean-something"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do recurring dreams mean something?</span>
              </Link>
              
              <Link
                href="/consciousness/sleep-dreams/sleep-fundamentals/what-are-the-stages-of-sleep-and-what-happens-in-each"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are the stages of sleep and what happens in each?</span>
              </Link>
              
              <Link
                href="/consciousness/sleep-dreams/sleep-fundamentals/why-do-we-need-sleep"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Why do we need sleep?</span>
              </Link>
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/sleep-dreams/dream-work"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Dream Work & Interpretation questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}
