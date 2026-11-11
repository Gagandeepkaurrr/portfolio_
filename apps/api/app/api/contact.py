from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, Header, Query, Request, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.db import get_db, now
from app.errors import APIError
from app.models import ContactSubmission
from app.pagination import paginate
from app.schemas import ContactRequest, ContactStatus, ContactReceipt, ContactPage, ContactDetail
from app.security.auth import audit, owner_session, require_json, require_origin
from app.services.contact import notify_contact, receive_contact, scrub

router = APIRouter(tags=['contact'])


def dto(contact, detail=False):
    value = {'id': str(contact.id), 'name': contact.name, 'email': contact.email, 'subject': contact.subject, 'excerpt': (contact.message or '')[:160], 'created_at': contact.created_at, 'is_read': contact.is_read, 'is_archived': contact.is_archived, 'notification_status': contact.notification_status}
    if detail:
        value['message'] = contact.message
    return value


def active_contact(db, identifier, lock=False):
    query = select(ContactSubmission).where(ContactSubmission.id == identifier, ContactSubmission.deleted_at.is_(None))
    if lock:
        query = query.with_for_update()
    contact = db.scalar(query)
    if not contact:
        raise APIError(404, 'CONTACT_NOT_FOUND', 'Message not found.')
    return contact


@router.post('/contact', response_model=ContactReceipt)
def send_message(body: ContactRequest, request: Request, response: Response, background_tasks: BackgroundTasks, idempotency_key: UUID = Header(...), db: Session = Depends(get_db)):
    require_origin(request)
    require_json(request)
    contact, created = receive_contact(db, body, idempotency_key, request)
    response.status_code = 201 if created else 200
    if created and contact.notification_status == 'pending':
        background_tasks.add_task(notify_contact, contact.id)
    return {'receipt_id': str(contact.id), 'status': 'received'}


@router.get('/admin/contact', response_model=ContactPage)
def inbox(status: str = 'all', cursor: str | None = None, limit: int = Query(default=30, ge=1, le=100), db: Session = Depends(get_db), auth=Depends(owner_session)):
    query = select(ContactSubmission).where(ContactSubmission.deleted_at.is_(None))
    if status == 'unread':
        query = query.where(ContactSubmission.is_read.is_(False), ContactSubmission.is_archived.is_(False))
    elif status == 'archived':
        query = query.where(ContactSubmission.is_archived.is_(True))
    elif status == 'all':
        query = query.where(ContactSubmission.is_archived.is_(False))
    else:
        raise APIError(400, 'INVALID_FILTER', 'Choose all, unread or archived.')
    items, pagination = paginate(db, query, ContactSubmission, cursor, limit)
    unread = db.scalar(select(func.count()).select_from(ContactSubmission).where(ContactSubmission.deleted_at.is_(None), ContactSubmission.is_read.is_(False), ContactSubmission.is_archived.is_(False)))
    return {'items': [dto(item) for item in items], 'unread_count': unread, **pagination}


@router.get('/admin/contact/{contact_id}', response_model=ContactDetail)
def detail(contact_id: UUID, db: Session = Depends(get_db), auth=Depends(owner_session)):
    return dto(active_contact(db, contact_id), detail=True)


@router.patch('/admin/contact/{contact_id}/status', response_model=ContactDetail)
def update_status(contact_id: UUID, body: ContactStatus, request: Request, db: Session = Depends(get_db), auth=Depends(owner_session)):
    require_json(request)
    contact = active_contact(db, contact_id, lock=True)
    for key, value in body.model_dump(exclude_none=True).items():
        setattr(contact, key, value)
    contact.updated_at = now()
    db.commit()
    return dto(contact, detail=True)


@router.delete('/admin/contact/{contact_id}', status_code=204)
def delete(contact_id: UUID, request: Request, db: Session = Depends(get_db), auth=Depends(owner_session)):
    contact = active_contact(db, contact_id, lock=True)
    scrub(contact)
    audit(db, 'contact_delete', auth[0].id, 'contact', contact_id, request)
    db.commit()
