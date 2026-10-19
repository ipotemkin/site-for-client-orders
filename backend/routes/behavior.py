"""FastAPI routes for LeadBehavior CRUD."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from models.behavior import LeadBehavior, LeadBehaviorCRUD

router = APIRouter()


@router.post(
    "/",
    response_model=LeadBehavior,
    status_code=status.HTTP_201_CREATED,
)
async def create_behavior(
    payload: LeadBehavior,
) -> LeadBehavior:
    return await LeadBehaviorCRUD.create(payload)


@router.get("/", response_model=list[LeadBehavior])
async def list_behaviors(
    limit: int = 100,
) -> list[LeadBehavior]:
    return await LeadBehaviorCRUD.list_all(limit=limit)


@router.get("/{behavior_id}", response_model=LeadBehavior)
async def get_behavior(behavior_id: UUID) -> LeadBehavior:
    item = await LeadBehaviorCRUD.get_by_id(behavior_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Behavior not found",
        )
    return item


@router.put("/{behavior_id}", response_model=LeadBehavior)
async def update_behavior(
    behavior_id: UUID,
    payload: LeadBehavior,
) -> LeadBehavior:
    item = await LeadBehaviorCRUD.update(
        behavior_id,
        payload,
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Behavior not found",
        )
    return item


@router.delete(
    "/{behavior_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_behavior(behavior_id: UUID) -> Response:
    deleted = await LeadBehaviorCRUD.delete(behavior_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Behavior not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
