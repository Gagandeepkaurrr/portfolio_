import hashlib
import json
import re
from uuid import UUID
from sqlalchemy import select
from app.config import get_settings
from app.db import now
from app.errors import APIError
from app.models import MediaAsset, SiteDraft, SiteRelease, SiteState, SlugRedirect
from app.schemas import SiteContent, PublicSiteContent, PublicProject
from app.security.auth import audit

COLLECTIONS = ('projects', 'experience', 'leadership', 'education', 'skill_groups', 'recognition', 'certifications')


def canonical_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def typed_references(content: SiteContent) -> dict[UUID, str]:
    refs = {}
    if content.profile.portrait:
        refs[content.profile.portrait.asset_id] = 'image'
    if content.profile.resume_asset_id:
        if content.profile.resume_asset_id in refs and refs[content.profile.resume_asset_id] != 'pdf':
            raise APIError(422, 'MEDIA_KIND_MISMATCH', 'An asset cannot be used as both an image and a résumé PDF.')
        refs[content.profile.resume_asset_id] = 'pdf'
    for project in content.projects:
        for ref in ([project.cover] if project.cover else []) + project.gallery:
            if ref.asset_id in refs and refs[ref.asset_id] != 'image':
                raise APIError(422, 'MEDIA_KIND_MISMATCH', 'A PDF cannot be used as an image.')
            refs[ref.asset_id] = 'image'
    return refs


def validate_assets(db, content: SiteContent, lock=True):
    refs = typed_references(content)
    assets = {}
    for asset_id in sorted(refs, key=str):
        query = select(MediaAsset).where(MediaAsset.id == asset_id)
        if lock:
            query = query.with_for_update()
        asset = db.scalar(query)
        if not asset or asset.status != 'ready' or asset.kind != refs[asset_id]:
            raise APIError(422, 'MEDIA_NOT_READY', 'A selected asset is missing, unavailable or the wrong type.', {'asset_id': str(asset_id)})
        assets[asset_id] = asset
    return assets


def publication_errors(content: SiteContent):
    errors = []
    slugs = set()
    for i, project in enumerate(content.projects):
        if not project.is_visible or 'work' not in content.settings.visible_sections:
            continue
        for field in ('slug', 'summary', 'overview', 'technologies'):
            if not getattr(project, field):
                errors.append({'path': f'projects.{i}.{field}', 'message': 'Required for a visible published project.'})
        if project.slug in slugs:
            errors.append({'path': f'projects.{i}.slug', 'message': 'Visible project slugs must be unique.'})
        slugs.add(project.slug)
    if content.settings.availability_enabled and not content.settings.availability_text:
        errors.append({'path': 'settings.availability_text', 'message': 'Provide wording before enabling availability.'})
    if get_settings().app_env == 'production' and content.settings.site_url.rstrip('/') != get_settings().public_origin:
        errors.append({'path': 'settings.site_url', 'message': 'Canonical site URL must match PUBLIC_ORIGIN in production.'})
    return errors


def media_variants(asset, preview=False):
    prefix = '/api/v1/admin/media' if preview else '/api/v1/media'
    return {name: {'url': f'{prefix}/{asset.id}/{name}', 'width': value.get('width'), 'height': value.get('height'), 'mime': value['mime'], 'byte_size': value['byte_size']} for name, value in asset.variants.items()}


def resolve_ref(ref, assets, preview):
    if not ref:
        return None
    asset = assets[ref.asset_id]
    variants = media_variants(asset, preview)
    variant = variants.get('full') or next(iter(variants.values()))
    return {**ref.model_dump(mode='json'), 'url': variant['url'], 'width': variant['width'], 'height': variant['height'], 'variants': variants}


def project_projection(project, assets, preview=False):
    raw = project.model_dump(mode='json')
    raw['cover'] = resolve_ref(project.cover, assets, preview)
    raw['gallery'] = [resolve_ref(ref, assets, preview) for ref in project.gallery]
    return PublicProject.model_validate(raw).model_dump(mode='json')


def project_public(content, assets, preview=False):
    data = content.model_dump(mode='json')
    visible = set(content.settings.visible_sections)
    section_map = {'projects': 'work', 'experience': 'experience', 'leadership': 'community', 'education': 'about', 'skill_groups': 'about', 'recognition': 'about', 'certifications': 'about'}
    for name in COLLECTIONS:
        data[name] = [x.model_dump(mode='json') for x in getattr(content, name) if x.is_visible and section_map[name] in visible]
    # Community feature can remain visible even when the qualifications section is disabled.
    featured = content.settings.featured_recognition_id
    if 'community' in visible and featured and not any(x['id'] == str(featured) for x in data['recognition']):
        data['recognition'] += [x.model_dump(mode='json') for x in content.recognition if x.is_visible and x.id == featured]
    data['projects'] = [project_projection(p, assets, preview) for p in content.projects if p.is_visible and 'work' in visible]
    profile = data['profile']
    profile.pop('resume_asset_id')
    if not content.settings.show_phone:
        profile.pop('phone_display')
        profile.pop('phone_e164')
    if 'about' not in visible:
        profile['biography'] = ''
    profile['portrait'] = resolve_ref(content.profile.portrait, assets, preview)
    profile['resume_available'] = bool(content.settings.show_resume and content.profile.resume_asset_id)
    profile['resume_url'] = (f'/api/v1/admin/media/{content.profile.resume_asset_id}/document' if preview else '/api/v1/resume') if profile['resume_available'] else None
    for section in set(data['settings']['section_intros']) - visible:
        data['settings']['section_intros'][section] = {'heading': '', 'description': ''}
        data['settings']['section_labels'][section] = section.capitalize()
    visible_ids = {p['id'] for p in data['projects']}
    data['settings']['featured_project_ids'] = [p for p in data['settings']['featured_project_ids'] if p in visible_ids]
    if featured and not any(x['id'] == str(featured) for x in data['recognition']):
        data['settings']['featured_recognition_id'] = None
    if not data['settings']['availability_enabled']:
        data['settings']['availability_text'] = None
    data['contact_retention_days'] = get_settings().contact_retention_days
    return PublicSiteContent.model_validate(data).model_dump(mode='json')


