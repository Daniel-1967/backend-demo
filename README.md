# Backend Demo — Integrations API (FastAPI + Postgres)

Public demo repo to showcase **backend + integrations engineering standards** without exposing private product IP.
No real domain, no real business rules, no private schemas.

Focus:
API standards, API-key auth, webhook ingestion (idempotency + signatures),
real-world outbound integrations (WhatsApp / SAP / GPT style),
migrations, tests, and a clean, production-like structure.

---

## Stack

- FastAPI
- PostgreSQL (Docker)
- SQLAlchemy + Alembic
- Uvicorn
- Pytest + GitHub Actions CI

---

## What this repo demonstrates

- API base path: `/v1`
- API-key authentication via `X-API-Key` (demo keys seeded locally)
- Inbound webhooks:
  - Generic provider webhook: `Idempotency-Key` + HMAC signature (`X-Signature` over raw body)
  - WhatsApp webhook: Meta verification + optional `X-Hub-Signature-256`
- Outbound integrations:
  - WhatsApp Cloud API–style endpoints (send text / template) + webhook receiver
  - SAP OData–style fetch endpoint (proxy pattern)
  - GPT collection analyze endpoint
- Centralized error model (`code`, `message`)
- Alembic migrations + local Postgres via Docker Compose
- Minimal automated tests + CI

---

## Run locally (Windows PowerShell)

```powershell
Copy-Item .env.example .env
docker compose -f docker/docker-compose.yml up -d
python -m pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed_api_keys
uvicorn app.main:app --reload
```

## Then:
    Health: GET http://127.0.0.1:8000/v1/health
    OpenAPI: http://127.0.0.1:8000/docs

## Repo structure (high-level)

    app/main.py — FastAPI bootstrap + router registration
    app/api/routers/health.py — GET /v1/health
    app/api/routers/events.py — GET /v1/events (API-key protected)
    app/api/routers/webhooks.py — inbound webhook (idempotency + HMAC)
    app/api/routers/integrations.py — outbound ERP-like sync
    app/api/routers/mock_erp.py — mock upstream used by ERP sync
    app/api/routers/whatsapp.py — WhatsApp send + webhook verify/receive
    app/api/routers/sap.py — SAP OData proxy fetch
    app/api/routers/gpt.py — GPT analyze endpoint
    app/api/routers/invoices.py — inbound API example
    app/api/deps.py — require_api_key dependency
    app/models/ — ORM models (ApiKey, WebhookEvent, Invoice)
    migrations/ — Alembic migrations
    docker/docker-compose.yml — Postgres
    scripts/seed_api_keys.py — seeds demo API keys

## Public hygiene / no-IP rules
    No real client data, domains, KPIs, or business logic
    Secrets are never committed
    .env ignored, .env.example provided

## Documentation
    docs/USAGE.md
    How to run the project and exercise the APIs.
    docs/INTEGRATIONS.md
    Integration design notes: contracts, idempotency, retries, error handling.