import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/integration/integration-mistakes`;

export const metadata: Metadata = {
  title: "Common Integration Mistakes | Integration & Grounding",
  description: "Typical pitfalls and errors people make during the integration process. 8 research-based answers about rushing integration, spiritual bypassing, and when to seek support.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Common Integration Mistakes",
    description: "Typical pitfalls and errors people make during the integration process.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["integration mistakes", "spiritual bypassing", "consciousness work", "integration errors"],
};

const questions = [
  {
    text: "What are the most common integration mistakes people make?",
    slug: "what-are-the-most-common-integration-mistakes-people-make",
  },
  {
    text: "Why do people rush back into intense practices too quickly?",
    slug: "why-do-people-rush-back-into-intense-practices-too-quickly",
  },
  {
    text: "What happens when you try to force integration to happen faster?",
    slug: "what-happens-when-you-try-to-force-integration-to-happen-faster",
  },
  {
    text: "Should you talk about your experiences immediately or wait?",
    slug: "should-you-talk-about-your-experiences-immediately-or-wait",
  },
  {
    text: "Why is spiritual bypassing a problem in integration?",
    slug: "why-is-spiritual-bypassing-a-problem-in-integration",
  },
  {
    text: "What's the difference between integration and suppressing the experience?",
    slug: "whats-the-difference-between-integration-and-suppressing-the-experience",
  },
  {
    text: "How do you avoid becoming ungrounded while staying open to change?",
    slug: "how-do-you-avoid-becoming-ungrounded-while-staying-open-to-change",
  },
  {
    text: "When should you seek support during integration instead of going it alone?",
    slug: "when-should-you-seek-support-during-integration-instead-of-going-it-alone",
  },
];

export default function IntegrationMistakesPage() {
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
            Common Integration Mistakes
          </h1>
          <p className="text-xl text-muted-foreground mb-12">
            Typical pitfalls and errors people make during the integration process.
          </p>

          {/* Questions List */}
          <div className="space-y-3">
            {questions.map((question) => (
              <Link
                key={question.slug}
                href={`/consciousness/integration/integration-mistakes/${question.slug}`}
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
