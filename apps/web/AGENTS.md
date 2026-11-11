# Frontend conventions

This is a React + Vite application using React Router framework mode with SSR.
Route declarations live in src/routes.ts; src/root.tsx owns the document.
Keep server-only configuration and fetches in .server.ts modules. FastAPI
remains the sole authority for authentication, drafts, publication and media.
Browser API requests use /api/v1. Preserve the shared AdminProvider across
owner routes so navigation cannot discard unsaved edits.

Run lint, typecheck, unit tests and build through the root pnpm scripts.
The isolated make e2e command exercises real PostgreSQL/API/browser workflows.
