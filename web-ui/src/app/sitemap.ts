import type { MetadataRoute } from "next";

const baseUrl = "https://salars.net";

export default function sitemap(): MetadataRoute.Sitemap {
  const routes = ["/"];

  return routes.map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: "weekly",
    priority: 0.8,
  }));
}
