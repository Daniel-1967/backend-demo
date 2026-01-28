
## b/app/integrations/sap_odata.py
from __future__ import annotations

import httpx

from app.core.config import get_settings, get_logger
from app.core.errors import app_error

log = get_logger("sap_odata")


def fetch(entity_path: str, top: int = 10) -> dict:
    s = get_settings()
    base = s.get("SAP_BASE_URL")
    if not base:
        raise app_error("CONFIG_ERROR", "SAP_BASE_URL not set")

    # OData typical params: $top
    url = f"{base.rstrip('/')}/{entity_path.lstrip('/')}"
    params = {"$top": top}

    auth = None
    if s.get("SAP_USER") and s.get("SAP_PASSWORD"):
        auth = (s["SAP_USER"], s["SAP_PASSWORD"])

    with httpx.Client(timeout=30.0) as client:
        r = client.get(url, params=params, auth=auth, headers={"Accept": "application/json"})
        if r.status_code >= 400:
            log.error("sap fetch failed status=%s body=%s", r.status_code, r.text[:500])
            raise app_error("UPSTREAM_ERROR", "SAP OData fetch failed", upstream_status=r.status_code)
        return r.json()
