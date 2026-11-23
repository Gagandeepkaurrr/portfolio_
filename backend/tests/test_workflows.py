import copy
import io
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from PIL import Image
from pypdf import PdfWriter
from sqlalchemy import func, select
from fastapi.testclient import TestClient
from app.cli import create_owner, seed_site
from app.config import get_settings
from app.db import now, session_factory
from app.main import app
from app.models import AdminSession, ContactSubmission, SiteDraft, SiteRelease

ORIGIN = {'Origin': 'http://localhost:3000'}


def draft(owner):
    response = owner.get('/api/v1/admin/draft')
    assert response.status_code == 200
    return response.json(), response.headers['etag']


def save(owner, content, tag):
    return owner.put('/api/v1/admin/draft', json=content, headers={'If-Match': tag})


def publish(owner, current):
    return owner.post('/api/v1/admin/publish', json={'expected_draft_revision': current['revision'], 'expected_live_release_id': current['live_release']['id'], 'idempotency_key': str(uuid.uuid4())})


def image_bytes(width=800, height=600):
    stream = io.BytesIO()
    Image.new('RGB', (width, height), 'teal').save(stream, format='PNG')
    return stream.getvalue()


def upload(owner, data=None, name='portrait.png'):
    response = owner.post('/api/v1/admin/media', files={'file': (name, data or image_bytes(), 'application/octet-stream')})
    assert response.status_code == 201, response.text
    return response.json()


def contact(client, key=None, **changes):
    body = {'name': 'A visitor', 'email': 'visitor@example.com', 'message': 'A thoughtful portfolio inquiry.'}
    body.update(changes)
    return client.post('/api/v1/contact', json=body, headers={**ORIGIN, 'Idempotency-Key': key or str(uuid.uuid4())})


def test_draft_isolation_and_stale_save(owner):
    current, tag = draft(owner)
    current['content']['profile']['intro'] = 'This sentence is private draft content.'
    saved = save(owner, current['content'], tag)
    assert saved.status_code == 200
    assert save(owner, current['content'], tag).status_code == 412
    assert owner.put('/api/v1/admin/draft', json=current['content']).status_code == 428
    assert 'private draft' not in owner.get('/api/v1/site').text
    assert 'private draft' in owner.get('/api/v1/admin/preview').text
    assert saved.json()['revision'] == current['revision'] + 1


def test_publish_is_atomic_idempotent_and_old_receipt_cannot_rollback(owner):
    current, tag = draft(owner)
    first_live = current['live_release']['id']
    current['content']['profile']['intro'] = 'A freshly published introduction.'
    saved = save(owner, current['content'], tag).json()
    body = {'expected_draft_revision': saved['revision'], 'expected_live_release_id': first_live, 'idempotency_key': str(uuid.uuid4())}
    first = owner.post('/api/v1/admin/publish', json=body)
    assert first.status_code == 201, first.text
    assert owner.get('/api/v1/site').json()['content']['profile']['intro'] == 'A freshly published introduction.'
    replay = owner.post('/api/v1/admin/publish', json=body)
    assert replay.status_code == 200 and replay.json() == first.json()
    conflict = owner.post('/api/v1/admin/publish', json={**body, 'expected_draft_revision': saved['revision'] + 1})
    assert conflict.status_code == 409
    next_draft, _ = draft(owner)
    second = publish(owner, next_draft)
    assert second.status_code == 201
    owner.post('/api/v1/admin/publish', json=body)
    assert owner.get('/api/v1/site').json()['release']['id'] == second.json()['release']['id']


def test_publication_rejects_incomplete_visible_project_but_save_succeeds(owner):
    current, tag = draft(owner)
    current['content']['projects'][0]['summary'] = ''
    saved = save(owner, current['content'], tag)
    assert saved.status_code == 200
    response = publish(owner, saved.json())
    assert response.status_code == 422
    assert response.json()['error']['details']['field_errors'][0]['path'] == 'projects.0.summary'
    assert owner.get('/api/v1/site').json()['release']['id'] == current['live_release']['id']


