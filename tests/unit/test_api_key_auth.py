## b/tests/unit/test_api_key_auth.py

def test_events_requires_api_key(client):
    r = client.get("/v1/events")
    assert r.status_code in (401, 403)


def test_events_with_api_key_ok(client, seed_api_key):
    r = client.get("/v1/events", headers={"X-API-Key": seed_api_key})
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "next_cursor" in data
