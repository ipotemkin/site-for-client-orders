"""Anonymous page behavior metrics (heatmap / time)."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from core.database import execute, fetch, fetchrow, fetchval


class BehaviorMetric(BaseModel):
    """Streaming page metrics from the public landing.

    CREATE TABLE IF NOT EXISTS behavior_metrics (
        id SERIAL PRIMARY KEY,
        application_id INTEGER NOT NULL DEFAULT 0,
        time_on_page INTEGER NOT NULL DEFAULT 0,
        buttons_clicked TEXT NOT NULL DEFAULT '',
        cursor_positions TEXT NOT NULL DEFAULT '',
        return_frequency INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    id: int | None = None
    application_id: int = 0
    time_on_page: int = 0
    buttons_clicked: str = ""
    cursor_positions: str = ""
    return_frequency: int = 0
    created_at: datetime | None = None


class PeriodTimeStats(BaseModel):
    avg_seconds: float = 0
    max_seconds: int = 0


class HeatPoint(BaseModel):
    x: float
    y: float
    weight: int


class BehaviorStats(BaseModel):
    day: PeriodTimeStats
    week: PeriodTimeStats
    month: PeriodTimeStats
    heatmap: list[HeatPoint] = Field(default_factory=list)


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS behavior_metrics (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL DEFAULT 0,
    time_on_page INTEGER NOT NULL DEFAULT 0,
    buttons_clicked TEXT NOT NULL DEFAULT '',
    cursor_positions TEXT NOT NULL DEFAULT '',
    return_frequency INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def _row_to_metric(row: Any) -> BehaviorMetric:
    return BehaviorMetric(
        id=row["id"],
        application_id=row["application_id"],
        time_on_page=row["time_on_page"],
        buttons_clicked=row["buttons_clicked"] or "",
        cursor_positions=row["cursor_positions"] or "",
        return_frequency=row["return_frequency"],
        created_at=row["created_at"],
    )


def _parse_positions(raw: str) -> list[dict[str, Any]]:
    if not raw or not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [p for p in data if isinstance(p, dict)]


class BehaviorMetricCRUD:
    @staticmethod
    async def ensure_table() -> None:
        await execute(CREATE_TABLE_SQL)

    @staticmethod
    async def create(metric: BehaviorMetric) -> BehaviorMetric:
        row = await fetchrow(
            """
            INSERT INTO behavior_metrics (
                application_id,
                time_on_page,
                buttons_clicked,
                cursor_positions,
                return_frequency
            )
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            """,
            metric.application_id,
            metric.time_on_page,
            metric.buttons_clicked,
            metric.cursor_positions,
            metric.return_frequency,
        )
        return _row_to_metric(row)

    @staticmethod
    async def period_time_stats(days: int) -> PeriodTimeStats:
        max_sec = await fetchval(
            """
            SELECT COALESCE(MAX(time_on_page), 0)
            FROM behavior_metrics
            WHERE created_at >= NOW() - ($1 * INTERVAL '1 day')
            """,
            days,
        )
        avg_sec = await fetchval(
            """
            SELECT COALESCE(AVG(bucket_max), 0)
            FROM (
                SELECT MAX(time_on_page) AS bucket_max
                FROM behavior_metrics
                WHERE created_at >= NOW()
                    - ($1 * INTERVAL '1 day')
                GROUP BY date_trunc('hour', created_at)
            ) AS buckets
            """,
            days,
        )
        return PeriodTimeStats(
            avg_seconds=round(float(avg_sec or 0), 1),
            max_seconds=int(max_sec or 0),
        )

    @staticmethod
    async def heatmap(
        days: int = 30,
        limit_rows: int = 2000,
        bin_size: int = 2,
    ) -> list[HeatPoint]:
        rows = await fetch(
            """
            SELECT cursor_positions
            FROM behavior_metrics
            WHERE created_at >= NOW()
                - ($1 * INTERVAL '1 day')
              AND cursor_positions <> ''
            ORDER BY created_at DESC
            LIMIT $2
            """,
            days,
            limit_rows,
        )
        weights: dict[tuple[int, int], int] = {}
        for row in rows:
            for point in _parse_positions(
                row["cursor_positions"] or "",
            ):
                try:
                    x = float(point.get("x", 0))
                    y = float(point.get("y", 0))
                except (TypeError, ValueError):
                    continue
                bx = int(x // bin_size) * bin_size
                by = int(y // bin_size) * bin_size
                key = (bx, by)
                weights[key] = weights.get(key, 0) + 1

        points = [
            HeatPoint(x=float(x), y=float(y), weight=w)
            for (x, y), w in weights.items()
        ]
        points.sort(key=lambda p: p.weight, reverse=True)
        return points[:400]

    @staticmethod
    async def stats() -> BehaviorStats:
        return BehaviorStats(
            day=await BehaviorMetricCRUD.period_time_stats(1),
            week=await BehaviorMetricCRUD.period_time_stats(7),
            month=await BehaviorMetricCRUD.period_time_stats(
                30,
            ),
            heatmap=await BehaviorMetricCRUD.heatmap(),
        )