def test_restore_keeps_live_and_hidden_content(owner):
    current, tag = draft(owner)
    initial = current['live_release']['id']
    current['content']['projects'][0]['is_visible'] = False
    saved = save(owner, current['content'], tag).json()
    live = publish(owner, saved).json()['release']['id']
    latest, tag = draft(owner)
    restored = owner.post(f'/api/v1/admin/releases/{initial}/restore', headers={'If-Match': tag})
    assert restored.status_code == 200
    assert restored.json()['revision'] == latest['revision'] + 1
    assert restored.json()['content']['projects'][0]['is_visible'] is True
    assert owner.get('/api/v1/site').json()['release']['id'] == live


def test_alias_resolves_current_slug_and_withdrawal_returns404(owner):
    current, tag = draft(owner)
    current['content']['projects'][0]['slug'] = 'city-weather'
    saved = save(owner, current['content'], tag).json()
    assert publish(owner, saved).status_code == 201
    assert owner.get('/api/v1/projects/weather-app').json()['canonical_slug'] == 'city-weather'
    current, tag = draft(owner)
    current['content']['projects'][0]['is_visible'] = False
    saved = save(owner, current['content'], tag).json()
    publish(owner, saved)
    assert owner.get('/api/v1/projects/weather-app').status_code == 404
    assert owner.get('/api/v1/projects/city-weather').status_code == 404
    current, tag = draft(owner)
    current['content']['projects'][1]['slug'] = 'weather-app'
    saved = save(owner, current['content'], tag).json()
    assert publish(owner, saved).status_code == 409


def test_sessions_hash_only_csrf_origin_and_logout(owner):
    current, tag = draft(owner)
    with session_factory()() as db:
        record = db.scalar(select(AdminSession))
        assert record.token_digest != owner.cookies[get_settings().cookie_name]
        assert len(record.token_digest) == 64
    response = owner.put('/api/v1/admin/draft', json=current['content'], headers={'If-Match': tag, 'X-CSRF-Token': ''})
    assert response.status_code == 403
    assert owner.post('/api/v1/admin/auth/logout', headers={'Origin': 'https://foreign.example'}).status_code == 403
    assert owner.post('/api/v1/admin/auth/logout').status_code == 204
    assert owner.get('/api/v1/admin/draft').status_code == 401


def test_session_inactivity_is_enforced(owner):
    with session_factory()() as db:
        record = db.scalar(select(AdminSession))
        record.last_activity_at = now() - timedelta(hours=2)
        db.commit()
    assert owner.get('/api/v1/admin/auth/session').status_code == 401


def test_password_spaces_are_preserved(client):
    password = '  a long private passphrase  '
    with session_factory()() as db:
        create_owner(db, 'owner@example.com', password)
    response = client.post('/api/v1/admin/auth/login', json={'email': 'owner@example.com', 'password': password}, headers=ORIGIN)
    assert response.status_code == 200
    assert client.post('/api/v1/admin/auth/login', json={'email': 'owner@example.com', 'password': password.strip()}, headers=ORIGIN).status_code == 401


def test_contact_retry_delete_tombstone_and_conflict(owner):
    key = str(uuid.uuid4())
    first = contact(owner, key)
    assert first.status_code == 201
    second = contact(owner, key)
    assert second.status_code == 200 and first.json() == second.json()
    assert contact(owner, key, message='A different sufficiently long message.').status_code == 409
    receipt = first.json()['receipt_id']
    assert owner.get('/api/v1/admin/contact').json()['unread_count'] == 1
    assert owner.delete(f'/api/v1/admin/contact/{receipt}').status_code == 204
    assert contact(owner, key).json() == first.json()
    assert owner.get('/api/v1/admin/contact').json()['items'] == []
    with session_factory()() as db:
        record = db.get(ContactSubmission, uuid.UUID(receipt))
        assert record.message is None and record.email is None


def test_contact_concurrent_retry_has_one_record(client):
    key = str(uuid.uuid4())
    def request(_):
        with TestClient(app, base_url='http://localhost:3000') as other:
            return contact(other, key)
    with ThreadPoolExecutor(max_workers=4) as executor:
        responses = list(executor.map(request, range(4)))
    assert sorted(r.status_code for r in responses) == [200, 200, 200, 201]
    assert len({r.json()['receipt_id'] for r in responses}) == 1
    with session_factory()() as db:
        assert db.scalar(select(func.count()).select_from(ContactSubmission)) == 1


