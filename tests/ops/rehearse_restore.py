#!/usr/bin/env python3
"""Add synthetic inbox/session records to an ISOLATED restored copy, then verify recovery again."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'scripts'))
from backup_common import FINGERPRINT_SQL, file_hash, validate_restore_name

if len(sys.argv) != 4:
    raise SystemExit('Usage: rehearse_restore.py BACKUP EXISTING_ISOLATED_COPY NEW_ISOLATED_TARGET')
backup=Path(sys.argv[1]).resolve()
source=validate_restore_name(sys.argv[2])
target=validate_restore_name(sys.argv[3])
os.umask(0o077)
subprocess.run(['docker','start',source],check=True,stdout=subprocess.DEVNULL)
def psql(sql):
    return subprocess.run(['docker','exec','-i',source,'psql','-v','ON_ERROR_STOP=1','-U','portfolio','-d','portfolio','-Atc',sql],check=True,text=True,capture_output=True).stdout.strip()
try:
    for _ in range(60):
        try:
            psql('SELECT 1')
            break
        except subprocess.CalledProcessError:
            time.sleep(.25)
    else:
        raise RuntimeError('Isolated source failed readiness.')
    psql("""INSERT INTO admin_users (id,normalized_email,password_hash,is_active,created_at,updated_at,password_changed_at)
        VALUES ('f0000000-0000-4000-8000-000000000001','recovery-fixture@example.com','inactive-recovery-fixture',false,now(),now(),now());
        INSERT INTO admin_sessions (id,admin_user_id,token_digest,csrf_token_digest,created_at,expires_at,last_activity_at)
        VALUES ('f0000000-0000-4000-8000-000000000002','f0000000-0000-4000-8000-000000000001','recovery-fixture-session-digest','recovery-fixture-csrf-digest',now(),now()+interval '12 hours',now());
        INSERT INTO contact_submissions (id,idempotency_key,request_hash,name,email,subject,message,is_read,is_archived,notification_status,created_at,updated_at,receipt_expires_at)
        VALUES ('f0000000-0000-4000-8000-000000000003','f0000000-0000-4000-8000-000000000004','recovery-fixture-hash','Recovery fixture','recovery-fixture@example.com','Recovery rehearsal','Synthetic contact used only in a network-isolated recovery rehearsal.',false,false,'not_configured',now(),now(),now()+interval '24 hours');""")
    assert psql('SELECT count(*) FROM admin_sessions')=='1'
    fixture=backup.parent/(backup.name+'-with-recovery-fixtures')
    fixture.mkdir(mode=0o700)
    with (fixture/'database.dump').open('wb') as output:
        subprocess.run(['docker','exec',source,'pg_dump','--format=custom','--no-owner','--no-acl','-U','portfolio','-d','portfolio'],check=True,stdout=output)
    shutil.copyfile(backup/'media.tar.gz',fixture/'media.tar.gz')
    manifest=json.loads((backup/'manifest.json').read_text())
    manifest['database_sha256']=file_hash(fixture/'database.dump')
    manifest['fingerprints']=json.loads(psql(FINGERPRINT_SQL))
    manifest['counts']=json.loads(psql("SELECT json_build_object('drafts',(SELECT count(*) FROM site_drafts),'releases',(SELECT count(*) FROM site_releases),'contacts',(SELECT count(*) FROM contact_submissions),'media',(SELECT count(*) FROM media_assets))"))
    manifest['rehearsal_fixture_note']='Actual seeded portfolio and supplied PDF plus synthetic contact and inactive owner/session added only to an isolated copy.'
    (fixture/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    subprocess.run([sys.executable,str(Path(__file__).resolve().parents[2]/'scripts/restore.py'),'--backup',str(fixture),'--name',target],check=True)
    subprocess.run(['docker','start',target],check=True,stdout=subprocess.DEVNULL)
    for _ in range(60):
        result=subprocess.run(['docker','exec',target,'psql','-U','portfolio','-d','portfolio','-Atc','SELECT count(*) FROM admin_sessions'],capture_output=True,text=True)
        if result.returncode==0:
            assert result.stdout.strip()=='0','Restored session was not revoked'
            break
        time.sleep(.25)
    else:
        raise RuntimeError('Restored session count could not be checked.')
    print('Populated rehearsal passed: synthetic contact retained, source session removed on restore, real PDF and all site records verified. Development data untouched.')
finally:
    subprocess.run(['docker','stop',source],check=False,stdout=subprocess.DEVNULL)
    subprocess.run(['docker','stop',target],check=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
