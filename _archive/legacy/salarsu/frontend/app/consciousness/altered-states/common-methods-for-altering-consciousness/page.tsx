import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/common-methods-for-altering-consciousness`;

type Method = {
  slug: string;
  name: string;
  oneLine: string;
  primaryMechanism: string;
  intensity: "Low" | "Moderate" | "High" | "Variable";
  risk: "Low" | "Moderate" | "High" | "Variable";
};

const methods: Method[] = [
  {
    slug: "breathwork",
    name: "Breathwork",
    oneLine:
      "Controlled breathing patterns that shift arousal, attention, and perception—sometimes rapidly.",
    primaryMechanism: "CO₂/O₂ balance + autonomic nervous system",
    intensity: "Variable",
    risk: "Moderate",
  },
  {
    slug: "meditation-and-mindfulness",
    name: "Meditation and Mindfulness",
    oneLine:
      "Attention training and awareness practices that reshape perception, time sense, and self-experience.",
    primaryMechanism: "Attention regulation + meta-awareness",
    intensity: "Variable",
    risk: "Low",
  },
  {
    slug: "sensory-deprivation",
    name: "Sensory Deprivation",
    oneLine:
      "Reducing external input (float tanks, darkness) so internal imagery and memory become louder.",
    primaryMechanism: "Reduced input → internal amplification",
    intensity: "Variable",
    risk: "Moderate",
  },
  {
    slug: "psychedelics-and-entheogens",
    name: "Psychedelics and Entheogens",
    oneLine:
      "Substances like psilocybin, LSD, or ayahuasca that can profoundly alter perception, emotion, and meaning.",
    primaryMechanism: "Serotonergic modulation + network reorganization",
    intensity: "High",
    risk: "High",
  },
  {
    slug: "fasting-and-sleep-deprivation",
    name: "Fasting and Sleep Deprivation",
    oneLine:
      "Deprivation-based methods that can trigger unusual thoughts, vivid imagery, and instability—used carefully in some traditions.",
    primaryMechanism: "Metabolic + circadian disruption",
    intensity: "High",
    risk: "High",
  },
  {
    slug: "sleep-dreams-and-hypnagogia",
    name: "Sleep, Dreams, and Hypnagogia",
    oneLine:
      "Natural altered states every night: REM dreams, lucid dreams, and the liminal hypnagogic transition.",
    primaryMechanism: "Sleep-stage neurobiology + imagery networks",
    intensity: "Variable",
    risk: "Low",
  },
  {
    slug: "rituals-and-chanting",
    name: "Rituals and Chanting",
    oneLine:
      "Rhythm, repetition, and synchrony (drumming, chanting, movement) that induce trance and group coherence.",
    primaryMechanism: "Rhythm + entrainment + social synchrony",
    intensity: "Moderate",
    risk: "Moderate",
  },
  {
    slug: "physical-extremes",
    name: "Physical Extremes",
    oneLine:
      "Cold/heat exposure or intense exertion that shifts neurochemistry and attention through stress and recovery.",
    primaryMechanism: "Stress response + endorphins/catecholamines",
    intensity: "High",
    risk: "Moderate",
  },
  {
    slug: "hypnosis-and-visualization",
    name: "Hypnosis and Visualization",
    oneLine:
      "Guided suggestion and vivid imagery that change perception, memory, and bodily sensation through focused attention.",
    primaryMechanism: "Focused attention + suggestibility",
    intensity: "Moderate",
    risk: "Low",
  },
  {
    slug: "art-music-and-creative-flow",
    name: "Art, Music, and Creative Flow",
    oneLine:
      "Deep creative absorption that changes time sense, self-consciousness, and the felt meaning of experience.",
    primaryMechanism: "Flow + absorption + emotion regulation",
    intensity: "Moderate",
    risk: "Low",
  },
];

export const metadata: Metadata = {
  title: "Common Methods for Altering Consciousness | Salars Consciousness",
  description:
    "A grounded overview of common ways humans alter consciousness—breathwork, meditation, sensory deprivation, psychedelics, deprivation, sleep states, ritual, physical extremes, hypnosis, and creative flow—plus safety framing and comparisons.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Common Methods for Altering Consciousness",
    description:
      "A grounded overview of common ways humans alter consciousness, with comparisons and safety framing.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "altered states",
    "consciousness",
    "breathwork",
    "meditation",
    "mindfulness",
    "sensory deprivation",
    "psychedelics",
    "fasting",
    "sleep deprivation",
    "hypnosis",
    "flow state",
    "ritual",
  ],
};

export default function CommonMethodsForAlteringConsciousnessPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12 max-w-6xl">
        <Link
          href="/consciousness/altered-states"
          className="text-primary hover:underline mb-6 inline-flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Altered States
        </Link>

        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-foreground">
          Common Methods for Altering Consciousness
        </h1>

        <p className="text-lg text-muted-foreground mb-10 max-w-3xl">
          “Altering consciousness” means shifting perception, attention, emotion,
          time sense, or sense of self away from ordinary waking experience. The
          methods below range from gentle training practices to intense, high-risk
          interventions. The goal here is clarity: what each method is, how it
          works, what people report, and what to watch out for.
        </p>

        <section className="mb-12 rounded-2xl border border-border bg-card/40 p-6">
          <h2 className="text-2xl font-semibold tracking-tight text-foreground mb-4">
            Quick Comparison
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-border">
              <thead>
                <tr className="bg-card">
                  <th className="border border-border p-3 text-left text-foreground">
                    Method
                  </th>
                  <th className="border border-border p-3 text-left text-foreground">
                    Primary Mechanism
                  </th>
                  <th className="border border-border p-3 text-left text-foreground">
                    Typical Intensity
                  </th>
                  <th className="border border-border p-3 text-left text-foreground">
                    Risk Level
                  </th>
                </tr>
              </thead>
              <tbody>
                {methods.map((method) => (
                  <tr key={method.slug}>
                    <td className="border border-border p-3">
                      <Link
                        href={`/consciousness/altered-states/common-methods-for-altering-consciousness/${method.slug}`}
                        className="text-primary hover:underline"
                      >
                        {method.name}
                      </Link>
                    </td>
                    <td className="border border-border p-3 text-foreground">
                      {method.primaryMechanism}
                    </td>
                    <td className="border border-border p-3 text-foreground">
                      {method.intensity}
                    </td>
                    <td className="border border-border p-3 text-foreground">
                      {method.risk}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            Risk level depends on context, dose/intensity, supervision, medical
            history, and mental health. For a safety-first overview, start with{" "}
            <Link
              href="/consciousness/altered-states/safety-and-risks"
              className="text-primary hover:underline"
            >
              Safety, Risks &amp; Stability
            </Link>
            .
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold tracking-tight text-foreground mb-6">
            Methods (Detailed Pages)
          </h2>
          <div className="grid gap-4 md:grid-cols-2">
            {methods.map((method) => (
              <Link
                key={method.slug}
                href={`/consciousness/altered-states/common-methods-for-altering-consciousness/${method.slug}`}
                className="group rounded-xl border border-border bg-card/30 p-6 transition-colors hover:bg-card/50"
              >
                <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                  {method.name}
                </h3>
                <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                  {method.oneLine}
                </p>
              </Link>
            ))}
          </div>
        </section>

        <section className="rounded-2xl border border-border bg-card/40 p-6">
          <h2 className="text-xl font-semibold text-foreground mb-3">
            How to Use This Hub
          </h2>
          <div className="space-y-3 text-muted-foreground leading-relaxed">
            <p>
              If you want a calm, low-risk entry point, start with{" "}
              <Link
                href="/consciousness/altered-states/common-methods-for-altering-consciousness/meditation-and-mindfulness"
                className="text-primary hover:underline"
              >
                meditation and mindfulness
              </Link>{" "}
              or{" "}
              <Link
                href="/consciousness/altered-states/common-methods-for-altering-consciousness/hypnosis-and-visualization"
                className="text-primary hover:underline"
              >
                hypnosis and visualization
              </Link>
              .
            </p>
            <p>
              If you want a natural, nightly altered-state map, see{" "}
              <Link
                href="/consciousness/sleep-dreams"
                className="text-primary hover:underline"
              >
                Sleep &amp; Dreams
              </Link>{" "}
              and the{" "}
              <Link
                href="/consciousness/altered-states/common-methods-for-altering-consciousness/sleep-dreams-and-hypnagogia"
                className="text-primary hover:underline"
              >
                sleep states page
              </Link>
              .
            </p>
            <p>
              If you’re comparing intense methods (deprivation, physical extremes,
              psychedelics), read the safety framing first and treat integration
              as part of the method—not an optional add-on.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}

