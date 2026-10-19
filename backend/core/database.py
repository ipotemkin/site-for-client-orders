"""Async PostgreSQL driver using asyncpg.

Connection comes from DATABASE_URL (docker-compose) or is built
from POSTGRES_* env vars for local runs.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import quote_plus

import asyncpg

_pool: asyncpg.Pool | None = None


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Decode JSON/JSONB as Python objects."""
    await conn.set_type_codec(
        "json",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )


def _build_dsn() -> str:
    """Return DSN from DATABASE_URL or POSTGRES_* variables."""
    url = os.getenv("DATABASE_URL")
    if url:
        # asyncpg expects postgresql://, not SQLAlchemy-style
        return url.replace("postgresql+asyncpg://", "postgresql://")

    user = os.getenv("POSTGRES_USER", "app")
    password = os.getenv("POSTGRES_PASSWORD", "app")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "app_db")
    safe = quote_plus(password)
    return (
        f"postgresql://{user}:{safe}@{host}:{port}/{db}"
    )


async def init_pool() -> asyncpg.Pool:
    """Create the global connection pool if missing."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=_build_dsn(),
            min_size=1,
            max_size=10,
            init=_init_connection,
        )
    return _pool


async def close_pool() -> None:
    """Close the global pool on application shutdown."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    """Return the active pool or raise if not initialized."""
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    return _pool


async def fetch(
    query: str,
    *args: Any,
) -> list[asyncpg.Record]:
    """Execute a SELECT and return all rows."""
    pool = get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)


async def fetchrow(
    query: str,
    *args: Any,
) -> asyncpg.Record | None:
    """Execute a query and return one row or None."""
    pool = get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)


async def fetchval(
    query: str,
    *args: Any,
) -> Any:
    """Execute a query and return a single value."""
    pool = get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(query, *args)


async def execute(query: str, *args: Any) -> str:
    """Execute a statement (INSERT/UPDATE/DELETE/DDL)."""
    pool = get_pool()
    async with pool.acquire() as conn:
        return await conn.execute(query, *args)
