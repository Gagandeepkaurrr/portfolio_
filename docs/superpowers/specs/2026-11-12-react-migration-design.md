# React frontend migration

The user requested converting Next.js to React. Keep the existing design, content, FastAPI/PostgreSQL authority, owner editor and publishing/media/contact behavior. Replace all Next-specific runtime, routing, metadata, middleware and build dependencies.

Use React 19 with Vite and React Router framework mode (7.18.5, compatible with the current Vercel adapter). Public route loaders preserve server-rendered content, status codes, live metadata, sitemap and aliases. Owner routes share one persistent AdminProvider and use React Router client navigation. No backend schema or stored data migration is needed.

A plain client-only Vite SPA would remove server-rendered portfolio content and HTTP project404/redirect semantics; a hand-written SSR server would add unnecessary infrastructure. React Router supplies those capabilities with Vite and a supported Vercel preset. This implementation choice follows the user's explicit migration request and preserves the already-built product.

Retain same-origin /api/v1 routing, no-store content, per-document CSP nonces, owner noindex and preview-only self framing. Development uses Vite's fixed API proxy; container ingress continues nginx. A streaming resource proxy supports a standalone Node run; Vercel deployment must use an external API rewrite to keep uploads out of frontend functions.

Verify the full existing test suite plus HTML-without-JavaScript, HTTP404, security headers, navigation and production build/runtime checks. Update README, Docker, CI and deployment guide. Commit and push the verified migration to the existing authorized repository.
