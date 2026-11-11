export function loader() {
  const origin = process.env.PUBLIC_ORIGIN || 'http://localhost:3000';
  const policy = process.env.APP_ENV === 'production' ? `Allow: /\nDisallow: /admin\nDisallow: /api/\nSitemap: ${origin}/sitemap.xml` : 'Disallow: /';
  return new Response(`User-agent: *\n${policy}\n`, { headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' } });
}
