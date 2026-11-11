# Owner studio implementation report

Implemented the private owner interface under `/admin`, using the backend's authenticated API. All work remains local; no account password is built into the frontend.

## Delivered

- Sign-in, sign-out confirmation, password change, session-bound CSRF headers, timeout/error parsing, in-place reauthentication that preserves existing unsaved draft edits.
- Shared in-memory draft state across content routes, explicit Save Draft, actual saved revision, strong If-Match preconditions, conflict handling, safe reload confirmation, before-unload warning, and preservation of edits typed while a save is in flight.
- Ordinary labeled fields for profile, all project fields/narrative/gallery/SEO, experience, leadership/metrics, education, skill groups, recognition, certifications, navigation/section intros, feature selection, phone/résumé visibility and availability.
- Stable-item creation, reorder, visibility and removal controls; new collection items begin hidden. Removing/hiding is clearly described as a draft change until publication.
- Review dialog compares draft against private live source, displays validation warnings and explicit draft/live preconditions, uses an unchanged publication UUID when retrying, and refetches status after acceptance.
- Paginated history with confirmation before restoring an immutable release to a new draft. Restoration does not publish.
- Authenticated public-shaped previews using the exact public components, in a same-origin frame whose width can be switched to 375px. No raw SiteContent is passed to public components. Project links remain inside the preview journey. No session or bearer secret is included in frame URLs.
- Searchable/filterable paginated media library; file upload states, protected deletion with reference summary, portrait crop with keyboard-operable sliders and desktop/mobile preview, alt text, gallery captions/order, résumé selection and real PDF links. Crop applies a new immutable derivative.
- Paginated inbox with unread/all/archive filters, accepted mark-read behavior, archive/restore, scrub-delete confirmation, safe plain-text message display, and encoded mailto reply links.
- Responsive studio sidebar/menu, semantic controls, Radix focus trapping, Escape close and explicit opener focus restoration, error summaries receiving focus, and reduced-motion CSS.

## Verification

- `pnpm --filter @portfolio/web typecheck`: passed.
- `pnpm --filter @portfolio/web exec eslint src/app/admin src/components/admin src/providers src/lib/api/admin.ts`: passed.
- `pnpm --filter @portfolio/web test`: 8 tests passed overall; admin tests exercise unsaved-conflict preservation, clean remote refresh, dirty sections, publication preconditions, narrative format conversion and dialog focus restoration.
- Dialog Escape focus issue was reproduced by a failing RTL test (focus incorrectly returned to body), then fixed and rerun successfully.
- Real isolated-stack Playwright suite in `tests/e2e/admin.spec.ts` exercises login, cross-tab unsaved persistence, draft isolation, mobile preview, publication/history restore, stale-save conflicts, inbox lifecycle, validated image upload/crop/private access, 320px overflow, desktop automated accessibility and menu focus. Actual rendered admin screenshots at 320px and 1440px were inspected and showed no clipping or horizontal overflow. First run exposed test-locator/email-fixture problems; second run passed all features except the dialog-focus defect described above. Final full isolated-stack browser rerun passed 13/13, including all four admin journeys. A subsequent targeted landscape-image crop test also passed (1/1), verifying an immutable derived asset with a parent and exact 4:5 dimensions.

## Practical limits

Automated accessibility checks and keyboard journeys are verification evidence, not formal WCAG certification. Media deletion remains governed by backend retained-reference rules. The image cropper uses keyboard-friendly focus/zoom sliders; it does not provide pointer dragging. Session expiry preserves edits only while the current page remains open, which the reauthentication dialog explains.
