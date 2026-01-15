import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/common-methods-for-altering-consciousness/physical-extremes`;

export const metadata: Metadata = {
  title: "Physical Extremes: How They Alter Consciousness | Salars Consciousness",
  description:
    "Physical extremes—intense exercise, heat, cold exposure—alter consciousness through stress physiology, neurochemicals, and attention narrowing. They can produce clarity and euphoria but require safety boundaries.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Physical Extremes: How They Alter Consciousness",
    description:
      "How heat, cold, and exertion change perception and mood—plus risks and best practices.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "physical extremes",
    "cold exposure",
    "heat exposure",
    "sauna",
    "endurance exercise",
    "runner's high",
    "altered states",
  ],
};

export default function PhysicalExtremesMethodPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-10">
          <Link
            href="/consciousness/altered-states/common-methods-for-altering-consciousness"
            className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Common Methods
          </Link>

          <header className="space-y-3">
            <h1 className="text-4xl font-semibold tracking-tight text-foreground">
              Physical Extremes: How They Alter Consciousness
            </h1>
            <p className="text-muted-foreground leading-relaxed">
              Physical extremes—intense exertion, heat exposure, and cold
              exposure—alter consciousness by stressing the body and forcing
              attention into the present. They can produce clarity, euphoria, and
              a narrowed, “quiet” mind, but the state change is powered by stress
              response and recovery, so safety matters.
            </p>
          </header>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              What This Method Is
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Physical extremes include endurance exercise, sweat lodges/sauna,
              cold plunges, breath-led cold exposure, and other practices where
              the body is pushed beyond comfort in a controlled way.
            </p>
            <p className="text-muted-foreground leading-relaxed">
              What it is not: proof of spiritual attainment. The altered state is
              a predictable consequence of physiology, attention, and meaning
              framing.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              How Physical Extremes Alter Consciousness
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">Stress response:</strong>{" "}
                catecholamines (adrenaline/noradrenaline) increase alertness and
                narrow attention.
              </li>
              <li>
                <strong className="text-foreground">Endorphins/endocannabinoids:</strong>{" "}
                sustained effort can produce analgesia and mood elevation.
              </li>
              <li>
                <strong className="text-foreground">Breath and focus:</strong>{" "}
                coping strategies (breath control, self-talk) become the dominant
                mental content.
              </li>
              <li>
                <strong className="text-foreground">Aftereffect:</strong> post
                stress recovery can feel like deep calm and clarity.
              </li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Typical Experiences Reported
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Euphoria and mood lift (“runner’s high”).</li>
              <li>Reduced rumination and heightened present-moment focus.</li>
              <li>Time distortion during sustained effort.</li>
              <li>Sense of resilience or confidence after completion.</li>
              <li>Occasionally: panic, dizziness, or overwhelm if pushed too hard.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Historical &amp; Cultural Use
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Many cultures use heat, cold, and endurance challenges as rite-of-passage
              tools. In modern contexts, these methods show up as athletics,
              recovery traditions (sauna, cold plunge), and structured stress
              inoculation practices.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Scientific &amp; Psychological Evidence
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Exercise is strongly supported for mood, cognition, and stress
              resilience. Heat and cold exposure have emerging evidence for
              certain health and mood effects, but protocols and safety vary.
              The altered-state experience is consistent with known stress and
              reward biology.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Risks, Limits, and Misuse
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Heat illness and cold shock are real risks; dose exposure conservatively.</li>
              <li>Cardiovascular conditions require medical guidance.</li>
              <li>Avoid “hero mode” escalation; repeated extremes without recovery increases injury risk.</li>
              <li>Never combine extremes with intoxication.</li>
            </ul>
            <p className="text-sm text-muted-foreground">
              Safety framing:{" "}
              <Link
                href="/consciousness/altered-states/safety-and-risks"
                className="text-primary hover:underline"
              >
                Safety, Risks &amp; Stability
              </Link>
              .
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Comparison to Other Methods
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                Like{" "}
                <Link
                  href="/consciousness/altered-states/common-methods-for-altering-consciousness/breathwork"
                  className="text-primary hover:underline"
                >
                  breathwork
                </Link>
                , physical extremes can rapidly shift arousal through physiology.
              </li>
              <li>
                Like{" "}
                <Link
                  href="/consciousness/altered-states/common-methods-for-altering-consciousness/fasting-and-sleep-deprivation"
                  className="text-primary hover:underline"
                >
                  deprivation-based methods
                </Link>
                , they rely on stress and compensation (but can be safer with
                proper dosing and recovery).
              </li>
              <li>
                Compared with{" "}
                <Link
                  href="/consciousness/altered-states/common-methods-for-altering-consciousness/meditation-and-mindfulness"
                  className="text-primary hover:underline"
                >
                  meditation
                </Link>
                , extremes are higher intensity and less precise, but can be
                compelling for people who benefit from embodied focus.
              </li>
              <li>
                Hub:{" "}
                <Link
                  href="/consciousness/altered-states/common-methods-for-altering-consciousness"
                  className="text-primary hover:underline"
                >
                  Common Methods for Altering Consciousness
                </Link>
                .
              </li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              When Physical Extremes Are Most Useful
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Breaking mental stagnation via embodied challenge.</li>
              <li>Stress inoculation and resilience training (conservatively).</li>
              <li>Improving mood and focus through exercise consistency.</li>
              <li>Clearing rumination by forcing present-moment attention.</li>
            </ul>
          </section>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <h2 className="text-xl font-semibold text-foreground mb-3">
              Key Takeaways
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Extremes alter consciousness through stress physiology and attention narrowing.</li>
              <li>They can produce euphoria and clarity but require conservative dosing.</li>
              <li>Recovery and safety are part of the method.</li>
              <li>They pair well with breath and mindfulness as stabilizers.</li>
              <li>Don’t escalate intensity as a proxy for meaning.</li>
            </ul>
          </section>
        </div>
      </main>
    </div>
  );
}

