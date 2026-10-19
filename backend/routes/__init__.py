"""HTTP route modules for each domain model."""

from fastapi import APIRouter

from routes.admin import router as admin_router
from routes.behavior import router as behavior_router
from routes.lead import router as lead_router

api_router = APIRouter()
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
    admin_router,
    prefix="/admin",
    tags=["admin"],
)

__all__ = ["api_router"]
