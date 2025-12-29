import React from "react";
import Link from "next/link";
import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export default function AIHubPage() {
  return (
    <div className="min-h-screen bg-slate-50 py-12 px-6">
      <div className="mx-auto max-w-6xl space-y-12">
        <div className="space-y-4">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900">AI Hub</h1>
          <p className="text-lg text-slate-600">
            Explore AI content hubs and generated resources.
          </p>
        </div>

        <section className="space-y-6">
          <h2 className="text-2xl font-semibold">Sections</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* HUB_CARDS_START */}
            <Card className="border-slate-200 bg-white transition-shadow hover:shadow-md">
              <CardHeader>
                <CardTitle className="text-lg">Operations</CardTitle>
                <CardDescription className="line-clamp-3">
                  Systems, workflows, and practical playbooks for running work with AI.
                </CardDescription>
              </CardHeader>
              <CardFooter>
                <Link href="/ai/operations" className="w-full">
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

