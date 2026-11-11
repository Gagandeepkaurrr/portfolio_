# Deployment and operational ownership

The repository is prepared for one host with Docker: nginx → Next.js/FastAPI → PostgreSQL plus a persistent private media volume. Only nginx exposes application ports. `compose.production.yaml` builds unprivileged application images with pinned dependencies; a one-shot migration/seed service runs after database readiness, before the API and web start. Development Compose is a separate stack and volume.

## Local production-like check

Stop `make dev`, then run `make up`. The default root `.env` has `APP_ENV=development` and `PUBLIC_ORIGIN=http://localhost:3000`, so local HTTP is explicitly development-cookie mode even though Next.js is a production build. This is useful for container testing; it is not secure production configuration. Open localhost3000. Create the separate containerized owner interactively:

```sh
docker compose -f compose.production.yaml exec api python -m app.cli admin-create
```

`make down` stops containers and preserves their volumes. Never append `--volumes` casually: deletion is a separate deliberate operator action.

## Before a public release

1. Provision a domain and TLS certificate through the chosen host. Public deployment and paid services require the owner's authorization; none are performed by this task.
2. Use a distinct protected environment file. Set `APP_ENV=production`, `PUBLIC_ORIGIN=https://the-authorized-domain`, strong distinct CSRF/abuse secrets, and a distinct database password. Startup rejects an HTTP production origin. Set the CMS `site_url` to the same public origin before publication.
3. Mount a configured version of `infra/nginx/tls.conf.example` with certificate/key files. Expose only proxy ports80/443. Remove the loopback-only binding only after the authorized deployment is ready. Do not expose API8000 or PostgreSQL5432.
4. Configure `TRUSTED_PROXY_CIDRS` narrowly for the proxy network if forwarded source-IP accounting is needed. Arbitrary internet forwarded headers must never become trusted. nginx overwrites forwarded headers. Default API starts with uvicorn proxy-header trust disabled; application settings govern any forwarded-IP parsing.
5. Set media storage to the persistent private volume. Local filesystem is implemented; S3 is not an advertised backend. Do not mount media into nginx, enable public bucket URLs, or cache private/publicly withdrawable media through an image optimizer.
6. Run `make verify` and the integrated browser checks, build immutable images, and record the Git revision. Produce a coordinated protected backup before updating an existing instance.
7. Run the migration once, start the new services, and check `/api/v1/health/live`, `/api/v1/health/ready`, public pages, owner sign-in and a real contact submission. Inspect correlation-ID logs. SMTP is optional and does not determine readiness.

Next's server-only `API_INTERNAL_URL` is runtime configuration. Browser API calls remain relative `/api/v1`. All credentials and storage paths are server runtime values. Fonts, CSS and JavaScript are static build output; no secret is a `NEXT_PUBLIC_` value. Docker images contain no `.env`, uploads or backups.

## Maintenance

Run `make cleanup-dry-run` before `make cleanup`. Schedule cleanup with the host's scheduler after review; it expires sessions and rate buckets, handles contact retention/tombstones and reports/removes safely aged unreferenced files. Retained releases stay intact by default. Backups contain private information: use encrypted off-host storage and an operator retention policy, for example seven daily and four weekly copies.

Review app logs and health checks for database/storage failures, contact failures and failed publishes. Liveness should not require PostgreSQL; readiness should. A stopped database must produce controlled 503 errors, not fake empty content or success receipts.

A rollback must consider database compatibility. Keep the coordinated pre-release backup; do not run destructive Alembic downgrades blindly. Restore rehearsal uses new, explicitly named disposable volumes and invalidates sessions; see the recovery guide.

## Evidence boundaries

Configuration is not a deployment. Local HTTP tests do not establish production HTTPS cookie behavior or certificate operations. A real domain, certificate provisioning, remote host backup schedule, email provider and external monitoring remain operator choices. The final verification record lists what was actually executed.
