## b/app/integrations/whatsapp_client.py
from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.core.errors import app_error
from app.core.config import get_logger

log = get_logger("whatsapp_client")


def _wa_headers() -> dict:
    s = get_settings()
    token = s.get("WA_ACCESS_TOKEN")
    if not token:
        raise app_error("CONFIG_ERROR", "WA_ACCESS_TOKEN not set")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def send_text(to_phone: str, body: str) -> dict:
    s = get_settings()
    base = s.get("WA_BASE_URL")
    ver = s.get("WA_API_VERSION")
    phone_id = s.get("WA_PHONE_NUMBER_ID")
    if not phone_id:
        raise app_error("CONFIG_ERROR", "WA_PHONE_NUMBER_ID not set")

    url = f"{base}/{ver}/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": body},
    }

    with httpx.Client(timeout=30.0) as client:
        r = client.post(url, headers=_wa_headers(), json=payload)
        if r.status_code >= 400:
            log.error("wa send failed status=%s body=%s", r.status_code, r.text)
            raise app_error("UPSTREAM_ERROR", "WhatsApp send failed", upstream_status=r.status_code)
        return r.json()


def send_template(to_phone: str, template_name: str, lang_code: str = "en_US") -> dict:
    s = get_settings()
    base = s.get("WA_BASE_URL")
    ver = s.get("WA_API_VERSION")
    phone_id = s.get("WA_PHONE_NUMBER_ID")
    if not phone_id:
        raise app_error("CONFIG_ERROR", "WA_PHONE_NUMBER_ID not set")

    url = f"{base}/{ver}/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "template",
        "template": {"name": template_name, "language": {"code": lang_code}},
    }

    with httpx.Client(timeout=30.0) as client:
        r = client.post(url, headers=_wa_headers(), json=payload)
        if r.status_code >= 400:
            log.error("wa template send failed status=%s body=%s", r.status_code, r.text)
            raise app_error("UPSTREAM_ERROR", "WhatsApp send failed", upstream_status=r.status_code)
        return r.json()
