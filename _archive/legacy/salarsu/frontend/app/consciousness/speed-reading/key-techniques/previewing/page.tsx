import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/speed-reading/key-techniques/previewing`;

export const metadata: Metadata = {
  title: "Previewing | Speed Reading",
  description:
    "Preview headings, subheadings, and summaries before reading to create a mental map and improve comprehension at higher speeds.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Previewing",
    description:
      "Preview headings, subheadings, and summaries before reading to create a mental map and improve comprehension.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["previewing", "reading strategy", "mental map", "comprehension"],
};

export default function PreviewingPage() {
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
            Previewing
          </h1>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Preview by scanning headings, subheadings, visuals, and summaries
              before you read in detail. This creates a mental map, so your
              brain knows what to look for—and comprehension stays higher even
              when you increase speed.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              A 2-Minute Preview Routine
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">1) Structure:</strong>{" "}
                Read the title, headings, and subheadings.
              </p>
              <p>
                <strong className="text-foreground">2) Signals:</strong>{" "}
                Notice bold terms, lists, charts, and callouts.
              </p>
              <p>
                <strong className="text-foreground">3) Questions:</strong>{" "}
                Ask: “What is this trying to prove or explain?” and “What do I
                need from it?”
              </p>
              <p>
                <strong className="text-foreground">4) Summaries:</strong>{" "}
                Read the intro and conclusion (or abstract) if present.
              </p>
            </div>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Pages
            </h2>
            <div className="grid gap-3">
              <Link
                href="/consciousness/speed-reading/key-techniques/skimming-and-scanning"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Skimming and Scanning</span>
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

