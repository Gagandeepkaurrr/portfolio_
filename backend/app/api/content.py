from uuid import UUID
from fastapi import APIRouter, Depends, Header, Query, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.config import get_settings
from app.errors import APIError
from app.models import SiteDraft, SiteRelease, SlugRedirect
from app.pagination import paginate
from app.schemas import PublishRequest, SiteContent, SiteEnvelope, ProjectEnvelope, DraftEnvelope, PreviewEnvelope, ProjectPreviewEnvelope, PublishEnvelope, ReleasePage, ReleaseDetail
from app.security.auth import owner_session, require_json
from app.services import content as svc

router = APIRouter(tags=['content'])


@router.get('/site', response_model=SiteEnvelope)
def public_site(db: Session = Depends(get_db)):
    release = svc.require_live(db)
    return {'release': svc.release_summary(release), 'content': {**release.public_content, 'contact_retention_days': get_settings().contact_retention_days}}


@router.get('/projects/{slug}', response_model=ProjectEnvelope)
def project(slug: str, db: Session = Depends(get_db)):
    release = svc.require_live(db)
    found = next((p for p in release.public_content['projects'] if p['slug'] == slug), None)
    if not found:
        alias = db.get(SlugRedirect, slug)
        if alias:
            found = next((p for p in release.public_content['projects'] if p['id'] == str(alias.project_id)), None)
    if not found:
        raise APIError(404, 'PROJECT_NOT_FOUND', 'Project not found.')
    return {'release': svc.release_summary(release), 'requested_slug': slug, 'canonical_slug': found['slug'], 'project': found}


@router.get('/admin/draft', response_model=DraftEnvelope)
def draft(response: Response, db: Session = Depends(get_db), auth=Depends(owner_session)):
    row = db.get(SiteDraft, 1)
    if not row:
        raise APIError(503, 'SITE_NOT_INITIALIZED', 'Run the site seed command first.')
    response.headers['ETag'] = f'"draft-{row.revision}"'
    return svc.draft_envelope(db, row)


@router.put('/admin/draft', response_model=DraftEnvelope)
def save(body: SiteContent, request: Request, response: Response, if_match: str | None = Header(default=None), db: Session = Depends(get_db), auth=Depends(owner_session)):
    require_json(request)
    result = svc.save_draft(db, body, if_match, auth[0])
    response.headers['ETag'] = f'"draft-{result["revision"]}"'
    return result


@router.get('/admin/preview', response_model=PreviewEnvelope)
def preview(db: Session = Depends(get_db), auth=Depends(owner_session)):
    draft = db.get(SiteDraft, 1)
    if not draft:
        raise APIError(503, 'SITE_NOT_INITIALIZED', 'Run seed first.')
    content = SiteContent.model_validate(draft.content)
    assets = svc.validate_assets(db, content, lock=False)
    return {'draft_revision': draft.revision, 'content': svc.project_public(content, assets, preview=True), 'validation_warnings': svc.publication_errors(content)}


@router.get('/admin/preview/projects/{project_id}', response_model=ProjectPreviewEnvelope)
def preview_project(project_id: UUID, db: Session = Depends(get_db), auth=Depends(owner_session)):
    draft = db.get(SiteDraft, 1)
    if not draft:
        raise APIError(503, 'SITE_NOT_INITIALIZED', 'Run seed first.')
    content = SiteContent.model_validate(draft.content)
    project = next((p for p in content.projects if p.id == project_id), None)
    if not project:
        raise APIError(404, 'PROJECT_NOT_FOUND', 'Project not found.')
    assets = svc.validate_assets(db, content, lock=False)
    return {'draft_revision': draft.revision, 'project': svc.project_projection(project, assets, preview=True), 'is_hidden': not project.is_visible, 'validation_warnings': svc.publication_errors(content)}


@router.post('/admin/publish', response_model=PublishEnvelope)
def publish(body: PublishRequest, request: Request, response: Response, db: Session = Depends(get_db), auth=Depends(owner_session)):
    require_json(request)
    result, created = svc.publish(db, body, auth[0], request)
    response.status_code = 201 if created else 200
    return result


@router.get('/admin/releases', response_model=ReleasePage)
def releases(cursor: str | None = None, limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db), auth=Depends(owner_session)):
    items, pagination = paginate(db, select(SiteRelease), SiteRelease, cursor, limit)
    return {'items': [{**svc.release_summary(r), 'source_draft_revision': r.source_draft_revision, 'content_hash': r.content_hash} for r in items], **pagination}


@router.get('/admin/releases/{release_id}', response_model=ReleaseDetail)
def release_detail(release_id: UUID, db: Session = Depends(get_db), auth=Depends(owner_session)):
    row = db.get(SiteRelease, release_id)
    if not row:
        raise APIError(404, 'RELEASE_NOT_FOUND', 'Release not found.')
    return {**svc.release_summary(row), 'source_draft_revision': row.source_draft_revision, 'source_content': row.source_content, 'content': row.source_content}


@router.post('/admin/releases/{release_id}/restore', response_model=DraftEnvelope)
def restore(release_id: UUID, request: Request, response: Response, if_match: str | None = Header(default=None), db: Session = Depends(get_db), auth=Depends(owner_session)):
    result = svc.restore(db, release_id, if_match, auth[0], request)
    response.headers['ETag'] = f'"draft-{result["revision"]}"'
    return result
