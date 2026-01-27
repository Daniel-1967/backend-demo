from fastapi import FastAPI

from app.api.routers import health, events, webhooks
from app.api.routers import integrations, mock_erp

from app.api.routers.health import router as health_router
from app.api.routers.events import router as events_router
from app.api.routers.webhooks import router as webhooks_router

app = FastAPI(title="Backend Demo — Integrations API")

app.include_router(health_router, prefix="/v1")
app.include_router(events_router, prefix="/v1")
app.include_router(webhooks_router, prefix="/v1")
app.include_router(integrations.router, prefix="/v1")
app.include_router(mock_erp.router, prefix="/v1")