"""FastAPI application entrypoint.

Binds inside the container only. Host access goes through Nginx
(`/api/`). No Docker `ports:` publish — see docker-compose.yml.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database import close_pool, init_pool
from models.admin import AdminSettingsCRUD
from models.behavior import LeadBehaviorCRUD
from models.lead import LeadCRUD
from models.service import ServiceCRUD
from routes import api_router


async def _ensure_schema() -> None:
    """Create tables in dependency order (leads first)."""
    await LeadCRUD.ensure_table()
    await LeadBehaviorCRUD.ensure_table()
    await AdminSettingsCRUD.ensure_table()
    await ServiceCRUD.ensure_table()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_pool()
    await _ensure_schema()
    yield
    await close_pool()


app = FastAPI(
    title="Client Orders API",
    version="0.1.0",
    lifespan=lifespan,
    # Nginx mounts us under /api/ (prefix stripped upstream).
    # root_path makes Swagger/OpenAPI use /api/docs and
    # /api/openapi.json in the browser.
    root_path="/api",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc",
)
app.include_router(api_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
