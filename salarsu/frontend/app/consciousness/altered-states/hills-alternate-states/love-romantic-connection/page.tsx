import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, Heart, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/hills-alternate-states/love-romantic-connection`;

export const metadata: Metadata = {
  title: "Love & Romantic Connection as an Altered State | Salars",
  description:
    "Love and romantic connection can function as a consciousness-altering state: regulating the nervous system, expanding perception, and increasing creative coherence when it’s stable and secure.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Love & Romantic Connection as an Altered State",
    description:
      "How stable connection shifts attention, perception, and creative output—and how to avoid obsession and dependency.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "love",
    "romance",
    "attachment",
    "altered states",
    "creativity",
    "motivation",
    "Napoleon Hill",
  ],
};

export default function LoveRomanticConnectionPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-10">
          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states/hills-alternate-states"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Hill’s states
            </Link>
          </div>

          {/* Header */}
          <header className="space-y-3">
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card/40 px-3 py-1 text-sm text-muted-foreground">
              <Heart className="h-4 w-4 text-primary" />
              Emotional coherence
            </div>
            <h1 className="text-4xl font-semibold tracking-tight text-foreground">
              Love & Romantic Connection as a Consciousness-Altering State
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Love isn’t only a feeling. At its best, it’s a stable pattern of
              attention: the nervous system relaxes, threat-scanning decreases,
              and the mind begins to think in longer arcs. That shift changes
              what you notice, what you believe is possible, and what you can
              sustain.
            </p>
          </header>

          {/* Short answer */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Core idea
            </p>
            <p className="text-foreground leading-relaxed">
              Secure love tends to widen perception and increase coherence: it
              reduces internal friction, makes emotion easier to regulate, and
              frees attention for creativity, meaning-making, and effort that
              compounds over time.
            </p>
          </section>

          {/* Definition */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              What “love” means here (not sentimentality)
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              In consciousness terms, love is a high-trust relational state: you
              feel safe enough to be honest, to build, and to take risks that
              would otherwise trigger avoidance. It’s different from:
            </p>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">Infatuation</strong>: high
                dopamine novelty with unstable valuation.
              </li>
              <li>
                <strong className="text-foreground">Attachment panic</strong>:
                fear-based bonding that narrows your world.
              </li>
              <li>
                <strong className="text-foreground">Dependency</strong>: “I need
                you so I can function,” which tends to collapse autonomy.
              </li>
            </ul>
          </section>

          {/* Mechanism */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why love reliably alters consciousness
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              When connection feels stable, the brain can reduce vigilance.
              Attention becomes less fragmented, and you regain bandwidth for
              pattern recognition, creativity, and future planning. Practically,
              that looks like:
            </p>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">Emotional regulation</strong>{" "}
                becomes easier; recovery is faster after stress.
              </li>
              <li>
                <strong className="text-foreground">Time horizon expands</strong>
                ; you naturally think in months/years instead of hours/days.
              </li>
              <li>
                <strong className="text-foreground">
                  Meaning-making increases
                </strong>
                ; effort feels worth it.
              </li>
              <li>
                <strong className="text-foreground">Social cognition</strong> is
                sharpened; you read nuance and intent more clearly.
              </li>
            </ul>
          </section>

          {/* Practical applications */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Practical applications (using love as fuel, not distraction)
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Love becomes an amplifier when it increases clarity and stability
              rather than drama. A useful rule: the more grounded the
              relationship, the more usable the energy.
            </p>
            <div className="rounded-xl border border-border bg-card/30 p-5 space-y-3">
              <p className="text-foreground font-semibold">
                A simple way to harness it
              </p>
              <ol className="list-decimal pl-6 text-muted-foreground space-y-2">
                <li>
                  Identify a project that benefits from long-term persistence.
                </li>
                <li>
                  Use connection as regulation: calm first, then build.
                </li>
                <li>
                  Convert emotion into a concrete commitment (a schedule, a
                  deliverable, a standard).
                </li>
                <li>
                  Protect the relationship from the project (and the project
                  from the relationship) with clear boundaries.
                </li>
              </ol>
            </div>
          </section>

          {/* Distortions */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Failure modes & distortions
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The same intensity that can expand consciousness can also narrow
              it when fear takes over. Common distortions:
            </p>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">Obsession</strong>: attention
                becomes compulsive and repetitive instead of creative.
              </li>
              <li>
                <strong className="text-foreground">Idealization</strong>:
                ignoring reality signals and over-investing in fantasy.
              </li>
              <li>
                <strong className="text-foreground">Emotional volatility</strong>
                : the relationship becomes a dopamine rollercoaster.
              </li>
              <li>
                <strong className="text-foreground">
                  Creative collapse under threat
                </strong>
                : when security drops, output drops with it.
              </li>
            </ul>
          </section>

          {/* Integration & links */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related pages
            </h2>
            <div className="grid gap-3">
              <Link
                href="/consciousness/altered-states/safety-and-risks"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Safety, Risks & Stability for altered states
                </span>
              </Link>
              <Link
                href="/consciousness/integration"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Integration: turning insight into behavior
                </span>
              </Link>
              <Link
                href="/consciousness/altered-states/hills-alternate-states/intense-desire-passion"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Intense desire & passion as a cognitive amplifier
                </span>
              </Link>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

