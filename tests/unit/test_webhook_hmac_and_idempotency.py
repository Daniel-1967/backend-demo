## b/tests/unit/test_webhook_hmac_and_idempotency.py

import hmac
import hashlib
import json


def _sig(secret: str, body_bytes: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()


def test_webhook_hmac_valid_and_replay(client):
    body = {"event_type": "invoice.created", "external_id": "inv_1"}
    raw = json.dumps(body, separators=(",", ":")).encode("utf-8")

    secret = "change_me"
    sig = _sig(secret, raw)

    r1 = client.post(
        "/v1/webhooks/provider-x",
        headers={
            "Idempotency-Key": "idem_001",
            "X-Signature": sig,
            "Content-Type": "application/json",
        },
        content=raw,
    )
    assert r1.status_code == 200
    j1 = r1.json()
    assert j1["status"] in ("accepted", "accepted_with_invalid_signature")
    assert j1["signature_valid"] is True

    # replay
    r2 = client.post(
        "/v1/webhooks/provider-x",
        headers={
            "Idempotency-Key": "idem_001",
            "X-Signature": sig,
            "Content-Type": "application/json",
        },
        content=raw,
    )
    assert r2.status_code == 200
    j2 = r2.json()
    assert j2["status"] == "replay"
    assert j2["id"] == j1["id"]


def test_webhook_invalid_json_returns_400(client):
    r = client.post(
        "/v1/webhooks/provider-x",
        headers={"Idempotency-Key": "idem_bad", "Content-Type": "application/json"},
        content=b"{bad json",
    )
    assert r.status_code == 400
