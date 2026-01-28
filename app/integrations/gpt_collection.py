## b/app/integrations/gpt_collection.py

from __future__ import annotations

import json
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


def _get_client():
    # Lazy import so repo can run without OpenAI installed unless this endpoint is used
    try:
        from openai import OpenAI
    except Exception:
        raise app_error("CONFIG_ERROR", "openai package not installed (pip install openai)")

    s = get_settings()
    key = s.get("OPENAI_API_KEY")
    if not key:
        raise app_error("CONFIG_ERROR", "OPENAI_API_KEY not set")
    return OpenAI(api_key=key)


def analyze(payload: dict) -> Any:
    s = get_settings()
    model = s.get("OPENAI_MODEL") or "gpt-4.1-mini"
    timeout_s = int(s.get("OPENAI_TIMEOUT_S") or 30)

    client = _get_client()
    user = json.dumps(payload, ensure_ascii=False)

    # Responses API (current OpenAI SDK pattern)
    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        timeout=timeout_s,
    )
    raw = (resp.output_text or "").strip()
    if not raw:
        raise app_error("UPSTREAM_ERROR", "Empty model response", upstream_status=502)

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
            raise app_error("UPSTREAM_ERROR", f"Model returned invalid JSON: {type(e).__name__}", upstream_status=502)
