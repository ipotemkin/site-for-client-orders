"""Lead behavior metrics model and CRUD (1:1 with leads)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from core.database import execute, fetch, fetchrow


class LeadBehavior(BaseModel):
    """Frontend-collected user behavior for one lead.

    Shares primary key with leads (one-to-one).

    CREATE TABLE IF NOT EXISTS lead_behaviors (
        id UUID PRIMARY KEY
            REFERENCES leads(id) ON DELETE CASCADE,
        time_on_page_seconds INTEGER,
        buttons_clicked JSONB NOT NULL DEFAULT '[]'::jsonb,
        cursor_hotspots JSONB NOT NULL DEFAULT '[]'::jsonb,
        return_count INTEGER NOT NULL DEFAULT 0,
        raw_metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    id: UUID
    time_on_page_seconds: int | None = None
    buttons_clicked: list[Any] = Field(default_factory=list)
    cursor_hotspots: list[Any] = Field(default_factory=list)
    return_count: int = 0
    raw_metrics: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS lead_behaviors (
    id UUID PRIMARY KEY
        REFERENCES leads(id) ON DELETE CASCADE,
    time_on_page_seconds INTEGER,
    buttons_clicked JSONB NOT NULL DEFAULT '[]'::jsonb,
    cursor_hotspots JSONB NOT NULL DEFAULT '[]'::jsonb,
    return_count INTEGER NOT NULL DEFAULT 0,
    raw_metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def _decode_json(value: Any, fallback: Any) -> Any:
    if value is None:
        return fallback
    if isinstance(value, (list, dict)):
        return value
    return fallback


def _row_to_behavior(row: Any) -> LeadBehavior:
    data = dict(row)
    data["buttons_clicked"] = _decode_json(
        data.get("buttons_clicked"),
        [],
    )
    data["cursor_hotspots"] = _decode_json(
        data.get("cursor_hotspots"),
        [],
    )
    data["raw_metrics"] = _decode_json(
        data.get("raw_metrics"),
        {},
    )
    return LeadBehavior(**data)


class LeadBehaviorCRUD:
    """Async CRUD helpers for lead_behaviors."""

    @staticmethod
    async def ensure_table() -> None:
        await execute(CREATE_TABLE_SQL)

    @staticmethod
    async def create(behavior: LeadBehavior) -> LeadBehavior:
        row = await fetchrow(
            """
            INSERT INTO lead_behaviors (
                id,
                time_on_page_seconds,
                buttons_clicked,
                cursor_hotspots,
                return_count,
                raw_metrics
            )
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
            """,
            behavior.id,
            behavior.time_on_page_seconds,
            behavior.buttons_clicked,
            behavior.cursor_hotspots,
            behavior.return_count,
            behavior.raw_metrics,
        )
        return _row_to_behavior(row)

    @staticmethod
    async def get_by_id(
        behavior_id: UUID,
    ) -> LeadBehavior | None:
        row = await fetchrow(
            "SELECT * FROM lead_behaviors WHERE id = $1",
            behavior_id,
        )
        return _row_to_behavior(row) if row else None

    @staticmethod
    async def list_all(limit: int = 100) -> list[LeadBehavior]:
        rows = await fetch(
            """
            SELECT * FROM lead_behaviors
            ORDER BY created_at DESC
            LIMIT $1
            """,
            limit,
        )
        return [_row_to_behavior(r) for r in rows]

    @staticmethod
    async def update(
        behavior_id: UUID,
        behavior: LeadBehavior,
    ) -> LeadBehavior | None:
        row = await fetchrow(
            """
            UPDATE lead_behaviors
            SET
                time_on_page_seconds = $1,
                buttons_clicked = $2,
                cursor_hotspots = $3,
                return_count = $4,
                raw_metrics = $5
            WHERE id = $6
            RETURNING *
            """,
            behavior.time_on_page_seconds,
            behavior.buttons_clicked,
            behavior.cursor_hotspots,
            behavior.return_count,
            behavior.raw_metrics,
            behavior_id,
        )
        return _row_to_behavior(row) if row else None

    @staticmethod
    async def delete(behavior_id: UUID) -> bool:
        status = await execute(
            "DELETE FROM lead_behaviors WHERE id = $1",
            behavior_id,
        )
        return status.endswith("1")
