// @vitest-environment node
import { afterEach, describe, expect, it, vi } from 'vitest';
import { proxyApiRequest } from './proxy.server';

afterEach(() => vi.unstubAllGlobals());
describe('standalone same-origin API proxy', () => {
  it('preserves multipart bytes, CSRF, origin and opaque session cookies', async () => {
    const upstream = vi.fn(async (_url: string, init: RequestInit) => {
      expect(new Headers(init.headers).get('cookie')).toBe('portfolio_session=opaque');
      expect(new Headers(init.headers).get('origin')).toBe('http://localhost:3000');
      expect(new Headers(init.headers).get('x-csrf-token')).toBe('csrf-value');
      expect(new Headers(init.headers).has('x-forwarded-for')).toBe(false);
      expect(await new Response(init.body).text()).toBe('multipart-body');
      return new Response('received', { status: 201, headers: { 'Set-Cookie': 'portfolio_session=rotated; HttpOnly; Path=/', 'X-Request-ID': 'receipt', 'Content-Encoding': 'gzip', 'Content-Length': '8' } });
    });
    vi.stubGlobal('fetch', upstream);
    const request = new Request('http://localhost:3000/api/v1/admin/media?kind=image', { method: 'POST', headers: { Cookie: 'portfolio_session=opaque', Origin: 'http://localhost:3000', 'X-CSRF-Token': 'csrf-value', 'Content-Type': 'multipart/form-data; boundary=example', 'X-Forwarded-For': 'spoofed' }, body: 'multipart-body' });
    const result = await proxyApiRequest(request, 'http://127.0.0.1:8100/api/v1');
    expect(upstream.mock.calls[0][0]).toBe('http://127.0.0.1:8100/api/v1/admin/media?kind=image');
    expect(result.status).toBe(201);
    expect(result.headers.get('Set-Cookie')).toContain('rotated');
    expect(result.headers.get('X-Request-ID')).toBe('receipt');
    expect(result.headers.has('Content-Encoding')).toBe(false);
    expect(result.headers.get('Cache-Control')).toBe('no-store');
    expect(await result.text()).toBe('received');
  });
  it('fails closed on upstream errors and never follows redirects', async () => {
    vi.stubGlobal('fetch', vi.fn(async (_url, init) => { expect(init.redirect).toBe('manual'); throw new Error('private upstream detail'); }));
    const response = await proxyApiRequest(new Request('http://localhost/api/v1/site'), 'http://127.0.0.1:8100/api/v1');
    expect(response.status).toBe(503);
    expect(await response.text()).not.toContain('private upstream detail');
  });
});
