import base64
import json
from datetime import datetime
from uuid import UUID
from sqlalchemy import and_, or_
from app.errors import APIError


def paginate(db, query, model, cursor, limit):
    if cursor:
        try:
            if len(cursor) > 300:
                raise ValueError()
            stamp, identifier = json.loads(base64.urlsafe_b64decode(cursor + '=' * (-len(cursor) % 4)))
            timestamp = datetime.fromisoformat(stamp)
            if timestamp.tzinfo is None:
                raise ValueError()
            identifier = UUID(identifier)
        except Exception:
            raise APIError(400, 'INVALID_CURSOR', 'This page cursor is invalid.')
        query = query.where(or_(model.created_at < timestamp, and_(model.created_at == timestamp, model.id < identifier)))
    items = list(db.scalars(query.order_by(model.created_at.desc(), model.id.desc()).limit(limit + 1)))
    more = len(items) > limit
    items = items[:limit]
    next_cursor = None
    if more and items:
        last = items[-1]
        next_cursor = base64.urlsafe_b64encode(json.dumps([last.created_at.isoformat(), str(last.id)]).encode()).decode().rstrip('=')
    return items, {'next_cursor': next_cursor, 'has_more': more}
