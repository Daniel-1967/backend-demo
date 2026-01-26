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
        "API_BASE_PATH": _pick("API_BASE_PATH") or "/v1",
        "OPENAPI_PATH": _pick("OPENAPI_PATH") or "/v1/openapi.json",
        "ALLOWED_ORIGINS": _pick("ALLOWED_ORIGINS") or "http://localhost:3000",
        "ENABLE_HEALTH_ROOT": (_pick("ENABLE_HEALTH_ROOT") or "false").lower() in ("1", "true", "yes"),
        # Optional (used only if you enable the AI provider module later)
        "OPENAI_API_KEY": _pick("OPENAI_API_KEY"),
        "OPENAI_MODEL": _pick("OPENAI_MODEL") or "gpt-4.1-mini",
    }


_logger_inited = False


def get_logger(name: str) -> logging.Logger:
    global _logger_inited
    if not _logger_inited:
        lvl = getattr(logging, str(get_settings()["LOG_LEVEL"]).upper(), logging.INFO)
        logging.basicConfig(level=lvl, format="%(levelname)s %(name)s | %(message)s")
        _logger_inited = True
    return logging.getLogger(name)
