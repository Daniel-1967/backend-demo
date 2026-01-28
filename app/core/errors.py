from __future__ import annotations

from typing import Any, Optional
from fastapi import HTTPException


def app_error(
    *,
    code: str,
    message: str,
    http_status: int = 400,
    extra: Optional[dict[str, Any]] = None,
) -> HTTPException:
    payload: dict[str, Any] = {"code": code, "message": message}
    if extra:
        payload.update(extra)
    return HTTPException(status_code=http_status, detail=payload)
