import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/sleep-dreams/sleep-consciousness/what-is-sleep-paralysis-and-why-does-it-happen`;

export const metadata: Metadata = {
  title: "What is sleep paralysis and why does it happen? | Salars Consciousness",
  description: "What is sleep paralysis and why does it happen?",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "What is sleep paralysis and why does it happen?",
    description: "What is sleep paralysis and why does it happen?",
    url: pageUrl,
    type: "article",
  },
  keywords: ["consciousness", "awareness", "perception"],
};

export default function WhatIsSleepParalysisAndWhyDoesItHappenPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/sleep-dreams/sleep-consciousness"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Sleep & Consciousness States
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            What is sleep paralysis and why does it happen?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Sleep paralysis is a brief episode where you’re conscious but can’t move, typically while falling asleep or waking. It happens when REM muscle atonia persists into wakefulness, sometimes with vivid hallucinations.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Sleep paralysis can feel terrifying because the brain’s threat system is active while the body remains “locked” in REM immobility. That mismatch leads to panic, chest pressure sensations, and intense interpretations of the experience. Understanding the mechanism reduces fear, which often shortens episodes and prevents a feedback loop of anxiety-driven sleep disruption.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Episodes are more common with sleep deprivation, irregular schedules, sleeping on your back, and high stress. If paralysis is frequent, includes sudden daytime sleep attacks, or severely disrupts life, it can be worth discussing with a clinician to rule out narcolepsy or other sleep disorders.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/sleep-dreams/sleep-consciousness/is-sleep-an-altered-state-of-consciousness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Is sleep an altered state of consciousness?</span>
              </Link>
              
              <Link
                href="/consciousness/sleep-dreams/sleep-consciousness/what-is-hypnagogia-the-transition-to-sleep"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is hypnagogia (the transition to sleep)?</span>
              </Link>
              
              <Link
                href="/consciousness/sleep-dreams/sleep-consciousness/can-you-be-conscious-while-sleeping"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can you be conscious while sleeping?</span>
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
              href="/consciousness/sleep-dreams/sleep-consciousness"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Sleep & Consciousness States questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}
