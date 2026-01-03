import Link from "next/link";
import { Metadata } from "next";
import { ArrowRight } from "lucide-react";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  marketingSalesGrowthArticles,
  marketingSalesGrowthCategories,
  marketingSalesGrowthHub,
} from "@/lib/marketing-sales-growth/articles";

export const metadata: Metadata = {
  title: `${marketingSalesGrowthHub.title} | AI Hub`,
  description:
    "Practical, monetizable playbooks for using AI to scale marketing output, improve sales conversations, and build sustainable growth systems.",
  alternates: { canonical: marketingSalesGrowthHub.href },
};

export default function MarketingSalesGrowthHubPage() {
  const breadcrumbSchema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: "/" },
      { "@type": "ListItem", position: 2, name: "AI", item: "/ai" },
      {
        "@type": "ListItem",
        position: 3,
        name: marketingSalesGrowthHub.title,
        item: marketingSalesGrowthHub.href,
      },
    ],
  };

  const hubSchema = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: marketingSalesGrowthHub.title,
    description:
      "Practical, monetizable playbooks for using AI across marketing systems, personas, email, offer validation, and sales execution.",
    mainEntity: {
      "@type": "ItemList",
      itemListOrder: "ItemListOrderAscending",
      numberOfItems: marketingSalesGrowthArticles.length,
      itemListElement: marketingSalesGrowthArticles.map((article, index) => ({
        "@type": "ListItem",
        position: index + 1,
        name: article.title,
        url: `${marketingSalesGrowthHub.href}/${article.slug}`,
      })),
    },
  };

  return (
    <div className="min-h-screen bg-background py-12 px-6">
      <div className="mx-auto max-w-6xl space-y-10">
        <Breadcrumbs
          items={[
            { href: "/", label: "Home" },
            { href: "/ai", label: "AI" },
            { href: marketingSalesGrowthHub.href, label: marketingSalesGrowthHub.title },
          ]}
        />

        <header className="space-y-3">
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">
            {marketingSalesGrowthHub.title}
          </h1>
          <p className="text-base text-muted-foreground max-w-3xl">
            A focused content hub for AI-first marketing systems, customer insight, offer validation, and sales execution.
            Each article is written to be both search-friendly (SEO) and answer-friendly (AEO) with clear playbooks and FAQs.
          </p>
          <p className="text-sm text-muted-foreground">
            Source notes:{" "}
            <a
              href={marketingSalesGrowthHub.sourceNotionUrl}
              className="underline underline-offset-4 hover:text-foreground"
              target="_blank"
              rel="noreferrer"
            >
              Notion outline
            </a>
          </p>
          <div className="flex flex-wrap gap-3 pt-1">
            <Link href="/ai">
              <Button variant="secondary">Explore AI</Button>
            </Link>
            <Link href="/ai/operations">
              <Button variant="outline">AI Operations</Button>
            </Link>
          </div>
        </header>

        <section className="space-y-6">
          <h2 className="text-2xl font-semibold text-foreground">Articles</h2>
          <div className="space-y-10">
            {marketingSalesGrowthCategories.map((category) => {
              const articles = marketingSalesGrowthArticles.filter((a) => a.category === category);
              return (
                <div key={category} className="space-y-4">
                  <h3 className="text-lg font-semibold text-foreground">{category}</h3>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {articles.map((article) => (
                      <Card key={article.slug} className="transition-shadow hover:shadow-md">
                        <CardHeader>
                          <CardTitle className="text-base leading-snug line-clamp-2">
                            {article.title}
                          </CardTitle>
                          <CardDescription className="line-clamp-3">{article.description}</CardDescription>
                        </CardHeader>
                        <CardFooter>
                          <Link href={`${marketingSalesGrowthHub.href}/${article.slug}`} className="w-full">
                            <Button variant="ghost" className="w-full justify-between gap-2">
                              Read <ArrowRight className="h-4 w-4" />
                            </Button>
                          </Link>
                        </CardFooter>
                      </Card>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </div>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(hubSchema) }}
      />
    </div>
  );
}
