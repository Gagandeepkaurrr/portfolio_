import type { MetadataRoute } from "next";
import { getSite } from "@/lib/api/public";
export const dynamic = "force-dynamic";
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const { content } = await getSite();
  const origin = content.settings.site_url.replace(/\/$/, "");
  return [
    "",
    "/privacy",
    ...content.projects.map((p) => `/projects/${p.slug}`),
  ].map((path) => ({ url: `${origin}${path}` }));
}