def public_asset_ids(content):
    refs = set()
    portrait = content['profile']['portrait']
    if portrait:
        refs.add(portrait['asset_id'])
    for p in content['projects']:
        for ref in ([p['cover']] if p['cover'] else []) + p['gallery']:
            refs.add(ref['asset_id'])
    return sorted(refs)


def release_summary(release):
    if not release:
        return None
    return {'id': str(release.id), 'revision': release.revision, 'published_at': release.created_at}


def live_release(db):
    return db.scalar(select(SiteRelease).join(SiteState, SiteState.live_release_id == SiteRelease.id).where(SiteState.id == 1))


def require_live(db):
    release = live_release(db)
    if not release:
        raise APIError(503, 'SITE_UNPUBLISHED', 'The portfolio is being prepared. Please try again soon.')
    return release


def lock_draft(db):
    draft = db.scalar(select(SiteDraft).where(SiteDraft.id == 1).with_for_update())
    if not draft:
        raise APIError(503, 'SITE_NOT_INITIALIZED', 'Run the site seed command first.')
    return draft


def check_etag(draft, supplied):
    if supplied is None:
        raise APIError(428, 'PRECONDITION_REQUIRED', 'Supply the current draft revision before saving.')
    if not re.fullmatch(r'"draft-[1-9][0-9]*"', supplied) or supplied != f'"draft-{draft.revision}"':
        raise APIError(412, 'DRAFT_REVISION_MISMATCH', 'The draft changed. Reload before saving.', {'current_revision': draft.revision})


def draft_envelope(db, draft):
    return {'revision': draft.revision, 'content': draft.content, 'live_release': release_summary(live_release(db)), 'updated_at': draft.updated_at}


def save_draft(db, content, etag, owner):
    draft = lock_draft(db)
    check_etag(draft, etag)
    validate_assets(db, content)
    draft.content = content.model_dump(mode='json')
    draft.revision += 1
    draft.updated_by = owner.id
    draft.updated_at = now()
    db.commit()
    return draft_envelope(db, draft)


def publish(db, body, owner=None, request=None):
    draft = lock_draft(db)
    state = db.scalar(select(SiteState).where(SiteState.id == 1).with_for_update())
    request_hash = canonical_hash(body.model_dump(mode='json'))
    existing = db.scalar(select(SiteRelease).where(SiteRelease.publish_idempotency_key == body.idempotency_key))
    if existing:
        if existing.publish_request_hash != request_hash:
            raise APIError(409, 'IDEMPOTENCY_CONFLICT', 'This publication key was used for a different request.')
        return {'release': release_summary(existing), 'source_draft_revision': existing.source_draft_revision}, False
    if draft.revision != body.expected_draft_revision or state.live_release_id != body.expected_live_release_id:
        raise APIError(409, 'PUBLICATION_CONFLICT', 'The saved draft or live release changed. Review the current content before publishing.', {'current_draft_revision': draft.revision, 'current_live_release_id': str(state.live_release_id) if state.live_release_id else None})
    content = SiteContent.model_validate(draft.content)
    errors = publication_errors(content)
    if errors:
        raise APIError(422, 'PUBLICATION_INVALID', 'Complete the visible content before publishing.', {'field_errors': errors})
    assets = validate_assets(db, content)
    public = project_public(content, assets)
    aliases = {a.old_slug: a for a in db.scalars(select(SlugRedirect))}
    for p in public['projects']:
        alias = aliases.get(p['slug'])
        if alias and str(alias.project_id) != p['id']:
            raise APIError(409, 'SLUG_OWNERSHIP_CONFLICT', 'That slug belongs to a different project.', {'slug': p['slug']})
    resume = content.profile.resume_asset_id if public['profile']['resume_available'] else None
    asset_ids = public_asset_ids(public)
    if resume:
        asset_ids.append(str(resume))
    release = SiteRelease(source_content=content.model_dump(mode='json'), public_content=public, public_asset_ids=asset_ids, resume_asset_id=resume, content_hash=canonical_hash(content.model_dump(mode='json')), source_draft_revision=draft.revision, publish_idempotency_key=body.idempotency_key, publish_request_hash=request_hash, created_by=owner.id if owner else None)
    db.add(release)
    db.flush()
    for p in public['projects']:
        if p['slug'] not in aliases:
            db.add(SlugRedirect(old_slug=p['slug'], project_id=UUID(p['id']), created_release_id=release.id))
    state.live_release_id = release.id
    state.updated_at = now()
    audit(db, 'publish', actor=owner.id if owner else None, target_type='release', target_id=release.id, request=request)
    db.commit()
    return {'release': release_summary(release), 'source_draft_revision': draft.revision}, True


def restore(db, release_id, etag, owner, request=None):
    draft = lock_draft(db)
    check_etag(draft, etag)
    release = db.get(SiteRelease, release_id)
    if not release:
        raise APIError(404, 'RELEASE_NOT_FOUND', 'Release not found.')
    content = SiteContent.model_validate(release.source_content)
    validate_assets(db, content)
    draft.content = content.model_dump(mode='json')
    draft.revision += 1
    draft.updated_by = owner.id
    draft.updated_at = now()
    audit(db, 'restore_draft', owner.id, 'release', release.id, request)
    db.commit()
    return draft_envelope(db, draft)
