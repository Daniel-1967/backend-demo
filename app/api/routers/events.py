from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc

from app.api.deps import require_api_key
from app.core.db import db_session
from app.models.webhook_event import WebhookEvent

router = APIRouter(tags=["events"])

@router.get("/events", dependencies=[Depends(require_api_key)])
def list_events(limit: int = 50, cursor: int | None = None):
    limit = min(max(limit, 1), 50)

    with db_session() as db:
        stmt = select(WebhookEvent).order_by(WebhookEvent.id.desc()).limit(limit + 1)
        if cursor:
            stmt = stmt.where(WebhookEvent.id < cursor)
        rows = db.execute(stmt).scalars().all()

        next_cursor = None
        if len(rows) > limit:
            next_cursor = rows[-1].id
            rows = rows[:limit]

        items = [
            {
                "id": e.id,
                "provider": e.provider,
                "event_type": e.event_type,
                "external_id": e.external_id,
                "idempotency_key": e.idempotency_key,
                "signature_valid": e.signature_valid,
                "received_at": e.received_at,
            }
            for e in rows
        ]

        return {"items": items, "next_cursor": next_cursor}    