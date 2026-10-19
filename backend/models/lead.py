"""Lead (client application) model and CRUD."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from core.database import execute, fetch, fetchrow


class Lead(BaseModel):
    """Client application submitted from the warm-lead form.

    CREATE TABLE IF NOT EXISTS leads (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        middle_name VARCHAR(100),
        email VARCHAR(255),
        phone VARCHAR(50),
        business_info TEXT,
        niche VARCHAR(255),
        company_size VARCHAR(100),
        task_volume VARCHAR(255),
        need_volume VARCHAR(255),
        role VARCHAR(50),
        budget VARCHAR(50),
        contact_method VARCHAR(100),
        convenient_time VARCHAR(100),
        comments TEXT,
        deadline VARCHAR(100),
        task_type VARCHAR(255),
        interested_product VARCHAR(255),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    id: UUID | None = None
    first_name: str
    last_name: str
    middle_name: str | None = None
    email: str | None = None
    phone: str | None = None
    business_info: str | None = None
    niche: str | None = None
    company_size: str | None = None
    task_volume: str | None = None
    need_volume: str | None = None
    role: str | None = Field(
        default=None,
        description="employee or manager",
    )
    budget: str | None = None
    contact_method: str | None = None
    convenient_time: str | None = None
    comments: str | None = None
    deadline: str | None = None
    task_type: str | None = None
    interested_product: str | None = None
    created_at: datetime | None = None


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    business_info TEXT,
    niche VARCHAR(255),
    company_size VARCHAR(100),
    task_volume VARCHAR(255),
    need_volume VARCHAR(255),
    role VARCHAR(50),
    budget VARCHAR(50),
    contact_method VARCHAR(100),
    convenient_time VARCHAR(100),
    comments TEXT,
    deadline VARCHAR(100),
    task_type VARCHAR(255),
    interested_product VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

_COLUMNS = (
    "first_name",
    "last_name",
    "middle_name",
    "email",
    "phone",
    "business_info",
    "niche",
    "company_size",
    "task_volume",
    "need_volume",
    "role",
    "budget",
    "contact_method",
    "convenient_time",
    "comments",
    "deadline",
    "task_type",
    "interested_product",
)


def _row_to_lead(row: Any) -> Lead:
    return Lead(**dict(row))


class LeadCRUD:
    """Async CRUD helpers for the leads table."""

    @staticmethod
    async def ensure_table() -> None:
        await execute(
            "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
        )
        await execute(CREATE_TABLE_SQL)

    @staticmethod
    async def create(lead: Lead) -> Lead:
        placeholders = ", ".join(
            f"${i}" for i in range(1, len(_COLUMNS) + 1)
        )
        cols = ", ".join(_COLUMNS)
        values = [getattr(lead, c) for c in _COLUMNS]
        row = await fetchrow(
            f"""
            INSERT INTO leads ({cols})
            VALUES ({placeholders})
            RETURNING *
            """,
            *values,
        )
        return _row_to_lead(row)

    @staticmethod
    async def get_by_id(lead_id: UUID) -> Lead | None:
        row = await fetchrow(
            "SELECT * FROM leads WHERE id = $1",
            lead_id,
        )
        return _row_to_lead(row) if row else None

    @staticmethod
    async def list_all(limit: int = 100) -> list[Lead]:
        rows = await fetch(
            """
            SELECT * FROM leads
            ORDER BY created_at DESC
            LIMIT $1
            """,
            limit,
        )
        return [_row_to_lead(r) for r in rows]

    @staticmethod
    async def update(
        lead_id: UUID,
        lead: Lead,
    ) -> Lead | None:
        sets = ", ".join(
            f"{c} = ${i}"
            for i, c in enumerate(_COLUMNS, start=1)
        )
        values = [getattr(lead, c) for c in _COLUMNS]
        idx = len(_COLUMNS) + 1
        row = await fetchrow(
            f"""
            UPDATE leads
            SET {sets}
            WHERE id = ${idx}
            RETURNING *
            """,
            *values,
            lead_id,
        )
        return _row_to_lead(row) if row else None

    @staticmethod
    async def delete(lead_id: UUID) -> bool:
        status = await execute(
            "DELETE FROM leads WHERE id = $1",
            lead_id,
        )
        return status.endswith("1")
