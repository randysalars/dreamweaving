import type { MetadataRoute } from "next";
import { marketingSalesGrowthArticles, marketingSalesGrowthHub } from "@/lib/marketing-sales-growth/articles";
import { listMoneySlugs } from "@/lib/money/content";

const baseUrl = "https://salars.net";

export default function sitemap(): MetadataRoute.Sitemap {
  const moneyRoutes = ["/money", ...listMoneySlugs().map((slug) => `/money/${slug}`)];

  const routes = [
    "/",
    "/ai",
    "/ai/operations",
    "/wealth",
    marketingSalesGrowthHub.href,
    ...marketingSalesGrowthArticles.map((a) => `${marketingSalesGrowthHub.href}/${a.slug}`),
    ...moneyRoutes,
    "/ai/operations/your_ai_morning_briefing_replacing_the_to-do_list_with_a_daily_intelligence_report",
    "/ai/operations/from_inbox_to_action_how_ai_converts_emails_into_tasks_decisions_or_delegation",
    "/ai/operations/the_zero-admin_business_designing_an_operation_where_ai_handles_all_routine_work",
  ];

  return routes.map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: "weekly",
    priority: 0.8,
  }));
}
