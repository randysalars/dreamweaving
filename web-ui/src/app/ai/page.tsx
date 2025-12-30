import React from "react";
import Link from "next/link";
import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export default function AIHubPage() {
  return (
    <div className="min-h-screen bg-background py-12 px-6">
      <div className="mx-auto max-w-6xl space-y-12">
        <div className="space-y-4">
          <h1 className="text-4xl font-semibold tracking-tight text-foreground">AI</h1>
          <p className="text-base text-muted-foreground max-w-3xl">
            Explore practical AI playbooks and content hubs designed for operators, founders, and teams.
          </p>
        </div>

        <section className="space-y-6">
          <h2 className="text-2xl font-semibold text-foreground">Explore AI Dimensions</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* HUB_CARDS_START */}
            <Card className="transition-shadow hover:shadow-md">
              <CardHeader>
                <CardTitle className="text-lg">AI as the Business Operating System</CardTitle>
                <CardDescription className="line-clamp-3">
                  Systems and operating rituals for running work with AI: prioritization, delegation, and daily execution loops.
                </CardDescription>
              </CardHeader>
              <CardFooter>
                <Link href="/ai/operations" className="w-full">
                  <Button variant="ghost" className="w-full justify-between gap-2">
                    Explore <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </CardFooter>
            </Card>

            <Card className="transition-shadow hover:shadow-md">
              <CardHeader>
                <CardTitle className="text-lg">Marketing, Sales &amp; Growth</CardTitle>
                <CardDescription className="line-clamp-3">
                  SEO + AEO-ready playbooks for content systems, living personas, offer validation, and sales workflows—powered by AI.
                </CardDescription>
              </CardHeader>
              <CardFooter>
                <Link href="/marketing-sales-growth" className="w-full">
                  <Button variant="ghost" className="w-full justify-between gap-2">
                    Open Hub <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </CardFooter>
            </Card>

            {/* HUB_CARDS_END */}
          </div>
        </section>
      </div>
    </div>
  );
}
