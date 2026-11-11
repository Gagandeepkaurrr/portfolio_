import hashlib
import io
import logging
import warnings
from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError
from pypdf import PdfReader
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject
from sqlalchemy import select
from app.db import now
from app.errors import APIError
from app.models import MediaAsset, SiteDraft, SiteRelease
from app.schemas import SiteContent
from app.security.auth import audit
from app.services.content import lock_draft, media_variants, typed_references
from app.storage.local import LocalStorage

IMAGE_LIMIT = 8 * 1024 * 1024
PDF_LIMIT = 10 * 1024 * 1024
PIXEL_LIMIT = 24_000_000
Image.MAX_IMAGE_PIXELS = PIXEL_LIMIT
logger = logging.getLogger('portfolio.media')


def checksum(data):
    return hashlib.sha256(data).hexdigest()


def keys_for(asset):
    return {asset.sanitized_source_key} | {v['key'] for v in asset.variants.values()}


def _encode_image(image):
    output = io.BytesIO()
    image.save(output, format='WEBP', quality=88, method=4)
    return output.getvalue()


def _image_bytes(image):
    storage = LocalStorage()
    keys = []
    try:
        source = _encode_image(image)
        source_key = storage.write_private(source)
        keys.append(source_key)
        variants = {}
        for name, bound in [('thumb', 320), ('card', 960), ('full', 1600)]:
            scaled = image.copy()
            scaled.thumbnail((bound, bound), Image.Resampling.LANCZOS)
            # Cropped portraits retain an exact 4:5 output at all sizes.
            if image.width * 5 == image.height * 4:
                unit = min(scaled.width // 4, scaled.height // 5)
                scaled = image.resize((unit * 4, unit * 5), Image.Resampling.LANCZOS)
            data = _encode_image(scaled)
            key = storage.write_private(data)
            keys.append(key)
            variants[name] = {'key': key, 'mime': 'image/webp', 'width': scaled.width, 'height': scaled.height, 'byte_size': len(data), 'sha256': checksum(data)}
        return {'kind': 'image', 'verified_mime': 'image/webp', 'sanitized_source_key': source_key, 'variants': variants, 'source_width': image.width, 'source_height': image.height, 'byte_size': len(source), 'sha256': checksum(source), 'page_count': None}
    except Exception:
        for key in keys:
            storage.delete(key)
        raise


def decode_image(data):
    if len(data) > IMAGE_LIMIT:
        raise APIError(413, 'IMAGE_TOO_LARGE', 'Images must be at most 8 MiB.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            image: Image.Image = Image.open(io.BytesIO(data))
            if image.format not in ('JPEG', 'PNG', 'WEBP') or getattr(image, 'is_animated', False):
                raise APIError(415, 'UNSUPPORTED_IMAGE', 'Use a still JPEG, PNG or WebP image.')
            if image.width * image.height > PIXEL_LIMIT:
                raise APIError(413, 'IMAGE_PIXELS_EXCEEDED', 'Images must contain at most 24 megapixels.')
            image.load()
            image = ImageOps.exif_transpose(image)
            image = image.convert('RGBA' if image.mode in ('RGBA', 'LA') or 'transparency' in image.info else 'RGB')
            image.info.clear()
            return image
    except APIError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise APIError(415, 'INVALID_IMAGE', 'The image could not be safely decoded.')


def validate_pdf(data):
    if len(data) > PDF_LIMIT:
        raise APIError(413, 'PDF_TOO_LARGE', 'Résumé PDFs must be at most 10 MiB.')
    if not data.startswith(b'%PDF-'):
        raise APIError(415, 'INVALID_PDF', 'Select a valid PDF document.')
    try:
        reader = PdfReader(io.BytesIO(data), strict=True)
        if reader.is_encrypted:
            raise ValueError('Encrypted')
        if not 1 <= len(reader.pages) <= 20:
            raise ValueError('Page count')
        seen = set()
        budget = [50000]
        forbidden = {'/JavaScript', '/JS', '/Launch', '/EmbeddedFiles', '/EmbeddedFile', '/AA', '/RichMedia', '/XFA'}

        def visit(obj):
            budget[0] -= 1
            if budget[0] <= 0:
                raise ValueError('Complex document')
            if isinstance(obj, IndirectObject):
                ident = (obj.idnum, obj.generation)
                if ident in seen:
                    return
                seen.add(ident)
                obj = obj.get_object()
            if isinstance(obj, DictionaryObject):
                action = obj.get('/OpenAction')
                if action is not None:
                    action = action.get_object() if isinstance(action, IndirectObject) else action
                    if isinstance(action, DictionaryObject):
                        if action.get('/S') != '/GoTo' or '/D' not in action or '/Next' in action:
                            raise ValueError('Unsafe document open action')
                    elif not isinstance(action, ArrayObject):
                        raise ValueError('Unsupported document open action')
                if any(str(k) in forbidden or str(v) in forbidden for k, v in obj.items()):
                    raise ValueError('Active PDF content')
                for value in obj.values():
                    visit(value)
            elif isinstance(obj, (ArrayObject, list)):
                for value in obj:
                    visit(value)
        visit(reader.trailer)
        return len(reader.pages)
    except Exception:
        raise APIError(415, 'INVALID_PDF', 'Use an unencrypted PDF with 1–20 pages and no scripts, attachments or launch actions.')


def upload_bytes(db, data, filename, owner=None):
    if not data:
        raise APIError(415, 'EMPTY_FILE', 'The selected file is empty.')
    if data.startswith(b'%PDF-'):
        pages = validate_pdf(data)
        key = LocalStorage().write_private(data)
        fields = {'kind': 'pdf', 'verified_mime': 'application/pdf', 'sanitized_source_key': key, 'variants': {'document': {'key': key, 'mime': 'application/pdf', 'width': None, 'height': None, 'byte_size': len(data), 'sha256': checksum(data)}}, 'source_width': None, 'source_height': None, 'page_count': pages, 'byte_size': len(data), 'sha256': checksum(data)}
    else:
        fields = _image_bytes(decode_image(data))
    name = ''.join(c for c in Path(filename or 'upload').name if c.isprintable())[:180] or 'upload'
    asset = MediaAsset(**fields, original_display_name=name, created_by=owner.id if owner else None)
    try:
        db.add(asset)
        db.commit()
    except Exception:
        db.rollback()
        for key in keys_for(asset):
            LocalStorage().delete(key)
        raise
    return asset


def asset_usage(db, asset_id):
    result = []
    draft = db.get(SiteDraft, 1)
    if draft and asset_id in typed_references(SiteContent.model_validate(draft.content)):
        result.append({'type': 'draft', 'revision': draft.revision})
    for release in db.scalars(select(SiteRelease)):
        if asset_id in typed_references(SiteContent.model_validate(release.source_content)):
            result.append({'type': 'release', 'id': str(release.id), 'revision': release.revision})
    for child in db.scalars(select(MediaAsset).where(MediaAsset.parent_asset_id == asset_id, MediaAsset.status != 'deleted')):
        result.append({'type': 'derived_asset', 'id': str(child.id)})
    return result


def asset_metadata(db, asset, include_usage=True):
    variants = media_variants(asset, preview=True)
    return {'id': str(asset.id), 'kind': asset.kind, 'status': asset.status, 'verified_mime': asset.verified_mime, 'original_display_name': asset.original_display_name, 'created_at': asset.created_at, 'source_width': asset.source_width, 'source_height': asset.source_height, 'page_count': asset.page_count, 'byte_size': asset.byte_size, 'parent_asset_id': str(asset.parent_asset_id) if asset.parent_asset_id else None, 'crop': asset.crop, 'variants': variants, 'url': (variants.get('full') or variants.get('document') or {}) .get('url'), 'usage': asset_usage(db, asset.id) if include_usage else [], 'quality_warning': 'Small image; displayed without upscaling.' if asset.kind == 'image' and min(asset.source_width, asset.source_height) < 400 else None}


def crop_asset(db, asset_id, crop, owner):
    parent = db.get(MediaAsset, asset_id)
    if not parent or parent.status != 'ready' or parent.kind != 'image':
        raise APIError(404, 'MEDIA_NOT_FOUND', 'Image not found.')
    source_key, sw, sh = parent.sanitized_source_key, parent.source_width, parent.source_height
    display_name = parent.original_display_name
    db.rollback()  # No open DB transaction during image processing.
    pw, ph = crop.width * sw, crop.height * sh
    if abs(pw * 5 - ph * 4) > 5:
        raise APIError(422, 'INVALID_CROP_RATIO', 'Portrait crops must have a 4:5 ratio in source pixels (one-pixel rounding tolerance).')
    try:
        image = Image.open(io.BytesIO(LocalStorage().read_private(source_key)))
        box = (round(crop.x * sw), round(crop.y * sh), round((crop.x + crop.width) * sw), round((crop.y + crop.height) * sh))
        cropped = image.crop(box)
        units = min(cropped.width // 4, cropped.height // 5)
        if units < 1:
            raise APIError(422, 'CROP_TOO_SMALL', 'Choose a crop at least 4 by 5 pixels.')
        cropped = cropped.resize((units * 4, units * 5), Image.Resampling.LANCZOS)
        fields = _image_bytes(cropped)
    except FileNotFoundError:
        raise APIError(503, 'MEDIA_UNAVAILABLE', 'Stored image is temporarily unavailable.')
    child = MediaAsset(**fields, original_display_name=display_name, parent_asset_id=asset_id, crop=crop.model_dump(), created_by=owner.id)
    try:
        lock_draft(db)
        parent = db.scalar(select(MediaAsset).where(MediaAsset.id == asset_id).with_for_update())
        if not parent or parent.status != 'ready':
            raise APIError(409, 'MEDIA_CHANGED', 'The source image changed; select it again.')
        db.add(child)
        db.commit()
        return child
    except Exception:
        db.rollback()
        for key in keys_for(child):
            LocalStorage().delete(key)
        raise


def delete_asset(db, asset_id, owner, request=None):
    lock_draft(db)
    asset = db.scalar(select(MediaAsset).where(MediaAsset.id == asset_id).with_for_update())
    if not asset or asset.status == 'deleted':
        raise APIError(404, 'MEDIA_NOT_FOUND', 'Media not found.')
    usage = asset_usage(db, asset_id)
    if usage:
        raise APIError(409, 'MEDIA_IN_USE', 'This asset is required by a draft, retained release or derived image.', {'usage': usage})
    asset.status = 'deleted'
    asset.deleted_at = now()
    audit(db, 'media_delete', owner.id, 'media', asset.id, request)
    db.commit()
    for key in keys_for(asset):
        try:
            LocalStorage().delete(key)
        except OSError:
            logger.warning('media_deletion_pending', extra={'asset_id': str(asset.id)})
