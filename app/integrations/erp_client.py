## b/app/integrations/erp_client.py
from __future__ import annotations

import time
from dataclasses import dataclass

import httpx

from app.core.config import get_settings
from app.core.config import get_logger

log = get_logger("erp_client")


@dataclass
class ErpResult:
    ok: bool
    attempts: int
    status_code: int | None
    body: str | None
    error_code: str | None


def post_with_retries(*, url: str, json_body: dict, idempotency_key: str) -> ErpResult:
    s = get_settings()
    timeout_s = float(s["ERP_TIMEOUT_S"])
    retries = int(s["ERP_RETRIES"])
    backoffs = [0.2, 0.5, 1.0]  # simple deterministic backoff (seconds)

    attempts = 0
    last_status = None
    last_body = None

    for i in range(max(retries, 1)):
        attempts += 1
        try:
            with httpx.Client(timeout=httpx.Timeout(timeout_s)) as client:
                r = client.post(
                    url,
                    json=json_body,
                    headers={"Idempotency-Key": idempotency_key},
                )
                last_status = r.status_code
                last_body = r.text

                if 200 <= r.status_code < 300:
                    log.info("erp call ok attempt=%s status=%s", attempts, r.status_code)
                    return ErpResult(True, attempts, r.status_code, r.text, None)

                # retry on 5xx
                if 500 <= r.status_code < 600 and attempts < retries:
                    log.warning("erp call retry attempt=%s status=%s", attempts, r.status_code)
                    time.sleep(backoffs[min(i, len(backoffs) - 1)])
                    continue

                # non-retriable (4xx) or retries exhausted
                return ErpResult(False, attempts, r.status_code, r.text, "UPSTREAM_ERROR" if r.status_code >= 500 else "UPSTREAM_REJECTED")

        except (httpx.ReadTimeout, httpx.ConnectTimeout):
            if attempts < retries:
                log.warning("erp timeout retry attempt=%s", attempts)
                time.sleep(backoffs[min(i, len(backoffs) - 1)])
                continue
            return ErpResult(False, attempts, last_status, last_body, "UPSTREAM_TIMEOUT")
        except httpx.HTTPError as e:
            # network/transport errors
            return ErpResult(False, attempts, last_status, str(e), "UPSTREAM_NETWORK_ERROR")

    return ErpResult(False, attempts, last_status, last_body, "UPSTREAM_ERROR")
