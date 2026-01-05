import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type ContentCardProps = {
  title: string;
  description: string;
  href: string;
  badge?: string;
};

export function ContentCard({ title, description, href, badge }: ContentCardProps) {
  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <CardTitle className="text-base leading-snug">{title}</CardTitle>
          {badge ? (
            <span className="shrink-0 rounded-full border px-2 py-1 text-xs text-muted-foreground">
              {badge}
            </span>
          ) : null}
        </div>
        <CardDescription className="leading-relaxed">{description}</CardDescription>
      </CardHeader>
      <CardFooter>
        <Link href={href} className="w-full">
          <Button variant="ghost" className="w-full justify-between gap-2">
            Explore <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}

