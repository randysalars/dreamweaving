import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/integration/integration-matters/why-do-some-people-feel-worse-after-profound-consciousness-experiences`;

export const metadata: Metadata = {
  title: "Why do some people feel worse after profound consciousness experiences? | Salars Consciousness",
  description: "Profound consciousness experiences can destabilize existing psychological structures and worldviews without providing adequate tools or support for rebuild",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Why do some people feel worse after profound consciousness experiences?",
    description: "Profound consciousness experiences can destabilize existing psychological structures and worldviews without providing adequate tools or support for rebuild",
    url: pageUrl,
    type: "article",
  },
  keywords: ["spiritual emergency", "integration therapy", "ego dissolution", "meaning-making", "cognitive dissonance", "spiritual bypassing", "psychological destabilization", "post-experience depression"],
};

export default function WhyDoSomePeopleFeelWorseAfterProfoundConsciousnessExperiencesPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/integration/integration-matters"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Why Integration Matters More Than Insight
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            Why do some people feel worse after profound consciousness experiences?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Profound consciousness experiences can destabilize existing psychological structures and worldviews without providing adequate tools or support for rebuilding coherent meaning systems.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              These experiences often dissolve familiar identity structures and belief systems that previously provided psychological stability and meaning. When the expanded awareness gained from the experience cannot be integrated with daily life, it creates cognitive dissonance and emotional dysregulation. The contrast between the profound state and ordinary consciousness can lead to spiritual bypassing, depression, or feelings of alienation because the person lacks frameworks for making sense of the experience.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Integration becomes easier with proper preparation, ongoing support, and gradual exposure to expanded states. People with existing contemplative practices or psychological resilience typically navigate these transitions more smoothly.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
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
              
              <Link
                href="/consciousness/integration/integration-matters/how-long-does-integration-typically-take-after-a-profound-experience"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How long does integration typically take after a profound experience?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/staying-functional/how-do-you-stay-functional-while-your-awareness-is-changing"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do you stay functional while your awareness is changing?</span>
              </Link>
              
              <Link
                href="/consciousness/integration/staying-functional/what-does-grounding-mean-in-the-context-of-consciousness-shifts"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">What does grounding mean in the context of consciousness shifts?</span>
              </Link>
              
            </div>
          </section>

          {/* Back to Category */}
          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/integration/integration-matters"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Why Integration Matters More Than Insight questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}