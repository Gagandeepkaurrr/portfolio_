# Portfolio architecture

The supplied project brief in `docs/project-brief.txt` is the product specification. The user requested implementation of that brief. Ordinary engineering choices are made here without additional approval gates. Work remains local; no public deployment, purchases, or external messages are part of this implementation.

Next.js App Router renders one no-store public snapshot obtained from FastAPI. FastAPI alone owns PostgreSQL content, owner sessions, private media and contact storage. Browser requests use the same origin at `/api/v1`. Local origin is `http://localhost:3000`; API listens privately at `http://127.0.0.1:8100`. Production nginx routes both services behind one TLS origin.

One typed JSONB draft, revision preconditions, and immutable release snapshots preserve editorial isolation. Publication locks draft then state then media. Public projection removes hidden items and phone values, resolves media to authorized URLs, and never exposes storage keys. Session and CSRF values stay out of persistent browser storage. Uploads use a private filesystem volume.

Design: A Personal Journal of Building. Instrument Serif and Manrope, warm ivory #F5F1E8, deep teal #153E3B, sage #E4EBE4 and copper #A65F42. Portrait remains the intentional GK placeholder until the owner uploads a real image. Project artwork is clearly labeled and does not pretend to be a screenshot.

Alternatives considered: a static portfolio cannot fulfill the owner publishing/inbox requirements; a single JavaScript backend conflicts with the requested FastAPI boundary. The selected monorepo follows the supplied architecture. npm registry version resolution will be locked with pnpm; Python uses uv on 3.12; local Node 26 is a supported LTS. PostgreSQL 17 is supported. Exact versions are recorded in lockfiles and verification results.

Optional SMTP is disabled unless explicitly configured; stored messages are reported as received, never delivered emails. S3 is an extension point, not an implemented storage backend. No portrait, project screenshots, or project-specific repository URLs have been supplied. The supplied real résumé is imported through the validated PDF path, outside Git.

Primary documentation checked: https://nextjs.org/docs/app/getting-started/installation, https://fastapi.tiangolo.com/deployment/concepts/, https://www.postgresql.org/support/versioning/, https://nodejs.org/en/about/previous-releases.
