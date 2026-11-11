import json
import logging
import time
from uuid import uuid4
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException
from app.api import auth, contact, content, media
from app.config import get_settings
from app.db import get_db
from app.errors import APIError
from app.storage.local import LocalStorage

logger = logging.getLogger('portfolio')
config = get_settings()
app = FastAPI(title='Gagandeep Kaur Portfolio API', version='1.0.0', docs_url='/api/v1/docs' if config.app_env != 'production' else None, openapi_url='/api/v1/openapi.json' if config.app_env != 'production' else None, redoc_url=None)


def error_response(request, status, code, message, details=None, headers=None):
    return JSONResponse(status_code=status, content={'error': {'code': code, 'message': message, 'details': details or {}}, 'request_id': str(getattr(request.state, 'request_id', uuid4()))}, headers=headers)


@app.exception_handler(APIError)
async def api_error(request: Request, error: APIError):
    return error_response(request, error.status, error.code, error.message, error.details, error.headers)


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, error: RequestValidationError):
    fields = [{'path': '.'.join(map(str, e['loc'][1:])), 'message': e['msg']} for e in error.errors()[:30]]
    return error_response(request, 422, 'VALIDATION_ERROR', 'Check the highlighted fields.', {'field_errors': fields})


@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, error: SQLAlchemyError):
    logger.error('database_operation_failed request_id=%s error_type=%s', request.state.request_id, type(error).__name__)
    return error_response(request, 503, 'SERVICE_UNAVAILABLE', 'The service is temporarily unavailable. Please try again.')


@app.exception_handler(HTTPException)
async def http_error(request: Request, error: HTTPException):
    return error_response(request, error.status_code, 'NOT_FOUND' if error.status_code == 404 else 'REQUEST_FAILED', 'Resource not found.' if error.status_code == 404 else 'The request could not be completed.')


@app.exception_handler(Exception)
async def unexpected_error(request: Request, error: Exception):
    logger.error('unexpected_error request_id=%s error_type=%s', getattr(request.state, 'request_id', 'unknown'), type(error).__name__)
    return error_response(request, 500, 'INTERNAL_ERROR', 'The request could not be completed. Please try again.')


class RequestBoundary:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        request_id = str(uuid4())
        scope.setdefault('state', {})['request_id'] = request_id
        started = time.monotonic()
        status = [500]
        async def wrapped_send(message):
            if message['type'] == 'http.response.start':
                status[0] = message['status']
                headers = list(message.get('headers', []))
                headers += [(b'x-request-id', request_id.encode()), (b'cache-control', b'no-store'), (b'x-content-type-options', b'nosniff'), (b'referrer-policy', b'strict-origin-when-cross-origin')]
                if '/admin' in scope['path']:
                    headers.append((b'x-robots-tag', b'noindex, nofollow'))
                message['headers'] = headers
            await send(message)
        async def reject(code, name, message):
            payload = json.dumps({'error': {'code': name, 'message': message, 'details': {}}, 'request_id': request_id}).encode()
            await wrapped_send({'type': 'http.response.start', 'status': code, 'headers': [(b'content-type', b'application/json')]})
            await wrapped_send({'type': 'http.response.body', 'body': payload})
        if scope['method'] not in ('GET', 'HEAD', 'OPTIONS'):
            headers = dict(scope['headers'])
            if headers.get(b'origin', b'').decode(errors='replace') != config.public_origin:
                return await reject(403, 'ORIGIN_REJECTED', 'This request must come from the portfolio origin.')
            limit = 16 * 1024 if scope['path'] == '/api/v1/contact' else (11 * 1024 * 1024 if scope['path'] == '/api/v1/admin/media' else 256 * 1024)
            body = bytearray()
            while True:
                message = await receive()
                if message['type'] == 'http.disconnect':
                    return
                body.extend(message.get('body', b''))
                if len(body) > limit:
                    return await reject(413, 'BODY_TOO_LARGE', 'The request exceeds the allowed size.')
                if not message.get('more_body'):
                    break
            if body and scope['path'] != '/api/v1/admin/media' and headers.get(b'content-type', b'').split(b';')[0].strip().lower() != b'application/json':
                return await reject(415, 'JSON_REQUIRED', 'Send application/json.')
            sent = False
            original_receive = receive
            async def replay():
                nonlocal sent
                if not sent:
                    sent = True
                    return {'type': 'http.request', 'body': bytes(body), 'more_body': False}
                return await original_receive()
            receive = replay
        try:
            await self.app(scope, receive, wrapped_send)
        finally:
            logger.info('request id=%s method=%s path=%s status=%s duration_ms=%s', request_id, scope['method'], scope['path'][:180], status[0], round((time.monotonic() - started) * 1000))


app.add_middleware(RequestBoundary)
for router in (auth.router, content.router, media.router, contact.router):
    app.include_router(router, prefix='/api/v1')


@app.get('/api/v1/health/live')
def live():
    return {'status': 'ok'}


@app.get('/api/v1/health/ready')
def ready(db: Session = Depends(get_db)):
    try:
        version = db.scalar(text('SELECT version_num FROM alembic_version'))
        if version != '0001_initial':
            raise ValueError('Schema mismatch')
        LocalStorage().health_check()
    except Exception:
        raise APIError(503, 'NOT_READY', 'A required service is unavailable.')
    return {'status': 'ready'}
