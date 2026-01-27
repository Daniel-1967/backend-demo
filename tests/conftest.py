##  b/tests/conftest.py

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text


@pytest.fixture(scope="session", autouse=True)
def _test_env():
    """
    Ensure required env vars exist for tests.
    Uses local .env if present; but tests should not depend on it.
    """
    os.environ.setdefault("ENV", "test")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("WEBHOOK_SECRET", "change_me")
    # DB_URL must be provided externally (local .env or CI env)
    yield


@pytest.fixture()
def client():
    # Import lazily AFTER env is set
    from app.main import app
    return TestClient(app)


def _truncate_all():
    from app.core.db import db_session
    with db_session() as db:
        # Keep it simple; these are the only demo tables we care about
        db.execute(text("TRUNCATE TABLE webhook_events RESTART IDENTITY CASCADE"))
        db.execute(text("TRUNCATE TABLE api_keys RESTART IDENTITY CASCADE"))


@pytest.fixture(autouse=True)
def _clean_db_between_tests():
    """
    Requires DB to be migrated (alembic upgrade head) before running tests.
    """
    _truncate_all()
    yield
    _truncate_all()


@pytest.fixture()
def seed_api_key():
    """
    Inserts demo_key_1 as active API key.
    """
    from app.core.db import db_session
    from app.models.api_key import ApiKey

    with db_session() as db:
        db.add(ApiKey(key="demo_key_1", is_active=True))
        db.flush()
    return "demo_key_1"
