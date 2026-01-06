import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/speed-reading/key-techniques`;

export const metadata: Metadata = {
  title: "Key Speed Reading Techniques | Speed Reading",
  description:
    "Core speed reading techniques: subvocalization reduction, wider visual span, pointers, skimming and scanning, previewing, and regression reduction.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Key Speed Reading Techniques",
    description:
      "Core speed reading techniques: subvocalization reduction, wider visual span, pointers, skimming and scanning, previewing, and regression reduction.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "speed reading techniques",
    "subvocalization",
    "peripheral vision",
    "pointer reading",
    "skimming",
    "scanning",
    "previewing",
    "regression",
  ],
};

const techniques = [
  {
    text: "Minimize Subvocalization",
    slug: "minimize-subvocalization",
  },
  {
    text: "Expand Peripheral Vision",
    slug: "expand-peripheral-vision",
  },
  {
    text: "Use a Pointer or Guide",
    slug: "use-a-pointer-or-guide",
  },
  {
    text: "Skimming and Scanning",
    slug: "skimming-and-scanning",
  },
  {
    text: "Previewing",
    slug: "previewing",
  },
  {
    text: "Regression Reduction",
    slug: "regression-reduction",
  },
];

export default function SpeedReadingKeyTechniquesPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12 max-w-4xl">
        <Link
          href="/consciousness/speed-reading"
          className="text-primary hover:underline mb-6 inline-flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Speed Reading
        </Link>

        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-foreground">
          Key Techniques
        </h1>
        <p className="text-xl text-muted-foreground mb-12">
          Build speed by improving eye movement, attention, and strategy (not by
          forcing yourself to “go fast”).
        </p>

        <div className="space-y-4">
          {techniques.map((t) => (
            <Link
              key={t.slug}
              href={`/consciousness/speed-reading/key-techniques/${t.slug}`}
              className="block group"
            >
              <div className="p-6 rounded-xl border border-border bg-card/40 hover:bg-card/60 transition-all hover:scale-[1.02] hover:shadow-md">
                <div className="flex items-start gap-4">
                  <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                    <HelpCircle className="h-5 w-5 text-primary" />
                  </div>
                  <h2 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors flex-1">
                    {t.text}
                  </h2>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}

