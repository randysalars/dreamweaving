import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, Target, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/hills-alternate-states/intense-desire-passion`;

export const metadata: Metadata = {
  title: "Intense Desire & Passion | Hill’s Altered States | Salars",
  description:
    "Intense desire and passion can act as a cognitive amplifier: narrowing attention, increasing risk tolerance, and accelerating learning when the target is clear and the energy is structured.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Intense Desire & Passion as a Cognitive Amplifier",
    description:
      "How desire changes attention and behavior—and how to prevent burnout, obsession, and urgency addiction.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "desire",
    "passion",
    "motivation",
    "Napoleon Hill",
    "altered states",
    "focus",
    "goal pursuit",
  ],
};

export default function IntenseDesirePassionPage() {
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
              <Target className="h-4 w-4 text-primary" />
              Goal gravity
            </div>
            <h1 className="text-4xl font-semibold tracking-tight text-foreground">
              Intense Desire & Passion as a Cognitive Amplifier
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Hill treated desire as the starting point of achievement because
              it reconfigures attention. In this state, the mind becomes
              “narrow and loud” in a useful way: you notice opportunities,
              tolerate discomfort, and persist longer than you normally would.
            </p>
          </header>

          {/* Core idea */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Core idea
            </p>
            <p className="text-foreground leading-relaxed">
              Desire becomes an altered state when it reorganizes your
              priorities so strongly that action feels inevitable—provided the
              desire is directed and structured rather than scattered.
            </p>
          </section>

          {/* Definition */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Desire vs neediness vs obsession
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The quality of desire matters. A quick diagnostic:
            </p>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">Directed desire</strong>:
                energizes you and clarifies options.
              </li>
              <li>
                <strong className="text-foreground">Neediness</strong>: creates
                urgency and collapses self-respect.
              </li>
              <li>
                <strong className="text-foreground">Obsession</strong>: loops
                attention without producing progress.
              </li>
            </ul>
          </section>

          {/* Mechanism */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              What changes in the mind
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              In the passion state, attention is biased toward anything that
              supports the aim. That bias can be productive:
            </p>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">
                  Signal amplification
                </strong>
                : you spot resources, mentors, and patterns that were “invisible”
                before.
              </li>
              <li>
                <strong className="text-foreground">
                  Higher discomfort tolerance
                </strong>
                : effort feels meaningful, so resistance decreases.
              </li>
              <li>
                <strong className="text-foreground">Faster learning</strong>:
                you train more, iterate more, and notice feedback more quickly.
              </li>
            </ul>
          </section>

          {/* Direction */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              The power of direction (desire + structure)
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Desire without structure burns out. Structure without desire is
              brittle. Combine them by turning emotion into constraints:
            </p>
            <div className="rounded-xl border border-border bg-card/30 p-5 space-y-3">
              <ul className="list-disc pl-6 text-muted-foreground space-y-2">
                <li>
                  Define a target you can measure weekly (not someday).
                </li>
                <li>
                  Create a daily “minimum effective dose” you can keep even on
                  bad days.
                </li>
                <li>
                  Track a single lead indicator (hours practiced, reps shipped,
                  sessions completed).
                </li>
              </ul>
            </div>
          </section>

          {/* Failure modes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Failure modes (how passion goes sideways)
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">Urgency addiction</strong>:
                you start chasing intensity instead of results.
              </li>
              <li>
                <strong className="text-foreground">Overcommitment</strong>:
                you outrun recovery and lose consistency.
              </li>
              <li>
                <strong className="text-foreground">Identity fusion</strong>:
                setbacks feel like threats to the self, not feedback.
              </li>
            </ul>
          </section>

          {/* Related */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related pages
            </h2>
            <div className="grid gap-3">
              <Link
                href="/consciousness/altered-states/hills-alternate-states/imagination-via-emotion"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Imagination stimulated by emotion (insight from intensity)
                </span>
              </Link>
              <Link
                href="/consciousness/altered-states/hills-alternate-states/sexual-transmutation"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Sexual transmutation (routing intensity into output)
                </span>
              </Link>
              <Link
                href="/consciousness/integration/integration-mistakes"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Integration mistakes that waste powerful states
                </span>
              </Link>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

