# Backend implementation and verification

Implemented in `apps/api` on 12 November 2026. The API uses FastAPI 0.162.4, SQLAlchemy 2.1.8/psycopg 3.3.8, Pydantic 2.14.3, Alembic 1.20.1, Argon2id, Pillow 13.0.0 and pypdf 7.0.1. Direct dependencies and the complete `uv.lock` are pinned. Python 3.12.16 was used locally.

## Implemented behavior

- Reviewed initial Alembic migration creates the relational schema, JSONB draft/release records, monotonic release sequence, immutable release snapshots, session/token-digest storage, private media metadata, contact receipts/tombstones, shared transactional rate buckets, aliases and safe audit records.
- Idempotent CV-based seed initializes exactly one draft and initial release without overwriting existing data. The supplied résumé passed the PDF pipeline and was published by the operations task; no portrait or project screenshot was fabricated.
- Strict bounded Pydantic content schemas forbid unknown keys, validate URLs/date precision/identifiers/order/media references, and distinguish incomplete drafts from valid publications. Explicit response models prevent ORM/private snapshot serialization through public endpoints. Public output excludes hidden items, hidden phone values, hidden section copy, raw storage keys and résumé asset internals.
- Opaque cookie sessions, Argon2id passphrases, exact-origin enforcement, session-bound HMAC CSRF, absolute/inactivity expiry, logout, login rotation, password change/revocation, operator recovery, and shared PostgreSQL login throttling.
- Draft ETag preconditions; atomic locked publish with both preconditions and idempotent receipts; no live-pointer movement on replay; restore into a new draft; stable-ID slug ownership/aliases; hidden/withdrawn routes return 404.
- Authenticated previews reuse public-shaped DTOs and owner-only media URLs. Hidden projects can be previewed by stable ID.
- Private filesystem storage with random server keys, streaming request/file bounds, actual raster decoding, animation/SVG rejection, EXIF removal/re-encoding, bounded variants, immutable 4:5 crop derivatives, verified bounded PDFs, live-reference GET/HEAD authorization and deletion blocked by all retained draft/release/derived references.
- Contact persistence with exact-payload UUID receipts, concurrent replay deduplication, transactional source/global rate ceilings, safe pagination, read/unread/archive/restore/deletion, 24-hour post-deletion tombstones and 180-day configurable retention. Privacy retention data reflects current operator configuration without needing a content republish.
- Optional SMTP is a single bounded best-effort claimed attempt after commit; no SMTP credentials were configured and no external message was sent.
- Request IDs, safe bounded error envelopes/log context, no-store responses, noindex owner responses, minimal liveness and dependency/schema/storage readiness.
- Operator CLI: seed, admin-create, admin-reset, revoke-sessions, import-resume (draft-only unless `--publish` explicitly supplied), export-openapi, verify-media, cleanup (dry-run unless `--apply`). No owner default password exists.

## Executed verification

- `uv run pytest -q`: **31 passed**, actual PostgreSQL 17.11 in a dedicated `_test` database. No SQLite or mocked successful database mutations.
- `uv run mypy app`: **success, 18 source files**.
- `uv run ruff check app tests`: **all checks passed**.
- `uv run alembic upgrade head`: **passed**, including empty-database initialization.
- `uv run alembic check`: **no new upgrade operations detected**.
- `uv run python -m app.cli seed`: initial publication succeeded; repeated seeding preserved all state (also covered by integration tests).
- `uv run python -m app.cli export-openapi`: exported `apps/api/openapi.json`, including explicit public/admin transport DTOs.
- `uv run python -m app.cli verify-media`: 2 stored references checked; 0 invalid assets for the real résumé.
- `uv run python -m app.cli cleanup`: dry-run completed, 2 retained releases, no expired or orphan data.
- `uv run python -m compileall -q app`: passed.

Tests cover real concurrent publication/preconditions and contact retries/quota charging, failure injection before publication commit, stale drafts, private preview isolation, hidden section copy removal, restore, alias ownership/withdrawal, token digests/CSRF/origin/session expiry/rotation/password change, passphrase whitespace, inbox pagination/tombstones, media crop/source-pixel geometry, publication access and retained-reference deletion, malformed files/PDF active content, safe internal PDF page-view actions, actual PDF delivery, safe URLs/unknown keys/date precision, seeding and health headers.

Initial contract tests were observed failing with 404 before implementation. Regression tests were observed failing before fixes for passphrase whitespace, safe PDF internal page-view actions, hidden-section copy leakage, login token revocation, and runtime privacy retention. The first migration run exposed a missing autogenerate sequence; the reviewed migration now explicitly creates/drops it. Latest suite is clean with no warnings; current Starlette's HTTPX2 test transport is pinned as a development dependency.

## Boundaries and remaining validation

- Only private persistent local filesystem storage is implemented. `MEDIA_BACKEND=s3` is deliberately rejected; an S3 adapter is not claimed.
- SMTP configuration/delivery and public HTTPS deployment were not exercised by this backend task. No email delivery or production certification is claimed.
- Image/PDF validation is bounded parsing, not antivirus certification. Previously downloaded public bytes cannot be recalled. Retained releases are preserved by default and keep referenced media undeletable.
- API tests exercise real PostgreSQL concurrency using multiple request threads. Process-level two-worker/TLS and full-browser checks are coordinated by the root/operations tasks and reported separately.
- Existing development data is never used as a destructive test target: the test fixture creates/uses a separate database whose name must contain `_test`.
- No commits were made by this worker; files are available directly in the shared branch for root integration/review.

## Final review correction

The reviewer found that one UUID used for both portrait and résumé could overwrite the expected image kind with PDF in the shared typed-reference map. The conflict is now rejected before any save/publication mutation. A regression was observed failing with HTTP 200 before the fix; it now verifies HTTP 422 for both save and publication, unchanged saved draft/revision/live snapshot, and no public PDF access even when résumé visibility is off. Fresh verification after this correction: `uv run pytest -q` **31 passed**, Ruff clean, mypy clean (18 source files).
