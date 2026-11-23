from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.db import get_db, now
from app.errors import APIError
from app.models import AdminSession, AdminUser
from app.schemas import LoginRequest, PasswordChange, SessionEnvelope
from app.security.auth import DUMMY_HASH, audit, csrf_for, digest, enforce_buckets, hash_password, locked_buckets, new_session, owner_session, require_json, require_origin, set_cookie, source_identifier, verify_password
from app.config import get_settings

router = APIRouter(prefix='/admin/auth', tags=['owner-auth'])


def envelope(owner, session, csrf):
    return {'owner': {'id': str(owner.id), 'email': owner.normalized_email}, 'csrf_token': csrf, 'expires_at': session.expires_at}


@router.post('/login', response_model=SessionEnvelope)
def login(body: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    require_origin(request)
    require_json(request)
    email = str(body.email).lower()
    source = source_identifier(request)
    buckets = locked_buckets(db, [('login-ip', source, 900, 30), ('login-pair', digest(source + email), 900, 5)])
    enforce_buckets(buckets)
    owner = db.scalar(select(AdminUser).where(AdminUser.normalized_email == email))
    valid = verify_password(owner.password_hash if owner else DUMMY_HASH, body.password)
    if not owner or not owner.is_active or not valid:
        for bucket, _, _ in buckets:
            bucket.count += 1
        audit(db, 'login_failed', request=request)
        db.commit()
        raise APIError(401, 'INVALID_CREDENTIALS', 'Email or password is incorrect.')
    for bucket, _, _ in buckets:
        if bucket.scope == 'login-pair':
            bucket.count = 0
    previous_token = request.cookies.get(get_settings().cookie_name)
    if previous_token:
        db.execute(update(AdminSession).where(AdminSession.token_digest == digest(previous_token), AdminSession.admin_user_id == owner.id).values(revoked_at=now()))
    session, token, csrf = new_session(db, owner)
    audit(db, 'login', actor=owner.id, request=request)
    db.commit()
    set_cookie(response, token)
    return envelope(owner, session, csrf)


@router.get('/session', response_model=SessionEnvelope)
def session_info(auth=Depends(owner_session)):
    owner, session, token = auth
    return envelope(owner, session, csrf_for(token))


@router.post('/logout', status_code=204)
def logout(response: Response, db: Session = Depends(get_db), auth=Depends(owner_session)):
    _, session, _ = auth
    session.revoked_at = now()
    db.commit()
    response.delete_cookie(get_settings().cookie_name, path='/', secure=get_settings().app_env == 'production', httponly=True, samesite='lax')


@router.post('/change-password', response_model=SessionEnvelope)
def change_password(body: PasswordChange, request: Request, response: Response, db: Session = Depends(get_db), auth=Depends(owner_session)):
    require_json(request)
    owner, _, _ = auth
    if not verify_password(owner.password_hash, body.current_password):
        raise APIError(400, 'INVALID_PASSWORD', 'The current password is incorrect.')
    owner.password_hash = hash_password(body.new_password)
    owner.password_changed_at = now()
    owner.updated_at = now()
    db.execute(update(AdminSession).where(AdminSession.admin_user_id == owner.id).values(revoked_at=now()))
    session, token, csrf = new_session(db, owner)
    audit(db, 'password_change', actor=owner.id, request=request)
    db.commit()
    set_cookie(response, token)
    return envelope(owner, session, csrf)
