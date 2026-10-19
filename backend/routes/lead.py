"""FastAPI routes for Lead CRUD."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from models.lead import Lead, LeadCRUD

router = APIRouter()


@router.post(
    "/",
    response_model=Lead,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead(payload: Lead) -> Lead:
    return await LeadCRUD.create(payload)


@router.get("/", response_model=list[Lead])
async def list_leads(limit: int = 100) -> list[Lead]:
    return await LeadCRUD.list_all(limit=limit)


@router.get("/{lead_id}", response_model=Lead)
async def get_lead(lead_id: UUID) -> Lead:
    lead = await LeadCRUD.get_by_id(lead_id)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return lead


@router.put("/{lead_id}", response_model=Lead)
async def update_lead(
    lead_id: UUID,
    payload: Lead,
) -> Lead:
    lead = await LeadCRUD.update(lead_id, payload)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return lead


@router.delete(
    "/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_lead(lead_id: UUID) -> Response:
    deleted = await LeadCRUD.delete(lead_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
