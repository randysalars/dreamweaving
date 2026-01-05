import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/cultural-historical/were-altered-states-used-in-ritual-or-initiation`;

export const metadata: Metadata = {
  title: "Were altered states used in ritual or initiation? | Salars Consciousness",
  description: "Most traditional cultures incorporated altered states into rituals and initiations through psychoactive plants, rhythmic practices, fasting, and sensory ma",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Were altered states used in ritual or initiation?",
    description: "Most traditional cultures incorporated altered states into rituals and initiations through psychoactive plants, rhythmic practices, fasting, and sensory ma",
    url: pageUrl,
    type: "article",
  },
  keywords: ["shamanism", "vision quest", "psychoactive plants", "ritual transformation", "initiation ceremonies", "spiritual practices", "consciousness alteration", "traditional medicine"],
};

export default function WereAlteredStatesUsedInRitualOrInitiationPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/cultural-historical"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Cultural & Historical Perspectives
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Were altered states used in ritual or initiation?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Most traditional cultures incorporated altered states into rituals and initiations through psychoactive plants, rhythmic practices, fasting, and sensory manipulation to facilitate spiritual transformation and social transitions.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Altered states served crucial functions in traditional societies because they provided direct experiential access to spiritual realms and facilitated psychological transformation during major life transitions. The neurological changes induced by these practices resulted in profound shifts in identity, worldview, and social bonding that reinforced cultural values and group cohesion. These experiences demonstrated the malleable nature of consciousness and created shared meaning systems that unified communities around common spiritual beliefs.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The specific methods and contexts vary dramatically across cultures, from ayahuasca ceremonies in the Amazon to vision quests among Plains tribes. Some traditions rely primarily on plant medicines while others use purely behavioral techniques like meditation, chanting, or extreme physical practices.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/altered-states/cultural-historical/how-have-altered-states-been-viewed-historically"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How have altered states been viewed historically?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/cultural-historical/how-did-ancient-cultures-interpret-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How did ancient cultures interpret altered states?</span>
              </Link>
              
              <Link
                href="/consciousness/altered-states/cultural-historical/how-do-spiritual-traditions-describe-altered-states"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do spiritual traditions describe altered states?</span>
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
              href="/consciousness/altered-states/cultural-historical"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Cultural & Historical Perspectives questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}