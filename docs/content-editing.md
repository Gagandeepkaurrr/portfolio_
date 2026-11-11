# Owner editing guide

Sign in at `/admin/login` using the account created with `make admin-create`. A password cannot be recovered from the database; an operator can run `make admin-reset` to set a new passphrase and revoke existing sessions. Treat the private media and backups like the inbox: they may contain unpublished information.

## Saving and publishing

The editor holds unsaved changes in the current tab. Use **Save Draft** to store them. Preview shows the saved draft through the same public components, with a banner and desktop/mobile widths. **Publish** creates one immutable release and atomically makes the complete release live. A saved hidden project remains live until a later publication removes it.

If another tab saves first, the server rejects your stale save. Keep your text, review the current draft, and deliberately reconcile the conflict. Reloading or closing the browser can lose unsaved in-memory edits. Signing in again after expiry should preserve an open editor's recoverable edits; never rely on local browser storage as a backup.

History lists releases. **Restore to draft** copies a chosen historical version into a new draft revision; it does not publish. Inspect the restored result, then explicitly publish if wanted.

## Portrait and résumé

In Media, upload a JPEG, PNG or WebP up to 8 MiB. The API decodes and re-encodes it, strips metadata and makes private variants. Select it in Profile, set meaningful alt text, and adjust the 4:5 crop with the labeled controls. Applying a crop creates a new immutable image. Save, preview, then publish. Removing a portrait restores the intentional GK placeholder after publication.

Upload an unencrypted PDF résumé up to 10 MiB and 20 pages. Executable actions and attachments are rejected. Select it in Profile, enable résumé visibility in Settings, save and publish. The previous public PDF stays available until publication. The public URL always resolves the current release at `/api/v1/resume`.

Media deletion is permanent and blocked if a draft, retained release, or derived crop needs it. Removing a media reference from a draft is different from deleting its stored bytes. Historical releases are retained by default. Uploaded files never live in the public web directory.

## Projects and other content

Projects have stable internal IDs and editable public slugs. Add title, category, summary, overview, tools, supported feature bullets and real links. Repository links can remain empty. Add cover/gallery files and alt text only when the actual images exist. Move-up/down controls support keyboard ordering; visibility is a draft setting. Missing optional narrative blocks disappear cleanly from public pages.

A public project needs a valid unique slug, summary, overview and at least one technology before publication. A renamed project's old URL redirects to its current URL while that project remains published. Publishing its withdrawal makes both canonical and historical URLs unavailable.

Experience, Community and About allow the owner to edit and reorder the supplied role, education, skill, recognition and certification records. Keep date precision and evidence intact. Registration figures describe registrations, not attendance. The earlier portfolio's description must not attribute this new CMS/backend to that earlier project.

## Inbox and privacy

Inbox entries are stored PostgreSQL submissions, not proof of email delivery. Opening a message marks it read after the API accepts the change. Archive is reversible. Delete scrubs sender and content; a brief non-content idempotency receipt prevents a network retry recreating it. Reply opens your mail client and does not automatically send anything.

By default contacts are retained for 180 days. Operators must run the cleanup command regularly for deletion to take effect. If an operator changes the retention environment variable, check that the public privacy notice reflects the new policy. No external analytics are required.
