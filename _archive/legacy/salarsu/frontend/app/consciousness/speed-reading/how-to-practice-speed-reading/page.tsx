import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/speed-reading/how-to-practice-speed-reading`;

export const metadata: Metadata = {
  title: "How to Practice Speed Reading | Speed Reading",
  description:
    "A practical, repeatable routine to improve speed reading: start easy, track WPM, increase gradually, and verify comprehension with summaries.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How to Practice Speed Reading",
    description:
      "A practical routine: start easy, track WPM, increase gradually, and verify comprehension with summaries.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "speed reading practice",
    "words per minute",
    "comprehension",
    "reading drills",
    "daily practice",
  ],
};

export default function HowToPracticeSpeedReadingPage() {
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
            How to Practice Speed Reading
          </h1>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Practice speed reading by starting with easy material, tracking
              words per minute (WPM), and gradually increasing pace while
              checking comprehension with quick summaries or questions. Daily
              practice (even 5–10 minutes) builds eye coordination and
              consistency.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              A Simple Daily Routine (10 Minutes)
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">1) Preview (1 min):</strong>{" "}
                Skim headings and the first/last paragraph so you know what the
                piece is about.
              </p>
              <p>
                <strong className="text-foreground">2) Timed read (5 min):</strong>{" "}
                Use a pointer and read at a steady pace. Don’t stop to perfect
                every sentence.
              </p>
              <p>
                <strong className="text-foreground">
                  3) Comprehension check (2 min):
                </strong>{" "}
                Write a 2–3 bullet summary or answer: “What was the main
                claim?” “What were 2 supporting points?”
              </p>
              <p>
                <strong className="text-foreground">4) Calibrate (2 min):</strong>{" "}
                If your summary is solid, increase pace slightly tomorrow. If
                it’s shaky, reduce pace slightly and focus on chunking.
              </p>
            </div>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              How to Track WPM (Quick Method)
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Count the words in a typical line (or use an estimate), multiply
              by the number of lines you read, then divide by minutes. Track
              weekly averages rather than obsessing over a single session.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Progress Without Losing Comprehension
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">
                  Increase in small steps:
                </strong>{" "}
                Add 5–10% speed when comprehension is stable.
              </p>
              <p>
                <strong className="text-foreground">Use easy material:</strong>{" "}
                Build the “mechanics” on familiar text before attacking dense
                technical writing.
              </p>
              <p>
                <strong className="text-foreground">
                  Mix strategies by goal:
                </strong>{" "}
                Skim for overview, scan for details, slow down for complexity.
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
                href="/consciousness/speed-reading/practical-example"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Practical Example</span>
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
        </div>
      </main>
    </div>
  );
}

