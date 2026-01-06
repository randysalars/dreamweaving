import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/speed-reading/key-techniques/minimize-subvocalization`;

export const metadata: Metadata = {
  title: "Minimize Subvocalization | Speed Reading",
  description:
    "Minimize subvocalization to read faster by shifting from inner speech to phrase-based meaning, while keeping comprehension high.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Minimize Subvocalization",
    description:
      "Shift from word-by-word inner speech to phrase-based meaning—without losing comprehension.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "subvocalization",
    "inner voice",
    "speed reading",
    "phrase reading",
    "reading comprehension",
  ],
};

export default function MinimizeSubvocalizationPage() {
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
            Minimize Subvocalization
          </h1>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Reduce subvocalization by reading in phrases and focusing on
              meaning instead of “hearing” every word internally. A pointer,
              gentle speed increases, and short comprehension checks help you
              stay accurate while your brain learns to process bigger chunks.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              What It Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Subvocalization is a common habit—your inner voice “speaks” the
              text as you read. That can limit speed because speech is slower
              than visual recognition and meaning extraction. The goal is not to
              eliminate inner speech completely; it’s to prevent it from forcing
              a word-by-word pace.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              How to Practice
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">1) Use a guide:</strong>{" "}
                Move a finger or pen under the line at a steady pace. Your eyes
                tend to follow it, which reduces time spent on each word.
              </p>
              <p>
                <strong className="text-foreground">2) Read in chunks:</strong>{" "}
                Intentionally group 2–4 words at a time (especially common
                phrase pairs like “in order to”, “as a result”, “for example”).
              </p>
              <p>
                <strong className="text-foreground">3) Summarize quickly:</strong>{" "}
                After a paragraph, say the main point in one sentence. This
                trains meaning-first reading.
              </p>
            </div>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              A 60-Second Drill
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Pick an easy article. Set a timer for 60 seconds. Use your finger
              to keep a slightly faster pace than normal. When time is up, write
              a 2–3 bullet summary. If you can’t summarize, slow down a notch
              and repeat.
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
                href="/consciousness/speed-reading/key-techniques/previewing"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Previewing</span>
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

