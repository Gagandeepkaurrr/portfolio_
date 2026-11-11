# Deploy the web app on Vercel and the API/database on Render

This guide keeps the application's PostgreSQL data model: **Vercel runs Next.js; Render runs FastAPI, PostgreSQL and a private persistent media disk.**

These are instructions for an owner-authorized deployment. No hosting service, paid disk or database has been purchased or deployed by the repository build task. Repository: [Gagandeepkaurrr/portfolio_](https://github.com/Gagandeepkaurrr/portfolio_).

## 1. Choose the final frontend origin

Use one stable HTTPS origin, for example the production Vercel project domain or an owned custom domain. In the steps below, replace `https://YOUR-PORTFOLIO.vercel.app` with that exact origin (no path/trailing slash), and replace `https://YOUR-API.onrender.com` with the Render API URL.

Browsers must continue calling `/api/v1/...` on the frontend origin. Next's existing external rewrite forwards those requests to Render. Server components use the same Render URL through `API_INTERNAL_URL`. The owner cookie is therefore set through the frontend origin, preserving the same-origin session/CSRF design. Do not change frontend fetches to call Render directly and do not add wildcard credentialed CORS.

## 2. Create PostgreSQL on Render

In Render, choose **New → Postgres**. Choose PostgreSQL 17 (the locally verified major), an appropriate database plan, and the same region you will use for the API. Name it `gagandeep-portfolio-db`. After it is available, copy its **Internal Database URL** privately. Render recommends internal connections for services in the same account/region. [Render PostgreSQL connection guide](https://render.com/docs/postgresql-creating-connecting)

Convert only the URL's driver scheme for this application:

```text
postgresql://USER:PASSWORD@HOST/DATABASE
→ postgresql+psycopg://USER:PASSWORD@HOST/DATABASE
```

Keep the rest of the generated URL and its credentials unchanged. Put it only in the Render API's secret `DATABASE_URL`. Do not paste it into Git, Vercel frontend variables, screenshots, or chat. Local development remains on its separate local PostgreSQL database.

## 3. Create the Render API service and disk

Choose **New → Web Service**, connect the GitHub repository, and configure:

| Setting | Value |
| --- | --- |
| Runtime | Python 3 |
| Root directory | `apps/api` |
| Python version environment variable | `PYTHON_VERSION=3.12.16` |
| uv version environment variable | `UV_VERSION=0.13.6` |
| Build command | `uv sync --frozen --no-dev` |
| Pre-deploy command | `uv run --frozen --no-dev alembic upgrade head` |
| Start command | `uv run --frozen --no-dev uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2 --no-proxy-headers` |
| Health check path | `/api/v1/health/ready` |
| Instances | One while using the local-disk storage backend |

Render detects the committed `uv.lock`; `UV_VERSION` pins its provided uv executable. [Render uv version configuration](https://render.com/docs/uv-version)

Render requires binding the assigned `PORT`; the command above follows its documented FastAPI setup while preserving this project's locked dependencies. The migration runs once in the pre-deploy step, not independently in each API worker. [Render FastAPI deployment guide](https://render.com/docs/deploy-fastapi)

Attach a **persistent disk** with mount path `/var/data`, and set `MEDIA_ROOT=/var/data/media`. Choose capacity for the expected images/PDFs and monitor usage. A persistent disk requires a paid eligible Render service; files outside its mount path are ephemeral. The disk is available to only one service instance and only at runtime, so uploads, résumé import and media cleanup must not run during build/pre-deploy. [Render persistent disks](https://render.com/docs/disks)

Set these API environment variables before deploying:

| Variable | Production value |
| --- | --- |
| `APP_ENV` | `production` |
| `PUBLIC_ORIGIN` | `https://YOUR-PORTFOLIO.vercel.app` |
| `DATABASE_URL` | Converted private Render PostgreSQL internal URL |
| `MEDIA_BACKEND` | `local` |
| `MEDIA_ROOT` | `/var/data/media` |
| `CSRF_SECRET` | Independently generated random secret, at least 32 characters |
| `ABUSE_HMAC_SECRET` | A different independently generated random secret |
| `SESSION_ABSOLUTE_SECONDS` | `43200` |
| `SESSION_IDLE_SECONDS` | `3600` |
| `CONTACT_RETENTION_DAYS` | `180`, or the deliberate policy you want shown in Privacy |
| `CONTACT_IP_LIMIT` / `CONTACT_SITE_LIMIT` | `5` / `100` initially |
| `TRUSTED_PROXY_CIDRS` | Initially empty as a conservative fallback; complete the source-IP deployment gate below before public launch |
| `LOG_LEVEL` | `INFO` |

Render's secret-generation control may be used for both distinct HMAC values. Do not reuse development secrets. Leave SMTP variables empty unless you deliberately configure notifications. Without SMTP, messages still persist in the inbox and the UI reports receipt rather than email delivery.

The database migration can run without the media disk. Once the API is running, open **Render → API service → Shell** and run:

```sh
uv run --frozen --no-dev python -m app.cli seed
uv run --frozen --no-dev python -m app.cli admin-create
```

The first command initializes one verified draft and release only when empty. The second privately prompts for your email/passphrase; there is no default password. The API may report an unpublished state before seed. To recover access later, run `uv run --frozen --no-dev python -m app.cli admin-reset` in the service shell.

## 4. Import the frontend into Vercel

In Vercel, create a project from the same GitHub repository. Set **Root Directory** to `apps/web`, select **Next.js**, and enable inclusion of source files outside that directory so the workspace lockfile can be used. Vercel's monorepo workflow assigns a project root to the selected app. [Vercel monorepo guide](https://vercel.com/docs/monorepos)

| Setting | Value |
| --- | --- |
| Node version | `26.x` |
| Install command | `cd ../.. && npx --yes pnpm@12.18.0 install --frozen-lockfile` |
| Build command | `cd ../.. && npx --yes pnpm@12.18.0 --filter @portfolio/web build` |
| Output directory | Leave the Next.js default `.next` |

Select Node 26.x in project settings; this matches the locally verified Node 26 toolchain. [Vercel Node.js versions](https://vercel.com/docs/functions/runtimes/node-js/node-js-versions)

Set these **Production** environment variables:

```text
API_INTERNAL_URL=https://YOUR-API.onrender.com/api/v1
PUBLIC_ORIGIN=https://YOUR-PORTFOLIO.vercel.app
APP_ENV=production
```

Do not set database passwords, CSRF secrets, storage credentials or session secrets on Vercel. Do not prefix the internal API setting with `NEXT_PUBLIC_`. `API_INTERNAL_URL` is also used to compile the external rewrite, so redeploy Vercel after changing it. `APP_ENV=production` allows public indexing; admin/preview remain noindex.

Deploy the Vercel production project, then confirm the deployed hostname exactly matches Render's `PUBLIC_ORIGIN`. If it changed, update Render, redeploy/restart the API, update the site URL in owner Settings and publish. Exact Origin validation intentionally rejects arbitrary Vercel preview URLs. Use a separate staging API/database/disk for independent preview editing, or keep previews read-only; never add a wildcard allowed origin.

## 5. Verify and add your real assets

From the Vercel origin, verify:

1. `/api/v1/health/ready` returns healthy, the home page and both project routes render, and unknown projects return404.
2. `/admin/login` accepts your owner account; the HTTPS session cookie is `__Host-portfolio_session` with Secure, HttpOnly, SameSite=Lax and Path=/.
3. Save a draft edit, inspect Preview, and check the public page remains unchanged until Publish. Confirm a new release in History.
4. Upload the real résumé and portrait in the admin Media/Profile screens. These requests must pass through the same frontend origin. Save and publish. Verify the actual PDF and image still work after restarting the Render API.
5. Submit one message from the public form, open it in Inbox and confirm it survives a refresh. Archive/delete your test message deliberately.
6. Verify current sitemap/canonical URLs, no-store media headers, and private media being unavailable anonymously. Inspect logs using request IDs.

A résumé can also be imported from an actual PDF already copied to the runtime disk using `uv run --frozen --no-dev python -m app.cli import-resume /var/data/the-file.pdf`, then published from the editor. Never put the original PDF or uploads in Git just to deploy them.

## Required source-IP deployment gate

With `TRUSTED_PROXY_CIDRS` empty and uvicorn proxy-header trust disabled, the application hashes its socket peer. On Render that is normally a proxy, so unrelated visitors can share the five-messages-per-15-minute source bucket and broad login bucket. The default is conservative about spoofed headers; it does **not** establish per-visitor IP rate limiting on this hosting path. Render documents that the original address is carried through forwarded headers because its edge/load balancers sit in front of the app. [Render proxy and client-IP guidance](https://render.com/articles/how-render-handles-ddos-attacks)

Before describing the hosted deployment as ready, establish the actual Vercel → Render edge → service chain and a narrowly bounded set of trusted proxy CIDRs from verified provider information. The backend walks `X-Forwarded-For` from right to left only when the connected peer is trusted, stopping at the first untrusted address. Validate the result from at least two independent source networks, and send spoofed incoming forwarded headers to prove they cannot select arbitrary source buckets. Keep raw addresses out of permanent message rows/logs; compare derived identifiers during controlled verification.

Never use `*`, `0.0.0.0/0`, or trust the internet's first forwarded-header value. If the providers' actual chain cannot be reliably bounded for this route, add and verify an authenticated ingress arrangement before public launch. That integration is not claimed to exist in this repository. Until this gate passes, report the shared-proxy fallback and its usability limit explicitly rather than calling per-source limits configured.

## Maintenance and recovery on this hosting arrangement

Run `uv run --frozen --no-dev python -m app.cli cleanup` in the API shell for a dry run; add `--apply` after review. The command must run on the disk-owning API instance. A separate Render cron service cannot access this disk. Keep PostgreSQL recovery/export settings and protected media backups; the repository's Docker backup scripts target the local/Compose topology and are not presented as a turnkey Render backup integration. An operator must arrange a coordinated writer-stopped database/media backup and rehearse recovery before relying on the hosted deployment for irreplaceable data.

The local storage adapter intentionally limits horizontal scaling. Do not add API instances sharing an assumed filesystem or advertise S3 support: an S3 adapter would need implementation and verification first. Keep `/api/v1` as a direct external rewrite, without adding a Next API route/function that reads uploaded files. Vercel Functions have a 4.5 MB request/response limit, which does not by itself establish the limit of the external rewrite route. Smoke-test actual near-limit 8 MiB images and 10 MiB PDFs through the deployed Vercel→Render path; no blanket upload-capacity guarantee is made here. [Vercel function payload limits](https://vercel.com/docs/errors/function_payload_too_large) Platform ingress limits, runtime proxy headers and cookie behavior must also be checked on the deployed services. The local verification record is not a claim that these hosted checks have run.