def test_rate_limit_replays_are_free_and_untrusted_forwarding_does_not_bypass(client):
    key = str(uuid.uuid4())
    assert contact(client, key).status_code == 201
    for _ in range(7):
        assert contact(client, key).status_code == 200
    for _ in range(4):
        assert contact(client).status_code == 201
    client.headers['X-Forwarded-For'] = '203.0.113.99'
    response = contact(client)
    assert response.status_code == 429 and int(response.headers['retry-after']) > 0


def test_inbox_status_persists_and_pagination(owner):
    receipts = [contact(owner).json()['receipt_id'] for _ in range(3)]
    page = owner.get('/api/v1/admin/contact?limit=2').json()
    assert page['has_more'] and len(page['items']) == 2
    next_page = owner.get('/api/v1/admin/contact', params={'limit': 2, 'cursor': page['next_cursor']}).json()
    assert len(next_page['items']) == 1
    target = receipts[0]
    response = owner.patch(f'/api/v1/admin/contact/{target}/status', json={'is_read': True, 'is_archived': True})
    assert response.status_code == 200
    assert owner.get('/api/v1/admin/contact?status=archived').json()['items'][0]['id'] == target
    assert owner.get('/api/v1/admin/contact?status=all').json()['unread_count'] == 2


def test_media_private_until_published_then_unavailable_when_removed(owner):
    asset = upload(owner)
    private = asset['variants']['full']['url']
    public = private.replace('/admin/media/', '/media/')
    assert owner.get(public).status_code == 404
    with TestClient(app) as anon:
        assert anon.get(private).status_code == 401
    current, tag = draft(owner)
    current['content']['profile']['portrait'] = {'asset_id': asset['id'], 'alt': 'A real portrait supplied by its owner', 'caption': None}
    saved = save(owner, current['content'], tag).json()
    assert owner.get(public).status_code == 404
    assert publish(owner, saved).status_code == 201
    assert owner.get(public).status_code == 200
    assert owner.head(public).status_code == 200
    assert owner.delete('/api/v1/admin/media/' + asset['id']).status_code == 409
    current, tag = draft(owner)
    current['content']['profile']['portrait'] = None
    saved = save(owner, current['content'], tag).json()
    publish(owner, saved)
    assert owner.get(public).status_code == 404
    assert owner.head(public).status_code == 404
    assert owner.delete('/api/v1/admin/media/' + asset['id']).status_code == 409  # retained release


def test_crop_checks_source_pixel_ratio_and_creates_immutable_variants(owner):
    asset = upload(owner)
    incorrect = owner.post(f'/api/v1/admin/media/{asset["id"]}/crop', json={'x': 0, 'y': 0, 'width': .8, 'height': 1})
    assert incorrect.status_code == 422  # .8/1 normalized ratio is wrong for 800x600
    result = owner.post(f'/api/v1/admin/media/{asset["id"]}/crop', json={'x': .2, 'y': 0, 'width': .6, 'height': 1})
    assert result.status_code == 201, result.text
    assert result.json()['id'] != asset['id']
    for variant in result.json()['variants'].values():
        assert variant['width'] * 5 == variant['height'] * 4
    assert owner.delete('/api/v1/admin/media/' + asset['id']).status_code == 409


def test_uploads_reject_svg_animation_invalid_pdf_and_oversize(owner):
    for name, data in [('vector.svg', b'<svg></svg>'), ('fake.pdf', b'%PDF-not really a document')]:
        response = owner.post('/api/v1/admin/media', files={'file': (name, data)})
        assert response.status_code == 415
    response = owner.post('/api/v1/admin/media', files={'file': ('large.png', b'x' * (8 * 1024 * 1024 + 1))})
    assert response.status_code == 413


def test_pdf_resume_download_requires_publication(owner):
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buffer = io.BytesIO()
    writer.write(buffer)
    asset = upload(owner, buffer.getvalue(), 'resume.pdf')
    current, tag = draft(owner)
    current['content']['profile']['resume_asset_id'] = asset['id']
    current['content']['settings']['show_resume'] = True
    saved = save(owner, current['content'], tag).json()
    assert owner.get('/api/v1/resume').status_code == 404
    publish(owner, saved)
    response = owner.get('/api/v1/resume')
    assert response.status_code == 200 and response.content.startswith(b'%PDF-')
    assert response.headers['content-disposition'].endswith('"Gagandeep_Kaur_Resume.pdf"')
    assert 'resume_asset_id' not in owner.get('/api/v1/site').text


