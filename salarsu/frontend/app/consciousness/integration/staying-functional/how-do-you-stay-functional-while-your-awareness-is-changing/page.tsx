import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/integration/staying-functional/how-do-you-stay-functional-while-your-awareness-is-changing`;

export const metadata: Metadata = {
  title: "How do you stay functional while your awareness is changing? | Salars Consciousness",
  description: "Maintain routine activities and social connections while allowing gradual adjustment periods between awareness shifts. Focus on practical tasks during tran",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "How do you stay functional while your awareness is changing?",
    description: "Maintain routine activities and social connections while allowing gradual adjustment periods between awareness shifts. Focus on practical tasks during tran",
    url: pageUrl,
    type: "article",
  },
  keywords: ["consciousness integration", "awareness transitions", "functional stability", "cognitive adaptation", "perspective shifts", "altered states", "grounding techniques", "consciousness exploration"],
};

export default function HowDoYouStayFunctionalWhileYourAwarenessIsChangingPage() {
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
            How do you stay functional while your awareness is changing?
          </h1>

          {/* Short Answer Block */}
          <section className="rounded-2xl border border-border bg-card/40 p-6">
            <p className="text-sm font-semibold uppercase tracking-wide text-primary mb-3">
              Short Answer
            </p>
            <p className="text-lg text-foreground leading-relaxed">
              Maintain routine activities and social connections while allowing gradual adjustment periods between awareness shifts. Focus on practical tasks during transitions.
            </p>
          </section>

          {/* Why This Matters */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Why This Matters
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Consciousness changes often disrupt familiar patterns of perception and decision-making, which can impair daily functioning. Maintaining structured activities provides stability because routine tasks require less cognitive adaptation than novel situations. Social connections serve as external anchors that help maintain perspective during internal shifts, while gradual transitions prevent overwhelming the system's capacity to integrate new awareness levels.
            </p>
          </section>

          {/* Where This Changes */}
          <section className="space-y-3">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Where This Changes
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Functionality becomes more difficult during rapid or intense awareness shifts, particularly those involving altered states or major perspective changes. Some individuals require longer adjustment periods, while others integrate changes more quickly based on prior experience with consciousness exploration.
            </p>
          </section>

          {/* Related Questions */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Related Questions
            </h2>
            <div className="grid gap-3">
              
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
                href="/consciousness/integration/staying-functional/how-do-you-balance-spiritual-practice-with-practical-responsibilities"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">How do you balance spiritual practice with practical responsibilities?</span>
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