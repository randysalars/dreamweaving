import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/safety-and-risks/can-altered-states-worsen-mental-health-conditions`;

export const metadata: Metadata = {
  title: "Can altered states worsen mental health conditions? | Salars Consciousness",
  description: "Yes, altered states can worsen existing mental health conditions by destabilizing psychological defenses, triggering episodes, and intensifying symptoms in",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Can altered states worsen mental health conditions?",
    description: "Yes, altered states can worsen existing mental health conditions by destabilizing psychological defenses, triggering episodes, and intensifying symptoms in",
    url: pageUrl,
    type: "article",
  },
  keywords: ["psychotic episodes", "bipolar triggers", "PTSD flashbacks", "psychiatric medication interactions", "mental health screening", "psychological stability", "neurochemical disruption", "contraindications"],
};

export default function CanAlteredStatesWorsenMentalHealthConditionsPage() {
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
            Can altered states worsen mental health conditions?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Yes, altered states can worsen existing mental health conditions by destabilizing psychological defenses, triggering episodes, and intensifying symptoms in vulnerable individuals.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Altered states temporarily disrupt normal cognitive filters and emotional regulation mechanisms that help manage psychiatric symptoms. This disruption can trigger psychotic episodes in those with schizophrenia, intensify manic episodes in bipolar disorder, or activate trauma responses in PTSD. The brain's altered neurochemistry during these states can overwhelm already compromised mental health systems, because conditions like depression and anxiety often involve dysregulated neurotransmitter pathways that altered states further destabilize.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Risk varies significantly based on the specific condition, its current stability, the type and intensity of altered state, and individual neurochemistry. Some individuals with well-managed conditions may experience minimal impact, while others in acute phases face substantial risk.
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