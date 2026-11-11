# React Migration Implementation Plan

> Use superpowers:executing-plans for implementation and superpowers:requesting-code-review for independent final review.

**Goal:** Replace Next.js with React + Vite while preserving the complete portfolio and owner application.
**Architecture:** React Router route loaders and SSR; existing React components and FastAPI contracts; same-origin API proxy and PostgreSQL unchanged.
**Tech Stack:** React19, React Router7.18.5, Vite8.3.8, TypeScript, FastAPI/PostgreSQL.
**Spec:** docs/superpowers/specs/2026-11-12-react-migration-design.md

## Global constraints
- Preserve content, visual design, private drafts, CSRF/cookies and media authorization.
- No Next dependency/import/config/build output in the resulting active frontend.
- No credentials, private media, backups or database migrations in this change.
- Public routes retain SSR, metadata, aliases and real404 responses.

## Review focus
- Navigation must not remount owner state or lose unsaved edits.
- Streaming API forwarding must preserve cookies, Origin, multipart bytes and errors.
- CSP nonces must match SSR and hydration, including preview frames.
- API outage/hidden projects must not render private data or false successful pages.
- Container and Vercel builds must use the new entry points and output directories.

### Task1: React runtime and routing
- [x] Add failing framework-removal and SSR/security regressions.
- [x] Replace Next packages/config with React Router/Vite, migrate routes, links/navigation and server API module.
- [x] Retain public metadata/sitemap, errors, CSP and API routing.
- [x] Run lint/type checks/unit tests and build.

### Task2: Operations and documentation
- [x] Update Docker, E2E runner, CI, ignored artifacts and Vercel/Render instructions.
- [x] Verify production Node and container runtime, same-origin proxy and Vercel build preset.

### Task3: Acceptance and handoff
- [x] Run make verify and isolated real-stack browser acceptance.
- [x] Independent review; fix confirmed issues and document verification.
- Repository handoff: commit and push after the checks above; the final chat records the remote commit and CI outcome.
