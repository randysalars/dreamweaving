import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/memory/modern-approaches/which-memory-apps-are-most-effective-anki-quizlet-etc`;

export const metadata: Metadata = {
  title: "Which memory apps are most effective (Anki, Quizlet, etc.)? | Salars Consciousness",
  description: "Which memory apps are most effective (Anki, Quizlet, etc.)?",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Which memory apps are most effective (Anki, Quizlet, etc.)?",
    description: "Which memory apps are most effective (Anki, Quizlet, etc.)?",
    url: pageUrl,
    type: "article",
  },
  keywords: ["consciousness", "awareness", "perception"],
};

export default function WhichMemoryAppsAreMostEffectiveAnkiQuizletEtcPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/memory/modern-approaches"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Modern Memory Approaches
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Which memory apps are most effective (Anki, Quizlet, etc.)?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              [Claude: Write 20-35 word answer to "Which memory apps are most effective (Anki, Quizlet, etc.)?"]
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              [Claude: Write 2-4 sentences explaining WHY this matters, using causal language (because, results in, leads to). Be specific about mechanisms and broader implications.]
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              [Claude: Write 1-3 sentences addressing when this CHANGES, what the limits are, or what exceptions exist. Add nuance without contradicting the short answer.]
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/memory/modern-approaches/what-is-spaced-repetition-and-why-does-it-work"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is spaced repetition and why does it work?</span>
              </Link>
              
              <Link
                href="/consciousness/memory/modern-approaches/how-does-the-leitner-system-improve-memorization"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How does the Leitner system improve memorization?</span>
              </Link>
              
              <Link
                href="/consciousness/memory/modern-approaches/what-is-active-recall-and-how-is-it-different-from-re-reading"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is active recall and how is it different from re-reading?</span>
              </Link>
              
              <Link
                href="/consciousness/memory/fundamentals/what-are-the-different-types-of-memory-short-term-long-term-working"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are the different types of memory (short-term, long-term, working)?</span>
              </Link>
              
              <Link
                href="/consciousness/memory/fundamentals/how-does-the-brain-encode-and-retrieve-memories"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How does the brain encode and retrieve memories?</span>
              </Link>
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/memory/modern-approaches"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Modern Memory Approaches questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}