def test_seed_is_idempotent_and_preserves_owner_edits(owner):
    current, tag = draft(owner)
    current['content']['profile']['intro'] = 'Owner-written introduction preserved.'
    saved = save(owner, current['content'], tag).json()
    with session_factory()() as db:
        assert seed_site(db) is False
        assert db.get(SiteDraft, 1).revision == saved['revision']
    assert draft(owner)[0]['content']['profile']['intro'] == 'Owner-written introduction preserved.'


def test_invalid_unknown_keys_unsafe_links_and_precise_dates(owner):
    current, tag = draft(owner)
    bad = copy.deepcopy(current['content'])
    bad['profile']['github_url'] = 'javascript:alert(1)'
    assert save(owner, bad, tag).status_code == 422
    bad = copy.deepcopy(current['content'])
    bad['projects'][0]['extra_html'] = '<script>bad</script>'
    assert save(owner, bad, tag).status_code == 422
    bad = copy.deepcopy(current['content'])
    bad['experience'][0]['start'] = {'value': '2025-08-01', 'precision': 'month'}
    assert save(owner, bad, tag).status_code == 422
    assert owner.get('/api/v1/admin/releases?cursor=garbage').status_code == 400


def test_health_and_public_headers(client):
    assert client.get('/api/v1/health/live').status_code == 200
    assert client.get('/api/v1/health/ready').status_code == 200
    response = client.get('/api/v1/site')
    assert response.headers['cache-control'] == 'no-store'
    assert uuid.UUID(response.headers['x-request-id'])
    assert client.get('/api/v1/admin/preview').headers['x-robots-tag'] == 'noindex, nofollow'


def test_contact_validation_honeypot_origin_and_body_limit(client):
    assert contact(client, message='short').status_code == 422
    assert contact(client, website='https://bot.example').status_code == 400
    assert client.post('/api/v1/contact', json={}).status_code == 403
    response = client.post('/api/v1/contact', content=json.dumps({'message': 'x' * 18000}), headers={**ORIGIN, 'Content-Type': 'application/json', 'Idempotency-Key': str(uuid.uuid4())})
    assert response.status_code == 413


def test_pdf_allows_internal_page_view_but_rejects_javascript(owner):
    from pypdf.generic import ArrayObject, DictionaryObject, NameObject, TextStringObject
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    writer._root_object[NameObject('/OpenAction')] = DictionaryObject({NameObject('/S'): NameObject('/GoTo'), NameObject('/D'): ArrayObject([page.indirect_reference, NameObject('/Fit')])})
    buffer = io.BytesIO()
    writer.write(buffer)
    safe = owner.post('/api/v1/admin/media', files={'file': ('resume.pdf', buffer.getvalue(), 'application/pdf')})
    assert safe.status_code == 201, safe.text
    writer._root_object[NameObject('/OpenAction')] = DictionaryObject({NameObject('/S'): NameObject('/JavaScript'), NameObject('/JS'): TextStringObject('app.alert("unsafe")')})
    malicious = io.BytesIO()
    writer.write(malicious)
    assert owner.post('/api/v1/admin/media', files={'file': ('unsafe.pdf', malicious.getvalue(), 'application/pdf')}).status_code == 415


def test_hidden_section_introductions_do_not_leak_into_public_snapshot(owner):
    current, tag = draft(owner)
    current['content']['settings']['visible_sections'].remove('experience')
    current['content']['settings']['section_intros']['experience']['description'] = 'Unannounced private experience introduction.'
    saved = save(owner, current['content'], tag).json()
    assert publish(owner, saved).status_code == 201
    assert 'Unannounced private' not in owner.get('/api/v1/site').text


def test_competing_publishes_only_one_commits(owner):
    current, _ = draft(owner)
    cookies = dict(owner.cookies)
    headers = dict(owner.headers)
    def submit(_):
        with TestClient(app, base_url='http://localhost:3000', cookies=cookies, headers=headers) as other:
            return publish(other, current)
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(submit, range(2)))
    assert sorted(r.status_code for r in responses) == [201, 409]
    with session_factory()() as db:
        assert db.scalar(select(func.count()).select_from(SiteRelease)) == 2


