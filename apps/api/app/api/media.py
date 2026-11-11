from uuid import UUID
from fastapi import APIRouter, Depends, File, Query, Request, Response, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.errors import APIError
from app.models import MediaAsset
from app.pagination import paginate
from app.schemas import CropRequest, MediaMetadata, MediaPage
from app.security.auth import owner_session, require_json
from app.services import media as svc
from app.services.content import require_live
from app.storage.local import LocalStorage

router = APIRouter(tags=['media'])


def serve_asset(db, asset_id, variant, head=False, public=False, resume=False):
    if variant not in ('thumb', 'card', 'full', 'document'):
        raise APIError(404, 'MEDIA_NOT_FOUND', 'Media not found.')
    if public:
        release = require_live(db)
        if str(asset_id) not in release.public_asset_ids:
            raise APIError(404, 'MEDIA_NOT_FOUND', 'Media not found.')
    asset = db.get(MediaAsset, asset_id)
    if not asset or asset.status != 'ready' or variant not in asset.variants:
        raise APIError(404, 'MEDIA_NOT_FOUND', 'Media not found.')
    version = asset.variants[variant]
    try:
        content = LocalStorage().read_private(version['key'])
    except OSError:
        raise APIError(503, 'MEDIA_UNAVAILABLE', 'Media is temporarily unavailable.')
    headers = {'Content-Length': str(len(content)), 'X-Content-Type-Options': 'nosniff'}
    if asset.kind == 'pdf':
        headers['Content-Disposition'] = 'attachment; filename="Gagandeep_Kaur_Resume.pdf"' if resume else 'attachment; filename="document.pdf"'
        headers['Content-Security-Policy'] = "default-src 'none'; sandbox"
    return Response(content=b'' if head else content, media_type=version['mime'], headers=headers)


@router.get('/media/{asset_id}/{variant}')
@router.head('/media/{asset_id}/{variant}', include_in_schema=False)
def public_media(asset_id: UUID, variant: str, request: Request, db: Session = Depends(get_db)):
    return serve_asset(db, asset_id, variant, head=request.method == 'HEAD', public=True)


@router.get('/resume')
@router.head('/resume', include_in_schema=False)
def resume(request: Request, db: Session = Depends(get_db)):
    release = require_live(db)
    if not release.resume_asset_id:
        raise APIError(404, 'RESUME_UNAVAILABLE', 'No résumé is currently published.')
    return serve_asset(db, release.resume_asset_id, 'document', head=request.method == 'HEAD', public=True, resume=True)


@router.get('/admin/media', response_model=MediaPage)
def media_list(kind: str | None = None, search: str | None = Query(default=None, max_length=180), cursor: str | None = None, limit: int = Query(default=30, ge=1, le=100), db: Session = Depends(get_db), auth=Depends(owner_session)):
    query = select(MediaAsset).where(MediaAsset.status == 'ready')
    if kind:
        if kind not in ('image', 'pdf'):
            raise APIError(400, 'INVALID_KIND', 'Choose image or pdf.')
        query = query.where(MediaAsset.kind == kind)
    if search:
        query = query.where(MediaAsset.original_display_name.icontains(search, autoescape=True))
    items, pagination = paginate(db, query, MediaAsset, cursor, limit)
    return {'items': [svc.asset_metadata(db, x) for x in items], **pagination}


@router.post('/admin/media', status_code=201, response_model=MediaMetadata)
def upload(file: UploadFile = File(...), db: Session = Depends(get_db), auth=Depends(owner_session)):
    data = file.file.read(svc.PDF_LIMIT + 1)
    if len(data) > svc.PDF_LIMIT:
        raise APIError(413, 'FILE_TOO_LARGE', 'Files must be at most 10 MiB; images at most 8 MiB.')
    asset = svc.upload_bytes(db, data, file.filename, auth[0])
    return svc.asset_metadata(db, asset)


@router.post('/admin/media/{asset_id}/crop', status_code=201, response_model=MediaMetadata)
def crop(asset_id: UUID, body: CropRequest, request: Request, db: Session = Depends(get_db), auth=Depends(owner_session)):
    require_json(request)
    asset = svc.crop_asset(db, asset_id, body, auth[0])
    return svc.asset_metadata(db, asset)


@router.get('/admin/media/{asset_id}/{variant}')
@router.head('/admin/media/{asset_id}/{variant}', include_in_schema=False)
def private_media(asset_id: UUID, variant: str, request: Request, db: Session = Depends(get_db), auth=Depends(owner_session)):
    return serve_asset(db, asset_id, variant, head=request.method == 'HEAD')


@router.delete('/admin/media/{asset_id}', status_code=204)
def delete(asset_id: UUID, request: Request, db: Session = Depends(get_db), auth=Depends(owner_session)):
    svc.delete_asset(db, asset_id, auth[0], request)
