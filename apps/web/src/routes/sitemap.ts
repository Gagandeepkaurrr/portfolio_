import { getSite } from '@/lib/api/public.server';
function xml(value: string) { return value.replace(/[<>&"']/g, character => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;' })[character]!); }
export async function loader() {
  const { content } = await getSite();
  const origin = content.settings.site_url.replace(/\/$/, '');
  const paths = ['', '/privacy', ...content.projects.map(project => `/projects/${project.slug}`)];
  return new Response(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${paths.map(path => `<url><loc>${xml(origin + path)}</loc></url>`).join('')}</urlset>`, { headers: { 'Content-Type': 'application/xml; charset=utf-8', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' } });
}
