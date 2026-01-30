## b/app/integrations/gpt_collection.py

from __future__ import annotations

import json
from fastapi import HTTPException
from typing import Any

from app.core.config import get_settings, get_logger
from app.core.errors import app_error

log = get_logger("gpt_collection")


SYSTEM = (
    "You are a cash collection analyst for LATAM SMEs. "
    "Return ONLY valid JSON, no markdown. "
    "Schema: "
    '{"summary": str, "ranking":[{"priority":int,"customer":str,"amount":number,"due_date":str,'
    '"prob_pay":number,"reason":str}],"messages":[{"customer":str,"channel":str,"message":str}] }'
)


# Alias para compatibilidad con el nombre usado en analyze()
SYSTEM_INSTRUCTIONS = SYSTEM


def _use_demo_mode(s: dict) -> bool:
    mode = str(s.get("GPT_MODE") or "auto").lower().strip()
    if mode in ("demo", "mock"):
        return True
    if mode in ("real", "prod", "production"):
        return False
    # auto: if no key => demo
    return not bool(s.get("OPENAI_API_KEY"))


def _demo_response(payload: dict) -> dict:
    col = payload.get("collection") or []        
    ranking = []
    for i, item in enumerate(col[:3], start=1):
        cid = str(item.get("id") or f"item_{i}")
        ranking.append(
            {
                "priority": i,
                "customer": f"customer_{cid}",
                "amount": 0,
                "due_date": "2026-02-15",
                "prob_pay": 0.6,
                "reason": "demo-mock (no external calls)",
            }
        )
    return {
        "summary": f"demo-mock: analyzed {len(col)} items",
        "ranking": ranking,
        "messages": [
            {"customer": r["customer"], "channel": "whatsapp", "message": "demo reminder"}
            for r in ranking
        ],
    }


def _get_client_real(s: dict):
    # Lazy import so repo can run without OpenAI installed unless real mode is used
    try:
        from openai import OpenAI
    except Exception:
        raise app_error(
            code="CONFIG_ERROR",
            message="openai package not installed (pip install openai)",
            http_status=500,
        )

    key = s.get("OPENAI_API_KEY")
    if not key:
        raise app_error(code="CONFIG_ERROR", message="OPENAI_API_KEY not set", http_status=500)
         
    return OpenAI(api_key=key)

def _extract_text(resp) -> str:
    ot = getattr(resp, "output_text", None)
    if isinstance(ot, str) and ot.strip():
        return ot.strip()
    output = getattr(resp, "output", None)
    if not isinstance(output, list):
        return ""
    parts: list[str] = []
    for item in output:
        itype = getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else None)
        if itype != "message":
            continue
        content = getattr(item, "content", None) or (item.get("content") if isinstance(item, dict) else None)
        if not isinstance(content, list):
            continue
        for c in content:
            ctype = getattr(c, "type", None) or (c.get("type") if isinstance(c, dict) else None)
            text = getattr(c, "text", None) or (c.get("text") if isinstance(c, dict) else None)
            if ctype in ("output_text", "text") and isinstance(text, str):
                parts.append(text)
    return "\n".join(parts).strip()


def analyze(payload: dict) -> Any:
    s = get_settings()
    model = s.get("OPENAI_MODEL") or "gpt-4.1-mini"
    timeout_s = int(s.get("OPENAI_TIMEOUT_S") or 30)

    if _use_demo_mode(s):
        return _demo_response(payload)

    client = _get_client_real(s)
    user_prompt = json.dumps(payload, ensure_ascii=False)



    # Responses API (current OpenAI SDK pattern)
    try:
        resp = client.responses.create(            
            model=model,
            instructions=SYSTEM_INSTRUCTIONS,
            input=user_prompt,
            timeout=timeout_s,
        )
        raw = _extract_text(resp)
    except HTTPException:
        raise
    except Exception as e:
        log.exception("openai call failed")
        raise app_error(code="UPSTREAM_ERROR", message=f"OpenAI call failed: {type(e).__name__}: {e}", http_status=502)

    if not raw:
        raise app_error(code="UPSTREAM_ERROR", message="Empty model response", http_status=502)
         

    try:
        return json.loads(raw)
    except Exception:
        # best-effort cleanup
        cleaned = raw.strip().strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
        try:
            return json.loads(cleaned)
        except Exception as e:
            log.error("invalid model json raw=%s", raw[:500])
            raise app_error(
                code="UPSTREAM_ERROR",
                message=f"Model returned invalid JSON: {type(e).__name__}",
                http_status=502,
            )            
