from __future__ import annotations

from typing import Any, Optional
from fastapi import HTTPException

def app_error(*args, **kwargs) -> HTTPException:
    # Backward compatible:
    # - app_error(code="X", message="Y", http_status=..., extra={...})
    # - app_error("X", "Y", upstream_status=..., http_status=...)
    if args:
        if len(args) != 2:
            raise TypeError("app_error expects (code, message) as positional args")
        code, message = args
        http_status = kwargs.pop("http_status", 400)
        extra = kwargs.pop("extra", None)
        if kwargs:
            extra = {**(extra or {}), **kwargs}
    else:
        code = kwargs.pop("code")
        message = kwargs.pop("message")
        http_status = kwargs.pop("http_status", 400)
        extra = kwargs.pop("extra", None)
        if kwargs:
            extra = {**(extra or {}), **kwargs}

    payload: dict[str, Any] = {"code": code, "message": message}
    if extra:
        payload.update(extra)
    return HTTPException(status_code=http_status, detail=payload)


