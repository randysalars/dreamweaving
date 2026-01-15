import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/integration/integration-mistakes/whats-the-difference-between-integration-and-suppressing-the-experience`;

export const metadata: Metadata = {
  title: "What's the difference between integration and suppressing the experience? | Salars Consciousness",
  description: "Integration processes experiences through conscious awareness and meaning-making, while suppression pushes experiences away from conscious attention to avo",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "What's the difference between integration and suppressing the experience?",
    description: "Integration processes experiences through conscious awareness and meaning-making, while suppression pushes experiences away from conscious attention to avo",
    url: pageUrl,
    type: "article",
  },
  keywords: ["emotional suppression", "psychological integration", "avoidance mechanisms", "conscious processing", "experiential learning", "trauma integration", "meaning-making", "adaptive coping"],
};

export default function WhatsTheDifferenceBetweenIntegrationAndSuppressingTheExperiencePage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/integration/integration-mistakes"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Common Integration Mistakes
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            What's the difference between integration and suppressing the experience?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Integration processes experiences through conscious awareness and meaning-making, while suppression pushes experiences away from conscious attention to avoid discomfort.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Integration engages the prefrontal cortex to create coherent narratives and extract learning from experiences, which leads to psychological growth and adaptive responses. Suppression activates avoidance mechanisms that disconnect experiences from conscious processing, resulting in unresolved emotional content that can resurface later. This difference demonstrates how the brain either incorporates experiences into existing schemas or fragments them from awareness.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The distinction becomes less clear during partial integration, where some aspects of an experience receive conscious attention while others remain suppressed. Some therapeutic approaches deliberately use temporary suppression as a stepping stone toward eventual integration.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/integration/integration-mistakes/what-are-the-most-common-integration-mistakes-people-make"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are the most common integration mistakes people make?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/integration-mistakes/why-do-people-rush-back-into-intense-practices-too-quickly"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Why do people rush back into intense practices too quickly?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/integration-mistakes/what-happens-when-you-try-to-force-integration-to-happen-faster"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What happens when you try to force integration to happen faster?</span>
              </Link>
              
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
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/integration/integration-mistakes"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Common Integration Mistakes questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}