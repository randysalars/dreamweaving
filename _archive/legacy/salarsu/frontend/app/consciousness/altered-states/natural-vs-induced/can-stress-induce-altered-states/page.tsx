import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/natural-vs-induced/can-stress-induce-altered-states`;

export const metadata: Metadata = {
  title: "Can stress induce altered states? | Salars Consciousness",
  description: "Stress can induce altered states of consciousness through cortisol release, adrenaline surges, and hypervigilance that change perception, time awareness, a",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Can stress induce altered states?",
    description: "Stress can induce altered states of consciousness through cortisol release, adrenaline surges, and hypervigilance that change perception, time awareness, a",
    url: pageUrl,
    type: "article",
  },
  keywords: ["dissociation", "hypervigilance", "cortisol", "fight-or-flight", "depersonalization", "time distortion", "trauma response", "stress hormones"],
};

export default function CanStressInduceAlteredStatesPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/natural-vs-induced"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Natural vs Induced Altered States
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Can stress induce altered states?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Stress can induce altered states of consciousness through cortisol release, adrenaline surges, and hypervigilance that change perception, time awareness, and cognitive processing.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Chronic or acute stress triggers the hypothalamic-pituitary-adrenal axis, flooding the brain with cortisol and catecholamines that alter neurotransmitter balance. This biochemical cascade results in dissociation, tunnel vision, time distortion, and heightened sensory processing. These stress-induced states demonstrate how the nervous system's survival mechanisms naturally shift consciousness to prioritize threat detection over normal cognitive function.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The intensity and type of altered state depends on stress duration, individual stress tolerance, and whether the stressor is physical or psychological. Some people experience depersonalization under mild stress, while others require severe trauma to trigger noticeable consciousness shifts.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/natural-vs-induced/what-are-natural-altered-states-of-consciousness"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are natural altered states of consciousness?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/natural-vs-induced/what-causes-natural-altered-states-to-occur"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What causes natural altered states to occur?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/natural-vs-induced/what-are-induced-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What are induced altered states?</span>
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
              href="/consciousness/altered-states/natural-vs-induced"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Natural vs Induced Altered States questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}