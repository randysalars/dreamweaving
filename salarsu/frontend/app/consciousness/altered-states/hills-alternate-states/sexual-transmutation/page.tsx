import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, Flame, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/hills-alternate-states/sexual-transmutation`;

export const metadata: Metadata = {
  title: "Sexual Transmutation | Hill’s Altered States | Salars",
  description:
    "Sexual transmutation reframes arousal as usable energy: converting intensity into attention, focus, and long-arc creation without suppression or compulsion.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Sexual Transmutation",
    description:
      "How to redirect arousal into focus and creation—plus common failure modes like suppression, compulsion, and ego inflation.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "sexual transmutation",
    "Napoleon Hill",
    "altered states",
    "focus",
    "motivation",
    "discipline",
    "creativity",
  ],
};

export default function SexualTransmutationPage() {
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
              <Flame className="h-4 w-4 text-primary" />
              Channeling intensity
            </div>
            <h1 className="text-4xl font-semibold tracking-tight text-foreground">
              Sexual Transmutation: Channeling Life Force into Focus and Creation
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Hill used the term “sexual transmutation” to describe a functional
              conversion: strong biological intensity becomes usable mental
              energy. The point isn’t denial. It’s redirection—turning heat into
              output.
            </p>
          </header>

          {/* Core idea */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Core idea
            </p>
            <p className="text-foreground leading-relaxed">
              Sexual transmutation is the skill of converting arousal into
              sustained attention: instead of dissipating the energy (or
              suppressing it), you route it into work, learning, training, and
              creative expression.
            </p>
          </section>

          {/* Definition */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              What it is (and what it is not)
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The useful distinction is between three modes:
            </p>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">Indulgence</strong>: spend
                the energy on the shortest available outlet.
              </li>
              <li>
                <strong className="text-foreground">Suppression</strong>: clamp
                down with shame or rigidity (often unstable long-term).
              </li>
              <li>
                <strong className="text-foreground">Redirection</strong>: keep
                the intensity, change the target.
              </li>
            </ul>
          </section>

          {/* Mechanism */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              The mechanism: intensity → attention → output
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Arousal is one of the strongest attention magnets humans have. If
              you can hold steady in that charge without collapsing into
              compulsion, you gain:
            </p>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">More drive</strong> (you
                feel “pulled” toward creation).
              </li>
              <li>
                <strong className="text-foreground">More focus</strong> (fewer
                distractions feel interesting).
              </li>
              <li>
                <strong className="text-foreground">More stamina</strong>{" "}
                (effort feels less costly).
              </li>
              <li>
                <strong className="text-foreground">More confidence</strong>{" "}
                (clearer agency, reduced hesitation).
              </li>
            </ul>
          </section>

          {/* Practical use */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              A practical protocol (simple, repeatable)
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The goal is not perfection; it’s repeatable routing. Try this:
            </p>
            <div className="rounded-xl border border-border bg-card/30 p-5 space-y-3">
              <ol className="list-decimal pl-6 text-muted-foreground space-y-2">
                <li>
                  Notice the charge without narrating it: “intensity is
                  present.”
                </li>
                <li>
                  Pick a channel that benefits from energy: writing, building,
                  training, studying.
                </li>
                <li>
                  Use a short on-ramp (5–10 minutes): walking, breath pacing, or
                  light movement to stabilize arousal as attention.
                </li>
                <li>
                  Start a concrete task with visible progress within 15
                  minutes.
                </li>
                <li>
                  End with a clean stop: save, summarize next steps, and leave
                  the task “open” for the next session.
                </li>
              </ol>
            </div>
          </section>

          {/* Risks */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Risks & misuse (what breaks it)
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">Ascetic rigidity</strong>:
                suppression masquerading as discipline can backfire into
                rumination or binge behavior.
              </li>
              <li>
                <strong className="text-foreground">Compulsion loops</strong>:
                chasing release can reduce baseline motivation and focus.
              </li>
              <li>
                <strong className="text-foreground">Ego inflation</strong>:
                feeling energized can turn into impulsive overconfidence.
              </li>
            </ul>
            <p className="text-muted-foreground leading-relaxed">
              If sexuality is tied to trauma, compulsive behavior, or distress,
              treat this as a stability-first domain and consider professional
              support.
            </p>
          </section>

          {/* Related */}
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
                href="/consciousness/altered-states/hills-alternate-states/intense-desire-passion"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Intense desire & passion (direction turns heat into momentum)
                </span>
              </Link>
              <Link
                href="/consciousness/meditation"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Meditation (training attention so intensity becomes usable)
                </span>
              </Link>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

