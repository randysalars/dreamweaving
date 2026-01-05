import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/integration/integration-matters/can-you-have-too-many-insights-without-enough-integration-time`;

export const metadata: Metadata = {
  title: "Can you have too many insights without enough integration time? | Salars Consciousness",
  description: "Yes, accumulating multiple insights without processing time creates cognitive overload, emotional dysregulation, and prevents meaningful behavioral change ",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Can you have too many insights without enough integration time?",
    description: "Yes, accumulating multiple insights without processing time creates cognitive overload, emotional dysregulation, and prevents meaningful behavioral change ",
    url: pageUrl,
    type: "article",
  },
  keywords: ["insight fatigue", "cognitive overload", "neuroplasticity", "consolidation", "behavioral change", "processing capacity", "integration practices", "transformation"],
};

export default function CanYouHaveTooManyInsightsWithoutEnoughIntegrationTimePage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/integration/integration-matters"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Why Integration Matters More Than Insight
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Can you have too many insights without enough integration time?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Yes, accumulating multiple insights without processing time creates cognitive overload, emotional dysregulation, and prevents meaningful behavioral change from occurring.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Insights trigger neuroplastic changes that require consolidation time to form stable neural pathways. When new revelations arrive before previous ones integrate, the brain defaults to familiar patterns because it lacks the processing capacity to restructure multiple belief systems simultaneously. This results in insight fatigue, where profound realizations lose their transformative power and become mere intellectual concepts disconnected from lived experience.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Integration capacity varies based on the depth of insights, individual processing speed, and available support systems. Some people can handle rapid successive insights during intensive experiences, while others require weeks between meaningful realizations.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/integration/integration-matters/why-does-integration-matter-more-than-insight-in-consciousness-work"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Why does integration matter more than insight in consciousness work?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/integration-matters/what-is-the-difference-between-having-an-insight-and-integrating-it"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is the difference between having an insight and integrating it?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/integration-matters/how-long-does-integration-typically-take-after-a-profound-experience"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How long does integration typically take after a profound experience?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/staying-functional/how-do-you-stay-functional-while-your-awareness-is-changing"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do you stay functional while your awareness is changing?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/staying-functional/what-does-grounding-mean-in-the-context-of-consciousness-shifts"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What does grounding mean in the context of consciousness shifts?</span>
              </Link>
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/integration/integration-matters"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Why Integration Matters More Than Insight questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}