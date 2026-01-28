
## b/app/api/routers/invoices.py

from __future__ import annotations

import json

from fastapi import APIRouter, Depends

from sqlalchemy import select

from app.api.deps import require_api_key
from app.core.db import db_session
from app.core.errors import app_error
from app.models.invoice import Invoice

router = APIRouter(
    prefix="/invoices",
    tags=["invoices"],
    dependencies=[Depends(require_api_key)],
)


@router.post("")
def create_invoice(payload: dict):
    ext = payload.get("external_id")
    amount = payload.get("amount")
    if not ext or amount is None:
        raise app_error("VALIDATION_ERROR", "Missing fields: external_id, amount")
    with db_session() as db:
        inv = Invoice(
            external_id=str(ext),
            amount=float(amount),
            currency=str(payload.get("currency") or "USD"),
            due_date=str(payload.get("due_date") or ""),
            status=str(payload.get("status") or "open"),
            payload_json=json.dumps(payload, ensure_ascii=False),
        )
        db.add(inv)
        db.flush()
        db.refresh(inv)
        return {"id": inv.id, "external_id": inv.external_id}

@router.get("/{invoice_id}")
def get_invoice(invoice_id: int):
    with db_session() as db:
        inv = db.get(Invoice, invoice_id)
        if not inv:
            raise app_error("NOT_FOUND", "Invoice not found")
        return {
            "id": inv.id,
            "external_id": inv.external_id,
            "amount": float(inv.amount),
            "currency": inv.currency,
            "due_date": inv.due_date,
            "status": inv.status,
            "created_at": inv.created_at.isoformat(),
        }

@router.get("")
def list_invoices(limit: int = 50):
    with db_session() as db:
        rows = db.execute(select(Invoice).order_by(Invoice.id.desc()).limit(limit)).scalars().all()
        return {"items": [{"id": i.id, "external_id": i.external_id, "amount": float(i.amount), "currency": i.currency} for i in rows]}