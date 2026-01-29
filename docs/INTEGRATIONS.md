
---

## docs/INTEGRATIONS.md

```md
# Integration Design Notes

This document explains **why integrations are implemented this way**, not just how.

---

## General principles

- Explicit HTTP contracts
- Idempotency on all inbound writes
- Timeouts, retries, bounded failure
- No SDK lock-in (HTTP-first)
- Clear separation between transport and domain

---

## WhatsApp Business API (Meta)

### Outbound
- Meta Graph API
- Bearer token auth
- Template-based messaging
- Timeout + retry
- Errors mapped to standard error shape

### Inbound
- Real webhook payload structure
- Signature validation
- Idempotency via message ID
- Safe replay handling

---

## SAP integration

- OData-style HTTP integration
- Query-based reads
- External ID mapping
- Transport isolated from domain
- Ready for OAuth / principal propagation

---

## OpenAI / GPT integration

- Explicit prompt execution
- Deterministic input/output boundaries
- Timeouts and error classification
- No hidden SDK retries
- Provider-agnostic design

---

## ERP sync pattern

- Outbound sync endpoint
- Retries with backoff
- Upstream status surfaced
- Logs include attempt count and result
- Mock ERP provided for local testing

Reusable for:
- Accounting systems
- CRMs
- Payment processors

---

## Inbound API example (Invoices)

Represents external systems pushing data into us:
- Clear POST contract
- Boundary validation
- API-key auth
- Idempotent writes

---

## Why this is not a mock shell

- Real HTTP contracts
- Real error paths
- Real retry/idempotency logic
- Production-style structure
- Only credentials and domains are fake

The code is intentionally **boring, explicit, and predictable**.

