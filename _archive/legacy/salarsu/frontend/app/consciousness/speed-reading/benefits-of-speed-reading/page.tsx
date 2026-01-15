import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/speed-reading/benefits-of-speed-reading`;

export const metadata: Metadata = {
  title: "Benefits of Speed Reading | Speed Reading",
  description:
    "Benefits of speed reading: read more in less time, improve focus, boost confidence, support memory through active engagement, and adapt speed to the material.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Benefits of Speed Reading",
    description:
      "Read more in less time, improve focus, boost confidence, and adapt speed to the material.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "benefits of speed reading",
    "focus",
    "reading confidence",
    "learning",
    "memory retention",
  ],
};

export default function BenefitsOfSpeedReadingPage() {
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
            Benefits of Speed Reading
          </h1>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Speed reading helps you get through more material efficiently,
              improve focus, and build confidence—especially when you pair speed
              with active comprehension checks like summaries and questions. The
              real benefit is flexible control over pace, not maximum WPM.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Practical Benefits
            </h2>
            <div className="grid gap-3">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-muted-foreground leading-relaxed">
                  Read more books, articles, and research in less time.
                </p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-muted-foreground leading-relaxed">
                  Improve focus and concentration by reducing mind-wandering.
                </p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-muted-foreground leading-relaxed">
                  Boost confidence in academic and professional settings.
                </p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-muted-foreground leading-relaxed">
                  Improve retention through active engagement (previewing,
                  summarizing, questioning).
                </p>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                <p className="text-muted-foreground leading-relaxed">
                  Adapt your reading speed to your goals and the complexity of
                  the material.
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
                href="/consciousness/speed-reading/key-techniques/skimming-and-scanning"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Skimming and Scanning</span>
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

