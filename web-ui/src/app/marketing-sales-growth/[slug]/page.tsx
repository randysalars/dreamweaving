import React from "react";
import Link from "next/link";
import { Metadata } from "next";
import { notFound } from "next/navigation";
import { ArrowRight } from "lucide-react";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  getMarketingSalesGrowthArticle,
  marketingSalesGrowthArticles,
  marketingSalesGrowthHub,
} from "@/lib/marketing-sales-growth/articles";

type PageProps = {
  params: Promise<{ slug: string }>;
};

export async function generateStaticParams() {
  return marketingSalesGrowthArticles.map((article) => ({ slug: article.slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const article = getMarketingSalesGrowthArticle(slug);
  if (!article) return {};

  return {
    title: `${article.title} | ${marketingSalesGrowthHub.title}`,
    description: article.description,
    alternates: { canonical: `${marketingSalesGrowthHub.href}/${article.slug}` },
    openGraph: {
      title: article.title,
      description: article.description,
      url: `${marketingSalesGrowthHub.href}/${article.slug}`,
      type: "article",
    },
  };
}

export default async function MarketingSalesGrowthArticlePage({ params }: PageProps) {
  const { slug } = await params;
  const article = getMarketingSalesGrowthArticle(slug);
  if (!article) notFound();

  const sameCategory = marketingSalesGrowthArticles.filter(
    (candidate) => candidate.category === article.category && candidate.slug !== article.slug
  );
  const related = sameCategory.slice(0, 4);
  const crossCategory = marketingSalesGrowthArticles
    .filter((candidate) => candidate.category !== article.category)
    .slice(0, 2);
  const relatedReading = [...related, ...crossCategory].slice(0, 6);

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
      {
        "@type": "ListItem",
        position: 4,
        name: article.title,
        item: `${marketingSalesGrowthHub.href}/${article.slug}`,
      },
    ],
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: article.faqs.map((faq) => ({
      "@type": "Question",
      name: faq.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: faq.answer,
      },
    })),
  };

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: article.title,
    description: article.description,
    mainEntityOfPage: `${marketingSalesGrowthHub.href}/${article.slug}`,
    isPartOf: marketingSalesGrowthHub.href,
  };

  return (
    <div className="min-h-screen bg-background py-12 px-6">
      <div className="mx-auto max-w-3xl space-y-8">
        <Breadcrumbs
          items={[
            { href: "/", label: "Home" },
            { href: "/ai", label: "AI" },
            { href: marketingSalesGrowthHub.href, label: marketingSalesGrowthHub.title },
            { href: `${marketingSalesGrowthHub.href}/${article.slug}`, label: article.title },
          ]}
        />

        <header className="space-y-3">
          <p className="text-sm text-muted-foreground">{article.category}</p>
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">{article.title}</h1>
          <p className="text-base text-muted-foreground">{article.description}</p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link href={marketingSalesGrowthHub.href}>
              <Button variant="secondary">Back to hub</Button>
            </Link>
            <Link href="/ai">
              <Button variant="outline">Explore AI</Button>
            </Link>
          </div>
        </header>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Quick Answer</CardTitle>
            <CardDescription>For search, voice, and “just tell me what to do”.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-foreground">
            <p>{article.quickAnswer}</p>
            <ul className="list-disc pl-5 text-muted-foreground">
              {article.keyTakeaways.map((t) => (
                <li key={t}>{t}</li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold text-foreground">Playbook</h2>
          <ol className="list-decimal pl-5 text-muted-foreground space-y-2">
            {article.playbook.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold text-foreground">Common Pitfalls</h2>
          <ul className="list-disc pl-5 text-muted-foreground space-y-2">
            {article.pitfalls.map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold text-foreground">Metrics to Track</h2>
          <ul className="list-disc pl-5 text-muted-foreground space-y-2">
            {article.metrics.map((m) => (
              <li key={m}>{m}</li>
            ))}
          </ul>
        </section>

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-foreground">FAQ</h2>
          <div className="space-y-4">
            {article.faqs.map((faq) => (
              <div key={faq.question} className="space-y-1">
                <p className="font-semibold text-foreground">{faq.question}</p>
                <p className="text-muted-foreground">{faq.answer}</p>
              </div>
            ))}
          </div>
        </section>

        {relatedReading.length > 0 ? (
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Related Reading</h2>
            <div className="grid gap-4 md:grid-cols-2">
              {relatedReading.map((a) => (
                <Card key={a.slug} className="transition-shadow hover:shadow-md">
                  <CardHeader>
                    <CardTitle className="text-base leading-snug line-clamp-2">{a.title}</CardTitle>
                    <CardDescription className="line-clamp-2">{a.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Link href={`${marketingSalesGrowthHub.href}/${a.slug}`} className="w-full">
                      <Button variant="ghost" className="w-full justify-between gap-2">
                        Read <ArrowRight className="h-4 w-4" />
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>
        ) : null}

        <section className="pt-2">
          <p className="text-sm text-muted-foreground">
            Next:{" "}
            <Link href={marketingSalesGrowthHub.href} className="underline underline-offset-4 hover:text-foreground">
              browse the hub
            </Link>{" "}
            or{" "}
            <Link href="/ai/operations" className="underline underline-offset-4 hover:text-foreground">
              explore AI Operations
            </Link>
            .
          </p>
        </section>
      </div>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />
    </div>
  );
}
