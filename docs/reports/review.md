# Independent implementation review

Reviewed 12 November 2026 against `docs/project-brief.txt`, `docs/architecture.md` and the backend/admin/operations reports. This review covered all 18 backend source modules, the migration, publication/contact/media/authentication boundaries, central owner state and editing flows, public rendering, both nginx configurations, container/CI configuration, backup/restore scripts and `docs/vercel-render.md`. Product code was not edited by this reviewer.

## Findings

### P2 — Reject an asset used as both portrait and résumé — resolved

- Location: `apps/api/app/services/content.py:24` (`typed_references`).
- Evidence: the original reference extractor wrote the portrait's `image` kind and then overwrote it with `pdf` when `resume_asset_id` matched. A read-only reproduction using the actual local draft and ready PDF produced no publication errors, a portrait variant with `application/pdf`, `resume_available=false`, and the PDF in `public_asset_ids`. This could publish a broken portrait and publicly authorize a PDF despite hidden résumé settings. It required an invalid owner-authenticated content request; no anonymous write path was found.
- Correction inspected: conflicting kinds now raise `422 MEDIA_KIND_MISMATCH` before save/public projection. The same read-only reproduction now returns that error without database writes. The added integration regression checks draft/live preservation, anonymous PDF denial, and rejection during both save and publication of a pre-existing invalid draft.

### P2 — Explain shared source limits in the Render deployment defaults — resolved

- Location: `docs/vercel-render.md:115`, “Required source-IP deployment gate,” with behavior in `apps/api/app/security/auth.py:55` (`source_identifier`).
- Evidence: the guide combines `--no-proxy-headers` with an empty `TRUSTED_PROXY_CIDRS`. The implementation therefore hashes the immediate Render proxy peer instead of the visitor address. Visitors sharing that peer also share the five-message/15-minute contact bucket and the login-failure bucket. Render documents that the application sees its proxy's address by default. [Render proxy behavior](https://render.com/articles/how-render-handles-ddos-attacks)
- Correction inspected: the guide now explicitly describes the shared-bucket fallback and its usability limit, requires verification from two independent source networks plus spoofed-header checks, and forbids blanket trust of incoming forwarded headers. It requires a verified ingress arrangement before launch if provider proxy boundaries cannot be established. The documentation finding is closed; actual hosted source differentiation remains a deployment acceptance task, not a locally verified capability.

## Spec and quality verdict

The required application is substantially implemented with real database mutations, owner authorization, isolated drafts/previews, atomic publication, retained history, private media authorization, contact receipts and reversible inbox operations. The reviewed lock order and idempotency paths are coherent. Both actionable review findings are resolved. No unresolved critical or high-severity security or transaction defect was found.

The implementation is suitable for repository handoff, subject to the coordinator's final verification run. The new regression check passes. This is not evidence of a public deployment: real HTTPS cookies, Vercel-to-Render uploads/rewrites, trusted proxy addresses and remote backup operations still require the documented deployment checks.

Existing verification was not unnecessarily repeated. The backend report records 31 passing PostgreSQL tests after the added media regression, with Ruff and mypy clean. The coordinator reports 8 frontend tests, 5 operational tests and all 13 browser journeys passing. The reviewer independently performed the read-only media reproduction before/after the fix and a read-only Chromium frame check through the running nginx stack. The earlier suspicion that nginx's duplicate frame header blocked modern Chromium was disproved by that check and is not a functional finding.
