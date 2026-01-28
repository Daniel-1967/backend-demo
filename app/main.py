from fastapi import FastAPI

from app.api.routers import health, events, webhooks
from app.api.routers import integrations, mock_erp

from app.api.routers.health import router as health_router
from app.api.routers.events import router as events_router
from app.api.routers.webhooks import router as webhooks_router

from app.api.routers import whatsapp as whatsapp_router
from app.api.routers import gpt as gpt_router
from app.api.routers import sap as sap_router
from app.api.routers import invoices as invoices_router



app = FastAPI(title="Backend Demo — Integrations API")

app.include_router(health_router, prefix="/v1")
app.include_router(events_router, prefix="/v1")
app.include_router(webhooks_router, prefix="/v1")
app.include_router(integrations.router, prefix="/v1")
app.include_router(mock_erp.router, prefix="/v1")
# “Real contract” integrations
app.include_router(whatsapp_router.router, prefix="/v1")
app.include_router(gpt_router.router, prefix="/v1")
app.include_router(sap_router.router, prefix="/v1")

# Inbound API example (to be consumed by others)
app.include_router(invoices_router.router, prefix="/v1")