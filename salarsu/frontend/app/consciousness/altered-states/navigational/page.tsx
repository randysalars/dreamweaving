import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, HelpCircle } from "lucide-react";
import { getSiteUrl } from "@/lib/siteUrl";

const pageUrl = `${getSiteUrl()}/consciousness/altered-states/navigational`;

export const metadata: Metadata = {
  title: "Navigational & Exploratory Prompts | Altered States",
  description: "Comparative questions helping readers navigate the landscape of altered states.",
  alternates: { canonical: pageUrl },
  openGraph: {
    title: "Navigational & Exploratory Prompts",
    description: "Comparative questions helping readers navigate the landscape of altered states.",
    url: pageUrl,
    type: "website",
  },
};

export default function NavigationalPage() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-4xl space-y-8">
          <div className="space-y-2">
            <Link
              href="/consciousness/altered-states"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Altered States
            </Link>
          </div>

          <div className="space-y-3">
            <h1 className="text-4xl font-semibold tracking-tight text-foreground">
              Navigational & Exploratory Prompts
            </h1>
            <p className="text-lg text-muted-foreground">
              Comparative questions helping readers navigate the landscape of altered states.
            </p>
          </div>

          <section className="space-y-4">
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">
              Questions in this category
            </h2>
            <div className="grid gap-3">
              <Link
                href="/consciousness/altered-states/navigational/which-altered-states-occur-most-commonly"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Which altered states occur most commonly?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/navigational/which-altered-states-are-easiest-to-access"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Which altered states are easiest to access?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/navigational/which-altered-states-are-hardest-to-describe"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Which altered states are hardest to describe?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/navigational/which-altered-states-change-identity-perception"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Which altered states change identity perception?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/navigational/which-altered-states-feel-most-meaningful"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Which altered states feel most meaningful?</span>
              </Link>
              <Link
                href="/consciousness/altered-states/navigational/which-altered-states-require-the-most-care"
                className="flex items-start gap-3 rounded-lg border border-border bg-card/30 p-4 transition-colors hover:bg-card/50"
              >
                <HelpCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <span className="text-foreground">Which altered states require the most care?</span>
              </Link>
            </div>
          </section>

          <section className="pt-6 border-t border-border">
            <Link
              href="/consciousness/altered-states"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              View all Altered States categories
              <ArrowLeft className="h-4 w-4 rotate-180" />
            </Link>
          </section>
        </div>
      </main>
    </div>
  );
}
