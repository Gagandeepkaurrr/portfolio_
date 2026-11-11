import "server-only";
import { cache } from "react";
import type { SiteEnvelope, PublicProject, Release } from "@/lib/types";
export class PublicApiError extends Error {
  constructor(
    public status: number,
    public requestId: string | null,
  ) {
    super(
      status === 404
        ? "This page could not be found."
        : "The portfolio is temporarily unavailable. Please try again.",
    );
  }
}
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
    throw new PublicApiError(503, null);
  }
  if (!response.ok)
    throw new PublicApiError(
      response.status,
      response.headers.get("x-request-id"),
    );
  return response.json() as Promise<T>;
}
export const getSite = cache(() => publicFetch<SiteEnvelope>("/site"));
export const getProject = cache((slug: string) =>
  publicFetch<{
    release: Release;
    requested_slug: string;
    canonical_slug: string;
    project: PublicProject;
  }>(`/projects/${encodeURIComponent(slug)}`),
);
