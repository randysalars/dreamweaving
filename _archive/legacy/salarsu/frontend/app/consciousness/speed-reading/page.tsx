import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/speed-reading`;

export const metadata: Metadata = {
  title: "Speed Reading | Salars Consciousness",
  description:
    "Learn practical speed reading techniques to increase reading speed while protecting comprehension: subvocalization reduction, peripheral vision, skimming, previewing, and more.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Speed Reading",
    description:
      "Practical speed reading techniques to increase reading speed while protecting comprehension.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "speed reading",
    "reading comprehension",
    "subvocalization",
    "peripheral vision",
    "skimming",
    "scanning",
    "previewing",
    "regression reduction",
    "reading focus",
  ],
};

const techniqueLinks = [
  {
    title: "Minimize Subvocalization",
    description: "Reduce the habit of pronouncing each word internally.",
    href: "/consciousness/speed-reading/key-techniques/minimize-subvocalization",
  },
  {
    title: "Expand Peripheral Vision",
    description: "Take in groups of words, not single-word fixations.",
    href: "/consciousness/speed-reading/key-techniques/expand-peripheral-vision",
  },
  {
    title: "Use a Pointer or Guide",
    description: "Keep your eyes moving smoothly across the line.",
    href: "/consciousness/speed-reading/key-techniques/use-a-pointer-or-guide",
  },
  {
    title: "Skimming and Scanning",
    description: "Find main ideas quickly and locate specific info fast.",
    href: "/consciousness/speed-reading/key-techniques/skimming-and-scanning",
  },
  {
    title: "Previewing",
    description: "Build a mental map before you read in detail.",
    href: "/consciousness/speed-reading/key-techniques/previewing",
  },
  {
    title: "Regression Reduction",
    description: "Avoid unnecessary backtracking and rereading.",
    href: "/consciousness/speed-reading/key-techniques/regression-reduction",
  },
];

const practiceLinks = [
  {
    title: "How to Practice Speed Reading",
    description: "A simple routine to improve speed + comprehension.",
    href: "/consciousness/speed-reading/how-to-practice-speed-reading",
  },
  {
    title: "Practical Example",
    description: "Try a guided, real-world drill with summaries.",
    href: "/consciousness/speed-reading/practical-example",
  },
  {
    title: "Common Challenges and Solutions",
    description: "Fix comprehension drops, eye fatigue, and dense material.",
    href: "/consciousness/speed-reading/common-challenges-and-solutions",
  },
  {
    title: "Benefits of Speed Reading",
    description: "What you gain when speed and comprehension align.",
    href: "/consciousness/speed-reading/benefits-of-speed-reading",
  },
  {
    title: "Tips for Success",
    description: "Small habits that make speed reading stick.",
    href: "/consciousness/speed-reading/tips-for-success",
  },
];

export default function SpeedReadingPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12 max-w-6xl">
        <Link
          href="/consciousness"
          className="text-primary hover:underline mb-6 inline-flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Consciousness
        </Link>

        <div className="space-y-4 mb-10">
          <Badge variant="outline">Accelerated Learning</Badge>
          <h1 className="text-4xl md:text-5xl font-bold text-foreground">
            Speed Reading
          </h1>
          <p className="text-lg text-muted-foreground max-w-3xl">
            Speed reading is a set of techniques that helps you move through
            text faster without sacrificing understanding. The goal is flexible
            control: slow down for dense passages, speed up for familiar or
            easier material, and always verify comprehension.
          </p>
        </div>

        <div className="rounded-2xl border border-border bg-card/40 p-8">
          <h2 className="text-2xl md:text-3xl font-semibold text-foreground mb-4">
            Start Here
          </h2>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
              <p className="text-muted-foreground">
                Use a <strong className="text-foreground">pointer</strong> to
                reduce regressions and stabilize pace.
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
              <p className="text-muted-foreground">
                Read in <strong className="text-foreground">phrases</strong>,
                not word-by-word.
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
              <p className="text-muted-foreground">
                <strong className="text-foreground">Preview</strong> headings
                and structure before deep reading.
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
              <p className="text-muted-foreground">
                <strong className="text-foreground">Measure</strong> speed (WPM)
                and comprehension weekly.
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
              <p className="text-muted-foreground">
                <strong className="text-foreground">Practice daily</strong> for
                5–10 minutes; consistency matters most.
              </p>
            </div>
          </div>
        </div>

        <Separator className="my-14" />

        <section className="space-y-6">
          <div className="flex items-baseline justify-between gap-4 flex-wrap">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground">
              Key Techniques
            </h2>
            <Link
              href="/consciousness/speed-reading/key-techniques"
              className="text-primary hover:underline"
            >
              View all techniques
            </Link>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {techniqueLinks.map((card) => (
              <Link key={card.href} href={card.href} className="group">
                <div className="h-full p-6 rounded-2xl border border-border bg-card/40 hover:bg-card/60 transition-all hover:scale-[1.02] hover:shadow-md">
                  <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                    {card.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mt-2">
                    {card.description}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </section>

        <Separator className="my-14" />

        <section className="space-y-6">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground">
            Practice, Examples, and Troubleshooting
          </h2>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {practiceLinks.map((card) => (
              <Link key={card.href} href={card.href} className="group">
                <div className="h-full p-6 rounded-2xl border border-border bg-card/40 hover:bg-card/60 transition-all hover:scale-[1.02] hover:shadow-md">
                  <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                    {card.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mt-2">
                    {card.description}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

