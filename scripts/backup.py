#!/usr/bin/env python3
"""Coordinated protected database + private-media backup, with writer checks."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tarfile
import tempfile
import uuid
from backup_common import FINGERPRINT_SQL, file_hash, media_hashes
from manage import ROOT, environment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['development','production'], default='development')
    args = parser.parse_args()
    os.umask(0o077)
    env = environment()
    compose = ['docker','compose'] + (['-f','compose.production.yaml'] if args.mode == 'production' else [])
    def command(*parts, **kwargs):
        return subprocess.run([*compose,*parts], cwd=ROOT, env=env, check=True, **kwargs)
    running = []
    if args.mode == 'development':
        api_port = int(env.get('API_DEV_PORT','8100'))
        with socket.socket() as client:
            client.settimeout(1)
            if client.connect_ex(('127.0.0.1',api_port)) == 0:
                parser.error('Stop the development app first (Ctrl+C in make dev). PostgreSQL stays running; backups refuse active writers.')
    else:
        listed = command('ps','--status','running','--services',capture_output=True,text=True).stdout.splitlines()
        running = [name for name in ('proxy','web','api') if name in listed]
        if running:
            command('stop',*running)
    destination = ROOT / 'backups' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:6])
    destination.mkdir(parents=True, mode=0o700)
    try:
        with (destination/'database.dump').open('wb') as output:
            command('exec','-T','db','pg_dump','--format=custom','--no-owner','--no-acl','-U',env['POSTGRES_USER'],'-d',env['POSTGRES_DB'],stdout=output)
        if args.mode == 'development':
            media_root = Path(env['MEDIA_ROOT'])
            if not media_root.is_absolute():
                media_root = ROOT / media_root
            hashes = media_hashes(media_root)
            with tarfile.open(destination/'media.tar.gz','w:gz') as bundle:
                for name in hashes:
                    bundle.add(media_root/name,arcname=name,recursive=False)
        else:
            api_id = command('ps','-a','-q','api',capture_output=True,text=True).stdout.strip()
            if not api_id:
                raise RuntimeError('Production API container must exist before backing up its media volume.')
            with tempfile.TemporaryDirectory() as temporary:
                media_root = Path(temporary)/'media'
                media_root.mkdir()
                subprocess.run(['docker','cp',f'{api_id}:/data/media/.',str(media_root)],check=True)
                hashes = media_hashes(media_root)
                with tarfile.open(destination/'media.tar.gz','w:gz') as bundle:
                    for name in hashes:
                        bundle.add(media_root/name,arcname=name,recursive=False)
        version = subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True)
        schema = command('exec','-T','db','psql','-U',env['POSTGRES_USER'],'-d',env['POSTGRES_DB'],'-Atc','SELECT version_num FROM alembic_version',capture_output=True,text=True).stdout.strip()
        counts = command('exec','-T','db','psql','-U',env['POSTGRES_USER'],'-d',env['POSTGRES_DB'],'-Atc',"SELECT json_build_object('drafts',(SELECT count(*) FROM site_drafts),'releases',(SELECT count(*) FROM site_releases),'contacts',(SELECT count(*) FROM contact_submissions),'media',(SELECT count(*) FROM media_assets))",capture_output=True,text=True).stdout.strip()
        fingerprints = command('exec','-T','db','psql','-U',env['POSTGRES_USER'],'-d',env['POSTGRES_DB'],'-Atc',FINGERPRINT_SQL,capture_output=True,text=True).stdout.strip()
        manifest = {'fingerprints':json.loads(fingerprints),'format':1,'created_at':datetime.now(timezone.utc).isoformat(),'mode':args.mode,'git_commit':version.stdout.strip() if version.returncode==0 else None,'migration':schema,'database_sha256':file_hash(destination/'database.dump'),'archive_sha256':file_hash(destination/'media.tar.gz'),'media_sha256':hashes,'counts':json.loads(counts)}
        (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(f'Backup complete: {destination}\nIncludes PostgreSQL, {len(hashes)} private media files, hashes and migration version. Protect this directory.')
    except Exception:
        shutil.rmtree(destination)
        raise
    finally:
        if running:
            command('start',*reversed(running))

if __name__ == '__main__':
    main()
