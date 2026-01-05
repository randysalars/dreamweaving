import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/integration/staying-functional/how-do-you-balance-spiritual-practice-with-practical-responsibilities`;

export const metadata: Metadata = {
  title: "How do you balance spiritual practice with practical responsibilities? | Salars Consciousness",
  description: "Spiritual practice and practical responsibilities integrate through structured time allocation, present-moment awareness during routine tasks, and treating",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How do you balance spiritual practice with practical responsibilities?",
    description: "Spiritual practice and practical responsibilities integrate through structured time allocation, present-moment awareness during routine tasks, and treating",
    url: pageUrl,
    type: "article",
  },
  keywords: ["spiritual bypassing", "embodied spirituality", "mindful productivity", "contemplative living", "functional awakening", "practice-life integration", "spiritual materialism", "grounded awareness"],
};

export default function HowDoYouBalanceSpiritualPracticeWithPracticalResponsibilitiesPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-3xl space-y-8">

          {/* Breadcrumb */}
          <div className="space-y-2">
            <Link
              href="/consciousness/integration/staying-functional"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to How to Stay Functional While Awareness Changes
            </Link>
          </div>

          {/* Question Title */}
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            How do you balance spiritual practice with practical responsibilities?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Spiritual practice and practical responsibilities integrate through structured time allocation, present-moment awareness during routine tasks, and treating daily obligations as mindfulness opportunities rather than obstacles.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              This integration occurs because consciousness shifts don't require withdrawal from ordinary activities—they transform how activities are experienced. Maintaining practical functioning during awareness changes demonstrates that spiritual development can enhance rather than impair daily performance. The nervous system adapts to expanded states through consistent practice within normal life contexts, creating sustainable growth patterns.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Integration becomes more challenging during intensive practice periods or sudden consciousness shifts that temporarily disrupt normal functioning. Some individuals experience phases where practical tasks feel less engaging as priorities shift toward inner exploration.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
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
              
              <Link
                href="/consciousness/integration/staying-functional/why-do-some-people-feel-disconnected-from-daily-life-after-consciousness-work"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Why do some people feel disconnected from daily life after consciousness work?</span>
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
              href="/consciousness/integration/staying-functional"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all How to Stay Functional While Awareness Changes questions
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>

        </div>
      </main>
    </div>
  );
}