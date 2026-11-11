# Verification record

## React migration — current application

On 12 November 2026 (India time), the user requested replacing Next.js with React and preparing deployment configuration. The frontend now uses React 19, Vite and React Router 7.18.5 with server rendering. Next.js dependencies, routing, middleware and configuration have been removed. FastAPI, PostgreSQL, the visual design and owner workflows are preserved.

Executed on the migration:

- `make verify`: passed; 32 real PostgreSQL backend tests, 12 frontend unit/component tests, 2 Vercel configuration tests, 5 operational checks, Ruff/mypy, ESLint/TypeScript, contract drift and production build.
- `make e2e`: all 14 browser tests passed against the Vite development server.
- `E2E_WEB_MODE=production make e2e`: all 14 browser tests passed against the built React SSR server and its streaming API proxy. This includes authentication, editing across routes, save conflicts, draft previews, publication/restore, contact persistence and media upload/crop.
- Production web Docker image built and ran as UID10001. Public/project SSR, missing-project404, canonical tags, fresh matching script/CSP nonces, owner noindex, preview-only same-origin framing, sitemap, static assets and API health forwarding passed.
- `VERCEL=1 pnpm build`: the provider-preset server bundle built successfully, including after the patched AJV dependency override.
- Production dependency audit: zero advisories after replacing the Vercel adapter's vulnerable transitive AJV version with 8.20.0.
- Independent review found no actionable migration defect; see [React migration review](reports/react-review.md). Production screenshots were refreshed and visually inspected.

Deployment source now includes `apps/web/vercel.json`, a tested helper for the actual Render API rewrite, and a schema-validated `render.yaml` with automatic PostgreSQL wiring and persistent private media. Generic provider PostgreSQL URLs normalize to the pinned psycopg driver; a regression checks credentials/query preservation. No data/schema migration is required.

The actual Render API URL and final Vercel origin remain operator configuration. The base Vercel file contains no invented hostname; run the documented configuration helper with the real API origin before launching uploads. No public deployment or paid service creation occurred. HTTPS cookie, large-upload, source-IP and remote recovery checks remain in the [hosting guide](vercel-render.md).

## Initial implementation evidence

The following records checks from the initial implementation before the React migration. Persistence/recovery behavior is unchanged. It is retained as historical evidence, not a claim that the current frontend uses Next.js.

## Final checks

`make verify` exited successfully on the final product code:

| Check | Result |
| --- | --- |
| Backend Ruff and mypy | Clean; 18 typed source modules |
| Backend integration suite | 31 passed against real PostgreSQL 17.11 |
| Frontend ESLint and strict TypeScript | Clean |
| Generated OpenAPI/TypeScript contract drift | No differences |
| Frontend unit/component suite | 8 passed |
| Operational archive and database-target safety suite | 5 passed |
| Next.js production build and Python compilation | Passed |

The complete isolated `make e2e` run passed **13/13** Playwright acceptance tests. It used a fresh random PostgreSQL database, temporary media and ephemeral owner credentials, then removed its test state. Tests exercise public pages and project routes, contact receipt/retry behavior, 320/360/768/1440px layouts, accessibility scans, login, preserved draft edits, stale save conflicts, private previews, publication/history restore, inbox operations, media upload/crop and mobile owner-menu focus. A separate landscape-crop browser check also passed. Screenshots are retained under `docs/screenshots/`.

The production dependency audit reported zero advisories at verification time. That is a point-in-time result, not a guarantee against future vulnerabilities. Accessibility scans and manual layout checks are not a formal WCAG certification; no field performance or Lighthouse score is claimed.

## Persistence and deployment rehearsal

Both production application images built and ran as non-root UID 10001 behind nginx with PostgreSQL. The isolated local stack returned public/project pages, served a validated real PDF, and retained a synthetic contact and PDF across database/API/web/proxy restarts. Browser smoke checks found no JavaScript/console errors, and verified production nonce-based CSP without `unsafe-eval`, no-store responses and correct preview frame permissions.

A coordinated database/media backup and isolated restore compared draft/release/contact/media identities and content hashes, the live release pointer, migration state, archive hashes and stored bytes. A populated restore preserved contact/PDF data and invalidated restored sessions. Disposable rehearsal volumes were removed. Backups remain private and Git-ignored. See [operations evidence](reports/ops.md) and [recovery instructions](backup-restore.md).

The actual supplied résumé was validated and published locally as release 2. No default owner, fabricated portrait, project screenshot or synthetic contact remains in the development database. The résumé and database are runtime data, so a new clone or hosting deployment must import/upload the résumé separately. Create the real owner interactively with `make admin-create`.

## Review and remaining inputs

Independent review examined backend authorization, transactions, media/public projections, owner editing, public rendering and operational tooling. Both findings were resolved: conflicting image/PDF references now fail before mutation with a regression test, and the Render guide explains shared-proxy rate limits and the required hosted source-IP verification. See [review](reports/review.md), [backend](reports/backend.md) and [owner UI](reports/admin.md) reports.

Optional content still needed from the owner: a real portrait, project screenshots and project-specific repository links. The UI uses explicit placeholders and omits unavailable project repository actions.

Public hosting was not performed. Follow [Vercel + Render + PostgreSQL](vercel-render.md), including its HTTPS cookie, trusted proxy/source-IP, near-limit upload and remote backup checks. PostgreSQL is the chosen database; no TiDB migration is included. SMTP delivery was not configured or tested, although contact messages persist without SMTP. Only the local persistent-filesystem media backend is implemented; S3 is not claimed.
