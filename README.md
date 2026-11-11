# Gagandeep Kaur — a personal journal of building

A responsive editorial portfolio and private owner publishing application, built with React 19, Vite, React Router, FastAPI and PostgreSQL. React Router framework mode server-renders the public pages and supports navigation in the owner editor. The supplied résumé facts seed the initial live release; edits live in a separate draft until the owner publishes. Portrait and project media have deliberate placeholders until real files are supplied.

## Local setup

Requires Docker Desktop/Engine with Compose, Node **26.13.0** (or supported Node 24 LTS), Python **3.12**, `uv` **0.13.6**, and `make`. On Apple Silicon, use native arm64 Docker images and install Node/uv with your preferred package manager. On Linux, install Docker Engine with the Compose plugin. `npx` runs the pinned pnpm **12.18.0**; no global pnpm install is needed.

Run these commands from the repository root:

```sh
make configure
make install
make db
make migrate
make seed
make admin-create
make dev
```

Open [the local portfolio](http://localhost:3000) or [owner login](http://localhost:3000/admin/login). `admin-create` prompts privately for your email and a passphrase of at least 12 characters. There is no default owner password and no public signup. The seed is idempotent and never overwrites owner changes. `make dev` repeats migration/seed safely, runs the API on loopback 8100 and the web app on 3000. Ctrl+C stops the web/API; the PostgreSQL volume remains.

`make configure` creates an ignored, mode-0600 `.env` with random development database and HMAC secrets. Existing `.env` files are preserved. PostgreSQL uses loopback **55433** because 55432 may be in use by other projects. Backend tests create a separate database whose name contains `_test`; `TEST_DATABASE_URL` may point to another explicitly isolated test database. Change `PORTFOLIO_DB_PORT` and the matching port in `DATABASE_URL` together if needed. Never commit `.env`, private media, or backups.

Import the real résumé through the same PDF validation path used by the owner upload screen:

```sh
make import-resume RESUME_PATH=/absolute/path/to/Gagandeep_kaur_resume.pdf
```

Import updates the draft; review and publish it from `/admin` to make it live. No fake résumé or portrait is generated. Phone display is off by default; the original downloadable résumé may contain the phone number.

## Owner workflow

Open `/admin` after signing in. Edit Profile, Projects, Experience, Community, About or Settings; save the draft; inspect Preview; then Publish. Media uploads are private until a published item references them. History can restore an older release to a new draft without changing the live site. Inbox holds real submitted messages and supports read/unread, archive/restore and deletion. See [the owner guide](docs/content-editing.md).

## Commands

| Command | Behavior |
| --- | --- |
| `make configure` | Create private local configuration if absent. |
| `make install` | Install exact pnpm and uv lockfiles. |
| `make db` | Start this project's PostgreSQL container. |
| `make dev` | Migrate, idempotently seed, then run local API and web. |
| `make migrate` / `make seed` | Explicit schema/initial-content operations. |
| `make admin-create` / `make admin-reset` | Secure interactive owner bootstrap or password reset. |
| `make revoke-sessions` | Invalidate all owner sessions. |
| `make import-resume RESUME_PATH=…` | Validate a PDF and attach it to the draft. |
| `make test` | Backend and frontend tests (separate test database is created automatically). |
| `make e2e` | Start isolated real API/web/database and random ephemeral owner, run browser tests, then clean up. |
| `make build` | Production web build and backend compilation. |
| `make verify` | Lint, types, unit/integration tests and production web build. |
| `make up` | Build and start the separate production-like Compose stack on localhost3000. Stop dev first. |
| `make down` | Stop this project's development and production-like containers; preserve volumes. |
| `make backup` | Pair database and media while development writers are stopped. |
| `make backup MODE=production` | Stop production-like writers, back up, then restart them. |
| `make restore BACKUP=… RESTORE_NAME=portfolio-restore-check` | Restore to new isolated disposable volumes only. |
| `make cleanup-dry-run` / `make cleanup` | Report/apply retention and orphan cleanup. |
| `make contracts` | Export backend OpenAPI. |

The production-like stack has its own database and private media volumes; local development data is not silently copied into it. `make up` is a local container deployment, not publication on the internet. For true production, configure HTTPS and production secrets as described in [deployment](docs/deployment.md). For the requested split hosting, follow [Vercel frontend + Render API/PostgreSQL](docs/vercel-render.md).

Deployment configuration is included in `apps/web/vercel.json` and `render.yaml`. After creating the Render API, run `node apps/web/scripts/configure-vercel.mjs https://YOUR-API.onrender.com` with its real HTTPS origin and commit the generated rewrite. Supply the environment values in the hosting guide before deployment. The Render Blueprint defines paid resources and has not been applied.

## Structure and verification

- `apps/web`: React Router routes and server loaders, owner forms, and shared React presentation components; Vite handles development and bundling.
- `apps/api`: strict contracts, transactional services, sessions, uploads, contact inbox, CLI and migrations.
- `infra/nginx`: one-origin proxy and TLS example.
- `scripts`: reproducible management and coordinated backup/restore.
- `docs/project-brief.txt`: original project specification.

The isolated browser runner uses ports 8002/3002 by default; override `E2E_API_PORT`/`E2E_WEB_PORT` if occupied. It creates only a random `portfolio_e2e_*` database and temporary media, passes credentials in child process memory, and removes its test data even after failed tests. Development data is unchanged. `E2E_WEB_MODE=production make e2e` builds and tests the production SSR server and its streaming API proxy; CI uses this mode. Browser binaries require `npx --yes pnpm@12.18.0 exec playwright install chromium` once.

The frontend's `build` script runs `react-router build`, producing `apps/web/build/client` assets and `apps/web/build/server/index.js`. To run that production build against a separately running API, use `API_INTERNAL_URL=http://127.0.0.1:8100/api/v1 HOST=0.0.0.0 PORT=3000 npx --yes pnpm@12.18.0 --filter @portfolio/web start`. Set `PUBLIC_ORIGIN` and `APP_ENV` for the intended environment. Browser requests stay on `/api/v1`: Vite proxies them in development, the Node server streams them in standalone mode, and nginx routes them in Compose.

See [architecture](docs/architecture.md), [API conventions](docs/api.md), [backup and recovery](docs/backup-restore.md), [content provenance](docs/content-provenance.md), and the final [verification record](docs/verification.md). Reports distinguish executed checks from remaining deployment work. Missing optional inputs are a real portrait, project screenshots and project-specific repository links. No SMTP credentials are required to receive and store contact messages.
