# Backend Demo — Integrations API (FastAPI + Postgres)

Public sample repo to demonstrate backend & integration patterns (without exposing private product IP).
Focus: API standards, API-key auth, webhook ingestion (idempotency + HMAC signature), migrations, and clean structure.

## Stack

- FastAPI
- PostgreSQL (Docker)
- SQLAlchemy + Alembic
- Uvicorn
- Pytest (CI)

## What this repo demonstrates

- API base `/v1`
- API-key auth via `X-API-Key`
- Webhook endpoint with:
  - `Idempotency-Key` (replay safe)
  - `X-Signature` (HMAC-SHA256 over raw body bytes)
- Outbound “ERP-like” sync:
  - retries + backoff
  - timeout/error mapping to a standard error payload
- Alembic migrations + local Postgres via Docker Compose
- Minimal tests + GitHub Actions CI

## Repo structure (high-level)

- `app/main.py` — FastAPI bootstrap + router registration
- `app/api/routers/health.py` — `GET /v1/health`
- `app/api/routers/events.py` — `GET /v1/events` (API key protected)
- `app/api/routers/webhooks.py` — `POST /v1/webhooks/{provider}`
- `app/api/routers/integrations.py` — `POST /v1/integrations/erp/sync`
- `app/api/deps.py` — `require_api_key` dependency (`X-API-Key`)
- `app/models/` — ORM models (`ApiKey`, `WebhookEvent`)
- `migrations/` — Alembic migrations
- `docker/docker-compose.yml` — Postgres 16
- `scripts/seed_api_keys.py` — seeds dummy API keys

## Configuration

Copy `.env.example` to `.env` and adjust if needed.

Typical `.env`:
- `DB_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/backend_demo`
- `WEBHOOK_SECRET=change_me`
- `API_KEYS_SEED_FILE=scripts/seeds/api_keys.csv`

Notes:
- If you change `.env`, restart `uvicorn` (settings are cached via `lru_cache`).

## Run locally (Windows / PowerShell)

### Prereqs
- Python 3.10+
- Docker Desktop

### 1) Start Postgres
```powershell
docker compose -f docker/docker-compose.yml up -d
docker ps


Wait until container status is healthy.
2) Apply migrations
alembic upgrade head

3) Seed API keys
python -m scripts.seed_api_keys

Creates:


demo_key_1


demo_key_2


4) Run API
uvicorn app.main:app --reload

Quick checks
PowerShell note about curl
In PowerShell, curl is an alias for Invoke-WebRequest. Use curl.exe.
Also, avoid inline curl.exe -d '{...}' JSON in PowerShell (quoting/encoding is unreliable).
Prefer Invoke-RestMethod or --data-binary @file (examples below).
Health
curl.exe "http://127.0.0.1:8000/v1/health"

Expected:
{"status":"ok"}

Events (API key required)
curl.exe "http://127.0.0.1:8000/v1/events" -H "X-API-Key: demo_key_1"

Expected:
{"items":[],"next_cursor":null}

Database verification (optional)
List tables:
docker exec -it backend-demo-db psql -U postgres -d backend_demo -c "\dt"

Expected:


api_keys


webhook_events


alembic_version


Webhook (HMAC + Idempotency) — PowerShell-safe
Endpoint:


POST /v1/webhooks/{provider} (example: /v1/webhooks/provider-x)


This endpoint validates:


Idempotency-Key (required)


X-Signature = HMAC-SHA256 of the raw request body bytes using WEBHOOK_SECRET


1) Ensure secret is set
In .env:


WEBHOOK_SECRET=change_me


Restart uvicorn after changes.
2) Send a webhook (Windows PowerShell + curl.exe)
Use a UTF-8 file and post bytes from disk (avoids JSON corruption):
$body = '{"event_type":"invoice.created","external_id":"inv_1"}'
Set-Content -Path .\tmp.json -Value $body -Encoding utf8 -NoNewline

$sig = python -c "import hmac,hashlib,pathlib; secret=b'change_me'; body=pathlib.Path('tmp.json').read_bytes(); print(hmac.new(secret,body,hashlib.sha256).hexdigest())"

curl.exe -X POST "http://127.0.0.1:8000/v1/webhooks/provider-x" `
  -H "Idempotency-Key: idem_002" `
  -H "X-Signature: $sig" `
  -H "Content-Type: application/json" `
  --data-binary "@tmp.json"

Expected:
{"status":"accepted","id":1,"idempotency_key":"idem_002","signature_valid":true}

3) Verify stored events
curl.exe "http://127.0.0.1:8000/v1/events" -H "X-API-Key: demo_key_1"

Integration (Outbound) — ERP-like sync (retries/backoff)
Endpoint:


POST /v1/integrations/erp/sync (API key required)


Send sync (PowerShell-safe)
Option A — Invoke-RestMethod (recommended):
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/v1/integrations/erp/sync" `
  -Headers @{ "X-API-Key"="demo_key_1" } `
  -ContentType "application/json" `
  -Body '{"external_id":"inv_2"}'

Option B — curl.exe posting bytes from a UTF-8 file:
$body = '{"external_id":"inv_2"}'
Set-Content -Path .\tmp-sync.json -Value $body -Encoding utf8 -NoNewline

curl.exe -X POST "http://127.0.0.1:8000/v1/integrations/erp/sync" `
  -H "X-API-Key: demo_key_1" `
  -H "Content-Type: application/json" `
  --data-binary "@tmp-sync.json"

Expected:
{"status":"sent","attempts":1,"upstream_status":200}

Tests
Run:
python -m pytest -q

Troubleshooting

If you see JSON decode errors using curl.exe -d ... in PowerShell, use:

Invoke-RestMethod, or

--data-binary @file with a UTF-8 file (examples above).

If migrations don’t apply, confirm DB is reachable and tables exist via \dt.

Si querés, próximo paso concreto: “pulir” README con 1 bloque “Run in 3 commands” bien corto (sin ejemplos largos) y dejar los ejemplos webhook/sync como “Appendix: PowerShell-safe examples” para que no quede kilométrico.
::contentReference[oaicite:1]{index=1}
Fuentes