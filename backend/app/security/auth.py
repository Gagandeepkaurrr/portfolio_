import hashlib
import hmac
import ipaddress
import secrets
from datetime import timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from fastapi import Depends, Request
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.config import get_settings
from app.db import get_db, now
from app.errors import APIError
from app.models import AdminSession, AdminUser, AuditEvent, RateLimitBucket

password_hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)
DUMMY_HASH = password_hasher.hash(secrets.token_urlsafe(32))


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def hash_password(value: str) -> str:
    if not 12 <= len(value) <= 256:
        raise ValueError('Password must contain 12 to 256 characters')
    return password_hasher.hash(value)


def verify_password(encoded: str, value: str) -> bool:
    try:
        return password_hasher.verify(encoded, value)
    except VerificationError:
        return False


def csrf_for(token: str) -> str:
    return hmac.new(get_settings().csrf_secret.encode(), b'portfolio-csrf-v1\x00' + token.encode(), hashlib.sha256).hexdigest()


def audit(db, operation, actor=None, target_type=None, target_id=None, request=None, metadata=None):
    db.add(AuditEvent(actor_id=actor, operation=operation, target_type=target_type, target_id=str(target_id) if target_id else None, request_id=getattr(request.state, 'request_id', None) if request else None, safe_metadata=metadata or {}))


def require_origin(request: Request):
    if request.headers.get('origin') != get_settings().public_origin:
        raise APIError(403, 'ORIGIN_REJECTED', 'This request must come from the portfolio origin.')


def require_json(request: Request):
    if request.headers.get('content-type', '').split(';')[0].strip().lower() != 'application/json':
        raise APIError(415, 'JSON_REQUIRED', 'Send application/json.')


def source_identifier(request: Request) -> str:
    source = request.client.host if request.client else 'unknown'
    config = get_settings()
    networks = [ipaddress.ip_network(v.strip()) for v in config.trusted_proxy_cidrs.split(',') if v.strip()]
    try:
        peer = ipaddress.ip_address(source)
        if networks and any(peer in n for n in networks):
            chain = [v.strip() for v in request.headers.get('x-forwarded-for', '').split(',') if v.strip()]
            for candidate in reversed(chain):
                peer = ipaddress.ip_address(candidate)
                source = str(peer)
                if not any(peer in n for n in networks):
                    break
    except ValueError:
        pass
    return hmac.new(config.abuse_hmac_secret.encode(), source.encode(), hashlib.sha256).hexdigest()


def locked_buckets(db: Session, specs):
    """Lock by deterministic scope/key before inserting: works across API workers."""
    buckets = []
    for scope, key, seconds, limit in sorted(specs):
        lock_key = int.from_bytes(hashlib.sha256(f'{scope}:{key}'.encode()).digest()[:8], 'big', signed=True)
        db.execute(text('SELECT pg_advisory_xact_lock(:key)'), {'key': lock_key})
        current = now()
        start = current.fromtimestamp(int(current.timestamp()) // seconds * seconds, current.tzinfo)
        bucket = db.get(RateLimitBucket, (scope, key, start))
        if bucket is None:
            bucket = RateLimitBucket(scope=scope, key_digest=key, window_start=start, count=0, expires_at=start + timedelta(seconds=seconds * 2))
            db.add(bucket)
            db.flush()
        buckets.append((bucket, limit, max(1, int((start + timedelta(seconds=seconds) - current).total_seconds()))))
    return buckets


def enforce_buckets(buckets):
    for bucket, limit, retry_after in buckets:
        if bucket.count >= limit:
            raise APIError(429, 'RATE_LIMITED', 'Too many requests. Please try again later.', headers={'Retry-After': str(retry_after)})


def new_session(db: Session, owner: AdminUser):
    token = secrets.token_urlsafe(48)
    csrf = csrf_for(token)
    session = AdminSession(admin_user_id=owner.id, token_digest=digest(token), csrf_token_digest=digest(csrf), expires_at=now() + timedelta(seconds=get_settings().session_absolute_seconds), last_activity_at=now())
    db.add(session)
    db.flush()
    return session, token, csrf


def set_cookie(response, token):
    config = get_settings()
    response.set_cookie(config.cookie_name, token, secure=config.app_env == 'production', httponly=True, samesite='lax', path='/', max_age=config.session_absolute_seconds)


def owner_session(request: Request, db: Session = Depends(get_db)):
    config = get_settings()
    token = request.cookies.get(config.cookie_name)
    if not token or len(token) > 200:
        raise APIError(401, 'AUTH_REQUIRED', 'Please sign in to continue.')
    row = db.execute(select(AdminSession, AdminUser).join(AdminUser, AdminSession.admin_user_id == AdminUser.id).where(AdminSession.token_digest == digest(token))).first()
    if not row:
        raise APIError(401, 'AUTH_REQUIRED', 'Please sign in to continue.')
    session, owner = row
    current = now()
    if session.revoked_at or not owner.is_active or session.expires_at <= current or session.last_activity_at + timedelta(seconds=config.session_idle_seconds) <= current:
        raise APIError(401, 'AUTH_REQUIRED', 'Your session expired. Sign in again.')
    if request.method not in ('GET', 'HEAD', 'OPTIONS'):
        require_origin(request)
        submitted = request.headers.get('x-csrf-token', '')
        if not hmac.compare_digest(digest(submitted), session.csrf_token_digest):
            raise APIError(403, 'CSRF_REJECTED', 'Refresh your session before trying again.')
    session.last_activity_at = current
    db.commit()
    return owner, session, token
