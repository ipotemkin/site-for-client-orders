"""Routes for anonymous behavior metrics."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from core.deps import get_current_admin
from models.admin_user import AdminUser
from models.behavior_metric import (
    BehaviorMetric,
    BehaviorMetricCRUD,
    BehaviorStats,
)

router = APIRouter()


@router.post(
    "/",
    response_model=BehaviorMetric,
    status_code=status.HTTP_201_CREATED,
)
async def create_metric(
    payload: BehaviorMetric,
) -> BehaviorMetric:
    return await BehaviorMetricCRUD.create(payload)


@router.get("/stats", response_model=BehaviorStats)
async def get_stats(
    _: AdminUser = Depends(get_current_admin),
) -> BehaviorStats:
    return await BehaviorMetricCRUD.stats()
