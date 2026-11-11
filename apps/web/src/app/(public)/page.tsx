import type { Metadata } from "next";
import { headers } from "next/headers";
import { getSite } from "@/lib/api/public";
import { PortfolioHome, PublicShell } from "@/components/public";
export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  const { content } = await getSite();
  const { settings: s } = content;
  return {
    title: s.default_seo_title,
    description: s.default_seo_description,
    alternates: { canonical: s.site_url },
    openGraph: {
      title: s.default_seo_title,
      description: s.default_seo_description,
      url: s.site_url,
      type: "website",
      images: [
        {
          url: `${s.site_url.replace(/\/$/, "")}/social.svg`,
          width: 1200,
          height: 630,
        },
      ],
    },
    twitter: { card: "summary_large_image" },
  };
}
export default async function Home() {
  const { content } = await getSite();
  const p = content.profile;
  const person = {
    "@context": "https://schema.org",
    "@type": "Person",
    name: p.full_name,
    url: content.settings.site_url,
    sameAs: [p.github_url, p.linkedin_url].filter(Boolean),
  };
  return (
    <PublicShell content={content}>
      <script
        nonce={(await headers()).get("x-nonce") || undefined}
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(person).replace(/</g, "\\u003c"),
        }}
      />
      <PortfolioHome content={content} />
    </PublicShell>
  );
}
