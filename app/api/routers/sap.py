## b/app/api/routers/sap.py

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.integrations.sap_odata import fetch
from app.core.db import get_db

router = APIRouter(prefix="/v1", tags=["sap"])


@router.get("/integrations/sap/odata/{entity_path:path}")
def sap_odata_get(entity_path: str, top: int = 10, _=Depends(require_api_key)):
    return fetch(entity_path=entity_path, top=top)
