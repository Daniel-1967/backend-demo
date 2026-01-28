## b/app/core/config.py

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

# Load .env once (does not override already-exported env vars)
_dotenv_path = find_dotenv(usecwd=True)
if not _dotenv_path:
    maybe = Path(".env")
    _dotenv_path = str(maybe) if maybe.exists() else ""
if _dotenv_path:
    load_dotenv(_dotenv_path, override=False)


def _pick(*keys: str) -> str | None:
    for k in keys:
        v = os.getenv(k)
        if v:
            return v
    return None


@lru_cache()    
def get_settings() -> dict:
    # Keep this repo domain-agnostic and safe for public use.
    return {
        "APP_NAME": _pick("APP_NAME") or "backend-demo",
        "ENV": _pick("ENV") or "local",
        "LOG_LEVEL": _pick("LOG_LEVEL") or "INFO",
        "DB_URL": _pick("DB_URL", "DATABASE_URL"),
        "API_KEYS_SEED_FILE": _pick("API_KEYS_SEED_FILE") or "scripts/seeds/api_keys.csv",
        "WEBHOOK_SECRET": _pick("WEBHOOK_SECRET"),
        "ERP_BASE_URL": _pick("ERP_BASE_URL") or "http://127.0.0.1:8000/v1/_mock/erp",        
        "API_BASE_PATH": _pick("API_BASE_PATH") or "/v1",
        "OPENAPI_PATH": _pick("OPENAPI_PATH") or "/v1/openapi.json",
        "ALLOWED_ORIGINS": _pick("ALLOWED_ORIGINS") or "http://localhost:3000",
        "ENABLE_HEALTH_ROOT": (_pick("ENABLE_HEALTH_ROOT") or "false").lower() in ("1", "true", "yes"),
        "WEBHOOK_SECRET": _pick("WEBHOOK_SECRET"),        
        # Optional (used only if you enable the AI provider module later)
        "OPENAI_API_KEY": _pick("OPENAI_API_KEY"),
        "OPENAI_MODEL": _pick("OPENAI_MODEL") or "gpt-4.1-mini",
        "OPENAI_TIMEOUT_S": int(_pick("OPENAI_TIMEOUT_S") or "30"),        
        # Optional (WhatsApp Cloud API)
        "WA_BASE_URL": _pick("WA_BASE_URL") or "https://graph.facebook.com",
        "WA_API_VERSION": _pick("WA_API_VERSION") or "v20.0",
        "WA_PHONE_NUMBER_ID": _pick("WA_PHONE_NUMBER_ID"),
        "WA_ACCESS_TOKEN": _pick("WA_ACCESS_TOKEN"),
        "WA_VERIFY_TOKEN": _pick("WA_VERIFY_TOKEN") or "change_me",
        # If set, validate Meta webhooks signature header X-Hub-Signature-256
        "WA_APP_SECRET": _pick("WA_APP_SECRET"),

        # Optional (SAP OData)
        "SAP_BASE_URL": _pick("SAP_BASE_URL"),
        "SAP_USER": _pick("SAP_USER"),
        "SAP_PASSWORD": _pick("SAP_PASSWORD"),
        # Outbound integration demo (ERP-like)
        "ERP_BASE_URL": _pick("ERP_BASE_URL") or "http://127.0.0.1:8000/v1/_mock/erp",
        "ERP_TIMEOUT_S": float(_pick("ERP_TIMEOUT_S") or "5"),
        "ERP_RETRIES": int(_pick("ERP_RETRIES") or "3"),        
    }


_logger_inited = False


def get_logger(name: str) -> logging.Logger:
    global _logger_inited
    if not _logger_inited:
        lvl = getattr(logging, str(get_settings()["LOG_LEVEL"]).upper(), logging.INFO)
        logging.basicConfig(level=lvl, format="%(levelname)s %(name)s | %(message)s")
        _logger_inited = True
    return logging.getLogger(name)
