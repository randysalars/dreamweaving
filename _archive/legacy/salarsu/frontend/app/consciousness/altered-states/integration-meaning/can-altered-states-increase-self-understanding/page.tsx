import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/integration-meaning/can-altered-states-increase-self-understanding`;

export const metadata: Metadata = {
  title: "Can altered states increase self-understanding? | Salars Consciousness",
  description: "Altered states can enhance self-understanding by reducing default mental patterns, increasing introspective awareness, and providing novel perspectives on ",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Can altered states increase self-understanding?",
    description: "Altered states can enhance self-understanding by reducing default mental patterns, increasing introspective awareness, and providing novel perspectives on ",
    url: pageUrl,
    type: "article",
  },
  keywords: ["default mode network", "introspection", "neuroplasticity", "self-reflection", "integration practices", "perspective shifts", "psychological insights", "consciousness expansion"],
};

export default function CanAlteredStatesIncreaseSelfUnderstandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/integration-meaning"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Integration, Meaning & Daily Life
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Can altered states increase self-understanding?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Altered states can enhance self-understanding by reducing default mental patterns, increasing introspective awareness, and providing novel perspectives on habitual thoughts and behaviors.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Altered states temporarily suppress the brain's default mode network, which normally maintains rigid self-narratives and automatic thinking patterns. This suppression allows access to suppressed memories, emotions, and perspectives that are typically filtered out by ordinary consciousness. The heightened neuroplasticity during these states enables new neural connections to form, leading to fresh insights about personal motivations, relationships, and life patterns.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The depth of insight depends on the intensity and type of altered state, individual psychological readiness, and integration practices afterward. Some people experience profound revelations while others gain only temporary perspective shifts that fade without proper integration work.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/integration-meaning/what-does-it-mean-to-integrate-an-altered-state"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What does it mean to integrate an altered state?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/integration-meaning/why-is-integration-important-after-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Why is integration important after altered states?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/integration-meaning/can-altered-states-change-worldview"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Can altered states change worldview?</span>
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
              href="/consciousness/altered-states/integration-meaning"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Integration, Meaning & Daily Life questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}