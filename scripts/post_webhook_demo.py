import json, hmac, hashlib
from urllib import request as ureq

URL = "http://127.0.0.1:8000/v1/webhooks/provider-x"
SECRET = "change_me"
IDEMP = "idem_001"

payload = {"event_type": "invoice.created", "external_id": "inv_1"}
body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
sig = hmac.new(SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()

req = ureq.Request(URL, data=body, method="POST")
req.add_header("Content-Type", "application/json")
req.add_header("Idempotency-Key", IDEMP)
req.add_header("X-Signature", sig)

with ureq.urlopen(req) as resp:
    print(resp.status, resp.read().decode("utf-8"))
