import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/common-methods-for-altering-consciousness/psychedelics-and-entheogens`;

export const metadata: Metadata = {
  title: "Psychedelics and Entheogens: How They Alter Consciousness | Salars Consciousness",
  description:
    "Psychedelics and entheogens can alter consciousness by changing serotonin signaling and brain network dynamics, producing profound shifts in perception, emotion, meaning, and sense of self. Risks and legality vary widely.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Psychedelics and Entheogens: How They Alter Consciousness",
    description:
      "Mechanisms, typical effects, therapeutic research context, and clear safety and legality framing.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "psychedelics",
    "entheogens",
    "psilocybin",
    "LSD",
    "ayahuasca",
    "DMT",
    "altered states",
    "serotonin",
    "integration",
  ],
};

export default function PsychedelicsAndEntheogensMethodPage() {
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
              Psychedelics and Entheogens: How They Alter Consciousness
            </h1>
            <p className="text-muted-foreground leading-relaxed">
              Psychedelics and entheogens are substances that can dramatically
              alter perception, emotion, and the felt sense of meaning. They
              often produce intensified sensory experience, novel associations,
              and shifts in identity and worldview. Because intensity is high,
              so is the need for safety, screening, and integration.
            </p>
          </header>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              What This Method Is
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              “Psychedelics” typically refers to compounds like psilocybin, LSD,
              mescaline, and DMT (including ayahuasca preparations) that
              profoundly alter perception and cognition. “Entheogens” is a term
              often used for psychedelic substances in religious or ceremonial
              contexts.
            </p>
            <p className="text-muted-foreground leading-relaxed">
              What this method is not: a universally safe shortcut, a guaranteed
              cure, or a replacement for stable mental health supports. Context,
              dosage, legality, and individual vulnerability strongly shape
              outcomes.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              How Psychedelics Alter Consciousness
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">
                  Serotonin receptor modulation:
                </strong>{" "}
                many classic psychedelics act strongly on 5-HT2A receptors,
                changing perception and cognition.
              </li>
              <li>
                <strong className="text-foreground">
                  Network reorganization:
                </strong>{" "}
                brain networks involved in self-referential processing and
                sensory integration can shift, changing how experience is bound
                together.
              </li>
              <li>
                <strong className="text-foreground">
                  Meaning amplification:
                </strong>{" "}
                emotion and salience can increase, making experiences feel
                deeply significant.
              </li>
              <li>
                <strong className="text-foreground">Set and setting:</strong>{" "}
                expectations, environment, music, and guidance are major causal
                factors for both benefit and harm.
              </li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Typical Experiences Reported
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Perceptual intensification (color, sound, pattern recognition).</li>
              <li>Novel associations and a sense of psychological “opening.”</li>
              <li>Emotional catharsis or deep compassion.</li>
              <li>Disruption of self-boundaries (“ego dissolution”).</li>
              <li>Challenging experiences: fear, confusion, paranoia, panic.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Historical &amp; Cultural Use
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Some cultures use entheogenic plants or preparations in ritual
              contexts that include community support, norms, and integration
              practices. Modern use spans clinical research, underground
              facilitation, and recreational contexts—with dramatically different
              risk profiles.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Scientific &amp; Clinical Context
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Clinical research explores psychedelic-assisted therapy for certain
              conditions under strict screening, dosing, and psychological
              support. Results can be promising in controlled settings. Outside
              controlled contexts, risks rise due to unknown substance purity,
              lack of screening, unsafe environments, and poor integration.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Risks, Limits, Legality, and Ethics
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                Legal status varies by location; legality is part of safety and
                should be checked first.
              </li>
              <li>
                Higher risk for people with personal or family history of
                psychosis, bipolar mania, or severe dissociation.
              </li>
              <li>
                Drug interactions matter (especially with SSRIs/MAOIs and other
                medications). Medical supervision is non-negotiable if you are
                on prescriptions.
              </li>
              <li>
                “Bad trips” can have lasting psychological impact; integration
                and social support reduce harm.
              </li>
            </ul>
            <p className="text-sm text-muted-foreground">
              For a general safety framework, start with{" "}
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
                Like intense{" "}
                <Link
                  href="/consciousness/altered-states/common-methods-for-altering-consciousness/breathwork"
                  className="text-primary hover:underline"
                >
                  breathwork
                </Link>
                , psychedelics can rapidly shift perception and meaning.
              </li>
              <li>
                Like{" "}
                <Link
                  href="/consciousness/altered-states/common-methods-for-altering-consciousness/rituals-and-chanting"
                  className="text-primary hover:underline"
                >
                  ritual contexts
                </Link>
                , outcomes are heavily shaped by environment, guidance, and group
                norms.
              </li>
              <li>
                Compared with{" "}
                <Link
                  href="/consciousness/altered-states/common-methods-for-altering-consciousness/meditation-and-mindfulness"
                  className="text-primary hover:underline"
                >
                  meditation
                </Link>
                , psychedelics are higher-intensity and higher-risk, with less
                day-to-day controllability.
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
              When This Method Is Most Useful (Conceptually)
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              In clinical contexts, the “usefulness” discussion centers on
              structured therapeutic goals and integration. In general, this
              method is not an everyday tool; it is an intervention that requires
              preparation, supervision, and aftercare.
            </p>
          </section>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <h2 className="text-xl font-semibold text-foreground mb-3">
              Key Takeaways
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Psychedelics can profoundly alter perception, emotion, and self-experience.</li>
              <li>Mechanisms and outcomes depend heavily on set, setting, and support.</li>
              <li>Risks are real: screening, legality, interactions, and integration matter.</li>
              <li>Clinical contexts differ dramatically from uncontrolled contexts.</li>
              <li>Safety framing is not optional at high intensity.</li>
            </ul>
          </section>
        </div>
      </main>
    </div>
  );
}

