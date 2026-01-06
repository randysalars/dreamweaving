import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/common-methods-for-altering-consciousness/breathwork`;

export const metadata: Metadata = {
  title: "Breathwork: How It Alters Consciousness | Salars Consciousness",
  description:
    "Breathwork alters consciousness by changing CO₂/O₂ balance and autonomic arousal, which can rapidly shift attention, emotion, and perception—sometimes into visionary states.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Breathwork: How It Alters Consciousness",
    description:
      "How breath patterns change arousal, perception, and attention—plus typical effects, evidence, and safety boundaries.",
    url: pageUrl,
    type: "article",
  },
  keywords: [
    "breathwork",
    "holotropic breathwork",
    "pranayama",
    "Wim Hof",
    "altered states",
    "hyperventilation",
    "autonomic nervous system",
  ],
};

export default function BreathworkMethodPage() {
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
              Breathwork: How It Alters Consciousness
            </h1>
            <p className="text-muted-foreground leading-relaxed">
              Breathwork uses deliberate breathing patterns to shift physiology
              and attention. Depending on the technique, it can downshift into
              calm focus or upshift into intense, sometimes psychedelic-like
              experiences—without drugs—by changing arousal, carbon dioxide
              tolerance, and interoceptive (body-sensation) processing.
            </p>
          </header>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              What This Method Is
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Breathwork is any structured practice where breath rate, depth,
              holds, or rhythms are intentionally modified for a specific effect.
              It ranges from gentle nasal breathing and slow exhale protocols to
              intensive methods that include extended hyperventilation and breath
              retention.
            </p>
            <p className="text-muted-foreground leading-relaxed">
              What breathwork is not: a guarantee of catharsis, a substitute for
              medical care, or a safe intensity-maximization game. The same
              mechanism that produces “breakthrough” experiences can also produce
              dizziness, panic, or fainting when misapplied.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              How Breathwork Alters Consciousness
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                <strong className="text-foreground">CO₂/O₂ balance:</strong>{" "}
                Faster breathing can lower CO₂ (hypocapnia), changing blood pH and
                brain blood flow, which can shift sensation and perception.
              </li>
              <li>
                <strong className="text-foreground">
                  Autonomic state shift:
                </strong>{" "}
                Slow, controlled breathing often increases parasympathetic tone
                (downshifts), while intense methods can increase sympathetic
                arousal (upshifts).
              </li>
              <li>
                <strong className="text-foreground">Interoception:</strong>{" "}
                Breath becomes a high-salience signal; attention narrows onto the
                body, changing time sense and emotion appraisal.
              </li>
              <li>
                <strong className="text-foreground">Expectation + context:</strong>{" "}
                Music, setting, guidance, and meaning-making can amplify imagery
                and emotional release.
              </li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Typical Experiences Reported
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Deep relaxation, warmth, or calm focus (common in slow breathing).</li>
              <li>Emotional release (crying, laughter, shaking) without clear narrative.</li>
              <li>Tingling, muscle tightness, or cramping (often from low CO₂).</li>
              <li>Visual patterns, autobiographical memories, or symbolic imagery.</li>
              <li>Altered time perception and a sense of “reset” afterward.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Historical &amp; Cultural Use
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Breath regulation appears across contemplative traditions (e.g.,
              pranayama in yoga) and modern therapeutic or ceremonial contexts.
              Contemporary approaches include holotropic-style group sessions,
              athletic protocols (e.g., cold exposure preparation), and clinical
              breathing retraining for anxiety and respiratory issues.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Scientific &amp; Psychological Evidence
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Evidence is strongest for slow breathing as a regulator of stress,
              anxiety, and autonomic balance (especially when paired with
              attention training). Research on intensive breathwork suggests it
              can produce powerful subjective experiences and emotional
              processing, but outcomes vary widely and are strongly influenced by
              screening, facilitation quality, and integration support.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Risks, Limits, and Misuse
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>
                Avoid intense breathwork if you have uncontrolled cardiovascular
                disease, seizure disorder, pregnancy, glaucoma/retinal issues, or
                a history of fainting.
              </li>
              <li>
                If you have panic disorder, PTSD, or dissociation, start with
                gentle protocols and consider professional guidance.
              </li>
              <li>
                Never combine intense breathing with water, driving, or situations
                where fainting would be dangerous.
              </li>
              <li>
                Treat numbness/tingling as a warning to reduce intensity, not a
                “breakthrough” signal.
              </li>
            </ul>
            <p className="text-sm text-muted-foreground">
              For a broader safety map, see{" "}
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
                  href="/consciousness/altered-states/common-methods-for-altering-consciousness/physical-extremes"
                  className="text-primary hover:underline"
                >
                  physical extremes
                </Link>
                , breathwork can rapidly change arousal through physiology.
              </li>
              <li>
                Like{" "}
                <Link
                  href="/consciousness/altered-states/common-methods-for-altering-consciousness/sensory-deprivation"
                  className="text-primary hover:underline"
                >
                  sensory deprivation
                </Link>
                , it can amplify internal sensation and imagery when attention
                turns inward.
              </li>
              <li>
                Compared with{" "}
                <Link
                  href="/consciousness/altered-states/common-methods-for-altering-consciousness/meditation-and-mindfulness"
                  className="text-primary hover:underline"
                >
                  meditation
                </Link>
                , breathwork often produces faster state changes, but can be less
                stable if pushed too hard.
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
              When Breathwork Is Most Useful
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Downshifting stress quickly (slow exhale protocols).</li>
              <li>Breaking rumination by re-centering attention in the body.</li>
              <li>Supporting exposure to physiological arousal (with care).</li>
              <li>As a bridge into meditation (breath as an attention anchor).</li>
            </ul>
          </section>

          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <h2 className="text-xl font-semibold text-foreground mb-3">
              Key Takeaways
            </h2>
            <ul className="list-disc pl-6 text-muted-foreground space-y-2">
              <li>Breathwork alters consciousness through physiology and attention.</li>
              <li>Gentle protocols are low-risk and broadly useful; intensity is optional.</li>
              <li>Intense methods can be powerful but require screening and boundaries.</li>
              <li>Context and integration strongly shape what the experience means.</li>
              <li>Safety comes first: never chase symptoms as a sign of progress.</li>
            </ul>
          </section>
        </div>
      </main>
    </div>
  );
}

