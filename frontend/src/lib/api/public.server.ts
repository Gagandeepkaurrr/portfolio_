import type { SiteEnvelope, PublicProject, Release } from "@/lib/types";
const base = () =>
  process.env.API_INTERNAL_URL || "http://127.0.0.1:8100/api/v1";
export async function publicFetch<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${base()}${path}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
  } catch {
    throw new Response('Portfolio temporarily unavailable', { status: 503 });
  }
  if (!response.ok)
    throw new Response(response.status === 404 ? 'Not found' : 'Portfolio temporarily unavailable', { status: response.status === 404 ? 404 : 503 });
  return response.json() as Promise<T>;
}
export const getSite = () => publicFetch<SiteEnvelope>("/site");
export const getProject = (slug: string) =>
  publicFetch<{
    release: Release;
    requested_slug: string;
    canonical_slug: string;
    project: PublicProject;
  }>(`/projects/${encodeURIComponent(slug)}`);
