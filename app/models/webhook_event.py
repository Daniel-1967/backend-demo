## /app/models/webhook_event.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String

from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

from sqlalchemy.dialects.postgresql import JSONB


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    external_id: Mapped[str] = mapped_column(String(128), index=True, nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    signature_valid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)    
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
