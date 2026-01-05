import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/integration/integration-matters`;

export const metadata: Metadata = {
  title: "Why Integration Matters More Than Insight | Integration & Grounding",
  description: "Understanding why integration is more important than insights in consciousness work. 8 research-based answers about integration vs insight, timing, and what happens when integration is neglected.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Why Integration Matters More Than Insight",
    description: "Understanding why integration is more important than insights in consciousness work.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["integration", "insight", "consciousness work", "spiritual practice", "embodiment"],
};

const questions = [
  {
    text: "Why does integration matter more than insight in consciousness work?",
    slug: "why-does-integration-matter-more-than-insight-in-consciousness-work",
  },
  {
    text: "What is the difference between having an insight and integrating it?",
    slug: "what-is-the-difference-between-having-an-insight-and-integrating-it",
  },
  {
    text: "How long does integration typically take after a profound experience?",
    slug: "how-long-does-integration-typically-take-after-a-profound-experience",
  },
  {
    text: "What happens when insights aren't properly integrated?",
    slug: "what-happens-when-insights-arent-properly-integrated",
  },
  {
    text: "Can you have too many insights without enough integration time?",
    slug: "can-you-have-too-many-insights-without-enough-integration-time",
  },
  {
    text: "Why do some people feel worse after profound consciousness experiences?",
    slug: "why-do-some-people-feel-worse-after-profound-consciousness-experiences",
  },
  {
    text: "What makes integration harder than the initial experience?",
    slug: "what-makes-integration-harder-than-the-initial-experience",
  },
  {
    text: "How do you know when an insight has been fully integrated?",
    slug: "how-do-you-know-when-an-insight-has-been-fully-integrated",
  },
];

export default function IntegrationMattersPage() {
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
            Why Integration Matters More Than Insight
          </h1>
          <p className="text-xl text-muted-foreground mb-12">
            Understanding why integration is more important than insights in consciousness work.
          </p>

          {/* Questions List */}
          <div className="space-y-3">
            {questions.map((question) => (
              <Link
                key={question.slug}
                href={`/consciousness/integration/integration-matters/${question.slug}`}
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
