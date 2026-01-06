import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, Wand2, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/hills-alternate-states/imagination-via-emotion`;

export const metadata: Metadata = {
  title: "Imagination Stimulated by Emotion | Hill’s Altered States | Salars",
  description:
    "Imagination becomes an altered state when emotion energizes it: inner censorship drops, pattern synthesis increases, and ideas arrive with traction and urgency.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Imagination Stimulated by Emotion",
    description:
      "How emotion ignites imagination, why neutral fantasy doesn’t create output, and how to convert insight into action.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "imagination",
    "creativity",
    "emotion",
    "altered states",
    "Napoleon Hill",
    "intuition",
    "insight",
  ],
};

export default function ImaginationViaEmotionPage() {
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
              <Wand2 className="h-4 w-4 text-primary" />
              Creative ignition
            </div>
            <h1 className="text-4xl font-semibold tracking-tight text-foreground">
              Imagination Stimulated by Love, Sex, and Emotion
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Imagination is always available, but it’s not always powerful.
              Emotion is what gives imagination traction. When you care deeply,
              the mind synthesizes faster, inhibits less, and offers bolder
              combinations.
            </p>
          </header>

          {/* Core idea */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Core idea
            </p>
            <p className="text-foreground leading-relaxed">
              Emotion increases salience. Higher salience strengthens imagery,
              loosens internal censorship, and makes ideas feel “real enough” to
              act on—turning imagination from idle simulation into productive
              vision.
            </p>
          </section>

          {/* What changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              What changes in this state
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">
                  Pattern synthesis increases
                </strong>
                : distant memories and concepts combine into new structures.
              </li>
              <li>
                <strong className="text-foreground">Censorship decreases</strong>
                : fewer “don’t do that” thoughts interrupt exploration.
              </li>
              <li>
                <strong className="text-foreground">Future modeling sharpens</strong>
                : you can simulate strategies, scenes, and outcomes more vividly.
              </li>
            </ul>
          </section>

          {/* Using it */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Turning inspired imagination into results
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              The weakness of imagination is that it can feel complete without
              being real. The fix is to translate insight into the next small
              action.
            </p>
            <div className="rounded-xl border border-border bg-card/30 p-5 space-y-3">
              <p className="text-foreground font-semibold">
                A practical conversion loop
              </p>
              <ol className="list-decimal pl-6 text-muted-foreground space-y-2">
                <li>
                  Capture the idea fast (notes, voice memo, sketch).
                </li>
                <li>
                  Ask: “What would make this real in 48 hours?”
                </li>
                <li>
                  Create one artifact: an outline, a prototype, a draft, a
                  plan.
                </li>
                <li>
                  Schedule the next session before the emotion fades.
                </li>
              </ol>
            </div>
          </section>

          {/* Distortions */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Distortions & risks
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">Escapist fantasy</strong>:
                imagination becomes avoidance rather than creation.
              </li>
              <li>
                <strong className="text-foreground">Emotional flooding</strong>:
                too much intensity reduces clarity and follow-through.
              </li>
              <li>
                <strong className="text-foreground">Idea hoarding</strong>: you
                collect visions but don’t ship artifacts.
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
                href="/consciousness/altered-states/hills-alternate-states/love-romantic-connection"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Love & romantic connection (coherence and safety)
                </span>
              </Link>
              <Link
                href="/consciousness/altered-states/subjective-experience/can-altered-states-amplify-imagination"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Can altered states amplify imagination?
                </span>
              </Link>
              <Link
                href="/consciousness/integration/staying-functional"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">
                  Staying functional while processing big experiences
                </span>
              </Link>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

