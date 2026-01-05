import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/sleep-dreams/dream-science/what-are-reality-checks-for-lucid-dreaming`;

export const metadata: Metadata = {
  title: "What are reality checks for lucid dreaming? | Salars Consciousness",
  description: "What are reality checks for lucid dreaming?",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "What are reality checks for lucid dreaming?",
    description: "What are reality checks for lucid dreaming?",
    url: pageUrl,
    type: "article",
  },
  keywords: ["consciousness", "awareness", "perception"],
};

export default function WhatAreRealityChecksForLucidDreamingPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/sleep-dreams/dream-science"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dream Science & Lucid Dreaming
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            What are reality checks for lucid dreaming?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Reality checks are small tests you do while awake to confirm you’re not dreaming—then repeat in dreams. Examples include reading text twice, pinching your nose and trying to breathe, or checking a clock.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Reality checks work because they build a habit of questioning your state, which leads to lucidity when dream logic gets weird. The “critical reflection” moment results in recognition, and recognition can unlock choice—even simple choices like calming down in a nightmare. They also provide a practical, beginner-friendly bridge between daytime attention and nighttime awareness.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Checks work best when paired with genuine curiosity, not rote repetition; otherwise the habit doesn’t transfer into dreams. Some checks fail occasionally even in dreams, so combining multiple cues (and noticing dream signs) is more reliable than any single test.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/sleep-dreams/dream-science/what-are-dreams-and-why-do-we-dream"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are dreams and why do we dream?</span>
              </Link>
              
              <Link
                href="/consciousness/sleep-dreams/dream-science/what-is-lucid-dreaming"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is lucid dreaming?</span>
              </Link>
              
              <Link
                href="/consciousness/sleep-dreams/dream-science/how-can-i-learn-to-lucid-dream"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How can I learn to lucid dream?</span>
              </Link>
              
              <Link
                href="/consciousness/sleep-dreams/sleep-fundamentals/what-are-the-stages-of-sleep-and-what-happens-in-each"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are the stages of sleep and what happens in each?</span>
              </Link>
              
              <Link
                href="/consciousness/sleep-dreams/sleep-fundamentals/why-do-we-need-sleep"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Why do we need sleep?</span>
              </Link>
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/sleep-dreams/dream-science"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Dream Science & Lucid Dreaming questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}
