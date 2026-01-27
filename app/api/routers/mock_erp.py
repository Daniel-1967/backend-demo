## b/app/api/routers/mock_erp.py
from __future__ import annotations
import json
from fastapi import APIRouter, HTTPException, Request
from app.core.config import get_logger

router = APIRouter(tags=["_mock"])
log = get_logger("mock_erp")

@router.post("/_mock/erp")
async def mock_erp(request: Request):
    # deterministic failure injection:
    # /v1/_mock/erp?fail=1 -> 500
    fail = request.query_params.get("fail")
    if fail in ("1", "true", "yes"):
        raise HTTPException(status_code=500, detail={"code": "MOCK_FAIL", "message": "forced failure"})

    raw = await request.body()
    if not raw:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": "Empty body"})

    try:
        # Parse JSON ourselves so we can control the error and avoid 500s.
        body = json.loads(raw.decode("utf-8"))
    except Exception as e:
        preview = raw[:200].decode("utf-8", errors="replace")
        log.warning("Invalid JSON body (preview=%r) err=%s", preview, type(e).__name__)
        raise HTTPException(
            status_code=400,
            detail={"code": "VALIDATION_ERROR", "message": f"Invalid JSON body: {type(e).__name__}"},
        )
