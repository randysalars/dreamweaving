import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/navigational/which-altered-states-feel-most-meaningful`;

export const metadata: Metadata = {
  title: "Which altered states feel most meaningful? | Salars Consciousness",
  description: "Deep meditative states, psychedelic experiences, and flow states rank highest for reported meaningfulness because they involve dissolution of ego boundarie",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Which altered states feel most meaningful?",
    description: "Deep meditative states, psychedelic experiences, and flow states rank highest for reported meaningfulness because they involve dissolution of ego boundarie",
    url: pageUrl,
    type: "article",
  },
  keywords: ["mystical experiences", "flow states", "psychedelic therapy", "meditation depth", "ego dissolution", "default mode network", "transpersonal psychology", "peak experiences"],
};

export default function WhichAlteredStatesFeelMostMeaningfulPage() {
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
            Which altered states feel most meaningful?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Deep meditative states, psychedelic experiences, and flow states rank highest for reported meaningfulness because they involve dissolution of ego boundaries and enhanced pattern recognition.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              These states activate the default mode network differently than ordinary consciousness, reducing self-referential thinking while increasing connectivity between brain regions that normally operate independently. This leads to experiences of unity, interconnectedness, and profound insight that participants consistently rate as among the most meaningful events of their lives. The combination of reduced ego activity and enhanced neural integration creates conditions where new perspectives and emotional breakthroughs can emerge.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Meaningfulness varies significantly based on set, setting, personal history, and integration practices afterward. Some individuals find certain states distressing rather than meaningful, particularly without proper preparation or support.
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