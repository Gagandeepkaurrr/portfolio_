// @vitest-environment node
import { describe, expect, it } from 'vitest';
import { pageHeaders } from './security.server';

describe('React document security', () => {
  it('uses the document nonce and prevents public framing/caching', () => {
    const headers = pageHeaders('/projects/weather-app', 'test-document-nonce', false, true);
    expect(headers.get('Content-Security-Policy')).toContain("'nonce-test-document-nonce'");
    expect(headers.get('Content-Security-Policy')).not.toContain('unsafe-eval');
    expect(headers.get('Content-Security-Policy')).toContain("frame-ancestors 'none'");
    expect(headers.get('Cache-Control')).toBe('no-store');
    expect(headers.get('X-Frame-Options')).toBe('DENY');
    expect(headers.has('X-Robots-Tag')).toBe(false);
  });
  it('permits only preview documents to frame themselves and keeps owner pages private', () => {
    const headers = pageHeaders('/admin/preview/frame/projects/example', 'nonce', false, true);
    expect(headers.get('Content-Security-Policy')).toContain("frame-ancestors 'self'");
    expect(headers.get('X-Frame-Options')).toBe('SAMEORIGIN');
    expect(headers.get('X-Robots-Tag')).toBe('noindex, nofollow');
    expect(pageHeaders('/admin/preview/frame-evil', 'nonce', false, true).get('X-Frame-Options')).toBe('DENY');
    expect(pageHeaders('/', 'nonce', true, false).get('X-Robots-Tag')).toBe('noindex, nofollow');
  });
});
