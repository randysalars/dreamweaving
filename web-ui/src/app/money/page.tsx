import Link from "next/link";
import { Metadata } from "next";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { ContentCard } from "@/components/ContentCard";
import { Markdown } from "@/components/Markdown";
import { getMoneyHubDoc, listMoneyDocs } from "@/lib/money/content";

export const metadata: Metadata = {
  title: "How Money Actually Works: A Practical Model of Wealth, Value, and Flow | Salars",
  description:
    "A practical, mechanism-first model of money: value, trust, leverage, optionality, risk, and why effort does not predict income.",
  alternates: { canonical: "/money" },
};

const minimumViableCanon: string[] = [
  "what-is-money",
  "what-is-wealth",
  "income-vs-wealth",
  "what-is-value",
  "why-effort-is-poorly-paid",
  "why-certainty-commands-premiums",
  "what-is-leverage-really",
  "why-distribution-matters",
  "what-is-financial-risk",
  "what-is-optionality",
  "why-stability-is-a-competitive-advantage",
  "what-ai-changes-about-wealth",
];

export default function MoneyHubPage() {
  const hub = getMoneyHubDoc();
  const docs = listMoneyDocs();
  const tier1 = docs.filter((d) => d.tier === 1).sort((a, b) => a.title.localeCompare(b.title));
  const tier2 = docs.filter((d) => d.tier === 2).sort((a, b) => a.title.localeCompare(b.title));
  const mvpDocs = minimumViableCanon
    .map((slug) => docs.find((d) => d.slug === slug))
    .filter(Boolean);

  return (
    <div className="min-h-screen bg-background py-12 px-6">
      <div className="mx-auto max-w-6xl space-y-10">
        <Breadcrumbs items={[{ href: "/", label: "Home" }, { href: "/money", label: "Money" }]} />

        <header className="space-y-3">
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">{hub.frontmatter.title}</h1>
          <p className="text-base text-muted-foreground max-w-3xl">{hub.frontmatter.description}</p>
          <p className="text-sm text-muted-foreground">
            Source notes:{" "}
            <a
              href="https://www.notion.so/1-Money-Wealth-Value-Creation-Highest-Traffic-Impact-2df2bab3796d800f8fa4c0f141996a05"
              className="underline underline-offset-4 hover:text-foreground"
              target="_blank"
              rel="noreferrer"
            >
              Notion outline
            </a>
          </p>
        </header>

        <section className="space-y-6">
          <Markdown content={hub.content} />
        </section>

        {mvpDocs.length > 0 ? (
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Start Here: The Must-Have 12</h2>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {mvpDocs.map((doc) => (
                <ContentCard
                  key={doc!.slug}
                  title={doc!.title}
                  description={doc!.description}
                  href={`/money/${doc!.slug}`}
                  badge="Answer"
                />
              ))}
            </div>
          </section>
        ) : null}

        {tier1.length > 0 ? (
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Core Models</h2>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {tier1.map((doc) => (
                <ContentCard
                  key={doc.slug}
                  title={doc.title}
                  description={doc.description}
                  href={`/money/${doc.slug}`}
                  badge="Model"
                />
              ))}
            </div>
          </section>
        ) : null}

        {tier2.length > 0 ? (
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Answer Pages</h2>
            <p className="text-base text-muted-foreground max-w-3xl">
              Short, mechanism-first pages designed to be quotable, linkable, and durable.
            </p>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {tier2.map((doc) => (
                <ContentCard
                  key={doc.slug}
                  title={doc.title}
                  description={doc.description}
                  href={`/money/${doc.slug}`}
                  badge="Answer"
                />
              ))}
            </div>
          </section>
        ) : null}

        <section className="pt-2">
          <p className="text-sm text-muted-foreground">
            Prefer the philosophy first? Start with{" "}
            <Link href="/wealth" className="underline underline-offset-4 hover:text-foreground">
              Wealth
            </Link>
            .
          </p>
        </section>
      </div>
    </div>
  );
}

