import { useLoaderData, useRouteLoaderData, type MetaFunction } from 'react-router';
import { getSite } from '@/lib/api/public.server';
import { PortfolioHome, PublicShell } from '@/components/public';
import type { loader as rootLoader } from '@/root';

export const loader = () => getSite();
export const meta: MetaFunction<typeof loader> = ({ data }) => {
  if (!data) return [{ title: 'Gagandeep Kaur' }];
  const s = data.content.settings;
  return [
    { title: s.default_seo_title }, { name: 'description', content: s.default_seo_description },
    { tagName: 'link', rel: 'canonical', href: s.site_url },
    { property: 'og:title', content: s.default_seo_title }, { property: 'og:description', content: s.default_seo_description },
    { property: 'og:url', content: s.site_url }, { property: 'og:type', content: 'website' },
    { property: 'og:image', content: `${s.site_url.replace(/\/$/, '')}/social.svg` },
    { name: 'twitter:card', content: 'summary_large_image' },
  ];
};
export default function Home() {
  const { content } = useLoaderData<typeof loader>();
  const root = useRouteLoaderData<typeof rootLoader>('root');
  const p = content.profile;
  const person = { '@context': 'https://schema.org', '@type': 'Person', name: p.full_name, url: content.settings.site_url, sameAs: [p.github_url, p.linkedin_url].filter(Boolean) };
  return <PublicShell content={content}><script nonce={root?.nonce} type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(person).replace(/</g, '\\u003c') }} /><PortfolioHome content={content} /></PublicShell>;
}
