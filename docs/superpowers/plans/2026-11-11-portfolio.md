# Gagandeep Kaur portfolio implementation plan

> **For agentic workers:** Use superpowers:executing-plans or superpowers:subagent-driven-development for bounded implementation, with dispatching-parallel-agents for independent file ownership.

**Goal:** Implement the complete local portfolio, CMS, validated media, publishing, inbox and operational tooling described in the supplied brief.

**Architecture:** Next.js public SSR and owner UI consume FastAPI's typed API. PostgreSQL is authoritative. One origin; private filesystem media; immutable releases.

**Tech Stack:** Next.js, React, TypeScript, Tailwind, TanStack Query, React Hook Form, Zod; FastAPI, SQLAlchemy, psycopg, Pydantic, Alembic, Argon2, Pillow, pypdf; PostgreSQL; Playwright, Vitest, pytest.

**Spec:** `docs/project-brief.txt`; design decisions in `docs/architecture.md`.

## Global constraints
- Preserve all supplied facts and exact project/demo/profile links. Never invent missing personal details.
- Use snake_case wire keys and strict schemas; public responses must never contain raw private snapshots.
- Browser API prefix `/api/v1`; server API_INTERNAL_URL; PUBLIC_ORIGIN `http://localhost:3000` locally.
- PostgreSQL transactions and actual tests, never localStorage or SQLite as authoritative storage.
- Save/preview/publish are separate actions. Owner bootstrap requires a private interactive password.
- Keep uploaded media and credentials outside Git; no public hosting deployment or external messages. The user subsequently authorized pushing finished code to Gagandeepkaurrr/portfolio_.

## Review focus
- Retry after an ambiguous response must not duplicate contacts or publications.
- Hidden draft-only fields/media must not escape through SSR, metadata, redirects or public bytes.
- Concurrent saves and publish preconditions must reject stale edits without lost changes.
- Upload/crop/deletion must preserve immutable bytes and retained references.
- API outages, invalid input and expired sessions must produce usable errors, preserving local edits.

### Task 1: Backend and authoritative contracts
**Owner/files:** backend agent exclusively `apps/api/**`, backend report.
**Interfaces:** Implement all `/api/v1` endpoints from brief sections 11–17; public profile and collections preserve canonical keys, MediaRef additionally resolves `url`, `variants` and dimensions; public profile adds `resume_available`, removes `resume_asset_id` and hidden phone; preview uses same shape with private URLs. API errors follow supplied envelope. Pagination `{items,next_cursor,has_more}`.
- [x] Write and run failing behavior tests for seed content, draft isolation/staleness, publish idempotency/aliases, sessions/CSRF, contact persistence/retries and media authorization.
- [x] Implement strict Pydantic schemas, SQLAlchemy tables, Alembic migration and idempotent seed.
- [x] Implement services and routes, secure owner CLI, media import/crop/deletion, maintenance, OpenAPI export.
- [x] Run real PostgreSQL tests and produce `docs/reports/backend.md` with evidence and limitations.

### Task 2: Public frontend and shared workspace
**Owner/files:** root `apps/web` excluding admin components/routes/provider owned by task 3; root package config, browser tests.
**Interfaces:** Fetch `/site` aggregate once per render; content uses section 11 types. Export `PortfolioHome({content})`, `ProjectDetail({project,projects})` and `PublicShell({content,children})` from `src/components/public` for authenticated previews. Contact sends stable UUID idempotency key and immutable payload across ambiguous retries.
- [x] Add tests that catch changed-key retries, invalid form submission and hidden navigation.
- [x] Implement editorial home, project template, privacy, errors, SEO, sitemap, menus and real contact form.
- [x] Add strict TypeScript contracts checked against backend OpenAPI, locally served fonts, responsive CSS.
- [x] Build and inspect at 320/360/768/1440 widths, verify navigation and contact through real API.

### Task 3: Owner editing application
**Owner/files:** admin agent exclusively `apps/web/src/app/admin/**`, `src/components/admin/**`, `src/providers/**`, `src/styles/admin.css`, `src/lib/api/admin.ts` and admin tests.
**Interfaces:** Use backend endpoints from brief; all owner writes include CSRF; draft saves require quoted `draft-N` ETag. Content in provider persists across tabs; no raw JSON as main editor. Use shared public components for previews; typed imports from `@/lib/types` when available.
- [x] Test save conflict and preserve-in-memory behavior before implementation.
- [x] Implement login/session, protected shell, complete field editors and collection controls, overview, save/publish review, history restore, preview viewport.
- [x] Implement media upload/picker, crop numeric controls, alt text, ordered galleries, inbox pagination/read/archive/delete and password change.
- [x] Typecheck and produce `docs/reports/admin.md` with evidence and limitations.

### Task 4: Reproducible operations
**Owner/files:** ops agent exclusively `compose*.yaml`, `Makefile`, `.env.example`, Dockerfiles, `infra/**`, `scripts/**`, `.github/**`, README and operational docs.
**Interfaces:** Backend CLI `uv run python -m app.cli` subcommands seed, admin-create, admin-reset, import-resume, cleanup, export-openapi; API `app.main:app`; backend deps uv; web pnpm workspace named `@portfolio/web`. Database local exposed loopback 55433. API defaults configured through root .env (scripts must load it). Node 26.13.0, Python 3.12, PostgreSQL 17 pinned image version after registry check.
- [x] Implement every Make entry from brief with real checks/failure exits.
- [x] Configure Docker, persistent private media, nginx same-origin/TLS example, safe startup/migration ordering, CI.
- [x] Add coordinated protected DB/media backup and restore into an explicitly named empty target with hash verification/session invalidation.
- [x] Execute recovery rehearsal and document exact commands and limitations in report.

### Task 5: Integration and final review
**Owner:** root; fresh review agent after implementations.
- [x] Integrate contracts, import supplied résumé via validated pipeline, bootstrap local services without default owner credentials.
- [x] Run backend suite, frontend unit/types/build and real browser acceptance/a11y checks; fix observed issues.
- [x] Review privacy, concurrency, uploads and operational scripts; update verification report honestly.
- [x] Deliver local preview, setup/admin commands and remaining optional inputs.
