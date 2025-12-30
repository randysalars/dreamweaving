import React from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export default function HubPage() {
  return (
    <div className="min-h-screen bg-background py-12 px-6">
      <div className="max-w-6xl mx-auto space-y-12">
        <div className="space-y-4">
            <h1 className="text-4xl font-semibold tracking-tight text-foreground">Operations</h1>
            <p className="text-base text-muted-foreground">Systems, workflows, and practical playbooks for running work with AI.</p>
        </div>
        
        
        <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Daily Work</h2>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                 <Card className="hover:shadow-md transition-shadow">
                    <CardHeader>
                        <CardTitle className="text-lg line-clamp-2">Your AI Morning Briefing: Replacing the To-Do List With a Daily Intelligence Report</CardTitle>
                        <CardDescription className="line-clamp-3">Read full article...</CardDescription>
                    </CardHeader>
                    <CardFooter>
                        <Link href="your_ai_morning_briefing_replacing_the_to-do_list_with_a_daily_intelligence_report" className="w-full">
                            <Button variant="ghost" className="w-full justify-between gap-2">
                                Read Article <ArrowRight className="h-4 w-4" />
                            </Button>
                        </Link>
                    </CardFooter>
                 </Card>
            </div>
        </section>
        
      </div>
    </div>
  );
}
