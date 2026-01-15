import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/integration/grounding-not-regression/why-is-it-important-to-return-to-the-body-after-consciousness-exploration`;

export const metadata: Metadata = {
  title: "Why is it important to return to the body after consciousness exploration? | Salars Consciousness",
  description: "Returning to the body after consciousness exploration integrates insights into ordinary awareness and prevents dissociation from physical reality and daily",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Why is it important to return to the body after consciousness exploration?",
    description: "Returning to the body after consciousness exploration integrates insights into ordinary awareness and prevents dissociation from physical reality and daily",
    url: pageUrl,
    type: "article",
  },
  keywords: ["embodiment", "dissociation", "grounding techniques", "state integration", "somatic awareness", "nervous system regulation", "altered states", "consciousness bridging"],
};

export default function WhyIsItImportantToReturnToTheBodyAfterConsciousnessExplorationPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/integration/grounding-not-regression"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Why Grounding Is Not Regression
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Why is it important to return to the body after consciousness exploration?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Returning to the body after consciousness exploration integrates insights into ordinary awareness and prevents dissociation from physical reality and daily functioning.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Consciousness exploration activates altered states that shift attention away from bodily awareness and conventional thinking patterns. Without deliberate grounding, insights remain disconnected from practical application because they exist in a different state context than normal waking consciousness. This integration process allows expanded awareness to inform decision-making and behavior in everyday life, while maintaining connection to physical sensations prevents the destabilizing effects of prolonged dissociation.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Some individuals naturally integrate expanded states without formal grounding practices, particularly those with stable nervous systems and extensive meditation experience. The need for grounding varies based on the intensity and duration of the consciousness exploration and individual neurological resilience.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
              <Link
                href="/consciousness/integration/grounding-not-regression/is-grounding-the-same-as-going-backwards-in-consciousness-development"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Is grounding the same as going backwards in consciousness development?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/grounding-not-regression/why-does-grounding-sometimes-feel-like-losing-progress"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Why does grounding sometimes feel like losing progress?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/grounding-not-regression/whats-the-difference-between-healthy-grounding-and-spiritual-bypassing"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What's the difference between healthy grounding and spiritual bypassing?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/integration-matters/why-does-integration-matter-more-than-insight-in-consciousness-work"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Why does integration matter more than insight in consciousness work?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/integration-matters/what-is-the-difference-between-having-an-insight-and-integrating-it"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What is the difference between having an insight and integrating it?</span>
              </Link>
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/integration/grounding-not-regression"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Why Grounding Is Not Regression questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}