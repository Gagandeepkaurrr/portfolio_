import uuid
from datetime import datetime
from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Index, Integer, Sequence, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base, now

U = UUID(as_uuid=True)
T = TIMESTAMP(timezone=True)


class AdminUser(Base):
    __tablename__ = 'admin_users'
    id: Mapped[uuid.UUID] = mapped_column(U, primary_key=True, default=uuid.uuid4)
    normalized_email: Mapped[str] = mapped_column(Text, unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(T, default=now)
    updated_at: Mapped[datetime] = mapped_column(T, default=now)
    password_changed_at: Mapped[datetime] = mapped_column(T, default=now)


class AdminSession(Base):
    __tablename__ = 'admin_sessions'
    id: Mapped[uuid.UUID] = mapped_column(U, primary_key=True, default=uuid.uuid4)
    admin_user_id: Mapped[uuid.UUID] = mapped_column(U, ForeignKey('admin_users.id'))
    token_digest: Mapped[str] = mapped_column(Text, unique=True)
    csrf_token_digest: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(T, default=now)
    expires_at: Mapped[datetime] = mapped_column(T, index=True)
    last_activity_at: Mapped[datetime] = mapped_column(T, default=now)
    revoked_at: Mapped[datetime | None] = mapped_column(T)


class SiteDraft(Base):
    __tablename__ = 'site_drafts'
    __table_args__ = (CheckConstraint('id = 1'), CheckConstraint('revision > 0'))
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, default=1)
    schema_version: Mapped[int] = mapped_column(Integer, default=1)
    content: Mapped[dict] = mapped_column(JSONB)
    revision: Mapped[int] = mapped_column(BigInteger, default=1)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(U, ForeignKey('admin_users.id'))
    updated_at: Mapped[datetime] = mapped_column(T, default=now)


release_sequence = Sequence('site_release_revision_seq', start=1)


class SiteRelease(Base):
    __tablename__ = 'site_releases'
    id: Mapped[uuid.UUID] = mapped_column(U, primary_key=True, default=uuid.uuid4)
    revision: Mapped[int] = mapped_column(BigInteger, release_sequence, server_default=release_sequence.next_value(), unique=True)
    schema_version: Mapped[int] = mapped_column(Integer, default=1)
    source_content: Mapped[dict] = mapped_column(JSONB)
    public_content: Mapped[dict] = mapped_column(JSONB)
    public_asset_ids: Mapped[list] = mapped_column(JSONB, default=list)
    resume_asset_id: Mapped[uuid.UUID | None] = mapped_column(U, ForeignKey('media_assets.id'))
    content_hash: Mapped[str] = mapped_column(Text)
    source_draft_revision: Mapped[int] = mapped_column(BigInteger)
    publish_idempotency_key: Mapped[uuid.UUID] = mapped_column(U, unique=True)
    publish_request_hash: Mapped[str] = mapped_column(Text)
    created_by: Mapped[uuid.UUID | None] = mapped_column(U, ForeignKey('admin_users.id'))
    created_at: Mapped[datetime] = mapped_column(T, default=now, index=True)


class SiteState(Base):
    __tablename__ = 'site_state'
    __table_args__ = (CheckConstraint('id = 1'),)
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, default=1)
    live_release_id: Mapped[uuid.UUID | None] = mapped_column(U, ForeignKey('site_releases.id', ondelete='RESTRICT'))
    updated_at: Mapped[datetime] = mapped_column(T, default=now)


class MediaAsset(Base):
    __tablename__ = 'media_assets'
    __table_args__ = (CheckConstraint("kind IN ('image','pdf')"), CheckConstraint("status IN ('processing','ready','deleted','failed')"))
    id: Mapped[uuid.UUID] = mapped_column(U, primary_key=True, default=uuid.uuid4)
    kind: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20), default='ready')
    verified_mime: Mapped[str] = mapped_column(Text)
    sanitized_source_key: Mapped[str] = mapped_column(Text)
    variants: Mapped[dict] = mapped_column(JSONB)
    source_width: Mapped[int | None] = mapped_column(Integer)
    source_height: Mapped[int | None] = mapped_column(Integer)
    page_count: Mapped[int | None] = mapped_column(Integer)
    byte_size: Mapped[int] = mapped_column(BigInteger)
    sha256: Mapped[str] = mapped_column(Text)
    original_display_name: Mapped[str] = mapped_column(Text)
    parent_asset_id: Mapped[uuid.UUID | None] = mapped_column(U, ForeignKey('media_assets.id', ondelete='RESTRICT'))
    crop: Mapped[dict | None] = mapped_column(JSONB)
    created_by: Mapped[uuid.UUID | None] = mapped_column(U, ForeignKey('admin_users.id'))
    created_at: Mapped[datetime] = mapped_column(T, default=now, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(T)


class ContactSubmission(Base):
    __tablename__ = 'contact_submissions'
    id: Mapped[uuid.UUID] = mapped_column(U, primary_key=True, default=uuid.uuid4)
    idempotency_key: Mapped[uuid.UUID] = mapped_column(U, unique=True)
    request_hash: Mapped[str] = mapped_column(Text)
    name: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text)
    subject: Mapped[str | None] = mapped_column(Text)
    message: Mapped[str | None] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_status: Mapped[str] = mapped_column(String(20), default='not_configured')
    created_at: Mapped[datetime] = mapped_column(T, default=now)
    updated_at: Mapped[datetime] = mapped_column(T, default=now)
    deleted_at: Mapped[datetime | None] = mapped_column(T)
    receipt_expires_at: Mapped[datetime] = mapped_column(T)
    notification_attempted_at: Mapped[datetime | None] = mapped_column(T)
    notification_error_code: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (Index('ix_contact_inbox', 'is_archived', 'is_read', 'created_at'),)


class RateLimitBucket(Base):
    __tablename__ = 'rate_limit_buckets'
    scope: Mapped[str] = mapped_column(Text, primary_key=True)
    key_digest: Mapped[str] = mapped_column(Text, primary_key=True)
    window_start: Mapped[datetime] = mapped_column(T, primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime] = mapped_column(T, index=True)
    __table_args__ = (CheckConstraint('count >= 0'),)


class SlugRedirect(Base):
    __tablename__ = 'slug_redirects'
    old_slug: Mapped[str] = mapped_column(String(80), primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(U)
    created_release_id: Mapped[uuid.UUID] = mapped_column(U, ForeignKey('site_releases.id'))


class AuditEvent(Base):
    __tablename__ = 'admin_audit_events'
    id: Mapped[uuid.UUID] = mapped_column(U, primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(U, ForeignKey('admin_users.id'))
    operation: Mapped[str] = mapped_column(Text)
    target_type: Mapped[str | None] = mapped_column(Text)
    target_id: Mapped[str | None] = mapped_column(Text)
    request_id: Mapped[uuid.UUID] = mapped_column(U, default=uuid.uuid4)
    safe_metadata: Mapped[dict] = mapped_column('metadata', JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(T, default=now)
