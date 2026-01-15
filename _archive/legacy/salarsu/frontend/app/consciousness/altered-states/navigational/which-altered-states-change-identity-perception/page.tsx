import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/navigational/which-altered-states-change-identity-perception`;

export const metadata: Metadata = {
  title: "Which altered states change identity perception? | Salars Consciousness",
  description: "Psychedelic experiences, dissociative states, deep meditation, ego dissolution episodes, and certain mystical experiences fundamentally alter how individua",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Which altered states change identity perception?",
    description: "Psychedelic experiences, dissociative states, deep meditation, ego dissolution episodes, and certain mystical experiences fundamentally alter how individua",
    url: pageUrl,
    type: "article",
  },
  keywords: ["ego dissolution", "self-dissolution", "mystical experiences", "default mode network", "dissociative states", "depersonalization", "transpersonal experiences", "unity consciousness"],
};

export default function WhichAlteredStatesChangeIdentityPerceptionPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/navigational"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Navigational & Exploratory Prompts
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Which altered states change identity perception?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Psychedelic experiences, dissociative states, deep meditation, ego dissolution episodes, and certain mystical experiences fundamentally alter how individuals perceive their sense of self and personal boundaries.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              These states disrupt the default mode network in the brain, which normally maintains our sense of continuous selfhood and personal narrative. The disruption occurs because altered states reduce activity in brain regions responsible for self-referential thinking, leading to experiences where the boundary between self and environment dissolves. This demonstrates that identity perception is a constructed neural process rather than a fixed feature of consciousness.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The intensity of identity shifts varies significantly based on the depth of the altered state, individual brain chemistry, and environmental context. Some states produce subtle shifts in self-perception while others can temporarily eliminate the sense of being a separate individual entirely.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/navigational/which-altered-states-occur-most-commonly"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Which altered states occur most commonly?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/navigational/which-altered-states-are-easiest-to-access"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Which altered states are easiest to access?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/navigational/which-altered-states-are-hardest-to-describe"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Which altered states are hardest to describe?</span>
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
              href="/consciousness/altered-states/navigational"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Navigational & Exploratory Prompts questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}