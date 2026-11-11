"""Safe archive handling shared by backup/restore tooling."""
from __future__ import annotations
import hashlib
from pathlib import Path, PurePosixPath
import re
import tarfile


def validate_restore_name(name: str) -> str:
    if not re.fullmatch(r'portfolio-restore-[a-z0-9][a-z0-9-]{0,45}', name):
        raise ValueError('RESTORE_NAME must start portfolio-restore- and contain only lowercase letters, digits and hyphens.')
    return name


def media_hashes(root: Path) -> dict[str, str]:
    output = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Media storage must not contain symbolic links.')
        if path.is_file():
            with path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(stream.read()).hexdigest()
            output[path.relative_to(root).as_posix()] = digest
    return output


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def safe_media_extract(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, 'r:gz') as bundle:
        members = bundle.getmembers()
        total = 0
        for member in members:
            parts = PurePosixPath(member.name).parts
            if member.name.startswith('/') or '..' in parts or not (member.isfile() or member.isdir()):
                raise ValueError('Backup contains an unsafe archive member.')
            total += member.size
            if total > 10 * 1024**3:
                raise ValueError('Backup exceeds the 10 GiB rehearsal extraction limit.')
        for member in members:
            target = destination / member.name
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            source = bundle.extractfile(member)
            if source is None:
                raise ValueError('Backup member has no readable bytes.')
            with source, target.open('xb') as output:
                for chunk in iter(lambda: source.read(1024 * 1024), b''):
                    output.write(chunk)
            target.chmod(0o600)

# Non-content identifiers and hashes prove records survived, without copying PII into reports.
FINGERPRINT_SQL = """
SELECT json_build_object(
  'drafts', (SELECT coalesce(json_agg(json_build_array(id, revision, md5(content::text)) ORDER BY id), '[]') FROM site_drafts),
  'releases', (SELECT coalesce(json_agg(json_build_array(id, revision, content_hash) ORDER BY revision), '[]') FROM site_releases),
  'contacts', (SELECT coalesce(json_agg(json_build_array(id, request_hash) ORDER BY id), '[]') FROM contact_submissions),
  'media', (SELECT coalesce(json_agg(json_build_array(id, sha256, status) ORDER BY id), '[]') FROM media_assets),
  'live_release_id', (SELECT live_release_id FROM site_state WHERE id = 1)
)
"""
