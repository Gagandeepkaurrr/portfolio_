# Operations implementation and verification

## Implemented

- Separate development and production-like Compose stacks. Development PostgreSQL 17.11 runs only on loopback 55433; existing unrelated containers/ports remain unchanged.
- Random private local configuration generator, exact pnpm/uv installation wrappers, every requested Make entry point, secure interactive owner commands, explicit résumé path validation and bounded readiness polling.
- Multi-stage Node 26.13.0 / uv 0.13.6 / Python 3.12.16 application images with non-root UID 10001 runtime. nginx 1.30.0 same-origin routing, private API/DB networks, persistent database/media volumes, request limits and an explicit TLS configuration example.
- One migration/seed service before API startup, healthchecks and clean stop without volume deletion.
- Coordinated backup and restore tools with restrictive file permissions, private media, schema/app version, archive/media checksums, draft/release/contact/media ID/content-hash comparison and restored-session invalidation. Restore targets must be new explicitly named `portfolio-restore-*` network-isolated containers/volumes.
- CI definition for locked install, backend/frontend checks, operational safety tests, actual API/web startup and real-stack browser tests.
- README, owner workflow, API conventions, content provenance, deployment and backup/recovery guides.

## Checks executed so far

- `docker compose up -d --wait db`: PostgreSQL 17.11 healthy on 127.0.0.1:55433.
- `docker compose -f compose.production.yaml config --quiet`: passed.
- Docker manifest checks for pinned PostgreSQL/Node/Python/uv/nginx tags: passed.
- `docker run ... nginx:1.30.0-alpine nginx -t`: configuration syntax successful.
- `python3 -m unittest discover -s tests/ops -v`: 5 passed, covering unsafe archive members, restore-target naming, changed media bytes, and corrupt-backup rejection before target creation.
- `python3 -m py_compile scripts/*.py`: passed.
- `make help`, repeated `make configure`: passed; repeated configuration preserved `.env` unchanged.
- Missing résumé path check: rejected with exit 2 before mutation.

## Integrated evidence (12 November 2026, India time)

- `make migrate` and repeated `make seed` passed; existing seed was preserved.
- Actual supplied `Gagandeep_kaur_resume.pdf` imported through the validator and published as release 2. Initial import caught a too-broad rejection of harmless internal PDF page-view actions; the backend fix and regression test allowed the genuine document without changing it. `verify-media` checked two source/variant entries with zero invalid assets.
- `make backup` produced `backups/20261111T184314Z-4116fd` (UTC timestamp), containing one draft, two releases and one real résumé asset. Source snapshots and hashes remain in the protected, Git-ignored backup.
- `make restore ... RESTORE_NAME=portfolio-restore-rehearsal-a2` verified every draft/release/contact/media ID/content hash, live pointer, migration, archive hash and actual media byte hash in fresh network-isolated volumes. An initial bootstrap readiness race was discovered and fixed by checking a successful database query rather than `pg_isready` alone.
- A second rehearsal added a synthetic inbox message and an inactive synthetic owner/session only to the isolated copy. Restoring that populated copy to `portfolio-restore-rehearsal-a3` retained the contact and actual PDF and deleted the restored session. The source had one session; the restored target had zero. Restore reports are retained beside both protected backups. All three disposable rehearsal containers and their specifically named volumes were removed afterward.
- Development data remained one draft, two releases, one real PDF, zero owners and zero contacts after rehearsal; no default owner or synthetic inbox entry was left in the user's database.
- `docker compose -f compose.production.yaml build api` passed with the locked Python environment and unprivileged runtime. The image must be rebuilt after any later backend fixes.
- `make e2e` now owns a fresh random `portfolio_e2e_*` database, temp media, random in-memory owner credentials, API 8002 and web 3002. The first real-stack run executed 13 tests (5 passed / 8 failed), exposed test-locator/fixture and public contrast issues, and removed its database/media even on failure. Fixes and subsequent evidence are recorded in the final verification report. The environment does not touch the user's owner database.
- Existing unrelated services occupied API port 8000 and database port 55432. They were preserved. Portfolio development uses configured API port 8100 and database port 55433.

A configured file is not evidence that its public deployment happened. Both API and frontend production images now build successfully, and the full nginx/Next/FastAPI/PostgreSQL stack started healthy on localhost3004. Both app containers run UID10001. Public/project routes, real résumé bytes and a synthetic contact persisted across restarting database/API/web/proxy. `make backup MODE=production` successfully stopped writers, archived matching DB/media, and restored healthy services. The final full isolated browser suite passed13/13; the mobile menu focus defect found in the prior run was fixed and verified. nginx no longer duplicates `X-Frame-Options`: the actual preview response has exactly SAMEORIGIN and matching self-only frame ancestors, while ordinary pages retain DENY through Next.

The Render/Vercel guide has exact current tool/runtime settings and dashboard commands. Hosted HTTPS cookies, near-limit upload ingress and true-source-IP differentiation remain required deployed-service checks. The initial untrusted-proxy fallback can group visitors behind the same Render peer; the guide explicitly gates production readiness on a verified bounded proxy chain, rather than recommending wildcard trust.

## Deployment limits

No internet publication, paid-service activation or external messages were performed. A real HTTPS domain/certificate, remote host, operator backup schedule and optional SMTP credentials remain external inputs. Development HTTP uses explicitly relaxed development cookies; production requires HTTPS and separate secrets. S3 is not implemented. Production backups stop application writers; development backups refuse an active API and require the operator to stop `make dev` first. Retention requires running cleanup. Backup encryption/off-host scheduling remain operator tasks.
