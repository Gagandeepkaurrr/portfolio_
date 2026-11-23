import { handleRequest } from '@vercel/react-router/entry.server';
import type { AppLoadContext, EntryContext } from 'react-router';
import { documentNonce, pageHeaders } from '@/lib/security.server';

export default async function render(request: Request, status: number, headers: Headers, context: EntryContext, loadContext: AppLoadContext) {
  const nonce = (context.staticHandlerContext.loaderData.root as { nonce?: string } | undefined)?.nonce || documentNonce();
  const response = await handleRequest(request, status, headers, context, loadContext, { nonce });
  pageHeaders(new URL(request.url).pathname, nonce, process.env.NODE_ENV === 'development', process.env.APP_ENV === 'production').forEach((value, name) => response.headers.set(name, value));
  return response;
}

export function handleDataRequest(response: Response) {
  response.headers.set('Cache-Control', 'no-store');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Robots-Tag', 'noindex, nofollow');
  return response;
}
