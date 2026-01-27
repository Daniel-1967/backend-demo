import hmac
import hashlib
import json
from json import JSONDecodeError

from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy import select

from app.core.config import get_settings
from app.core.db import db_session
from app.models.webhook_event import WebhookEvent

router = APIRouter(tags=["webhooks"])


@router.post("/webhooks/provider-x")
async def inbound_webhook(
    request: Request,
    x_signature: str | None = Header(default=None, alias="X-Signature"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    if not idempotency_key:
        raise HTTPException(
            status_code=400,
            detail={"code": "VALIDATION_ERROR", "message": "Idempotency-Key required"},
        )

    raw = await request.body()
    settings = get_settings()
    secret = (settings.get("WEBHOOK_SECRET") or "").encode("utf-8")    
    if not secret:
        raise HTTPException(
            status_code=500,
            detail={"code": "CONFIG_ERROR", "message": "WEBHOOK_SECRET not set"},
        )

    # Compute HMAC SHA256 over raw body; expect hex digest in X-Signature
    computed = hmac.new(secret, raw, hashlib.sha256).hexdigest()
    signature_valid = bool(x_signature) and hmac.compare_digest(x_signature, computed)

    try:
        # Parse EXACTLY what was received (and signed): raw bytes -> text -> json
        try:
            txt = raw.decode("utf-8-sig").strip()
        except UnicodeDecodeError:
            # PowerShell/curl can end up sending UTF-16; accept it defensively
            txt = raw.decode("utf-16").strip()
        payload_obj = json.loads(txt) if txt else {}
        if not isinstance(payload_obj, dict):
            raise HTTPException(
                status_code=400,
                detail={"code": "VALIDATION_ERROR", "message": "JSON body must be an object"},
            )
    except (JSONDecodeError, UnicodeDecodeError) as e:
        sample = raw[:200].decode("utf-8", errors="replace")
        raise HTTPException(
            status_code=400,
            detail={"code": "VALIDATION_ERROR", "message": f"Invalid JSON body: {type(e).__name__}. Raw(sample)={sample}"},
                         
        )

    provider = "provider-x"
    event_type = str(payload_obj.get("event_type") or "unknown")
    external_id = payload_obj.get("external_id")


    with db_session() as db:
        # idempotency check
        existing = db.execute(
            select(WebhookEvent).where(WebhookEvent.idempotency_key == idempotency_key)
        ).scalar_one_or_none()

        if existing:
            return {
                "status": "replay",
                "id": existing.id,
                "idempotency_key": existing.idempotency_key,
                "signature_valid": existing.signature_valid,
            }

        ev = WebhookEvent(
            provider=provider,
            event_type=event_type,
            external_id=external_id,
            idempotency_key=idempotency_key,
            signature_valid=signature_valid,
            payload=payload_obj,            
        )
        db.add(ev)
        db.flush()  # to get ev.id

        return {
            "status": "accepted" if signature_valid else "accepted_with_invalid_signature",
            "id": ev.id,
            "idempotency_key": idempotency_key,
            "signature_valid": signature_valid,
        }
