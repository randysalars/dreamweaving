import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/integration/integration-matters/how-do-you-know-when-an-insight-has-been-fully-integrated`;

export const metadata: Metadata = {
  title: "How do you know when an insight has been fully integrated? | Salars Consciousness",
  description: "Full integration shows through consistent behavioral changes, automatic responses that align with the insight, and the absence of internal conflict around ",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How do you know when an insight has been fully integrated?",
    description: "Full integration shows through consistent behavioral changes, automatic responses that align with the insight, and the absence of internal conflict around ",
    url: pageUrl,
    type: "article",
  },
  keywords: ["embodied understanding", "behavioral change", "neural rewiring", "cognitive-emotional alignment", "insight processing", "pattern integration", "unconscious competence", "somatic integration"],
};

export default function HowDoYouKnowWhenAnInsightHasBeenFullyIntegratedPage() {
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
            How do you know when an insight has been fully integrated?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Full integration shows through consistent behavioral changes, automatic responses that align with the insight, and the absence of internal conflict around the topic.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Integration occurs because insights must rewire neural pathways and emotional associations to create lasting change. When insights remain purely cognitive, they compete with existing patterns and create internal tension. Full integration results in coherent alignment between understanding, feeling, and action because the new pattern has become the default response rather than requiring conscious effort to maintain.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Integration depth varies based on how fundamental the insight challenges existing belief systems and identity structures. Insights that contradict core assumptions take longer to integrate and may require multiple processing cycles before reaching behavioral consistency.
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