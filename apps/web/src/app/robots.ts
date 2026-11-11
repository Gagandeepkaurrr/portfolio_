import type { MetadataRoute } from "next";
export default function robots(): MetadataRoute.Robots {
  const origin = process.env.PUBLIC_ORIGIN || "http://localhost:3000";
  return {
    rules: { userAgent: "*", allow: "/", disallow: ["/admin", "/api/"] },
    sitemap: `${origin}/sitemap.xml`,
  };
}
