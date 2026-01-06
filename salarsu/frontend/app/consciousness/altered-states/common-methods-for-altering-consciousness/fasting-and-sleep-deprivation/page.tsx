import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/common-methods-for-altering-consciousness/fasting-and-sleep-deprivation`;

export const metadata: Metadata = {
  title: "Fasting and Sleep Deprivation: How They Alter Consciousness | Salars Consciousness",
  description:
    "Fasting and sleep deprivation alter consciousness by stressing metabolism and circadian systems. They can produce vivid imagery and unusual thought patterns but carry significant risks and are not recommended as casual methods.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Fasting and Sleep Deprivation: How They Alter Consciousness",
    description:
      "Mechanisms, reported effects, and clear safety boundaries for deprivation-based altered states.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "fasting",
    "sleep deprivation",
    "altered states",
    "ketosis",
    "circadian rhythm",
    "hallucinations",
  ],
};

export default function FastingAndSleepDeprivationMethodPage() {
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
              Fasting and Sleep Deprivation: How They Alter Consciousness
            </h1>
            <p className="text-muted-foreground leading-relaxed">
              Deprivation alters consciousness by removing basic stabilizers:
              calories and sleep. When energy supply, hormones, and circadian
              timing are disrupted, attention, emotion, and perception can become
              unusually fluid—sometimes producing visions or intense meaning—but
              also confusion, irritability, and cognitive impairment.
            </p>
          </header>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              What This Method Is
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Fasting is intentional restriction of food intake for a set period.
              Sleep deprivation is intentional or unintentional restriction of
              sleep. Both have been used in some spiritual traditions and
              endurance contexts, but both also degrade cognition and can worsen
              mental health when done without structure or screening.
            </p>
            <p className="text-muted-foreground leading-relaxed">
              What this method is not: a safe default. Most people seeking altered
              states for insight are better served by methods that do not damage
              sleep or metabolic stability.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              How Deprivation Alters Consciousness
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">Metabolic shifts:</strong>{" "}
                fasting can change glucose availability and increase ketone use,
                affecting energy and arousal.
              </li>
              <li>
                <strong className="text-foreground">Hormonal changes:</strong>{" "}
                cortisol, ghrelin, leptin, and other signals shift, affecting
                mood, focus, and impulse control.
              </li>
              <li>
                <strong className="text-foreground">Circadian disruption:</strong>{" "}
                sleep loss impairs prefrontal regulation and increases emotional
                volatility.
              </li>
              <li>
                <strong className="text-foreground">Perceptual instability:</strong>{" "}
                prolonged sleep deprivation can produce hallucination-like
                experiences and derealization.
              </li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Typical Experiences Reported
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Heightened sensitivity to sound, light, or emotion.</li>
              <li>Unusual thought patterns, racing associations, or “meaning load.”</li>
              <li>Vivid imagery or dreamlike perception (especially with sleep loss).</li>
              <li>Disorientation, irritability, and reduced impulse control.</li>
              <li>In fasting: periods of clarity alternating with fatigue.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Historical &amp; Cultural Use
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Many traditions include fasting or vigil as part of initiation,
              purification, mourning, or prayer. These practices are typically
              embedded in community structure and meaning-making frameworks, not
              used as a casual “hack.”
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Scientific &amp; Psychological Evidence
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Sleep deprivation reliably impairs attention, working memory, mood
              regulation, and decision-making. Fasting can produce metabolic
              adaptations and may affect mood and focus in variable ways, but the
              altered-state “benefits” are not reliable and can come with
              meaningful costs.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Risks, Limits, and Misuse
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Sleep loss increases accident risk; do not drive or operate machinery when deprived.</li>
              <li>Higher risk if you have bipolar disorder, psychosis risk, or severe anxiety.</li>
              <li>Fasting can be unsafe with diabetes, eating disorders, pregnancy, or certain medications.</li>
              <li>“Visions” under deprivation can reflect instability, not insight.</li>
            </ul>
            <p className="text-sm text-muted-foreground">
              For healthier altered-state exploration, consider{" "}
              <Link
                href="/consciousness/altered-states/common-methods-for-altering-consciousness/meditation-and-mindfulness"
                className="text-primary hover:underline"
              >
                meditation
              </Link>{" "}
              or natural sleep states via{" "}
              <Link href="/consciousness/sleep-dreams" className="text-primary hover:underline">
                Sleep &amp; Dreams
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
                  href="/consciousness/altered-states/common-methods-for-altering-consciousness/physical-extremes"
                  className="text-primary hover:underline"
                >
                  physical extremes
                </Link>
                , deprivation stresses the system; altered states often reflect
                stress and compensation.
              </li>
              <li>
                Like long{" "}
                <Link
                  href="/consciousness/altered-states/common-methods-for-altering-consciousness/sensory-deprivation"
                  className="text-primary hover:underline"
                >
                  sensory deprivation
                </Link>
                , it can produce dreamlike imagery, but with less stability.
              </li>
              <li>
                Compared with{" "}
                <Link
                  href="/consciousness/altered-states/common-methods-for-altering-consciousness/meditation-and-mindfulness"
                  className="text-primary hover:underline"
                >
                  meditation
                </Link>
                , deprivation is more disruptive and less controllable.
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
              When This Method Is Most Useful
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Practically, deprivation is rarely the best choice. If used at all,
              it belongs in structured contexts with medical awareness,
              conservative limits, and strong recovery plans. For most people,
              the wiser path is to protect sleep and use methods that increase
              stability rather than reduce it.
            </p>
          </section>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <h2 className="text-xl font-semibold text-foreground mb-3">
              Key Takeaways
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Deprivation can produce altered states, but often through impairment and instability.</li>
              <li>Sleep deprivation reliably degrades judgment and mood regulation.</li>
              <li>Fasting affects metabolism and arousal; outcomes vary and risks can be serious.</li>
              <li>Most people benefit more from stabilizing methods than deprivation.</li>
              <li>Use strict boundaries and prioritize recovery if you engage at all.</li>
            </ul>
          </section>
        </div>
      </main>
    </div>
  );
}

