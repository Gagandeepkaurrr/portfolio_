"""Operator-only commands. Passwords are read privately, never from command arguments."""
import getpass
import hashlib
import json
import logging
from datetime import timedelta
from pathlib import Path
from uuid import uuid4
import typer
from pydantic import EmailStr, TypeAdapter
from sqlalchemy import select, text, update
from app.config import get_settings
from app.errors import APIError
from app.db import now, session_factory
from app.models import AdminSession, AdminUser, ContactSubmission, MediaAsset, RateLimitBucket, SiteDraft, SiteRelease, SiteState
from app.schemas import PublishRequest, SiteContent
from app.security.auth import audit, hash_password
from app.services.contact import scrub
from app.services.content import lock_draft, publish, typed_references
from app.services.media import keys_for, upload_bytes
from app.storage.local import LocalStorage

cli = typer.Typer(no_args_is_help=True)
SEED_PATH = Path(__file__).resolve().parents[1] / 'seed/portfolio.json'


def seed_site(db):
    db.execute(text('SELECT pg_advisory_xact_lock(172927141)'))
    if db.get(SiteDraft, 1) or db.get(SiteState, 1):
        db.rollback()
        return False
    raw = json.loads(SEED_PATH.read_text())
    raw['settings']['site_url'] = get_settings().public_origin
    content = SiteContent.model_validate(raw)
    db.add(SiteDraft(id=1, content=content.model_dump(mode='json'), revision=1))
    db.add(SiteState(id=1))
    db.flush()
    publish(db, PublishRequest(expected_draft_revision=1, expected_live_release_id=None, idempotency_key=uuid4()))
    return True


def create_owner(db, email, password):
    normalized = str(TypeAdapter(EmailStr).validate_python(email)).lower()
    encoded = hash_password(password)
    db.execute(text('SELECT pg_advisory_xact_lock(172927142)'))
    if db.scalar(select(AdminUser.id).limit(1)):
        raise ValueError('An owner already exists. Use admin-reset to recover access.')
    owner = AdminUser(normalized_email=normalized, password_hash=encoded)
    db.add(owner)
    db.flush()
    audit(db, 'owner_bootstrap', actor=owner.id)
    db.commit()
    return owner


def private_password():
    password = getpass.getpass('Passphrase (12–256 characters): ')
    confirmation = getpass.getpass('Repeat passphrase: ')
    if password != confirmation:
        raise typer.BadParameter('Passphrases do not match.')
    if not 12 <= len(password) <= 256:
        raise typer.BadParameter('Passphrase must contain 12 to 256 characters.')
    return password


@cli.command('seed')
def seed():
    with session_factory()() as db:
        typer.echo('Initialized CV-based draft and first release.' if seed_site(db) else 'Site already initialized; all existing data preserved.')


@cli.command('admin-create')
def admin_create():
    email = typer.prompt('Owner email')
    password = private_password()
    with session_factory()() as db:
        try:
            create_owner(db, email, password)
        except ValueError as error:
            raise typer.BadParameter(str(error))
    typer.echo('Owner created. Sign in at /admin/login.')


@cli.command('admin-reset')
def admin_reset():
    password = private_password()
    with session_factory()() as db:
        owner = db.scalar(select(AdminUser).with_for_update())
        if not owner:
            raise typer.BadParameter('No owner exists. Run admin-create first.')
        owner.password_hash = hash_password(password)
        owner.password_changed_at = now()
        owner.updated_at = now()
        db.execute(update(AdminSession).values(revoked_at=now()))
        audit(db, 'operator_password_reset', actor=owner.id)
        db.commit()
    typer.echo('Owner passphrase replaced. All previous sessions revoked.')


@cli.command('revoke-sessions')
def revoke_sessions():
    with session_factory()() as db:
        db.execute(update(AdminSession).values(revoked_at=now()))
        db.commit()
    typer.echo('All owner sessions revoked.')


@cli.command('import-resume')
def import_resume(path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True), publish_now: bool = typer.Option(False, '--publish', help='Explicitly publish the new résumé and current saved draft.')):
    with path.open('rb') as handle:
        data = handle.read(10 * 1024 * 1024 + 1)
    with session_factory()() as db:
        if not data.startswith(b'%PDF-'):
            raise typer.BadParameter('Résumé must be a PDF.')
        asset = upload_bytes(db, data, path.name)
        draft = lock_draft(db)
        content = SiteContent.model_validate(draft.content)
        content.profile.resume_asset_id = asset.id
        content.settings.show_resume = True
        draft.content = content.model_dump(mode='json')
        draft.revision += 1
        draft.updated_at = now()
        db.commit()
        if publish_now:
            state = db.get(SiteState, 1)
            result, _ = publish(db, PublishRequest(expected_draft_revision=draft.revision, expected_live_release_id=state.live_release_id, idempotency_key=uuid4()))
            typer.echo(f'Validated PDF imported and published as release {result["release"]["revision"]}.')
        else:
            typer.echo('Validated PDF imported into the saved draft. Publish from the owner editor when ready.')