def test_transaction_failure_before_publish_commit_preserves_live(owner):
    from sqlalchemy import event
    from app.services.content import publish as publish_service
    from app.schemas import PublishRequest
    current, _ = draft(owner)
    with session_factory()() as db:
        def fail_commit(session):
            raise RuntimeError('Simulated failure before commit')
        event.listen(db, 'before_commit', fail_commit)
        try:
            publish_service(db, PublishRequest(expected_draft_revision=current['revision'], expected_live_release_id=uuid.UUID(current['live_release']['id']), idempotency_key=uuid.uuid4()))
        except RuntimeError:
            db.rollback()
        else:
            raise AssertionError('Failure injection did not execute')
    assert owner.get('/api/v1/site').json()['release']['id'] == current['live_release']['id']
    with session_factory()() as db:
        assert db.scalar(select(func.count()).select_from(SiteRelease)) == 1


def test_concurrent_contact_quota_is_transactional(client):
    def submit(_):
        with TestClient(app, base_url='http://localhost:3000') as other:
            return contact(other)
    with ThreadPoolExecutor(max_workers=10) as executor:
        responses = list(executor.map(submit, range(10)))
    assert sorted(r.status_code for r in responses) == [201] * 5 + [429] * 5


def test_reauthentication_rotates_and_revokes_presented_session(owner):
    previous = owner.cookies[get_settings().cookie_name]
    response = owner.post('/api/v1/admin/auth/login', json={'email': 'owner@example.com', 'password': 'test-only-passphrase-12345'})
    assert response.status_code == 200
    assert owner.cookies[get_settings().cookie_name] != previous
    with TestClient(app, base_url='http://localhost:3000', cookies={get_settings().cookie_name: previous}) as old_client:
        assert old_client.get('/api/v1/admin/auth/session').status_code == 401


def test_password_change_revokes_other_sessions(owner):
    with TestClient(app, base_url='http://localhost:3000') as other:
        old = other.post('/api/v1/admin/auth/login', json={'email': 'owner@example.com', 'password': 'test-only-passphrase-12345'}, headers=ORIGIN)
        assert old.status_code == 200
        changed = owner.post('/api/v1/admin/auth/change-password', json={'current_password': 'test-only-passphrase-12345', 'new_password': 'another-test-only-passphrase'})
        assert changed.status_code == 200
        assert changed.json()['csrf_token'] != owner.headers['x-csrf-token']
        assert other.get('/api/v1/admin/auth/session').status_code == 401
        assert owner.get('/api/v1/admin/auth/session').status_code == 200


def test_public_retention_notice_tracks_operator_policy_without_republishing(client, monkeypatch):
    monkeypatch.setattr(get_settings(), 'contact_retention_days', 90)
    assert client.get('/api/v1/site').json()['content']['contact_retention_days'] == 90


def test_pdf_cannot_alias_portrait_and_resume_even_when_resume_hidden(owner):
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buffer = io.BytesIO()
    writer.write(buffer)
    asset = upload(owner, buffer.getvalue(), 'private-resume.pdf')
    current, tag = draft(owner)
    prior_live = owner.get('/api/v1/site').json()
    invalid = copy.deepcopy(current['content'])
    invalid['profile']['portrait'] = {'asset_id': asset['id'], 'alt': 'Portrait', 'caption': None}
    invalid['profile']['resume_asset_id'] = asset['id']
    invalid['settings']['show_resume'] = False
    response = save(owner, invalid, tag)
    assert response.status_code == 422, response.text
    assert response.json()['error']['code'] == 'MEDIA_KIND_MISMATCH'
    assert draft(owner)[0] == current
    assert owner.get('/api/v1/site').json() == prior_live
    assert owner.get(f'/api/v1/media/{asset["id"]}/document').status_code == 404

    # Publication also validates references in a pre-existing/imported draft.
    with session_factory()() as db:
        row = db.get(SiteDraft, 1)
        row.content = invalid
        db.commit()
    rejected_publish = publish(owner, current)
    assert rejected_publish.status_code == 422
    assert rejected_publish.json()['error']['code'] == 'MEDIA_KIND_MISMATCH'
    assert owner.get('/api/v1/site').json() == prior_live
    with session_factory()() as db:
        assert db.get(SiteDraft, 1).revision == current['revision']
        assert db.scalar(select(func.count()).select_from(SiteRelease)) == 1
