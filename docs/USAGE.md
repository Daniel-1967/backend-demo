

---

## docs/USAGE.md

```md
# Usage Guide

This document shows **how to exercise the APIs locally**.
Examples are PowerShell-safe.

---

## Prerequisites

- Python 3.10+
- Docker Desktop
- PowerShell (Windows)

> Note: in PowerShell, `curl` is an alias for `Invoke-WebRequest`.  
> Use `curl.exe` explicitly.

---

## Health check

```bash
curl.exe "http://127.0.0.1:8000/v1/health"


## Authentication
    Protected endpoints require:
        Header: X-API-Key: <value>
    Demo keys are seeded via:
        python -m scripts.seed_api_keys


    PowerShell example:
        $headers = @{ "X-API-Key" = "demo_key_1" }

## Events (protected)
    Invoke-RestMethod -Method GET `
    -Uri "http://127.0.0.1:8000/v1/events?limit=50" `
    -Headers $headers

## Invoices (inbound API example)

    Create:

        $body = @{
        external_id = "inv-1001"
        amount      = 1250.50
        currency    = "USD"
        issued_at   = "2026-01-01"
        } | ConvertTo-Json

        Invoke-RestMethod -Method POST `
        -Uri "http://127.0.0.1:8000/v1/invoices" `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $body


    List:

        Invoke-RestMethod -Method GET `
        -Uri "http://127.0.0.1:8000/v1/invoices?limit=50" `
        -Headers $headers

##Webhooks (provider)

    Endpoint:
        POST /v1/webhooks/{provider}

    Required headers:
        Idempotency-Key
        X-Signature (HMAC over raw body using WEBHOOK_SECRET)

    PowerShell signature example:
        $secret = "change_me"
        $body = '{"event_id":"evt_001","type":"payment.updated"}'
        $bytes = [Text.Encoding]::UTF8.GetBytes($body)
        $hmac = New-Object Security.Cryptography.HMACSHA256
        $hmac.Key = [Text.Encoding]::UTF8.GetBytes($secret)
        $signature = ([BitConverter]::ToString($hmac.ComputeHash($bytes)) -replace "-", "").ToLower()

## ERP sync (outbound)
    Invoke-RestMethod -Method POST `
    -Uri "http://127.0.0.1:8000/v1/integrations/erp/sync" `
    -Headers $headers


    Uses mock upstream:
        POST /v1/_mock/erp
    Tests
        pytest -q
