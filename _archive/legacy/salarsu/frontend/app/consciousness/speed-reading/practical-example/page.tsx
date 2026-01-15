import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/speed-reading/practical-example`;

export const metadata: Metadata = {
  title: "Practical Speed Reading Example | Speed Reading",
  description:
    "Try a practical speed reading drill: read a familiar article with a pointer, increase pace gradually, and summarize to reinforce comprehension.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Practical Speed Reading Example",
    description:
      "A practical drill: read with a pointer, increase pace gradually, and summarize to reinforce comprehension.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "speed reading example",
    "reading drill",
    "pointer",
    "summary",
    "comprehension",
  ],
};

export default function PracticalSpeedReadingExamplePage() {
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
            Practical Example
          </h1>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Pick a familiar article and read it using your finger as a guide,
              moving smoothly under each line. Increase speed gradually while
              checking comprehension. Afterward, summarize the main points in
              your own words to reinforce retention.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Step-by-Step Drill (5–8 Minutes)
            </h2>
            <div className="space-y-3 text-muted-foreground leading-relaxed">
              <p>
                <strong className="text-foreground">1) Choose material:</strong>{" "}
                A short piece you already understand (news, blog post, essay).
              </p>
              <p>
                <strong className="text-foreground">2) Preview:</strong> Read
                headings and the first paragraph to set expectations.
              </p>
              <p>
                <strong className="text-foreground">3) Baseline pass:</strong>{" "}
                Read for 2 minutes at a comfortable speed using a pointer.
              </p>
              <p>
                <strong className="text-foreground">
                  4) Speed pass:
                </strong>{" "}
                Read for 2 minutes at ~10% faster. Keep the pointer moving; no
                pausing.
              </p>
              <p>
                <strong className="text-foreground">5) Summary check:</strong>{" "}
                Write 3 bullets: main point + 2 supporting details.
              </p>
            </div>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              What to Do If You Get Lost
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Don’t immediately reread sentence-by-sentence. First, slow down
              slightly and continue. If the paragraph still doesn’t make sense,
              then backtrack once to the start of the paragraph and reread with
              stronger previewing and chunking.
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
                href="/consciousness/speed-reading/key-techniques/minimize-subvocalization"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Minimize Subvocalization
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

