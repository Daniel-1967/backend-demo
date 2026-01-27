## b/app/api/routers/integrations.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import require_api_key
from app.core.config import get_settings
from app.integrations.erp_client import post_with_retries

router = APIRouter(tags=["integrations"])


@router.post("/integrations/erp/sync", dependencies=[Depends(require_api_key)])
def erp_sync(payload: dict):
    # minimal contract for demo
    external_id = payload.get("external_id")
    action = payload.get("action") or "sync"
    if not external_id:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": "external_id is required"})

    s = get_settings()
    url = s["ERP_BASE_URL"]
    idem = f"erp:{action}:{external_id}"

    res = post_with_retries(url=url, json_body={"external_id": external_id, "action": action}, idempotency_key=idem)

    if not res.ok:
        raise HTTPException(
            status_code=502,
            detail={
                "code": res.error_code or "UPSTREAM_ERROR",
                "message": "ERP sync failed",
                "upstream_status": res.status_code,
                "attempts": res.attempts,
            },
        )

    return {"status": "sent", "attempts": res.attempts, "upstream_status": res.status_code}
