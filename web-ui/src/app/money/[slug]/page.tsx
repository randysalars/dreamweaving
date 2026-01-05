import Link from "next/link";
import { Metadata } from "next";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Markdown } from "@/components/Markdown";
import { getMoneyDoc, listMoneyDocs, listMoneySlugs } from "@/lib/money/content";

type PageProps = {
  params: Promise<{ slug: string }>;
};

export async function generateStaticParams() {
  return listMoneySlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const doc = getMoneyDoc(slug);
  if (!doc) return {};

  const canonical = doc.frontmatter.canonical ?? `/money/${doc.frontmatter.slug}`;

  return {
    title: `${doc.frontmatter.title} | How Money Actually Works`,
    description: doc.frontmatter.description,
    alternates: { canonical },
    openGraph: {
      title: doc.frontmatter.title,
      description: doc.frontmatter.description,
      url: canonical,
      type: "article",
    },
  };
}

export default async function MoneyDocPage({ params }: PageProps) {
  const { slug } = await params;
  const doc = getMoneyDoc(slug);
  if (!doc) notFound();

  const allDocs = listMoneyDocs();
  const related = allDocs
    .filter((d) => d.slug !== doc.frontmatter.slug && d.tier === doc.frontmatter.tier)
    .slice(0, 6);

  const breadcrumbSchema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: "/" },
      { "@type": "ListItem", position: 2, name: "Money", item: "/money" },
      { "@type": "ListItem", position: 3, name: doc.frontmatter.title, item: `/money/${doc.frontmatter.slug}` },
    ],
  };

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: doc.frontmatter.title,
    description: doc.frontmatter.description,
    mainEntityOfPage: `/money/${doc.frontmatter.slug}`,
    isPartOf: "/money",
    dateModified: doc.frontmatter.updated,
  };

  return (
    <div className="min-h-screen bg-background py-12 px-6">
      <div className="mx-auto max-w-3xl space-y-8">
        <Breadcrumbs
          items={[
            { href: "/", label: "Home" },
            { href: "/money", label: "Money" },
            { href: `/money/${doc.frontmatter.slug}`, label: doc.frontmatter.title },
          ]}
        />

        <header className="space-y-3">
          <p className="text-sm text-muted-foreground">
            {doc.frontmatter.tier ? `Tier ${doc.frontmatter.tier}` : "Money"}{" "}
            {doc.frontmatter.readingTime ? `• ${doc.frontmatter.readingTime}` : null}
          </p>
          <p className="text-base text-muted-foreground">{doc.frontmatter.description}</p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link href="/money">
              <Button variant="secondary">Back to hub</Button>
            </Link>
            <Link href="/wealth">
              <Button variant="outline">Wealth</Button>
            </Link>
          </div>
        </header>

        <section className="space-y-6">
          <Markdown content={doc.content} />
        </section>

        {related.length > 0 ? (
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">Related Reading</h2>
            <div className="space-y-3">
              {related.map((d) => (
                <Card key={d.slug} className="transition-shadow hover:shadow-md">
                  <CardHeader>
                    <CardTitle className="text-base">{d.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <p className="text-sm text-muted-foreground">{d.description}</p>
                    <Link
                      href={`/money/${d.slug}`}
                      className="text-sm underline underline-offset-4 hover:text-foreground"
                    >
                      Read →
                    </Link>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>
        ) : null}
      </div>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
      />
    </div>
  );
}
