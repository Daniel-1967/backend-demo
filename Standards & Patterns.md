# Backend Demo — Standards & Patterns

This document defines the **engineering standards and backend patterns** used in this public demo repository. The goal is to demonstrate production-grade backend practices while keeping the project **domain-agnostic and IP-safe**.

---

## 1. API Versioning

* All endpoints are exposed under `/v1`.
* No root-level routes are provided.
* OpenAPI schema is available under `/v1/openapi.json`.

---

## 2. Authentication

* Authentication is performed via API Key.
* Clients must send the header: `X-API-Key`.
* Missing or invalid keys result in consistent error responses.

---

## 3. Error Handling

### Canonical Error Codes

* `AUTH_REQUIRED`
* `FORBIDDEN`
* `NOT_FOUND`
* `VALIDATION_ERROR`
* `CONFLICT`
* `RATE_LIMITED`
* `SIGNATURE_INVALID`
* `IDEMPOTENCY_REPLAY`
* `UPSTREAM_ERROR`
* `TIMEOUT`
* `INTERNAL_ERROR`

### Error Response Contract

```json
{
  "error": {
    "code": "STRING",
    "message": "Human readable message",
    "details": {},
    "request_id": "UUID"
  }
}
```

All error responses follow this structure.

---

## 4. Request ID & Logging

* The system uses `X-Request-Id` for request correlation.
* If the header is missing, a UUID is generated.
* The `request_id` is:

  * Included in all error responses
  * Logged for every request

### Minimum Log Fields

* `request_id`
* `method`
* `path`
* `status`
* `duration_ms`

---

## 5. Pagination

* Cursor-based pagination is used across the API.

### Request

```
GET /v1/resources?limit=50&cursor=<opaque>
```

### Response

```json
{
  "items": [],
  "next_cursor": "opaque-or-null",
  "limit": 50
}
```

Rules:

* `cursor` is opaque (not raw IDs)
* `limit` is capped (e.g. max 100)
* `next_cursor = null` means end of dataset

---

## 6. Layered Architecture

The backend follows a strict layered structure:

* **routers**: HTTP layer only (request/response, dependencies)
* **services**: application logic and use cases
* **integrations**: external providers (ERP, AI, messaging, etc.)
* **models**: persistence and ORM entities
* **schemas**: input/output DTOs
* **core**: configuration, middleware, errors, logging

Rules:

* Routers contain no business logic
* Services contain no HTTP concerns
* Retry logic lives in integrations

---

## 7. Testing Strategy

Two test levels are defined:

### Unit Tests

* Target: `services` and `core`
* No database
* Fast and deterministic

### Integration Tests

* Target: `routers`, database, and integrations (mocked)
* Enabled via environment flag

### Commands

```
pytest tests/unit
pytest tests/integration
```

---

## 8. Configuration

* Environment-based configuration via `.env`
* Settings loaded through a configuration layer
* No unsafe defaults committed to the repository

---

## 9. Anti-IP Rules

This repository intentionally avoids:

* Business-specific terminology
* Real customer flows or KPIs
* Real provider credentials or payloads
* Production data or schemas

All examples, providers, and entities are **generic and mock-based**.

---

## 10. Purpose of This Repository

This project is designed to demonstrate:

* Backend engineering standards
* Clean architecture
* Integration patterns (inbound & outbound)
* Production-minded error handling and observability

It is **not** intended to represent a full product or business domain.
