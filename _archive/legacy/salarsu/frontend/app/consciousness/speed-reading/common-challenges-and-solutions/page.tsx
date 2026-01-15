import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/speed-reading/common-challenges-and-solutions`;

export const metadata: Metadata = {
  title: "Common Speed Reading Challenges and Solutions | Speed Reading",
  description:
    "Troubleshoot speed reading: what to do when comprehension drops, your eyes get tired, or the material is complex and technical.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Common Speed Reading Challenges and Solutions",
    description:
      "Troubleshoot speed reading: comprehension drops, eye fatigue, and complex material.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "speed reading challenges",
    "comprehension",
    "eye fatigue",
    "technical reading",
    "regression",
  ],
};

export default function CommonChallengesAndSolutionsPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">
          <div className="space-y-2">
            <Link
              href="/consciousness/speed-reading"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Speed Reading
            </Link>
          </div>

          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Common Challenges and Solutions
          </h1>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              When speed reading breaks, the fix is usually calibration: slow
              down slightly, preview structure, use a guide, and confirm meaning
              with quick summaries. Speed without feedback tends to collapse
              into skimming without understanding.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Challenge: Comprehension Drops
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">What to do:</strong> Reduce
                pace 5–10% and focus on main ideas. Use previewing first, then
                read for meaning in phrases.
              </p>
              <p>
                <strong className="text-foreground">Quick check:</strong> After
                each paragraph, write one sentence: “This paragraph is about…”
              </p>
            </div>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Challenge: Eye Fatigue
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">What to do:</strong> Take
                short breaks, blink intentionally, and adjust lighting/contrast.
                If you’re on a screen, increase font size and line spacing.
              </p>
              <p>
                <strong className="text-foreground">Rule of thumb:</strong> If
                your eyes burn, your practice is too long or too intense—reduce
                session length and build gradually.
              </p>
            </div>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Challenge: Complex or Technical Material
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">What to do:</strong> Use
                speed reading for the first pass (overview), then slow down for
                dense sections. For technical reading, previewing and
                skimming-to-map are often more valuable than raw WPM.
              </p>
              <p>
                <strong className="text-foreground">Strategy:</strong> Identify
                definitions, key formulas, and examples—then reread only those
                parts deliberately.
              </p>
            </div>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Pages
            </h2>
            <div className="grid gap-3">
              <Link
                href="/consciousness/speed-reading/how-to-practice-speed-reading"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  How to Practice Speed Reading
                </span>
              </Link>
              <Link
                href="/consciousness/speed-reading/key-techniques/previewing"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Previewing</span>
              </Link>
              <Link
                href="/consciousness/speed-reading/key-techniques/regression-reduction"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Regression Reduction</span>
              </Link>
              <Link
                href="/consciousness/speed-reading/tips-for-success"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Tips for Success</span>
              </Link>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

