import smtplib
from datetime import timedelta
from email.message import EmailMessage
from sqlalchemy import select
from app.config import get_settings
from app.db import now, session_factory
from app.errors import APIError
from app.models import ContactSubmission
from app.security.auth import enforce_buckets, locked_buckets, source_identifier
from app.services.content import canonical_hash


def receive_contact(db, body, key, request):
    if body.website:
        raise APIError(400, 'MESSAGE_REJECTED', 'Your message could not be accepted. Please email directly.')
    payload = body.model_dump(mode='json', exclude={'website'})
    request_hash = canonical_hash(payload)
    config = get_settings()
    # The shared global bucket serializes receipt lookup, insert and counter charge across workers.
    buckets = locked_buckets(db, [('contact-global', 'site', 3600, config.contact_site_limit), ('contact-source', source_identifier(request), 900, config.contact_ip_limit)])
    existing = db.scalar(select(ContactSubmission).where(ContactSubmission.idempotency_key == key))
    if existing:
        if existing.request_hash != request_hash:
            raise APIError(409, 'IDEMPOTENCY_CONFLICT', 'This submission key was already used for a different message.')
        return existing, False
    enforce_buckets(buckets)
    configured = bool(config.smtp_host and config.smtp_from and config.contact_notify_to)
    contact = ContactSubmission(**payload, idempotency_key=key, request_hash=request_hash, receipt_expires_at=now() + timedelta(days=config.contact_retention_days, hours=24), notification_status='pending' if configured else 'not_configured')
    db.add(contact)
    for bucket, _, _ in buckets:
        bucket.count += 1
    db.commit()
    return contact, True


def notify_contact(contact_id):
    """Best effort after commit; one claimed attempt, never an automatic retry loop."""
    config = get_settings()
    if not config.smtp_host:
        return
    with session_factory()() as db:
        contact = db.scalar(select(ContactSubmission).where(ContactSubmission.id == contact_id).with_for_update())
        if not contact or contact.deleted_at or contact.notification_status != 'pending':
            return
        contact.notification_status = 'processing'
        contact.notification_attempted_at = now()
        sender_email, subject, name, message = contact.email, contact.subject, contact.name, contact.message
        db.commit()
        try:
            mail = EmailMessage()
            mail['From'] = config.smtp_from
            mail['To'] = config.contact_notify_to
            mail['Reply-To'] = sender_email
            mail['Subject'] = 'Portfolio inquiry' + (': ' + subject if subject else '')
            mail.set_content(f'New inquiry from {name}\n\n{message}')
            with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=10) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                if config.smtp_user:
                    smtp.login(config.smtp_user, config.smtp_password or '')
                smtp.send_message(mail)
            contact.notification_status = 'sent'
        except Exception:
            contact.notification_status = 'failed'
            contact.notification_error_code = 'SMTP_DELIVERY_FAILED'
        db.commit()


def scrub(contact):
    contact.name = None
    contact.email = None
    contact.subject = None
    contact.message = None
    contact.deleted_at = now()
    contact.updated_at = now()
    contact.receipt_expires_at = now() + timedelta(hours=24)
