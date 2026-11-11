const requestHeaders = ['accept', 'content-type', 'cookie', 'origin', 'referer', 'x-csrf-token', 'if-match', 'idempotency-key', 'range', 'if-none-match'];

/** The destination is operator configuration, never a URL supplied by a visitor. */
export async function proxyApiRequest(request: Request, base = process.env.API_INTERNAL_URL || 'http://127.0.0.1:8100/api/v1') {
  const url = new URL(request.url);
  if (!url.pathname.startsWith('/api/v1/')) return new Response('Not found', { status: 404 });
  const headers = new Headers();
  for (const name of requestHeaders) {
    const value = request.headers.get(name);
    if (value !== null) headers.set(name, value);
  }
  const init: RequestInit & { duplex: 'half' } = {
    method: request.method, headers, redirect: 'manual', duplex: 'half',
    body: ['GET', 'HEAD'].includes(request.method) ? undefined : request.body,
    signal: AbortSignal.any([request.signal, AbortSignal.timeout(60000)]),
  };
  try {
    const upstream = await fetch(`${base.replace(/\/$/, '')}${url.pathname.slice('/api/v1'.length)}${url.search}`, init);
    const responseHeaders = new Headers(upstream.headers);
    // Node fetch decompresses upstream bytes; preserve cookies, status and request IDs.
    for (const name of ['content-encoding', 'content-length', 'transfer-encoding', 'connection']) responseHeaders.delete(name);
    responseHeaders.set('Cache-Control', 'no-store');
    return new Response(request.method === 'HEAD' ? null : upstream.body, { status: upstream.status, headers: responseHeaders });
  } catch {
    return Response.json({ error: { code: 'API_UNAVAILABLE', message: 'The service is temporarily unavailable. Please try again.' } }, { status: 503, headers: { 'Cache-Control': 'no-store' } });
  }
}
