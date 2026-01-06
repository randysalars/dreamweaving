import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/sleep-dreams/sleep-optimization/what-role-does-the-mattress-and-pillow-play-in-sleep-quality`;

export const metadata: Metadata = {
  title: "What role does the mattress and pillow play in sleep quality? | Salars Consciousness",
  description: "What role does the mattress and pillow play in sleep quality?",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "What role does the mattress and pillow play in sleep quality?",
    description: "What role does the mattress and pillow play in sleep quality?",
    url: pageUrl,
    type: "article",
  },
  keywords: ["consciousness", "awareness", "perception"],
};

export default function WhatRoleDoesTheMattressAndPillowPlayInSleepQualityPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/sleep-dreams/sleep-optimization"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Sleep Optimization & Hygiene
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            What role does the mattress and pillow play in sleep quality?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Mattress and pillow affect sleep by supporting spinal alignment, reducing pressure points, and regulating temperature. The right setup reduces pain and micro-awakenings, which improves sleep continuity and how rested you feel.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              This matters because discomfort results in movement and arousals that you may not remember, leading to fragmented sleep. Better alignment reduces muscle tension and joint stress, which leads to fewer wake-ups and better morning recovery. Temperature and material choice also influence sweating and restlessness, affecting overall sleep quality.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              No single firmness is “best”—body size, sleep position, and pain conditions change the ideal. If you’re waking with consistent neck/back pain, adjusting pillow loft or adding targeted support can help more than replacing everything at once.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/sleep-dreams/sleep-optimization/what-is-sleep-hygiene"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is sleep hygiene?</span>
              </Link>
              
              <Link
                href="/consciousness/sleep-dreams/sleep-optimization/how-does-light-exposure-affect-sleep"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How does light exposure affect sleep?</span>
              </Link>
              
              <Link
                href="/consciousness/sleep-dreams/sleep-optimization/what-is-the-best-sleeping-position"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is the best sleeping position?</span>
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
              href="/consciousness/sleep-dreams/sleep-optimization"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Sleep Optimization & Hygiene questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}
