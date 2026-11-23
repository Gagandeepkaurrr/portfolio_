from datetime import datetime, timezone
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import get_settings


class Base(DeclarativeBase):
    pass


def now():
    return datetime.now(timezone.utc)


@lru_cache
def get_engine():
    return create_engine(get_settings().database_url, pool_pre_ping=True, pool_size=5, max_overflow=10)


def session_factory():
    return sessionmaker(get_engine(), expire_on_commit=False)


def get_db():
    with session_factory()() as session:
        try:
            yield session
        finally:
            session.rollback()
