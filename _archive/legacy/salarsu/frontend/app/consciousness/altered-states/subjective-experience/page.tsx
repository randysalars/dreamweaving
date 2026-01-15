import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/subjective-experience`;

export const metadata: Metadata = {
  title: "Subjective Experience & Perception Changes | Altered States",
  description: "How altered states feel subjectively and affect perception, emotion, and sensation.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Subjective Experience & Perception Changes",
    description: "How altered states feel subjectively and affect perception, emotion, and sensation.",
    url: pageUrl,
    type: "website",
  },
};

export default function SubjectiveExperiencePage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-4xl space-y-8">
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Altered States
            </Link>
          </div>

          <div className="space-y-3">
            <h1 className="text-4xl font-semibold tracking-tight text-foreground">
              Subjective Experience & Perception Changes
            </h1>
            <p className="text-lg text-muted-foreground">
              How altered states feel subjectively and affect perception, emotion, and sensation.
            </p>
          </div>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Questions in this category
            </h2>
            <div className="grid gap-3">
              <Link
                href="/consciousness/altered-states/subjective-experience/how-do-altered-states-feel-subjectively"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do altered states feel subjectively?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/do-altered-states-change-perception-of-time"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do altered states change perception of time?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/do-altered-states-affect-sensory-clarity"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do altered states affect sensory clarity?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/can-altered-states-increase-vividness-of-experience"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states increase vividness of experience?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/can-altered-states-dull-sensation"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states dull sensation?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/do-altered-states-change-emotional-intensity"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do altered states change emotional intensity?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/can-altered-states-feel-euphoric"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states feel euphoric?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/can-altered-states-feel-frightening"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states feel frightening?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/do-altered-states-change-body-awareness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do altered states change body awareness?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/can-altered-states-alter-sense-of-self"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states alter sense of self?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/can-altered-states-create-feelings-of-unity-or-separation"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states create feelings of unity or separation?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/do-altered-states-affect-thought-speed"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Do altered states affect thought speed?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/can-altered-states-silence-internal-dialogue"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states silence internal dialogue?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/can-altered-states-amplify-imagination"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states amplify imagination?</span>
              </Link>
            </div>
          </section>

          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/altered-states"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Altered States categories
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>
        </div>
      </main>
    </div>
  );
}
