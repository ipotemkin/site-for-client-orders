"""HTTP route modules for each domain model."""

from fastapi import APIRouter

from routes.admin import router as admin_router
from routes.auth import router as auth_router
from routes.behavior import router as behavior_router
from routes.behavior_metrics import router as metrics_router
from routes.lead import router as lead_router
from routes.service import router as service_router

api_router = APIRouter()
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"],
)
api_router.include_router(
    lead_router,
    prefix="/leads",
    tags=["leads"],
)
api_router.include_router(
    behavior_router,
    prefix="/behaviors",
    tags=["behaviors"],
)
api_router.include_router(
    metrics_router,
    prefix="/behavior-metrics",
    tags=["behavior-metrics"],
)
api_router.include_router(
    service_router,
    prefix="/services",
    tags=["services"],
)
api_router.include_router(
    admin_router,
    prefix="/admin",
    tags=["admin"],
)

__all__ = ["api_router"]
