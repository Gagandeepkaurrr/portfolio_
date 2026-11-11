"""Initial portfolio schema"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute('CREATE SEQUENCE site_release_revision_seq START 1')
    op.create_table('admin_users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('normalized_email', sa.Text(), nullable=False),
    sa.Column('password_hash', sa.Text(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('password_changed_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('normalized_email')
    )
    op.create_table('contact_submissions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('idempotency_key', sa.UUID(), nullable=False),
    sa.Column('request_hash', sa.Text(), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('email', sa.Text(), nullable=True),
    sa.Column('subject', sa.Text(), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('is_archived', sa.Boolean(), nullable=False),
    sa.Column('notification_status', sa.String(length=20), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('receipt_expires_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('notification_attempted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('notification_error_code', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('idempotency_key')
    )
    op.create_index('ix_contact_inbox', 'contact_submissions', ['is_archived', 'is_read', 'created_at'], unique=False)
    op.create_table('rate_limit_buckets',
    sa.Column('scope', sa.Text(), nullable=False),
    sa.Column('key_digest', sa.Text(), nullable=False),
    sa.Column('window_start', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.Column('expires_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.CheckConstraint('count >= 0'),
    sa.PrimaryKeyConstraint('scope', 'key_digest', 'window_start')
    )
    op.create_index(op.f('ix_rate_limit_buckets_expires_at'), 'rate_limit_buckets', ['expires_at'], unique=False)
    op.create_table('admin_audit_events',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('actor_id', sa.UUID(), nullable=True),
    sa.Column('operation', sa.Text(), nullable=False),
    sa.Column('target_type', sa.Text(), nullable=True),
    sa.Column('target_id', sa.Text(), nullable=True),
    sa.Column('request_id', sa.UUID(), nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['actor_id'], ['admin_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('admin_sessions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('admin_user_id', sa.UUID(), nullable=False),
    sa.Column('token_digest', sa.Text(), nullable=False),
    sa.Column('csrf_token_digest', sa.Text(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('expires_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('last_activity_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('revoked_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token_digest')
    )
    op.create_index(op.f('ix_admin_sessions_expires_at'), 'admin_sessions', ['expires_at'], unique=False)
    op.create_table('media_assets',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('kind', sa.String(length=10), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('verified_mime', sa.Text(), nullable=False),
    sa.Column('sanitized_source_key', sa.Text(), nullable=False),
    sa.Column('variants', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('source_width', sa.Integer(), nullable=True),
    sa.Column('source_height', sa.Integer(), nullable=True),
    sa.Column('page_count', sa.Integer(), nullable=True),
    sa.Column('byte_size', sa.BigInteger(), nullable=False),
    sa.Column('sha256', sa.Text(), nullable=False),
    sa.Column('original_display_name', sa.Text(), nullable=False),
    sa.Column('parent_asset_id', sa.UUID(), nullable=True),
    sa.Column('crop', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
    sa.CheckConstraint("kind IN ('image','pdf')"),
    sa.CheckConstraint("status IN ('processing','ready','deleted','failed')"),
    sa.ForeignKeyConstraint(['created_by'], ['admin_users.id'], ),
    sa.ForeignKeyConstraint(['parent_asset_id'], ['media_assets.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_media_assets_created_at'), 'media_assets', ['created_at'], unique=False)
    op.create_table('site_drafts',
    sa.Column('id', sa.SmallInteger(), nullable=False),
    sa.Column('schema_version', sa.Integer(), nullable=False),
    sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('revision', sa.BigInteger(), nullable=False),
    sa.Column('updated_by', sa.UUID(), nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.CheckConstraint('id = 1'),
    sa.CheckConstraint('revision > 0'),
    sa.ForeignKeyConstraint(['updated_by'], ['admin_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('site_releases',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('revision', sa.BigInteger(), server_default=sa.text("nextval('site_release_revision_seq')"), nullable=False),
    sa.Column('schema_version', sa.Integer(), nullable=False),
    sa.Column('source_content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('public_content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('public_asset_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('resume_asset_id', sa.UUID(), nullable=True),
    sa.Column('content_hash', sa.Text(), nullable=False),
    sa.Column('source_draft_revision', sa.BigInteger(), nullable=False),
    sa.Column('publish_idempotency_key', sa.UUID(), nullable=False),
    sa.Column('publish_request_hash', sa.Text(), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['admin_users.id'], ),
    sa.ForeignKeyConstraint(['resume_asset_id'], ['media_assets.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('publish_idempotency_key'),
    sa.UniqueConstraint('revision')
    )
    op.create_index(op.f('ix_site_releases_created_at'), 'site_releases', ['created_at'], unique=False)
    op.create_table('site_state',
    sa.Column('id', sa.SmallInteger(), nullable=False),
    sa.Column('live_release_id', sa.UUID(), nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.CheckConstraint('id = 1'),
    sa.ForeignKeyConstraint(['live_release_id'], ['site_releases.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('slug_redirects',
    sa.Column('old_slug', sa.String(length=80), nullable=False),
    sa.Column('project_id', sa.UUID(), nullable=False),
    sa.Column('created_release_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['created_release_id'], ['site_releases.id'], ),
    sa.PrimaryKeyConstraint('old_slug')
    )

def downgrade():
    op.drop_table('slug_redirects')
    op.drop_table('site_state')
    op.drop_index(op.f('ix_site_releases_created_at'), table_name='site_releases')
    op.drop_table('site_releases')
    op.drop_table('site_drafts')
    op.drop_index(op.f('ix_media_assets_created_at'), table_name='media_assets')
    op.drop_table('media_assets')
    op.drop_index(op.f('ix_admin_sessions_expires_at'), table_name='admin_sessions')
    op.drop_table('admin_sessions')
    op.drop_table('admin_audit_events')
    op.drop_index(op.f('ix_rate_limit_buckets_expires_at'), table_name='rate_limit_buckets')
    op.drop_table('rate_limit_buckets')
    op.drop_index('ix_contact_inbox', table_name='contact_submissions')
    op.drop_table('contact_submissions')
    op.drop_table('admin_users')
    op.execute('DROP SEQUENCE site_release_revision_seq')
