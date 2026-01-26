## b/app/core/db.py

from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache()
def get_engine() -> Engine:
    s = get_settings()
    url = s.get("DB_URL") or s.get("DATABASE_URL")
    if not url:
        raise ValueError("DB_URL (or DATABASE_URL) is required")

    # Public demo: keep it simple, sync engine (docker-compose Postgres)
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=1800,
        future=True,
    )


@lru_cache()
def _session_factory() -> sessionmaker:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)


@contextmanager
def db_session() -> Iterator[Session]:
    session = _session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
