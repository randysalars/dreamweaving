import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/safety-and-risks/when-can-altered-states-become-destabilizing`;

export const metadata: Metadata = {
  title: "When can altered states become destabilizing? | Salars Consciousness",
  description: "Altered states become destabilizing when they exceed cognitive tolerance limits, occur without proper preparation, or interact with existing psychological ",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "When can altered states become destabilizing?",
    description: "Altered states become destabilizing when they exceed cognitive tolerance limits, occur without proper preparation, or interact with existing psychological ",
    url: pageUrl,
    type: "article",
  },
  keywords: ["psychological vulnerability", "cognitive tolerance", "integration difficulties", "trauma triggers", "psychotic episodes", "grounding techniques", "set and setting", "psychological preparation"],
};

export default function WhenCanAlteredStatesBecomeDestabilizingPage() {
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
            When can altered states become destabilizing?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Altered states become destabilizing when they exceed cognitive tolerance limits, occur without proper preparation, or interact with existing psychological vulnerabilities.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Destabilization occurs because altered states temporarily disrupt normal neural processing patterns and executive function. This disruption can trigger latent psychological conditions, overwhelm coping mechanisms, or create lasting perceptual distortions. The brain's homeostatic systems may struggle to reintegrate these experiences, particularly when the altered state is intense, prolonged, or occurs in psychologically vulnerable individuals.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The threshold for destabilization varies significantly based on individual psychological resilience, experience level, environmental factors, and the specific method used to induce the altered state. Some people maintain stability through intense experiences while others become destabilized by mild alterations.
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
                href="/consciousness/altered-states/safety-and-risks/who-should-avoid-certain-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Who should avoid certain altered states?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/safety-and-risks/can-altered-states-worsen-mental-health-conditions"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states worsen mental health conditions?</span>
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