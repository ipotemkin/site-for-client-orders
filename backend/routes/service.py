"""FastAPI routes for Service CRUD."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status

from models.service import Service, ServiceCRUD

router = APIRouter()


@router.post(
    "/",
    response_model=Service,
    status_code=status.HTTP_201_CREATED,
)
async def create_service(payload: Service) -> Service:
    return await ServiceCRUD.create(payload)


@router.get("/", response_model=list[Service])
async def list_services(
    active_only: bool = False,
    limit: int = 200,
) -> list[Service]:
    return await ServiceCRUD.list_all(
        active_only=active_only,
        limit=limit,
    )


@router.get("/{service_id}", response_model=Service)
async def get_service(service_id: int) -> Service:
    item = await ServiceCRUD.get_by_id(service_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )
    return item


@router.put("/{service_id}", response_model=Service)
async def update_service(
    service_id: int,
    payload: Service,
) -> Service:
    item = await ServiceCRUD.update(service_id, payload)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )
    return item


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service(service_id: int) -> Response:
    deleted = await ServiceCRUD.delete(service_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
