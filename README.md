# Backend Demo — Integrations API (FastAPI + Postgres)

Public sample repo to demonstrate backend & integration patterns **without exposing private product IP**.
Focus: API standards, API-key auth, webhook ingestion (idempotency + HMAC signature), migrations, and clean structure.

## Stack
- FastAPI
- PostgreSQL (Docker)
- SQLAlchemy + Alembic
- Uvicorn
- Pytest + GitHub Actions CI

## What this repo demonstrates
- API base path: `/v1`
- API-key auth via `X-API-Key`
- Webhook ingestion:
  - `Idempotency-Key` (replay-safe)
  - `X-Signature` = **HMAC-SHA256 of raw body bytes** using `WEBHOOK_SECRET`
- Outbound “ERP-like” sync (mock upstream):
  - retries + backoff + timeouts
  - error mapping to a standard error payload
  - structured logging
- Alembic migrations + local Postgres via Docker Compose
- Minimal tests + CI

## Repo structure (high-level)
- `app/main.py` — FastAPI bootstrap + router registration
- `app/api/routers/health.py` — `GET /v1/health`
- `app/api/routers/events.py` — `GET /v1/events` (API-key protected)
- `app/api/routers/webhooks.py` — `POST /v1/webhooks/{provider}`
- `app/api/routers/integrations.py` — `POST /v1/integrations/erp/sync`
- `app/api/deps.py` — `require_api_key` dependency (`X-API-Key`)
- `app/models/` — ORM models (`ApiKey`, `WebhookEvent`)
- `migrations/` — Alembic migrations
- `docker/docker-compose.yml` — Postgres 16
- `scripts/seed_api_keys.py` — seeds dummy API keys

## Public hygiene / no-IP rules
- No real client data, domain models, table names, endpoints, or business rules from private projects.
- Secrets are **never** committed:
  - `.env` is ignored by git
  - `.env.example` is committed as template

## Configuration
Copy `.env.example` to `.env`:

- `DB_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/backend_demo`
- `WEBHOOK_SECRET=change_me`
- `API_KEYS_SEED_FILE=scripts/seeds/api_keys.csv`
- (optional) `ERP_BASE_URL=http://127.0.0.1:8000/v1/_mock/erp`

Notes:
- If you change `.env`, restart `uvicorn` (settings are cached via `lru_cache`).

## Run locally (Windows / PowerShell)

### Prereqs
- Python 3.10+
- Docker Desktop

### Run in 3 steps
1) Start Postgres
```powershell
docker compose -f docker/docker-compose.yml up -d
