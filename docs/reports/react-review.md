# Independent React migration review

Reviewed 12 November 2026 against base `4905714`, the React migration design and implementation plan, and the uncommitted `codex/react-vite` changes. Product code was not edited by this reviewer.

## Findings

No actionable migration defect was confirmed. The reviewed implementation retains public server rendering, live metadata, project aliases and HTTP error statuses. The shared owner provider remains above the owner route outlet, and private drafts, previews and media continue to depend on backend session authorization. Server-only fetch configuration is confined to server modules; the inspected client build contains none of the server fetch/proxy helpers or sensitive environment variable names checked.

The checked Vercel configuration selects React Router and the workspace build commands. Its separate configuration helper preserves existing settings while adding the direct API rewrite. The deployment guide explicitly requires the real API hostname and rewrite before launching uploads. The Render Blueprint's database connection string is compatible with the new psycopg URL normalization. Infrastructure was not provisioned or changed during review.

## Independent verification

Read-only requests through React Router's production request handler using the existing Vercel-preset server artifact and a mocked backend confirmed:

- Home/project HTML and every emitted script nonce agree with the document CSP.
- Owner/login/preview documents are no-store and noindex; preview framing is restricted to the same origin.
- Project aliases return 308, absent projects and unknown pages return 404, and an unavailable backend returns 503 without the underlying error detail.
- Sitemap and filtered client data responses retain no-store behavior.
- The standalone resource proxy preserves a JSON POST body and multiple Set-Cookie headers; a DELETE response remains an empty 204.

Both configuration-helper tests passed independently. The coordinator's existing frontend, backend, container and full browser checks were not unnecessarily repeated.

## Evidence boundaries

The migration is suitable for the coordinator's final verification and repository handoff. This review does not establish a live deployment. Actual Vercel-to-Render routing, HTTPS cookies, near-limit uploads, trusted source-IP accounting and remote backup/recovery remain the deployment acceptance checks documented in `docs/vercel-render.md`.
