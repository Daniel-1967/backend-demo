
## b/app/api/routers/whatsapp.py

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

from fastapi import APIRouter, Depends, Request

from app.api.deps import require_api_key
from app.core.config import get_settings, get_logger
from app.core.errors import app_error
from app.core.db import get_db
from app.models.webhook_event import WebhookEvent

from app.integrations.whatsapp_client import send_text, send_template

router = APIRouter(prefix="/v1", tags=["whatsapp"])
log = get_logger("whatsapp_router")


@router.post("/integrations/whatsapp/send-text")
def wa_send_text(payload: dict, _=Depends(require_api_key)) -> Any:
    to = payload.get("to")
    body = payload.get("body")
    if not to or not body:
        raise app_error("VALIDATION_ERROR", "Missing fields: to, body")
    return send_text(to_phone=str(to), body=str(body))


@router.post("/integrations/whatsapp/send-template")
def wa_send_template(payload: dict, _=Depends(require_api_key)) -> Any:
    to = payload.get("to")
    template = payload.get("template_name")
    lang = payload.get("lang_code") or "en_US"
    if not to or not template:
        raise app_error("VALIDATION_ERROR", "Missing fields: to, template_name")
    return send_template(to_phone=str(to), template_name=str(template), lang_code=str(lang))


# Meta webhook verification (GET)
# /v1/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...
@router.get("/webhooks/whatsapp")
def wa_webhook_verify(request: Request) -> Any:
    s = get_settings()
    verify_token = s.get("WA_VERIFY_TOKEN") or "change_me"

    q = request.query_params
    mode = q.get("hub.mode")
    token = q.get("hub.verify_token")
    challenge = q.get("hub.challenge")

    if mode == "subscribe" and token == verify_token and challenge:
        # Must return raw challenge string
        return challenge
    raise app_error("FORBIDDEN", "Webhook verify failed")


def _verify_meta_signature(raw_body: bytes, header_value: str | None) -> bool:
    """
    Meta sends: X-Hub-Signature-256: sha256=<hex>
    If WA_APP_SECRET is not set, we skip verification (still safe for public demo).
    """
    s = get_settings()
    secret = s.get("WA_APP_SECRET")
    if not secret:
        return True
    if not header_value:
        return False
    if not header_value.startswith("sha256="):
        return False
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(header_value.split("=", 1)[1], expected)


@router.post("/webhooks/whatsapp")
async def wa_webhook_receive(request: Request) -> Any:
    raw = await request.body()
    sig = request.headers.get("X-Hub-Signature-256")
    if not _verify_meta_signature(raw, sig):
        raise app_error("FORBIDDEN", "Invalid webhook signature")

    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise app_error("VALIDATION_ERROR", f"Invalid JSON body: {type(e).__name__}")

    # Best-effort extraction of message id / sender / text for demo visibility
    extracted = {
        "message_id": None,
        "from": None,
        "text": None,
        "raw": data,
    }
    try:
        entry0 = (data.get("entry") or [])[0]
        change0 = (entry0.get("changes") or [])[0]
        value = change0.get("value") or {}
        msg0 = (value.get("messages") or [])[0]
        extracted["message_id"] = msg0.get("id")
        extracted["from"] = msg0.get("from")
        txt = msg0.get("text") or {}
        extracted["text"] = txt.get("body")
    except Exception:
        pass

    db = get_db()
    ev = WebhookEvent(
        provider="whatsapp",
        event_type="messages",
        external_id=extracted["message_id"],
        idempotency_key=extracted["message_id"] or f"wa_{hashlib.sha256(raw).hexdigest()[:16]}",
        signature_valid=True,
        payload=json.dumps(extracted, ensure_ascii=False),
    )
    db.add(ev)
    db.commit()

    return {"status": "accepted", "stored_event_id": ev.id}
