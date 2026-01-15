import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/integration/grounding-not-regression`;

export const metadata: Metadata = {
  title: "Why Grounding Is Not Regression | Integration & Grounding",
  description: "Clarifying the difference between healthy grounding and backwards movement. 8 research-based answers about embodiment, grounding practices, and maintaining expanded awareness.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Why Grounding Is Not Regression",
    description: "Clarifying the difference between healthy grounding and backwards movement.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["grounding", "embodiment", "spiritual practice", "consciousness", "regression"],
};

const questions = [
  {
    text: "Is grounding the same as going backwards in consciousness development?",
    slug: "is-grounding-the-same-as-going-backwards-in-consciousness-development",
  },
  {
    text: "Why does grounding sometimes feel like losing progress?",
    slug: "why-does-grounding-sometimes-feel-like-losing-progress",
  },
  {
    text: "What's the difference between healthy grounding and spiritual bypassing?",
    slug: "whats-the-difference-between-healthy-grounding-and-spiritual-bypassing",
  },
  {
    text: "Can you be both grounded and spiritually aware at the same time?",
    slug: "can-you-be-both-grounded-and-spiritually-aware-at-the-same-time",
  },
  {
    text: "Why do some teachers emphasize grounding over transcendence?",
    slug: "why-do-some-teachers-emphasize-grounding-over-transcendence",
  },
  {
    text: "What does \"embodiment\" mean in consciousness work?",
    slug: "what-does-embodiment-mean-in-consciousness-work",
  },
  {
    text: "How do you ground without losing the benefits of expanded awareness?",
    slug: "how-do-you-ground-without-losing-the-benefits-of-expanded-awareness",
  },
  {
    text: "Why is it important to return to the body after consciousness exploration?",
    slug: "why-is-it-important-to-return-to-the-body-after-consciousness-exploration",
  },
];

export default function GroundingNotRegressionPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-4xl">

          {/* Breadcrumb */}
          <div className="mb-6">
            <Link
              href="/consciousness/integration"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Integration & Grounding
            </Link>
          </div>

          {/* Header */}
          <h1 className="text-4xl font-bold mb-4 text-foreground">
            Why Grounding Is Not Regression
          </h1>
          <p className="text-xl text-muted-foreground mb-12">
            Clarifying the difference between healthy grounding and backwards movement.
          </p>

          {/* Questions List */}
          <div className="space-y-3">
            {questions.map((question) => (
              <Link
                key={question.slug}
                href={`/consciousness/integration/grounding-not-regression/${question.slug}`}
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-5 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                <span className="text-lg text-foreground">{question.text}</span>
              </Link>
            ))}
          </div>

        </div>
      </main>
    </div>
  );
}
