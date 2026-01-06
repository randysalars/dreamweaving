import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/speed-reading/tips-for-success`;

export const metadata: Metadata = {
  title: "Speed Reading Tips for Success | Speed Reading",
  description:
    "Speed reading tips: practice regularly, preview first, use a guide, run speed drills, and always check comprehension. Progress is gradual but cumulative.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Speed Reading Tips for Success",
    description:
      "Practice regularly, preview first, use a guide, run drills, and always check comprehension.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "speed reading tips",
    "practice",
    "comprehension",
    "previewing",
    "pointer",
    "drills",
  ],
};

export default function TipsForSuccessPage() {
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
            Tips for Success
          </h1>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Speed and comprehension improve with consistent practice. Preview
              before deep reading, use a pointer to stabilize pace, challenge
              yourself with short drills, and always verify understanding.
              Progress can feel slow, but it compounds.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              High-Leverage Tips
            </h2>
            <div className="grid gap-3">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-muted-foreground leading-relaxed">
                  Practice regularly—5–10 minutes daily beats occasional long
                  sessions.
                </p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-muted-foreground leading-relaxed">
                  Preview material before reading in depth to build a mental
                  map.
                </p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-muted-foreground leading-relaxed">
                  Use a guide (finger/pen/cursor) to keep your eyes moving
                  smoothly.
                </p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-muted-foreground leading-relaxed">
                  Push speed in short drills, then check comprehension with a
                  quick summary.
                </p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-muted-foreground leading-relaxed">
                  Be patient—better mechanics (chunking, fewer regressions) take
                  time to become automatic.
                </p>
              </div>
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
                href="/consciousness/speed-reading/key-techniques/use-a-pointer-or-guide"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Use a Pointer or Guide</span>
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
              <Link
                href="/consciousness/speed-reading/benefits-of-speed-reading"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Benefits of Speed Reading
                </span>
              </Link>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

