import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/speed-reading/key-techniques/regression-reduction`;

export const metadata: Metadata = {
  title: "Regression Reduction | Speed Reading",
  description:
    "Reduce regressions (unnecessary rereading) by using a guide, improving attention, and confirming meaning with quick summaries.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Regression Reduction",
    description:
      "Reduce regressions (unnecessary rereading) by using a guide, improving attention, and confirming meaning with quick summaries.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["regression", "rereading", "focus", "pointer", "comprehension"],
};

export default function RegressionReductionPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">
          <div className="space-y-2">
            <Link
              href="/consciousness/speed-reading/key-techniques"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Key Techniques
            </Link>
          </div>

          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Regression Reduction
          </h1>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Reduce regressions by keeping your eyes moving forward with a
              guide, setting a clear purpose for the text, and verifying
              comprehension with quick summaries. Most backtracking is caused by
              distraction or uncertainty—not true necessity.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              What Causes Backtracking
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Regressions usually happen when your attention drifts, when a
              sentence is ambiguous, or when you’re trying to read too fast for
              the material. The fix is to stabilize attention and pace—not to
              “force” your eyes not to move back.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              A Practical Routine
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">1) Preview first:</strong>{" "}
                Know the structure before you start.
              </p>
              <p>
                <strong className="text-foreground">2) Use a pointer:</strong>{" "}
                Track steadily under the line.
              </p>
              <p>
                <strong className="text-foreground">3) Pause at paragraphs:</strong>{" "}
                One-sentence summary; then continue.
              </p>
            </div>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Pages
            </h2>
            <div className="grid gap-3">
              <Link
                href="/consciousness/speed-reading/key-techniques/use-a-pointer-or-guide"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Use a Pointer or Guide</span>
              </Link>
              <Link
                href="/consciousness/speed-reading/key-techniques/previewing"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Previewing</span>
              </Link>
              <Link
                href="/consciousness/speed-reading/common-challenges-and-solutions"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Common Challenges and Solutions
                </span>
              </Link>
            </div>
          </section>

          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/speed-reading"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              Back to Speed Reading hub
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>
        </div>
      </main>
    </div>
  );
}

