import { Metadata } from "next";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { ContentCard } from "@/components/ContentCard";

export const metadata: Metadata = {
  title: "Wealth | Salars",
  description: "A practical, mechanism-first view of wealth: optionality, resilience, and value creation.",
  alternates: { canonical: "/wealth" },
};

export default function WealthPage() {
  return (
    <div className="min-h-screen bg-background py-12 px-6">
      <div className="mx-auto max-w-3xl space-y-10">
        <Breadcrumbs items={[{ href: "/", label: "Home" }, { href: "/wealth", label: "Wealth" }]} />

        <header className="space-y-3">
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">Wealth</h1>
          <p className="text-base text-muted-foreground">
            Wealth is not a number. It is stored optionality: the ability to move without panic, choose without coercion,
            and keep making good decisions under stress.
          </p>
        </header>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold text-foreground">What Is True Wealth?</h2>
          <p className="text-base text-muted-foreground">
            True wealth is the accumulation of capabilities that keep your life stable and expandable: skills, trust,
            access, health, savings, and systems. Money is a tool inside that ecosystem. It is not the ecosystem.
          </p>
          <p className="text-base text-muted-foreground">
            The goal is not to look rich. The goal is to be hard to destabilize.
          </p>
        </section>

        <section className="space-y-4">
          <ContentCard
            title="How Money Actually Works: A Practical Model of Wealth, Value, and Flow"
            description="Start here. A mechanism-based hub: what money measures, why effort does not predict income, and the core models (value, leverage, trust, optionality, risk)."
            href="/money"
            badge="Start here"
          />
        </section>
      </div>
    </div>
  );
}

