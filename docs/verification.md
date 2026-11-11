# Verification record

Verified locally on 12 November 2026 (India time). The application implements the supplied portfolio brief with a Next.js public site and owner editor, a FastAPI API, PostgreSQL, and private persistent media. This record distinguishes local verification from hosting work.

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
