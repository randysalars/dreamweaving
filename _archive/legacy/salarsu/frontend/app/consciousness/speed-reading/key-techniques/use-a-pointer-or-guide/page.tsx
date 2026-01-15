import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/speed-reading/key-techniques/use-a-pointer-or-guide`;

export const metadata: Metadata = {
  title: "Use a Pointer or Guide | Speed Reading",
  description:
    "Use a finger, pen, or cursor as a reading guide to maintain pace, reduce regressions, and improve focus.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Use a Pointer or Guide",
    description:
      "Use a finger, pen, or cursor as a reading guide to maintain pace, reduce regressions, and improve focus.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["pointer", "reading guide", "regression reduction", "focus", "WPM"],
};

export default function UseAPointerOrGuidePage() {
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
            Use a Pointer or Guide
          </h1>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              A pointer (finger, pen, or cursor) gives your eyes a stable target
              to follow. It reduces mind-wandering and backtracking, keeps your
              pace consistent, and makes it easier to read in chunks.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              How to Use It Well
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">1) Smooth motion:</strong>{" "}
                Move the pointer steadily—no tapping or jumping.
              </p>
              <p>
                <strong className="text-foreground">2) Slightly under text:</strong>{" "}
                Track just under the line so you don’t block words.
              </p>
              <p>
                <strong className="text-foreground">3) Calibrate pace:</strong>{" "}
                Start at a comfortable speed, then increase by 5–10% once you
                can summarize reliably.
              </p>
            </div>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Common Mistake
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Using a pointer as a “metronome” that forces you faster than your
              comprehension can handle. Your pointer should guide attention, not
              bully the pace. If comprehension drops, slow down until summaries
              return.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Pages
            </h2>
            <div className="grid gap-3">
              <Link
                href="/consciousness/speed-reading/key-techniques/regression-reduction"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Regression Reduction</span>
              </Link>
              <Link
                href="/consciousness/speed-reading/key-techniques/minimize-subvocalization"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Minimize Subvocalization
                </span>
              </Link>
              <Link
                href="/consciousness/speed-reading/practical-example"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Practical Example</span>
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

