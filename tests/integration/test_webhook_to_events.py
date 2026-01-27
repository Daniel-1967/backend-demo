## b/tests/integration/test_webhook_to_events.py

import hmac
import hashlib
import json


def test_webhook_persists_and_events_lists_it(client, seed_api_key):
    body = {"event_type": "invoice.created", "external_id": "inv_1"}
    raw = json.dumps(body, separators=(",", ":")).encode("utf-8")
    sig = hmac.new(b"change_me", raw, hashlib.sha256).hexdigest()

    r = client.post(
        "/v1/webhooks/provider-x",
        headers={
            "Idempotency-Key": "idem_001",
            "X-Signature": sig,
            "Content-Type": "application/json",
        },
        content=raw,
    )
    assert r.status_code == 200

    r2 = client.get("/v1/events", headers={"X-API-Key": seed_api_key})
    assert r2.status_code == 200
    data = r2.json()
    assert isinstance(data.get("items"), list)
    assert len(data["items"]) >= 1
