import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/integration/integration-mistakes/what-are-the-most-common-integration-mistakes-people-make`;

export const metadata: Metadata = {
  title: "What are the most common integration mistakes people make? | Salars Consciousness",
  description: "Common integration mistakes include rushing the process, ignoring emotional resistance, compartmentalizing experiences, and lacking proper support systems ",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "What are the most common integration mistakes people make?",
    description: "Common integration mistakes include rushing the process, ignoring emotional resistance, compartmentalizing experiences, and lacking proper support systems ",
    url: pageUrl,
    type: "article",
  },
  keywords: ["integration process", "spiritual bypassing", "trauma integration", "shadow work", "nervous system regulation", "psychological assimilation", "consciousness development", "embodied awareness"],
};

export default function WhatAreTheMostCommonIntegrationMistakesPeopleMakePage() {
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
            What are the most common integration mistakes people make?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Common integration mistakes include rushing the process, ignoring emotional resistance, compartmentalizing experiences, and lacking proper support systems during assimilation periods.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              These mistakes occur because integration requires time for neural pathways to reorganize and stabilize new patterns of awareness. Rushing leads to incomplete processing, while ignoring resistance creates internal conflict that blocks assimilation. Compartmentalization prevents experiences from connecting with existing knowledge structures, resulting in isolated insights rather than coherent understanding. Without adequate support, individuals often revert to familiar patterns because the nervous system defaults to established pathways when overwhelmed.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Integration success varies significantly based on individual readiness, experience intensity, and available resources. Some people naturally integrate experiences more fluidly, while others require structured approaches and extended timeframes.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
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
                href="/consciousness/integration/integration-mistakes/should-you-talk-about-your-experiences-immediately-or-wait"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Should you talk about your experiences immediately or wait?</span>
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