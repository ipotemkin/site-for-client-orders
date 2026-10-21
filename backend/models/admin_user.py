"""Admin operator accounts (login + password hash)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from core.database import execute, fetchrow, fetchval


class AdminUser(BaseModel):
    """Operator who can access the admin panel.

    CREATE TABLE IF NOT EXISTS admins (
        id SERIAL PRIMARY KEY,
        login VARCHAR(64) NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    id: int | None = None
    login: str = Field(min_length=1, max_length=64)
    created_at: datetime | None = None


class AdminUserCreate(BaseModel):
    """Credentials for bootstrap registration / login."""

    login: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=6, max_length=128)


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    login VARCHAR(64) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def _row_to_admin(row: Any) -> AdminUser:
    return AdminUser(
        id=row["id"],
        login=row["login"],
        created_at=row["created_at"],
    )


class AdminUserCRUD:
    @staticmethod
    async def ensure_table() -> None:
        await execute(CREATE_TABLE_SQL)

    @staticmethod
    async def count() -> int:
        value = await fetchval("SELECT COUNT(*) FROM admins")
        return int(value or 0)

    @staticmethod
    async def get_by_login(login: str) -> tuple[AdminUser, str] | None:
        row = await fetchrow(
            """
            SELECT id, login, password_hash, created_at
            FROM admins
            WHERE login = $1
            """,
            login,
        )
        if row is None:
            return None
        return _row_to_admin(row), row["password_hash"]

    @staticmethod
    async def get_by_id(admin_id: int) -> AdminUser | None:
        row = await fetchrow(
            """
            SELECT id, login, created_at
            FROM admins
            WHERE id = $1
            """,
            admin_id,
        )
        if row is None:
            return None
        return _row_to_admin(row)

    @staticmethod
    async def create(
        login: str,
        password_hash: str,
    ) -> AdminUser:
        row = await fetchrow(
            """
            INSERT INTO admins (login, password_hash)
            VALUES ($1, $2)
            RETURNING id, login, created_at
            """,
            login,
            password_hash,
        )
        return _row_to_admin(row)
