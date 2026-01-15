import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/safety-and-risks/what-is-the-difference-between-dissociation-and-altered-states`;

export const metadata: Metadata = {
  title: "What is the difference between dissociation and altered states? | Salars Consciousness",
  description: "Dissociation is a specific psychological mechanism where awareness detaches from experience, while altered states encompass any significant change from ord",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "What is the difference between dissociation and altered states?",
    description: "Dissociation is a specific psychological mechanism where awareness detaches from experience, while altered states encompass any significant change from ord",
    url: pageUrl,
    type: "article",
  },
  keywords: ["depersonalization", "derealization", "trance states", "consciousness modification", "psychological dissociation", "mindfulness detachment", "ego dissolution", "awareness fragmentation"],
};

export default function WhatIsTheDifferenceBetweenDissociationAndAlteredStatesPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/safety-and-risks"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Safety, Risks & Stability
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            What is the difference between dissociation and altered states?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Dissociation is a specific psychological mechanism where awareness detaches from experience, while altered states encompass any significant change from ordinary waking consciousness.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Dissociation represents a protective mental process that creates distance between the self and overwhelming experiences, often involving disconnection from thoughts, feelings, or memories. Altered states include a broader spectrum of consciousness changes that can result from meditation, substances, sleep deprivation, or spiritual practices. This distinction matters because dissociation typically indicates psychological stress responses, while altered states can be intentionally induced for therapeutic, spiritual, or exploratory purposes.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The boundary blurs when dissociation occurs within deliberately induced altered states, such as during deep meditation or psychedelic therapy. Some altered states naturally include dissociative elements, making the distinction more about context and intention than discrete categories.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/safety-and-risks/are-altered-states-dangerous"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Are altered states dangerous?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/safety-and-risks/when-can-altered-states-become-destabilizing"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">When can altered states become destabilizing?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/safety-and-risks/who-should-avoid-certain-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Who should avoid certain altered states?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/definitions-foundations/what-is-an-altered-state-of-consciousness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is an altered state of consciousness?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/definitions-foundations/what-defines-normal-waking-consciousness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What defines normal waking consciousness?</span>
              </Link>
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/altered-states/safety-and-risks"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Safety, Risks & Stability questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}