import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, Sparkles } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/hills-alternate-states`;

export const metadata: Metadata = {
  title: "Hill’s Consciousness-Altering States | Altered States",
  description:
    "Napoleon Hill’s four emotion-driven states that reliably shift perception, motivation, and creative output: love, sexual transmutation, desire, and imagination stimulated by emotion.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Hill’s Consciousness-Altering States",
    description:
      "Four emotion-driven states that alter perception, motivation, and creativity: love, transmutation, desire, and imagination.",
    url: pageUrl,
    type: "website",
  },
  keywords: [
    "Napoleon Hill",
    "altered states",
    "love",
    "sexual transmutation",
    "desire",
    "imagination",
    "creativity",
    "motivation",
  ],
};

const hillStates = [
  {
    href: "/consciousness/altered-states/hills-alternate-states/love-romantic-connection",
    title: "Love & Romantic Connection",
    description:
      "How deep connection regulates the nervous system, expands time-horizon thinking, and unlocks creative coherence.",
  },
  {
    href: "/consciousness/altered-states/hills-alternate-states/sexual-transmutation",
    title: "Sexual Transmutation",
    description:
      "How to redirect arousal into focus, ambition, and sustained creation without suppression or compulsion.",
  },
  {
    href: "/consciousness/altered-states/hills-alternate-states/intense-desire-passion",
    title: "Intense Desire & Passion",
    description:
      "Why “white-hot desire” narrows attention, increases risk tolerance, and accelerates skill acquisition when directed well.",
  },
  {
    href: "/consciousness/altered-states/hills-alternate-states/imagination-via-emotion",
    title: "Imagination Stimulated by Emotion",
    description:
      "How emotion energizes imagination and reduces inner censorship—turning insight into usable vision and output.",
  },
];

export default function HillsAlternateStatesHubPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-4xl space-y-10">
          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Altered States
            </Link>
          </div>

          {/* Header */}
          <header className="space-y-3">
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card/40 px-3 py-1 text-sm text-muted-foreground">
              <Sparkles className="h-4 w-4 text-primary" />
              Emotional & motivational altered states
            </div>
            <h1 className="text-4xl font-semibold tracking-tight text-foreground">
              Hill’s Consciousness-Altering States
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Napoleon Hill described a set of emotion-driven states that can
              temporarily reorganize perception, motivation, and creative
              ability. These are not “mystical modes” so much as high-voltage
              configurations: when emotion and meaning align, attention becomes
              cleaner, and action becomes easier.
            </p>
          </header>

          {/* Quick map */}
          <section className="rounded-2xl border border-border bg-card/40 p-6 space-y-4">
            <h2 className="text-xl font-semibold text-foreground">
              The four states (a practical map)
            </h2>
            <div className="grid gap-4 md:grid-cols-2">
              {hillStates.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="group rounded-xl border border-border bg-card/30 p-5 transition-colors hover:bg-card/50"
                >
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                      {item.title}
                    </h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          </section>

          {/* How to use */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              How to use these pages
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Each page explains the state as a mechanism (what changes in
              attention, emotion, and behavior), then translates that into
              practical approaches: how to enter the state, how to keep it
              constructive, and how to avoid common distortions.
            </p>
          </section>

          {/* Cross-links */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related reading
            </h2>
            <div className="grid gap-3">
              <Link
                href="/consciousness/altered-states/safety-and-risks"
                className="rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <span className="text-foreground">
                  Safety, Risks & Stability for altered states
                </span>
              </Link>
              <Link
                href="/consciousness/integration"
                className="rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <span className="text-foreground">
                  Integration: turning experiences into behavior change
                </span>
              </Link>
              <Link
                href="/consciousness/meditation"
                className="rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <span className="text-foreground">
                  Meditation as training for attention and emotional regulation
                </span>
              </Link>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

