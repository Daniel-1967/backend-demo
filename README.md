Backend Demo — Integrations API (FastAPI + Postgres)

Public sample repo to demonstrate backend & integration patterns (without exposing private product IP). Focus: API standards, API-key auth, webhook ingestion (idempotency/signature), migrations, and clean project structure.

## Stack

  FastAPI
  PostgreSQL (Docker)
  SQLAlchemy + Alembic
  Uvicorn

## Repo structure (high-level)

  app/main.py — FastAPI bootstrap + router registration
  app/api/routers/health.py — GET /v1/health
  app/api/routers/events.py — GET /v1/events (API key protected)
  app/api/deps.py — require_api_key dependency (X-API-Key)
  app/models/ — ORM models (ApiKey, WebhookEvent)
  migrations/ — Alembic migrations
  docker/docker-compose.yml — Postgres 16
  scripts/seed_api_keys.py — creates dummy API keys

## Run locally (Windows / PowerShell)

## Prereqs

  Python 3.10+
  Docker Desktop
  Dependencies installed (venv recommended)

### 1) Start Postgres
  +```powershell
  docker compose -f docker/docker-compose.yml up -d
  docker ps
  +```

Wait until container status is healthy.

### 2) Apply migrations
  +```powershell
  alembic upgrade head
  +```

### 3) Seed API keys
  +```powershell
  python -m scripts.seed_api_keys
  +```

Creates:

  demo_key_1
  demo_key_2

### 4) Run API
  +```powershell
  uvicorn app.main:app --reload
  +```

## Quick checks

### PowerShell note about curl

In PowerShell, `curl` is an alias for `Invoke-WebRequest`. Use `curl.exe` to avoid warnings.
Also, **avoid** inline `curl.exe -d '{...}'` in PowerShell for JSON payloads (quoting/encoding is unreliable). Use `Invoke-RestMethod` or `--data-binary @file` as shown below.

In PowerShell, curl is an alias for Invoke-WebRequest. Use curl.exe to avoid warnings:

curl.exe http://127.0.0.1:8000/v1/health

## Health
curl.exe http://127.0.0.1:8000/v1/health

Expected:

{"status":"ok"}

Events (API key required)
curl.exe http://127.0.0.1:8000/v1/events -H "X-API-Key: demo_key_1"

Expected:

{"items":[],"next_cursor":null}

## Database verification (optional)

List tables:

docker exec -it backend-demo-db psql -U postgres -d backend_demo -c "\dt"

Expected:

  api_keys
  webhook_events
  alembic_version

## Notes / Decisions

  Alembic migrations are required before running seeds.
  API keys are stored in api_keys and validated via X-API-Key.
  Webhook/event persistence is stored in webhook_events.


## Webhook (HMAC + Idempotency) — PowerShell-safe

This endpoint validates:
- `Idempotency-Key` (required)
- `X-Signature` = HMAC-SHA256 of the **raw request body bytes** using `WEBHOOK_SECRET`

## 1) Set secret (local)

Add to `.env`:
- `WEBHOOK_SECRET=change_me`

Restart the server after changing env vars.

## 2) Send a webhook (Windows PowerShell + curl.exe)

PowerShell quoting/encoding can corrupt JSON bytes. Use a UTF-8 file and post bytes from disk:

```powershell
$body = '{"event_type":"invoice.created","external_id":"inv_1"}'
Set-Content -Path .\tmp.json -Value $body -Encoding utf8 -NoNewline

$sig = python -c "import hmac,hashlib,pathlib; secret=b'change_me'; body=pathlib.Path('tmp.json').read_bytes(); print(hmac.new(secret,body,hashlib.sha256).hexdigest())"

curl.exe -X POST "http://127.0.0.1:8000/v1/webhooks/provider-x" `
  -H "Idempotency-Key: idem_002" `
  -H "X-Signature: $sig" `
  -H "Content-Type: application/json" `
  --data-binary "@tmp.json"

  ```
  Expected:
  ```json
  {"status":"accepted","id":1,"idempotency_key":"idem_002","signature_valid":true}
  ```
### 3) Verify stored events
```powershell
 curl.exe "http://127.0.0.1:8000/v1/events" -H "X-API-Key: demo_key_1"
```

## Integration (Outbound) — ERP-like sync (retries/backoff)

Endpoint:
- `POST /v1/integrations/erp/sync` (API key required)

### Send sync (PowerShell-safe)

Option A — `Invoke-RestMethod` (recommended):
```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/v1/integrations/erp/sync" `
  -Headers @{ "X-API-Key"="demo_key_1" } `
  -ContentType "application/json" `
  -Body '{"external_id":"inv_2"}'
```

Option B — `curl.exe` posting bytes from a UTF-8 file:
```powershell
$body = '{"external_id":"inv_2"}'
Set-Content -Path .\tmp-sync.json -Value $body -Encoding utf8 -NoNewline

curl.exe -X POST "http://127.0.0.1:8000/v1/integrations/erp/sync" `
  -H "X-API-Key: demo_key_1" `
  -H "Content-Type: application/json" `
  --data-binary "@tmp-sync.json"
```

Expected:
```json
{"status":"sent","attempts":1,"upstream_status":200}
```

## Troubleshooting

- If you edit `.env`, restart `uvicorn` (settings are cached via `lru_cache`).
- If you see JSON decode errors using `curl.exe -d ...` on PowerShell, use `Invoke-RestMethod` or `--data-binary @file` (see examples above).