from fastapi import Header, HTTPException
from sqlalchemy import select

from app.core.db import db_session
from app.models.api_key import ApiKey


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str:
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail={"code": "AUTH_REQUIRED", "message": "X-API-Key required"},
        )

    with db_session() as db:
        row = db.execute(
            select(ApiKey).where(ApiKey.key == x_api_key, ApiKey.is_active.is_(True))
        ).scalar_one_or_none()

    if not row:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "Invalid or inactive API key"},
        )

    return x_api_key
