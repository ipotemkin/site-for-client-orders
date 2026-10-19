"""Service catalog model and CRUD (tuning offerings)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from core.database import execute, fetch, fetchrow, fetchval


class Service(BaseModel):
    """Exclusive car tuning / upgrade offering.

    CREATE TABLE IF NOT EXISTS services (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        params JSONB NOT NULL DEFAULT '{}'::jsonb,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        sort_order INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    id: int | None = None
    name: str
    description: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    sort_order: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    params JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

DEFAULT_SERVICES: list[Service] = [
    Service(
        name="Акустика Bose",
        description=(
            "Установка элитной музыкальной системы Bose "
            "с калибровкой салона"
        ),
        params={
            "price_from": "450000",
            "duration": "3–7 дней",
        },
        sort_order=10,
    ),
    Service(
        name="Покраска кузова",
        description=(
            "Полная покраска по итальянской технологии, "
            "лак и полировка"
        ),
        params={
            "price_from": "800000",
            "duration": "14–21 день",
        },
        sort_order=20,
    ),
    Service(
        name="Аэрография",
        description=(
            "Авторская аэрография кузова или элементов "
            "по эскизу"
        ),
        params={
            "price_from": "250000",
            "duration": "7–14 дней",
        },
        sort_order=30,
    ),
    Service(
        name="Детейлинг и защита",
        description=(
            "Керамика, антигравийная плёнка, "
            "премиальный детейлинг"
        ),
        params={
            "price_from": "180000",
            "duration": "2–5 дней",
        },
        sort_order=40,
    ),
]


def _decode_params(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _row_to_service(row: Any) -> Service:
    data = dict(row)
    data["params"] = _decode_params(data.get("params"))
    return Service(**data)


class ServiceCRUD:
    """Async CRUD helpers for services."""

    @staticmethod
    async def ensure_table() -> None:
        await execute(CREATE_TABLE_SQL)
        existing = await fetchval(
            "SELECT COUNT(*) FROM services",
        )
        if int(existing or 0) == 0:
            for item in DEFAULT_SERVICES:
                await ServiceCRUD.create(item)

    @staticmethod
    async def create(service: Service) -> Service:
        row = await fetchrow(
            """
            INSERT INTO services (
                name,
                description,
                params,
                is_active,
                sort_order
            )
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            """,
            service.name,
            service.description,
            service.params,
            service.is_active,
            service.sort_order,
        )
        return _row_to_service(row)

    @staticmethod
    async def get_by_id(service_id: int) -> Service | None:
        row = await fetchrow(
            "SELECT * FROM services WHERE id = $1",
            service_id,
        )
        return _row_to_service(row) if row else None

    @staticmethod
    async def list_all(
        active_only: bool = False,
        limit: int = 200,
    ) -> list[Service]:
        if active_only:
            rows = await fetch(
                """
                SELECT * FROM services
                WHERE is_active = TRUE
                ORDER BY sort_order ASC, id ASC
                LIMIT $1
                """,
                limit,
            )
        else:
            rows = await fetch(
                """
                SELECT * FROM services
                ORDER BY sort_order ASC, id ASC
                LIMIT $1
                """,
                limit,
            )
        return [_row_to_service(r) for r in rows]

    @staticmethod
    async def update(
        service_id: int,
        service: Service,
    ) -> Service | None:
        row = await fetchrow(
            """
            UPDATE services
            SET
                name = $1,
                description = $2,
                params = $3,
                is_active = $4,
                sort_order = $5,
                updated_at = NOW()
            WHERE id = $6
            RETURNING *
            """,
            service.name,
            service.description,
            service.params,
            service.is_active,
            service.sort_order,
            service_id,
        )
        return _row_to_service(row) if row else None

    @staticmethod
    async def delete(service_id: int) -> bool:
        status = await execute(
            "DELETE FROM services WHERE id = $1",
            service_id,
        )
        return status.endswith("1")
