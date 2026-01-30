
## b/app/api/routers/gpt.py

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.integrations.gpt_collection import analyze

router = APIRouter(tags=["gpt"])


@router.post("/integrations/gpt/collection/analyze")
def gpt_analyze(payload: dict, _=Depends(require_api_key)):
    return analyze(payload)
