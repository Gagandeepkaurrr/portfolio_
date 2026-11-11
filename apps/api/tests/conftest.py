# ruff: noqa: E402
# Configure the isolated test database before importing the application.
import os
import shutil
from pathlib import Path
import pytest
from dotenv import dotenv_values
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[3]
source = os.environ.get('DATABASE_URL') or dotenv_values(ROOT / '.env').get('DATABASE_URL')
if not source:
    raise RuntimeError('Provide DATABASE_URL or TEST_DATABASE_URL for real PostgreSQL tests')
url = make_url(os.environ.get('TEST_DATABASE_URL') or source).set(database=make_url(os.environ.get('TEST_DATABASE_URL') or source).database if os.environ.get('TEST_DATABASE_URL') else 'portfolio_test_backend')
if '_test' not in url.database:
    raise RuntimeError('Test database name MUST contain _test; refusing to touch it')
with create_engine(url.set(database='postgres'), isolation_level='AUTOCOMMIT').connect() as connection:
    if not connection.scalar(text('SELECT 1 FROM pg_database WHERE datname=:name'), {'name': url.database}):
        # Identifier derives from a guarded URL and is quoted by the DB dialect.
        connection.execute(text('CREATE DATABASE ' + connection.dialect.identifier_preparer.quote(url.database)))
os.environ['DATABASE_URL'] = url.render_as_string(hide_password=False)
os.environ['APP_ENV'] = 'test'
os.environ['MEDIA_ROOT'] = str(ROOT / '.data/test-media')
os.environ.setdefault('PUBLIC_ORIGIN', 'http://localhost:3000')
os.environ.setdefault('CSRF_SECRET', 'test-csrf-secret-which-is-not-a-live-secret-0001')
os.environ.setdefault('ABUSE_HMAC_SECRET', 'test-abuse-secret-which-is-not-a-live-secret-0002')
from alembic import command
from alembic.config import Config
from app.db import Base, get_engine, session_factory
from app.cli import create_owner, seed_site
from app.main import app
from fastapi.testclient import TestClient

command.upgrade(Config(str(ROOT / 'apps/api/alembic.ini')), 'head')


@pytest.fixture(autouse=True)
def reset_database():
    with get_engine().begin() as connection:
        names = ','.join('"' + table.name + '"' for table in Base.metadata.sorted_tables)
        connection.execute(text('TRUNCATE ' + names + ' RESTART IDENTITY CASCADE'))
    shutil.rmtree(ROOT / '.data/test-media', ignore_errors=True)
    with session_factory()() as db:
        seed_site(db)
    yield


@pytest.fixture
def client():
    with TestClient(app, base_url='http://localhost:3000') as value:
        yield value


@pytest.fixture
def owner(client):
    with session_factory()() as db:
        create_owner(db, 'owner@example.com', 'test-only-passphrase-12345')
    response = client.post('/api/v1/admin/auth/login', json={'email': 'owner@example.com', 'password': 'test-only-passphrase-12345'}, headers={'Origin': 'http://localhost:3000'})
    assert response.status_code == 200, response.text
    client.headers.update({'Origin': 'http://localhost:3000', 'X-CSRF-Token': response.json()['csrf_token']})
    return client
