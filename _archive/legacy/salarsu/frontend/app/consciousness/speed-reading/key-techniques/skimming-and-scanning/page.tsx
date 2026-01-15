import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/speed-reading/key-techniques/skimming-and-scanning`;

export const metadata: Metadata = {
  title: "Skimming and Scanning | Speed Reading",
  description:
    "Skim to capture the main ideas quickly and scan to locate specific information—two essential speed reading strategies.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Skimming and Scanning",
    description:
      "Skim to capture the main ideas quickly and scan to locate specific information.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["skimming", "scanning", "main ideas", "information retrieval"],
};

export default function SkimmingAndScanningPage() {
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
            Skimming and Scanning
          </h1>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Skimming is for understanding the gist (structure, claims, key
              points). Scanning is for finding a specific detail (a date, name,
              definition, or step). Use them to match your reading speed to your
              purpose instead of reading everything at the same pace.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              How to Skim
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">1) Read headings:</strong>{" "}
                Use the table of contents, headings, and subheadings to see the
                map.
              </p>
              <p>
                <strong className="text-foreground">2) Hunt topic sentences:</strong>{" "}
                First sentences of paragraphs often carry the main idea.
              </p>
              <p>
                <strong className="text-foreground">3) Capture keywords:</strong>{" "}
                Bold terms, lists, and summaries are high-signal.
              </p>
            </div>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              How to Scan
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Decide what you’re looking for (a number, name, concept). Then
              move your eyes quickly down the page, letting that target “pop”
              out. You’re not reading sentences; you’re searching for a match.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Pages
            </h2>
            <div className="grid gap-3">
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

