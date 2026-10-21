"""FastAPI routes for Lead CRUD + intel queue."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

from core.deps import get_current_admin
from core.lead_intel import (
    LeadQueueStats,
    ScoredLead,
    queue_stats,
    score_leads,
)
from models.admin_user import AdminUser
from models.lead import Lead, LeadCRUD

router = APIRouter()


class LeadQueueResponse(BaseModel):
    stats: LeadQueueStats
    items: list[ScoredLead]


@router.post(
    "/",
    response_model=Lead,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead(payload: Lead) -> Lead:
    return await LeadCRUD.create(payload)


@router.get("/queue", response_model=LeadQueueResponse)
async def list_lead_queue(
    limit: int = 200,
    _: AdminUser = Depends(get_current_admin),
) -> LeadQueueResponse:
    leads = await LeadCRUD.list_all(limit=limit)
    scored = score_leads(leads)
    return LeadQueueResponse(
        stats=queue_stats(scored),
        items=scored,
    )


@router.get("/", response_model=list[Lead])
async def list_leads(
    limit: int = 100,
    _: AdminUser = Depends(get_current_admin),
) -> list[Lead]:
    return await LeadCRUD.list_all(limit=limit)


@router.get("/{lead_id}", response_model=Lead)
async def get_lead(
    lead_id: UUID,
    _: AdminUser = Depends(get_current_admin),
) -> Lead:
    lead = await LeadCRUD.get_by_id(lead_id)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена",
        )
    return lead


@router.put("/{lead_id}", response_model=Lead)
async def update_lead(
    lead_id: UUID,
    payload: Lead,
    _: AdminUser = Depends(get_current_admin),
) -> Lead:
    lead = await LeadCRUD.update(lead_id, payload)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена",
        )
    return lead


@router.delete(
    "/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_lead(
    lead_id: UUID,
    _: AdminUser = Depends(get_current_admin),
) -> Response:
    deleted = await LeadCRUD.delete(lead_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
