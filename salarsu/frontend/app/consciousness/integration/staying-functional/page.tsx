import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/integration/staying-functional`;

export const metadata: Metadata = {
  title: "How to Stay Functional While Awareness Changes | Integration & Grounding",
  description: "Practical guidance for maintaining daily function during consciousness shifts. 8 research-based answers about grounding, balancing practice with responsibilities, and staying present.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How to Stay Functional While Awareness Changes",
    description: "Practical guidance for maintaining daily function during consciousness shifts.",
    url: pageUrl,
    type: "article",
  },
  keywords: ["grounding", "functional", "consciousness", "daily life", "spiritual practice", "balance"],
};

const questions = [
  {
    text: "How do you stay functional while your awareness is changing?",
    slug: "how-do-you-stay-functional-while-your-awareness-is-changing",
  },
  {
    text: "What does grounding mean in the context of consciousness shifts?",
    slug: "what-does-grounding-mean-in-the-context-of-consciousness-shifts",
  },
  {
    text: "Why do some people feel disconnected from daily life after consciousness work?",
    slug: "why-do-some-people-feel-disconnected-from-daily-life-after-consciousness-work",
  },
  {
    text: "How do you balance spiritual practice with practical responsibilities?",
    slug: "how-do-you-balance-spiritual-practice-with-practical-responsibilities",
  },
  {
    text: "What are signs that you're losing functional grounding?",
    slug: "what-are-signs-that-youre-losing-functional-grounding",
  },
  {
    text: "Can consciousness changes make it harder to work or maintain relationships?",
    slug: "can-consciousness-changes-make-it-harder-to-work-or-maintain-relationships",
  },
  {
    text: "How do you integrate expanded awareness into everyday activities?",
    slug: "how-do-you-integrate-expanded-awareness-into-everyday-activities",
  },
  {
    text: "What helps you stay present in ordinary tasks after altered states?",
    slug: "what-helps-you-stay-present-in-ordinary-tasks-after-altered-states",
  },
];

export default function StayingFunctionalPage() {
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
            How to Stay Functional While Awareness Changes
          </h1>
          <p className="text-xl text-muted-foreground mb-12">
            Practical guidance for maintaining daily function during consciousness shifts.
          </p>

          {/* Questions List */}
          <div className="space-y-3">
            {questions.map((question) => (
              <Link
                key={question.slug}
                href={`/consciousness/integration/staying-functional/${question.slug}`}
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
