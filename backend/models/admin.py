"""Admin settings model and CRUD (UI config for frontend)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from core.database import execute, fetch, fetchrow


class AdminSettings(BaseModel):
    """Services and budget range for the lead form UI.

    CREATE TABLE IF NOT EXISTS admin_settings (
        id SERIAL PRIMARY KEY,
        services JSONB NOT NULL DEFAULT '[]'::jsonb,
        budget_min VARCHAR(50),
        budget_max VARCHAR(50),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    id: int | None = None
    services: list[str] = Field(default_factory=list)
    budget_min: str | None = None
    budget_max: str | None = None
    updated_at: datetime | None = None


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS admin_settings (
    id SERIAL PRIMARY KEY,
    services JSONB NOT NULL DEFAULT '[]'::jsonb,
    budget_min VARCHAR(50),
    budget_max VARCHAR(50),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def _decode_services(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _row_to_settings(row: Any) -> AdminSettings:
    data = dict(row)
    data["services"] = _decode_services(data.get("services"))
    return AdminSettings(**data)


class AdminSettingsCRUD:
    """Async CRUD helpers for admin_settings."""

    @staticmethod
    async def ensure_table() -> None:
        await execute(CREATE_TABLE_SQL)

    @staticmethod
    async def create(
        settings: AdminSettings,
    ) -> AdminSettings:
        row = await fetchrow(
            """
            INSERT INTO admin_settings (
                services,
                budget_min,
                budget_max
            )
            VALUES ($1, $2, $3)
            RETURNING *
            """,
            settings.services,
            settings.budget_min,
            settings.budget_max,
        )
        return _row_to_settings(row)

    @staticmethod
    async def get_by_id(
        settings_id: int,
    ) -> AdminSettings | None:
        row = await fetchrow(
            "SELECT * FROM admin_settings WHERE id = $1",
            settings_id,
        )
        return _row_to_settings(row) if row else None

    @staticmethod
    async def get_latest() -> AdminSettings | None:
        row = await fetchrow(
            """
            SELECT * FROM admin_settings
            ORDER BY id DESC
            LIMIT 1
            """
        )
        return _row_to_settings(row) if row else None

    @staticmethod
    async def list_all(limit: int = 50) -> list[AdminSettings]:
        rows = await fetch(
            """
            SELECT * FROM admin_settings
            ORDER BY id DESC
            LIMIT $1
            """,
            limit,
        )
        return [_row_to_settings(r) for r in rows]

    @staticmethod
    async def update(
        settings_id: int,
        settings: AdminSettings,
    ) -> AdminSettings | None:
        row = await fetchrow(
            """
            UPDATE admin_settings
            SET
                services = $1,
                budget_min = $2,
                budget_max = $3,
                updated_at = NOW()
            WHERE id = $4
            RETURNING *
            """,
            settings.services,
            settings.budget_min,
            settings.budget_max,
            settings_id,
        )
        return _row_to_settings(row) if row else None

    @staticmethod
    async def delete(settings_id: int) -> bool:
        status = await execute(
            "DELETE FROM admin_settings WHERE id = $1",
            settings_id,
        )
        return status.endswith("1")
