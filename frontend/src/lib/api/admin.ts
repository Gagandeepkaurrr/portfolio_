export interface FieldError { path: string | (string | number)[]; message: string }
export class ApiError extends Error {
  constructor(public status: number, message: string, public code = 'REQUEST_FAILED', public details: Record<string, unknown> = {}, public requestId?: string) { super(message); this.name = 'ApiError'; }
  get fieldErrors(): FieldError[] { return Array.isArray(this.details.field_errors) ? this.details.field_errors as FieldError[] : []; }
}
export async function adminApi<T>(path: string, options: RequestInit & { csrf?: string } = {}): Promise<T> {
  const { csrf, ...init } = options;
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData)) headers.set('Content-Type', 'application/json');
  if (csrf) headers.set('X-CSRF-Token', csrf);
  let response: Response;
  try { response = await fetch(`/api/v1${path}`, { ...init, headers, credentials: 'same-origin', cache: 'no-store', signal: init.signal ?? AbortSignal.timeout(30000) }); }
  catch (error) { if (error instanceof DOMException && error.name === 'AbortError') throw error; throw new ApiError(0, 'The server could not be reached. Your changes are still here. Please try again.'); }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new ApiError(response.status, data.error?.message ?? `The request could not be completed (${response.status}).`, data.error?.code, data.error?.details, data.request_id ?? response.headers.get('X-Request-ID') ?? undefined);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
export const jsonBody = (value: unknown) => JSON.stringify(value);
