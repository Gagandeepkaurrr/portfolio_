export function pageHeaders(path: string, nonce: string, development: boolean, productionSite: boolean) {
  const preview = path === '/admin/preview/frame' || path.startsWith('/admin/preview/frame/');
  const headers = new Headers({
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'X-Frame-Options': preview ? 'SAMEORIGIN' : 'DENY',
    'Content-Security-Policy': [
      "default-src 'self'",
      `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${development ? " 'unsafe-eval'" : ''}`,
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' blob: data:",
      "font-src 'self'",
      `connect-src 'self'${development ? ' ws: wss:' : ''}`,
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      `frame-ancestors ${preview ? "'self'" : "'none'"}`,
    ].join('; '),
  });
  if (path === '/admin' || path.startsWith('/admin/') || !productionSite) headers.set('X-Robots-Tag', 'noindex, nofollow');
  return headers;
}
import { randomBytes } from 'node:crypto';

export function documentNonce() { return randomBytes(24).toString('base64'); }
