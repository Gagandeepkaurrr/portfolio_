# Coordinated backup and restore

The database contains private drafts, contacts and owner session digests. The private media directory contains unpublished uploads. Back up both at the same consistent stopping point; a database-only backup cannot restore the portfolio.

## Create a backup

For development, stop the API/web first with Ctrl+C in `make dev`; leave PostgreSQL running. Then:

```sh
make backup
```

The script refuses to proceed while the configured loopback API port (8100 by default) is listening. This is deliberate: development has no writer maintenance protocol. For the production-like Compose stack:

```sh
make backup MODE=production
```

It records running API/web/proxy services, stops them gracefully, takes a custom-format PostgreSQL dump and matching private-media archive, then restarts only services previously running, including after failure. Do not run external migration/seed/upload tools during this maintenance window.

The new directory under `backups/` has restrictive permissions and contains `database.dump`, `media.tar.gz` and `manifest.json`. The manifest records the migration, application Git revision (when committed), row counts and SHA-256 hashes of both archives and every media file. Secrets remain outside the backup, but database data remains sensitive. Copy backups to encrypted storage; do not commit or expose them.

## Rehearse recovery safely

Use the complete printed backup directory and a new explicit disposable name:

```sh
make restore BACKUP=/absolute/path/to/backups/your-backup RESTORE_NAME=portfolio-restore-rehearsal
```

The script refuses existing containers/volumes, unsafe names, bad checksums, archive traversal, symlinks and non-file archive members. It creates a network-isolated PostgreSQL container with two new volumes, restores the database and media, deletes every restored owner session, and checks schema, row counts and media hashes. It stops the disposable container at completion and writes a restore report next to the backup.

The original application is never overwritten. The command prints explicit cleanup commands for its disposable container and volumes. Run those only after finishing inspection. Promotion into an authorized production target is a separate controlled operational procedure: stop writers, select empty target volumes, restore the matched pair, configure secrets/domain, run compatible migrations, revoke sessions and verify service behavior before switching traffic.

## Retention and limits

All site releases are retained by default; media referenced by any retained source release remains needed for restoration. Pruning requires a reviewed operator procedure and backup first. The archive extractor limits a rehearsal to 10 GiB; increase that limit deliberately only after assessing storage capacity. These scripts protect against accidental overwrite and validate integrity; they do not provide encryption, remote backup scheduling or antivirus certification.

See `docs/reports/ops.md` for the actual rehearsal evidence and unresolved checks.
