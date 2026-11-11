#!/usr/bin/env python3
"""Restore only into NEW explicitly named disposable Docker volumes; never overwrite live state."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import time
from backup_common import FINGERPRINT_SQL, file_hash, media_hashes, safe_media_extract, validate_restore_name

POSTGRES_IMAGE = 'postgres:17.11-alpine'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backup', required=True)
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    try:
        name = validate_restore_name(args.name)
    except ValueError as error:
        parser.error(str(error))
    backup = Path(args.backup).resolve()
    if not backup.is_dir():
        parser.error('BACKUP must be the complete directory printed by make backup.')
    manifest = json.loads((backup/'manifest.json').read_text())
    if manifest.get('format') != 1:
        parser.error('Unsupported backup format.')
    for file, key in [('database.dump','database_sha256'),('media.tar.gz','archive_sha256')]:
        if file_hash(backup/file) != manifest[key]:
            parser.error(f'Checksum mismatch: {file}; no target was created.')
    for kind, target in [('container',name),('volume',name+'-db'),('volume',name+'-media')]:
        if subprocess.run(['docker',kind,'inspect',target],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode == 0:
            parser.error(f'Target {target} already exists; refusing overwrite.')
    os.umask(0o077)
    with tempfile.TemporaryDirectory() as temporary:
        extracted = Path(temporary)/'media'
        safe_media_extract(backup/'media.tar.gz',extracted)
        if media_hashes(extracted) != manifest['media_sha256']:
            parser.error('Extracted media checksum mismatch; no target was created.')
        for suffix in ('-db','-media'):
            subprocess.run(['docker','volume','create',name+suffix],check=True,stdout=subprocess.DEVNULL)
        password = secrets.token_hex(32)
        subprocess.run(['docker','run','-d','--name',name,'--network','none','--env-file','/dev/stdin','-v',name+'-db:/var/lib/postgresql/data','-v',name+'-media:/restore-media',POSTGRES_IMAGE],input=f'POSTGRES_USER=portfolio\nPOSTGRES_DB=portfolio\nPOSTGRES_PASSWORD={password}\n',text=True,check=True,stdout=subprocess.DEVNULL)
        try:
            for _ in range(60):
                ready = subprocess.run(['docker','exec',name,'psql','-U','portfolio','-d','portfolio','-Atc','SELECT 1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                if ready.returncode == 0:
                    break
                time.sleep(0.5)
            else:
                raise RuntimeError('Disposable restore database did not become ready.')
            with (backup/'database.dump').open('rb') as source:
                subprocess.run(['docker','exec','-i',name,'pg_restore','--exit-on-error','--no-owner','--no-acl','-U','portfolio','-d','portfolio'],stdin=source,check=True)
            subprocess.run(['docker','cp',str(extracted)+'/.',name+':/restore-media/'],check=True)
            subprocess.run(['docker','exec',name,'chown','-R','10001:10001','/restore-media'],check=True)
            subprocess.run(['docker','exec',name,'psql','-v','ON_ERROR_STOP=1','-U','portfolio','-d','portfolio','-c','DELETE FROM admin_sessions;'],check=True,stdout=subprocess.DEVNULL)
            sql = "SELECT json_build_object('drafts',(SELECT count(*) FROM site_drafts),'releases',(SELECT count(*) FROM site_releases),'contacts',(SELECT count(*) FROM contact_submissions),'media',(SELECT count(*) FROM media_assets))"
            output = subprocess.run(['docker','exec',name,'psql','-U','portfolio','-d','portfolio','-Atc',sql],capture_output=True,text=True,check=True)
            if json.loads(output.stdout) != manifest['counts']:
                raise RuntimeError('Restored record counts differ from the manifest.')
            fingerprints = subprocess.run(['docker','exec',name,'psql','-U','portfolio','-d','portfolio','-Atc',FINGERPRINT_SQL],capture_output=True,text=True,check=True)
            if json.loads(fingerprints.stdout) != manifest['fingerprints']:
                raise RuntimeError('Restored record IDs/content hashes/live pointer differ from the backup.')
            schema = subprocess.run(['docker','exec',name,'psql','-U','portfolio','-d','portfolio','-Atc','SELECT version_num FROM alembic_version'],capture_output=True,text=True,check=True).stdout.strip()
            if schema != manifest['migration']:
                raise RuntimeError('Restored migration differs from the manifest.')
            copied = Path(temporary)/'verify-media'
            copied.mkdir()
            subprocess.run(['docker','cp',name+':/restore-media/.',str(copied)],check=True)
            if media_hashes(copied) != manifest['media_sha256']:
                raise RuntimeError('Restored media volume hashes differ.')
            result = {'backup':str(backup),'target':name,'counts_verified':manifest['counts'],'record_ids_and_hashes_verified':True,'media_files_verified':len(manifest['media_sha256']),'migration':schema,'sessions_revoked':True,'network':'none'}
            report = backup / f'restore-{name}.json'
            report.write_text(json.dumps(result,indent=2)+'\n')
            print(f'Restore verified in isolated container {name}; no live data changed. Report: {report}')
            print(f'When finished inspecting: docker rm -f {name}\ndocker volume rm {name}-db {name}-media')
        finally:
            subprocess.run(['docker','stop',name],check=False,stdout=subprocess.DEVNULL)

if __name__ == '__main__':
    main()
