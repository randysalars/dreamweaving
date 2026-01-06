import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/speed-reading/key-techniques/expand-peripheral-vision`;

export const metadata: Metadata = {
  title: "Expand Peripheral Vision | Speed Reading",
  description:
    "Train your eyes to take in groups of words per fixation instead of reading one word at a time.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Expand Peripheral Vision",
    description:
      "Train your eyes to take in groups of words per fixation instead of reading one word at a time.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "peripheral vision",
    "visual span",
    "eye fixations",
    "speed reading",
    "chunking",
  ],
};

export default function ExpandPeripheralVisionPage() {
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
            Expand Peripheral Vision
          </h1>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Improve speed by widening your “visual span”—the number of words
              you can recognize in a single glance. Practice by aiming your gaze
              at the center of a phrase and letting your peripheral vision pick
              up nearby words, while checking comprehension frequently.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Works
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Reading speed is largely constrained by how many eye fixations you
              make per line and how often you regress. If you can recognize more
              words per fixation, you can move through lines with fewer stops.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              How to Practice
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">1) Two-word chunks:</strong>{" "}
                Read by intentionally grouping two words at a time for a few
                minutes.
              </p>
              <p>
                <strong className="text-foreground">2) Center gaze:</strong>{" "}
                Place your eyes near the middle of a short phrase and try to
                capture the words on both sides.
              </p>
              <p>
                <strong className="text-foreground">3) Increase gradually:</strong>{" "}
                Move from two-word chunks to three- and four-word chunks over
                days (not minutes).
              </p>
            </div>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              A Simple Drill
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Take a paragraph and draw light vertical marks every 3–4 words.
              Use a pointer to keep pace and try to “land” your eyes near each
              mark instead of on individual words. Summarize the paragraph to
              confirm comprehension.
            </p>
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
                href="/consciousness/speed-reading/key-techniques/regression-reduction"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Regression Reduction</span>
              </Link>
              <Link
                href="/consciousness/speed-reading/how-to-practice-speed-reading"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  How to Practice Speed Reading
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