@cli.command('export-openapi')
def export_openapi(path: Path = typer.Argument(Path('openapi.json'))):
    from app.main import app
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(app.openapi(), sort_keys=True, indent=2) + '\n')
    typer.echo(f'OpenAPI exported to {path}.')


@cli.command('verify-media')
def verify_media():
    storage = LocalStorage()
    checked = 0
    failures = []
    with session_factory()() as db:
        for asset in db.scalars(select(MediaAsset).where(MediaAsset.status == 'ready')):
            entries = [(asset.sanitized_source_key, asset.sha256)] + [(v['key'], v['sha256']) for v in asset.variants.values()]
            for key, expected in entries:
                try:
                    if hashlib.sha256(storage.read_private(key)).hexdigest() != expected:
                        failures.append(str(asset.id))
                    checked += 1
                except OSError:
                    failures.append(str(asset.id))
        for draft in db.scalars(select(SiteDraft)):
            for asset_id in typed_references(SiteContent.model_validate(draft.content)):
                asset = db.get(MediaAsset, asset_id)
                if not asset or asset.status != 'ready':
                    failures.append(str(asset_id))
        for release in db.scalars(select(SiteRelease)):
            for asset_id in typed_references(SiteContent.model_validate(release.source_content)):
                asset = db.get(MediaAsset, asset_id)
                if not asset or asset.status != 'ready':
                    failures.append(str(asset_id))
    typer.echo(json.dumps({'files_checked': checked, 'invalid_asset_ids': sorted(set(failures))}))
    if failures:
        raise typer.Exit(1)


@cli.command('cleanup')
def cleanup(apply: bool = typer.Option(False, '--apply')):
    current = now()
    storage = LocalStorage()
    with session_factory()() as db:
        sessions = list(db.scalars(select(AdminSession).where((AdminSession.expires_at < current) | AdminSession.revoked_at.is_not(None) | (AdminSession.last_activity_at < current - timedelta(seconds=get_settings().session_idle_seconds)))))
        buckets = list(db.scalars(select(RateLimitBucket).where(RateLimitBucket.expires_at < current)))
        contacts = list(db.scalars(select(ContactSubmission).where(ContactSubmission.deleted_at.is_(None), ContactSubmission.created_at < current - timedelta(days=get_settings().contact_retention_days)).with_for_update()))
        tombstones = list(db.scalars(select(ContactSubmission).where(ContactSubmission.deleted_at.is_not(None), ContactSubmission.receipt_expires_at < current).with_for_update()))
        assets = list(db.scalars(select(MediaAsset)))
        referenced = set().union(*(keys_for(a) for a in assets if a.status != 'deleted')) if assets else set()
        orphans = [p for p in storage.root.iterdir() if p.is_file() and p.name not in referenced and p.stat().st_mtime < (current - timedelta(hours=24)).timestamp()]
        deleted_keys = set().union(*(keys_for(a) for a in assets if a.status == 'deleted')) if assets else set()
        report = {'apply': apply, 'expired_sessions': len(sessions), 'expired_buckets': len(buckets), 'contacts_to_scrub': len(contacts), 'tombstones_to_remove': len(tombstones), 'old_orphan_files': len(orphans), 'deleted_asset_files_to_retry': len(deleted_keys), 'retained_releases': db.scalar(select(__import__('sqlalchemy').func.count()).select_from(SiteRelease))}
        if apply:
            for row in sessions + buckets + tombstones:
                db.delete(row)
            for row in contacts:
                scrub(row)
            db.commit()
            for key in deleted_keys | {p.name for p in orphans}:
                try:
                    storage.delete(key)
                except (OSError, ValueError):
                    logging.getLogger('portfolio').warning('cleanup_file_pending')
        typer.echo(json.dumps(report, indent=2))


if __name__ == '__main__':
    try:
        cli()
    except APIError as error:
        typer.echo(f'{error.code}: {error.message}', err=True)
        raise SystemExit(1)
